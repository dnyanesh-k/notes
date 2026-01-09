# Real-Time Communication

A comprehensive guide to real-time communication patterns: Long Polling, WebSockets, and Server-Sent Events (SSE).

---

## Table of Contents

1. [What is Real-Time Communication?](#what-is-real-time-communication)
2. [Long Polling](#long-polling)
3. [WebSockets](#websockets)
4. [Server-Sent Events (SSE)](#server-sent-events-sse)
5. [Comparison: Long Polling vs WebSockets vs SSE](#comparison)
6. [Use Cases](#use-cases)
7. [Scalability Considerations](#scalability-considerations)
8. [Interview Tips](#interview-tips)

---

# What is Real-Time Communication?

**Real-time communication** allows servers to push data to clients immediately when events occur, without the client needing to repeatedly request updates.

**Simple definition:** Server can send data to client instantly when something happens, rather than client polling for updates.

## The Problem: Traditional HTTP Request-Response

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL HTTP (Request-Response)                       │
└─────────────────────────────────────────────────────────────────────────────┘

    Client                                    Server
      │                                          │
      │  1. GET /api/messages?lastId=100         │
      │─────────────────────────────────────────>│
      │                                          │
      │<─────────────────────────────────────────│
      │  2. Response: [] (no new messages)       │
      │                                          │
      │  Wait 5 seconds...                       │
      │                                          │
      │  3. GET /api/messages?lastId=100         │
      │─────────────────────────────────────────>│
      │                                          │
      │<─────────────────────────────────────────│
      │  4. Response: [] (still no messages)     │
      │                                          │
      │  Wait 5 seconds...                       │
      │                                          │
      │  5. GET /api/messages?lastId=100         │
      │─────────────────────────────────────────>│
      │                                          │
      │                                          │  New message arrives!
      │                                          │
      │<─────────────────────────────────────────│
      │  6. Response: [{id: 101, text: "..."}]   │

    Problems:
    • High latency (up to 5 seconds delay)
    • Wasted requests (most return empty)
    • Server load (constant polling)
    • Battery drain (mobile devices)
```

## Real-Time Solutions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    REAL-TIME COMMUNICATION OPTIONS                          │
└─────────────────────────────────────────────────────────────────────────────┘

1. LONG POLLING
   • Client sends request, server holds it open
   • Server responds when data available
   • Client immediately sends new request

2. WEBSOCKETS
   • Full-duplex persistent connection
   • Both client and server can send anytime
   • Low latency, efficient

3. SERVER-SENT EVENTS (SSE)
   • Server pushes data to client
   • One-way (server → client)
   • Built on HTTP, simple
```

---

# Long Polling

## What is Long Polling?

**Long Polling** is a technique where the client sends a request to the server, and the server holds the request open until data is available or timeout occurs.

**Simple definition:** Client makes a request, server keeps it open until there's data to send, then client immediately makes another request.

Think of it like calling a restaurant and asking "Is my order ready?" - instead of hanging up and calling back, you stay on the line until they tell you it's ready, then you immediately call again to check for the next order.

## How does Long Polling work?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    LONG POLLING FLOW                                         │
└─────────────────────────────────────────────────────────────────────────────┘

    Client                                    Server
      │                                          │
      │  1. GET /api/messages?lastId=100         │
      │─────────────────────────────────────────>│
      │                                          │
      │  Server holds request open...            │
      │  (waiting for new messages)              │
      │                                          │
      │                                          │  New message arrives!
      │                                          │
      │<─────────────────────────────────────────│
      │  2. Response: [{id: 101, text: "..."}]   │
      │     (after 3 seconds)                    │
      │                                          │
      │  Client immediately sends new request    │
      │                                          │
      │  3. GET /api/messages?lastId=101         │
      │─────────────────────────────────────────>│
      │                                          │
      │  Server holds request open again...      │
      │                                          │
      │  (If timeout, server returns empty)      │
      │<─────────────────────────────────────────│
      │  4. Response: [] (timeout after 30s)     │
      │                                          │
      │  Client sends new request immediately    │
      │                                          │
      │  5. GET /api/messages?lastId=101         │
      │─────────────────────────────────────────>│
```

Here's the step-by-step flow:

1. **Client sends request** to server (e.g., `GET /api/messages?lastId=100`)
2. **Server holds connection open** - doesn't respond immediately
3. **Server waits** for new data or timeout (typically 30 seconds)
4. **When data arrives** - server responds immediately with the data
5. **Client receives response** and immediately sends a new request
6. **If timeout** - server responds with empty data, client sends new request

## Key Characteristics

- **Protocol**: HTTP/HTTPS (standard HTTP requests)
- **Connection**: Request-response (server holds connection open)
- **Latency**: Medium (better than polling, worse than WebSockets)
- **Server Resources**: Medium (holds connections open)
- **Client Complexity**: Low (simple HTTP requests)
- **Firewall Support**: Excellent (works everywhere)

## Benefits

- Simple to implement (just HTTP requests)
- Works through firewalls and proxies
- No special infrastructure needed
- Better than regular polling (lower latency)
- Each request is a new connection (automatic reconnection)

## Disadvantages

- Connection overhead (new connection for each request)
- Server holds many connections open
- Not true real-time (connection setup latency)
- Need to handle timeouts
- Less efficient than WebSockets

## When to Use Long Polling

**Use Long Polling when:**
- Need simple real-time updates
- Can't use WebSockets (firewall restrictions)
- Infrequent updates (few per minute)
- Want simple implementation
- Need to work with existing HTTP infrastructure

**Don't use Long Polling when:**
- High-frequency updates (many per second)
- Bidirectional communication needed
- Low latency critical
- High number of concurrent connections

---

# WebSockets

## What are WebSockets?

**WebSockets** provide a full-duplex communication channel over a single TCP connection, allowing both client and server to send data at any time.

**Simple definition:** A persistent, two-way connection where both client and server can send messages anytime without establishing new connections.

Think of it like a phone call - once connected, both people can talk at any time without hanging up and calling again.

## How do WebSockets work?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WEBSOCKET CONNECTION FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

    Client                                    Server
      │                                          │
      │  1. HTTP Upgrade Request                 │
      │     GET /ws                              │
      │     Upgrade: websocket                   │
      │     Connection: Upgrade                  │
      │─────────────────────────────────────────>│
      │                                          │
      │<─────────────────────────────────────────│
      │  2. HTTP 101 Switching Protocols         │
      │     (Connection upgraded to WebSocket)   │
      │                                          │
      │  ────────────────────────────────────────│
      │  WEBSOCKET CONNECTION ESTABLISHED        │
      │  (Persistent, full-duplex)               │
      │  ────────────────────────────────────────│
      │                                          │
      │  3. Client → Server: "Hello"             │
      │─────────────────────────────────────────>│
      │                                          │
      │<─────────────────────────────────────────│
      │  4. Server → Client: "Hi there!"         │
      │                                          │
      │  5. Server → Client: "New message!"      │
      │<─────────────────────────────────────────│
      │                                          │
      │  6. Client → Server: "Got it!"           │
      │─────────────────────────────────────────>│
      │                                          │
      │  ... (connection stays open) ...         │
      │                                          │
      │  7. Close connection                     │
      │─────────────────────────────────────────>│
```

Here's the step-by-step flow:

1. **Client sends HTTP upgrade request** with `Upgrade: websocket` header
2. **Server responds with 101 Switching Protocols** - connection upgraded
3. **WebSocket connection established** - persistent, full-duplex
4. **Both sides can send messages** anytime (text or binary)
5. **Connection stays open** until either side closes it

**Key point:** Starts as HTTP, then upgrades to WebSocket protocol. After upgrade, it's no longer HTTP - it's a persistent bidirectional connection.

## Key Characteristics

- **Protocol**: WebSocket (starts as HTTP, upgrades to WebSocket)
- **Connection**: Persistent (single connection stays open)
- **Latency**: Very Low (no connection setup per message)
- **Server Resources**: Efficient (one connection per client)
- **Client Complexity**: Medium (need to handle reconnection)
- **Firewall Support**: May have issues (some proxies block it)
- **Data Types**: Text or binary frames

## Benefits

- Low latency (no connection setup per message)
- Full-duplex (both sides can send anytime)
- Efficient (single persistent connection)
- True real-time communication
- Can send binary data
- Scalable (handles many concurrent connections)

## Disadvantages

- More complex than HTTP
- Need to handle reconnection and heartbeats
- Some firewalls/proxies block WebSockets
- Need to track connection state
- Requires sticky sessions or shared state for load balancing
- No automatic retry (need to implement reconnection)

## When to Use WebSockets

**Use WebSockets when:**
- Real-time bidirectional communication
- High-frequency updates (gaming, trading)
- Chat applications
- Collaborative editing
- Live notifications
- Low latency critical

**Don't use WebSockets when:**
- Simple one-way updates (use SSE)
- Infrequent updates (use long polling)
- Firewall restrictions
- Simple HTTP polling sufficient

---

# Server-Sent Events (SSE)

## What are Server-Sent Events?

**Server-Sent Events (SSE)** is a technology that allows a server to push data to a client over HTTP, providing one-way real-time communication from server to client.

**Simple definition:** Server can push text data to client over a persistent HTTP connection, but client can only send regular HTTP requests.

Think of it like a radio - the station (server) broadcasts to you (client), but you can't talk back through the radio. If you need to respond, you use a phone (regular HTTP request).

## How does SSE work?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SERVER-SENT EVENTS FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    Client                                    Server
      │                                          │
      │  1. GET /api/events                      │
      │     Accept: text/event-stream            │
      │─────────────────────────────────────────>│
      │                                          │
      │<─────────────────────────────────────────│
      │  2. HTTP 200 OK                          │
      │     Content-Type: text/event-stream      │
      │     Connection: keep-alive               │
      │                                          │
      │  ────────────────────────────────────────│
      │  SSE CONNECTION ESTABLISHED              │
      │  (One-way: Server → Client)              │
      │  ────────────────────────────────────────│
      │                                          │
      │<─────────────────────────────────────────│
      │  3. data: {"type": "message", "text": "Hello"}
      │                                          │
      │<─────────────────────────────────────────│
      │  4. data: {"type": "notification", "text": "New order"}
      │                                          │
      │<─────────────────────────────────────────│
      │  5. data: {"type": "update", "count": 42}
      │                                          │
      │  ... (server keeps sending) ...          │
      │                                          │
      │  Client can send regular HTTP requests:  │
      │                                          │
      │  6. POST /api/acknowledge                │
      │─────────────────────────────────────────>│
      │                                          │
      │  (SSE connection still open)             │
```

Here's the step-by-step flow:

1. **Client sends HTTP request** with `Accept: text/event-stream` header
2. **Server responds** with `Content-Type: text/event-stream` and keeps connection open
3. **SSE connection established** - one-way (server → client) 
4. **Server sends events** in text format whenever data is available
5. **Client receives events** automatically
6. **Client can send regular HTTP requests** separately if needed

**Key point:** It's still HTTP, but the server keeps the connection open and pushes data. The browser automatically reconnects if the connection drops.

## Message Format

Server sends messages in simple text format:
- `data: message content` (required)
- `event: eventType` (optional, default: "message")
- `id: messageId` (optional, for reconnection)
- `retry: milliseconds` (optional, retry interval)

## Key Characteristics

- **Protocol**: HTTP/HTTPS (standard HTTP)
- **Connection**: Persistent HTTP (server keeps connection open)
- **Latency**: Low (no connection setup per message)
- **Server Resources**: Efficient (one connection per client)
- **Client Complexity**: Very Low (simple EventSource API, auto-reconnect)
- **Firewall Support**: Excellent (standard HTTP, works everywhere)
- **Data Types**: Text only (UTF-8)

## Benefits

- Very simple to implement
- Automatic reconnection (browser handles it)
- Works through all firewalls (standard HTTP)
- Low overhead (text-only, efficient)
- Perfect for one-way server-to-client updates
- Supports different event types

## Disadvantages

- One-way only (server → client)
- Text only (no binary data)
- Browsers limit concurrent connections
- Can't send data over SSE connection (use regular HTTP)
- Less flexible than WebSockets

## When to Use SSE

**Use SSE when:**
- One-way server-to-client updates
- Real-time notifications
- Live feeds (news, sports scores)
- Progress updates
- Simple implementation needed
- Firewall-friendly solution required

**Don't use SSE when:**
- Need bidirectional communication (use WebSockets)
- Need to send binary data
- High-frequency bidirectional messages
- Need full control over connection

---

# Comparison: Long Polling vs WebSockets vs SSE

## Quick Comparison Table

| Aspect | Long Polling | WebSockets | SSE |
|--------|--------------|------------|-----|
| **Protocol** | HTTP | WebSocket | HTTP |
| **Direction** | Request-Response | Full-duplex | One-way (Server → Client) |
| **Latency** | Medium | Very Low | Low |
| **Connection** | Per Request | Persistent | Persistent |
| **Server Resources** | Medium | Efficient | Efficient |
| **Client Complexity** | Low | Medium | Very Low |
| **Firewall Support** | Excellent | May have issues | Excellent |
| **Binary Data** | Yes | Yes | No (text only) |
| **Auto Reconnection** | No | No | Yes |
| **Use Case** | Simple updates | Chat, gaming, trading | Notifications, live feeds |

## When to Use What?

**Use Long Polling when:**
- Simple real-time updates needed
- Can't use WebSockets (firewall restrictions)
- Infrequent updates
- Want simplest implementation

**Use WebSockets when:**
- Bidirectional communication needed
- High-frequency updates
- Low latency critical
- Chat, gaming, collaborative apps
- Need binary data support

**Use SSE when:**
- One-way server-to-client updates
- Real-time notifications
- Live feeds, progress updates
- Want simple implementation
- Firewall-friendly solution required

---

# Use Cases

## Long Polling Use Cases

- Simple notifications (email alerts, system alerts)
- Basic chat applications (low traffic)
- Dashboard updates (periodic refresh)
- When WebSockets are not available (firewall restrictions)

## WebSocket Use Cases

- **Chat applications**: Slack, Discord, WhatsApp Web (real-time messaging)
- **Collaborative editing**: Google Docs, Notion (multiple users editing simultaneously)
- **Gaming**: Multiplayer games (real-time game state, low latency)
- **Trading platforms**: Real-time stock prices, live order book
- **Live collaboration**: Video conferencing signaling, screen sharing

## SSE Use Cases

- **Notifications**: Push notifications, system alerts (GitHub notifications)
- **Live feeds**: News feeds, sports scores, social media feeds
- **Progress updates**: File upload progress, job processing status
- **Dashboards**: Real-time metrics, live charts, monitoring
- **Streaming data**: Log streaming, event streams, time-series data

---

# Scalability Considerations

## Scaling Challenges

**Long Polling:**
- Many open connections
- Server memory usage
- Connection timeout handling

**WebSockets & SSE:**
- Sticky sessions (client must connect to same server)
- Shared state (broadcasting to all clients)
- Connection management

## Scaling Solutions

### 1. Load Balancing with Sticky Sessions
- Load balancer routes same client to same server
- Problem: Uneven load distribution

### 2. Shared State (Redis Pub/Sub)
- All servers subscribe to Redis
- When server receives message, publish to Redis
- All servers receive and broadcast to their clients

### 3. Message Broker (RabbitMQ, Kafka)
- Use message broker for event distribution
- Servers consume events and broadcast

### 4. Dedicated Real-Time Servers
- Separate WebSocket/SSE servers from API servers
- Scale independently

## Scalable Architecture

```
Clients
  │
  ▼
Load Balancer (sticky sessions)
  │
  ├──────┬──────┬──────┐
  │      │      │      │
  ▼      ▼      ▼      ▼
WS1    WS2    WS3    WS4
  │      │      │      │
  └──────┼──────┼──────┘
         │      │
         ▼      ▼
    Redis    Message
    Pub/Sub  Broker
```

**Flow:**
1. Client connects to WS Server 1
2. Event occurs → Published to Redis/Message Broker
3. All WS servers receive event
4. Each server broadcasts to its connected clients

---

# Interview Tips

## Common Questions

**Q: What is the difference between Long Polling, WebSockets, and SSE?**
- **Long Polling**: HTTP requests held open until data available, then client sends new request
- **WebSockets**: Full-duplex persistent connection for bidirectional communication
- **SSE**: One-way server-to-client communication over HTTP

**Q: When would you use WebSockets vs SSE?**
- **WebSockets**: Bidirectional communication (chat, gaming, collaborative editing)
- **SSE**: One-way server-to-client updates (notifications, live feeds, progress)

**Q: How do you scale WebSocket connections?**
- Sticky sessions for load balancing
- Redis Pub/Sub or message brokers for event distribution
- Separate WebSocket servers from API servers
- Connection pooling

**Q: How does WebSocket handshake work?**
- Client sends HTTP request with `Upgrade: websocket` header
- Server responds with `101 Switching Protocols`
- Connection upgraded to WebSocket protocol (full-duplex)

**Q: What is the advantage of SSE over WebSockets?**
- Simpler to implement
- Automatic reconnection (browser handles it)
- Works through all firewalls (standard HTTP)
- Perfect for one-way updates

**Q: How do you handle WebSocket reconnection?**
- Exponential backoff
- Store connection state
- Handle missed messages (use message IDs)
- Heartbeat/ping-pong to detect dead connections

## Key Points to Remember

- **Long Polling** = HTTP requests held open, simple, firewall-friendly
- **WebSockets** = Full-duplex persistent connection, low latency, bidirectional
- **SSE** = One-way server-to-client over HTTP, simple, auto-reconnect
- **Scaling** = Use message brokers, sticky sessions, shared state (Redis)
- **Use WebSockets** for chat, gaming, collaborative apps
- **Use SSE** for notifications, live feeds, progress updates
- **Use Long Polling** when WebSockets not available, simple updates

---

## Related Topics

- [API Design](../system-design/API-Design.md) - REST, GraphQL, gRPC APIs
- [Message Systems](../system-design/Message-Systems.md) - Pub/Sub for event distribution
- [Event-Driven Architecture](../system-design/Event-Driven-Architecture.md) - Event-based real-time updates
- [Caching](../system-design/Caching.md) - Cache WebSocket state and SSE data

