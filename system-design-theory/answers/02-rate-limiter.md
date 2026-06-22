# Q2: Design Rate Limiter

---

## How to Approach This in an Interview

Rate limiter is a design interview that tests whether you understand distributed systems consistency under concurrency. The interesting part isn't the algorithm — it's how you make it work correctly when 10 servers are checking limits simultaneously.

---

## Clarifying Questions

**1. Where does the rate limiter live?**

"Is this a standalone service we're building, or middleware inside an existing API gateway? Or are we embedding it per-service?"

*Why this matters:* Placement determines deployment model. API Gateway middleware is the most common — every request passes through one chokepoint. Per-service means duplicated logic but works for internal service-to-service limits.

**2. Who are we limiting and on what rule?**

"Are we limiting by user, by IP address, by API key? And is it one global rule like '100 requests per minute' or does each endpoint have its own limit?"

*Why this matters:* Per-endpoint rules need a rules configuration system. Global rules are simpler. The key structure in Redis changes based on what dimension you're limiting.

**3. What happens when the limit is hit?**

"Hard reject with 429 Too Many Requests? Or soft throttle — add artificial latency?"

*Why this matters:* Hard reject is almost always right. Soft throttle (adding delay) keeps connections open and can exhaust your server's connection pool. Reject fast and let clients back off.

**4. Single region or distributed?**

"Is this one data center or are we multi-region? Multi-region means a user in India and the same user in the US could be on different servers."

*Why this matters:* Multi-region is the hardest part of rate limiting. Different regions can't see each other's counters without coordination.

### Assumptions

```
- Rate limiter as API Gateway middleware (in the path of every request)
- Limit by user_id (authenticated) and IP (unauthenticated)
- Rules configurable per endpoint and per user tier
- Hard 429 rejection when limit exceeded
- Starting with single region, multi-region is a follow-up
- 10M active users, peak 1.6M requests/sec → 1.6M rate limit checks/sec
- Each check must be sub-millisecond (rate limiter is in critical path)
```

---

## Back-of-Envelope Math

```
10M active users
Each user: 10 requests/minute average
Rate limit checks/sec: 10M × 10 / 60 = 1.67M checks/sec at average load
Peak (3x): ~5M checks/sec

Each check: Redis lookup + decision + update
Redis handles ~500K-1M ops/sec per node
→ Need Redis cluster for production scale

Latency budget: rate limiter adds overhead to EVERY request
Target: < 1ms for the rate limit check
Redis in same datacenter: 0.1-0.5ms round trip → feasible
```

---

## High Level Design

```
                    ┌─────────────────────────────────────────┐
                    │           Rate Limiter Middleware        │
                    │                                          │
┌────────┐  HTTPS   │  ┌──────────────┐   ┌────────────────┐ │   ┌─────────────┐
│ Client │─────────▶│  │ Rule Fetcher │   │ Counter Store  │ │──▶│  Backend    │
└────────┘          │  │ (local cache)│   │   (Redis)      │ │   │  Services   │
          ← 429     │  └──────┬───────┘   └────────┬───────┘ │   └─────────────┘
   or 200           │         │                     │         │
                    │         ▼                     ▼         │
                    │  ┌──────────────┐   ┌────────────────┐ │
                    │  │  Rules DB    │   │  RL Algorithm  │ │
                    │  │  (MySQL)     │   │  (Token Bucket │ │
                    │  └──────────────┘   │  or Sliding W) │ │
                    │                     └────────────────┘ │
                    └─────────────────────────────────────────┘

Every request (allowed OR rejected) includes these headers:
  X-RateLimit-Limit:     100       ← what the rule says
  X-RateLimit-Remaining: 43        ← how many left this window
  X-RateLimit-Reset:     1687392000 ← unix timestamp when window resets
  Retry-After:           30        ← only on 429, how long to wait
```

**Why the rate limiter is at the API Gateway, not inside each backend service?**

If 10 backend services each implement rate limiting independently, you'd have duplicated Redis connections, inconsistent behavior, and 10x the operational complexity. One API Gateway layer enforces limits centrally before any backend service sees the request. Rejected requests never touch business logic.

---

## The Four Rate Limiting Algorithms

This is what interviewers want depth on. Know all four, their trade-offs, and when to use each.

---

### Algorithm 1: Token Bucket (Most Common)

**The mental model:**

Imagine a physical bucket that holds tokens. The bucket has a maximum capacity (say 100 tokens). Tokens fall into the bucket at a fixed rate (say 10 tokens per second). Each API request removes one token. If the bucket is empty, reject the request.

```
[Bucket capacity: 100]

At t=0:  bucket = 100 tokens (full)
Request: remove 1 → bucket = 99

... user makes 99 more requests ...

At t=5s: bucket = 0 tokens, but 50 new tokens have dripped in
         (5 seconds × 10 tokens/sec = 50)
         bucket = 50

Request: remove 1 → bucket = 49
Request: remove 1 → bucket = 48
... 48 more requests ...
Request: bucket = 0 → REJECT with 429

At t=10s: another 50 tokens drip in → bucket = 50
```

**Why this is better than simple per-minute counters:**

A user who hasn't made requests for 30 seconds has accumulated tokens. They can make a short burst — which is legitimate (a mobile app reconnecting after network drop). Token bucket is **burst-friendly** by design.

**The algorithm in code:**

```python
def token_bucket_check(user_id: str, capacity: int, refill_rate: float) -> bool:
    """
    capacity:     max tokens in bucket (e.g., 100)
    refill_rate:  tokens per second (e.g., 10.0)
    Returns True if allowed, False if rejected
    """
    now = time.time()
    key = f"rate_limit:{user_id}"
    
    # Read current state
    state = redis.hmget(key, 'tokens', 'last_refill')
    tokens = float(state[0]) if state[0] else capacity
    last_refill = float(state[1]) if state[1] else now
    
    # How much time passed? Add those tokens back.
    elapsed = now - last_refill
    tokens = min(capacity, tokens + elapsed * refill_rate)
    
    # Is there a token available?
    if tokens >= 1.0:
        tokens -= 1.0
        redis.hmset(key, {'tokens': tokens, 'last_refill': now})
        redis.expire(key, 3600)  # cleanup inactive users
        return True  # allowed
    else:
        # Don't update last_refill — tokens are still accumulating
        return False  # rejected
```

**Critical problem with this code:** Race condition. What if two requests arrive simultaneously? Both read `tokens = 1.0`. Both check `>= 1.0`. Both subtract. Both write `tokens = 0.0`. Two requests passed when only one should have. This is the classic **check-then-act** race condition.

**The fix: Redis Lua scripts (atomic execution)**

Redis is single-threaded. Lua scripts run entirely before any other Redis command. This makes the entire read-compute-write operation atomic — no other request can interleave.

```lua
-- This entire script runs as one atomic Redis operation
-- No other command can run between any of these lines
local key = KEYS[1]
local capacity = tonumber(ARGV[1])      -- 100
local refill_rate = tonumber(ARGV[2])   -- 10.0 tokens/second
local now = tonumber(ARGV[3])           -- current Unix timestamp

-- Read current state
local data = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(data[1]) or capacity    -- default: full bucket
local last_refill = tonumber(data[2]) or now

-- Compute new token count based on elapsed time
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

if tokens >= 1 then
    tokens = tokens - 1
    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
    redis.call('EXPIRE', key, 3600)
    return 1   -- ALLOWED
else
    -- Still update last_refill so next call has correct elapsed time
    redis.call('HSET', key, 'last_refill', now)
    return 0   -- REJECTED
end
```

**Calling from Python:**

```python
# Load the script once at startup
LUA_SCRIPT = redis.register_script(TOKEN_BUCKET_LUA)

def check_rate_limit(user_id: str) -> bool:
    result = LUA_SCRIPT(
        keys=[f"rate_limit:{user_id}"],
        args=[100, 10.0, time.time()]
    )
    return result == 1  # 1 = allowed, 0 = rejected
```

**Redis data structure used:**

```
Key:   rate_limit:user:12345
Type:  Hash (HMSET/HMGET)
Fields:
  tokens:       97.5        ← current float token count
  last_refill:  1687391823  ← Unix timestamp of last access
TTL:   3600 seconds (cleanup if user inactive)
```

Why Hash and not String? Because we need two values (tokens + last_refill) and hash atomically stores/reads both.

---

### Algorithm 2: Fixed Window Counter

**How it works:**

Divide time into fixed windows: 12:00:00-12:00:59, 12:01:00-12:01:59, etc. Count requests per user per window. Reject if count > limit.

```
Window 12:00: user made 80 requests (limit=100) ✓
Window 12:01: user made 20 requests so far ✓

Redis: INCR rate:user:12345:window:202606221200  → returns 81
       EXPIRE rate:user:12345:window:202606221200 60
```

**Implementation:**

```python
def fixed_window_check(user_id: str, limit: int) -> bool:
    # Window key includes minute timestamp
    window = int(time.time() / 60)  # current minute as integer
    key = f"rate:fixed:{user_id}:{window}"
    
    count = redis.incr(key)       # atomically increment
    if count == 1:
        redis.expire(key, 60)     # set TTL on first request in window
    
    return count <= limit
```

**The boundary problem (why not to use this in production):**

```
Limit: 100 requests per minute

At 12:00:59 — user makes 100 requests (hits limit)
At 12:01:00 — new window starts, counter resets
At 12:01:01 — user makes 100 more requests

Result: 200 requests in 2 seconds!

[Window A: 12:00:00-12:00:59]    100 requests ← fills window
[Window B: 12:01:00-12:01:59]    100 requests ← new window, counter reset
                ↑ boundary: 200 requests happened in 2 seconds
```

For most applications this is fine — the boundary condition is rare and minor. For rate-limiting a payment API where exactly 100/min is critical, this is unacceptable.

---

### Algorithm 3: Sliding Window Log

**How it works:**

Keep an exact log of timestamps for every request in the current window. On each request, delete old timestamps (outside the window), count remaining, allow or reject.

```python
def sliding_window_log_check(user_id: str, limit: int, window_secs: int) -> bool:
    key = f"rate:log:{user_id}"
    now = time.time()
    window_start = now - window_secs
    
    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)  # remove old entries
    pipe.zadd(key, {str(uuid4()): now})          # add this request
    pipe.zcard(key)                              # count in window
    pipe.expire(key, window_secs)
    results = pipe.execute()
    
    count = results[2]
    return count <= limit
```

**Why not use this at scale:**

Stores one entry per request. For a user making 10K requests/hour, the sorted set has 10K members = significant memory per user. At 10M users × 1KB average = 10GB just for rate limit logs. For low-traffic users it's fine, but it doesn't scale to high-throughput users.

---

### Algorithm 4: Sliding Window Counter (Best Balance — Recommended)

**How it works:**

Use two fixed-window counters: one for the current minute, one for the previous minute. Estimate the actual sliding window count by weighting the previous counter by how much of the previous window is still "in scope."

**The math with an example:**

```
Limit: 100 requests per minute

Current time: 12:01:45 (45 seconds into current minute)

Previous window (12:00:00 - 12:00:59): 80 requests
Current window (12:01:00 - 12:01:59): 30 requests so far

How much of the previous window is still in the 1-minute sliding window?
  Current position: 45 seconds into 12:01
  = we're 45/60 = 75% into the current window
  = only the last 25% of the previous window is still "in scope"
  
Sliding window estimate:
  = current_count + (previous_count × (1 - position_in_current_window))
  = 30 + (80 × (1 - 0.75))
  = 30 + (80 × 0.25)
  = 30 + 20
  = 50

User has made estimated 50 requests in the last 60 seconds.
50 < 100 → ALLOW
```

**The formula:**

```
sliding_count = current_window_count 
              + previous_window_count × (1 - elapsed_fraction_in_current_window)

where elapsed_fraction = (current_time % window_size) / window_size
```

**Implementation:**

```python
def sliding_window_counter_check(user_id: str, limit: int, window_secs: int) -> bool:
    now = time.time()
    current_window = int(now / window_secs)
    previous_window = current_window - 1
    
    # Position within current window (0.0 to 1.0)
    elapsed_fraction = (now % window_secs) / window_secs
    
    curr_key = f"rate:sw:{user_id}:{current_window}"
    prev_key = f"rate:sw:{user_id}:{previous_window}"
    
    # Atomically get both and increment current
    pipe = redis.pipeline()
    pipe.get(prev_key)
    pipe.incr(curr_key)
    pipe.expire(curr_key, window_secs * 2)
    results = pipe.execute()
    
    prev_count = int(results[0] or 0)
    curr_count = int(results[1])
    
    # Estimate sliding window count
    sliding_count = curr_count + prev_count * (1 - elapsed_fraction)
    
    if sliding_count > limit:
        # Undo the increment — we're going to reject
        redis.decr(curr_key)
        return False  # rejected
    
    return True  # allowed
```

**Why this is the recommended algorithm:**

- No boundary problem (unlike fixed window)
- O(1) memory — just two integer counters per user per window
- No timestamps stored (unlike sliding window log)
- Good enough accuracy for most rate limiting needs
- Slightly under-counts in edge cases, which is acceptable — better to slightly over-allow than to be complex

---

## Rules Configuration

Rate limit rules stored in MySQL, cached locally in-memory on each rate limiter instance:

```sql
CREATE TABLE rate_limit_rules (
    id           INT PRIMARY KEY AUTO_INCREMENT,
    rule_key     VARCHAR(100) NOT NULL,   -- 'user', 'ip', 'api_key'
    endpoint     VARCHAR(200),            -- NULL = applies to ALL endpoints
    user_tier    VARCHAR(50),             -- 'free', 'paid', 'enterprise'
    limit_count  INT NOT NULL,            -- 100
    window_secs  INT NOT NULL,            -- 60
    algorithm    VARCHAR(20) NOT NULL,    -- 'token_bucket', 'sliding_window'
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   DATETIME NOT NULL
);

-- Example rules:
-- free users: 100 requests/minute globally
-- paid users: 1,000 requests/minute globally
-- /v1/auth/login: 10 requests/minute per IP (brute force protection)
-- /v1/send-sms: 5 requests/hour per user (cost protection)
```

**Why cache rules locally?**

Every request needs to check the rule. If we queried MySQL for every request, that's 1.6M MySQL queries/sec — MySQL can't sustain that. Rules change maybe once a day. So: load all rules into in-memory dictionary at startup, refresh every 60 seconds via a background job.

```python
# Local in-memory cache on each rate limiter instance
_rules_cache: dict[str, RateLimitRule] = {}
_cache_loaded_at: float = 0

def get_rule(endpoint: str, user_tier: str) -> RateLimitRule:
    if time.time() - _cache_loaded_at > 60:  # refresh every 60 seconds
        refresh_rules_from_db()
    
    # Check most specific rule first, fall back to general
    rule = (_rules_cache.get(f"{endpoint}:{user_tier}") or
            _rules_cache.get(f"{endpoint}:*") or
            _rules_cache.get(f"*:{user_tier}") or
            _rules_cache.get("*:*"))
    return rule
```

---

## Where the Rate Limiter Lives

**Option A: Client-side** — Never. Client controls it, trivially bypassed.

**Option B: API Gateway middleware** — Best for external-facing APIs. Single enforcement point. This is what I'd build.

```
Client → Load Balancer → API Gateway (rate limiter here) → Backend Services
                                ↑
                         All traffic passes through
                         Redis check: ~0.5ms overhead
```

**Option C: Per-service middleware** — Useful for internal service-to-service rate limiting (prevent a buggy service from hammering another). Each service has its own Redis counters. Coexists with API Gateway rate limiting — two layers.

**Option D: Service mesh (Envoy/Istio sidecar)** — For Kubernetes deployments, rate limiting at the sidecar level. Each service's sidecar checks limits before forwarding to the service. Same Redis-backed approach, but configurable via service mesh control plane.

---

## Full Request Flow

```
Step 1: Request arrives at API Gateway
        Extract: user_id from JWT, IP address, endpoint path

Step 2: Determine applicable rule
        get_rule("/v1/payments", "free") → {limit: 10/min, algo: token_bucket}

Step 3: Check Redis (using Lua script for atomicity)
        key = "rate:user:12345"
        result = lua_script.execute(key, capacity=10, refill_rate=0.167, now=now)
        
        If result == 0: REJECT
          → Return 429 with headers:
            X-RateLimit-Limit: 10
            X-RateLimit-Remaining: 0
            Retry-After: 30
          → Log: {user: 12345, endpoint: /v1/payments, action: rejected}
        
        If result == 1: ALLOW
          → Compute remaining tokens from Redis state
          → Add headers to forwarded request:
            X-RateLimit-Limit: 10
            X-RateLimit-Remaining: 7
          → Forward to backend service

Step 4: Backend processes, returns response
        Rate limiter passes response through (adds headers)
        Returns to client

Total overhead: ~0.5ms (one Redis round trip)
```

---

## Scale — What Breaks at 10x?

**Current:** 1.6M checks/sec
**10x:** 16M checks/sec

**Redis becomes the bottleneck first.**

A single Redis node handles ~500K-1M simple ops/sec. At 16M checks/sec with a Lua script (which is slightly heavier than simple GET/SET), we'd need ~20-30 Redis nodes.

**Fix: Redis Cluster**

Redis Cluster shards data across multiple nodes. The rate limiter hashes `user_id` to determine which shard to use.

```python
# Redis Cluster automatically routes based on key hash
# Key "rate:user:12345" → hash → shard 3 → Node 3

redis_cluster = RedisCluster(nodes=[
    {"host": "redis-1", "port": 7001},
    {"host": "redis-2", "port": 7001},
    {"host": "redis-3", "port": 7001},
])

# All writes for user 12345 go to the same shard
# Consistent hashing: adding a new node only moves ~1/N keys
```

**The multi-region problem:**

If we have US and India regions with separate Redis instances:

```
User makes requests: 50 to US, 60 to India
Each region sees: 50 requests (US) and 60 requests (India)
Each allows the user (under 100 limit)
Reality: 110 requests made — 10% over limit

This is the "thundering herd across regions" problem
```

**Solutions:**

1. **Sticky routing** (simplest): Route each user to the same region via GeoDNS. All requests for user 12345 always go to `us-east-1`. Perfect accuracy. Fails if that region goes down.

2. **Global Redis with replication** (AWS Elasticache Global Datastore): Cross-region replication with ~100ms lag. User can make ~10% over limit during the replication window. Usually acceptable.

3. **Local counter + sync** (most scalable): Each region maintains its own counter, syncs to a global counter every 100ms. Accept up to 10% over-limit for a 100ms window. Best performance, slight inaccuracy.

For most products, sticky routing is sufficient. Implement global sync only if over-limit tolerance is unacceptable.

**Hot users:**

A celebrity API key making thousands of requests/sec could hot-spot one Redis shard. Fix: local in-memory counter as first check. The rate limiter process keeps a per-user in-memory counter, checks it first, only writes to Redis every 100ms. Requests obviously way over limit are rejected locally without a Redis call.

---

## Trade-offs

**Token bucket vs sliding window counter:**

| Aspect | Token Bucket | Sliding Window Counter |
|--------|-------------|----------------------|
| Burst handling | Allows legitimate bursts | Smooth limit |
| Memory | Hash (2 fields) | 2 integer counters |
| Accuracy | Exact | ~Exact (slight estimation) |
| Best for | Public APIs, mobile clients | Financial APIs, SMS sending |

Default to token bucket for external APIs. Use sliding window counter when you need strict per-unit-time accuracy (billing, regulated systems).

**Redis vs in-process:**

In-process rate limiting (each server counts its own requests) is zero-latency but doesn't coordinate. With 10 API servers, a user can actually make 10x the limit. Only correct for single-server deployments or when approximate limits are acceptable.

Redis adds ~0.5ms but gives correct distributed limiting. For a public API, Redis is non-negotiable.

**Hard 429 vs soft throttle:**

Soft throttle (sleep 50ms to slow the user down) sounds gentle but is dangerous: it keeps the connection open, consuming a thread/goroutine. A sustained attack creates thousands of slow connections that exhaust the server's connection pool. Hard 429 closes the connection immediately, freeing resources. Always use hard reject.

---

## Cross-Questions

**Q: How does the Lua script prevent race conditions exactly?**

Redis is single-threaded — it processes one command at a time. A Lua script runs as a single atomic command. No other Redis command can execute between any line of the Lua script.

Without Lua, imagine two requests arriving simultaneously:
```
Thread 1: GET rate:user:123 → returns 99
Thread 2: GET rate:user:123 → returns 99  (hasn't seen Thread 1's write yet)
Thread 1: SET rate:user:123 100 (incremented)
Thread 2: SET rate:user:123 100 (incremented again, should be 101)

Result: both are allowed, but we've exceeded the limit
```

With Lua:
```
Thread 1 starts Lua script: acquires Redis single-thread lock
Thread 2 is queued: waits
Thread 1 Lua: GET 99, SET 100, return 1 (allowed)
Thread 2 Lua: GET 100, already at limit, return 0 (rejected)

Result: correct
```

**Q: What if Redis goes down?**

Two strategies based on the product:

**Fail open** (recommended for most APIs): If Redis is unavailable, allow all requests through. A brief window of unprotected traffic is better than a complete API outage. Use a circuit breaker pattern:

```python
def check_rate_limit(user_id: str) -> bool:
    try:
        return redis_lua_check(user_id)
    except RedisConnectionError:
        # Circuit breaker: Redis is down, fail open
        # But log this so ops gets alerted
        metrics.increment("rate_limit.redis_failure")
        return True  # allow through
```

**Fail closed** (for security-critical endpoints): If the limit check fails, reject the request. Appropriate for login endpoints, payment APIs where security > availability.

**Q: How do you rate limit unauthenticated requests by IP?**

Same algorithm, different Redis key: `rate:ip:{ip_address}`.

Problems with IP rate limiting:
- **NAT**: An entire office behind one IP — 500 employees share one limit
- **IPv6**: Users can easily cycle through IPv6 addresses
- **CDN/VPN**: Cloudflare exit nodes will appear as one IP

Mitigations:
- Use IP rate limiting as a coarse filter (e.g., 1,000/min per IP) to catch bots
- For authenticated endpoints, always prefer user-based limits
- Allowlist corporate IP ranges if you know them

**Q: How do you handle different limits for free vs paid vs enterprise users?**

Rule lookup includes user tier from JWT claims:

```python
def get_limit(user_id: str, endpoint: str) -> RateLimitRule:
    # JWT contains user_tier: 'free', 'paid', 'enterprise'
    user_tier = jwt.claims['user_tier']
    
    # Rule lookup order: most specific → least specific
    return (
        rule_cache.get(f"{endpoint}:{user_tier}") or   # endpoint + tier
        rule_cache.get(f"{endpoint}:*") or             # endpoint only
        rule_cache.get(f"*:{user_tier}") or            # tier only
        rule_cache.get("*:*")                          # global default
    )

# Different Redis keys per tier prevents mixing counts
key = f"rate:{user_tier}:{user_id}"
```

Tier-based limits:
- free: 100 requests/minute → bucket capacity 100, refill 1.67/sec
- paid: 1,000 requests/minute → bucket capacity 1000, refill 16.7/sec
- enterprise: 10,000 requests/minute or unlimited (no rate limit check)

**Q: How would you expose rate limit information to clients so they can self-throttle?**

Include standard headers on every response (allowed or rejected):

```
HTTP/1.1 200 OK
X-RateLimit-Limit:     1000     ← the configured rule
X-RateLimit-Remaining: 847      ← how many left in window
X-RateLimit-Reset:     1687392060  ← Unix epoch when window resets

HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit:     1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset:     1687392060
Retry-After:           42       ← seconds until they can try again
```

Well-behaved clients (Stripe SDK, GitHub SDK, OpenAI Python client) automatically read `Retry-After` and wait before retrying. This eliminates retry storms — clients back off gracefully instead of hammering the 429 endpoint.

**Q: How would you handle a DDoS attack targeting a single IP?**

Layered defense:
1. CDN/Cloud WAF (Cloudflare) blocks obviously malicious IPs at the edge before reaching your servers — they have network-level detection
2. Your rate limiter blocks the IP after N requests/sec (say 1,000/sec per IP)
3. Your rate limiter detects a sudden spike in 429s from one IP and escalates to a longer block (30-minute ban via a Redis key with 30-min TTL)

A DDoS that exhausts your rate limiter's Redis is harder to handle — you need WAF-level protection before the request even reaches your infrastructure.
