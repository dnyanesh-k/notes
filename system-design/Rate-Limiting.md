# Rate Limiting

A comprehensive guide to rate limiting and throttling strategies for protecting APIs and services from abuse and ensuring fair resource usage.

---

## Table of Contents

1. [What is Rate Limiting?](#what-is-rate-limiting)
2. [Why Rate Limiting?](#why-rate-limiting)
3. [Rate Limiting Algorithms](#rate-limiting-algorithms)
4. [Rate Limiting Strategies](#rate-limiting-strategies)
5. [Distributed Rate Limiting](#distributed-rate-limiting)
6. [Rate Limiting Headers](#rate-limiting-headers)
7. [Implementation Considerations](#implementation-considerations)
8. [Real-World Examples](#real-world-examples)
9. [Interview Tips](#interview-tips)

---

# What is Rate Limiting?

## What is Rate Limiting?

**Rate limiting** is a technique used to control the number of requests a client can make to a server within a specific time period. It prevents abuse, ensures fair resource usage, and protects services from being overwhelmed.

**Simple definition:** A mechanism that limits how many requests a user or service can make in a given time window, like a bouncer at a club who only lets a certain number of people in per hour.

Rate limiting is essential for maintaining system stability, preventing denial-of-service attacks, and ensuring that all users get fair access to resources.

## Why Rate Limiting?

**Problems Without Rate Limiting:**
- A single user or bot can overwhelm the server with too many requests
- One abusive client can degrade service for all other users
- System resources can be exhausted, causing service unavailability
- API costs can skyrocket due to excessive usage
- No protection against distributed denial-of-service (DDoS) attacks

**Benefits With Rate Limiting:**
- Prevents abuse and protects system resources
- Ensures fair usage among all clients
- Helps maintain system stability and availability
- Controls costs by limiting excessive API calls
- Provides protection against DDoS attacks
- Improves user experience by preventing service degradation

---

# Rate Limiting Algorithms

## 1. Fixed Window Rate Limiting

**What is Fixed Window Rate Limiting?**

Fixed window rate limiting divides time into fixed intervals (windows) and allows a maximum number of requests per window. Each window is independent, and the counter resets at the start of each new window.

**How does it work?**

1. Time is divided into fixed windows (e.g., 1 minute, 1 hour)
2. Each window has a maximum request limit (e.g., 100 requests per minute)
3. When a request arrives, check if the current window has exceeded the limit
4. If limit not exceeded, allow the request and increment counter
5. If limit exceeded, reject the request
6. Counter resets at the start of the next window

**Example:**
- Limit: 10 requests per minute
- Window 1 (00:00-00:59): User makes 10 requests - all allowed
- Window 2 (01:00-01:59): Counter resets, user can make 10 more requests

**Characteristics:**
- Simple to implement and understand
- Memory efficient (only need to store counter per window)
- Can allow bursts at window boundaries (user can make 20 requests in 2 seconds if windows align)
- Not smooth distribution (all requests can happen at start of window)

**Advantages:**
- Simple implementation
- Low memory overhead
- Easy to understand and debug
- Works well for evenly distributed traffic

**Disadvantages:**
- Burst problem: User can make 2x limit at window boundaries
- Not smooth: All requests can happen at start of window
- Can be unfair if traffic is bursty

## 2. Sliding Window Rate Limiting

**What is Sliding Window Rate Limiting?**

Sliding window rate limiting tracks requests over a rolling time window. Instead of fixed intervals, it maintains a continuous sliding window that moves forward with time.

**How does it work?**

1. Track timestamps of requests in a sliding window
2. When a request arrives, count requests within the current window
3. If count is below limit, allow request and add timestamp
4. If count exceeds limit, reject request
5. Remove timestamps older than the window size

**Example:**
- Limit: 10 requests per minute
- Request at 00:00:30 - Count requests from 23:59:31 to 00:00:30
- If count < 10, allow request
- Remove any timestamps older than 1 minute

**Characteristics:**
- More accurate than fixed window
- Smooth distribution of requests
- Prevents burst at window boundaries
- Requires more memory (store timestamps)
- More complex to implement

**Advantages:**
- Prevents burst at window boundaries
- More accurate rate limiting
- Smooth request distribution
- Better user experience

**Disadvantages:**
- Higher memory overhead (store timestamps)
- More complex implementation
- Requires cleanup of old timestamps
- Slower performance than fixed window

## 3. Token Bucket Algorithm

**What is Token Bucket Algorithm?**

Token bucket algorithm maintains a bucket of tokens. Each request consumes a token, and tokens are refilled at a constant rate. Requests are allowed if tokens are available.

**How does it work?**

1. Bucket has a maximum capacity (e.g., 100 tokens)
2. Tokens are added to bucket at a constant rate (e.g., 10 tokens per second)
3. When a request arrives, check if tokens are available
4. If tokens available, allow request and remove one token
5. If no tokens available, reject request
6. Tokens never exceed bucket capacity (overflow is discarded)

**Example:**
- Bucket capacity: 10 tokens
- Refill rate: 2 tokens per second
- Initial state: 10 tokens
- Request 1: Consume 1 token (9 remaining)
- After 1 second: 2 tokens added (11, but capped at 10)
- Request 2-10: All allowed (tokens available)
- Request 11: Rejected (no tokens)

**Characteristics:**
- Allows bursts up to bucket capacity
- Smooth rate limiting over time
- Tokens accumulate when not used
- Good for variable traffic patterns
- Memory efficient (only store token count)

**Advantages:**
- Allows bursts (good for legitimate traffic spikes)
- Smooth rate limiting
- Tokens accumulate when idle
- Memory efficient
- Good for variable traffic

**Disadvantages:**
- Can allow large bursts (may not be desired)
- Requires periodic token refill logic
- Need to handle token overflow

## 4. Leaky Bucket Algorithm

**What is Leaky Bucket Algorithm?**

Leaky bucket algorithm is similar to token bucket but works in reverse. Requests are added to a bucket, and they leak out at a constant rate. If bucket overflows, requests are rejected.

**How does it work?**

1. Bucket has a maximum capacity (e.g., 100 requests)
2. Requests are added to bucket
3. Requests leak out at constant rate (e.g., 10 requests per second)
4. If bucket has space, add request to bucket
5. If bucket is full, reject request
6. Process requests from bucket at constant rate

**Example:**
- Bucket capacity: 10 requests
- Leak rate: 2 requests per second
- Request 1-10: Added to bucket
- Request 11: Rejected (bucket full)
- Every second: 2 requests processed from bucket

**Characteristics:**
- Smooth output rate (constant leak rate)
- Prevents bursts in output
- Requests queued in bucket
- Good for smoothing traffic
- Can cause delays for queued requests

**Advantages:**
- Smooth output rate
- Prevents bursts
- Good for traffic shaping
- Predictable behavior

**Disadvantages:**
- Can cause delays (requests queued)
- More complex than token bucket
- May not be suitable for real-time systems

## Algorithm Comparison

| Algorithm | Burst Handling | Memory | Complexity | Use Case |
|-----------|----------------|--------|------------|----------|
| Fixed Window | Allows bursts at boundaries | Low | Low | Simple APIs, evenly distributed traffic |
| Sliding Window | Prevents bursts | Medium | Medium | APIs requiring smooth rate limiting |
| Token Bucket | Allows controlled bursts | Low | Medium | APIs that need to handle traffic spikes |
| Leaky Bucket | Prevents bursts, smooths output | Medium | Medium | Traffic shaping, smoothing output |

---

# Rate Limiting Strategies

## 1. Per User Rate Limiting

**What is Per User Rate Limiting?**

Rate limiting applied per individual user. Each user has their own rate limit based on their user ID or authentication token.

**How it works:**
- Track requests per user ID
- Each user has independent rate limit
- User A can make 100 requests/minute
- User B can make 100 requests/minute
- Limits are independent

**Use Cases:**
- User-facing APIs
- APIs with user authentication
- Fair resource distribution
- Preventing individual user abuse

**Advantages:**
- Fair distribution among users
- Prevents single user from dominating
- Easy to implement with user authentication
- Can have different limits per user tier

**Disadvantages:**
- Requires user identification
- More storage needed (per user counters)
- Doesn't prevent distributed attacks from multiple users

## 2. Per IP Address Rate Limiting

**What is Per IP Rate Limiting?**

Rate limiting applied per IP address. All requests from the same IP share the same rate limit.

**How it works:**
- Track requests per IP address
- Each IP has independent rate limit
- IP 192.168.1.1 can make 100 requests/minute
- IP 192.168.1.2 can make 100 requests/minute
- Limits are independent

**Use Cases:**
- Public APIs without authentication
- DDoS protection
- Preventing IP-based abuse
- Anonymous access control

**Advantages:**
- Works without authentication
- Simple to implement
- Good for DDoS protection
- Prevents IP-based abuse

**Disadvantages:**
- Can block legitimate users behind NAT/proxy
- Multiple users behind same IP share limit
- Can be bypassed with multiple IPs
- Not fair for shared IPs (offices, schools)

## 3. Per API Key Rate Limiting

**What is Per API Key Rate Limiting?**

Rate limiting applied per API key. Each API key has its own rate limit, allowing different limits for different clients or tiers.

**How it works:**
- Track requests per API key
- Each API key has independent rate limit
- Free tier: 100 requests/minute
- Premium tier: 1000 requests/minute
- Enterprise tier: 10000 requests/minute

**Use Cases:**
- API services with multiple tiers
- Third-party integrations
- Different limits for different clients
- Monetization based on usage

**Advantages:**
- Supports tiered pricing
- Different limits per client
- Easy to monetize
- Good for API services

**Disadvantages:**
- Requires API key management
- More complex implementation
- Key sharing can bypass limits

## 4. Global Rate Limiting

**What is Global Rate Limiting?**

Rate limiting applied globally across all users. All requests share the same rate limit pool.

**How it works:**
- Single counter for all requests
- All users share the same limit
- Total system capacity: 10000 requests/minute
- All users compete for this pool

**Use Cases:**
- System-wide capacity limits
- Protecting backend resources
- Overall system protection
- Cost control

**Advantages:**
- Simple implementation
- Protects system resources
- Good for cost control
- Single point of control

**Disadvantages:**
- Not fair (one user can consume all capacity)
- Doesn't prevent individual abuse
- Poor user experience if abused

## 5. Tiered Rate Limiting

**What is Tiered Rate Limiting?**

Rate limiting with different limits for different user tiers or subscription levels.

**How it works:**
- Free tier: 100 requests/hour
- Basic tier: 1000 requests/hour
- Premium tier: 10000 requests/hour
- Enterprise: Unlimited (or very high limit)

**Use Cases:**
- SaaS applications
- API monetization
- Subscription-based services
- Freemium models

**Advantages:**
- Supports business models
- Fair for different tiers
- Encourages upgrades
- Flexible limits

**Disadvantages:**
- More complex to implement
- Requires tier management
- Need to handle tier changes

---

# Distributed Rate Limiting

## The Challenge

**Problem:** In a distributed system with multiple servers, rate limiting must work across all servers. A user should not be able to bypass limits by hitting different servers.

**Example:**
- Server 1: User makes 100 requests (limit: 100/minute)
- Server 2: Same user makes 100 requests (should be blocked, but server 2 doesn't know about server 1)

## Solutions

### 1. Centralized Rate Limiting Store

**How it works:**
- All servers use shared storage (Redis, Memcached)
- Rate limit counters stored in shared store
- All servers check and update same counters
- Atomic operations ensure consistency

**Example:**
- Redis stores: `user:123:requests` = 95
- Server 1: Check Redis, increment if < 100
- Server 2: Check Redis, sees 96, increments to 97
- Both servers see same count

**Advantages:**
- Accurate across all servers
- Single source of truth
- Works with any number of servers

**Disadvantages:**
- Requires shared storage (Redis)
- Network latency for each check
- Single point of failure (if Redis down)
- Can become bottleneck at scale

### 2. Distributed Rate Limiting with Consistent Hashing

**How it works:**
- Use consistent hashing to assign users to servers
- Each server handles rate limiting for assigned users
- User always hits same server for rate limiting
- Load balanced across servers

**Example:**
- User ID 123 → Hash → Server 3 (always)
- User ID 456 → Hash → Server 1 (always)
- Each server maintains its own rate limit counters

**Advantages:**
- No shared storage needed
- Lower latency (no network calls)
- Scales horizontally

**Disadvantages:**
- Server failure loses rate limit state
- Uneven distribution possible
- User must hit same server (sticky sessions)

### 3. Approximate Rate Limiting

**How it works:**
- Each server maintains local counters
- Periodically sync with other servers
- Accepts small inaccuracies for performance
- Good enough for most use cases

**Example:**
- Server 1: Local count = 95
- Server 2: Local count = 3
- Sync every 10 seconds
- Small window where limits can be exceeded

**Advantages:**
- Fast (local checks)
- No shared storage needed
- Good enough for most cases

**Disadvantages:**
- Not perfectly accurate
- Can allow slight limit violations
- Requires sync mechanism

---

# Rate Limiting Headers

## Standard Headers

Rate limiting information is typically communicated via HTTP headers.

### Request Headers

**X-RateLimit-Limit:** Maximum number of requests allowed in the time window
```
X-RateLimit-Limit: 100
```

**X-RateLimit-Remaining:** Number of requests remaining in current window
```
X-RateLimit-Remaining: 95
```

**X-RateLimit-Reset:** Time when the rate limit resets (Unix timestamp)
```
X-RateLimit-Reset: 1640995200
```

### Response Headers (When Limit Exceeded)

**429 Too Many Requests:** HTTP status code for rate limit exceeded

**Retry-After:** Number of seconds to wait before retrying
```
Retry-After: 60
```

## Example Response

**Success Response (200 OK):**
```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

**Rate Limit Exceeded (429 Too Many Requests):**
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

---

# Implementation Considerations

## Storage Options

### 1. In-Memory (Single Server)

**Use When:**
- Single server application
- Simple rate limiting needs
- No distributed requirements

**Advantages:**
- Fast (no network calls)
- Simple implementation
- No external dependencies

**Disadvantages:**
- Lost on server restart
- Doesn't work in distributed systems
- Limited scalability

### 2. Redis

**Use When:**
- Distributed systems
- Need persistence
- High performance requirements

**Advantages:**
- Fast (in-memory)
- Persistence options
- Atomic operations
- TTL support (automatic expiration)

**Disadvantages:**
- Requires Redis infrastructure
- Network latency
- Can become bottleneck

### 3. Database

**Use When:**
- Need strong consistency
- Already have database
- Lower performance requirements

**Advantages:**
- Strong consistency
- Persistent storage
- No additional infrastructure

**Disadvantages:**
- Slower than Redis
- Database load
- More complex queries

## Error Handling

### Graceful Degradation

**Strategy:** When rate limiting service is down, allow requests but log warning.

**Implementation:**
- Try to check rate limit
- If service unavailable, allow request
- Log warning for monitoring
- Don't block legitimate users

### Fail-Open vs Fail-Close

**Fail-Open:** If rate limiting fails, allow requests (better user experience, risk of abuse)

**Fail-Close:** If rate limiting fails, reject requests (safer, but blocks legitimate users)

**Recommendation:** Fail-open for most cases, but monitor and alert on failures.

## Performance Optimization

### 1. Caching

Cache rate limit results for short periods to reduce storage lookups.

### 2. Batch Updates

Update multiple counters in batch to reduce network calls.

### 3. Lazy Evaluation

Only check rate limits when necessary, not on every request.

### 4. Approximate Counting

Use probabilistic data structures (HyperLogLog) for approximate counting when exact counts aren't needed.

---

# Real-World Examples

## GitHub API

**Rate Limits:**
- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour

**Headers:**
```
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4999
X-RateLimit-Reset: 1640995200
```

## Twitter API

**Rate Limits:**
- Different limits per endpoint
- Tiered based on account type
- Rate limit windows vary (15 minutes, 1 hour, 24 hours)

## Stripe API

**Rate Limits:**
- Test mode: 25 requests/second
- Live mode: 100 requests/second
- Per API key

**Implementation:**
- Uses token bucket algorithm
- Distributed rate limiting with Redis
- Graceful degradation on failures

## AWS API Gateway

**Rate Limits:**
- Configurable per API key
- Burst limits and steady-state limits
- Uses token bucket algorithm
- Distributed across regions

---

# Interview Tips

## Common Questions

**Q: What is rate limiting and why is it important?**
- Rate limiting controls the number of requests a client can make in a time period
- Prevents abuse, ensures fair usage, protects system resources
- Essential for API stability and cost control

**Q: Explain the difference between fixed window and sliding window rate limiting.**
- Fixed window: Divides time into fixed intervals, counter resets at window boundary, can allow bursts at boundaries
- Sliding window: Rolling time window, more accurate, prevents bursts, requires more memory

**Q: What is the token bucket algorithm?**
- Maintains bucket of tokens, requests consume tokens, tokens refill at constant rate
- Allows bursts up to bucket capacity, smooth rate limiting, tokens accumulate when idle
- Good for variable traffic patterns

**Q: How do you implement rate limiting in a distributed system?**
- Use centralized store (Redis) for shared counters
- All servers check same counters, atomic operations ensure consistency
- Alternative: Consistent hashing to assign users to servers, each server maintains own counters

**Q: What are the trade-offs between different rate limiting algorithms?**
- Fixed window: Simple but allows bursts
- Sliding window: Accurate but more memory
- Token bucket: Allows bursts but more complex
- Leaky bucket: Smooth output but can cause delays

**Q: How do you handle rate limiting failures?**
- Graceful degradation: Allow requests if rate limiting service down
- Fail-open vs fail-close: Fail-open for better UX, fail-close for security
- Monitor and alert on failures

**Q: What HTTP headers are used for rate limiting?**
- X-RateLimit-Limit: Maximum requests allowed
- X-RateLimit-Remaining: Requests remaining
- X-RateLimit-Reset: When limit resets
- 429 status code: Rate limit exceeded
- Retry-After: Seconds to wait before retry

## Key Points to Remember

- **Rate limiting** = Control requests per time period
- **Fixed window** = Simple but allows bursts
- **Sliding window** = Accurate but more memory
- **Token bucket** = Allows bursts, smooth limiting
- **Distributed** = Use Redis or consistent hashing
- **Headers** = X-RateLimit-*, 429 status, Retry-After
- **Fail-open** = Better UX, fail-close = More secure
- **Use rate limiting** for API protection, fair usage, cost control

---

## Related Topics

- [API Design](./API-Design.md) - Rate limiting in API design
- [Caching](./Caching.md) - Caching rate limit results
- [Load Balancing](./LoadBalancing.md) - Rate limiting with load balancers
- [Databases](./Databases.md) - Using databases for rate limiting storage
