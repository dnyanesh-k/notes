# Q3: Design Notification System

---

## Introduction

A notification system is responsible for delivering messages to users across multiple channels — push notifications on mobile, emails, SMS, and in-app alerts. It is a backend infrastructure component that sits between the event-producing services and the user-facing delivery channels. Almost every modern application — social media, e-commerce, banking, SaaS — relies on a notification system to communicate with its users.

The core flow is straightforward: something happens in the system (a new message, a payment, a friend request), and the notification service is triggered to inform the relevant user. But at scale, this simple flow becomes complex. Millions of events can fire simultaneously, and each one may need to be delivered to thousands of users across different devices and time zones.

The primary challenges are reliability and scale. Notifications must be delivered at least once — a missed payment alert or a failed OTP delivery is unacceptable. At the same time, the system must avoid duplicate notifications, which are annoying to users and can undermine trust. This requires careful use of message queues, idempotency keys, and delivery tracking.

Delivery channels each have their own complexity. Push notifications go through third-party providers like APNs (Apple-Apple Push Notification) and FCM (Google-Firebase Cloud Messaging), which have their own rate limits and delivery guarantees. Emails require handling bounces, unsubscribes, and spam scoring. SMS is expensive and has strict character limits. A well-designed notification system abstracts these channels behind a unified interface so the rest of the application does not need to know which channel is being used.

Additional considerations include user preferences (opt-in/opt-out per channel), notification templates, prioritization (critical alerts vs promotional), and observability to track delivery success and failure rates.

---

## How to Approach This in an Interview

Notification systems look simple but have a surprising number of failure modes. The interesting parts are: fan-out at scale (5M users need the same message), third-party provider failures (FCM goes down), and deduplication (same notification sent twice because of a retry). Know these deeply.

---

## Clarifying Questions

**1. What channels do we support?**

"Are we handling push notifications (mobile), email, SMS, or in-app notifications? Each has a completely different delivery mechanism."

*Why this matters:* Push goes through Apple APNs and Google FCM — you don't control the last mile. Email goes through SendGrid/SES. SMS through Twilio. In-app is just a DB query on app open. Different reliability guarantees, different latency, different costs.

**2. What triggers a notification?**

"Is this event-driven (user A liked your post → notify user B) or scheduled campaigns (weekly digest email to 5M users) or system alerts (your payment failed)?"

*Why this matters:* Event-driven needs a pub-sub pipeline. Scheduled campaigns need a batch fan-out system that doesn't hammer FCM all at once. System alerts need very low latency.

**3. What's the scale?**

"How many notifications per day? And what's the peak — is it uniform or spiky? A campaign blast to 5M users is very different from steady 10K/sec."

*Why this matters:* A 5M-user blast in 30 seconds = 166K notifications/sec. Your pipeline and third-party provider limits must handle spikes.

**4. Delivery guarantees?**

"If a notification fails, do we retry? How many times? And is it acceptable to send the same notification twice (at-least-once) or must we guarantee exactly-once?"

*Why this matters:* At-least-once (might deliver twice) is much easier to build than exactly-once. For most notifications (like posts, alerts), duplicates are acceptable. For payment confirmation emails, duplicates are bad UX.

### Assumptions

```
- Channels: push (FCM + APNs), email (SendGrid), SMS (Twilio)
- Both event-driven and scheduled campaigns
- 10M notifications/day average, 5M in a single campaign blast
- Push: sub-5-second delivery. Email: within 1 minute. SMS: within 30 seconds.
- At-least-once with idempotency key to prevent logical duplicates
- Retry up to 3 times with exponential backoff
- User preferences: can opt out per channel, set quiet hours
```

---

## Back-of-Envelope Math

```
10M notifications/day
Spread over 16 active hours = 625K/hour = ~175/sec average

Campaign blast: 5M notifications in 10 minutes
= 500K/minute = ~8,333/sec for those 10 minutes

FCM throughput limit: varies, but assume ~10K/sec per connection
→ Need to manage delivery rate to stay within provider limits

Storage:
  Each notification record: ~500 bytes (content + metadata + status)
  10M/day × 30 days × 500 bytes = ~150 GB/month
  → PostgreSQL or MySQL with monthly partitions
```

---

## High Level Design

```
┌────────────────┐     ┌──────────────────────────────────────────────┐
│  Event Sources  │     │           Notification Service                │
│                 │     │                                               │
│ • Order Service │     │  ┌──────────────┐    ┌───────────────────┐  │
│ • Payment Svc   │────▶│  │  Notification │    │   Kafka Topics    │  │
│ • User Service  │     │  │     API       │───▶│                   │  │
│ • Campaign Svc  │     │  └──────────────┘    │ • push.pending    │  │
│ • Scheduler     │     │                       │ • email.pending   │  │
└────────────────┘     │                       │ • sms.pending     │  │
                        │                       │ • notif.retry     │  │
                        │                       └─────────┬─────────┘  │
                        └─────────────────────────────────┼────────────┘
                                                          │
                    ┌─────────────────────────────────────┼──────────────────────┐
                    │                   Workers            │                      │
                    │                                      │                      │
          ┌─────────▼──────┐   ┌──────────────┐   ┌──────▼────────┐            │
          │  Push Worker   │   │ Email Worker  │   │  SMS Worker   │            │
          └────────┬───────┘   └──────┬────────┘   └──────┬────────┘            │
                   │                  │                    │                      │
                   ▼                  ▼                    ▼                      │
          ┌────────────────┐  ┌──────────────┐  ┌───────────────┐              │
          │ APNs (iOS)     │  │  SendGrid /  │  │  Twilio /     │              │
          │ FCM (Android)  │  │  AWS SES     │  │  AWS SNS      │              │
          └────────────────┘  └──────────────┘  └───────────────┘              │
```

**Why separate workers per channel?**

FCM, APNs, SendGrid, and Twilio have different rate limits, different failure modes, and different retry policies. If you mix them, a FCM slowdown blocks your email workers too. Separate workers mean each channel scales and fails independently.

**Why Kafka in the middle?**

Without Kafka: the Notification API directly calls FCM. If FCM is slow (5 seconds), the API blocks for 5 seconds per request. During a 5M campaign, the API would queue up millions of pending FCM calls in memory → OOM crash.

With Kafka: the API enqueues instantly (milliseconds). Workers consume at whatever rate FCM can handle. The queue absorbs the burst. If FCM is down for an hour, messages wait in Kafka — nothing is lost.

---

## What is FCM and APNs?

**FCM (Firebase Cloud Messaging):** Google's push notification service for Android. When you install an Android app, the device registers with Google and gets a **device token** — a unique string like `dJR_abc...xyz`. Your server sends a notification to FCM with this token, and FCM delivers it to the specific device over a persistent connection that Android maintains with Google's servers.

**APNs (Apple Push Notification service):** Same concept for iOS. Every iPhone maintains a persistent connection to Apple's servers. Your server sends to APNs, APNs delivers to the specific device.

**Why use APNs/FCM instead of your own push server?**

Your server can't maintain persistent connections to billions of mobile devices — the TCP connection overhead alone would require thousands of servers. Apple and Google maintain these connections globally. You only need to call their API with the device token and payload. They handle delivery, queueing when the device is offline, and retrying when the device wakes up.

**Device token lifecycle:**

```
User installs app → App registers with FCM/APNs → Gets token → 
App sends token to your server → You store it

User uninstalls app → Token becomes invalid
FCM/APNs returns "BadDeviceToken" when you try to send to it
→ You mark the token inactive in your DB
→ Stop sending to it

User reinstalls app → New token generated → 
App sends new token to your server → Update the DB
```

---

## Low Level Design

### Data Model

```sql
-- Track every notification sent (source of truth for status + retries)
CREATE TABLE notifications (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT NOT NULL,
    type            VARCHAR(50) NOT NULL,
    -- Examples: 'order_shipped', 'payment_failed', 'friend_request'
    
    channel         ENUM('push', 'email', 'sms') NOT NULL,
    
    status          ENUM('pending', 'sent', 'delivered', 'failed') 
                    NOT NULL DEFAULT 'pending',
    
    content         JSON NOT NULL,
    -- { "title": "Your order shipped", "body": "...", "deep_link": "app://..." }
    
    idempotency_key VARCHAR(100) UNIQUE,
    -- Caller provides this to prevent duplicates on retry.
    -- If key already in DB, return existing record, don't re-send.
    -- Example: "order-789-shipped-push" (unique per event + channel)
    
    attempt_count   INT NOT NULL DEFAULT 0,
    max_attempts    INT NOT NULL DEFAULT 3,
    last_attempted  DATETIME,
    sent_at         DATETIME,    -- when actually sent to provider
    error_message   TEXT,        -- last failure reason
    
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    
    INDEX idx_user_id (user_id),
    INDEX idx_status_created (status, created_at),   -- for retry queries
    INDEX idx_idempotency (idempotency_key)           -- fast dedup lookup
);

-- Per-user delivery preferences and device tokens
CREATE TABLE user_notification_prefs (
    user_id         BIGINT PRIMARY KEY,
    email           VARCHAR(200),
    phone           VARCHAR(20),
    
    push_enabled    BOOLEAN DEFAULT TRUE,
    email_enabled   BOOLEAN DEFAULT TRUE,
    sms_enabled     BOOLEAN DEFAULT TRUE,
    
    -- Don't send push between these hours (user's local time)
    quiet_hours_start TIME,           -- e.g., '22:00:00'
    quiet_hours_end   TIME,           -- e.g., '07:00:00'
    timezone          VARCHAR(50) DEFAULT 'UTC'
);

-- Each device = one row (user may have multiple devices)
CREATE TABLE device_tokens (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id     BIGINT NOT NULL,
    token       VARCHAR(500) NOT NULL,
    platform    ENUM('ios', 'android', 'web') NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    registered_at DATETIME NOT NULL,
    updated_at  DATETIME NOT NULL,
    
    UNIQUE KEY uk_token (token),
    INDEX idx_user_id (user_id)
);
```

---

### API Design

```
POST /v1/notifications
  Purpose: Send one notification to one user on specified channels
  Body:
    {
      "user_id": 12345,
      "type": "order_shipped",
      "channels": ["push", "email"],    ← which channels to use
      "idempotency_key": "order-789-shipped",  ← caller provides
      "content": {
        "title": "Your order has shipped",
        "body": "Arrives by June 25. Track: bit.ly/xyz",
        "deep_link": "app://orders/789"
      },
      "priority": "high"    ← high = deliver immediately, low = can batch
    }
  Response 202 Accepted:
    { "notification_id": 456, "status": "queued" }
    
  Why 202 and not 201?
  202 = "I've accepted your request but haven't completed it yet."
  The actual delivery happens asynchronously — we haven't sent to FCM yet,
  just queued it. 201 would imply completion.

POST /v1/notifications/batch
  Purpose: Send same notification to many users (campaign)
  Body:
    {
      "user_ids": [1, 2, 3, ...],    ← up to 10,000 per call
      "type": "weekly_digest",
      "channels": ["email"]
    }
  Response 202:
    { "batch_id": "batch_abc", "queued_count": 5000 }
    
  For 5M users: caller makes 500 batch API calls × 10K users each.
  Or: caller pushes user_ids to an S3 file, we read it asynchronously.

GET /v1/notifications/{id}/status
  Response 200:
    { 
      "status": "delivered",
      "sent_at": "2026-06-22T10:30:45Z",
      "attempt_count": 1,
      "channel": "push"
    }
```

---

### The Write Path — Step by Step

When `POST /v1/notifications` arrives:

```
Step 1: Notification API receives request
        - Validate JWT, extract caller service identity
        - Validate body (user_id exists? content valid? channel supported?)

Step 2: Idempotency check
        SELECT id, status FROM notifications
        WHERE idempotency_key = 'order-789-shipped'
        
        If found: return existing notification (don't re-send)
        If not found: continue
        
        Why: Order Service might retry this call if it gets a network timeout.
        Without this check, the user gets two "Your order shipped" notifications.

Step 3: Fetch user preferences (from Redis cache or DB)
        GET user_prefs:{user_id}
        
        Returns: {
          push_enabled: true,
          quiet_hours: null,       ← null = no quiet hours set
          device_tokens: [         ← cached for 5 minutes
            { token: "dJR_...", platform: "android" },
            { token: "aXY_...", platform: "ios" }   ← 2 devices
          ]
        }
        
        If user has disabled push: skip push channel
        If in quiet hours: skip push, or delay until quiet hours end

Step 4: Create notification record(s) in DB
        For each eligible channel × each device:
          INSERT INTO notifications (user_id, type, channel, content, 
                                     idempotency_key, status)
          User has 2 devices → 2 push notification rows + 1 email row = 3 records
        
Step 5: Publish to Kafka
        For each notification record:
          Publish to appropriate topic:
          - push.pending: { notif_id: 456, token: "dJR_...", platform: "android", content: {...} }
          - push.pending: { notif_id: 457, token: "aXY_...", platform: "ios", content: {...} }
          - email.pending: { notif_id: 458, to: "user@email.com", content: {...} }
        
Step 6: Return 202 to caller
        Caller gets response in ~5ms — before any actual delivery happens.
```

---

### The Delivery Path — Push Worker Step by Step

Push Worker consumes from `push.pending` Kafka topic:

```
Step 1: Pick up message from Kafka
        { notif_id: 456, token: "dJR_...", platform: "android", content: {...} }

Step 2: Update DB status to 'sending'
        UPDATE notifications SET status='sending', last_attempted=NOW(),
               attempt_count=attempt_count+1 WHERE id=456

Step 3: Call FCM or APNs based on platform
        
        For Android (FCM):
        response = fcm_client.send({
          "to": "dJR_...",   ← device token
          "notification": {
            "title": "Your order has shipped",
            "body": "Arrives by June 25"
          },
          "data": {
            "deep_link": "app://orders/789"
          }
        })
        
        For iOS (APNs):
        response = apns_client.send_notification(
          device_token="aXY_...",
          alert=APNsAlert(title="Your order has shipped", body="..."),
          data={"deep_link": "app://orders/789"}
        )

Step 4: Handle the response
        
        If SUCCESS (FCM returns 200, APNs returns 200):
          UPDATE notifications SET status='sent', sent_at=NOW() WHERE id=456
          Commit Kafka offset (mark message processed)
        
        If PERMANENT FAILURE:
          FCM: "Registration token is not valid" (user uninstalled)
          APNs: "BadDeviceToken"
          → UPDATE notifications SET status='failed', error_message='invalid token'
          → UPDATE device_tokens SET is_active=FALSE WHERE token='dJR_...'
          → Commit Kafka offset
        
        If TRANSIENT FAILURE:
          FCM: "InternalServerError" or timeout
          → UPDATE notifications SET status='pending', error_message='fcm timeout'
          → DO NOT commit Kafka offset
          → Message will be re-delivered by Kafka (at-least-once guarantee)
          → But: to avoid immediate retry, publish to notif.retry topic with delay
```

---

### Retry Logic with Exponential Backoff

```
Attempt 1 fails → publish to notif.retry with delay_seconds=60
Attempt 2 fails → publish to notif.retry with delay_seconds=300  (5 min)
Attempt 3 fails → publish to notif.retry with delay_seconds=1800 (30 min)
Attempt 4 (attempt_count >= max_attempts):
  → UPDATE notifications SET status='failed', error_message='max retries exceeded'
  → Alert ops (PagerDuty) if it's a high-priority notification type

Formula: delay = base_delay × 2^attempt + random_jitter
  Attempt 1: 60 + random(0-30) seconds
  Attempt 2: 120 + random(0-60) seconds
  Attempt 3: 240 + random(0-120) seconds
```

**Why jitter?**

Without jitter: if 10,000 notifications fail simultaneously (FCM blip), they all retry at exactly the same time → second thundering herd → FCM gets hit again → fails again → infinite loop.

With jitter: the retries are spread across a time window. FCM recovers, the queue drains gradually.

---

### Campaign Fan-out — Sending to 5M Users

```
Campaign Scheduler sends request:
  POST /v1/notifications/batch
  { user_ids: [1...5M], type: "weekly_digest", channel: ["email"] }

Step 1: API doesn't process 5M in-line
        Creates batch job record: { batch_id: "batch_abc", status: "pending", total: 5000000 }
        Returns 202 immediately

Step 2: Campaign Fan-out Worker reads batch
        Paginate through user_ids in chunks of 10,000
        For each chunk:
          - Query user preferences (batch fetch from Redis/DB)
          - Filter: only users with email_enabled=true
          - Publish each eligible notification to email.pending Kafka topic

Step 3: Email Workers consume from email.pending
        Rate: 1,000 emails/sec per worker × 10 workers = 10,000/sec
        5M emails / 10,000/sec = 500 seconds ≈ 8.3 minutes

Step 4: Progress tracking
        UPDATE batch_jobs SET processed=processed+1000 WHERE batch_id='batch_abc'
        Caller can poll GET /v1/batches/batch_abc/status
```

**Why does this work?**

Kafka decouples the fan-out rate from the delivery rate. The Campaign Scheduler can push all 5M events in 30 seconds. Workers drain at 10K/sec. FCM/SendGrid never gets overwhelmed because workers are rate-limited by your Kafka consumer group configuration.

---

### What is At-Least-Once Delivery?

Kafka's guarantee: if a worker picks up a message, processes it, but crashes before committing the offset, Kafka will re-deliver the message to another worker. This is "at-least-once" — the message is delivered at minimum one time, possibly more.

This means a notification might be sent twice. To prevent the user seeing a duplicate:

**Idempotency key at the API level:** Prevents the caller from creating two identical notifications.

**Status check at the worker level:** Before calling FCM, check if `notifications.status == 'sent'`. If already sent, skip the FCM call and just commit the Kafka offset. This is the second deduplication layer.

```python
def process_notification(message: KafkaMessage):
    notif_id = message['notif_id']
    
    # Check if already sent (handles Kafka re-delivery)
    notif = db.get(notif_id)
    if notif.status == 'sent':
        # Already delivered on a previous attempt
        kafka.commit(message.offset)
        return
    
    # Proceed with delivery...
    result = fcm_client.send(...)
    
    if result.success:
        db.update(notif_id, status='sent', sent_at=now())
        kafka.commit(message.offset)  # mark as processed
```

---

## Scale — What Breaks at 10x?

10x = 100M notifications/day, peaks of 50M in a campaign blast.

**Kafka** — Kafka is designed for millions of messages/sec. Partition `push.pending` by `user_id` (consistent distribution). At 50M messages in 10 minutes = 83K messages/sec. With 50 partitions × 2K messages/sec each = handles it comfortably.

**FCM/APNs throughput limits** — Google allows multiple parallel connections to FCM. Each HTTP/2 connection handles multiple streams. Run multiple FCM HTTP/2 connections and multiplex push requests. If FCM enforces org-level limits, use multiple Firebase projects.

**Worker scaling** — Workers are stateless Kafka consumers. Add more workers = more throughput. Auto-scale in Kubernetes based on Kafka consumer lag (how far behind the workers are). If lag > 100K messages, scale up workers.

**MySQL notification log** — At 100M rows/day, partition by `created_at` (monthly partitions). `PARTITION BY RANGE (YEAR(created_at) * 100 + MONTH(created_at))`. Each month is a separate partition. Queries on recent notifications only scan the current partition. Archive and drop partitions older than 90 days.

**Redis for deduplication** — Idempotency key check is a Redis GET. Shard by `user_id`. 10M checks/day = 115 checks/sec — Redis handles this easily even on a single node.

---

## Trade-offs

**Push vs email vs SMS for critical alerts:**

| Channel | Latency | Cost | Open Rate | Appropriate for |
|---------|---------|------|-----------|-----------------|
| Push | <5 sec | Free | 7-10% | Real-time updates |
| Email | <1 min | Cheap | 20-25% | Transactional, detailed |
| SMS | <30 sec | Expensive ($0.01/msg) | 95%+ | Critical OTP, payments |

For a payment failure: send all three. Email for details, push for immediacy, SMS if user hasn't opened the app in 30 seconds.

**At-least-once vs exactly-once:**

Exactly-once delivery across distributed systems requires distributed transactions (2-phase commit) between Kafka and your DB. The overhead is huge. At-least-once + idempotency is the industry standard — it achieves the same result (user sees notification once) with much simpler infrastructure.

**Fan-out on write vs fan-out on read:**

Fan-out on write: when an event happens, immediately create and queue a notification for every target user. Fast delivery, high write amplification.

Fan-out on read: store one notification object, each user fetches it when they open the app. No push needed, eventual delivery only.

For push notifications, write-time fan-out is correct — push is time-sensitive and fire-and-forget. Fan-out on read only works for in-app notification centers (the bell icon).

---

## Cross-Questions

**Q: How do you prevent sending duplicate notifications to the same user?**

Two layers:

Layer 1 — API level (idempotency key): The caller provides `idempotency_key: "order-789-shipped-push"`. Before creating any notification records, check if this key exists in the DB. If yes, return the existing notification. This handles the case where the calling service retries after a timeout.

Layer 2 — Worker level (status check): Before calling FCM, check `notifications.status`. If already `sent`, skip the FCM call and commit the Kafka offset. This handles Kafka re-delivery after worker crashes.

These two layers together make the system behave like exactly-once from the user's perspective, while using the simpler at-least-once infrastructure.

**Q: How do you handle quiet hours?**

At fan-out time in the Notification API:

```python
def should_send_push(user_id: int, prefs: UserPrefs) -> bool:
    if not prefs.push_enabled:
        return False
    
    if prefs.quiet_hours_start and prefs.quiet_hours_end:
        user_now = datetime.now(pytz.timezone(prefs.timezone))
        current_time = user_now.time()
        
        if prefs.quiet_hours_start <= current_time <= prefs.quiet_hours_end:
            return False  # within quiet hours
    
    return True

# If should_send returns False:
# Option A: Drop the notification
# Option B: Schedule it for after quiet hours end
#   → Create notification with scheduled_at = quiet_hours_end
#   → Job scheduler (Q8) picks it up at that time
```

For high-priority notifications (like payment failure), ignore quiet hours — user should always know their payment failed.

**Q: What happens if FCM is completely down for 2 hours?**

```
Hour 1: FCM is down
  - Push workers keep receiving messages from Kafka
  - Every call to FCM returns 503 Service Unavailable (transient error)
  - Workers publish to notif.retry with delay
  - Messages accumulate in notif.retry topic (Kafka buffers them)
  - Kafka consumer lag grows — ops gets alerted
  - Circuit breaker activates: stop trying FCM, directly enqueue retries

Hour 2: FCM recovers
  - Circuit breaker detects recovery (periodic health check pings FCM)
  - Workers resume consuming notif.retry topic
  - Backlog drains at full worker throughput
  - Users receive their push notifications 1-2 hours late
  - Nothing was lost
```

Users get a delay, not silence. This is the correct behavior — Kafka as a buffer ensures no notification is lost during provider outages.

**Q: How do you track whether a user actually opened the notification?**

**Push notifications:** Include a deep link with a tracking parameter `?notif_id=456`. When the user taps the notification, the app opens the deep link and fires:
```
GET /v1/notifications/456/opened
→ UPDATE notifications SET status='read', read_at=NOW()
```

**Email:** Embed a 1×1 pixel image (tracking pixel):
```html
<img src="https://api.example.com/track/456/open.gif" width="1" height="1"/>
```
When the email client loads this image, our server records the open. Note: iOS Mail Privacy Protection pre-fetches images — open tracking is unreliable for iOS Apple Mail users.

**SMS:** No open tracking. Only delivery confirmation from Twilio (carrier received it, not that user read it).

**Q: How would you implement notification templates with user-specific variables?**

```python
# Template stored in DB:
# type: "order_shipped"
# template: "Hi {{user_name}}, your order #{{order_id}} has shipped! Arrives {{delivery_date}}."

def render_notification(template_type: str, variables: dict) -> str:
    template = template_cache.get(template_type)  # cached in Redis
    # Use Jinja2 or Mustache for safe variable substitution
    return template.render(**variables)

# Notification API call from Order Service:
POST /v1/notifications
{
  "user_id": 12345,
  "type": "order_shipped",
  "variables": {
    "user_name": "Dnyaneshwar",
    "order_id": "789",
    "delivery_date": "June 25"
  }
}
```

Rendering happens in the Notification API before Kafka publishing — the Kafka message contains the final rendered content, not the template. Workers are kept simple: they receive ready-to-send content and call the provider.

