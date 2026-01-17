# Circuit Breaker Pattern

A comprehensive guide to the Circuit Breaker pattern for building resilient distributed systems that can gracefully handle failures and prevent cascading failures.

---

## Table of Contents

1. [What is Circuit Breaker?](#what-is-circuit-breaker)
2. [Why Circuit Breaker?](#why-circuit-breaker)
3. [Circuit Breaker States](#circuit-breaker-states)
4. [How Circuit Breaker Works](#how-circuit-breaker-works)
5. [Circuit Breaker Implementation](#circuit-breaker-implementation)
6. [Configuration Parameters](#configuration-parameters)
7. [Fallback Strategies](#fallback-strategies)
8. [Circuit Breaker vs Retry](#circuit-breaker-vs-retry)
9. [Real-World Examples](#real-world-examples)
10. [Interview Tips](#interview-tips)

---

# What is Circuit Breaker?

## What is Circuit Breaker?

**Circuit Breaker** is a design pattern used in distributed systems to prevent cascading failures. It monitors calls to a remote service and, if failures exceed a threshold, it "opens" the circuit to stop further calls, allowing the service to recover.

**Simple definition:** Like an electrical circuit breaker that trips when there's too much current, a software circuit breaker "trips" when a service is failing too much, preventing further damage and allowing it to recover.

The circuit breaker pattern helps systems fail fast and recover gracefully, rather than continuing to make failing requests that waste resources and potentially cause system-wide failures.

## Why Circuit Breaker?

**Problems Without Circuit Breaker:**
- Cascading failures: One failing service can bring down entire system
- Resource exhaustion: Continuous retries consume resources
- Slow response times: Waiting for timeouts on failing services
- User experience degradation: Users wait for requests that will fail
- No automatic recovery: System doesn't know when service is back

**Benefits With Circuit Breaker:**
- Prevents cascading failures by stopping calls to failing services
- Fails fast instead of waiting for timeouts
- Saves resources by not making unnecessary calls
- Allows services to recover without constant load
- Improves user experience with faster failure responses
- Automatic recovery when service is healthy again

---

# Circuit Breaker States

## Three States

A circuit breaker has three distinct states that determine how it handles requests.

### 1. Closed State (Normal Operation)

**What is Closed State?**

Closed state is the normal operating state where the circuit breaker allows requests to pass through to the service. It monitors the success and failure of requests to detect if the service is healthy.

**Characteristics:**
- Requests are allowed to pass through
- Success and failure rates are monitored
- If failure rate exceeds threshold, circuit opens
- This is the default state when service is healthy

**Behavior:**
- All requests forwarded to service
- Response times and errors tracked
- Metrics collected for monitoring
- No restrictions on traffic

**Example:**
- Service is healthy, handling requests normally
- Circuit breaker allows all requests
- Monitoring shows 99% success rate
- Circuit remains closed

### 2. Open State (Service Failing)

**What is Open State?**

Open state is when the circuit breaker has detected too many failures and stops allowing requests to pass through. It immediately fails requests without calling the service, allowing the service to recover.

**Characteristics:**
- Requests are immediately rejected
- No calls made to the service
- Fast failure response to clients
- Service gets time to recover
- After timeout period, moves to half-open state

**Behavior:**
- All requests immediately rejected
- No network calls to service
- Returns error immediately (or fallback)
- Service is protected from further load
- Timer started for recovery attempt

**Example:**
- Service failure rate exceeds 50%
- Circuit breaker opens
- Next 100 requests immediately rejected
- Service gets 30 seconds to recover
- After 30 seconds, moves to half-open

### 3. Half-Open State (Testing Recovery)

**What is Half-Open State?**

Half-Open state is a testing state where the circuit breaker allows a limited number of requests to test if the service has recovered. Based on the results, it either closes (service recovered) or opens again (service still failing).

**Characteristics:**
- Limited requests allowed (usually 1-5)
- Used to test if service recovered
- If test requests succeed, circuit closes
- If test requests fail, circuit opens again
- Short duration state

**Behavior:**
- Allows small number of test requests
- Monitors success of test requests
- If all succeed, circuit closes (service recovered)
- If any fail, circuit opens again (still failing)
- Prevents full traffic until recovery confirmed

**Example:**
- Circuit was open for 30 seconds
- Moves to half-open state
- Allows 3 test requests
- All 3 succeed → Circuit closes (recovered)
- Any fail → Circuit opens again (still failing)

## State Transitions

```
┌─────────┐
│ CLOSED  │ ← Normal operation, requests allowed
└────┬────┘
     │ Failure threshold exceeded
     ▼
┌─────────┐
│  OPEN   │ ← Service failing, requests rejected
└────┬────┘
     │ Timeout period elapsed
     ▼
┌─────────┐
│HALF-OPEN│ ← Testing recovery, limited requests
└────┬────┘
     │
     ├─→ All test requests succeed → CLOSED
     └─→ Any test request fails → OPEN
```

---

# How Circuit Breaker Works

## Step-by-Step Flow

### Normal Operation (Closed State)

1. **Request Arrives:** Client makes request to service
2. **Circuit Check:** Circuit breaker checks state (closed)
3. **Request Forwarded:** Request forwarded to service
4. **Response Received:** Service responds (success or failure)
5. **Metrics Updated:** Success/failure recorded
6. **Response Returned:** Response returned to client
7. **Threshold Check:** If failure rate < threshold, remain closed

### Failure Detection (Opening Circuit)

1. **Request Arrives:** Client makes request
2. **Circuit Check:** Circuit breaker checks state (closed)
3. **Request Forwarded:** Request forwarded to service
4. **Failure Detected:** Service fails or times out
5. **Metrics Updated:** Failure recorded, failure rate calculated
6. **Threshold Exceeded:** Failure rate exceeds threshold (e.g., 50%)
7. **Circuit Opens:** Circuit breaker opens, starts recovery timer
8. **Future Requests:** Subsequent requests immediately rejected

### Recovery Testing (Half-Open State)

1. **Recovery Timer:** Timeout period elapsed (e.g., 30 seconds)
2. **State Transition:** Circuit moves to half-open state
3. **Test Request:** Next request allowed through
4. **Service Call:** Request forwarded to service
5. **Result Check:**
   - If success: Circuit closes (service recovered)
   - If failure: Circuit opens again (still failing)

### Successful Recovery (Back to Closed)

1. **Test Requests:** Multiple test requests succeed
2. **Recovery Confirmed:** Service appears healthy
3. **Circuit Closes:** Circuit breaker returns to closed state
4. **Normal Operation:** All requests allowed again
5. **Monitoring Continues:** Metrics continue to be tracked

---

# Circuit Breaker Implementation

## Basic Implementation Components

### 1. State Management

**State Storage:**
- Current state (closed, open, half-open)
- Failure count
- Success count
- Last failure time
- State transition timestamps

**State Updates:**
- Atomic state transitions
- Thread-safe operations
- Persistent storage (optional)

### 2. Failure Detection

**Failure Criteria:**
- HTTP error status codes (5xx)
- Timeout exceptions
- Connection errors
- Custom error conditions

**Failure Counting:**
- Count failures in time window
- Calculate failure rate
- Compare with threshold

### 3. Threshold Configuration

**Failure Threshold:**
- Percentage of failures (e.g., 50%)
- Absolute failure count (e.g., 10 failures)
- Time window (e.g., last 60 seconds)

**Example:**
- Threshold: 50% failure rate
- Window: Last 60 seconds
- If 5 failures out of 10 requests → Open circuit

### 4. Recovery Timer

**Timeout Configuration:**
- Time to wait before testing recovery
- Configurable per service
- Usually 30-60 seconds

**Timer Management:**
- Start timer when circuit opens
- Check timer on each request
- Transition to half-open when timer expires

## Implementation Patterns

### 1. Client-Side Circuit Breaker

**Location:** Implemented in the client application making service calls.

**How it works:**
- Client library includes circuit breaker
- Wraps service calls
- Monitors responses
- Opens circuit on failures

**Advantages:**
- No changes needed to service
- Client controls behavior
- Works with any service

**Disadvantages:**
- Each client implements separately
- Inconsistent behavior across clients
- More code in each client

### 2. Service Mesh Circuit Breaker

**Location:** Implemented in service mesh (e.g., Istio, Linkerd).

**How it works:**
- Service mesh handles circuit breaking
- Transparent to application code
- Centralized configuration
- Consistent behavior

**Advantages:**
- No application code changes
- Centralized management
- Consistent behavior
- Easy to configure

**Disadvantages:**
- Requires service mesh infrastructure
- Additional complexity
- Learning curve

### 3. API Gateway Circuit Breaker

**Location:** Implemented in API Gateway.

**How it works:**
- API Gateway monitors backend services
- Opens circuit for failing backends
- Returns error or fallback
- Protects backend services

**Advantages:**
- Protects backend services
- Centralized at gateway
- Easy to configure
- Works for all clients

**Disadvantages:**
- Single point of failure
- Gateway becomes critical
- May not detect all failure types

---

# Configuration Parameters

## Key Parameters

### 1. Failure Threshold

**What is Failure Threshold?**

Failure threshold is the condition that triggers the circuit to open. It can be based on failure rate, absolute failure count, or a combination.

**Types:**
- **Failure Rate:** Percentage of requests that fail (e.g., 50%)
- **Failure Count:** Absolute number of failures (e.g., 10 failures)
- **Consecutive Failures:** Number of failures in a row (e.g., 5 consecutive)

**Example Configuration:**
```
failureThreshold: 50%  // Open if 50% of requests fail
failureCount: 10       // Or open after 10 failures
consecutiveFailures: 5 // Or open after 5 consecutive failures
```

### 2. Time Window

**What is Time Window?**

Time window is the period over which failures are counted. Only failures within this window are considered for threshold evaluation.

**Purpose:**
- Prevents old failures from affecting current state
- Sliding window for recent failures
- Configurable duration

**Example:**
```
timeWindow: 60 seconds  // Count failures in last 60 seconds
```

### 3. Recovery Timeout

**What is Recovery Timeout?**

Recovery timeout is the time to wait in open state before attempting to test recovery (transitioning to half-open state).

**Purpose:**
- Gives service time to recover
- Prevents immediate retry storms
- Configurable per service

**Example:**
```
recoveryTimeout: 30 seconds  // Wait 30 seconds before testing recovery
```

### 4. Half-Open Test Requests

**What are Half-Open Test Requests?**

The number of requests allowed in half-open state to test if the service has recovered.

**Purpose:**
- Tests service recovery
- Prevents full traffic until confirmed
- Usually 1-5 requests

**Example:**
```
halfOpenRequests: 3  // Allow 3 test requests in half-open state
```

### 5. Success Threshold

**What is Success Threshold?**

Success threshold is the condition for closing the circuit from half-open state. Usually all test requests must succeed.

**Purpose:**
- Confirms service recovery
- Prevents premature closing
- Ensures service is truly healthy

**Example:**
```
successThreshold: 100%  // All test requests must succeed
```

## Example Configuration

```yaml
circuitBreaker:
  failureThreshold: 50%        # Open if 50% failures
  timeWindow: 60               # Count failures in last 60 seconds
  recoveryTimeout: 30          # Wait 30 seconds before testing
  halfOpenRequests: 3          # Allow 3 test requests
  successThreshold: 100%       # All test requests must succeed
  timeout: 5000                # Request timeout: 5 seconds
```

---

# Fallback Strategies

## What are Fallback Strategies?

Fallback strategies define what to do when the circuit is open or a request fails. They provide alternative responses instead of just returning errors.

## Common Fallback Strategies

### 1. Return Default Value

**How it works:**
- Return a default or cached value
- User gets response immediately
- Service doesn't need to be called

**Example:**
- Product service down → Return cached product data
- User service down → Return default user profile
- Recommendation service down → Return popular items

**Use When:**
- Default values are acceptable
- Cached data available
- Read-only operations

**Advantages:**
- Fast response
- Better user experience
- No service dependency

**Disadvantages:**
- May return stale data
- Not suitable for critical operations
- Requires cache management

### 2. Return Empty Result

**How it works:**
- Return empty list, null, or empty object
- Indicates no data available
- Better than error for some cases

**Example:**
- Search service down → Return empty search results
- Notification service down → Return empty notifications list
- Analytics service down → Return empty analytics data

**Use When:**
- Empty result is acceptable
- Optional features
- Non-critical data

**Advantages:**
- Simple implementation
- No dependencies
- Graceful degradation

**Disadvantages:**
- User may not understand why empty
- May need to show message
- Not suitable for critical data

### 3. Call Alternative Service

**How it works:**
- Call a backup or alternative service
- Fallback to secondary data source
- Maintains functionality

**Example:**
- Primary database down → Use read replica
- Primary cache down → Use secondary cache
- Primary API down → Use backup API

**Use When:**
- Alternative service available
- Redundancy built in
- Critical functionality

**Advantages:**
- Maintains functionality
- High availability
- Seamless failover

**Disadvantages:**
- Requires backup services
- More complex
- May have different data

### 4. Queue for Later Processing

**How it works:**
- Queue request for later processing
- Return acknowledgment to user
- Process when service recovers

**Example:**
- Order service down → Queue order, return "processing"
- Email service down → Queue email, send later
- Payment service down → Queue payment, process later

**Use When:**
- Async processing acceptable
- Can handle eventual consistency
- Important operations

**Advantages:**
- No data loss
- Operations eventually complete
- Better than failure

**Disadvantages:**
- Requires queue infrastructure
- Eventual consistency
- May need retry logic

### 5. Return Error with Context

**How it works:**
- Return meaningful error message
- Include retry information
- Help user understand situation

**Example:**
- Service temporarily unavailable
- Please try again in 30 seconds
- Include retry-after header

**Use When:**
- No fallback available
- User needs to know status
- Temporary failures

**Advantages:**
- Transparent to user
- Sets expectations
- Better than generic error

**Disadvantages:**
- Still a failure from user perspective
- May need retry logic
- User experience impact

---

# Circuit Breaker vs Retry

## Key Differences

### Retry Pattern

**What is Retry?**
- Automatically retries failed requests
- Hopes service recovers quickly
- Continues trying until success or max retries

**Characteristics:**
- Optimistic approach
- Assumes temporary failure
- Continues making requests
- Can overwhelm failing service

**Use When:**
- Transient failures expected
- Service likely to recover quickly
- Low failure rate
- Can handle retry overhead

### Circuit Breaker Pattern

**What is Circuit Breaker?**
- Stops making requests when failures detected
- Allows service to recover
- Tests recovery before resuming

**Characteristics:**
- Pessimistic approach
- Assumes service is down
- Stops making requests
- Protects failing service

**Use When:**
- Persistent failures possible
- Service may be down for extended period
- High failure rate
- Need to prevent cascading failures

## Combining Both Patterns

**Best Practice:** Use retry for transient failures, circuit breaker for persistent failures.

**Implementation:**
1. **Retry First:** Retry failed request a few times (e.g., 3 retries)
2. **Circuit Breaker:** If retries fail, circuit breaker opens
3. **Fast Failure:** Subsequent requests fail fast without retry
4. **Recovery:** Circuit breaker tests recovery periodically

**Example Flow:**
```
Request → Retry 3 times → All fail → Circuit opens → Fast failure
                                                          ↓
                                                    Recovery test
                                                          ↓
                                                    Service recovered → Circuit closes → Normal operation
```

---

# Real-World Examples

## Netflix Hystrix

**What is Hystrix?**
- Circuit breaker library by Netflix
- Widely used in microservices
- Now in maintenance mode (replaced by Resilience4j)

**Features:**
- Circuit breaker implementation
- Fallback support
- Metrics and monitoring
- Thread pool isolation

**Configuration:**
```java
HystrixCommandProperties.Setter()
    .withCircuitBreakerRequestVolumeThreshold(20)
    .withCircuitBreakerErrorThresholdPercentage(50)
    .withCircuitBreakerSleepWindowInMilliseconds(5000)
```

## Resilience4j

**What is Resilience4j?**
- Modern circuit breaker library
- Replaces Hystrix
- Lightweight and functional

**Features:**
- Circuit breaker
- Retry, rate limiter, bulkhead
- Reactive and functional programming support
- Metrics integration

## Istio Service Mesh

**What is Istio?**
- Service mesh with built-in circuit breaking
- Transparent to application
- Configuration via YAML

**Configuration:**
```yaml
circuitBreaker:
  consecutiveErrors: 5
  interval: 30s
  baseEjectionTime: 30s
  maxEjectionPercent: 50
```

## AWS API Gateway

**What is AWS API Gateway?**
- Managed API gateway with circuit breaking
- Protects backend services
- Automatic failover

**Features:**
- Built-in circuit breaker
- Integration with AWS services
- Automatic scaling
- Health checks

---

# Interview Tips

## Common Questions

**Q: What is the Circuit Breaker pattern?**
- Design pattern that prevents cascading failures in distributed systems
- Monitors service calls and opens circuit when failures exceed threshold
- Stops making requests to failing service, allows it to recover
- Three states: closed (normal), open (failing), half-open (testing recovery)

**Q: What are the three states of a circuit breaker?**
- **Closed:** Normal operation, requests allowed, monitoring failures
- **Open:** Service failing, requests rejected immediately, fast failure
- **Half-Open:** Testing recovery, limited requests allowed, transitions based on results

**Q: How does a circuit breaker detect failures?**
- Monitors request success/failure rates
- Tracks failures in time window
- Compares failure rate with threshold
- Opens circuit when threshold exceeded (e.g., 50% failure rate)

**Q: What is the difference between circuit breaker and retry?**
- **Retry:** Optimistically retries failed requests, assumes temporary failure
- **Circuit Breaker:** Pessimistically stops requests, assumes service is down
- Best practice: Use retry for transient failures, circuit breaker for persistent failures

**Q: How do you implement circuit breaker in a distributed system?**
- Client-side: Implement in client library, each client has own circuit breaker
- Service mesh: Use service mesh (Istio) for transparent circuit breaking
- API Gateway: Implement at gateway level, protects all backend services
- Shared state: Use distributed cache (Redis) for shared circuit breaker state

**Q: What are fallback strategies?**
- Default value: Return cached or default data
- Empty result: Return empty list/null
- Alternative service: Call backup service
- Queue: Queue request for later processing
- Error with context: Return meaningful error message

**Q: How do you configure a circuit breaker?**
- Failure threshold: Percentage or count of failures to trigger open
- Time window: Period to count failures
- Recovery timeout: Time to wait before testing recovery
- Half-open requests: Number of test requests in half-open state
- Success threshold: Condition to close circuit (usually 100% success)

## Key Points to Remember

- **Circuit Breaker** = Prevents cascading failures, fails fast
- **Three States** = Closed (normal), Open (failing), Half-Open (testing)
- **Failure Detection** = Monitor failure rate, compare with threshold
- **Fallback** = Provide alternative response when circuit open
- **Retry vs Circuit Breaker** = Retry for transient, circuit breaker for persistent
- **Configuration** = Threshold, time window, recovery timeout, test requests
- **Use circuit breaker** for resilient distributed systems, prevent cascading failures

---

## Related Topics

- [Architecture Patterns](./Architecture-Patterns.md) - Microservices resilience
- [Message Systems](./Message-Systems.md) - Handling failures in messaging
- [Availability](./Availability.md) - High availability and fault tolerance
- [Load Balancing](./LoadBalancing.md) - Health checks and failover
