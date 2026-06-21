# Q4: Design Chat System (WhatsApp)

---

## Clarifying Questions

Before I start, a few important things. Is this 1:1 messaging only, or do we need group chats too? Group chats have a very different fan-out problem — sending one message to 1,000 group members is fundamentally different from 1:1.

Do we need real-time delivery — like typing indicators and online presence — or is near-real-time acceptable? That determines whether we use WebSockets or polling.

Do messages need to be end-to-end encrypted? That's a product decision that changes key management significantly. I'll assume no E2E for this design, but I'll mention where it'd plug in.

What's the message history requirement — store forever like iMessage, or limited like Snapchat? And do we support media (images, video) or text only?

*Assuming: 1:1 and group chat (up to 500 members), real-time with WebSockets, no E2E encryption, messages stored indefinitely, text + media, 500M DAU, 50B messages/day.*

---

## Scope

I'll design the core messaging pipeline: sending and receiving messages in real-time, message persistence, delivery receipts (sent/delivered/read), online presence, and media upload. I'll skip user registration, contacts sync, and call features.

Scale estimate: 500M DAU, 50B messages/day = ~580,000 messages/sec. Each message is ~1KB of text. That's 580 MB/sec write throughput. This is WhatsApp-scale — a serious distributed systems problem.

---

## High Level Design

```
                                    ┌───────────────────────────────┐
                                    │         Chat Service          │
┌──────────┐  WebSocket  ┌──────────┴────┐   ┌─────────────────┐  │
│  User A  │────────────▶│  Chat Server  │   │  Presence       │  │
│ (online) │◀────────────│  (stateful)   │──▶│  Service        │  │
└──────────┘             └──────┬────────┘   │  (Redis PubSub) │  │
                                │            └─────────────────┘  │
                                ▼                                   │
                         ┌─────────────┐   ┌─────────────────┐   │
                         │    Kafka    │   │  Notification   │   │
                         │  (msg bus)  │   │  Service        │   │
                         └──────┬──────┘   │  (push for      │   │
                                │          │   offline users) │   │
                    ┌───────────┤          └─────────────────┘   │
                    │           │                                   │
          ┌─────────▼───┐  ┌────▼──────────┐                     │
          │  Message    │  │  Chat Server  │                     │
          │  Storage    │  │  (User B's)   │                     │
          │  (Cassandra)│  └──────┬────────┘                     │
          └─────────────┘         │   WebSocket                   │
                                  ▼                                │
                           ┌──────────┐                           │
                           │  User B  │                           │
                           │ (online) │                           │
                           └──────────┘                           │
                                                                   │
         ┌───────────────────────────────────────────────────┐   │
         │                   Data Layer                       │   │
         │  Cassandra  — messages (write-heavy, time-series)  │   │
         │  MySQL      — users, conversations, metadata       │   │
         │  Redis      — presence, session, recent messages   │   │
         │  S3         — media storage (images, videos)       │   │
         └───────────────────────────────────────────────────┘   │
                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

The core insight here: Chat servers are **stateful** — each server holds thousands of persistent WebSocket connections. When User A sends a message to User B, A's chat server needs to forward it to B's chat server (since they're likely on different servers). This is done via a message bus (Kafka) or a service discovery layer.

---

## Deep Dive 1 — WebSocket: Why and How

**Why not HTTP polling?**

With HTTP, the client repeatedly asks the server "any new messages?" — every 1-3 seconds. For 500M users, that's billions of wasted requests per minute. Latency is also bad — up to 3 seconds between message sent and received.

With long polling, the client makes an HTTP request and the server holds it open until a message arrives. Better, but still has overhead of re-establishing HTTP connections and HTTP headers on every message.

**WebSocket:** The client makes one HTTP request with an `Upgrade: websocket` header. The server accepts, and the HTTP connection is upgraded to a full-duplex TCP connection. Now both sides can send data at any time without request-response overhead. One connection, persistent, bidirectional.

```
Client                              Server
  │──── HTTP GET /chat ────────────▶│
  │     Upgrade: websocket           │
  │     Connection: Upgrade          │
  │◀─── 101 Switching Protocols ─────│
  │     (HTTP connection promoted)   │
  │                                  │
  │◀═══════ WebSocket frames ════════│  ← full duplex from here
  │════════ WebSocket frames ════════▶│
  │    (both sides send anytime)     │
```

**What makes WebSocket connections hard at scale:**

WebSocket connections are stateful — the server holds the connection in memory. If User A is connected to Chat Server 1, and User B is connected to Chat Server 2, and A sends B a message, Chat Server 1 needs to find B's server and forward the message.

This is solved with a **connection mapping service**: Redis stores `user_id → chat_server_id`. When A's server needs to reach B's server, it looks up B's server ID in Redis, then routes via Kafka (publish to a topic partitioned by server ID) or via direct gRPC call to B's server.

---

## Deep Dive 2 — Message Flow: Exactly What Happens

Let's trace a single message from A sending "Hello" to B:

```
Step 1: A types "Hello", hits send
  Client sends WebSocket frame to Chat Server 1:
  { "type": "message", "to": "user_B", "content": "Hello", "client_msg_id": "abc123" }

Step 2: Chat Server 1 assigns a global message ID
  - Generate a unique, ordered message ID (Snowflake: timestamp + server_id + sequence)
  - This ordering is critical — messages must appear in send order

Step 3: Persist to Cassandra (async, but before ack)
  INSERT INTO messages (conversation_id, message_id, sender_id, content, created_at)

Step 4: Ack back to A immediately
  { "type": "ack", "client_msg_id": "abc123", "message_id": 789, "status": "sent" }
  A's UI shows single grey tick ✓

Step 5: Look up B's connection
  Redis GET user_connection:user_B → "chat_server_3"

Step 6a: If B is online (found in Redis)
  Publish to Kafka topic: "server_3_inbox"
  Chat Server 3 picks it up, sends over B's WebSocket
  B receives message, B's client sends delivery receipt
  B's server publishes receipt to Kafka → A's server gets it
  A's UI shows double grey tick ✓✓

Step 6b: If B is offline (not found in Redis)
  Push Notification Service is triggered
  Sends FCM/APNs push: "A sent you a message"
  Message is stored in Cassandra — B fetches it when they come online
```

---

## Deep Dive 3 — Message Storage Schema

This is where most people get the schema wrong. The naive approach — one big `messages` table sorted by timestamp — breaks at scale because Cassandra (and any distributed DB) needs a good **partition key** to distribute data evenly.

```sql
-- Cassandra schema (not SQL — Cassandra CQL)
CREATE TABLE messages (
    conversation_id  UUID,
    message_id       BIGINT,   -- Snowflake ID: monotonically increasing, sortable
    sender_id        BIGINT,
    content          TEXT,
    content_type     TEXT,     -- 'text', 'image', 'video'
    media_url        TEXT,     -- S3 URL if media
    status           TEXT,     -- 'sent', 'delivered', 'read'
    created_at       TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)  -- partition by convo, sort by msg
) WITH CLUSTERING ORDER BY (message_id DESC);
-- "Give me the last 20 messages in conversation X" = fast partition scan

CREATE TABLE conversations (
    user_id          BIGINT,
    conversation_id  UUID,
    other_user_id    BIGINT,
    last_message     TEXT,
    last_message_at  TIMESTAMP,
    unread_count     INT,
    PRIMARY KEY (user_id, last_message_at)
) WITH CLUSTERING ORDER BY (last_message_at DESC);
-- "Give me A's recent conversations sorted by latest activity" = fast
```

**Why Cassandra and not MySQL?**

Cassandra is designed for high write throughput and time-series data. At 580K messages/sec, MySQL would become a bottleneck quickly — it handles writes on a single primary. Cassandra distributes writes across nodes with no single point of contention. The trade-off: no JOIN queries, no complex transactions. But chat doesn't need those — every query is "get messages in conversation X" which maps perfectly to a single Cassandra partition.

**Why Snowflake IDs instead of auto-increment?**

Auto-increment requires a centralized sequence generator — a single DB writing IDs. At 580K/sec, that's a bottleneck. Snowflake generates IDs in a distributed way: 41 bits timestamp + 10 bits machine ID + 12 bits sequence = 64-bit integer that's globally unique, ordered by time, and generated locally on each server with no coordination.

---

## Deep Dive 4 — Online Presence

Users expect to see "online" or "last seen 5 minutes ago" next to contacts.

**How it works:**

When a user opens the app and establishes a WebSocket connection, the chat server writes to Redis:
```
SET presence:user_123 "online" EX 30
```
TTL is 30 seconds. The client sends a heartbeat every 15 seconds to keep the key alive. When the app goes to background or disconnects, no more heartbeats → key expires after 30 seconds → user appears offline.

```
Client sends heartbeat every 15 seconds:
{ "type": "heartbeat" }

Server responds:
{ "type": "heartbeat_ack" }
Server also refreshes Redis TTL: EXPIRE presence:user_123 30
```

**Scaling presence to 500M users:**

Not all users care about all other users' presence. When A opens a chat with B, A's client subscribes to B's presence via Redis PubSub channel `presence:user_B`. When B comes online or goes offline, the Presence Service publishes to that channel — all subscribers (A, C, D who have B's chat open) get the update immediately.

At 500M users, storing all presence data in one Redis is fine — each key is tiny (30 bytes), 500M keys = 15 GB. But subscriptions at scale are the hard part — a celebrity with 10M followers coming online would trigger 10M pub/sub notifications. For that, batch the presence update and send it only to users who currently have that chat open (active subscription), not all followers.

---

## Group Chat — The Fan-out Problem

A group of 500 members. User A sends a message. We need to deliver it to 499 users.

**Approach 1 — Fan-out on write (at send time):**

When A sends, look up all 499 group members, find their chat servers, deliver to each. 499 Redis lookups + 499 Kafka publishes or WebSocket sends. Fast delivery but expensive per message. Works fine for groups up to ~100 members.

**Approach 2 — Fan-out on read (lazy delivery):**

Store the message once in Cassandra. When each group member opens the chat, they fetch messages from Cassandra. No fan-out cost at send time. But members who are online won't get real-time delivery without polling or some notification mechanism.

**Hybrid (WhatsApp's approach):**

For small groups (≤100 members): fan-out on write — deliver immediately to all online members.
For large groups (>100 members): publish one message to Kafka. A worker fans out asynchronously. Online users get a push notification that says "new message" and fetch from Cassandra. Slight delay but manageable.

---

## Scale — What Breaks at 10x?

At 5 billion messages/day, 5.8M messages/sec:

**Chat servers:** WebSocket servers are horizontally scalable — add more servers. Load balancer uses consistent hashing on `user_id` so A always connects to the same server, reducing connection migration overhead. Connection state is in Redis, not in-process memory, so losing a server means clients reconnect and pick up from Redis.

**Cassandra write throughput:** Cassandra scales by adding nodes — each node handles its partition range. At 5.8M writes/sec across 100 nodes, each handles 58K writes/sec — well within Cassandra's capability. Scale out by adding nodes without downtime.

**Kafka:** Partition `messages` topic by `conversation_id`. Each partition is an ordered log. Scale by adding partitions and brokers. At 5.8M messages/sec, with 1KB average size, that's 5.8 GB/sec — needs 100+ partitions across 20+ brokers.

**Media storage:** Media goes directly to S3 (pre-signed URL pattern — client gets a URL from the server, uploads directly to S3, sends the URL in the message). Media is never proxied through chat servers. CDN in front of S3 for fast reads globally.

---

## Trade-offs

**SQL vs Cassandra for messages:** SQL is easier to query but can't sustain 580K writes/sec on a single primary. Cassandra is write-optimized and distributed but gives up complex queries. For chat, the query patterns are simple — messages by conversation, sorted by time — which maps perfectly to Cassandra's partition+sort model. SQL stays for user metadata, conversations list, and relationships where joins matter.

**Kafka vs direct server-to-server gRPC:** For delivering messages between chat servers, we could use direct gRPC calls (Server 1 directly calls Server 3). This is faster — no broker in the middle. But it creates tight coupling — Server 1 needs to know Server 3's address, and if Server 3 is overloaded, Server 1 blocks. Kafka decouples them. Message delivery is async, Server 3 processes at its own pace. The trade-off is ~50-100ms additional latency from Kafka — acceptable for chat.

**Message ordering guarantee:** Within a conversation, messages must appear in order A sent them. Snowflake IDs give time-ordering but not strict sender ordering (two messages sent within the same millisecond might get interleaved). For truly strict ordering, use sequence numbers per conversation — a Cassandra counter per `conversation_id`. This adds a write to get the next sequence number but guarantees perfect ordering. Most chat apps use Snowflake IDs and accept rare out-of-order display for simplicity.

---

## Cross-Questions

**How do you handle a user sending a message when they're offline (no internet)?**

The mobile client queues the message locally with a `pending` state. When connectivity returns, it sends the message. The server assigns a `message_id` and returns it — the client replaces the local pending message with the confirmed one. The `client_msg_id` (a UUID the client generates) allows the server to detect and deduplicate retries — if the client sends the same message twice, the second one is ignored because `client_msg_id` is already in the DB.

**How do you implement message read receipts (single tick, double tick, blue tick)?**

Single grey tick (✓) — server received and persisted the message. Sent when the server ACKs in Step 4 above.

Double grey tick (✓✓) — recipient's device received the message. Sent when B's WebSocket connection receives the message. B's client sends `{ "type": "delivered", "message_id": 789 }` to B's server, which forwards to A's server, which updates the message status and pushes to A.

Blue tick (✓✓) — recipient read the message. Sent when B's app brings the chat into foreground focus. B's client sends `{ "type": "read", "conversation_id": X, "up_to_message_id": 789 }`. This marks all messages up to that ID as read in batch.

Privacy setting: if B has "read receipts off," we don't send the blue tick event. The message is still stored as read internally, but A's UI never shows blue ticks.

**How would you design end-to-end encryption?**

Each user generates a public/private key pair on device. Public key is uploaded to a key server. When A wants to message B, A fetches B's public key from the server. A encrypts the message with B's public key — only B's private key (stored only on B's device, never on the server) can decrypt it. The server stores and transmits ciphertext it cannot read.

The hard problems: key rotation (what if B gets a new device?), multi-device (B has phone + laptop — both need to decrypt), and key verification (how does A know the public key really belongs to B and wasn't tampered with by the server). WhatsApp uses the Signal Protocol which solves all three with prekeys and ratcheting.

**How do you handle a chat server crashing while holding 100,000 WebSocket connections?**

All 100,000 clients detect the disconnection (WebSocket connection drops). They reconnect to any available chat server (load balancer picks one). The new server reads the user's state from Redis — last seen, pending messages. Any messages that arrived during the disconnect are fetched from Cassandra. Kafka messages for this user that weren't delivered are picked up by the new server since it now owns those connections. Recovery time: a few seconds of reconnection. No message loss because everything is persisted.

**How is typing indicator different from regular messages?**

Typing indicators are ephemeral — they don't need to be stored. When A starts typing, A's client sends `{ "type": "typing_start", "to": "user_B" }` via WebSocket. The server looks up B's chat server and forwards it. No Kafka, no Cassandra — just a direct server-to-server push. TTL of 5 seconds — if A stops typing, the indicator disappears automatically on B's side after 5 seconds. This keeps the critical message path clean and doesn't pollute the persistent message store with ephemeral events.
