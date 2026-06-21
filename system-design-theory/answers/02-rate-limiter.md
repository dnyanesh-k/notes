# Q2: Design Rate Limiter

---

## Clarifying Questions

Before designing, let me ask a few things. Where does the rate limiter live — is it a standalone service, or built into an API gateway? That changes the deployment model significantly.

Who are we rate limiting — individual users, IP addresses, API keys, or all three? And what are the rules — is it one global limit like "100 requests per minute per user," or do different endpoints have different limits?

What should happen when the limit is hit — hard reject with 429, or soft throttle by slowing responses down? And do we need rate limiting across multiple data centers, or is single region enough to start?

*Assuming: distributed rate limiter as a middleware layer, per-user and per-IP rules, hard reject with 429, multi-region eventually, starting with single region.*

---

## Scope

I'll design a distributed rate limiter that sits between the client and backend services. It evaluates every incoming request against configurable rules, allows or rejects it, and returns proper HTTP headers. I'll cover the core algorithm, how rules are stored and evaluated, and how to scale it.

Scale estimate: if we have 10M active users each making 10 requests/minute, that's about 1.6M checks/sec at peak. The rate limiter itself needs to be extremely fast — sub-millisecond — because it's in the critical path of every single API call.

---

## High Level Design

```
                    ┌─────────────────────────────────────────┐
                    │           Rate Limiter Middleware        │
                    │                                          │
┌────────┐  HTTPS   │  ┌──────────────┐   ┌────────────────┐ │   ┌─────────────┐
│ Client │─────────▶│  │ Rule Fetcher │   │ Counter Store  │ │──▶│  Backend    │
└────────┘          │  │ (local cache)│   │   (Redis)      │ │   │  Services   │
                    │  └──────┬───────┘   └────────┬───────┘ │   └─────────────┘
                    │         │                     │         │
                    │         ▼                     ▼         │
                    │  ┌──────────────┐   ┌────────────────┐ │
                    │  │  Rules DB    │   │  Rate Limiter  │ │
                    │  │  (MySQL)     │   │   Algorithm    │ │
                    │  └──────────────┘   └────────────────┘ │
                    └─────────────────────────────────────────┘
                                          │
                              ┌───────────▼──────────┐
                              │   Response to Client  │
                              │ 200 OK + headers, OR  │
                              │ 429 Too Many Requests │
                              └──────────────────────┘

Response headers always include:
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 43
  X-RateLimit-Reset: 1687392000
```

The rate limiter sits between the API Gateway and backend services. It checks Redis for current counters, evaluates rules cached locally, and either forwards the request or rejects it. The backend never sees rate-limited requests.

---

## Low Level Design

### The Core Algorithms — Picking the Right One

This is the most important part of this design. There are four common algorithms and each has a real trade-off.

**Token Bucket**

Imagine a bucket with a maximum capacity of 100 tokens. Tokens refill at a fixed rate — say 10 tokens/second. Each request consumes one token. If the bucket is empty, reject. If not, consume and allow.

This is the most widely used algorithm. It handles burst traffic naturally — if a user makes no requests for 10 seconds, they've accumulated 100 tokens and can fire a burst. AWS API Gateway, Stripe, and most payment APIs use token bucket because it's forgiving of legitimate bursts.

```
state per user: { tokens: float, last_refill_time: timestamp }

on each request:
  elapsed = now - last_refill_time
  tokens = min(capacity, tokens + elapsed * refill_rate)
  last_refill_time = now
  if tokens >= 1:
    tokens -= 1
    allow request
  else:
    reject with 429
```

**Sliding Window Log**

Store a log of timestamps for every request in the last window. On each request, evict old timestamps, count remaining, allow or reject. Accurate but expensive — storing timestamps for every request per user doesn't scale at high throughput.

**Fixed Window Counter**

Divide time into fixed windows — 0:00 to 0:59, 1:00 to 1:59. Count requests per window. Simple and fast, but has a boundary problem: a user can make 100 requests at 0:59 and 100 more at 1:00 — 200 requests in 2 seconds while the limit is 100/minute.

**Sliding Window Counter** (best balance)

Combine fixed window counters with a weighted calculation. Current count = current window count + (previous window count × overlap percentage). For example, if we're 30% into the current minute, we weight the previous minute's count at 70%. This eliminates the boundary spike while keeping memory usage low.

This is what I'd recommend — it's accurate, memory-efficient, and Redis supports it natively.

---

### Redis Data Structures

For **Token Bucket** — store as a Redis Hash per user:

```
key:   rate_limit:user:{user_id}
field: tokens → 97.5
field: last_refill → 1687391823.456
TTL:   set to window_size (auto-cleanup for inactive users)
```

Use Redis Lua script to make the read-modify-write atomic. This is critical — without atomicity, two concurrent requests can both read "1 token remaining," both allow themselves, and you've exceeded the limit.

```lua
-- Atomic token bucket check in Lua (runs as single Redis operation)
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1  -- allowed
else
    return 0  -- rejected
end
```

For **Sliding Window Counter** — use Redis sorted sets:

```
key:   rate_limit:user:{user_id}
value: ZADD key <timestamp> <request_id>
       ZREMRANGEBYSCORE key 0 (now - window_ms)
       ZCARD key → current count
```

---

### Rules Configuration

Rate limit rules are stored in MySQL — configurable per endpoint, per user tier, per API key:

```sql
CREATE TABLE rate_limit_rules (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    rule_key     VARCHAR(100) NOT NULL,  -- "user", "ip", "api_key"
    endpoint     VARCHAR(200),           -- null = applies to all endpoints
    user_tier    VARCHAR(50),            -- "free", "paid", "enterprise"
    limit_count  INT NOT NULL,           -- 100
    window_secs  INT NOT NULL,           -- 60
    algorithm    VARCHAR(20) NOT NULL,   -- "token_bucket", "sliding_window"
    created_at   DATETIME NOT NULL
);
```

Rules are loaded into local in-memory cache on each rate limiter instance at startup, refreshed every 60 seconds. This avoids hitting MySQL on every request — rules change infrequently.

---

### Where the Rate Limiter Lives

Three options:

**Option A — Client-side:** Doesn't work. Client controls it, easily bypassed.

**Option B — API Gateway middleware:** Best for most cases. Single point of enforcement, close to the edge. This is what I'd build.

**Option C — Per-service:** Each backend service rate limits itself. Better for internal service-to-service rate limiting, but means duplicated logic.

For this design, rate limiter lives as middleware in the API Gateway. Every request passes through it before reaching any backend service.

---

## Scale — What Breaks at 10x?

At 16M checks/sec, a single Redis node breaks — it can handle maybe 200K ops/sec. 

**Redis Cluster:** Shard by `user_id`. Each shard handles a subset of users. The rate limiter hashes `user_id` to pick the right shard — consistent hashing so rebalancing moves minimal data.

**Multi-region consistency problem:** If the user sends requests to both US and India data centers, each region has its own Redis. A user could make 100 requests to US and 100 to India — 200 total, double the limit. 

Solutions:
- Sticky routing: route user always to same region (via GeoDNS). Simple but fails if their region goes down.
- Global Redis (Elasticache Global Datastore): eventually consistent cross-region replication. Accept slight over-limit tolerance — if the limit is 100, users might get 110 across regions. Usually acceptable.
- Centralized counter with local approximation: local Redis handles most checks, syncs to global every 100ms. Trade accuracy for latency.

For most products, sticky routing is fine. For strict financial rate limiting, accept slight over-limit with global sync.

**Hot users:** A single celebrity account making thousands of requests could hot-spot one Redis shard. Add a local in-memory counter as a first check — reject obviously over-limit requests before they even hit Redis. Local counter syncs to Redis every 100ms.

---

## Trade-offs

**Token bucket vs sliding window:** Token bucket is better when you want to allow short bursts — legitimate mobile clients reconnecting after network drop. Sliding window is better when you need strict per-minute accuracy — financial API, SMS sending. I'd default to token bucket and switch to sliding window for regulated use cases.

**Redis vs in-process:** In-process rate limiting (each server tracks its own count) is extremely fast but doesn't coordinate across servers. If you have 10 API servers and the limit is 100/min, a user could actually make 1,000 requests. Only works for single-server deployments. Redis adds ~1ms latency but gives consistent limits across all servers.

**Hard reject vs soft throttle:** Hard 429 is the right default. Soft throttle (adding artificial delay) keeps connections open and can backfire — slow clients pile up and exhaust connection pools. Reject fast, let clients back off.

---

## Cross-Questions

**How do you handle the race condition when two requests arrive simultaneously?**

Redis Lua scripts execute atomically — the entire script runs as a single Redis operation with no interleaving. This guarantees that read-modify-write of the token counter is safe. Without Lua, you'd need Redis MULTI/EXEC transactions, which are less ergonomic and can retry on conflict. Lua is the standard approach here.

**What if Redis goes down?**

Two choices: fail open (allow all requests) or fail closed (reject all). For most APIs, fail open is correct — a brief window of unprotected traffic is better than a full outage. For security-critical APIs like payment or authentication, fail closed. Implement a circuit breaker: if Redis latency exceeds 50ms or error rate exceeds 5%, fall back to local in-memory rate limiting with looser limits.

**How would you rate limit by IP for unauthenticated requests?**

Same algorithm, different key: `rate_limit:ip:{ip_address}`. The challenge is IP spoofing and NAT — an office building with 500 employees behind one NAT IP would all share one limit. Handle this by combining IP + User-Agent fingerprint, or by using lower limits per IP but exempting known corporate IP ranges. For logged-in users, always prefer user-based limiting over IP-based.

**How do you communicate rate limit info to clients?**

Standard HTTP headers on every response — even successful ones:
- `X-RateLimit-Limit: 100` — the rule
- `X-RateLimit-Remaining: 43` — how many left
- `X-RateLimit-Reset: 1687392000` — Unix timestamp when window resets
- `Retry-After: 30` — on 429, how many seconds to wait

Clients that respect these headers can self-throttle and avoid hammering the limit. This is how Stripe, GitHub, and Twitter's APIs work.

**How would you implement different limits for free vs paid users?**

The rule lookup checks `user_tier` from the JWT or session. Free users get `rate_limit:free:user:{id}` checked against the free-tier rule (say 100/hour). Paid users get `rate_limit:paid:user:{id}` against a higher limit (1000/hour). Enterprise customers might get no limit or a custom limit stored in the rules table. The algorithm is the same — only the capacity and refill rate differ.
