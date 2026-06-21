# Q1: Design URL Shortener (Bitly)

---

## Clarifying Questions

Before I start drawing anything, let me ask a few things to make sure I'm solving the right problem.

First — who are the users here? Is this a public service where anyone can shorten a URL, or is it authenticated users only? And do we need analytics, like click counts and geographic breakdown? That changes the architecture significantly.

Second — scale. Are we talking millions of daily users or something smaller? And do we expect read-heavy traffic — people clicking shortened links — or is it more balanced? Typically these systems are extremely read-heavy, maybe 100:1 reads to writes, but I want to confirm.

Third — do we support custom aliases? Like someone wanting `bit.ly/mycompany` instead of a random code? And should URLs expire after some time?

*Assuming: 100M DAU, 10K redirects/sec, 100 writes/sec, public service with analytics, custom aliases optional, expiry configurable.*

---

## Scope

So based on that, here's what I'll design: short URL generation, redirect to original URL, and basic click analytics. I'll skip user auth, billing, and abuse detection — I'll call those external concerns.

Let me do a quick estimate. 100M DAU, assume each user clicks maybe 3 short links a day — that's 300M requests/day, about 3,500 RPS average, maybe 10K at peak. Writes are much lower — maybe 1% of users shorten something, so 1M writes/day, about 12 writes/sec.

Storage: if each URL record is roughly 500 bytes, and we store 1 billion URLs over 5 years, that's about 500 GB — very manageable for a relational DB.

The system is clearly read-heavy. I'll optimize for fast redirects.

---

## High Level Design

```
                        ┌──────────────┐
                        │     CDN      │  ← cache hot redirects at edge
                        └──────┬───────┘
                               │
┌────────┐    HTTPS    ┌───────▼────────┐
│ Client │────────────▶│  API Gateway   │  ← rate limiting, auth (optional)
└────────┘             └───────┬────────┘
                               │
               ┌───────────────┼───────────────┐
               │                               │
       ┌───────▼──────┐               ┌────────▼────────┐
       │  URL Service  │               │  Redirect Service│
       │  (write path) │               │  (read path)     │
       └───────┬───────┘               └────────┬────────┘
               │                                │
               ▼                                ▼
       ┌───────────────┐               ┌────────────────┐
       │   MySQL (RW)  │◀──────────────│  Redis Cache   │
       └───────┬───────┘               └────────────────┘
               │
       ┌───────▼───────┐
       │  MySQL Replica │  ← redirect service reads from here
       └───────────────┘
               │
       ┌───────▼───────┐     ┌─────────────────┐
       │  Kafka Queue  │────▶│ Analytics Worker │──▶ ClickHouse
       └───────────────┘     └─────────────────┘
```

Two separate services: URL Service handles shortening (writes), Redirect Service handles redirection (reads). They scale independently — redirects are 100x more frequent.

---

## Low Level Design

### The Core Algorithm — How to Generate Short Codes

The most interesting part is how you generate a unique 6-character code for each URL.

**Option A — Base62 encoding of auto-increment ID**

Every URL gets a database auto-increment ID. We encode that integer in Base62 (a–z, A–Z, 0–9). ID 1 → "000001", ID 1 billion → "15ftgG". Six characters gives us 62^6 = 56 billion combinations. That's enough for decades.

This is what I'd go with. It's simple, collision-free by design, and reversible.

**Option B — MD5/SHA hash of the long URL**

Hash the long URL, take first 6 characters. Risk of collision — two different URLs could generate the same prefix. You'd need a retry loop with a counter appended. Gets complicated.

**Option C — Pre-generate keys** (KGS — Key Generation Service)

Generate 6-character codes in bulk, store them in a "keys available" table, lock and assign one per request. No collision, fast, but adds operational complexity.

Base62 on auto-increment is the cleanest. Let's go with that.

---

### Data Model

```sql
-- Primary URL store
CREATE TABLE urls (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    short_code  VARCHAR(8)   NOT NULL UNIQUE,   -- indexed, this is the lookup key
    long_url    TEXT         NOT NULL,
    user_id     BIGINT,                          -- null for anonymous
    created_at  DATETIME     NOT NULL DEFAULT NOW(),
    expires_at  DATETIME,                        -- null = never expires
    INDEX idx_short_code (short_code)            -- critical — every redirect hits this
);

-- Click analytics (write-heavy, kept separate)
CREATE TABLE clicks (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    url_id      BIGINT       NOT NULL,
    clicked_at  DATETIME     NOT NULL,
    country     VARCHAR(2),
    referrer    VARCHAR(500),
    INDEX idx_url_id (url_id)                    -- queries like "how many clicks for URL X"
);
```

---

### API Design

```
POST /v1/urls
  Headers: Authorization: Bearer <token>  (optional)
  Body:    { "url": "https://example.com/very-long-path",
             "custom_alias": "mylink",        // optional
             "expires_in": 86400 }            // seconds, optional
  Response 201: { "short_url": "https://bit.ly/aB3xZ9",
                  "expires_at": "2026-07-01T00:00:00Z" }
  Response 409: { "error": "alias already taken" }
  Response 400: { "error": "invalid URL" }

GET /{code}
  Response 302: Location: https://original-long-url.com/path
  Response 404: URL not found
  Response 410: URL expired

GET /v1/urls/{code}/stats
  Response 200: { "clicks": 4821, "unique_countries": 12, "top_referrer": "twitter.com" }
```

---

### Redirect Flow — Step by Step

When someone hits `bit.ly/aB3xZ9`:

1. Request hits CDN — if this short code was recently popular, CDN returns the redirect immediately without touching our servers.
2. Cache miss → hits Redirect Service → checks Redis. Key: `url:aB3xZ9` → Value: the long URL.
3. Cache miss → queries MySQL read replica: `SELECT long_url, expires_at FROM urls WHERE short_code = 'aB3xZ9'`
4. If expired → 410 Gone. If found → return 302, write to Redis with TTL.
5. Asynchronously publish click event to Kafka. Analytics worker picks it up, writes to ClickHouse. This is fire-and-forget — we don't block the redirect on analytics.

**301 vs 302 — a decision the interviewer will definitely ask about:**

301 is a permanent redirect. The browser caches it permanently and never hits our server again for that link. That's great for performance but kills analytics — we lose click data after the first request.

302 is temporary. Every click goes through our server. We get full analytics but bear all the traffic. For a system like Bitly where analytics is a paid feature, 302 is the right call.

---

## Scale — What Breaks at 10x?

If traffic goes from 10K to 100K RPS, here's what breaks and how to fix it:

**Redis becomes the bottleneck first.** Single Redis node handles maybe 100K ops/sec, but adding serialization and network it's realistically 50–60K. Solution: Redis Cluster — shard by `short_code`, consistent hashing ensures the same code always routes to the same shard.

**MySQL read replicas.** The redirect query `WHERE short_code = ?` with an index is extremely fast — sub-millisecond. But at 100K RPS you'll need 5–10 read replicas behind a read balancer. The short_code index is the critical piece here.

**Hot URLs.** If a short link goes viral — imagine a tweet with 10M impressions — all traffic floods one URL. Cache solves this but even Redis can get hammered. Push the hottest URLs to CDN edge with a longer TTL. Those redirects never touch our origin.

**Write scaling.** At 1,000 writes/sec (10x current), MySQL can handle it, but we'd move URL creation to async — accept the request, push to Kafka, return the short code immediately, persist asynchronously. This makes creation feel instant and decouples the DB write from the user response.

**Analytics.** ClickHouse handles billions of rows easily. The Kafka queue is the buffer — even if Analytics Workers fall behind, clicks are queued and nothing is lost.

---

## Trade-offs

**SQL vs NoSQL here:** I chose MySQL because short codes are fixed-length, schema is clear, and we need ACID for uniqueness constraints. If we were at Twitter-scale with multi-region writes, we'd consider DynamoDB — but that introduces eventual consistency for code uniqueness, which requires extra coordination. Not worth it at this scale.

**Sync vs Async for analytics:** Analytics write is async via Kafka. If Kafka is down, we lose some click data. This is acceptable — analytics being slightly off is far less bad than a redirect failing. If we needed perfect analytics, we'd use a synchronous write with a database transaction, but that adds latency to every redirect.

**Caching trade-off:** If we cache aggressively with long TTLs and a URL owner deletes their link, old cached entries still redirect for the TTL duration. We handle this with explicit cache invalidation on delete — publish a `url.deleted` event, consumers evict from Redis. CDN is harder — we'd need to call CDN purge API, which takes a few seconds.

---

## Cross-Questions

**How do you prevent someone from shortening malicious URLs?**

Two layers. At creation time, check the URL against a blocklist of known phishing/malware domains — Google Safe Browsing API is a standard choice. At redirect time, show an interstitial page for new or suspicious URLs ("you're leaving our site"). For scale, maintain a Redis Set of blocked domains — O(1) lookup at write time.

**How would you shard the database if you had 100 billion URLs?**

Shard by `short_code`. Consistent hashing: hash the short code, map to a shard. The redirect service uses the same hash to route to the right shard — no coordination needed. The tricky part is rebalancing when adding shards — consistent hashing minimizes data movement. The auto-increment ID approach breaks with sharding because two shards would generate the same IDs. Switch to a distributed ID generator like Twitter Snowflake — 64-bit IDs with machine ID + timestamp + sequence.

**How do custom aliases work without conflicts?**

Custom aliases go through the same `urls` table with a `UNIQUE` constraint on `short_code`. If someone requests `mylink` and it exists, we return 409 Conflict. The tricky case is a custom alias that collides with a system-generated code. Separate the namespace: system codes always start with a digit, custom aliases must start with a letter. Or maintain a separate `custom_aliases` table with a lookup before generation.

**What happens if your URL service goes down during creation?**

The user gets an error and can retry. We make creation idempotent: hash the long URL, and if the same URL was already shortened by the same user, return the existing short code instead of creating a duplicate. Store a `url_hash` column with an index. If the service is fully down, the client retries with exponential backoff. URLs are eventually created when the service recovers — creation is not in the critical path of reads.

**Why not just use a hash of the long URL as the short code?**

You'd have collisions — two different URLs could produce the same 6-character prefix of their MD5. You'd need to detect collisions and append a counter, turning O(1) generation into a retry loop. Also, hashing gives no ordering or predictability. Auto-increment gives you a natural audit trail — code "000001" was the first URL shortened. Clean, simple, no collision by design.
