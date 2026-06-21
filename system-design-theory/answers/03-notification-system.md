# Q3: Design Notification System

---

## Clarifying Questions

Let me ask a few things before starting. What types of notifications are we handling — push (mobile), email, SMS, or all three? The delivery mechanisms are very different and I want to know what to prioritize.

Who triggers notifications — is it user actions like "someone liked your post," or system events like "your order shipped," or scheduled campaigns like "weekly digest"? This determines whether it's event-driven or batch.

What are the scale expectations? Millions of notifications per day or per hour? And what's the latency requirement — should push notifications arrive within 1 second, or is a few seconds acceptable?

Finally, do we need to guarantee delivery — what happens if a notification fails? Should we retry, and how many times?

*Assuming: all three channels (push, email, SMS), event-driven + scheduled, 10M notifications/day peak, sub-5-second delivery for push, at-least-once delivery guarantee with retry.*

---

## Scope

I'll design a notification service that receives events from other services, fans out to the right channels, handles failures with retry, and tracks delivery status. I'll skip user preference management UI and A/B testing for notification content — those are product concerns. I'll cover the pipeline from event to delivery.

Scale estimate: 10M notifications/day. Spread across 16 hours that's about 175/sec average, with peaks maybe 5x higher — 875/sec. Not extreme, but we need to handle bursts from campaigns — a marketing blast to 5M users needs to go out within minutes, not hours.

---

## High Level Design

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│  Event Sources  │     │           Notification Service                │
│                 │     │                                               │
│ • Order Service │     │  ┌──────────────┐    ┌───────────────────┐  │
│ • Payment Svc   │────▶│  │  Notification │    │   Kafka Topics    │  │
│ • User Service  │     │  │    API        │───▶│                   │  │
│ • Campaign Svc  │     │  └──────────────┘    │ • push.send       │  │
│ • Scheduler     │     │                       │ • email.send      │  │
└─────────────────┘     │                       │ • sms.send        │  │
                        │                       │ • notif.retry     │  │
                        │                       └─────────┬─────────┘  │
                        └─────────────────────────────────┼────────────┘
                                                          │
                    ┌─────────────────────────────────────┼────────────────────┐
                    │                    Workers           │                    │
                    │                                      │                    │
          ┌─────────▼──────┐   ┌──────────────┐   ┌──────▼────────┐          │
          │  Push Worker   │   │ Email Worker  │   │  SMS Worker   │          │
          └────────┬───────┘   └──────┬────────┘   └──────┬────────┘          │
                   │                  │                    │                    │
                   ▼                  ▼                    ▼                    │
          ┌────────────────┐  ┌──────────────┐  ┌───────────────┐            │
          │ APNs (iOS)     │  │  SendGrid /  │  │  Twilio /     │            │
          │ FCM (Android)  │  │  AWS SES     │  │  AWS SNS      │            │
          └────────────────┘  └──────────────┘  └───────────────┘            │
                                                                               │
                        ┌──────────────────────────────────────────┐          │
                        │              Data Stores                  │          │
                        │                                           │          │
                        │  MySQL (notification log, user prefs)     │          │
                        │  Redis  (dedup, device token cache)       │          │
                        └──────────────────────────────────────────┘          │
```

The flow: an event comes in → Notification API validates it → publishes to the right Kafka topic → channel-specific worker picks it up → calls the third-party provider → logs the result. If delivery fails, it goes to a retry topic with exponential backoff.

---

## Low Level Design

### Data Model

```sql
-- Track every notification sent
CREATE TABLE notifications (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT NOT NULL,
    type            VARCHAR(50) NOT NULL,     -- 'order_shipped', 'payment_failed'
    channel         ENUM('push','email','sms') NOT NULL,
    status          ENUM('pending','sent','delivered','failed') NOT NULL DEFAULT 'pending',
    content         JSON NOT NULL,            -- { title, body, deep_link, ... }
    idempotency_key VARCHAR(100) UNIQUE,      -- prevent duplicate sends
    attempt_count   INT NOT NULL DEFAULT 0,
    last_attempted  DATETIME,
    sent_at         DATETIME,
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_status_created (status, created_at)   -- for retry queries
);

-- Per-user preferences and device tokens
CREATE TABLE user_notification_prefs (
    user_id         BIGINT PRIMARY KEY,
    email           VARCHAR(200),
    phone           VARCHAR(20),
    push_enabled    BOOLEAN DEFAULT TRUE,
    email_enabled   BOOLEAN DEFAULT TRUE,
    sms_enabled     BOOLEAN DEFAULT TRUE,
    quiet_hours_start TIME,                   -- don't send push 10pm–7am
    quiet_hours_end   TIME,
    timezone        VARCHAR(50) DEFAULT 'UTC'
);

CREATE TABLE device_tokens (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id     BIGINT NOT NULL,
    token       VARCHAR(500) NOT NULL,        -- FCM or APNs token
    platform    ENUM('ios','android','web') NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    updated_at  DATETIME NOT NULL,
    UNIQUE KEY uk_token (token),
    INDEX idx_user_id (user_id)
);
```

---

### API Design

```
POST /v1/notifications
  Body: {
    "user_id": 12345,
    "type": "order_shipped",
    "channels": ["push", "email"],           // which channels to use
    "idempotency_key": "order-789-shipped",  // caller provides for dedup
    "content": {
      "title": "Your order has shipped",
      "body": "Expected delivery: June 25",
      "deep_link": "app://orders/789"
    },
    "priority": "high"                       // high = deliver immediately
  }
  Response 202: { "notification_id": 456, "status": "queued" }

POST /v1/notifications/batch
  Body: {
    "user_ids": [1, 2, 3, ...],             // up to 10,000 per call
    "type": "weekly_digest",
    "channels": ["email"]
  }
  Response 202: { "batch_id": "batch_789", "total": 5000 }

GET /v1/notifications/{id}/status
  Response 200: { "status": "delivered", "sent_at": "...", "attempt_count": 1 }
```

---

### The Delivery Flow — Step by Step

When an event comes in — say "order 789 shipped" for user 12345:

1. **Notification API** receives the request. First checks idempotency key in Redis — if already seen, return the existing notification ID, don't re-process. This prevents duplicate sends when upstream services retry.

2. **User preferences** are fetched — is push enabled? Is the user in quiet hours? What device tokens do they have? This is cached in Redis keyed by `user_prefs:{user_id}`, TTL 5 minutes.

3. **Fan-out**: for each eligible channel, publish a message to the corresponding Kafka topic. If user has 3 devices, publish 3 push messages. The API returns 202 immediately — it doesn't wait for actual delivery.

4. **Push Worker** picks up from `push.send` topic. Calls FCM (Android) or APNs (iOS) with the device token and payload. FCM and APNs are asynchronous — they accept the message and deliver it when the device is reachable.

5. **Result handling**: if the third-party returns success, update `notifications.status = 'sent'`. If it returns a permanent error (invalid token), mark device as inactive and update status to `'failed'`. If it returns a transient error (rate limited, timeout), publish to `notif.retry` with a delay.

6. **Retry worker** processes the retry topic with exponential backoff — try after 1 min, then 5 min, then 30 min. After 3 attempts, mark as permanently failed.

---

### Handling Third-Party Provider Failures

APNs and FCM are outside our control. Three failure scenarios:

**Invalid device token** — user uninstalled the app. APNs returns `BadDeviceToken`. Mark the token as inactive in our DB, don't retry. If the user reinstalls, a new token registration event will update it.

**Rate limited by provider** — FCM has per-second limits. Implement exponential backoff with jitter. The retry topic has a delay configured. Never hammer a provider that's already overwhelmed.

**Provider is down** — this is the hardest. Our Kafka topic acts as a buffer — messages queue up. When the provider comes back, workers drain the queue. The user gets a delayed notification rather than no notification. For email, a delay of 30 minutes is usually acceptable. For push, ideally under 1 minute.

---

### Sending at Scale — The Campaign Problem

When a marketing team blasts a notification to 5 million users, you can't process all 5M synchronously. The batch API endpoint fans out to Kafka. Workers pick up messages at a rate they can sustain — say 1,000 messages/sec per worker. With 10 workers you're sending 10,000/sec. 5M messages takes 8 minutes. That's acceptable.

The key insight: Kafka decouples the batch ingestion rate from the delivery rate. The campaign scheduler pushes all 5M events instantly. Workers drain at a controlled pace. No thundering herd on FCM.

```
Campaign Scheduler
      │
      ▼ (5M messages in 30 seconds)
   Kafka Topic
      │
      ▼ (10 workers × 1,000/sec = 10K/sec sustained)
   Push/Email Workers
      │
      ▼ (FCM/SendGrid rate-limited per provider contract)
   Third-party providers
```

---

## Scale — What Breaks at 10x?

At 100M notifications/day, 8,750/sec peak, the pressure points are:

**Kafka:** Kafka handles millions of messages/sec natively. Partition by `user_id` so messages for the same user go to the same partition and stay ordered. Add partitions as throughput grows — no downtime.

**Worker scaling:** Workers are stateless. Add more pod replicas in Kubernetes. Each Kafka consumer group automatically rebalances partitions across workers. Scale each channel independently — you might need 20 push workers but only 5 SMS workers.

**MySQL notification log:** At 100M rows/day, this table grows fast. Partition by `created_at` (monthly partitions). Archive notifications older than 90 days to cold storage (S3). Only recent notifications need fast access.

**Redis for dedup and token cache:** Shard by `user_id`. Token cache TTL of 5 minutes means eventual consistency — a deactivated token might be used one more time before the cache expires. This is acceptable; the provider will return `BadDeviceToken` and we'll clean it up.

---

## Trade-offs

**At-least-once vs exactly-once delivery:** Kafka with consumer offset commits gives at-least-once by default — if a worker crashes after delivering but before committing the offset, it'll re-deliver. We handle this with the idempotency key — if the notification was already sent, we don't send again. Exactly-once requires distributed transactions across Kafka and our DB, which is complex. At-least-once + dedup is the industry standard.

**Push vs in-app notifications:** Push goes through APNs/FCM. In-app (like a notification bell icon) is different — it's a database query when the user opens the app, not a push. For a full system you'd have both: push to get the user's attention, in-app to show history. This design covers push; in-app is a simple read path from the notifications table.

**Fanout on write vs fanout on read:** We fan out on write — when the event arrives, we create one message per channel per device immediately. Alternative is fanout on read — store one notification, let each device fetch it. Fanout on write is faster for delivery but increases storage. For push notifications, write fanout is correct — push is time-sensitive and fire-and-forget.

---

## Cross-Questions

**How do you prevent sending duplicate notifications?**

Two layers. First, the idempotency key at the API level — checked in Redis with a 24-hour TTL. If the same key comes in twice, we return the first notification's ID and don't enqueue again. Second, at the worker level — before calling FCM/APNs, check if `notifications.status = 'sent'` for this notification ID. This handles the case where a worker crashes after sending but before committing the Kafka offset.

**How do you handle user preference for quiet hours?**

At fan-out time, check the user's quiet hours and timezone. If the current time in their timezone is within quiet hours, don't publish to the push topic — or publish to a delayed queue that holds the message until quiet hours end. Email can usually be sent anytime; push is the channel that needs quiet hours respect. The quiet hours setting is cached in Redis so we're not hitting MySQL on every notification.

**What if FCM or APNs is down for an hour?**

Kafka buffers everything. Workers detect the failure via repeated timeouts or error responses, activate a circuit breaker, and stop calling the provider. Messages stay in Kafka. When the circuit breaker detects recovery (periodic health check), workers resume. For a 1-hour outage, users receive their notifications late but nothing is lost. The user experience degrades gracefully.

**How would you implement notification templates with personalization?**

Store templates in a template service — simple key-value store where the key is the notification type like `order_shipped` and the value is a Mustache/Jinja template. At fan-out time, render the template with user-specific variables (name, order ID, delivery date). Template rendering is fast and stateless — it can happen in the Notification API before enqueuing, keeping workers simple. Cache compiled templates in memory; reload on template update events.

**How do you track if a user actually opened the notification?**

For push: include a `deep_link` with a tracking parameter like `notif_id=456`. When the user taps the notification, the app opens the deep link and fires a `GET /v1/notifications/456/opened` event to our backend. Update `status = 'delivered'`. For email: embed a 1x1 pixel tracking image — when the email client loads the image, we register an open. For SMS: no standard open tracking; only delivery receipt from Twilio (which confirms the carrier received it, not that the user read it).
