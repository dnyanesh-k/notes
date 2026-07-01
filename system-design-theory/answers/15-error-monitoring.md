# Q15: Design an Error Monitoring System (Sentry)

---

> **Interview Phase Map** → Phase 1: Requirements (5 min) · Phase 2: Core Entities (2 min) · Phase 3: API Design (5 min) · Phase 4: High Level Design (12 min) · Phase 5: Deep Dives (10 min)

---

## Introduction

An error monitoring system collects, aggregates, and surfaces errors that occur in production software so that engineering teams can identify issues, understand their impact, and fix them before they affect more users. Sentry is the most well-known example. Every time an unhandled exception occurs in an application, the monitoring system captures the error, its full stack trace, the request context, and the user affected, and groups it with all other occurrences of the same error for analysis.

The core value is visibility. In a distributed system with dozens of services and millions of requests per day, errors happen constantly. Most are noise — transient network blips, client-side input errors, known edge cases. A small subset are critical — a new deployment broke a payment flow, a database query is suddenly timing out, a third-party API is returning 500s. Error monitoring filters the noise, groups related errors, and surfaces the ones that need attention, complete with the context needed to reproduce and fix them.

The ingestion path must handle very high write throughput at low latency. An application crash can generate hundreds of error events per second from multiple servers simultaneously, and the monitoring system must never become a bottleneck or go down when the service it's watching is already under stress. This is typically achieved with a lightweight SDK on the client side that sends events asynchronously via a fire-and-forget mechanism, with a high-throughput event ingestion layer on the backend using message queues to decouple capture from processing.

**Grouping** (also called fingerprinting) is the most technically interesting problem. The same bug in different conditions might produce slightly different error messages — different user IDs, different input values, different server names. The system must recognize that these are all the same underlying issue and group them together, showing a count of how many times it has happened and how many users it has affected.

Alerting rules, release tracking (to correlate error spikes with deployments), performance monitoring (transaction traces alongside errors), and data retention policies are all standard components of a complete error monitoring design.

---

## How to Approach This in an Interview

Error monitoring is deceptively complex. The basic idea — "collect errors, show them" — sounds simple. The hard parts are: (1) intelligently grouping thousands of similar errors into one issue so you don't drown developers in noise, (2) storing billions of events cheaply, and (3) alerting precisely — enough to catch real problems, not enough to cause alert fatigue. Lead with the grouping algorithm, because that's what separates Sentry from just a logging service.

---

## Clarifying Questions

**1. What sources?**

"Backend errors only, or also frontend (JavaScript), mobile (iOS/Android), and CLIs?"

*Why this matters:* Backend errors have stack traces. JavaScript needs source map deobfuscation before the stack trace makes sense. Mobile crash reports come in different formats. Each needs different processing.

**2. Volume and retention?**

"Millions of events/day or billions? How long should raw events be kept — 30 days, 90 days?"

*Why this matters:* At 1B events/day, you cannot store all of them forever. You need a purpose-built analytical database (ClickHouse) and a sampling strategy.

**3. What alerting behavior?**

"Alert on new issues only, or also on volume spikes (error rate suddenly 10×), regressions (issue was resolved, now happening again)?"

*Why this matters:* Three alerting scenarios require different detection logic. Most teams care about all three.

**4. Performance monitoring (APM)?**

"Just errors, or also slow transactions (latency profiling, N+1 query detection)?"

*Why this matters:* APM adds distributed tracing (Jaeger/OpenTelemetry), a different data model, and much higher event volume. Start with errors, extend to APM.

### Assumptions

```
- Sources: backend (Python, Node.js), frontend (JavaScript), mobile (iOS crash reports)
- Volume: 1B raw events/day = 11,574 events/second
- Retention: raw events 30 days, aggregated stats 2 years
- Alerting: new issues, regressions, frequency spikes, user impact threshold
- Client-side sampling: configurable (send only 10% of errors above rate limit)
- Source map deobfuscation for JavaScript stack traces
- Distributed tracing: link errors to trace IDs
```

---

## Functional Requirements

- Applications should be able to ingest error events (exceptions, crashes, log errors) from backend, frontend, and mobile clients
- Users should be able to view grouped error issues with stack traces, frequency trends, and affected user counts
- Users should be able to configure alert rules that fire on new issues, regressions, or frequency spikes

> **How to say this in the interview:** *"I see three core things this system needs to do — ingest error events from backend, frontend, and mobile clients, let teams view grouped issues with stack traces and frequency trends, and configure alerts that fire when something new or unexpected happens. Does that capture it?"* Error grouping is where the real product value is — stating it as a functional requirement rather than leaving it implied shows you understand what makes a monitoring tool useful versus just a log store.

## Non-functional Requirements

> **NFR = Non-Functional Requirements.** These answer *how the system behaves*, not *what it does*. FR = "users should be able to post a tweet" (the feature). NFR = "the feed must load in under 200ms" (the quality). Same system, completely different axis.

- **Ingest latency < 1 second**: errors must be captured immediately — slow ingest delays incident response
- **High write throughput**: 1B events/day ≈ 11,574 events/sec — write path must scale horizontally via Kafka
- **Read availability > Write consistency**: teams must always be able to view errors even during ingestion backpressure
- **Retention tiering**: raw events 30 days; aggregated stats 2 years — storage cost scales with retention window
- **Grouping accuracy**: grouping raw events (11K/sec) into meaningful issues (hundreds) is the core value — fingerprinting must be reliable

> **How to say this in the interview:** After agreeing on FRs, transition with: *"Now let me think about the non-functional requirements — the qualities the system needs to have, not just the features."* Then state each of the points listed above with its specific number or reason attached. Always quantify — "the system should be fast" signals nothing; the specific path and millisecond target is what shows you understand the system. Close with: *"Any specific constraints I should factor into my design?"*
>
> **Mental checklist for any system — pick your top 3:** Run through these mentally every time: *Is stale data acceptable, or must it always be correct?* (CAP — AP or CP?), *Which specific path must be fastest, and what is the millisecond target?* (Latency), *What is the read-to-write ratio and peak QPS?* (Scale). Add Durability, Security, or Compliance only when they are the defining constraint for that particular system — do not list all eight just to look thorough.

---

## Back-of-Envelope Math

> **Interview note:** Skip this section out loud. Say: *"I'll skip capacity estimation upfront — I'll do the math only if a specific number would directly change a design decision."* Then move on. The calculations above are study material — they show you the scale of this system and tell you what to optimize for.

```
Events: 1B/day = 11,574 events/sec peak

Event payload: ~2KB average (exception type, message, stack trace, 
                              user context, request headers, breadcrumbs)
Ingest bandwidth: 11,574 × 2KB = ~23MB/sec = ~2TB/day raw event data

Storage:
  ClickHouse (events, 30 days): 2TB/day × 30 = 60TB
    ClickHouse compression: ~10:1 for repetitive log-like data → 6TB actual disk
    
  PostgreSQL (issues table):
    1B events/day, ~1M unique issues after grouping
    Issues table: 1M rows × 2KB = 2GB → very manageable
    
Issue grouping:
  Goal: 1B events → ~1M issues (1000:1 compression)
  Same exception + stack trace → same fingerprint → same issue
  This is the core algorithm that makes the system usable
  
Alert evaluation:
  Check alerting rules every 60 seconds
  10,000 organizations × 5 rules each = 50,000 rule evaluations/minute = 833/sec
  → Single Redis + ClickHouse cluster handles this easily
```

---

## Core Entities

- **ErrorEvent** — raw inbound error: stack trace + context + timestamp + source platform
- **Issue** — grouped set of ErrorEvents sharing the same fingerprint (error type + location)
- **AlertRule** — condition + threshold + notification channel per user/team
- **SourceMap** — JavaScript/mobile symbol table for stack trace deobfuscation

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## API Design

> **Why REST (with a batching note for the ingest path):** The dashboard API is standard REST — querying issues and updating status is simple CRUD. The ingest endpoint deserves a deliberate choice: client SDKs send errors in batches (not one at a time) to reduce per-event overhead at 11K events/sec. WebSocket is not needed because error reporting is fire-and-forget — the SDK does not need a response per event. Say: *"I'll use REST for both paths. For the dashboard, it is standard CRUD. For ingestion, the SDK batches errors into a single POST to reduce overhead — at 11K events per second, per-event HTTP calls would be prohibitive. The ingest endpoint returns 202 Accepted and we never block the client waiting for confirmation."*

```
// Client SDK → ingest (bulk to reduce overhead)
POST /v1/ingest
body: { "errors": ErrorEvent[], "sdk_version": string }
→ 202 Accepted

// Dashboard — issues
GET /v1/issues?status=open&sort=frequency&limit=20
→ 200: { "issues": Issue[] }

GET /v1/issues/{issue_id}
→ 200: { "issue": Issue, "sample_events": ErrorEvent[], "trend": object }

PATCH /v1/issues/{issue_id}
body: { "status": "resolved|ignored" }
→ 200: { "issue": Issue }

// Alerting
POST /v1/alerts
body: { "condition": "new_issue|regression|spike", "threshold": object, "notify": { "email": string } }
→ 201: { "alert_id": string }
```

---

## High Level Design

> **How to build this diagram in the interview — this phase matters most:** Do not draw the complete architecture upfront. Start by saying: *"Let me build the architecture by going through each endpoint one at a time."* For each endpoint: draw only the components it needs, talk through the data flow out loud as you draw — the interviewer needs to follow your reasoning, not just see boxes appearing — and add the relevant schema fields directly next to the database component in the diagram. When you spot a need for a cache, queue, or additional component mid-drawing, say *"I can see we'll need a cache here — I'm going to note that and come back to it in deep dives"*, then keep moving. Do not solve deep dive problems during this phase. Finish High Level Design only when all three functional requirements have a working data path through the diagram. The diagram above is your reference for what the final state looks like.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ERROR MONITORING SYSTEM                                  │
│                                                                              │
│  SDK (Python/JS/iOS)                                                        │
│      │ HTTP POST /events                                                    │
│      ▼                                                                      │
│  ┌────────────────┐                                                         │
│  │  Ingest API    │  → Rate limiting (per DSN key)                         │
│  │  (stateless)   │  → Basic validation                                    │
│  │  100 replicas  │  → Publish to Kafka                                    │
│  └────────────────┘                                                         │
│          │                                                                   │
│          ▼ Kafka (raw events)                                               │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │         Event Processing Workers                            │            │
│  │                                                            │            │
│  │  1. Source map deobfuscation (JS stack traces)             │            │
│  │  2. Fingerprinting (grouping algorithm)                    │            │
│  │  3. Create/update Issue in PostgreSQL                      │            │
│  │  4. Store event in ClickHouse                              │            │
│  │  5. Update aggregation counters                            │            │
│  │  6. Check alerting rules → trigger alerts                  │            │
│  └────────────────────────────────────────────────────────────┘            │
│                                                                              │
│  STORAGE                                                                    │
│  ┌──────────────────────┐  ┌───────────────────────────────────────────┐   │
│  │ PostgreSQL           │  │ ClickHouse                                 │   │
│  │ - projects           │  │ - events (raw, 30 days)                   │   │
│  │ - issues (groups)    │  │ - issue_hourly_stats (2 years)            │   │
│  │ - alert_rules        │  │ Fast columnar queries:                    │   │
│  │ - users, settings    │  │   "top 10 errors last 24h by user impact" │   │
│  └──────────────────────┘  └───────────────────────────────────────────┘   │
│                                                                              │
│  DASHBOARD: React SPA, queries both PostgreSQL (issues list) +              │
│             ClickHouse (event trends, user impact analytics)                │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: The SDK and Event Ingestion

### Client SDK Design

```python
# sentry_sdk/__init__.py (simplified)

import sys
import traceback
import threading
import queue
from typing import Optional

class SentryClient:
    def __init__(self, dsn: str, sample_rate: float = 1.0, 
                 environment: str = "production"):
        self.dsn = DSN.parse(dsn)  # extracts project_id, public_key, host
        self.sample_rate = sample_rate
        self.environment = environment
        
        # Buffer: events queue, background thread flushes asynchronously
        self._queue = queue.Queue(maxsize=100)
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()
        
        # Install exception hook (captures unhandled exceptions automatically)
        self._original_excepthook = sys.excepthook
        sys.excepthook = self._handle_unhandled_exception
    
    def capture_exception(self, exc: Exception, 
                          user_context: dict = None) -> Optional[str]:
        """Called manually or automatically by exception hook."""
        
        # Client-side sampling: drop (1 - sample_rate) fraction of events
        # Reduces data volume at the source; prevents billing explosions during error storms
        import random
        if random.random() > self.sample_rate:
            return None
        
        # Build the event payload
        event = {
            "event_id": generate_uuid4(),
            "timestamp": datetime.utcnow().isoformat(),
            "exception": {
                "type": type(exc).__name__,
                "value": str(exc),
                "stacktrace": extract_stacktrace(exc)
            },
            "platform": "python",
            "environment": self.environment,
            "release": os.environ.get("SENTRY_RELEASE"),
            "user": user_context,
            # Breadcrumbs: last 100 logs leading up to this error
            "breadcrumbs": self._breadcrumb_buffer.get_last(100)
        }
        
        # Enqueue (non-blocking — never slow down the application)
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            # Queue is full → drop event (circuit breaker: SDK never crashes the app)
            pass
        
        return event["event_id"]
    
    def _worker_loop(self):
        """Background thread: flush events to Sentry server."""
        while True:
            events = []
            # Batch up to 10 events, or flush every 2 seconds
            deadline = time.time() + 2.0
            while time.time() < deadline and len(events) < 10:
                try:
                    event = self._queue.get(timeout=0.1)
                    events.append(event)
                except queue.Empty:
                    break
            
            if events:
                self._send_envelope(events)
    
    def _send_envelope(self, events: list[dict]):
        """Send events to ingest API."""
        envelope = {
            "dsn": str(self.dsn),
            "events": events
        }
        try:
            requests.post(
                f"https://ingest.sentry.io/api/{self.dsn.project_id}/envelope/",
                json=envelope,
                headers={"X-Sentry-Auth": f"Sentry sentry_key={self.dsn.public_key}"},
                timeout=5
            )
        except Exception:
            pass  # SDK failures must NEVER affect the application

def extract_stacktrace(exc: Exception) -> list[dict]:
    tb = traceback.extract_tb(exc.__traceback__)
    return [
        {
            "filename": frame.filename,
            "lineno": frame.lineno,
            "function": frame.name,
            "context_line": frame.line  # the actual line of code
        }
        for frame in tb
    ]
```

**Why background thread + queue?**

If the SDK sent events synchronously, every exception would add 50-100ms HTTP latency to your application. During an error storm (100 errors/sec), this would be catastrophic. The background thread decouples event sending from the application's request path entirely.

**Client-side sampling:**

Without sampling, a single misconfigured endpoint that throws 10,000 errors/minute would flood your Sentry quota and obscure other issues. The `sample_rate` parameter (0.0-1.0) drops events randomly at the source. 10% sampling = 1,000 events/minute instead of 10,000. The system compensates for sampling in volume calculations: if sample_rate=0.1 and we received 1,000 events, the actual occurrence count is ~10,000.

---

## Part 2: Event Processing Workers

### Source Map Deobfuscation

JavaScript deployed to production is minified. A minified stack trace looks like:

```
at t.fn (bundle.min.js:1:28947)
```

Useless. The source map maps minified position → original filename + line:

```
original: at handlePaymentSubmit (src/components/Checkout.tsx:127)
```

```python
def deobfuscate_javascript_stack(stack_frames: list[dict], 
                                  release: str, 
                                  project_id: str) -> list[dict]:
    """Apply source maps to transform minified positions to original code."""
    
    import sourcemap  # Python sourcemap library
    
    deobfuscated = []
    for frame in stack_frames:
        source_map = fetch_source_map(
            project_id=project_id,
            release=release,
            filename=frame['filename']
        )
        
        if source_map is None:
            deobfuscated.append(frame)  # can't deobfuscate, keep as-is
            continue
        
        # Map (line, column) in minified file → (filename, line, col) in original
        original = source_map.lookup(line=frame['lineno'], column=frame['colno'])
        
        deobfuscated.append({
            "filename": original.src,            # "src/components/Checkout.tsx"
            "lineno": original.src_line,         # 127
            "function": original.name or frame['function'],
            "context_line": fetch_original_line(original.src, original.src_line, release)
        })
    
    return deobfuscated
```

Source maps are uploaded to S3 as part of the deployment process (`sentry-cli upload-sourcemaps ./dist`). The worker fetches the relevant source map by `{project_id}/{release}/{filename}.map`.

---

## Part 3: Fingerprinting — The Core Algorithm

**Why does fingerprinting matter?**

Without intelligent grouping, 1B events/day = 1B separate issues. Every developer's inbox would be flooded with millions of notifications for what are essentially the same bug. Fingerprinting is the algorithm that groups events into issues.

**The basic fingerprint:**

```python
def compute_fingerprint(event: dict) -> str:
    """
    Two events with the same fingerprint are the same issue.
    Changes to fingerprint algorithm = issues get split or merged.
    """
    exception = event.get('exception', {})
    exc_type = exception.get('type', 'unknown')
    
    # Stack trace normalization: strip variable parts
    stack_frames = exception.get('stacktrace', [])
    
    # Filter to application frames only (exclude library frames)
    # Library frames (site-packages, node_modules) vary by version
    # but don't identify WHERE in YOUR code the bug is
    app_frames = [
        f for f in stack_frames
        if not is_library_frame(f['filename'])
    ]
    
    # Use the top 3 application frames in the fingerprint
    # Top = most recent (closest to where the exception was thrown)
    key_frames = app_frames[-3:] if len(app_frames) >= 3 else app_frames
    
    # Normalize each frame: just filename + function name (not line number)
    # Line numbers change when code is refactored; we want same function = same issue
    frame_keys = []
    for frame in key_frames:
        # Strip absolute path, keep relative: /app/src/payment.py → payment.py
        filename = normalize_filename(frame['filename'])
        func = frame.get('function', '<unknown>')
        frame_keys.append(f"{filename}:{func}")
    
    # Include the exception type + message prefix
    # "ValueError: invalid literal for int() with base 10: ''"
    # → strip the variable part ("''") → "ValueError: invalid literal for int() with base 10:"
    message_key = normalize_message(
        exc_type=exc_type,
        message=exception.get('value', '')
    )
    
    raw_key = "|".join([message_key] + frame_keys)
    return hashlib.sha256(raw_key.encode()).hexdigest()[:16]

def normalize_message(exc_type: str, message: str) -> str:
    """Remove variable data from error messages."""
    
    # Remove: numbers, UUIDs, file paths, IP addresses
    # "User 12345 not found" → "User <int> not found"
    # "File /tmp/abc123.tmp not found" → "File <path> not found"
    
    patterns = [
        (r'\b\d{5,}\b', '<int>'),          # long numbers (IDs)
        (r'[0-9a-f]{8}-[0-9a-f]{4}-...', '<uuid>'),  # UUIDs
        (r'/(?:tmp|var|home|app)/\S+', '<path>'),     # file paths
        (r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '<ip>'),    # IP addresses
        (r"'[^']{0,50}'", '<str>'),                    # short quoted strings
    ]
    
    normalized = f"{exc_type}: {message}"
    for pattern, replacement in patterns:
        normalized = re.sub(pattern, replacement, normalized)
    
    return normalized

def is_library_frame(filename: str) -> bool:
    library_paths = ['site-packages', 'node_modules', 'dist-packages', 
                     '/usr/lib/', 'Python3.']
    return any(path in filename for path in library_paths)
```

**Result:** Two events from different users, different request IDs, but the same `NullPointerException` in `payment.py:process_payment()` → same fingerprint → same issue. One notification, one issue to investigate.

**Custom fingerprinting (developer override):**

Sentry allows developers to set custom fingerprints:

```python
with push_scope() as scope:
    scope.fingerprint = ["database-connection", "timeout"]
    capture_exception(exc)
# All database connection timeout errors → same issue, regardless of call stack
```

---

## Part 4: Storage

### ClickHouse for Events

```sql
-- ClickHouse events table (stores raw events for 30 days)
CREATE TABLE events (
    -- Core fields
    event_id        UUID,
    project_id      UInt64,
    issue_id        UInt64,
    
    -- Exception details
    exc_type        LowCardinality(String),   -- 'NullPointerException'
    exc_message     String,
    
    -- Context
    environment     LowCardinality(String),  -- 'production', 'staging'
    release         String,
    user_id         Nullable(String),
    
    -- Timestamps
    timestamp       DateTime,
    received_at     DateTime DEFAULT now(),
    
    -- Full payload (for event detail view)
    payload         String,                   -- JSON blob with full event
    
    -- Partitioning: delete old data by dropping partition
    date            Date DEFAULT toDate(timestamp)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)      -- one partition per month
ORDER BY (project_id, issue_id, timestamp)   -- primary sort key: efficient for issue drilldowns
TTL date + INTERVAL 30 DAY DELETE;           -- auto-delete records older than 30 days
```

**Why ClickHouse, not PostgreSQL?**

At 1B events/day × 30 days = 30B rows, PostgreSQL would struggle with analytical queries like "count errors by issue over the last 7 days by hour." PostgreSQL is row-oriented — it reads every column to answer aggregation queries. ClickHouse is column-oriented: it reads only `(project_id, issue_id, timestamp)` — the three columns used in the WHERE/GROUP BY — skipping the large `payload` column entirely.

Query comparison (30B rows, 7 days, group by hour):

- PostgreSQL: sequential scan, 10-30 minutes
- ClickHouse: column scan, 2-5 seconds

**Pre-aggregated stats table** (for dashboard without hitting raw events):

```sql
CREATE TABLE issue_hourly_stats (
    project_id    UInt64,
    issue_id      UInt64,
    hour          DateTime,    -- truncated to hour
    
    event_count   UInt64,      -- how many events in this hour
    user_count    UInt64,      -- how many unique users affected (HyperLogLog estimate)
    
    -- HyperLogLog: probabilistic count of unique users
    -- Exact count: "store every user_id, COUNT(DISTINCT)" → massive storage
    -- HyperLogLog: 1.5KB of state, 1-2% error, handles billions of distinct values
    user_hll      AggregateFunction(uniq, String)
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (project_id, issue_id, hour);

-- This table is updated every minute from the raw events table
-- Dashboard queries use this instead of raw events (1000x faster)
```

### PostgreSQL for Issues

```sql
CREATE TABLE issues (
    id              BIGINT       PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    project_id      BIGINT       NOT NULL REFERENCES projects(id),
    fingerprint     CHAR(16)     NOT NULL,           -- the computed fingerprint
    
    -- Classification
    title           VARCHAR(500) NOT NULL,           -- "NullPointerException at payment.py:42"
    exc_type        VARCHAR(200) NOT NULL,
    exc_message     TEXT,
    platform        VARCHAR(50)  NOT NULL,           -- 'python', 'javascript', 'ios'
    
    -- Status
    status          ENUM('unresolved', 'resolved', 'ignored') DEFAULT 'unresolved',
    
    -- Aggregated counters (updated on every event)
    event_count     BIGINT       NOT NULL DEFAULT 0,
    user_count      INT          NOT NULL DEFAULT 0,  -- approximate (HyperLogLog)
    
    -- Timing
    first_seen      TIMESTAMP    NOT NULL,
    last_seen       TIMESTAMP    NOT NULL,
    
    -- Regression detection
    resolved_at     TIMESTAMP,           -- NULL if never resolved
    
    -- Assignment
    assigned_to     BIGINT       REFERENCES users(id),
    
    UNIQUE (project_id, fingerprint),    -- same fingerprint = same issue
    INDEX idx_project_status (project_id, status, last_seen),
    INDEX idx_project_fingerprint (project_id, fingerprint)
);
```

**Event processing (create or update issue):**

```python
def process_event(event: dict):
    # 1. Deobfuscate stack trace (if JavaScript)
    if event['platform'] == 'javascript':
        event['exception']['stacktrace'] = deobfuscate_javascript_stack(
            event['exception']['stacktrace'],
            event['release'],
            event['project_id']
        )
    
    # 2. Compute fingerprint
    fingerprint = compute_fingerprint(event)
    
    # 3. Create or update issue (atomic upsert)
    issue_id = db.execute("""
        INSERT INTO issues (project_id, fingerprint, title, exc_type, 
                           exc_message, platform, first_seen, last_seen)
        VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (project_id, fingerprint)
        DO UPDATE SET
            last_seen = NOW(),
            event_count = issues.event_count + 1,
            status = CASE 
                WHEN issues.status = 'resolved' THEN 'unresolved'  -- regression!
                ELSE issues.status
            END
        RETURNING id, status, (xmax = 0) AS is_new, 
                  (status = 'resolved' AND xmax != 0) AS is_regression
    """, (event['project_id'], fingerprint, build_title(event), ...))
    
    # 4. Store raw event in ClickHouse
    clickhouse.insert('events', [{
        'event_id': event['event_id'],
        'project_id': event['project_id'],
        'issue_id': issue_id,
        'exc_type': event['exception']['type'],
        ...
    }])
    
    # 5. Trigger alerts if needed
    if issue_id.is_new:
        trigger_new_issue_alert(issue_id, event)
    elif issue_id.is_regression:
        trigger_regression_alert(issue_id, event)
    
    return issue_id
```

---

## Part 5: Alerting Engine

### Three Alert Types

```python
class AlertEngine:
    
    # Alert Type 1: New Issue
    def evaluate_new_issue_alerts(self, issue_id: int, project_id: int):
        """Fire when a new issue is created for the first time."""
        rules = db.get_alert_rules(project_id, trigger='new_issue')
        
        for rule in rules:
            # Filter: only alert if environment matches
            if rule.environment and issue.environment != rule.environment:
                continue
            
            self.fire_alert(rule, issue_id, 
                            message=f"New issue detected: {issue.title}")
    
    # Alert Type 2: Frequency Spike (most important — catches error storms)
    def evaluate_frequency_spike_alerts(self, project_id: int):
        """
        Fire when error rate spikes suddenly.
        Strategy: compare last 1 hour to previous 24 hours average.
        If current rate > 5× baseline, alert.
        """
        rules = db.get_alert_rules(project_id, trigger='frequency_spike')
        
        for rule in rules:
            # Query ClickHouse for recent vs baseline rates
            stats = clickhouse.query("""
                SELECT
                    countIf(timestamp >= now() - INTERVAL 1 HOUR) AS last_1h,
                    countIf(timestamp < now() - INTERVAL 1 HOUR 
                            AND timestamp >= now() - INTERVAL 25 HOUR) / 24 AS baseline_1h
                FROM events
                WHERE project_id = %(project_id)s
                  AND timestamp >= now() - INTERVAL 25 HOUR
            """, {"project_id": project_id})
            
            spike_multiplier = stats['last_1h'] / max(stats['baseline_1h'], 1)
            
            if spike_multiplier > rule.threshold:
                # Deduplicate: don't re-alert if already alerted in last 15 min
                alert_key = f"alert:fired:{rule.id}"
                if not redis.set(alert_key, "1", nx=True, ex=900):  # 15 min TTL
                    continue  # already fired recently
                
                self.fire_alert(rule, 
                                message=f"Error rate spike: {spike_multiplier:.1f}× baseline")
    
    # Alert Type 3: Regression (previously resolved issue reappears)
    def evaluate_regression_alert(self, issue_id: int, project_id: int):
        """
        An issue was marked 'resolved' at some point.
        Now a new event came in with the same fingerprint.
        The fix didn't work — this is a regression.
        """
        issue = db.get_issue(issue_id)
        
        if issue.resolved_at is None:
            return  # was never resolved, not a regression
        
        rules = db.get_alert_rules(project_id, trigger='regression')
        for rule in rules:
            self.fire_alert(rule, issue_id,
                            message=f"Regression: '{issue.title}' reappeared "
                                    f"(was resolved {issue.resolved_at})")
    
    def fire_alert(self, rule: AlertRule, issue_id: int = None, message: str = ""):
        """Route alert to configured channels: email, Slack, PagerDuty, webhook."""
        
        alert = Alert(
            rule_id=rule.id,
            issue_id=issue_id,
            message=message,
            fired_at=datetime.now()
        )
        db.insert_alert(alert)
        
        for channel in rule.notification_channels:
            if channel.type == 'slack':
                slack_client.send_message(
                    webhook=channel.webhook_url,
                    text=f"[{rule.project_name}] {message}\n"
                         f"View: https://sentry.io/issues/{issue_id}/"
                )
            elif channel.type == 'email':
                email_service.send(
                    to=channel.email_list,
                    subject=f"[Sentry] {message}",
                    body=build_alert_email(alert)
                )
            elif channel.type == 'pagerduty':
                pagerduty_client.trigger_incident(
                    routing_key=channel.routing_key,
                    summary=message
                )
```

---

## Part 6: User Impact Tracking

**The killer feature:** "This error affected 1,247 unique users."

```python
# HyperLogLog for approximate unique user counting
# Why HyperLogLog? 
# Exact COUNT(DISTINCT user_id) requires storing every seen user_id
# At 1B events × 100M users = terabytes just for user tracking
# HyperLogLog: ~1.5KB of state, ~2% error, handles billions of items

# In Redis (for real-time counting):
def record_affected_user(issue_id: int, user_id: str):
    redis.pfadd(f"issue:{issue_id}:users", user_id)  # PFADD: HyperLogLog add
    # Current count estimate:
    count = redis.pfcount(f"issue:{issue_id}:users")  # PFCOUNT: HyperLogLog count
    
    # Sync to PostgreSQL periodically
    if should_sync():
        db.update(f"UPDATE issues SET user_count = {count} WHERE id = {issue_id}")

# In ClickHouse (for historical analytics):
# The issue_hourly_stats table stores uniq() aggregate state
# Merged across hours to get total unique users over any time range
```

---

## Scale — What Breaks at 10x?

> **How to transition into deep dives:** Say: *"I now have a working system that satisfies all three functional requirements. Let me harden it by addressing the non-functional requirements I identified at the start."* Then work through the NFRs one by one, starting with the most important. For each one, state the problem it creates in the current design, then your solution. After each point, pause and let the interviewer probe before moving on — do not monologue for more than two minutes at a stretch. The interviewer has specific signals they are looking for; if you are talking, they cannot ask for them. For senior roles, proactively identify the next bottleneck without waiting to be prompted.


10x = 10B events/day = 115K events/sec peak.

**Ingest API:** Stateless, horizontally scalable. 100 replicas → 1000 replicas. AWS ECS or Kubernetes auto-scaling based on CPU.

**Kafka:**

Events at 115K/sec × 2KB = 230MB/sec ingest bandwidth. Kafka can handle 1GB/sec per broker. 3-5 broker cluster sufficient. Partition events by `project_id` for ordered processing per project.

**Processing workers:**

Fingerprinting is CPU-bound (regex + SHA256). 115K events/sec at 1ms per event = 115 worker threads needed. Kafka consumer group: 100 workers consuming in parallel. Auto-scale based on consumer group lag.

**ClickHouse:**

At 10B events/day = 115K inserts/sec. Never insert one row at a time — batch inserts:

```python
# Worker buffers events for 1 second, then batch insert
buffer = []
for event in kafka_consumer:
    buffer.append(build_clickhouse_row(event))
    if len(buffer) >= 10000 or time_since_last_flush() > 1.0:
        clickhouse.bulk_insert('events', buffer)  # 10K rows in one INSERT
        buffer = []
# ClickHouse insert performance: ~500K rows/sec per server → fine
```

**PostgreSQL (issues table):**

Issue upserts: 115K events/sec but most are duplicates (same issue seen repeatedly). Actual new issues: ~1K/day across all projects. Rate limiting per project (max 1K unique issues/day/project) prevents runaway fingerprint generation.

The `ON CONFLICT DO UPDATE` upsert is efficient but creates write contention on popular issues (1 issue that fires 100K times/sec). Solution: batch counter increments using Redis:

```python
# Instead of: UPDATE issues SET event_count = event_count + 1 on every event
# Use Redis counter, flush to PostgreSQL every 30 seconds:
redis.hincrby(f"issue:counters:{issue_id}", "event_count", 1)
# Flush job (every 30s):
for issue_id, counts in redis.hgetall_batch("issue:counters:*"):
    db.execute(f"UPDATE issues SET event_count = event_count + {counts['event_count']} "
               f"WHERE id = {issue_id}")
```

---

## Trade-offs

**Sampling vs full fidelity:**

Full fidelity (capture every event): complete data, high cost, risk of overload.

Sampling (capture X% of events): reduced cost, estimated counts, miss low-volume critical errors.

**Hybrid sampling:** Head-based sampling (decide at event start): fast, simple, misses important events. Tail-based sampling (decide after seeing the full request): can sample based on outcome (always keep error traces, sample success traces at 1%), but requires keeping all traces in memory until decision. Sentry uses head-based sampling for simplicity; Jaeger supports tail-based for APM.

---

## Cross-Questions

**Q: How do you handle the same issue appearing across multiple releases/versions?**

Fingerprint is the same (same code path). Sentry groups them into one issue. But the events table stores `release` on each event. Dashboard query: "How many events for issue #123 by release?"

```sql
-- ClickHouse: event counts by release (waterfall view)
SELECT release, count() AS count
FROM events
WHERE issue_id = 123 AND timestamp >= now() - INTERVAL 7 DAY
GROUP BY release
ORDER BY count DESC;

-- Result:
-- v2.3.1: 45,892  ← new release, lots of errors
-- v2.3.0: 1,243   ← old release, some residual
-- v2.2.5: 89      ← very old, almost gone
-- → v2.3.1 introduced the regression
```

**Q: How do you handle PII in error messages?**

Error messages often contain user data: "User john.doe@email.com not found", "Invalid SSN: 123-45-6789".

Server-side scrubbing (processing worker):

```python
PII_PATTERNS = [
    (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[email]'),
    (r'\b\d{3}-\d{2}-\d{4}\b', '[ssn]'),
    (r'\b(?:\d{4}[\s-]?){3}\d{4}\b', '[credit-card]'),
]

def scrub_pii(text: str) -> str:
    for pattern, replacement in PII_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text

# Applied to: exc_message, breadcrumb data, request body (if logged)
```

SDK-side `before_send` hook (client-owned):

```python
def before_send(event, hint):
    # Remove request body entirely (might contain passwords)
    event.get('request', {}).pop('data', None)
    return event

sentry_sdk.init(dsn="...", before_send=before_send)
```

**Q: How do you build the "suspect commits" feature (which commit introduced this bug)?**

When a new issue appears in release v2.3.1:
1. Fetch the commit list between v2.3.0 (last release without this issue) and v2.3.1 from GitHub API.
2. Compare the stack trace filenames to the files changed in each commit.
3. Rank commits by: how many stack trace files did this commit touch? The highest-overlap commit is the "suspect commit."

```python
def find_suspect_commits(issue: Issue, current_release: str, 
                         previous_release: str) -> list[Commit]:
    # Get commits between the two releases
    commits = github.compare_commits(
        repo=project.github_repo,
        base=previous_release,
        head=current_release
    )
    
    # Get files in the stack trace
    stack_files = set(
        normalize_filename(frame['filename']) 
        for frame in issue.stacktrace_frames
    )
    
    # Score each commit by overlap with stack files
    scored = []
    for commit in commits:
        changed_files = set(f.filename for f in commit.files)
        overlap = len(stack_files & changed_files)
        if overlap > 0:
            scored.append((commit, overlap))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [commit for commit, score in scored[:3]]  # top 3 suspect commits
```

This feature alone makes error monitoring orders of magnitude more valuable than raw logging — developers go from "there's an error" to "these 2 commits are probably responsible" in seconds.
