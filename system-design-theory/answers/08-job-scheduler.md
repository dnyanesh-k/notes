# Q8: Design Job Scheduler

---

## Clarifying Questions

A few things to clarify first. What kind of jobs are we scheduling — one-time jobs at a specific time, recurring jobs on a cron schedule, or both? Recurring cron jobs have a different execution model.

What's the job execution model — are jobs short tasks (< 1 minute) or long-running processes (hours)? Long jobs need progress tracking and the ability to resume on failure.

What are the reliability guarantees — at-least-once execution (job might run twice on failure) or exactly-once (must never run twice, e.g., send payment)? Exactly-once is much harder.

What's the scale — how many jobs per second, and what's the largest delay we need to support (days? years)?

*Assuming: both one-time and recurring, short-to-medium jobs (< 1 hour), at-least-once with idempotency at the job level, 1M jobs/day = ~12 jobs/sec, schedule up to 1 year in the future.*

---

## Scope

I'll design: job scheduling (accepting a job with a trigger time), job dispatch (picking up jobs when their time comes and routing to workers), worker execution, retry on failure, and basic monitoring. I'll skip complex workflows (DAG of jobs with dependencies) — that's Apache Airflow territory.

---

## High Level Design

```
┌───────────┐                                                    ┌──────────────┐
│  Callers  │──POST /jobs──▶┌──────────────┐                   │              │
│(services, │               │  Scheduler   │──dispatch──▶Kafka──│   Workers    │
│ users,    │               │  API         │                    │  (stateless) │
│ cron cfg) │               └──────┬───────┘                   └──────┬───────┘
└───────────┘                      │                                   │
                                   ▼                                   │ result/heartbeat
                          ┌────────────────┐                          │
                          │  Job Store     │◀─────────────────────────┘
                          │  (MySQL)       │
                          └────────────────┘
                                   ▲
                                   │ poll for due jobs
                          ┌────────┴───────┐
                          │  Job Poller    │
                          │  (coordinator) │
                          └────────────────┘

                          ┌─────────────────────────────┐
                          │  Redis                       │
                          │  - distributed lock (elect   │
                          │    leader poller)            │
                          │  - job dedup (idempotency)   │
                          └─────────────────────────────┘
```

The core loop: Scheduler API accepts job definitions → stored in MySQL → Job Poller scans for due jobs → dispatches to Kafka → Workers execute → report results back.

---

## Low Level Design

### Data Model

```sql
CREATE TABLE jobs (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    job_type        VARCHAR(100) NOT NULL,    -- 'send_email', 'generate_report'
    payload         JSON NOT NULL,            -- job-specific parameters
    status          ENUM('pending','running','completed','failed','cancelled')
                    DEFAULT 'pending',
    scheduled_at    DATETIME NOT NULL,        -- when to run
    started_at      DATETIME,
    completed_at    DATETIME,
    attempt_count   INT DEFAULT 0,
    max_attempts    INT DEFAULT 3,
    last_error      TEXT,
    idempotency_key VARCHAR(200) UNIQUE,      -- caller provides to prevent dups
    worker_id       VARCHAR(100),             -- which worker is running this
    heartbeat_at    DATETIME,                 -- worker liveness check
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    INDEX idx_scheduled_status (scheduled_at, status),  -- the critical polling index
    INDEX idx_status_heartbeat (status, heartbeat_at)   -- detect stuck jobs
);

CREATE TABLE cron_jobs (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    name            VARCHAR(200) UNIQUE NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,    -- "0 9 * * 1-5" = weekdays 9AM
    job_type        VARCHAR(100) NOT NULL,
    payload_template JSON,
    is_active       BOOLEAN DEFAULT TRUE,
    last_run_at     DATETIME,
    next_run_at     DATETIME NOT NULL,
    INDEX idx_next_run (next_run_at, is_active)
);
```

---

### API Design

```
POST /v1/jobs
  Body: {
    "job_type": "send_invoice_email",
    "payload": { "user_id": 123, "invoice_id": 456 },
    "scheduled_at": "2026-07-01T09:00:00Z",
    "idempotency_key": "invoice-456-email",
    "max_attempts": 3
  }
  Response 201: { "job_id": 789, "status": "pending", "scheduled_at": "..." }

GET /v1/jobs/{id}
  Response 200: { "job_id": 789, "status": "running", "attempt_count": 1, ... }

DELETE /v1/jobs/{id}
  Response 200: { "status": "cancelled" }

POST /v1/cron-jobs
  Body: {
    "name": "daily_report",
    "cron_expression": "0 8 * * *",    -- every day at 8AM
    "job_type": "generate_daily_report",
    "payload_template": { "report_type": "summary" }
  }
  Response 201: { "cron_job_id": 10, "next_run_at": "2026-06-22T08:00:00Z" }
```

---

### The Job Poller — The Heart of the System

The Job Poller is a background process that runs every few seconds, scans for due jobs, and dispatches them. This is the most critical component — and the hardest to get right.

**The poll query:**

```sql
SELECT id, job_type, payload
FROM jobs
WHERE status = 'pending'
  AND scheduled_at <= NOW()
ORDER BY scheduled_at ASC
LIMIT 100
FOR UPDATE SKIP LOCKED;   -- critical: skip rows another poller instance has locked
```

`FOR UPDATE SKIP LOCKED` is the key. If you run multiple poller instances for redundancy (you should), without this, all pollers select the same 100 jobs, all try to dispatch them, and you get duplicate job execution. `SKIP LOCKED` means each poller grabs a different set of 100 rows — they don't compete.

After selecting, immediately update status to 'running' and set `worker_id` in the same transaction:

```sql
UPDATE jobs SET status = 'running', started_at = NOW(), worker_id = 'poller-1'
WHERE id IN (... selected ids ...)
```

Then publish to Kafka. The job is now "claimed" by this poller.

---

### Worker Execution and Heartbeat

Workers consume from Kafka, execute the job, and report results. Long-running jobs need a liveness mechanism — what if a worker crashes mid-execution?

**Heartbeat pattern:**

```
Worker picks up job from Kafka:
  1. Immediately update: worker_id = 'worker-3', heartbeat_at = NOW()
  2. Execute the job (could take minutes)
  3. Every 30 seconds during execution: UPDATE jobs SET heartbeat_at = NOW()
  4. On completion: UPDATE jobs SET status = 'completed', completed_at = NOW()
  5. On failure: UPDATE jobs SET status = 'failed', attempt_count = attempt_count + 1, last_error = '...'
```

**Stuck job detection:**

A separate watchdog process runs every minute:
```sql
SELECT id FROM jobs
WHERE status = 'running'
  AND heartbeat_at < NOW() - INTERVAL 2 MINUTE;
-- Worker hasn't sent heartbeat for 2 minutes → assumed dead
```

Reset these jobs to 'pending' so they can be picked up again:
```sql
UPDATE jobs SET status = 'pending', worker_id = NULL
WHERE id IN (... stuck job ids ...)
  AND attempt_count < max_attempts;

UPDATE jobs SET status = 'failed', last_error = 'worker timeout'
WHERE id IN (... stuck job ids ...)
  AND attempt_count >= max_attempts;
```

---

### Cron Job Execution

Cron jobs are different from one-time jobs — they repeat on a schedule.

```
Cron Poller (separate process, runs every minute):
  SELECT id, job_type, payload_template, cron_expression
  FROM cron_jobs
  WHERE is_active = TRUE AND next_run_at <= NOW()

For each due cron job:
  1. Insert a new row into `jobs` table (one-time job for this execution)
  2. Compute next_run_at using cron expression parser
  3. UPDATE cron_jobs SET last_run_at = NOW(), next_run_at = {computed}
```

The cron job definition is separate from execution — each cron execution creates a regular job record. History of all executions is preserved in the `jobs` table.

---

### Retry Logic with Exponential Backoff

When a job fails:
```
attempt 1 fails → retry after 1 min  (scheduled_at = NOW() + 60s)
attempt 2 fails → retry after 5 min  (scheduled_at = NOW() + 300s)
attempt 3 fails → retry after 30 min (scheduled_at = NOW() + 1800s)
attempt 4 → status = 'failed' permanently, alert ops team
```

Formula: `delay = base_delay * (2 ^ attempt_number) + random_jitter`

Jitter is important — without it, all failed jobs retry simultaneously, creating a thundering herd on the downstream service that originally caused the failure.

---

## Scale — What Breaks at 10x?

At 120 jobs/sec (10x current 12/sec):

**The poll query:** With the `(scheduled_at, status)` index, the poller scans only 'pending' rows sorted by time. At 120 insertions/sec and 120 completions/sec, the 'pending' backlog stays small. MySQL handles this easily. But if jobs pile up (worker outage), the pending set grows and the poll query slows. Fix: add a separate index on `(status, scheduled_at)` for the poller query.

**Kafka partitioning:** Partition the `jobs` topic by `job_type`. All `send_email` jobs go to partition 0, `generate_report` to partition 1, etc. This allows different worker pools per job type — email workers are separate from report workers. Scaling is independent.

**Multiple poller instances:** Run 3 poller instances. `FOR UPDATE SKIP LOCKED` ensures each polls a non-overlapping set of jobs. If one poller crashes, the other two continue. The stuck job watchdog reclaims any jobs the crashed poller claimed.

**Time precision:** If you have millions of jobs all scheduled at exactly "2026-07-01 08:00:00" (a daily batch), the poller picks them all up simultaneously. Spread them using jitter in the scheduled time — add random 0–60 second offset at registration time. Smooths the dispatch spike.

---

## Trade-offs

**MySQL vs specialized job queue (Sidekiq, Celery, BullMQ):** Purpose-built queues are easier to operate and have built-in UI. But they typically don't support scheduling far in the future (days/months), complex retry policies, or exactly-once semantics out of the box. Using MySQL gives full control — we can add custom fields, query job history with SQL, and integrate with existing infrastructure. The trade-off: we're building what open-source tools already provide. Justified when requirements are non-standard.

**At-least-once vs exactly-once:** Exactly-once requires distributed transactions across the DB and the job executor — expensive and complex. At-least-once + idempotent job handlers is the industry standard. Every job handler should be idempotent: "send invoice 456 email" checks if the email was already sent before sending. The idempotency key in the `jobs` table prevents duplicate job creation. This combination is effectively exactly-once from the business logic perspective, with simpler infrastructure.

**Polling vs event-driven (push):** We poll MySQL every few seconds, which means some jobs execute a few seconds later than their scheduled time. For truly time-critical scheduling (millisecond precision), switch to Redis sorted sets as a priority queue: `ZADD jobs_due {scheduled_at_timestamp} {job_id}`. A tight polling loop (every 100ms) on Redis gives near-millisecond precision. Trade-off: Redis is in-memory, requires persistence configuration for durability. MySQL is durable by default.

---

## Cross-Questions

**How do you prevent a job from running twice when the poller claims it but then crashes before publishing to Kafka?**

The job is in status='running' in MySQL, but never reached Kafka. The stuck job watchdog (runs every minute) detects this: `heartbeat_at < NOW() - 2 minutes`. It resets the job to 'pending'. The delay before recovery is at most 2 minutes. This is the at-least-once guarantee — a job might be retried, but never silently skipped. The job handler must be idempotent to handle this correctly.

**How do you handle a job that needs to run every 5 minutes but takes 6 minutes to execute?**

This is the overlapping execution problem. Two strategies. Strategy A: allow overlap — when the 5-minute trigger fires, create a new job execution even if the previous one is still running. This can cause race conditions. Strategy B: set a `concurrent_runs: 1` flag. The cron poller skips scheduling the next run if the previous execution is still in 'running' status. After completion, the next run is scheduled immediately from completion time + interval. LinkedIn's Azkaban scheduler uses this approach.

**How would you support job priorities?**

Add a `priority` column (1=low, 5=high) to the jobs table. Modify the poller query: `ORDER BY priority DESC, scheduled_at ASC`. High-priority jobs jump the queue. Use separate Kafka topics per priority: `jobs.priority.high`, `jobs.priority.low`. Workers dedicated to the high-priority topic drain it first. This ensures a critical payment job isn't stuck behind 1,000 low-priority email jobs.

**How would you design the job payload for a job that needs to transfer 1TB of data?**

The job payload should contain a *reference* to the data, not the data itself. `{ "s3_path": "s3://bucket/data.csv", "destination": "warehouse.table" }`. The worker fetches the data from S3, processes it in streaming fashion (never fully loading into memory), and writes to the destination. Job payload stored in MySQL should be small (< 10KB). Large data is always by reference.

**How do you build a dashboard showing job execution history and failure rates?**

The `jobs` table is the source of truth. A simple analytics query: `SELECT job_type, status, COUNT(*) FROM jobs WHERE created_at >= NOW() - INTERVAL 24 HOUR GROUP BY job_type, status`. For a richer dashboard, publish job lifecycle events (created, started, completed, failed) to a separate Kafka topic. A consumer writes to ClickHouse. Build Grafana dashboards on top: P95 execution time per job type, failure rate per job type, jobs backlog over time. Alert when failure rate > 5% for any job type.
