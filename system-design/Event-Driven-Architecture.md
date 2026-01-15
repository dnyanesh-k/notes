# Event-Driven Architecture

A comprehensive guide to Event-Driven Architecture (EDA), Event Sourcing, and Command Query Responsibility Segregation (CQRS).

---

## Table of Contents

1. [What is Event-Driven Architecture?](#what-is-event-driven-architecture)
2. [Event-Driven Architecture Patterns](#event-driven-architecture-patterns)
3. [Event Sourcing](#event-sourcing)
4. [CQRS (Command Query Responsibility Segregation)](#cqrs-command-query-responsibility-segregation)
5. [Combining Event Sourcing + CQRS](#combining-event-sourcing--cqrs)
6. [Event Store](#event-store)
7. [Event Replay and Snapshots](#event-replay-and-snapshots)
8. [When to Use Each Pattern](#when-to-use-each-pattern)
9. [Challenges and Solutions](#challenges-and-solutions)
10. [Real-World Examples](#real-world-examples)
11. [Interview Tips](#interview-tips)

---

# What is Event-Driven Architecture?

## What is EDA?

**Event-Driven Architecture (EDA)** is an architectural pattern where services communicate by producing and consuming events, rather than direct request-response calls.

**Simple definition:** Services react to events that happen in the system, rather than calling each other directly.

Think of it like a news broadcast - when something happens (event), all interested parties (services) get notified and can react, rather than each party having to constantly check if something happened.

## Traditional vs Event-Driven

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL REQUEST-RESPONSE                             │
└─────────────────────────────────────────────────────────────────────────────┘

    Order Service              Payment Service
         │                           │
         │  1. Process Payment       │
         │──────────────────────────>│
         │                           │
         │  (waiting...)             │  Processing...
         │                           │
         │<──────────────────────────│
         │  2. Payment Result        │
         │                           │

    Problems:
    • Tight coupling
    • Blocking calls
    • Cascading failures
    • Hard to scale
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     EVENT-DRIVEN ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────┘

    Order Service         Event Bus         Payment Service
         │                    │                    │
         │  1. OrderCreated   │                    │
         │     event          │                    │
         │───────────────────>│                    │
         │                    │                    │
         │  2. Return         │                    │
         │  (immediately)     │                    │
         │                    │                    │
         │                    │ 3. Event delivered │
         │                    │───────────────────>│
         │                    │                    │
         │                    │                    │  Processing...
         │                    │                    │
         │                    │ 4. PaymentProcessed│
         │                    │<───────────────────│
         │                    │                    │
         │  5. Event received │                    │
         │<───────────────────│                    │

    Benefits:
    • Loose coupling
    • Non-blocking
    • Better scalability
    • Resilience
```

## Key Concepts

- **Event**: Something that happened in the system (immutable). Example: "OrderCreated", "PaymentProcessed"
- **Event Producer (Publisher)**: Service that creates and publishes events. Doesn't know who will consume.
- **Event Consumer (Subscriber)**: Service that listens for and processes events. Reacts to events.
- **Event Bus/Broker**: Infrastructure that routes events (Kafka, RabbitMQ). Handles delivery, persistence, routing.
- **Eventual Consistency**: Services eventually become consistent (not immediately). Trade-off for scalability and decoupling.

---

# Event-Driven Architecture Patterns

## 1. Event Notification

Service publishes lightweight event (just notification) → Other services react and fetch additional data if needed.

**Example:** Order Service publishes "OrderCreated" event. Email Service, Inventory Service, and Analytics Service all react to it.

**Characteristics:**
- Lightweight events (just notifications)
- Consumers fetch additional data if needed
- Event contains minimal information
- Loose coupling

## 2. Event-Carried State Transfer

Service publishes event with full data → Consumers use event data directly (no need to fetch).

**Example:** Order Service publishes "OrderCreated" with full order details (orderId, userId, items, total). Email, Analytics, and Reporting services use this data directly.

**Characteristics:**
- Events contain full data
- Consumers don't need to fetch additional data
- Self-contained events
- Higher event size

## 3. Event Sourcing

Store events as source of truth → Replay to rebuild state. (See detailed section below)

---

# Event Sourcing

## What is Event Sourcing?

**Event Sourcing** is a pattern where the state of an application is determined by a sequence of events, rather than storing the current state.

**Simple definition:** Instead of updating a record, store events that happened. Rebuild current state by replaying events.

Think of it like a bank statement - instead of just showing your current balance, it shows all transactions (events) that led to that balance. You can calculate your balance at any point in time by replaying the transactions.

## Traditional vs Event Sourcing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL APPROACH                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    Current State (Database):
    ┌─────────────────────────────────────┐
    │  Order ID: 123                      │
    │  Status: Paid                       │
    │  Total: $99.99                      │
    │  Updated: 2024-01-20 10:30:00       │
    └─────────────────────────────────────┘

    Problem:
    • Lost history (don't know what changed)
    • Can't see past states
    • Hard to debug
    • Audit trail missing
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EVENT SOURCING APPROACH                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    Event Store (Append-Only):
    ┌─────────────────────────────────────────────────────────┐
    │  Event 1: OrderCreated {id: 123, total: 99.99, ...}     │
    │  Event 2: PaymentProcessed {orderId: 123, amount: 99.99} │
    │  Event 3: OrderShipped {orderId: 123, tracking: "..."}  │
    │  Event 4: OrderDelivered {orderId: 123, ...}            │
    └─────────────────────────────────────────────────────────┘

    Current State = Replay all events for Order 123

    Benefits:
    • Complete history
    • Can rebuild any past state
    • Full audit trail
    • Time travel debugging
```

## How does Event Sourcing work?

Here's the step-by-step flow:

1. **Command received** (e.g., "Create Order")
2. **Application logic** processes command
3. **Event generated** (e.g., "OrderCreated" event)
4. **Event appended** to Event Store (append-only)
5. **State rebuilt** by replaying all events for that entity

**To get current state:**
1. Load all events for entity
2. Replay events in order
3. Build current state

## Example: Bank Account

**Traditional Approach:**
- Account Table: Account ID 123, Balance $500 (current state only)
- Problem: How did balance become $500? Was there a deposit? Withdrawal?

**Event Sourcing Approach:**
- Event Store:
  - Event 1: AccountOpened {accountId: 123, initialBalance: 0}
  - Event 2: MoneyDeposited {accountId: 123, amount: 1000}
  - Event 3: MoneyWithdrawn {accountId: 123, amount: 300}
  - Event 4: MoneyDeposited {accountId: 123, amount: 200}
  - Event 5: MoneyWithdrawn {accountId: 123, amount: 400}

- Current Balance = Replay events: 0 + 1000 - 300 + 200 - 400 = $500

**Benefits:** Know exactly how balance changed, can see balance at any point in time, full audit trail, can replay to any state

## Key Characteristics

- **Append-Only**: Events are never modified or deleted. Only append new events. Immutable history.
- **Event Store**: Specialized database for events. Optimized for append operations. Can replay events.
- **State Reconstruction**: Current state = replay all events. Can rebuild state at any point in time. May use snapshots for performance.
- **Event Versioning**: Events may change structure over time. Need to handle old event formats. Schema evolution.

## Benefits

- Complete history (every change is recorded)
- Natural audit trail
- Time travel (rebuild state at any point)
- Better debugging (see exactly what happened)
- Flexibility (can create new read models from events)
- Scalability (append-only is fast)

## Disadvantages

- More complex than traditional approach
- Replaying many events can be slow
- Storage can grow large (need snapshots)
- Team needs to understand pattern
- Need to handle event schema changes

---

# CQRS (Command Query Responsibility Segregation)

## What is CQRS?

**CQRS** is a pattern that separates read and write operations, using different models for commands (writes) and queries (reads).

**Simple definition:** Use different models and databases for reading and writing data.

Think of it like a library - you have one system for checking out books (write - simple, fast) and another system for searching books (read - complex queries, optimized for search).

## Traditional vs CQRS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL APPROACH                                     │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────┐
    │      Single Database Model          │
    │                                     │
    │         ┌──────────────┐            │
    │         │   Orders     │            │
    │         │   Table      │            │
    │         │              │            │
    │         │  • Optimized │            │
    │         │    for both  │            │
    │         │    read &    │            │
    │         │    write     │            │
    │         └──────────────┘            │
    │                                     │
    │  Commands (Write)                   │
    │  Queries (Read)                     │
    └─────────────────────────────────────┘

    Problem:
    • Same model for different needs
    • Can't optimize separately
    • Complex queries affect writes
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CQRS APPROACH                                            │
└─────────────────────────────────────────────────────────────────────────────┘

    Commands (Write)              Queries (Read)
         │                             │
         │                             │
         ▼                             ▼
    ┌──────────────┐            ┌──────────────┐
    │  Write Model │            │  Read Model   │
    │  (Normalized)│            │  (Denormalized)│
    │              │            │               │
    │  • Optimized │            │  • Optimized  │
    │    for writes│            │    for reads  │
    │  • ACID      │            │  • Fast       │
    │  • Simple    │            │  • Complex    │
    │              │            │    queries    │
    └──────┬───────┘            └──────┬───────┘
           │                           │
           │                           │
           ▼                           ▼
    ┌──────────────┐            ┌──────────────┐
    │  Write DB    │            │  Read DB     │
    │  (PostgreSQL)│            │  (MongoDB,   │
    │              │            │   Elasticsearch)│
    └──────┬───────┘            └──────────────┘
           │
           │  Sync (async)
           │
           ▼
    Read DB updated from Write DB
```

## How does CQRS work?

**Command Side (Write):**
1. Client sends command (e.g., CreateOrder)
2. Command Handler validates and processes
3. Write to Write Database (normalized, optimized for writes)
4. Publish event to Event Bus
5. Read Model Updater consumes event
6. Update Read Database (denormalized, optimized for reads)

**Query Side (Read):**
1. Client sends query (e.g., GetOrdersByUser)
2. Query Handler reads from Read Database
3. Return optimized data (no joins needed, pre-computed)

## Example: E-Commerce

**Write Model (Normalized):**
- Orders Table: ID, UserID, Status, Total
- OrderItems Table: ID, OrderID, ProductID, Quantity
- Optimized for: Fast writes, data integrity, ACID transactions

**Read Model (Denormalized):**
- UserOrdersView: ID, UserID, Status, Items (JSON with full product details)
- Optimized for: Fast reads, complex queries, no joins needed, pre-computed aggregations

## Key Characteristics

- **Separation**: Commands (write) and Queries (read) separated. Different models for each. Can use different databases.
- **Write Model**: Normalized structure. Optimized for writes. ACID transactions. Simple structure.
- **Read Model**: Denormalized structure. Optimized for reads. Can be materialized views. Complex queries supported.
- **Synchronization**: Read model updated from write model. Usually asynchronous (event-driven). Eventual consistency.

## Benefits

- Independent scaling (scale read and write separately)
- Optimization (optimize each side for its purpose)
- Performance (fast reads - denormalized, fast writes - simple)
- Flexibility (different databases per side)
- Complex queries (read model can handle complex queries)

## Disadvantages

- More moving parts (complexity)
- Eventual consistency (read model may be slightly stale)
- Need to keep read model in sync
- Duplicate data (write + read)
- Team needs to understand pattern

---

# Combining Event Sourcing + CQRS

## How they work together

**Flow:** Commands → Events → Event Store → Read Models

**Command Side:**
1. Command received (e.g., CreateOrder)
2. Command Handler processes
3. Event generated (e.g., OrderCreated)
4. Event appended to Event Store

**Query Side:**
1. Events from Event Store consumed by Event Handlers
2. Each handler builds its own read model:
   - Order View (for order details page)
   - User Orders View (for user dashboard)
   - Analytics View (for reporting)
   - Search Index (for search)

**Benefits:**
- Event Sourcing: Complete history
- CQRS: Optimized reads and writes
- Can create multiple read models from same events
- Very flexible

## Example: Order System

**Event Store:**
- Event 1: OrderCreated {orderId: 123, userId: 456, items: [...], total: 99.99}
- Event 2: PaymentProcessed {orderId: 123, amount: 99.99}
- Event 3: OrderShipped {orderId: 123, tracking: "ABC123"}
- Event 4: OrderDelivered {orderId: 123}

**Read Models (Built from Events):**
1. **Order View**: Order 123, Status: Delivered, Total: $99.99, Timeline: Created → Paid → Shipped → Delivered
2. **User Orders View**: User 456 Orders: Order 123 (Delivered), Order 124 (Shipped), Order 125 (Processing)
3. **Analytics View**: Daily Orders: 150, Revenue: $14,998.50, Average Order: $99.99

All built from the same events!

---

# Event Store

An **Event Store** is a specialized database optimized for storing and retrieving events in an event-sourced system.

## Event Store Characteristics

- **Append-Only**: Events are never updated or deleted. Only append new events. Immutable history.
- **Fast Appends**: Optimized for write operations. Sequential writes (very fast). No updates = no locking.
- **Event Stream**: Events grouped by aggregate/entity. Can replay stream for specific entity. Ordered by sequence number.
- **Versioning**: Support for event schema versioning. Handle schema evolution. Backward compatibility.
- **Replay Capability**: Can replay events from any point. Support for snapshots. Time-travel queries.

## Popular Event Stores

- **EventStore**: Purpose-built event store, supports projections
- **Kafka**: Can be used as event store (with retention)
- **PostgreSQL**: Can implement event store (append-only table)
- **MongoDB**: Document store, can store events
- **DynamoDB**: NoSQL, can store events with streams

---

# Event Replay and Snapshots

## Event Replay

**Problem:** Replaying 1 million events is slow!

**Solution:** Snapshots

Instead of replaying all events:
1. Load latest snapshot (e.g., state at event 1000)
2. Replay only events after snapshot (events 1001 onwards)
3. Much faster than replaying all events!

## Snapshots

**Purpose:**
- Speed up state reconstruction
- Store state at specific event number
- Replay only events after snapshot

**When to Create:**
- Every N events (e.g., every 1000)
- Periodically (e.g., daily)
- On demand

**Storage:**
- Store snapshot with event number
- Can be in same store or separate
- Compress for storage efficiency

---

# When to Use Each Pattern

## Event-Driven Architecture

**Use EDA when:**
- Multiple services need to react to events
- Loose coupling important
- High scalability needed
- Eventual consistency acceptable
- Real-time updates needed

**Examples:** Microservices communication, real-time notifications, event-driven workflows, audit requirements

## Event Sourcing

**Use Event Sourcing when:**
- Need complete audit trail
- Need to rebuild state at any point
- Time-travel debugging needed
- Legal/compliance requirements
- Complex business logic with history

**Don't use when:**
- Simple CRUD operations
- Don't need history
- High write volume with simple state
- Team unfamiliar with pattern

## CQRS

**Use CQRS when:**
- Read and write patterns very different
- Need to scale reads and writes independently
- Complex queries needed
- High read/write ratio
- Different performance requirements

**Don't use when:**
- Simple CRUD with similar read/write patterns
- Low complexity
- Can't handle eventual consistency

---

# Challenges and Solutions

## Challenge 1: Eventual Consistency

**Problem:**
- Read model may be slightly stale
- User sees old data after update

**Solutions:**
- Accept eventual consistency (most cases)
- Show "processing" state
- Use version numbers
- Poll for updates
- WebSocket/SSE for real-time updates

## Challenge 2: Event Versioning

**Problem:**
- Event structure changes over time
- Old events have old structure
- New code needs to handle both

**Solutions:**
- Include version in event
- Upcasters (transform old events to new format)
- Schema registry
- Backward compatibility

## Challenge 3: Performance

**Problem:**
- Replaying many events is slow
- Event store can grow large

**Solutions:**
- Use snapshots
- Archive old events
- Optimize event store
- Cache read models
- Materialized views

---

# Real-World Examples

## Netflix: Event-Driven Architecture

Services communicate via events (user actions, content, recommendations, analytics).

**Benefits:** Loose coupling, high scalability, real-time recommendations

## Uber: Event Sourcing

Trip events stored: TripRequested, DriverAssigned, TripStarted, TripCompleted, PaymentProcessed

**Benefits:** Complete trip history, dispute resolution, analytics, audit trail

## Amazon: CQRS

Write: Order processing (normalized). Read: Product catalog (denormalized, optimized for search)

**Benefits:** Fast product search, fast order processing, independent scaling

---

# Interview Tips

## Common Questions

**Q: What is Event-Driven Architecture?**
- EDA is a pattern where services communicate via events rather than direct calls
- Services publish events when something happens, other services subscribe and react
- Benefits: loose coupling, scalability, resilience

**Q: What is Event Sourcing?**
- Event Sourcing stores events as the source of truth instead of current state
- Current state is rebuilt by replaying events
- Benefits: complete history, audit trail, time-travel debugging

**Q: What is CQRS?**
- CQRS separates read and write operations using different models
- Write model optimized for writes (normalized), read model optimized for reads (denormalized)
- Benefits: independent scaling and optimization

**Q: When would you use Event Sourcing?**
- Need complete audit trail
- Need to rebuild state at any point
- Legal/compliance requirements
- Time-travel debugging needed
- Not ideal for simple CRUD operations

**Q: What are the challenges of Event Sourcing?**
- Eventual consistency
- Event versioning (schema changes)
- Performance (replaying many events)
- Storage growth
- Complexity
- Solutions: snapshots, upcasters, accepting eventual consistency

**Q: How do you handle event versioning?**
- Include version in events
- Use upcasters to transform old events to new format
- Maintain backward compatibility
- Use schema registry for validation

**Q: What is the difference between Event Sourcing and Event-Driven Architecture?**
- Event-Driven Architecture: about communication (services react to events)
- Event Sourcing: about storage (events are source of truth)
- They can be used together

**Q: How do you ensure exactly-once processing in event-driven systems?**
- Idempotent processing (check if already processed)
- Unique event IDs
- Deduplication
- Idempotent operations
- True exactly-once is hard, often implemented as at-least-once + idempotency

## Key Points to Remember

- **EDA** = Services communicate via events, loose coupling
- **Event Sourcing** = Events are source of truth, complete history
- **CQRS** = Separate read/write models, independent optimization
- **Event Store** = Append-only, optimized for events
- **Snapshots** = Speed up replay, store state periodically
- **Eventual Consistency** = Trade-off for scalability
- **Event Versioning** = Handle schema changes over time
- **Use EDA** for loose coupling, **Event Sourcing** for audit/history, **CQRS** for different read/write needs

---

## Related Topics

- [Message Systems](../system-design/Message-Systems.md) - Message brokers and Pub/Sub for EDA
- [Architecture Patterns](../system-design/Architecture-Patterns.md) - Microservices architecture
- [Databases](../system-design/Databases.md) - Event stores and CQRS read/write databases
- [Distributed Transactions](../system-design/Databases.md#distributed-transactions) - Saga pattern for eventual consistency

