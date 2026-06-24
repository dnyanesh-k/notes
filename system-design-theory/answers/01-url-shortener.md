# Q1: Design URL Shortener (Bitly)

---

## How to Approach This in an Interview

Before drawing anything, always ask clarifying questions. This shows you don't jump to solutions before understanding the problem — which is exactly what senior engineers do.

---

## Clarifying Questions

**1. Who are the users and what's the core use case?**

"Is this a public service like Bitly where anyone pastes a long URL and gets a short one? Or is it internal — like a company's internal link shortener for employees?"

*Why this matters:* Public service → anonymous access, abuse potential, needs rate limiting. Internal → authentication is already handled, much simpler.

**2. Do we need analytics?**

"When someone clicks a short link, do we need to track that? Things like click count, country, referrer (did the click come from Twitter or email)?"

*Why this matters:* Analytics means every redirect must pass through our servers — we can't let browsers cache the redirect permanently. Also adds an entire analytics pipeline to the design.

**3. What's the expected scale?**

"Are we talking 100 million users or 1 million? And is traffic read-heavy — more people clicking links than creating them?"

*Why this matters:* URL shorteners are typically 100:1 read-to-write ratio. That means we optimize for fast reads (redirects), not writes (creating short URLs).

**4. Custom aliases and expiry?**

"Can users pick their own alias like `bit.ly/mycompany`? And should URLs expire after some time?"

*Why this matters:* Custom aliases require conflict detection. Expiry means we need to check expiry time on every redirect.

### Assumptions (state these out loud)

```
- 100M DAU
- 10K redirects/sec at peak (read path)
- ~100 writes/sec (creating short URLs)
- Analytics: yes (click count, country, referrer)
- Custom aliases: yes (optional per user)
- Expiry: configurable (default: never)
- Public service, auth optional
```

---

## Back-of-Envelope Math

Always do this before drawing. It tells you what to optimize for.

```
DAU:            100M users
Clicks/day:     Each user clicks ~3 short links/day
                = 300M requests/day
                = 300M / 86400 seconds
                = ~3,500 RPS average
Peak:           ~3x average = 10,000 RPS

Writes/day:     1% of users shorten a URL
                = 1M new URLs/day
                = ~12 writes/sec
                (writes are tiny compared to reads)

Read:Write ratio = 10,000 : 12 ≈ 833:1
This is extremely read-heavy. Design everything around fast reads.

Storage:
  Each URL record ≈ 500 bytes (short_code + long_url + metadata)
  1M new URLs/day × 365 days × 5 years = 1.8 billion URLs
  1.8B × 500 bytes = ~900 GB over 5 years
  Easily fits in a single relational DB with proper indexing.
```

Key conclusion: **This is a read-heavy system. Optimize the redirect path above everything else.**

---

## High Level Design

```
                        ┌──────────────┐
                        │     CDN      │  ← caches hot redirects at the edge,
                        └──────┬───────┘    requests never reach our servers
                               │
┌────────┐    HTTPS    ┌───────▼────────┐
│ Client │────────────▶│  API Gateway   │  ← rate limiting, auth check, SSL termination
└────────┘             └───────┬────────┘
                               │
               ┌───────────────┼───────────────┐
               │                               │
       ┌───────▼──────┐               ┌────────▼────────┐
       │  URL Service  │               │ Redirect Service │
       │  (write path) │               │  (read path)     │
       └───────┬───────┘               └────────┬────────┘
               │                                │
               ▼                                ▼
       ┌───────────────┐               ┌────────────────┐
       │  MySQL (RW)   │               │  Redis Cache   │
       │  primary      │               │  (L1 lookup)   │
       └───────┬───────┘               └────────┬───────┘
               │                                │ cache miss
       ┌───────▼────────┐                       ▼
       │  MySQL Replica │◀──────────────── DB lookup
       │  (read-only)   │
       └───────┬────────┘
               │ async (fire and forget)
       ┌───────▼───────┐     ┌─────────────────┐
       │  Kafka Queue  │────▶│ Analytics Worker │──▶ ClickHouse
       └───────────────┘     └─────────────────┘
```

**Why two separate services (URL Service and Redirect Service)?**

They have completely different load profiles:
- Redirect Service: 10,000 RPS, stateless, needs to scale horizontally
- URL Service: 12 RPS, does DB writes, much less load

If you combine them, you'd have to scale both together even though only the redirect path needs scaling. Separating them lets you run 50 Redirect Service instances and 2 URL Service instances. Independent scaling = cost efficiency.

**Why CDN?**

A CDN (Content Delivery Network) is a globally distributed cache. When `bit.ly/aB3xZ9` is a popular link (imagine a viral tweet), the CDN node nearest to the user returns the redirect without your servers being touched at all. This handles sudden traffic spikes automatically.

---

## Low Level Design

### Part 1: The Core Algorithm — How to Generate Short Codes

This is the most interesting part and interviewers love asking about it in depth.

**What is Base62 encoding?**

Base62 uses 62 characters: `a-z` (26) + `A-Z` (26) + `0-9` (10) = 62 total.
It's exactly like how we convert numbers from base 10 (decimal) to base 16 (hex), but here we use 62 as the base.

Why 62 and not 64 (like Base64)? Base64 includes `+` and `/` which are special characters in URLs and need to be percent-encoded. Base62 is URL-safe by design.

**Why does 6 characters give us 56 billion combinations?**

```
With 6 character positions and 62 choices per position:
62^6 = 62 × 62 × 62 × 62 × 62 × 62 = 56,800,235,584 ≈ 56 billion

At our rate of 1M new URLs/day:
56 billion / 1M = 56,000 days ≈ 153 years before we exhaust all codes

7 characters gives 62^7 = 3.5 trillion combinations — complete overkill.
6 is the sweet spot: short enough for the URL, large enough capacity.
```

**Option A — Base62 encoding of auto-increment ID (recommended)**

Every row in the database gets a `BIGINT AUTO_INCREMENT` primary key. When URL #1000000 is created, we encode the integer `1000000` into Base62.

Here is the actual algorithm:

```python
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
# index:   0                         25 26                        51 52      61

def encode_base62(num: int) -> str:
    """Convert an integer to a Base62 string."""
    if num == 0:
        return ALPHABET[0]
    
    result = []
    while num > 0:
        remainder = num % 62       # get the rightmost "digit" in base62
        result.append(ALPHABET[remainder])
        num = num // 62            # shift right by one base62 "digit"
    
    return ''.join(reversed(result))  # we built it right-to-left, so reverse

def decode_base62(code: str) -> int:
    """Convert a Base62 string back to an integer."""
    num = 0
    for char in code:
        num = num * 62 + ALPHABET.index(char)
    return num
```

**Worked example — let's encode ID = 1,000,000:**

```
Step 1: 1000000 % 62 = 40  → ALPHABET[40] = 'O'   (capital O)
        1000000 // 62 = 16129

Step 2: 16129 % 62 = 5     → ALPHABET[5]  = 'f'
        16129 // 62 = 260

Step 3: 260 % 62 = 10      → ALPHABET[10] = 'k'
        260 // 62 = 4

Step 4: 4 % 62 = 4         → ALPHABET[4]  = 'e'
        4 // 62 = 0  ← stop

Built right-to-left: ['O', 'f', 'k', 'e'] → reversed → "ekfO"

So ID 1,000,000 → short code "ekfO" (4 chars)
ID 56,800,235,583 → short code "zzzzzz" (6 chars, the maximum)
```

**Why is this collision-free by design?**

Because auto-increment IDs are unique by definition. The DB guarantees no two rows get the same ID. Since encoding is deterministic, unique ID → unique code. No collision is possible — there's no need to check if the code already exists.

**Why is it reversible?**

You can run `decode_base62("ekfO")` and get back `1000000`. This means you don't even need to store the `short_code` in the database — you can derive it from the ID. But we store it anyway for fast lookup.

> **Feistel Cipher (Format-Preserving Encryption)** : This method is highly recommended because it keeps your database efficient while making the output look completely random. You still use your normal auto-incrementing IDs, but you scramble them mathematically before encoding them to Base62
---

**Option B — MD5/SHA hash of the long URL (don't use this)**

```python
import hashlib
def hash_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()[:6]

# "https://example.com" → "d41d8c" (first 6 chars of MD5 hash)
```

**Why this breaks:**

Two different URLs could produce the same 6-character prefix. This is called a hash collision.

```
URL A: "https://site-a.com/page1" → MD5 → "d41d8c..."
URL B: "https://site-b.com/page2" → MD5 → "d41d8c..."  ← same prefix!
```

When this happens you need a retry loop:
```python
attempt = 0
while True:
    code = hash_url(url + str(attempt))[:6]
    if not db.exists(code):
        break
    attempt += 1  # keep trying with modified input
```

This turns O(1) code generation into O(n) retries, and as the DB fills up, collisions become more frequent. Avoid this.

---

**Option C — KGS (Key Generation Service)**

Pre-generate millions of 6-character codes, store them in a `keys` table with status `available`/`used`. When a URL is created, fetch one key, mark it `used`.

```sql
CREATE TABLE keys (
    code    VARCHAR(6) PRIMARY KEY,
    status  ENUM('available', 'used') DEFAULT 'available'
);
```

```
Pros:
- Zero collision guarantee
- Code generation is just a table lookup, very fast
- Can pre-fetch a batch into memory to avoid DB round-trip per request

Cons:
- Operational complexity: need to generate keys in advance
- Single point of failure (the KGS itself)
- Concurrent requests could race to claim the same key — need DB-level locking
  (SELECT ... FOR UPDATE or atomic compare-and-swap)
```

**Winner: Base62 on auto-increment** — simplest, collision-free, no extra service needed.

---

### Part 2: The Write Path — What Happens When You Create a Short URL

When user calls `POST /v1/urls` with a long URL:

```
Step 1: API Gateway receives request
        - Checks rate limit (e.g. 10 URLs/min per IP using Redis counter)
        - Validates JWT if user is logged in
        - Forwards to URL Service

Step 2: URL Service validates the input
        - Is it a valid URL format? (regex check)
        - Is the domain blocked? (check Redis blocklist Set)
        - If custom alias: does it already exist? (check DB)

Step 3: Check for deduplication (idempotency)
        - If same user already shortened this exact URL, return existing code
        - How? Store a url_hash column (MD5 of long_url) with an index
        - Query: SELECT short_code FROM urls WHERE url_hash = ? AND user_id = ?
        - If found, return it — don't create a duplicate

Step 4: Insert into DB
        INSERT INTO urls (long_url, user_id, url_hash, expires_at)
        VALUES (?, ?, MD5(?), ?)
        -- MySQL returns the auto-increment ID, say id = 1000000

Step 5: Generate short code
        short_code = encode_base62(1000000)  # → "ekfO"
        UPDATE urls SET short_code = 'ekfO' WHERE id = 1000000

        (Alternatively: insert with short_code computed before insert using
         a two-step transaction, but the above is simpler)

Step 6: Return to user
        {
          "short_url": "https://bit.ly/ekfO",
          "expires_at": null
        }
```

**Total latency:** ~5-10ms (one DB write + one DB update, both indexed, same transaction).

---

### Part 3: The Data Model

```sql
-- Primary URL store
CREATE TABLE urls (
    id          BIGINT          PRIMARY KEY AUTO_INCREMENT,
    -- AUTO_INCREMENT: DB assigns this, guaranteed unique, never reused.
    -- BIGINT: supports up to 9.2 × 10^18 — we'll never run out.

    short_code  VARCHAR(8)      NOT NULL UNIQUE,
    -- VARCHAR(8): 6 chars for generated codes, up to 8 for custom aliases.
    -- UNIQUE constraint: DB enforces no two rows have same short_code.
    -- This is our primary lookup key on every redirect.

    long_url    TEXT            NOT NULL,
    -- TEXT: long URLs can be thousands of characters (query params, tokens).
    -- We don't index this — it's only read, never searched.

    url_hash    CHAR(32)        NOT NULL,
    -- MD5 hash of long_url, stored for deduplication checks.
    -- CHAR(32): MD5 is always exactly 32 hex characters.

    user_id     BIGINT,
    -- NULL for anonymous users. FK to users table if auth exists.

    created_at  DATETIME        NOT NULL DEFAULT NOW(),
    expires_at  DATETIME,
    -- NULL means never expires. Checked on every redirect.

    INDEX idx_short_code (short_code),
    -- B-tree index. Every redirect does: WHERE short_code = 'ekfO'
    -- Without this index: full table scan = O(n) = death at 1B rows.
    -- With this index: B-tree lookup = O(log n) ≈ 30 comparisons for 1B rows.

    INDEX idx_url_hash_user (url_hash, user_id)
    -- For deduplication check: "has this user already shortened this URL?"
    -- Composite index: (hash, user_id) together because we always query both.
);

-- Click analytics — kept separate from urls table intentionally
CREATE TABLE clicks (
    id          BIGINT          PRIMARY KEY AUTO_INCREMENT,
    url_id      BIGINT          NOT NULL,   -- FK to urls.id
    clicked_at  DATETIME        NOT NULL,
    country     CHAR(2),                   -- "IN", "US", "GB" etc. ISO 3166
    referrer    VARCHAR(500),              -- "twitter.com", "gmail.com", null

    INDEX idx_url_id (url_id)
    -- For queries like "how many clicks for URL X over last 7 days?"
);
```

**Why is the analytics table separate?**

`clicks` is written on every redirect — that's 10K writes/sec. If this was in the `urls` table, every redirect would be updating the same row (the URL's click count), causing row-level locking contention. Separate table = no contention on the `urls` table which is only read during redirects.

**What is a B-tree index and why does it matter?**

When you add `INDEX idx_short_code (short_code)`, MySQL creates a B-tree — a sorted tree structure where each node holds a range of `short_code` values and pointers to the next level.

```
Finding "ekfO" in a B-tree with 1 billion rows:
- Each comparison splits the search space in half
- log2(1,000,000,000) ≈ 30 comparisons
- Each comparison is a memory read (index fits in RAM): ~1 nanosecond
- Total lookup: ~30ns to ~1ms (including disk I/O if index partially on disk)

Without index (full table scan):
- Read every row until we find it: up to 1 billion comparisons
- At 10K redirects/sec: this would collapse the DB in seconds
```

The index is not optional — it is the entire reason the system works at scale.

---

### Part 4: The Redirect Flow — Step by Step

When someone clicks `https://bit.ly/ekfO` in their browser:

```
Step 1: Browser sends HTTP GET request to bit.ly/ekfO
        → DNS resolves bit.ly → CDN IP (Cloudflare/Fastly edge node)

Step 2: CDN checks its cache
        Key: "ekfO"
        If HIT (popular URL): CDN returns 302 redirect instantly.
                               Request NEVER reaches our servers.
        If MISS: CDN forwards request to our API Gateway.

Step 3: API Gateway → Redirect Service

Step 4: Redirect Service checks Redis
        Command: GET url:ekfO
        If HIT: Redis returns the long URL in <1ms.
                Return HTTP 302 with Location: <long_url>
                (Also asynchronously publish click event to Kafka)
        If MISS: go to Step 5.

Step 5: Query MySQL read replica
        SELECT long_url, expires_at FROM urls WHERE short_code = 'ekfO'
        -- B-tree index lookup: ~1ms

        If not found → return 404
        If found but expires_at < NOW() → return 410 Gone
        If found and valid:
           - Write to Redis: SET url:ekfO <long_url> EX 3600  (1 hour TTL)
           - Return HTTP 302 Location: <long_url>

Step 6: Asynchronously (non-blocking) publish to Kafka:
        {
          "url_id": 1000000,
          "clicked_at": "2026-06-22T10:30:00Z",
          "country": "IN",
          "referrer": "t.co"
        }
        Analytics Worker consumes this and writes to ClickHouse.
        The redirect does NOT wait for this — it's fire-and-forget.
```

**Total latency on Redis HIT:** ~2-3ms (network + Redis lookup)
**Total latency on DB hit:** ~10-15ms (network + Redis miss + DB query + Redis write)

---

### Part 5: Redis — What It Is, How We Use It, and Edge Cases

**What is Redis?**

Redis is an in-memory key-value store. "In-memory" means all data lives in RAM — not on disk. RAM access is ~100x faster than SSD. This is why Redis can handle 100,000+ operations/second on a single node.

**Data structure we use: String**

```
Redis key:   "url:ekfO"         (namespace prefix + short code)
Redis value: "https://example.com/very/long/path?param=123"
TTL:         3600 seconds (1 hour)

Commands:
SET url:ekfO "https://example.com/..." EX 3600   ← write with TTL
GET url:ekfO                                       ← read
DEL url:ekfO                                       ← delete (on URL deletion)
```

**Why TTL?**

If we cache forever, deleted or expired URLs would still redirect from cache. TTL is our safety net: even without explicit deletion, stale cache entries expire automatically within 1 hour.

**The Cache Stampede Problem (important edge case)**

Imagine "ekfO" is a viral URL with 50,000 RPS. Its Redis TTL expires at exactly 12:00:00.000.

At 12:00:00.001, all 50,000 requests simultaneously find a cache miss and all 50,000 rush to query MySQL. MySQL gets 50,000 concurrent reads for the same row. This can overwhelm MySQL.

This is called a **cache stampede** (or thundering herd).

**Solution 1: Mutex lock (correct but adds latency)**

```python
def get_url(short_code):
    long_url = redis.get(f"url:{short_code}")
    if long_url:
        return long_url

    # Cache miss — use a distributed lock so only ONE request goes to DB
    lock_key = f"lock:{short_code}"
    if redis.set(lock_key, "1", nx=True, ex=5):  # nx=True: only set if not exists
        # This request won the lock — go to DB
        long_url = db.query(short_code)
        redis.set(f"url:{short_code}", long_url, ex=3600)
        redis.delete(lock_key)
        return long_url
    else:
        # Another request is fetching — wait briefly and retry from cache
        time.sleep(0.05)
        return redis.get(f"url:{short_code}")
```

**Solution 2: Probabilistic early expiry (elegant)**

Don't wait for TTL to expire. Proactively refresh the cache slightly before it expires, with some randomness so not all instances refresh at the same time.

```python
def get_url_with_early_refresh(short_code):
    value, ttl = redis.get_with_ttl(f"url:{short_code}")
    if value and ttl > 30:  # more than 30 seconds left: safe, use cache
        return value
    if value and ttl <= 30:  # expiring soon: 10% chance any instance refreshes early
        if random.random() < 0.1:
            long_url = db.query(short_code)
            redis.set(f"url:{short_code}", long_url, ex=3600)
            return long_url
        return value
    # Full miss: go to DB
    ...
```

For our scale, Solution 1 is simpler and sufficient.

---

### Part 6: 301 vs 302 — Deep Explanation

This is a classic interview question. You need to understand what actually happens at the HTTP level.

**What is an HTTP redirect?**

When your server returns a 3xx response, it includes a `Location` header with the destination URL. The browser sees this and automatically makes a new GET request to that URL.

```
Browser → GET bit.ly/ekfO
Server  → HTTP/1.1 302 Found
           Location: https://example.com/very-long-path
Browser → GET https://example.com/very-long-path  (follows redirect)
```

**301 Moved Permanently**

- The browser caches this redirect permanently (no expiry unless you set `Cache-Control`).
- Next time the user or anyone on that machine clicks the same link, the browser redirects locally without sending ANY request to our servers.
- **Pro:** Massive performance win. Zero server load after first click.
- **Con:** We never see the subsequent clicks. Analytics are broken after the first request. Also, if the URL changes, users with cached 301 will still go to the old destination — they need to clear browser cache to fix it.

**302 Found (Temporary Redirect)**

- The browser does NOT cache this redirect.
- Every click hits our servers.
- **Pro:** We see every click → full analytics.
- **Con:** We bear all the traffic. Every user, every device, every click = a server request.

**Which to use?**

For Bitly, analytics is a paid feature — it's the business model. Use 302. Without analytics data, the product has no value to paying customers.

If you built a personal redirect service with no analytics needs, 301 would be more efficient.

---

### Part 7: API Design

```
POST /v1/urls
  Purpose: Create a new short URL
  Headers: Authorization: Bearer <token>  (optional for anonymous use)
  Body:
    {
      "url": "https://example.com/very-long-path",
      "custom_alias": "mycompany",   // optional — user-chosen code
      "expires_in": 86400            // optional — seconds until expiry
    }
  
  Response 201 Created:
    { "short_url": "https://bit.ly/ekfO", "expires_at": "2026-06-23T10:30:00Z" }
  
  Response 409 Conflict:
    { "error": "alias 'mycompany' is already taken" }
    -- When custom_alias collides with existing code
  
  Response 400 Bad Request:
    { "error": "invalid URL format" }
    { "error": "URL domain is blocked" }
  
  Response 429 Too Many Requests:
    { "error": "rate limit exceeded" }

---

GET /{code}
  Purpose: Redirect to original URL
  No body, no auth needed — this is the public endpoint.
  
  Response 302 Found:
    Location: https://original-long-url.com/path
    -- Browser follows this automatically
  
  Response 404 Not Found:
    -- short_code doesn't exist in DB
  
  Response 410 Gone:
    -- URL existed but has expired (expires_at is in the past)
    -- 410 is better than 404 here: 404 = never existed, 410 = existed but gone

---

GET /v1/urls/{code}/stats
  Purpose: Get click analytics for a URL (auth required — only URL owner)
  
  Response 200:
    {
      "short_code": "ekfO",
      "total_clicks": 4821,
      "unique_countries": 12,
      "top_referrer": "twitter.com",
      "clicks_by_day": [
        { "date": "2026-06-22", "count": 1241 },
        ...
      ]
    }
```

---

## Scale — What Breaks at 10x and How to Fix It

Current load: 10K RPS reads, 100 RPS writes.
10x scenario: 100K RPS reads, 1K RPS writes.

**1. Redis — first bottleneck**

A single Redis node handles ~100K simple operations/sec in theory, but realistically ~50-60K under real network conditions. At 100K RPS this becomes the bottleneck.

**Fix: Redis Cluster**

Redis Cluster shards data across multiple nodes using consistent hashing (explained below). Each node owns a range of "slots" (there are 16,384 total slots). The short_code is hashed to determine which slot, and therefore which node, stores it.

```
Short code "ekfO" → hash → slot 9821 → Node 2
Short code "xYz1" → hash → slot 3421 → Node 0
```

Every Redirect Service instance knows the cluster topology and routes directly to the correct Redis node. No extra hop needed.

**2. MySQL read replicas — second bottleneck**

At 100K RPS with a 90% Redis cache hit rate, ~10K requests/sec still hit the DB. A single MySQL instance handles ~5-10K simple indexed reads/sec.

**Fix: Read replicas**

MySQL supports replication: every write to the primary is asynchronously replicated to read replicas. The Redirect Service reads from replicas (load balanced across them), writes only go to primary.

```
Writes (URL creation): → MySQL Primary
Reads (redirect lookup): → Read Load Balancer → [Replica 1, Replica 2, Replica 3...]
```

At 100K RPS with 90% cache hit, you'd need ~5 replicas each handling 2K reads/sec. Very manageable.

**Important note on replication lag:** Replicas are slightly behind the primary (usually <1ms on same datacenter). This means a URL created 1ms ago might not be visible on the replica yet. For URL shorteners this is fine — if a new URL isn't immediately clickable for 1ms, nobody notices.

**3. Hot URL problem (cache warming)**

Scenario: A celebrity tweets a short link with 10M followers. In 5 seconds, 2M people click it. Even Redis starts struggling with 400K RPS for that single key.

**Fix: CDN edge caching**

For URLs that are clearly viral (high click rate in a short window), push them to CDN edge nodes with a longer TTL (30 minutes). CDN nodes worldwide absorb the traffic — requests never reach our Redis or servers.

Detection: Analytics worker tracks clicks/min per URL. If it exceeds a threshold (say 1000 clicks/min), trigger a CDN cache warm for that URL.

**4. Write scaling**

At 1K writes/sec, MySQL handles it fine (writes are much cheaper in quantity). But if it went to 10K writes/sec:

**Fix: Async creation**

Accept the request → immediately return the short code (computed from a pre-allocated ID) → push the actual DB write to a Kafka queue → worker persists it asynchronously.

The user sees the short URL instantly. The DB write happens in the background within milliseconds. This decouples user latency from DB write latency.

**5. Analytics scaling**

ClickHouse is a columnar OLAP database designed for analytical queries on billions of rows. It ingests data from Kafka workers and supports queries like:

```sql
SELECT toDate(clicked_at) as day, count(*) as clicks
FROM clicks
WHERE url_id = 1000000
  AND clicked_at >= now() - INTERVAL 30 DAY
GROUP BY day
ORDER BY day
```

This query on 10 billion rows runs in ~2 seconds on ClickHouse. The same query on MySQL would take minutes or time out.

---

## What is Consistent Hashing? (Interviewers ask this)

Regular hashing: `node = hash(key) % N` where N = number of nodes.

**Problem:** If you add a new node (N goes from 3 to 4), almost every key remaps to a different node. This means you have to move most of your data — catastrophic for a live system.

**Consistent hashing:** Imagine a circle (ring) with positions 0 to 360 degrees. Each node is placed at a random position on the ring. Each key is also hashed to a position on the ring. A key is assigned to the **first node clockwise from the key's position**.

```
Ring positions:
  Node A at 60°
  Node B at 180°
  Node C at 300°

Key "ekfO" hashes to 90°  → first node clockwise = Node B (at 180°)
Key "xYz1" hashes to 220° → first node clockwise = Node C (at 300°)
Key "ab12" hashes to 320° → first node clockwise = Node A (wraps around, at 60°)
```

**When you add Node D at 240°:**

Only keys between 180° and 240° need to move (from Node C to Node D). Everything else stays. On average, only `1/N` of keys are remapped when a node is added. This minimizes data movement.

This is how Redis Cluster manages sharding without massive reshuffling when you scale out.

---

## Trade-offs (be ready to justify choices)

**Why MySQL and not DynamoDB/Cassandra?**

Our data model is relational with clear schema: `urls` table, `clicks` table, foreign key. Schema is fixed. We need ACID guarantees for uniqueness — two simultaneous requests for the same custom alias must not both succeed. MySQL's transactions handle this cleanly.

DynamoDB would give us multi-region active-active writes (eventual consistency) but we'd lose ACID. For short code uniqueness, eventual consistency means two different URLs could temporarily get the same code, requiring conflict resolution. Not worth the complexity at our scale.

DynamoDB makes sense at Twitter/Meta scale where global multi-region writes are necessary. For 100M DAU, MySQL + replicas is perfectly adequate.

**Why Kafka for analytics and not direct DB writes?**

At 10K RPS, if every redirect synchronously wrote a click record to MySQL, that's 10K writes/sec to the `clicks` table. MySQL can handle this but it adds ~5ms to every redirect (the round trip to write the click). Over millions of users, this compounds.

Kafka lets us fire-and-forget: publish a click event (microseconds), return the redirect, and let a background worker batch-write clicks to ClickHouse at its own pace. The redirect is fast regardless of analytics write speed.

The trade-off: if Kafka goes down, we lose click data during that window. For analytics, this is acceptable. For financial transactions, it wouldn't be.

**Why separate Redis cache and CDN?**

Redis is closest to our application servers — fastest for cache lookups, updatable immediately when URLs change. CDN is closest to users globally — fastest for reducing network hops worldwide, but slower to update (invalidation takes seconds).

Two-tier caching:
- CDN: absorbs global traffic for hot popular URLs (no server load at all)
- Redis: handles everything else with sub-millisecond lookups

---

## Cross-Questions

**Q: How do you handle malicious URLs?**

Two-layer defense:

Layer 1 — At creation time:
- Validate URL format (regex)
- Check domain against a Redis Set of known malicious domains (O(1) lookup)
- Optionally call Google Safe Browsing API for deep inspection (async, don't block on this for latency)
- If flagged: reject with 400 and log for review

Layer 2 — At redirect time:
- Check again against blocklist (Redis Set lookup is ~0.1ms, negligible)
- Show an interstitial page for suspicious URLs ("Warning: you're about to leave our site")
- Rate limit by IP to prevent automated abuse

**Q: How would you shard the database at 100 billion URLs?**

At 100 billion URLs, the `urls` table is ~50 TB. This doesn't fit on a single MySQL server.

Solution: Shard by `short_code` using consistent hashing.

```
short_code "ekfO" → hash → maps to Shard 2
Redirect Service knows: "ekfO" → Shard 2 → query that DB server
```

Problem with auto-increment at this point: two shards would both generate IDs starting at 1, 2, 3... and collide. 

Fix: Switch from MySQL auto-increment to **Twitter Snowflake IDs**:

```
Snowflake ID (64-bit integer):
  [41 bits: timestamp in ms] [10 bits: machine ID] [12 bits: sequence number]

- Timestamp: milliseconds since Jan 1, 2010 (gives ~69 years of capacity)
- Machine ID: uniquely identifies which Snowflake generator instance
- Sequence: 4096 IDs per millisecond per machine

Two different DB shards generate:
  Shard 1 machine ID = 001: ID = 1234567890_001_0001
  Shard 2 machine ID = 002: ID = 1234567890_002_0001
  These are different integers → no collision → Base62 encode uniquely
```

**Q: How do custom aliases avoid colliding with auto-generated codes?**

Namespace separation:
- Auto-generated codes: always start with a **lowercase letter** (e.g., `ekfO`, `aBc3`)
- Custom aliases: must start with an **uppercase letter** (enforced by validation on the API)

This means the two namespaces never overlap. Alternatively, maintain a separate `custom_aliases` table and check both tables before generation, but namespace separation is simpler and O(1).

**Q: What if a URL is deleted but it's cached in CDN/Redis?**

When URL owner calls `DELETE /v1/urls/ekfO`:

1. Soft-delete in DB: `UPDATE urls SET deleted_at = NOW() WHERE short_code = 'ekfO'`
2. Evict from Redis: `DEL url:ekfO` (instant)
3. Purge from CDN: call CDN purge API (takes 5-10 seconds to propagate globally)
4. Publish `url.deleted` event to Kafka so any other consumers (analytics workers etc.) can clean up

During the 5-10 second CDN propagation window, the deleted URL might still redirect from CDN edge caches. This is accepted: the SLA for deletion is "within 60 seconds", not instant.

**Q: What happens if two users simultaneously try to create the same custom alias?**

Both send `POST /v1/urls` with `custom_alias: "mylink"`.

Both reach the URL Service, both check the DB and find "mylink" doesn't exist (race condition), both try to insert.

MySQL's `UNIQUE` constraint on `short_code` saves us:
- First insert: succeeds (201 Created)
- Second insert: fails with `Duplicate entry 'mylink' for key 'short_code'`
- URL Service catches this DB error, returns 409 Conflict to the second user

This is the correct behavior. The UNIQUE constraint is the last line of defense — application-level checks are an optimization to give a better error message early, but the DB enforces correctness.

**Q: What if the URL Service crashes mid-creation?**

The user gets a 500 error (or timeout). They'll retry.

To prevent duplicates on retry, we use idempotency via `url_hash`:

```sql
-- On creation, store MD5 of the long URL
INSERT INTO urls (long_url, url_hash, user_id, ...)
VALUES (?, MD5(?), ?, ...)

-- On retry, check first:
SELECT short_code FROM urls 
WHERE url_hash = MD5(?) AND user_id = ?

-- If found: return existing short_url (don't create duplicate)
-- If not found: proceed with new creation
```

This makes the create endpoint **idempotent** — calling it multiple times with the same URL produces the same result.
