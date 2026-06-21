# Q5: Design News Feed (Twitter/LinkedIn)

---

## Clarifying Questions

A few things I want to nail down first. Is this a follower-based feed — you see posts from people you follow — or an algorithmic feed with ranking and recommendations? Algorithmic feeds are significantly more complex; I'll design the infrastructure and mention where ML ranking plugs in.

What's the scale — how many users, and what's the ratio of readers to writers? Social networks are typically heavily read-skewed — maybe 10:1 or even 100:1. That shapes everything.

Is there a celebrity problem? If someone has 50 million followers and posts something, do we push that to all 50 million feeds at once? This is the hardest problem in feed design.

Do we need real-time or is a few seconds of delay acceptable? LinkedIn-style feeds can be eventually consistent — if a post shows up 2 seconds late, nobody cares.

*Assuming: follower-based feed with basic ranking (recency + engagement), 300M DAU, heavy read-skew (1000:1), celebrity accounts with up to 50M followers, acceptable latency a few seconds.*

---

## Scope

I'll design post creation, feed generation, and feed retrieval. I'll skip the ML ranking model itself, ads insertion, and story/reel format. I'll focus on the infrastructure that makes feeds fast to read and eventually consistent on writes.

Scale: 300M DAU. Assume each user reads their feed 5 times/day = 1.5B feed reads/day = 17,000 reads/sec. Writes: if 10% of users post once a day = 30M posts/day = 350 writes/sec. This is heavily read-skewed — optimize for reads.

---

## High Level Design

```
┌──────────┐                                                         ┌──────────┐
│  Writer  │──POST /post──▶┌───────────────┐                        │  Reader  │
│  (user)  │               │  Post Service │                        │  (user)  │
└──────────┘               └──────┬────────┘                        └────┬─────┘
                                  │                                       │
                                  ▼                                       ▼
                           ┌─────────────┐                      ┌────────────────┐
                           │   Kafka     │                       │  Feed Service  │
                           │ (post.new)  │                       └────────┬───────┘
                           └──────┬──────┘                               │
                                  │                           ┌───────────┼────────────┐
                          ┌───────▼──────┐                   ▼           ▼            ▼
                          │  Fan-out     │           ┌────────────┐ ┌─────────┐ ┌─────────┐
                          │  Service     │           │ Feed Cache │ │  Post   │ │  User   │
                          └───┬──────┬──┘           │  (Redis)   │ │  Store  │ │  Graph  │
                              │      │               └────────────┘ │(Cassand)│ │ (MySQL) │
                 ┌────────────┘      └──────────┐                   └─────────┘ └─────────┘
                 ▼                              ▼
        ┌─────────────────┐          ┌──────────────────┐
        │  Feed Cache     │          │  Post Store      │
        │  (Redis sorted  │          │  (Cassandra)     │
        │   set per user) │          │                  │
        └─────────────────┘          └──────────────────┘
```

Two paths: write path (fan-out when a post is created) and read path (serving pre-built feeds). The key insight is **pre-computation** — build the feed at write time, not read time.

---

## Low Level Design

### The Core Problem: Fan-out on Write vs Fan-out on Read

This is the most important design decision for a feed system.

**Fan-out on Write (Push model):**
When User A posts something, immediately push that post ID into the feed of every follower. If A has 1,000 followers, write to 1,000 Redis sorted sets. When followers open their app, their feed is pre-built — just read from Redis. Reads are O(1). Writes are O(followers).

This works perfectly for normal users. But for a celebrity with 50M followers? One post = 50M Redis writes. That's a spike that can take minutes and crush the system.

**Fan-out on Read (Pull model):**
When a user opens their feed, fetch posts from everyone they follow on the fly. No pre-computation on write. Reads are expensive — if you follow 500 people, that's 500 lookups merged and sorted. But writes are cheap — just store the post once.

**Hybrid (what Twitter and LinkedIn actually use):**

Use fan-out on write for regular users. For celebrities (defined as followers > threshold, say 1M), skip fan-out — don't push to followers. Instead, on feed read, merge the pre-built feed with a real-time fetch of celebrity posts you follow. This keeps write fan-out manageable while ensuring celebrity posts appear in feeds.

```
Regular user posts:
  → Fan-out worker pushes post_id to all follower feed caches immediately

Celebrity posts:
  → Only persist to post store, no fan-out
  → When follower reads feed: merge feed_cache + fetch recent celebrity posts
```

---

### Data Model

```sql
-- MySQL: social graph (who follows whom)
CREATE TABLE follows (
    follower_id   BIGINT NOT NULL,
    followee_id   BIGINT NOT NULL,
    created_at    DATETIME NOT NULL,
    PRIMARY KEY (follower_id, followee_id),
    INDEX idx_followee (followee_id)     -- "who follows celebrity X" for fan-out
);

-- MySQL: post metadata
CREATE TABLE posts (
    id            BIGINT PRIMARY KEY,   -- Snowflake ID
    user_id       BIGINT NOT NULL,
    content       TEXT,
    media_urls    JSON,                 -- ["s3://...img1", "s3://...img2"]
    like_count    BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    created_at    DATETIME NOT NULL,
    INDEX idx_user_created (user_id, created_at DESC)
);
```

```
-- Redis: pre-built feed per user (sorted set, score = timestamp)
Key:   feed:{user_id}
Type:  Sorted Set
Value: post_ids, sorted by creation timestamp (score)
Max:   keep only latest 1,000 post IDs (trim on each write)

ZADD feed:12345 1687391823 "post_id:789"    -- add post to feed
ZREVRANGE feed:12345 0 19                   -- get 20 most recent posts
ZREMRANGEBYRANK feed:12345 0 -1001          -- trim to 1000 entries
```

---

### Post Creation Flow

```
1. User A submits post via POST /v1/posts
2. Post Service validates, saves to MySQL (returns post_id immediately)
3. Publish { post_id, user_id, timestamp } to Kafka topic "post.new"
4. Return 201 to user — done from their perspective

5. Fan-out Service consumes from Kafka:
   a. SELECT follower_id FROM follows WHERE followee_id = A.user_id
      (paginate if > 10,000 followers)
   b. Is A a celebrity? (followers > 1M) → skip fan-out, just index
   c. For each follower_id:
      ZADD feed:{follower_id} {timestamp} {post_id}
      EXPIRE feed:{follower_id} 604800  (7 days TTL)
```

Fan-out is async, decoupled via Kafka. Post creation feels instant for the writer. Followers see the post within a few seconds — the fan-out lag.

---

### Feed Read Flow

```
1. GET /v1/feed?page_token=xxx
2. Feed Service checks Redis: ZREVRANGE feed:{user_id} 0 19
3. Cache hit: get 20 post IDs
4. If user follows any celebrities: fetch their recent posts from Post Store
5. Merge and de-duplicate the two lists, re-sort by timestamp
6. Fetch full post details (content, author, like counts) for the 20 IDs
   - Post details cached in Redis too: GET post:{post_id}
7. Return hydrated feed objects

Cache miss (user hasn't loaded feed in 7 days or is new):
  - Fetch follower list from MySQL
  - Fetch recent posts from each followee from Cassandra
  - Merge, sort, store in Redis
  - Return result (this is slow — first load, acceptable)
```

---

### API Design

```
POST /v1/posts
  Body: { "content": "Hello world", "media": [...] }
  Response 201: { "post_id": "789", "created_at": "..." }

GET /v1/feed
  Query: page_token (cursor for pagination), limit=20
  Response 200: {
    "posts": [ { post_id, author, content, like_count, ... }, ... ],
    "next_page_token": "eyJsYXN0X3RzIjoiMT..."  // cursor = encoded last timestamp
  }

POST /v1/posts/{id}/like
POST /v1/posts/{id}/comment
```

Cursor-based pagination (not offset). Offset breaks when new posts are inserted — you miss posts or see duplicates. Cursor encodes the last seen timestamp/ID, so pagination is stable even as new posts arrive.

---

## Scale — What Breaks at 10x?

At 170,000 feed reads/sec, the pressure points:

**Redis feed cache:** Sorted sets per user. 300M users × 1,000 post IDs × 8 bytes = 2.4 TB. This requires a Redis cluster. Shard by `user_id` — consistent hashing. Each shard handles a subset of user feeds. The shard for a celebrity's followers might be hot if 50M fans all read their feed simultaneously — but we've mitigated this with the hybrid approach.

**Fan-out workers:** For 350 posts/sec average, but viral events cause spikes — a famous post might trigger 50M fan-outs. Workers scale horizontally. Kafka buffers the backlog. Fan-out lag increases during spikes (from 1 second to 30 seconds) but no data is lost. Set SLA expectations accordingly: "feed is eventually consistent, usually within a few seconds, up to 60 seconds during viral events."

**Post detail reads:** After getting post IDs from the feed cache, we need full post objects. Cache these in Redis with key `post:{post_id}` and TTL of 5 minutes. Like counts change frequently — cache with short TTL or update in-place with `HINCRBY`. Cassandra stores the source of truth for post content.

**Like/Comment counts:** Don't update MySQL on every like — that's millions of writes/sec on a hot post. Write likes to Cassandra (append-only log), aggregate counts with a background job every minute, update MySQL. Use Redis for real-time approximate counts with `INCR like_count:{post_id}`. Periodic sync to MySQL for persistence.

---

## Trade-offs

**Consistency of like counts:** Feed shows "4.2M likes" but the real count might be 4.2M ± 10K. This is fine. Showing "4,200,047" is not better UX than "4.2M." We accept approximate counts for high-engagement posts. Financial data can never be approximate — but social metrics can.

**Feed freshness vs computation cost:** Longer TTL on feed cache = cheaper to maintain but feeds go stale. We use TTL of 7 days with event-driven invalidation — if you unfollow someone, their posts are removed from your cached feed immediately. If you follow someone new, their recent posts are injected.

**Ranking:** Pure chronological feed is simple. Algorithmic ranking (engagement signals, relationship strength) improves the product but requires ML inference on each feed read. The infrastructure here supports it — ranking is a post-processing step after fetching the 20 candidate post IDs. Pass them through a lightweight ranking model (fast inference, pre-computed feature vectors) and re-sort before returning to the client.

---

## Cross-Questions

**How do you handle a user following 10,000 accounts?**

On feed read, fetching 10,000 people's recent posts in real-time is too slow. The pre-built cache solves this — we've already merged all their posts at write time. The 1,000-entry limit in the sorted set means if someone follows 10,000 people, only the most recent posts appear. For power users with very large follow graphs, we cap the active followees we fan-out from to the 500 most recent interactions — "you mostly see posts from people you engage with."

**How do you remove a post from all feeds if the user deletes it?**

Two approaches. Soft delete: mark the post as deleted in MySQL. During feed hydration (when we fetch full post objects), skip deleted post IDs. The post ID stays in cached feeds but returns null when fetched — the client filters it out. This is fast and requires no cache modification. Hard delete: publish a `post.deleted` event to Kafka. A cleanup worker removes the post ID from all affected user caches. Expensive for viral posts (millions of caches to update) — soft delete is the pragmatic choice.

**How would you implement "trending posts" or "trending topics"?**

A separate Trending Service. Every like, share, and comment is an event on Kafka. The Trending Service consumes these events and maintains a count-min sketch (a probabilistic data structure) per time window — say "likes in the last 5 minutes." Top-N post IDs with highest engagement in the window = trending. This doesn't require storing every event — the sketch is O(1) memory regardless of event volume. Update the trending feed in Redis every 30 seconds. Trending is a global feed, not personalized — one sorted set shared by all users.

**How do you handle time zones for scheduled posts?**

The post is stored with UTC timestamp. When the user says "post at 9 AM IST," convert to UTC at creation time and store in a `scheduled_at` column. A Job Scheduler (see Q8) picks up posts where `scheduled_at <= NOW()` and triggers the fan-out. No timezone logic in the feed service itself — everything is UTC internally, converted to the user's local timezone only at display time in the client.

**What's the difference between your design and Twitter's actual architecture?**

Twitter (now X) uses a similar hybrid fan-out. They found that for accounts with millions of followers, even their fan-out infrastructure couldn't keep up with high-volume tweeting events in real-time. Their solution: a separate "Timeline Mixer" that merges pre-built feed with real-time celebrity tweet injection at read time — essentially the same hybrid approach I described. The key difference is that Twitter's ranking ML model runs at read time in under 100ms, scoring thousands of candidate tweets for personalization. That ranking infrastructure is a massive separate system.
