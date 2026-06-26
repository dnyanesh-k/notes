# Q4: Design Chat System (WhatsApp)

---

## Introduction

A chat system is a real-time messaging platform that allows users to send and receive messages instantly, either one-on-one or in groups. WhatsApp, Slack, Telegram, and Facebook Messenger are all examples. The defining characteristic of a chat system is the real-time, bidirectional communication requirement — messages must appear on the recipient's screen within milliseconds of being sent, even if the sender and receiver are in different parts of the world.

The fundamental challenge is connection management. Unlike a typical HTTP request-response model where a client asks and the server responds once, a chat system needs a persistent connection so the server can push messages to the client at any time. This is typically solved using WebSockets, which maintain an open TCP connection, allowing both the server and client to send data to each other without waiting for a request.

At scale, maintaining millions of simultaneous WebSocket connections across multiple servers introduces a routing problem. If user A is connected to Server 1 and user B is connected to Server 2, Server 1 must know how to deliver B's message to A's server. This is typically solved with a pub/sub layer like Redis or a message queue that broadcasts to the correct server.

Message storage is another core concern. Chat history must be persisted so users can scroll back and see old messages, access them from a new device, or retrieve them after being offline. This puts heavy write pressure on the database, as every message from every user must be stored durably. Column-family databases like Apache Cassandra are commonly used for this because they are optimized for high-throughput sequential writes.

Additional features commonly asked about include message delivery receipts (sent, delivered, read), online/offline status, group chats, media file attachments, and end-to-end encryption.

---

## How to Approach This in an Interview

Chat is one of the hardest system design problems because it combines real-time delivery (WebSockets), massive write throughput (messages), distributed state (which server holds which connection), and data consistency (message ordering). Focus on these four challenges — the interviewer expects depth on all of them.

---

## Clarifying Questions

**1. 1:1 only or group chat too?**

"Are we doing just direct messages, or group chats? And if groups, how large? 10 people or 1,000?"

*Why this matters:* 1:1 = send to one user. Groups = send to N users — this is the fan-out problem. At 1,000 members, one message triggers 999 deliveries. The architecture is fundamentally different.

**2. Real-time or near-real-time?**

"Do users need to see messages instantly as the other person types (WebSocket), or is a few seconds delay okay (HTTP polling)?"

*Why this matters:* WebSocket = persistent connections, stateful servers, complex routing. HTTP polling = stateless but wasteful and high-latency.

**3. Do we need delivery receipts (read, delivered)?**

"Should the sender see a grey tick (sent), double tick (delivered), blue tick (read)? Like WhatsApp?"

*Why this matters:* Receipts mean every message has a return ACK path. Device → Server → Database → Sender's device. Doubles the message traffic.

**4. Message history — stored forever or ephemeral?**

"Do we store all messages permanently like iMessage, or do messages expire like Snapchat?"

*Why this matters:* Permanent storage = hundreds of petabytes, needs write-optimized database. Ephemeral = messages deleted after delivery, much simpler.

**5. Scale?**

"How many daily active users? How many messages per day?"

*Why this matters:* WhatsApp handles 100B+ messages/day. At that scale, a single database is impossible — you need a distributed database built for write-heavy time-series data.

### Assumptions

```
- 1:1 messaging + group chats (up to 500 members)
- Real-time with WebSockets (< 100ms delivery for online users)
- Full delivery receipts (sent ✓, delivered ✓✓, read ✓✓ blue)
- Messages stored permanently (users expect chat history)
- Text + media (images, video) support
- 500M DAU, 50B messages/day
- Online presence ("last seen X minutes ago")
```

---

## Back-of-Envelope Math

```
50B messages/day
= 50,000,000,000 / 86,400 seconds
= ~578,000 messages/sec
≈ 580K messages/sec write throughput

Message size: ~1KB average (text + metadata)
580K messages/sec × 1KB = 580 MB/sec write throughput

Storage:
  580K messages/sec × 86,400 sec/day × 1KB = ~50 TB/day
  50 TB/day × 365 days = ~18 PB/year (if storing forever)
  → Clearly needs a distributed storage system (not MySQL)

WebSocket connections:
  500M DAU, assume 20% online at peak = 100M concurrent connections
  Each connection is held by a Chat Server
  Typical server: 100,000 WebSocket connections max
  → Need 100M / 100K = 1,000 Chat Server instances
```

This immediately tells you: MySQL won't handle 580K writes/sec on a single primary. You need a write-distributed database like Cassandra.

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
                           └──────────┘

Data stores:
  Cassandra — messages (write-optimized, distributed, time-series)
  MySQL     — users, conversation metadata, contacts
  Redis     — online presence, connection mapping, recent messages cache
  S3        — media files (images, video)
```

**The key insight:** Chat servers are stateful. Each server holds thousands of persistent WebSocket connections in memory. If User A is on Server 1 and User B is on Server 3, Server 1 needs to route A's message to Server 3. This routing problem is what makes chat architecturally interesting.

---

## Part 1: What is WebSocket and Why Not HTTP?

**HTTP (request-response):**

The client asks, the server answers. For chat, if B wants to know if A sent a message, B must keep asking: "Any new messages?" every 1-3 seconds. This is called polling.

```
B → GET /messages?since=last_check    every 3 seconds
Server → { messages: [] }             most of the time: empty
Server → { messages: [A's message] }  eventually
```

Problems:
- 500M users polling every 3 seconds = 166M requests/sec just to check for messages
- Latency: message can be delayed by up to 3 seconds (the poll interval)
- Most responses are empty — wasted bandwidth and compute

**Long polling (slightly better):**

Client sends request, server holds the connection open until a message arrives (or timeout). Better latency, but still high overhead — each "message received" event causes a connection close + re-open cycle.

**WebSocket (what WhatsApp/Telegram/Slack use):**

One initial HTTP handshake upgrades the connection to a persistent full-duplex TCP connection. Both sides can send data at any time, no request needed.

```
B → HTTP GET /chat
    Header: Upgrade: websocket
    Header: Connection: Upgrade

Server → HTTP 101 Switching Protocols
         (HTTP connection is now upgraded to WebSocket)

Now both sides can send at any time:
A → Server: { type: "message", to: "B", content: "Hello" }
Server → B:  { type: "message", from: "A", content: "Hello" }
Server → A:  { type: "ack", message_id: 789, status: "delivered" }
```

**What keeps a WebSocket connection alive?**

The TCP connection needs keepalive pings to prevent intermediate routers/firewalls from timing it out. The server sends a `PING` frame every 30 seconds. The client responds with `PONG`. If the server doesn't receive a PONG within 10 seconds, the connection is considered dead and the server closes it.

---

## Part 2: The Routing Problem — How Does Server 1 Reach Server 3?

With 1,000 Chat Servers and 100M users, a message from A (on Server 1) to B (on Server 3) needs routing.

**Connection Registry in Redis:**

When a user connects, the Chat Server registers:
```
SET user_connection:user_B "server_3" EX 3600
```

When a user disconnects:
```
DEL user_connection:user_B
```

**Message routing flow:**

```
A's message arrives at Server 1
Server 1: GET user_connection:user_B → "server_3"

Option A (Kafka routing):
  Server 1 publishes to Kafka topic "server_3_inbox"
  Server 3 consumes from "server_3_inbox"
  Server 3 pushes message to B via WebSocket

Option B (Direct gRPC):
  Server 1 calls Server 3 directly via gRPC: DeliverMessage(user_B, content)
  Server 3 pushes to B via WebSocket
```

We use Kafka because: it decouples servers (Server 1 doesn't need to know Server 3's address), messages are durably stored if Server 3 is temporarily down, and it's easy to scale.

---

## Part 3: Exact Message Flow — Step by Step

User A sends "Hello" to User B:

```
Step 1: A types "Hello", taps send
  Client generates a client_msg_id (UUID): "client_abc123"
  Sends WebSocket frame to Chat Server 1:
  {
    "type": "message",
    "to": "user_B",
    "content": "Hello",
    "client_msg_id": "client_abc123"  ← for deduplication on retry
  }

Step 2: Server 1 assigns a global Snowflake ID
  message_id = generate_snowflake()  → e.g., 1687391823456001024
  (Snowflake = 41 bits timestamp + 10 bits server_id + 12 bits sequence)
  This ID is globally unique and sortable by time.

Step 3: Persist to Cassandra BEFORE acknowledging
  INSERT INTO messages (conversation_id, message_id, sender_id, content, created_at)
  VALUES ('conv_AB', 1687391823456001024, 'user_A', 'Hello', NOW())
  
  Why persist before ACK? If we ACK first and then crash, A thinks message was sent
  but it's gone. Persist first = durable message even if server crashes.

Step 4: Send ACK back to A
  {
    "type": "ack",
    "client_msg_id": "client_abc123",
    "message_id": 1687391823456001024,
    "status": "sent"
  }
  A's UI shows single grey tick ✓
  A can now see the message in the chat with the server-assigned ID.

Step 5: Route to B
  GET user_connection:user_B → "server_3"
  Publish to Kafka: topic="server_3_inbox"
  {
    "message_id": 1687391823456001024,
    "from": "user_A",
    "content": "Hello",
    "conversation_id": "conv_AB"
  }

Step 6a: If B is ONLINE (Server 3 is active)
  Server 3 consumes from Kafka
  Delivers to B over WebSocket
  B's client sends delivery receipt:
  { "type": "delivered", "message_id": 1687391823456001024 }
  Server 3 routes receipt back via Kafka → Server 1 → A's WebSocket
  A's UI shows double grey tick ✓✓
  
Step 6b: If B is OFFLINE
  GET user_connection:user_B → nil (not in Redis)
  Trigger Notification Service: send FCM/APNs push notification
  "A sent you a message"
  Message stays in Cassandra — when B comes online:
    B's client fetches missed messages from Cassandra
    B's client sends bulk delivery receipt
```

---

## Part 4: Why Cassandra and How It Works

**What is Cassandra?**

Cassandra is a distributed NoSQL database designed for high write throughput. Unlike MySQL (one primary, replicas read-only), Cassandra is "leaderless" — every node can accept writes. There's no single writer bottleneck.

**How writes work in Cassandra:**

When you INSERT a row, Cassandra:
1. Writes to an in-memory structure called a MemTable (instantly fast)
2. Appends to a WAL (Write-Ahead Log) on disk (durable)
3. Returns success to the client

Periodically, the MemTable is flushed to disk as an SSTable (Sorted String Table). This is why Cassandra writes are so fast — they're always sequential appends, never random overwrites.

**Why not MySQL for 580K writes/sec?**

MySQL's primary node handles writes with row-level locking and B-tree index updates. At 580K writes/sec, the B-tree index for the messages table would be continuously rebalanced — this is O(log n) per write. The index would become a bottleneck. You'd need to partition (shard) MySQL across hundreds of nodes and manage the routing — essentially reinventing Cassandra.

Cassandra is purpose-built for this: high write throughput, distributed from the start, no complex index rebalancing.

**The message storage schema:**

```sql
-- Cassandra CQL (not SQL — similar syntax but different semantics)

CREATE TABLE messages (
    conversation_id  UUID,
    -- The partition key. All messages in one conversation are
    -- stored on the same Cassandra node. This makes "fetch last
    -- 20 messages in conversation X" a single-node query — fast.
    
    message_id       BIGINT,
    -- Snowflake ID. Acts as the clustering key within the partition.
    -- Cassandra stores rows within a partition sorted by this.
    -- So messages in a conversation are automatically time-ordered.
    
    sender_id        BIGINT,
    content          TEXT,
    content_type     TEXT,    -- 'text', 'image', 'video'
    media_url        TEXT,    -- S3 URL if media message
    status           TEXT,    -- 'sent', 'delivered', 'read'
    created_at       TIMESTAMP,
    
    PRIMARY KEY (conversation_id, message_id)
    -- partition_key = conversation_id
    -- clustering_key = message_id (determines sort order within partition)
    
) WITH CLUSTERING ORDER BY (message_id DESC);
-- DESC means newest messages come first — matches typical chat UI (scroll down = older)

-- Query for last 20 messages in a conversation:
SELECT * FROM messages
WHERE conversation_id = 'conv_AB'
LIMIT 20;
-- This hits ONE Cassandra node (the one that owns conv_AB partition)
-- Returns in ~2ms
```

**The "conversation list" schema (inbox view):**

```sql
-- "Show me all my conversations sorted by last message time"
CREATE TABLE conversations (
    user_id          BIGINT,
    -- Each user has their own copy of the conversation list.
    -- (This is denormalization — the same conversation appears
    --  in both A's and B's conversation tables)
    
    conversation_id  UUID,
    other_user_id    BIGINT,
    last_message     TEXT,
    last_message_at  TIMESTAMP,
    unread_count     INT,
    
    PRIMARY KEY (user_id, last_message_at)
) WITH CLUSTERING ORDER BY (last_message_at DESC);

-- Query for A's inbox:
SELECT * FROM conversations WHERE user_id = 'user_A' LIMIT 20;
-- Single partition scan, returns most recent 20 conversations
-- Same O(1) Cassandra query
```

---

## Part 5: Snowflake IDs — Why Not Auto-Increment?

Auto-increment ID requires a single centralized counter. At 580K messages/sec:
- One service generates all IDs → single point of failure
- One DB write per ID generation → massive bottleneck

**Snowflake ID structure (Twitter-invented, widely adopted):**

```
64-bit integer, bit layout:
[41 bits: timestamp in ms] [10 bits: machine ID] [12 bits: sequence]

41 bits timestamp:
  Max value: 2^41 - 1 = 2,199,023,255,551 milliseconds
  = ~69 years from epoch
  If epoch = Jan 1, 2020 → valid until ~2089

10 bits machine ID:
  Max: 2^10 = 1,024 different machines
  Each Chat Server gets a unique machine ID assigned at startup

12 bits sequence:
  Max: 2^12 = 4,096 IDs per millisecond per machine
  At 580K messages/sec across 1,000 servers:
  580K / 1,000 servers = 580 messages/sec/server
  580 per second = 0.58 per millisecond
  Well within the 4,096/ms limit

Generation:
  timestamp = current_time_ms - EPOCH_MS
  machine_id = this_server_id   (static, known at startup)
  sequence = atomic_increment() % 4096  (per server, reset each ms)
  
  snowflake = (timestamp << 22) | (machine_id << 12) | sequence
```

**Properties:**
- **Globally unique:** No two servers generate the same ID (different machine_id)
- **Time-sortable:** Higher ID = later timestamp. Perfect for Cassandra clustering key.
- **No coordination:** Each server generates IDs independently — zero network calls
- **Reversible:** `timestamp = snowflake >> 22` extracts the timestamp for debugging

---

## Part 6: Online Presence

Users see "Online" or "Last seen 5 minutes ago" next to contacts.

**How it works:**

When a user connects → Chat Server writes:
```
SET presence:user_A "online" EX 30
```

Client sends a heartbeat every 15 seconds:
```
{ "type": "heartbeat" }
```

Server refreshes TTL:
```
EXPIRE presence:user_A 30
```

If the user closes the app → no more heartbeats → key expires in 30 seconds → user appears offline.

When user goes offline → Chat Server writes the last seen time:
```
SET last_seen:user_A "2026-06-22T10:30:45Z" EX 86400  (24 hour TTL)
```

**How does A know B came online?**

A subscribes to B's presence channel when A opens the chat with B:
```
SUBSCRIBE presence_updates:user_B
```

When B connects, B's Chat Server publishes:
```
PUBLISH presence_updates:user_B "online"
```

A's Chat Server receives the pub/sub message and pushes to A over WebSocket:
```
{ "type": "presence_update", "user": "user_B", "status": "online" }
```

**Why this is efficient:** A only subscribes to presence for contacts they currently have a chat window open with. B's presence update goes to maybe 5 active subscribers (people who have B's chat open), not B's entire contact list.

---

## Part 7: Group Chat Fan-out

Group of 500 members. A sends a message.

**Problem:** 499 deliveries per message. How?

**Fan-out on write (for groups ≤ 100 members):**
```
A's message arrives at Server 1
Server 1 looks up group members: [user_B, user_C, ... user_Z] (499 users)
For each member:
  GET user_connection:user_X → their server
  Publish to that server's Kafka topic
499 Redis lookups + 499 Kafka publishes
```

Works fine for small groups. At 100 members, 100 Redis lookups per message. Fast enough.

**Fan-out on read (for very large groups > 1,000 members):**
```
A's message arrives → stored in Cassandra once
No immediate fan-out

When member B opens the group chat:
  SELECT messages FROM group_messages WHERE group_id = X LIMIT 20
  B sees A's message

For real-time delivery: send one push notification to all group members
  "New message in group"
Members who have the group open receive it via polling or WebSocket subscription
```

**Hybrid approach (WhatsApp's actual strategy):**
```
≤ 100 members: fan-out on write to all online members immediately
> 100 members: 
  - Send message to Kafka once
  - Fan-out worker processes asynchronously (slight delay, acceptable)
  - Online members with the group chat open get it within 1-2 seconds
  - Others get a push notification "New message in group"
```

---

## Scale — What Breaks at 10x?

At 5B messages/sec, 5.8M messages/sec:

**WebSocket servers:** Horizontal scaling. Load balancer uses consistent hashing on `user_id` → same user always routes to same server → reduces connection migration. If a server crashes: clients detect disconnection → reconnect → pick any server → load state from Redis.

**Cassandra write throughput:** 5.8M writes/sec across 100 nodes = 58K writes/node/sec. Cassandra's tested limit is hundreds of thousands of writes/sec per node. Add nodes to increase throughput linearly — Cassandra's distributed architecture allows this without downtime.

**Kafka throughput:** 5.8M messages/sec × 1KB = 5.8 GB/sec. With 50 partitions on a 20-broker cluster, each broker handles ~290 MB/sec. Well within Kafka's capability.

**Media upload:** Client gets a pre-signed S3 URL → uploads directly to S3 (bypasses all chat servers). Media never flows through Chat Servers. CDN serves downloaded media. Our servers only store the media URL string in the message.

---

## Trade-offs

**Cassandra vs MySQL for messages:**

| | Cassandra | MySQL |
|---|---|---|
| Write throughput | 580K/sec distributed | ~10K/sec on single primary |
| Query flexibility | Partition-scoped queries only | Full SQL, JOINs, complex queries |
| Consistency | Tunable (1 to ALL replicas) | Strong ACID |
| Operational complexity | High | Low |

For chat messages, queries are simple: "give me messages in conversation X sorted by time." This maps perfectly to Cassandra's partition+clustering key model. We don't need JOINs. Cassandra wins.

MySQL stays for: users, contacts, conversation metadata, billing — where we need transactions and complex queries.

**Kafka vs direct gRPC server-to-server:**

Direct gRPC is faster (no broker hop, ~5ms vs ~50ms). But: Server 1 needs to know Server 3's address (service discovery required), if Server 3 is overloaded Server 1 blocks, and if Server 3 crashes messages are lost in-transit.

Kafka: Server 1 publishes and forgets. Server 3 processes when ready. Messages are durable in Kafka even if Server 3 crashes. The 50ms latency is acceptable — users don't notice 50ms vs 5ms in a chat message.

---

## Cross-Questions

**Q: What is a WebSocket frame and how does it differ from HTTP?**

HTTP is a text protocol: request + response header (200-2000 bytes of text overhead) + body. Every request has this overhead.

A WebSocket frame is binary: 2-10 bytes of header + payload. No HTTP verb, no URL, no headers repeated. A WebSocket message with "Hello" is ~12 bytes total. An HTTP POST with the same content would be ~400+ bytes. At 580K messages/sec, this bandwidth difference is significant.

WebSocket frames: `[FIN bit][opcode][masked bit][payload length][masking key][payload]`

The FIN bit indicates whether this is the last frame of a message (for fragmented large messages). The opcode distinguishes text (0x1), binary (0x2), ping (0x9), pong (0xA), and close (0x8) frames.

**Q: How do you implement read receipts (single tick, double tick, blue tick)?**

```
Single grey ✓ (sent to server):
  Server persists message to Cassandra
  Server sends ACK to A's WebSocket: { status: "sent", message_id: 789 }
  A's UI updates from "sending..." to ✓

Double grey ✓✓ (delivered to B's device):
  B's Chat Server pushes message to B over WebSocket
  B's client immediately sends back: { type: "delivered", message_id: 789 }
  Routed back to A via Kafka
  A's UI updates to ✓✓
  Also: UPDATE messages SET status='delivered' in Cassandra

Blue ✓✓ (read by B):
  B's app brings that conversation into foreground focus
  B's client sends: { type: "read", conversation_id: X, up_to_message_id: 789 }
  All messages up to 789 in that conversation are marked read
  Routed back to A
  A's UI updates to blue ✓✓

Privacy setting:
  If B has "read receipts off": B's client never sends the "read" event
  Message is still stored as read internally but A never sees blue ticks
```

**Q: How do you handle a Chat Server crashing with 100,000 active connections?**

```
1. Server crashes at t=0
2. All 100,000 clients detect TCP connection dropped (within 10-60 seconds,
   depending on TCP keepalive configuration)
3. All clients reconnect simultaneously to available servers
   (load balancer distributes across healthy servers)
4. Each reconnected client sends: { type: "sync", last_received_id: X }
5. Server fetches messages from Cassandra: 
   SELECT * FROM messages WHERE conversation_id = Y AND message_id > X
6. Server delivers missed messages
7. Presence state is re-established in Redis

The crashed server's Kafka partitions are reassigned to other consumers
in the same consumer group — they pick up unprocessed messages.

Total recovery: 10-30 seconds for reconnection spike to settle.
No message loss because everything is in Cassandra and Kafka.
```

**Q: How do you design end-to-end encryption?**

This is a deep question — here's the conceptual design:

```
Setup (one time per user):
  A generates a public key + private key pair on their device
  Private key NEVER leaves the device
  Public key is uploaded to a Key Server
  
Sending a message from A to B:
  1. A fetches B's public key from Key Server
  2. A encrypts message with B's public key
     Only B's private key can decrypt it
  3. A sends ciphertext to Chat Server
  4. Chat Server stores and forwards ciphertext — cannot read it
  5. B decrypts with their private key on their device

Signal Protocol (used by WhatsApp, Signal):
  Solves multi-device: each of B's devices has its own keypair
  A encrypts separately for each device
  Solves forward secrecy: keys are rotated per message (ratcheting)
  Even if B's current key is compromised, past messages can't be decrypted
  Solves key verification: safety numbers let A verify B's key wasn't
  swapped by the server
```

The hard parts: key rotation (new device?), group key management (adding a member means re-encrypting for all), and key verification UI (safety numbers are hard to explain to non-technical users).

**Q: How do typing indicators work? Why are they different from messages?**

Typing indicators are ephemeral — they don't need persistence or guaranteed delivery.

```
A starts typing → A's client sends:
{ "type": "typing_start", "conversation_id": "conv_AB" }

Server:
  GET user_connection:user_B → "server_3"
  Server 3 forwards to B via WebSocket (direct, no Kafka, no Cassandra)
  
B's UI shows "A is typing..."

Auto-expire:
  B's client shows the indicator for 5 seconds max
  If A types continuously, client re-sends typing_start every 3 seconds to refresh
  
A stops typing → A's client sends:
{ "type": "typing_stop", "conversation_id": "conv_AB" }
Or just: nothing — 5-second timeout on B's side removes the indicator automatically

Why skip Kafka/Cassandra?
  Typing indicators don't need durability — if the server crashes while A is typing,
  B just sees the indicator disappear. Fine.
  Adding Kafka/Cassandra would add 50-100ms latency and unnecessary storage.
  Keep the critical (message) path and the ephemeral (typing) path separate.
```

**Q: How does the client handle sending messages while offline (no internet)?**

```
A is offline, tries to send "Hello":
  Client stores message locally with status: "pending"
  Shows message in chat with a clock icon ⏰

Connection restored:
  Client sends the pending message with original client_msg_id
  Server checks: is this message already in Cassandra (idempotency check)?
    No → insert, ACK back with server message_id
    Yes (was sent before disconnect) → return existing message_id, don't duplicate
  Client replaces local pending message with confirmed message
  Clock icon changes to ✓

Multiple pending messages:
  Client maintains a queue of pending messages
  On reconnect, sends them in order
  Server assigns Snowflake IDs (so ordering is preserved as received)
```
