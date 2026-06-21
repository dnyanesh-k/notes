# Q15: Design Real-time Error Monitoring and Alerting System (Sentry-like)

---

## Clarifying Questions

First — what are we monitoring: application errors (exceptions, stack traces), infrastructure metrics (CPU, memory, latency), or both? Sentry-style focuses on errors; Datadog/Prometheus covers metrics. They have different data models.

What's the scale — how many events per second, and how many services are we monitoring? And what's the retention — do we need errors from 6 months ago or just last 7 days?

What are the alerting requirements — real-time (within seconds of an error spike) or near-real-time (minutes)? And who gets alerted — PagerDuty on-call, Slack channel, email?

Do we need error grouping (deduplication) — the same exception happening 1,000 times should be one alert, not 1,000? This is Sentry's core value — it's harder than it looks.

*Assuming: application error monitoring (exceptions + stack traces), 10,000 services, 100K events/sec at peak, 30-day retention, real-time alerting within 30 seconds, automatic error grouping by fingerprint, Slack + PagerDuty notifications.*

---

## Scope

I'll design: SDK for capturing errors, ingestion pipeline, error grouping and deduplication, storage, alerting engine, and the dashboard serving layer. This is a real-time data pipeline problem with some interesting grouping/fingerprinting challenges.

---

## High Level Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR MONITORING SYSTEM                                  │
│                                                                             │
│  APPLICATION SERVICES                                                       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                                │
│  │ Service A │ │ Service B │ │ Service C │  ← SDK installed in each        │
│  │  (SDK)    │ │  (SDK)    │ │  (SDK)    │                                │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘                                │
│        │             │             │                                        │
│        └─────────────┼─────────────┘                                        │
│                      │ HTTPS (error events)                                 │
│                      ▼                                                      │
│            ┌─────────────────┐                                             │
│            │  Ingestion API  │  ← rate limiting, auth, validation          │
│            │  (stateless)    │                                             │
│            └────────┬────────┘                                             │
│                     │                                                       │
│                     ▼                                                       │
│             ┌──────────────┐                                               │
│             │    Kafka     │  ← buffer for burst traffic                   │
│             │ (error.raw)  │                                               │
│             └──────┬───────┘                                               │
│                    │                                                        │
│       ┌────────────┼────────────┐                                          │
│       ▼            ▼            ▼                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                                   │
│  │ Grouping │ │ Storage  │ │ Alerting │                                   │
│  │ Worker   │ │ Worker   │ │ Engine   │                                   │
│  └──────────┘ └──────────┘ └──────────┘                                   │
│       │            │            │                                           │
│       ▼            ▼            ▼                                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐                           │
│  │  Redis   │ │ClickHouse│ │ PagerDuty/Slack   │                           │
│  │ (groups  │ │ (events  │ │ (notifications)   │                           │
│  │  state)  │ │ storage) │ └──────────────────┘                           │
│  └──────────┘ └──────────┘                                                 │
│                                                                             │
│            ┌──────────────────────────────────────┐                        │
│            │         Dashboard API                 │                        │
│            │  (query ClickHouse for UI rendering)  │                        │
│            └──────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Deep Dive 1 — The SDK (Client-side Capture)

The SDK lives in every monitored application. It must be: low overhead (can't slow down the app), reliable (buffer offline events), and smart (capture useful context, not just the error message).

**What the SDK captures:**

```python
# What happens when an unhandled exception occurs
import sentry_sdk

def capture_exception(exc: Exception):
    event = {
        'event_id': uuid4(),
        'timestamp': datetime.utcnow().isoformat(),
        'level': 'error',
        'exception': {
            'type': type(exc).__name__,          # 'ValueError', 'DatabaseError'
            'value': str(exc),                    # 'Connection refused to localhost:5432'
            'stacktrace': {
                'frames': format_stack_trace(exc) # file, line number, function, code snippet
            }
        },
        'environment': os.environ.get('ENV', 'production'),
        'release': os.environ.get('GIT_COMMIT', 'unknown'),
        'user': { 'id': current_user_id() },     # who triggered the error
        'tags': { 'service': 'payments-api', 'region': 'us-east-1' },
        'extra': {                                # additional context
            'request_id': request_id,
            'url': request.path,
            'method': request.method,
        },
        'breadcrumbs': recent_log_entries()       # last 10 log lines before error
    }
    
    # Buffer in memory queue (never block the main thread)
    background_queue.put(event)
```

**SDK design principles:**
- **Non-blocking:** all sends happen on a background thread. A slow error API never blocks the main app thread.
- **Buffering:** if the network is unavailable, buffer up to 100 events in memory. On reconnection, flush.
- **Sampling:** for high-frequency errors (same error happening 10K times/sec), sample 1% and send — don't flood the ingestion API. The server extrapolates counts.
- **PII scrubbing:** automatically redact credit card patterns, passwords from form fields, session tokens from headers before sending.

---

## Deep Dive 2 — Error Grouping (Fingerprinting)

This is Sentry's core technical innovation. The same bug produces thousands of identical errors — we need to group them into one "issue" with a count, not show 10,000 individual events.

**How fingerprinting works:**

Two errors belong to the same group if they have the same **fingerprint** — a hash of the key identifying features of the error.

```python
def compute_fingerprint(event: dict) -> str:
    exc = event['exception']
    stacktrace = exc['stacktrace']['frames']
    
    # Fingerprint based on: exception type + top 3 frames of the stack
    # Exclude variable parts: line numbers that change with minor edits,
    # dynamic values in error messages (user IDs, timestamps)
    
    fingerprint_parts = [
        exc['type'],                      # 'DatabaseError'
        normalize_message(exc['value']),  # strip dynamic values
    ]
    
    # Add top 3 relevant stack frames (skip library frames)
    app_frames = [f for f in stacktrace if '/site-packages/' not in f['filename']]
    for frame in app_frames[:3]:
        fingerprint_parts.append(f"{frame['filename']}:{frame['function']}")
    
    fingerprint = sha256('|'.join(fingerprint_parts)).hexdigest()[:16]
    return fingerprint

def normalize_message(message: str) -> str:
    # Remove dynamic content that changes between occurrences
    message = re.sub(r'\b\d+\b', 'NUM', message)      # numbers → NUM
    message = re.sub(r'user_\w+', 'USER', message)    # user IDs → USER
    message = re.sub(r'\b[0-9a-f]{8}-[0-9a-f-]+\b', 'UUID', message)  # UUIDs
    return message
```

**Grouping logic:**

```python
class GroupingWorker:
    def process(self, event: dict):
        fingerprint = compute_fingerprint(event)
        
        # Redis tracks group state
        group_key = f"group:{event['project_id']}:{fingerprint}"
        
        group = redis.hgetall(group_key)
        if not group:
            # First occurrence — create new group
            group = {
                'fingerprint': fingerprint,
                'first_seen': event['timestamp'],
                'last_seen': event['timestamp'],
                'count': 1,
                'status': 'unresolved',
                'title': f"{exc_type}: {normalized_message}"
            }
            redis.hmset(group_key, group)
            
            # Persist to PostgreSQL
            db.insert('issue_groups', group)
        else:
            # Existing group — increment counter, update last_seen
            redis.hincrby(group_key, 'count', 1)
            redis.hset(group_key, 'last_seen', event['timestamp'])
            
            # Periodic sync to PostgreSQL (every 60 seconds or every 100 events)
            self.schedule_db_sync(fingerprint)
        
        # Tag the raw event with its group ID for later retrieval
        event['group_id'] = fingerprint
        kafka_producer.send('events.processed', event)
```

---

## Deep Dive 3 — Storage Strategy

**Two data models for two query patterns:**

1. **Group-level queries** (most common): "Show me all unresolved issues in project X, sorted by frequency." → PostgreSQL

2. **Event-level queries** (drill-down): "Show me the 20 most recent occurrences of this specific error, with their full stack traces." → ClickHouse

```sql
-- PostgreSQL: issue groups (small table, fast aggregates)
CREATE TABLE issue_groups (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    project_id      BIGINT NOT NULL,
    fingerprint     VARCHAR(32) NOT NULL,
    title           VARCHAR(500) NOT NULL,
    exception_type  VARCHAR(200),
    status          ENUM('unresolved','resolved','ignored') DEFAULT 'unresolved',
    first_seen      TIMESTAMP NOT NULL,
    last_seen       TIMESTAMP NOT NULL,
    event_count     BIGINT DEFAULT 1,
    user_count      BIGINT DEFAULT 1,
    assigned_to     BIGINT,             -- team member assigned to fix this
    UNIQUE KEY uk_project_fp (project_id, fingerprint),
    INDEX idx_project_status (project_id, status, last_seen DESC)
);

-- PostgreSQL: project and alert configuration
CREATE TABLE alert_rules (
    id              BIGINT PRIMARY KEY,
    project_id      BIGINT NOT NULL,
    condition       ENUM('new_issue','regression','frequency_spike'),
    threshold       INT,                -- e.g., 100 events in 5 minutes
    window_minutes  INT,
    channel         ENUM('slack','pagerduty','email'),
    channel_config  JSON,               -- webhook URLs, email addresses
    is_active       BOOLEAN DEFAULT TRUE
);
```

```sql
-- ClickHouse: raw events (append-only, time-series, high-volume)
CREATE TABLE error_events (
    event_id        UUID,
    project_id      UInt64,
    group_id        String,             -- fingerprint
    timestamp       DateTime,
    level           LowCardinality(String),
    exception_type  String,
    exception_value String,
    stacktrace      String,             -- JSON blob
    environment     LowCardinality(String),
    release         String,
    user_id         String,
    tags            String,             -- JSON
    PRIMARY KEY (project_id, timestamp, event_id)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)      -- partition by month for efficient pruning
ORDER BY (project_id, timestamp)      -- sort key: queries filter by project + time
TTL timestamp + INTERVAL 30 DAY;      -- auto-delete events older than 30 days
```

ClickHouse is purpose-built for this workload: high-write-throughput append-only events, column-oriented storage (fast aggregations: `COUNT(*) WHERE project_id = X AND timestamp > NOW() - 1 hour`), and built-in TTL for auto-expiry.

---

## Deep Dive 4 — Alerting Engine

The alerting engine evaluates rules against incoming events and fires notifications.

**Alert types:**

```
1. New Issue:    First occurrence of a fingerprint → alert immediately
2. Regression:  A previously resolved issue reappears → alert immediately
3. Frequency:   Error rate spikes (e.g., >100 events/5min for a group) → alert
4. Volume:      Total error volume across project spikes by >50% vs previous hour
```

**Real-time frequency check:**

```python
class AlertingEngine:
    def check_alerts(self, event: dict):
        project_id = event['project_id']
        group_id = event['group_id']
        
        # Count events in sliding window using Redis sorted set
        window_key = f"alert_window:{project_id}:{group_id}"
        now = time.time()
        
        redis.zadd(window_key, { event['event_id']: now })
        redis.zremrangebyscore(window_key, 0, now - 300)  # 5-minute window
        
        count_in_window = redis.zcard(window_key)
        redis.expire(window_key, 600)   # TTL safety
        
        # Load alert rules for this project
        rules = self.load_rules(project_id)  # cached in Redis
        
        for rule in rules:
            if rule.condition == 'frequency' and count_in_window >= rule.threshold:
                if not self.is_rate_limited(project_id, group_id, rule.id):
                    self.fire_alert(rule, event, count_in_window)
                    self.set_alert_cooldown(project_id, group_id, rule.id, minutes=30)
    
    def fire_alert(self, rule: AlertRule, event: dict, count: int):
        message = self.format_alert_message(rule, event, count)
        
        if rule.channel == 'slack':
            requests.post(rule.channel_config['webhook_url'], json={
                "text": message,
                "attachments": [self.build_slack_attachment(event)]
            })
        elif rule.channel == 'pagerduty':
            pagerduty_client.trigger_incident(
                title=f"Error spike in {event['project']}",
                body=message,
                severity='critical' if count > 1000 else 'warning'
            )
```

**Alert deduplication:** An alert rule that fires once should not fire again for the next 30 minutes for the same issue (unless the issue worsens). The cooldown period is stored in Redis with TTL. This prevents alert fatigue — the single biggest cause of on-call burnout.

---

## Scale — What Breaks at 10x?

At 1M events/sec:

**Ingestion API:** Stateless, scale horizontally. 1M events/sec × 1KB average = 1 GB/sec ingestion. Run 50 ingestion servers behind a load balancer. Each server validates, deserializes, and publishes to Kafka. No DB calls in the hot path.

**Kafka:** At 1M events/sec × 1KB = 1 GB/sec, Kafka easily handles this with sufficient brokers (10–20 brokers × 100 MB/sec each = 1–2 GB/sec). Partition by `project_id` — events from the same project go to the same partition for ordered processing.

**Grouping workers:** The Redis sorted set for the sliding window and hash for group state are the hot path. At 1M events/sec, Redis needs cluster sharding by `project_id`. Grouping workers are CPU-bound (SHA256 fingerprinting). Scale: 1M events/sec × 1ms fingerprint time = 1,000 CPU-cores. That's actually fast — fingerprinting is sub-millisecond. 50–100 grouping worker processes handle this.

**ClickHouse:** Designed for 1M+ inserts/sec. Use batch inserts (not row-by-row): workers accumulate 1,000 events, write one batch insert per 100ms. ClickHouse handles bulk inserts efficiently. Replication across 3 nodes for durability. Partitioning by month ensures queries on recent data don't scan old partitions.

**Dashboard queries:** Analysts query ClickHouse: `SELECT count(*), exception_type FROM error_events WHERE project_id = X AND timestamp > NOW() - 1 HOUR GROUP BY exception_type`. ClickHouse columnar storage makes this extremely fast (reads only the `exception_type` and `timestamp` columns, not the full row). Results in < 500ms even on billions of rows.

---

## Trade-offs

**ClickHouse vs Elasticsearch for error storage:** Elasticsearch is commonly used for log storage and supports full-text search (searching stack traces for "NullPointerException" across all events). But ClickHouse is 10–50x faster for aggregate queries (count errors by type, group by time window) and 5x cheaper for storage. The trade-off: ClickHouse doesn't support full-text search natively (use LIKE queries, slower). For error monitoring where aggregate queries dominate, ClickHouse wins. For log search where you need to search the raw message, Elasticsearch is better. Many companies use both: ClickHouse for metrics/aggregates, Elasticsearch for searchable raw logs.

**Fingerprinting accuracy vs grouping precision:** Aggressive fingerprinting (hash only exception type + first frame) groups too aggressively — different bugs get merged. Conservative fingerprinting (hash entire stack trace) groups too loosely — the same bug with minor code changes creates separate groups. The right balance: hash type + normalized message + top 3 application frames, skip library frames. Allow manual group merging and splitting in the UI to correct mistakes.

**Alert fatigue vs alert coverage:** Too many alerts and engineers stop paying attention (alert fatigue). Too few and real problems go undetected. Solutions: alert on error rate change (percentage spike from baseline), not absolute counts. Set cooldown periods. Allow issue muting. Group related alerts ("5 issues spiking in payments service" instead of 5 separate alerts). PagerDuty's grouping and snooze features help operationally.

---

## Cross-Questions

**How do you handle an error that occurs 1 million times per second — won't it overwhelm the system?**

Client-side sampling: the SDK samples a percentage of occurrences (configurable: `sample_rate=0.01` = 1%). The server extrapolates: received 1,000 events × sample_rate 0.01 = estimated 100,000 actual events. Sampling is deterministic per error fingerprint so the same event always either sends or not — it doesn't create inconsistent counts. Server-side rate limiting: at the ingestion API, if a project exceeds 10K events/sec, start dropping with a 429 and logging the drop count. The grouping worker uses a separate counter in Redis regardless of what was sampled — even sampled events increment the occurrence counter.

**How do you handle errors across a distributed trace — a request that touches 5 microservices?**

Distributed tracing (OpenTelemetry integration). Each request gets a `trace_id` generated at the entry point. Every service propagates this ID in its headers. When an error occurs in Service 3, the error event includes the `trace_id`. The monitoring system stores the trace relationship. In the dashboard: when you view an error event, you see the full distributed trace — which services were involved, where the latency was, which service caused the error. Sentry integrates with Jaeger and Zipkin for this. The trace_id links error events across services into a coherent story.

**How do you implement source maps for JavaScript errors (minified code makes stack traces unreadable)?**

JavaScript in production is minified — stack traces show `bundle.js:1:5432` not `src/components/Payment.jsx:45`. Source maps map minified positions back to original source. Workflow: during the build, generate source maps and upload them to the error monitoring service (not publicly — they're confidential). Store in S3 keyed by `release + filename`. When a JS error arrives, the grouping worker fetches the source map, applies the mapping, and stores the readable stack trace. The raw minified trace is also stored for debugging. Source maps should only be accessible to authenticated team members — they contain your full source code structure.

**How do you calculate the error impact on users (user_count per issue)?**

Every error event includes `user_id` (if authenticated) or `session_id` (for anonymous users). The grouping worker maintains a HyperLogLog counter in Redis per group: `redis.pfadd(f"users:{group_id}", user_id)`. HyperLogLog gives an approximate distinct count with 0.81% error using only 12KB of memory regardless of how many users. `redis.pfcount(f"users:{group_id}")` → approximate unique users affected. For exact counts (for critical bugs), use a Redis Set (stores all user IDs, exact count, but grows with user count). Sync to PostgreSQL's `user_count` column every 5 minutes. "This error affected 47,293 users" is shown in the dashboard — this is what makes error monitoring immediately actionable for product teams.

**How would you implement performance monitoring (not just errors — also slow endpoints)?**

Every SDK request span captures: `duration_ms`, `endpoint`, `status_code`. If duration > P95 threshold, emit a performance event (same pipeline as errors). The ingestion pipeline routes performance events to a separate Kafka topic. A performance aggregation worker computes P50/P95/P99 latency per endpoint per 1-minute window, stored in ClickHouse time-series format. Dashboard shows: latency trends over time, slowest endpoints, latency distribution histogram. Alert when P95 latency for a critical endpoint exceeds SLA (e.g., payment checkout P95 > 2 seconds). This is Sentry's Performance product — same infrastructure, different data shape.
