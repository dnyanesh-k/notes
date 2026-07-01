# Q8: Design Job Scheduler

---

> **Interview Phase Map** → Phase 1: Requirements (5 min) · Phase 2: Core Entities (2 min) · Phase 3: API Design (5 min) · Phase 4: High Level Design (12 min) · Phase 5: Deep Dives (10 min)

---

## Introduction

A job scheduler is a system that executes tasks at a specified time or on a recurring schedule, without requiring a human to trigger them manually. Sending a weekly email digest, running a nightly database cleanup, generating monthly invoices, or refreshing a cache every 5 minutes are all jobs that a scheduler manages. Cron is the simplest example, but production systems need distributed schedulers that can handle millions of jobs reliably across multiple servers.

The core requirement is **at-least-once execution** — every scheduled job must run, even if a server crashes, a process dies, or the network fails. Missing a job is usually worse than running it twice, especially for time-sensitive tasks. This reliability requirement is what makes a distributed job scheduler significantly more complex than a simple cron file on a single machine.

The design centers around a **job store** and an **executor pool**. The job store (typically a database or Redis) holds all scheduled jobs with their next execution time, status, and retry configuration. Worker processes (executors) continuously poll or listen for jobs that are due, claim them atomically (using locks or row-level locking to prevent two workers from claiming the same job), execute them, and update their status. The atomic claim step is critical — without it, the same job runs twice simultaneously.

At scale, the scheduler must handle job prioritization (some jobs are more urgent than others), retry logic with exponential backoff (failed jobs should retry after increasing delays), dead-letter queues (jobs that fail repeatedly should be flagged for human review), and distributed locking to prevent duplicate execution across multiple scheduler nodes.

Recurrence patterns (run every Monday at 9am, run on the last day of every month) add parsing and scheduling complexity. Handling timezone-aware schedules, daylight saving time transitions, and jobs that missed their window due to downtime are edge cases that separate a toy implementation from a production system.

---

## How to Approach This in an Interview

Job scheduler looks deceptively simple ("just poll a table") but the interesting challenges are: how do you poll without two servers executing the same job simultaneously (distributed locking), what happens when a worker crashes mid-execution (heartbeat + watchdog), and how do you handle exactly-once semantics. Know these three deeply.

---

## Clarifying Questions

**1. One-time or recurring jobs?**

"Are we scheduling jobs for a specific time once, or recurring cron-style jobs that repeat on a schedule?"

*Why this matters:* One-time jobs = one row per job. Cron jobs = a separate definition table, and each execution creates a one-time job record.

**2. Job duration?**

"Are jobs short tasks (< 1 minute) like sending an email, or long-running processes (hours) like ML training?"

*Why this matters:* Long jobs need liveness tracking (heartbeat). If a worker crashes mid-job, you need to detect it and retry. Short jobs don't need this complexity.

**3. Reliability guarantee?**

"If a job fails mid-execution and we retry, is it okay to run it twice (at-least-once) or must it run exactly once? For example: 'send payment confirmation email' — running twice sends two emails."

*Why this matters:* At-least-once is achievable. Exactly-once requires either distributed transactions (complex) or idempotent job handlers (simpler). Every payment system uses idempotency.

**4. Scale?**

"How many jobs per day? What's the maximum schedule horizon — days in advance, months?"

### Assumptions

```
- Both one-time and recurring (cron) jobs
- Short-to-medium jobs (< 1 hour execution)
- At-least-once with idempotent job handlers
- 1M jobs/day = ~12 jobs/sec
- Schedule up to 1 year in the future
- Delay precision: within 5 seconds of scheduled time (not millisecond precision)
- Workers are stateless, separate from scheduler
```

---

## Functional Requirements

- Users should be able to schedule a job to run once at a specific time or on a recurring cron schedule
- The system should execute jobs within 5 seconds of their scheduled time
- Users should be able to view execution history and current status per job

> **How to say this in the interview:** *"I see three core things here — schedule jobs to run once at a specific time or on a recurring cron schedule, execute them within 5 seconds of the scheduled time, and view execution history and current status for any job. Does that match your thinking?"* The "within 5 seconds" precision point is worth stating early because it rules out millisecond-precision approaches and immediately focuses the design on polling-based schedulers rather than real-time triggers.

## Non-functional Requirements

> **NFR = Non-Functional Requirements.** These answer *how the system behaves*, not *what it does*. FR = "users should be able to post a tweet" (the feature). NFR = "the feed must load in under 200ms" (the quality). Same system, completely different axis.

- **At-least-once execution**: a missed job is worse than a duplicate — all job handlers must be idempotent
- **Schedule precision within 5 seconds**: not millisecond-accurate, but reliably near the target time
- **Scale**: 1M jobs/day ≈ 12 jobs/sec; workers scale independently from the scheduler
- **Durability**: scheduled jobs must survive scheduler restarts — persisted, not in-memory
- **Scheduler HA**: single point of failure — must use leader election (e.g. ZooKeeper) or active-passive failover

> **How to say this in the interview:** After agreeing on FRs, transition with: *"Now let me think about the non-functional requirements — the qualities the system needs to have, not just the features."* Then state each of the points listed above with its specific number or reason attached. Always quantify — "the system should be fast" signals nothing; the specific path and millisecond target is what shows you understand the system. Close with: *"Any specific constraints I should factor into my design?"*
>
> **Mental checklist for any system — pick your top 3:** Run through these mentally every time: *Is stale data acceptable, or must it always be correct?* (CAP — AP or CP?), *Which specific path must be fastest, and what is the millisecond target?* (Latency), *What is the read-to-write ratio and peak QPS?* (Scale). Add Durability, Security, or Compliance only when they are the defining constraint for that particular system — do not list all eight just to look thorough.

---

## Back-of-Envelope Math

> **Interview note:** Skip this section out loud. Say: *"I'll skip capacity estimation upfront — I'll do the math only if a specific number would directly change a design decision."* Then move on. The calculations above are study material — they show you the scale of this system and tell you what to optimize for.

```
1M jobs/day = ~12 jobs/sec

Poll query: runs every 5 seconds, fetches 100 due jobs
  Index scan on (status='pending', scheduled_at <= NOW())
  With proper indexing: < 5ms per poll

MySQL throughput:
  12 insertions/sec (new jobs)
  12 status updates/sec (started, completed, failed)
  ~30 writes/sec total → trivial for MySQL

Job types:
  "send_email": high volume, fast (< 1 second)
  "generate_report": slow (1-5 minutes), low volume
  "sync_external_api": medium, depends on external
  → Separate worker pools per job type for independent scaling
```

---

## Core Entities

- **Job** — definition: name, handler, payload, schedule type (cron/one-time), cron expression, status
- **JobRun** — execution instance: job_id + start_time + end_time + status + output + retry_count
- **Worker** — stateless execution unit that polls for ready jobs from the dispatch queue

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## API Design

> **Why REST:** This is a control plane API used by other services to schedule and manage jobs — a clean CRUD pattern on a Job resource. REST provides simplicity and broad compatibility with any service that needs to call it. Status polling is also straightforward: GET the job run and check the status field. Say: *"I'll use REST — this is a control plane interface for creating and managing jobs. Other services call it to schedule work, which is a standard resource management pattern. Status polling fits naturally into REST: GET the run, check the status."*

```
POST /v1/jobs
body: { "name": string, "handler": string, "payload": object, "schedule": "once|cron", "run_at"?: timestamp, "cron"?: string }
→ 201: { "job_id": string, "next_run_at": timestamp }

GET /v1/jobs/{job_id}
→ 200: { "job": Job, "last_run": JobRun }

GET /v1/jobs/{job_id}/runs?limit=20
→ 200: { "runs": JobRun[] }

POST /v1/jobs/{job_id}/trigger
→ 202 Accepted: { "run_id": string }   ← manual trigger

DELETE /v1/jobs/{job_id}
→ 204 No Content  (cancels future runs)
```

---

## High Level Design

> **How to build this diagram in the interview — this phase matters most:** Do not draw the complete architecture upfront. Start by saying: *"Let me build the architecture by going through each endpoint one at a time."* For each endpoint: draw only the components it needs, talk through the data flow out loud as you draw — the interviewer needs to follow your reasoning, not just see boxes appearing — and add the relevant schema fields directly next to the database component in the diagram. When you spot a need for a cache, queue, or additional component mid-drawing, say *"I can see we'll need a cache here — I'm going to note that and come back to it in deep dives"*, then keep moving. Do not solve deep dive problems during this phase. Finish High Level Design only when all three functional requirements have a working data path through the diagram. The diagram above is your reference for what the final state looks like.

```
┌───────────┐                                                    ┌──────────────┐
│  Callers  │──POST /jobs──▶┌──────────────┐                   │              │
│(services, │               │  Scheduler   │──dispatch──▶Kafka──│   Workers    │
│ crons,    │               │  API         │                    │  (stateless) │
│ users)    │               └──────┬───────┘                   └──────┬───────┘
└───────────┘                      │                                   │
                                   ▼                                   │ heartbeat + result
                          ┌────────────────┐                          │
                          │  Job Store     │◀─────────────────────────┘
                          │  (MySQL)       │
                          └────────────────┘
                                   ▲
                                   │ poll for due jobs
                          ┌────────┴───────┐
                          │  Job Poller    │  ← Multiple instances
                          │  (coordinator) │    FOR UPDATE SKIP LOCKED
                          └────────────────┘
                                   
                          ┌─────────────────────────────┐
                          │  Redis                       │
                          │  - dedup idempotency keys    │
                          │  - job execution lock        │
                          └─────────────────────────────┘
```

**Why two separate components (Scheduler API + Job Poller)?**

Scheduler API is stateless and handles writes (create jobs, cancel jobs). Job Poller is the time-driven component that detects when jobs are due. Separating them allows the poller to be a single coordinated process (to avoid duplicate execution) while the API scales horizontally.

---

## Data Model

```sql
CREATE TABLE jobs (
    id              BIGINT       PRIMARY KEY AUTO_INCREMENT,
    
    job_type        VARCHAR(100) NOT NULL,
    -- Examples: 'send_invoice_email', 'generate_monthly_report', 'sync_crm'
    -- Workers are registered per job_type — the right worker picks up the right job
    
    payload         JSON         NOT NULL,
    -- Job-specific parameters. The worker reads this to know what to do.
    -- Example: { "user_id": 123, "invoice_id": 456, "currency": "USD" }
    -- Should be small (< 10KB). Large data should be by reference (S3 path).
    
    status          ENUM('pending', 'running', 'completed', 'failed', 'cancelled')
                    DEFAULT 'pending',
    
    scheduled_at    DATETIME     NOT NULL,
    -- When should this job run? If NOW() >= scheduled_at, it's eligible.
    -- Future jobs sit here until their time comes.
    
    started_at      DATETIME,        -- set when a worker picks it up
    completed_at    DATETIME,        -- set when worker finishes
    
    attempt_count   INT          DEFAULT 0,
    max_attempts    INT          DEFAULT 3,
    last_error      TEXT,            -- last failure message for debugging
    
    idempotency_key VARCHAR(200) UNIQUE,
    -- Caller provides this to prevent duplicate jobs.
    -- Example: "invoice-456-email-send" 
    -- If the caller retries the API call, we return the existing job, not create a new one.
    
    worker_id       VARCHAR(100),
    -- Which worker instance is currently executing this job.
    -- Useful for debugging: "worker-3 was executing job 789 when it crashed"
    
    heartbeat_at    DATETIME,
    -- Worker updates this every 30 seconds while job is running.
    -- If heartbeat_at < NOW() - 2 minutes, worker is assumed dead.
    
    priority        INT          DEFAULT 5,
    -- 1 = highest, 10 = lowest. High-priority jobs are dispatched first.
    
    created_at      DATETIME     NOT NULL DEFAULT NOW(),
    
    -- CRITICAL INDEXES:
    INDEX idx_scheduled_status (status, scheduled_at),
    -- Used by poller: WHERE status='pending' AND scheduled_at <= NOW()
    -- Must be composite — MySQL only uses one index per query
    
    INDEX idx_status_heartbeat (status, heartbeat_at),
    -- Used by watchdog: WHERE status='running' AND heartbeat_at < NOW()-2min
    
    INDEX idx_idempotency (idempotency_key),
    -- Used by API: check for duplicate job before inserting
    
    INDEX idx_worker (worker_id, status)
    -- Used to find all jobs assigned to a specific worker
);

CREATE TABLE cron_jobs (
    id                  BIGINT       PRIMARY KEY AUTO_INCREMENT,
    name                VARCHAR(200) UNIQUE NOT NULL,  -- human-readable identifier
    cron_expression     VARCHAR(100) NOT NULL,
    -- Standard cron: "0 9 * * 1-5" = 9 AM on weekdays
    -- "*/5 * * * *" = every 5 minutes
    -- "0 0 1 * *"  = midnight on first of every month
    
    job_type            VARCHAR(100) NOT NULL,
    payload_template    JSON,        -- template, may contain variables
    is_active           BOOLEAN      DEFAULT TRUE,
    
    last_run_at         DATETIME,
    next_run_at         DATETIME     NOT NULL,
    -- Pre-computed from cron_expression to avoid parsing on every poll
    
    INDEX idx_next_run (next_run_at, is_active)
);
```

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## API Design

```
POST /v1/jobs
  Purpose: Schedule a one-time job
  Body: {
    "job_type": "send_invoice_email",
    "payload": { "user_id": 123, "invoice_id": 456 },
    "scheduled_at": "2026-07-01T09:00:00Z",  ← future time, or NOW() for immediate
    "idempotency_key": "invoice-456-email",
    "max_attempts": 3,
    "priority": 3  ← higher priority (1=urgent, 10=background)
  }
  Response 201:
    { "job_id": 789, "status": "pending", "scheduled_at": "2026-07-01T09:00:00Z" }

GET /v1/jobs/{id}
  Response 200:
    {
      "job_id": 789,
      "status": "running",
      "attempt_count": 1,
      "started_at": "2026-06-22T10:30:45Z",
      "worker_id": "worker-3"
    }

DELETE /v1/jobs/{id}
  Purpose: Cancel a pending job (can't cancel running jobs)
  Response 200: { "status": "cancelled" }

POST /v1/cron-jobs
  Purpose: Register a recurring cron job
  Body: {
    "name": "daily_digest_email",
    "cron_expression": "0 8 * * *",  ← every day at 8 AM UTC
    "job_type": "send_daily_digest",
    "payload_template": { "report_type": "summary" }
  }
  Response 201:
    { "cron_job_id": 10, "next_run_at": "2026-06-23T08:00:00Z" }
```

---

## The Job Poller — Core of the System

The Job Poller is a background process that runs every few seconds, checks for due jobs, and dispatches them to workers. This is the most critical and tricky component.

**The poll query:**

```sql
-- SELECT jobs that are due and not already running
SELECT id, job_type, payload, priority
FROM jobs
WHERE status = 'pending'
  AND scheduled_at <= NOW()
ORDER BY priority ASC, scheduled_at ASC   -- highest priority first
LIMIT 100
FOR UPDATE SKIP LOCKED;                   -- THE KEY CLAUSE
```

**What does `FOR UPDATE SKIP LOCKED` do?**

Without it:

```
Scenario: 2 Poller instances running (for redundancy)
Poller 1: SELECT 100 pending jobs → gets jobs [1, 2, 3, 4, ...]
Poller 2: SELECT 100 pending jobs → gets THE SAME jobs [1, 2, 3, 4, ...]
Poller 1: dispatches job 1 to Kafka
Poller 2: dispatches job 1 to Kafka AGAIN
Job 1 runs twice!
```

With `FOR UPDATE SKIP LOCKED`:

```
Poller 1: SELECT ... FOR UPDATE SKIP LOCKED
  → acquires row locks on jobs [1-100]
  → Other transactions see these rows as locked
  
Poller 2: SELECT ... FOR UPDATE SKIP LOCKED  (runs milliseconds later)
  → Sees rows 1-100 are locked
  → SKIP LOCKED means: skip locked rows, take the next available
  → Gets jobs [101-200]
  
Result: no overlap. Each job is dispatched by exactly one poller.
```

`FOR UPDATE` takes a row-level write lock. `SKIP LOCKED` skips rows that are already locked (instead of waiting for them). This is MySQL 8.0+ and PostgreSQL 9.5+.

**Full poller loop:**

```python
class JobPoller:
    def __init__(self, worker_id: str):
        self.worker_id = worker_id
    
    def run_poll_loop(self):
        while True:
            self.poll_and_dispatch()
            time.sleep(5)  # poll every 5 seconds
    
    def poll_and_dispatch(self):
        with db.begin_transaction() as txn:
            # Claim jobs atomically
            jobs = txn.execute("""
                SELECT id, job_type, payload, priority
                FROM jobs
                WHERE status = 'pending'
                  AND scheduled_at <= NOW()
                ORDER BY priority ASC, scheduled_at ASC
                LIMIT 100
                FOR UPDATE SKIP LOCKED
            """)
            
            if not jobs:
                txn.rollback()
                return
            
            job_ids = [j.id for j in jobs]
            
            # Mark as 'running' WITHIN THE SAME TRANSACTION
            # Critical: the status update and the lock must be in one transaction
            txn.execute("""
                UPDATE jobs 
                SET status = 'running',
                    started_at = NOW(),
                    worker_id = ?,
                    attempt_count = attempt_count + 1
                WHERE id IN (?)
            """, (self.worker_id, job_ids))
            
            txn.commit()  # releases the FOR UPDATE locks
        
        # Now dispatch to Kafka (outside the transaction)
        for job in jobs:
            kafka_producer.send(
                topic=f"jobs.{job.job_type}",  # separate topic per job type
                key=str(job.id),
                value=json.dumps({
                    "job_id": job.id,
                    "job_type": job.job_type,
                    "payload": job.payload
                })
            )
```

**Why commit the transaction before Kafka publish?**

If we published to Kafka inside the transaction and the Kafka publish succeeded but the DB commit failed:
- Job is in Kafka, but still 'pending' in DB
- Next poll picks it up again → double execution

If we commit DB first and then Kafka publish fails:
- Job is 'running' in DB, not in Kafka
- Stuck job watchdog detects no heartbeat after 2 minutes
- Resets to 'pending', re-dispatched

Committing DB first + handling stuck jobs = safer behavior.

---

## Worker Execution and Heartbeat

Workers consume from Kafka and execute jobs. For jobs that take more than a minute, we need liveness tracking.

```python
class JobWorker:
    def process_job(self, message: KafkaMessage):
        job_id = message.value['job_id']
        payload = message.value['payload']
        
        # Update: I'm alive and starting
        db.update_job(job_id, worker_id=self.worker_id, heartbeat_at=now())
        
        # Start heartbeat thread
        heartbeat_thread = threading.Thread(
            target=self.send_heartbeats,
            args=(job_id,),
            daemon=True
        )
        heartbeat_thread.start()
        
        try:
            # Execute the actual job
            handler = self.get_handler(message.value['job_type'])
            result = handler.execute(payload)
            
            # Success
            db.update_job(job_id, 
                         status='completed', 
                         completed_at=now(), 
                         result=result)
            kafka_consumer.commit(message.offset)
            
        except Exception as e:
            # Failure
            db.update_job(job_id,
                         status='pending',  # reset to pending for retry
                         attempt_count_increment=0,  # already incremented at dispatch
                         last_error=str(e))
            kafka_consumer.commit(message.offset)  # don't re-queue from Kafka
            # Retry will happen at next poller run (after exponential backoff delay)
        
        finally:
            heartbeat_thread.stop()
    
    def send_heartbeats(self, job_id: int):
        while not self.stopped:
            time.sleep(30)  # heartbeat every 30 seconds
            db.update_job(job_id, heartbeat_at=now())
```

---

## Stuck Job Watchdog

A separate process (or periodic Airflow task) detects workers that died mid-execution:

```python
def detect_and_recover_stuck_jobs():
    """Run every minute."""
    
    # Find jobs where worker hasn't sent heartbeat for 2+ minutes
    stuck_jobs = db.execute("""
        SELECT id, attempt_count, max_attempts, job_type
        FROM jobs
        WHERE status = 'running'
          AND heartbeat_at < NOW() - INTERVAL 2 MINUTE
    """)
    
    for job in stuck_jobs:
        if job.attempt_count < job.max_attempts:
            # Can retry: reset to pending with backoff delay
            delay_seconds = calculate_retry_delay(job.attempt_count)
            
            db.update_job(job.id,
                         status='pending',
                         scheduled_at=now() + timedelta(seconds=delay_seconds),
                         worker_id=None,
                         last_error=f"Worker timeout at attempt {job.attempt_count}")
            
            log.warning(f"Job {job.id} ({job.job_type}) stuck, reset to pending. "
                       f"Retry in {delay_seconds}s")
        
        else:
            # Exhausted retries: permanently failed
            db.update_job(job.id,
                         status='failed',
                         last_error=f"Worker timeout after {job.max_attempts} attempts")
            
            alert_ops(f"Job {job.id} permanently failed after {job.max_attempts} attempts")

def calculate_retry_delay(attempt_count: int) -> int:
    """Exponential backoff with jitter."""
    base = 60  # 1 minute base
    delay = base * (2 ** (attempt_count - 1))  # 60, 120, 240, 480...
    jitter = random.uniform(0, delay * 0.2)     # ±20% jitter
    return int(delay + jitter)
```

**The delay progression:**

```
Attempt 1 → failure → wait 60±12 seconds → Attempt 2
Attempt 2 → failure → wait 120±24 seconds → Attempt 3
Attempt 3 → failure → PERMANENTLY FAILED, alert ops

Why jitter?
Without jitter: if 100 jobs all fail at the same time (downstream service outage),
they all retry at exactly the same time → second spike → same outage → repeat.
With jitter: retries spread over 20% of the delay window → gradual recovery.
```

---

## Cron Job Execution

```python
class CronPoller:
    """Separate from the job poller. Runs every minute."""
    
    def poll(self):
        # Find cron jobs whose next_run_at has passed
        due_crons = db.execute("""
            SELECT id, job_type, payload_template, cron_expression, name
            FROM cron_jobs
            WHERE is_active = TRUE 
              AND next_run_at <= NOW()
            FOR UPDATE SKIP LOCKED
        """)
        
        for cron in due_crons:
            # 1. Create a one-time job for this execution
            job_id = db.insert_job(
                job_type=cron.job_type,
                payload=cron.payload_template,
                scheduled_at=cron.next_run_at,  # use the scheduled time, not NOW()
                idempotency_key=f"cron-{cron.id}-{cron.next_run_at.isoformat()}"
            )
            
            # 2. Compute next run time
            next_run = compute_next_cron_time(cron.cron_expression)
            
            # 3. Update cron definition
            db.update_cron(cron.id,
                          last_run_at=cron.next_run_at,
                          next_run_at=next_run)
        
        db.commit()

def compute_next_cron_time(cron_expression: str) -> datetime:
    """Parse cron expression and find next run time."""
    # Use croniter library (Python)
    from croniter import croniter
    cron = croniter(cron_expression, datetime.now(timezone.utc))
    return cron.get_next(datetime)
```

**Why create a one-time job record per cron execution?**

Execution history is preserved. You can query: "Show me all executions of the daily_report cron job in the last 30 days, with their durations and results." This is stored in the `jobs` table as regular job records.

---

## Scale — What Breaks at 10x?

> **How to transition into deep dives:** Say: *"I now have a working system that satisfies all three functional requirements. Let me harden it by addressing the non-functional requirements I identified at the start."* Then work through the NFRs one by one, starting with the most important. For each one, state the problem it creates in the current design, then your solution. After each point, pause and let the interviewer probe before moving on — do not monologue for more than two minutes at a stretch. The interviewer has specific signals they are looking for; if you are talking, they cannot ask for them. For senior roles, proactively identify the next bottleneck without waiting to be prompted.


10x = 120 jobs/sec, 10.3M jobs/day.

**Poll query performance:** The index `(status, scheduled_at)` makes the poll query fast — it only scans pending jobs sorted by schedule time. At 120 insertions/sec and 120 completions/sec, the pending backlog stays small (a few hundred rows). MySQL handles this easily.

But if workers fall behind (downstream outage): pending backlog grows to millions of rows. The index becomes less selective. Fix: add a Redis sorted set as a fast pending queue `ZADD jobs:pending {scheduled_at_timestamp} {job_id}`. Poller reads from Redis, MySQL remains the source of truth.

**Multiple poller instances:** Run 3 pollers. `FOR UPDATE SKIP LOCKED` ensures no overlap. If one crashes, the other two continue. The stuck job watchdog reclaims jobs that the crashed poller claimed.

**Kafka partitioning:** Partition `jobs.send_email` topic by `user_id` (consistent distribution). Partition `jobs.generate_report` topic by `org_id`. Each worker pool has a dedicated consumer group per topic.

**Clock skew:** Pollers run on different servers. If Server 1's clock is 30 seconds behind Server 2's, Server 1 might not see jobs that Server 2 would dispatch. Use NTP to keep server clocks synchronized. For critical timing, use the database server's `NOW()` function (all pollers use the DB's clock, eliminating skew).

---

## Trade-offs

**MySQL vs Redis sorted set as the scheduling queue:**

Redis sorted set `ZADD jobs:pending {scheduled_at} {job_id}` is natural for time-based queuing — `ZRANGEBYSCORE 0 current_time LIMIT 100` gives you due jobs in O(log N + K). Very fast.

But: Redis loses data if not persisted (AOF or RDB), and sorted sets don't have row-level locking (`SKIP LOCKED` equivalent). Two pollers can get the same jobs.

MySQL: slower for range queries but has `FOR UPDATE SKIP LOCKED`, full ACID transactions, and durability by default. Better for correctness. The extra 5ms per poll is irrelevant at 12 jobs/sec.

For < 10K jobs/sec: MySQL. For > 10K jobs/sec: Redis sorted set with distributed lock (Redlock) for claiming.

**At-least-once vs exactly-once:**

Exactly-once: requires distributed transactions across Kafka + MySQL. The job handler must be invoked exactly once. This is very hard (2-phase commit).

At-least-once + idempotent handlers: the handler checks before executing: "Has this job already been done?" If yes, return success without re-executing.

```python
def send_invoice_email(payload: dict):
    invoice_id = payload['invoice_id']
    
    # Idempotency check: has this email already been sent?
    if db.get_email_sent_flag(invoice_id, 'invoice_send'):
        log.info(f"Invoice {invoice_id} email already sent, skipping")
        return
    
    # Send the email
    email_service.send(template="invoice", to=payload['user_email'], 
                      data=payload)
    
    # Record that we sent it
    db.set_email_sent_flag(invoice_id, 'invoice_send')
```

This combination (at-least-once dispatch + idempotent handler) is effectively exactly-once behavior. It's the industry standard — Stripe, Twilio, AWS all use this pattern.

---

## Cross-Questions

**Q: `FOR UPDATE SKIP LOCKED` — what exactly is happening in MySQL?**

When you run `SELECT ... FOR UPDATE`, MySQL acquires a write lock on each row in the result set. No other transaction can lock these rows until you commit or rollback.

`SKIP LOCKED` modifies this: instead of waiting for locked rows (the default) or failing, it just skips locked rows and continues to the next available row.

Without `SKIP LOCKED` and two pollers:
```
Poller 1: SELECT ... FOR UPDATE → acquires locks on rows 1-100
Poller 2: SELECT ... FOR UPDATE → WAITS for Poller 1 to release locks
Poller 1: commits → releases locks
Poller 2: SELECT ... FOR UPDATE → acquires locks on rows 1-100 (same rows!)
→ Both pollers process the same jobs sequentially
```

With `SKIP LOCKED`:
```
Poller 1: SELECT ... FOR UPDATE SKIP LOCKED → acquires locks on rows 1-100
Poller 2: SELECT ... FOR UPDATE SKIP LOCKED → rows 1-100 are locked, SKIP them
  → acquires locks on rows 101-200
→ Pollers process different jobs in parallel, no overlap
```

This is a PostgreSQL feature first (9.5), added to MySQL in 8.0.

**Q: How do you prevent a job from running twice when the poller claims it but crashes before Kafka publish?**

```
Sequence of events:
1. Poller claims job 789 (status → 'running' in DB)
2. Kafka publish fails / poller crashes
3. Job is 'running' but never in Kafka
4. Worker never picks it up
5. No heartbeat sent

Stuck job watchdog (runs every minute):
  Detects: heartbeat_at IS NULL AND status='running' AND started_at < NOW()-2min
  → This means no worker ever started it (heartbeat was never set)
  → Reset to 'pending', schedule_at = NOW() (retry immediately)
  → Job is picked up on next poll cycle

Total delay: up to 2 minutes before recovery.
This is the at-least-once guarantee: job might run later, never silently skipped.
```

**Q: How would you support job priorities in the Kafka consumer setup?**

```
Kafka topics per priority:
  jobs.high    → worker pool dedicated to high-priority jobs
  jobs.medium  → default worker pool  
  jobs.low     → background worker pool (can be starved when high-priority backlog exists)

Worker pool allocation:
  High: 10 workers (never starved)
  Medium: 20 workers
  Low: 5 workers (can be scaled down when high-priority needs resources)

In Kubernetes: auto-scale worker Deployments based on Kafka consumer lag.
High-priority consumer lag > 100 → scale up high workers.
```

**Q: How would you build a monitoring dashboard for job health?**

```python
# ClickHouse for analytics (high-write, time-series queries)
# Every job lifecycle event published to Kafka → consumed by ClickHouse writer

# Key metrics queries:
# "What's the P95 execution time for each job type in the last 24h?"
SELECT 
    job_type,
    quantile(0.95)(DATEDIFF('second', started_at, completed_at)) AS p95_duration_secs,
    countIf(status='failed') / count() AS failure_rate,
    count() AS total_jobs
FROM job_events
WHERE created_at >= NOW() - INTERVAL 1 DAY
  AND status IN ('completed', 'failed')
GROUP BY job_type
ORDER BY failure_rate DESC;

# "Is there a job backlog growing?"
SELECT 
    toStartOfMinute(created_at) AS minute,
    countIf(status='pending') AS backlog_size
FROM jobs
WHERE created_at >= NOW() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute;

# Alerting:
# - Any job type with failure_rate > 5% → PagerDuty
# - Backlog growing faster than workers can drain → Slack warning
# - Any job stuck in 'running' for > 30 minutes → immediate alert
```
