# Q5: Design News Feed (Twitter/LinkedIn)

---

## Introduction

A news feed system is responsible for generating and displaying a personalized stream of content for each user — posts, updates, and activity from people or accounts they follow. Twitter's timeline, LinkedIn's feed, and Instagram's home screen are all news feed systems. The feed is typically sorted by recency, relevance, or a combination of both using a ranking algorithm.

The core challenge is that generating a feed on demand is expensive. When a user opens the app, the system would need to fetch all the people they follow, retrieve all their recent posts, merge them, sort them, and paginate — all in real time. For a user following thousands of accounts, this is too slow to be acceptable. The solution is to pre-compute feeds in the background and cache them, so the read is instant.

There are two primary design approaches: **fan-out on write** and **fan-out on read**. Fan-out on write means when a user posts something, the system immediately pushes that post to the feeds of all their followers. Reads are fast because the feed is pre-built. The downside is the write cost for celebrities with millions of followers — one post triggers millions of feed updates. Fan-out on read means the feed is assembled at query time, which is cheaper to write but slower to read. Most production systems use a hybrid: fan-out on write for regular users, fan-out on read for high-follower accounts.

Feed ranking adds another layer. A simple reverse-chronological feed is easy to build, but modern platforms use machine learning models to score and reorder posts based on engagement signals, user preferences, and content freshness. This ranking layer sits on top of the retrieval system and can be swapped or tuned independently.

Pagination, feed caching with TTL, and handling new posts after a user loads their feed (so you don't miss content) are additional operational concerns that come up in a complete design.

---

## How to Approach This in an Interview

News feed is about one core trade-off: **fan-out on write vs fan-out on read**. Everything else in the design flows from this decision. Interviewers expect you to explain both clearly, then justify which you'd choose and when you'd use the hybrid. The celebrity problem is the key stress test.

---

## Clarifying Questions

**1. Follower-based or algorithmic?**

"Is this a simple chronological feed (you see posts from people you follow, newest first) or an algorithmic feed ranked by engagement/relevance?"

*Why this matters:* Chronological = sort by timestamp. Algorithmic = ML ranking layer + more complex data needs. I'll design the infrastructure that supports both, with ranking as a post-processing step.

**2. Read:Write ratio?**

"What's the typical ratio of feed reads to post creations? And is there a celebrity problem — accounts with millions of followers?"

*Why this matters:* Social networks are typically 1,000:1 read-heavy. The celebrity problem (50M followers) breaks naive fan-out approaches — you can't write to 50M sorted sets every time Taylor Swift tweets.

**3. Consistency requirements?**

"If A posts something, does every follower need to see it immediately, or is a few seconds of delay acceptable?"

*Why this matters:* Eventually consistent feed (5-10 second delay) is much easier to build than strongly consistent feed. For a social network, nobody cares if a post appears 5 seconds late.

**4. Scale?**

"How many daily active users and posts per day?"

### Assumptions

```
- Follower-based feed with recency ranking (newest first)
- 300M DAU
- 1000:1 read-to-write ratio
- Celebrity accounts: up to 50M followers
- Eventually consistent: feed updates within a few seconds
- Each user reads feed 5x/day, posts once every 3 days
```

---

## Back-of-Envelope Math

```
DAU: 300M
Feed reads/day: 300M × 5 reads = 1.5B reads/day
= 1.5B / 86,400 = ~17,000 reads/sec
Peak (3x): ~50,000 reads/sec

Post writes/day: 300M / 3 = 100M posts/day
= 100M / 86,400 = ~1,157 posts/sec

Fan-out for average user with 500 followers:
  1,157 posts/sec × 500 followers = 578,500 fan-out writes/sec
  These go to Redis sorted sets — needs Redis cluster

Celebrity fan-out:
  One post by user with 50M followers = 50M Redis writes
  At 100K writes/sec for Redis, that's 500 seconds = 8 minutes
  Too slow — this is why we need the hybrid approach

Feed cache per user:
  Top 1,000 posts × 8 bytes per post_id = 8 KB per user
  300M users × 8 KB = 2.4 TB of Redis storage
  → Definitely needs Redis cluster with multiple shards
```

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
                                  │                           ┌───────────┼──────────┐
                          ┌───────▼──────┐                   ▼           ▼          ▼
                          │  Fan-out     │           ┌────────────┐ ┌─────────┐ ┌─────────┐
                          │  Worker      │           │ Feed Cache │ │  Post   │ │  Follow │
                          └───┬──────┬──┘           │  (Redis)   │ │  Store  │ │  Graph  │
                              │      │               └────────────┘ │(MySQL)  │ │ (MySQL) │
                 ┌────────────┘      └──────────┐                   └─────────┘ └─────────┘
                 ▼                              ▼
        ┌─────────────────┐          ┌──────────────────┐
        │  Feed Cache     │          │  Post Store      │
        │  (Redis sorted  │          │  (MySQL)         │
        │   set per user) │          │                  │
        └─────────────────┘          └──────────────────┘

Two separate paths:
  Write path: Post Service → Kafka → Fan-out Worker → Redis (feed caches)
  Read path:  Feed Service → Redis (read pre-built feed) → hydrate post details
```

---

## The Core Problem: Fan-out Explained

**What is fan-out?**

When User A posts something, their followers need to see it in their feed. "Fan-out" means distributing A's post to all of A's followers' feed caches. The name comes from the shape: one post fans out to many recipients.

```
        Post by A
            ↓
   ┌────────┴─────────┐
   ↓    ↓    ↓    ↓   ↓
Feed_B Feed_C Feed_D Feed_E ...
(A's followers' Redis sorted sets)
```

---

### Fan-out on Write (Push model) — Explained

**When:** A posts something.
**What happens:** Immediately compute A's follower list and write A's post_id to each follower's feed cache.

```python
def fanout_on_write(post_id: int, user_id: int, timestamp: float):
    # Get all followers of the poster
    followers = db.get_followers(user_id)  # could be 500 or 50M
    
    for follower_id in followers:
        # Add post_id to this follower's Redis sorted set
        # Score = timestamp (determines sort order in feed)
        redis.zadd(f"feed:{follower_id}", {str(post_id): timestamp})
        
        # Keep only the latest 1,000 posts to prevent unbounded growth
        redis.zremrangebyrank(f"feed:{follower_id}", 0, -1001)
        
        # Set TTL: if user hasn't loaded their feed in 7 days, cache expires
        redis.expire(f"feed:{follower_id}", 604800)
```

**What is a Redis Sorted Set?**

A Redis Sorted Set is a data structure where every element has:
- A **member** (the value, e.g., a post_id string like "789")
- A **score** (a float, e.g., Unix timestamp 1687391823.0)

Members are automatically sorted by score. This makes it perfect for a time-ordered feed.

```
Redis key: feed:user_B
Type: Sorted Set
Contents:
  member:"post_901"  score: 1687392000  ← newest (highest score)
  member:"post_799"  score: 1687391823
  member:"post_455"  score: 1687388400
  member:"post_123"  score: 1687300000  ← oldest
  ...

Commands:
ZADD feed:user_B 1687392001 "post_789"        → add new post
ZREVRANGE feed:user_B 0 19                    → get 20 newest posts
ZCARD feed:user_B                             → how many posts in cache
ZREMRANGEBYRANK feed:user_B 0 -1001           → remove oldest to keep max 1000
EXPIRE feed:user_B 604800                     → 7-day TTL
```

**Pros:** Feed reads are O(1) — just ZREVRANGE. No computation at read time.
**Cons:** Every post write causes N Redis writes (N = follower count). For celebrities, N = 50M = catastrophic.

---

### Fan-out on Read (Pull model) — Explained

**When:** User B opens their feed.
**What happens:** Fetch recent posts from everyone B follows on the fly.

```python
def fanout_on_read(user_id: int, limit: int = 20):
    # Get list of users B follows
    following = db.get_following(user_id)  # who user_B follows
    
    # For each followed user, fetch their recent posts
    all_posts = []
    for followee_id in following:
        posts = db.get_recent_posts(followee_id, limit=limit)
        all_posts.extend(posts)
    
    # Merge and sort by timestamp
    all_posts.sort(key=lambda p: p.created_at, reverse=True)
    return all_posts[:limit]
```

**Pros:** Write is cheap — just save the post once. No fan-out computation.
**Cons:** Read is expensive — if B follows 500 people, that's 500 DB lookups per feed load. At 50,000 reads/sec, that's 25M DB queries/sec. Database collapses.

---

### Hybrid Approach (What Twitter/LinkedIn Actually Use)

**The insight:** fan-out on write is great for most users but breaks for celebrities. Fan-out on read is great for celebrities but terrible for normal users.

**Solution:** Use fan-out on write for everyone EXCEPT celebrities. For celebrities, skip fan-out and merge at read time.

```python
CELEBRITY_THRESHOLD = 1_000_000  # 1M followers = celebrity

def fanout_on_write(post_id: int, poster_user_id: int, timestamp: float):
    follower_count = db.count_followers(poster_user_id)
    
    if follower_count > CELEBRITY_THRESHOLD:
        # Celebrity: just save the post, don't fan out
        # (post will be fetched at read time for celebrity followers)
        mark_as_celebrity_post(post_id, poster_user_id)
        return
    
    # Normal user: fan out to all followers
    followers = db.get_followers(poster_user_id)
    for follower_id in followers:
        redis.zadd(f"feed:{follower_id}", {str(post_id): timestamp})
        redis.zremrangebyrank(f"feed:{follower_id}", 0, -1001)

def get_feed(user_id: int) -> list[Post]:
    # Step 1: Get pre-built feed from Redis (non-celebrity posts)
    post_ids = redis.zrevrange(f"feed:{user_id}", 0, 19)  # 20 posts
    
    # Step 2: Check which celebrities this user follows
    celebrities_following = get_followed_celebrities(user_id)
    
    if celebrities_following:
        # Fetch recent celebrity posts directly from MySQL
        celeb_posts = db.get_recent_posts_by_users(
            user_ids=celebrities_following,
            limit=10
        )
        # Merge with pre-built feed
        all_posts = merge_and_sort(post_ids, celeb_posts)[:20]
    else:
        all_posts = post_ids
    
    # Step 3: Hydrate — get full post details for the post_ids
    return fetch_post_details(all_posts)
```

**Why does this work for celebrities?**

When Taylor Swift (50M followers) tweets, we don't write to 50M Redis sorted sets. We just save one row in MySQL. When any of her 50M followers loads their feed, we do ONE MySQL query `SELECT posts WHERE user_id = TaylorSwift_id LIMIT 10`. This is fast — indexed query on a hot row that's in MySQL's buffer pool.

The merge at read time adds maybe 5ms. Users don't notice.

---

## Data Model

```sql
-- MySQL: the social graph (who follows whom)
CREATE TABLE follows (
    follower_id   BIGINT NOT NULL,   -- the person who follows
    followee_id   BIGINT NOT NULL,   -- the person being followed
    created_at    DATETIME NOT NULL,
    
    PRIMARY KEY (follower_id, followee_id),
    -- Composite PK: fast lookup "does user A follow user B?"
    
    INDEX idx_followee (followee_id)
    -- Critical for fan-out: "who are all followers of user X?"
    -- SELECT follower_id FROM follows WHERE followee_id = X
);

-- MySQL: posts
CREATE TABLE posts (
    id            BIGINT PRIMARY KEY,   -- Snowflake ID (sortable by time)
    user_id       BIGINT NOT NULL,
    content       TEXT,
    media_urls    JSON,                  -- ["s3://img1.jpg", "s3://img2.jpg"]
    
    -- Counts are approximate (updated async) — not real-time exact
    like_count    BIGINT DEFAULT 0,
    comment_count BIGINT DEFAULT 0,
    share_count   BIGINT DEFAULT 0,
    
    is_deleted    BOOLEAN DEFAULT FALSE,
    created_at    DATETIME NOT NULL,
    
    INDEX idx_user_created (user_id, created_at DESC)
    -- Critical for celebrity fetch: "recent posts by user X"
    -- SELECT * FROM posts WHERE user_id = X ORDER BY created_at DESC LIMIT 10
);

-- MySQL: celebrity flag (cached, updated by background job)
CREATE TABLE user_stats (
    user_id       BIGINT PRIMARY KEY,
    follower_count BIGINT DEFAULT 0,
    is_celebrity  BOOLEAN DEFAULT FALSE,   -- follower_count > 1M
    updated_at    DATETIME NOT NULL
);
```

**Redis: feed cache per user**

```
Key:   feed:{user_id}
Type:  Sorted Set
Member: post_id (as string)
Score:  Unix timestamp (determines order — higher = newer)
Max:    1,000 entries (trim on each fan-out write)
TTL:    7 days (removed if user hasn't loaded feed in a week)
```

**Redis: post detail cache**

```
Key:   post:{post_id}
Type:  Hash
Fields: user_id, content, like_count, comment_count, created_at
TTL:   5 minutes

Why: After getting 20 post_ids from feed cache, we need full post details.
Caching posts avoids 20 MySQL queries per feed load.
```

---

## Write Path — Step by Step

When user A creates a post:

```
Step 1: POST /v1/posts
        Body: { "content": "Hello world", "media": ["s3://img.jpg"] }

Step 2: Post Service validates and saves to MySQL
        INSERT INTO posts (id, user_id, content, media_urls, created_at)
        id = generate_snowflake()   → e.g., 1687391823456001024
        
        Returns post_id to user immediately — write is done from their perspective

Step 3: Publish to Kafka
        Topic: post.new
        Message: { post_id: 1687..., user_id: A, timestamp: 1687391823 }

Step 4: Fan-out Worker consumes from Kafka
        Get poster's follower count from user_stats
        
        if is_celebrity: just index in celebrity_posts table, done
        
        else:
          SELECT follower_id FROM follows WHERE followee_id = A
          -- Paginate in batches of 1000 if many followers
          
          For each batch of followers:
            ZADD feed:{follower_id} {timestamp} {post_id}  (pipelined Redis)
          
          Fan-out complete

Step 5: Invalidate related caches
        If A updated an existing post (or deleted one):
        DEL post:{post_id}  → force next read to fetch fresh from MySQL
```

**Fan-out latency:**

For a normal user with 500 followers: 500 Redis writes ≈ 0.5 seconds.
Followers see the post within ~1-2 seconds of posting. This is acceptable (eventually consistent).

For a user with 100K followers: 100,000 Redis writes ≈ 50 seconds. Still eventually consistent — followers see the post within a minute. If the product requires faster fan-out, pre-shard the follower list and run fan-out workers in parallel.

---

## Read Path — Step by Step

When user B loads their feed:

```
Step 1: GET /v1/feed?limit=20&page_token=null

Step 2: Feed Service checks Redis
        ZREVRANGE feed:user_B 0 19
        Returns: ["post_901", "post_799", "post_455", ...]  (20 post_ids)

Step 3: If user follows celebrities
        SELECT id FROM follows f
        JOIN user_stats s ON f.followee_id = s.user_id
        WHERE f.follower_id = user_B AND s.is_celebrity = TRUE
        
        For each celebrity: SELECT * FROM posts WHERE user_id = X ORDER BY created_at DESC LIMIT 5
        
        Merge celebrity posts with Redis feed posts
        De-duplicate, sort by timestamp
        Take top 20

Step 4: Hydrate post details
        For each post_id in the 20:
          GET post:{post_id}   ← check Redis cache first
          If miss: SELECT * FROM posts WHERE id = post_id   ← MySQL fallback
        
        Cache miss posts back to Redis: SET post:{post_id} {...} EX 300

Step 5: Return hydrated feed
        {
          "posts": [
            { "id": 901, "user_id": ..., "content": "...", "like_count": 1247, ... },
            ...
          ],
          "next_page_token": "eyJsYXN0X3RzIjoxNjg3M..."  ← cursor for pagination
        }
```

**Cold start (new user or cache expired):**

```
ZREVRANGE feed:user_B 0 19 → empty (no cache)

Build feed from scratch:
  SELECT followee_id FROM follows WHERE follower_id = user_B
  For each followee (non-celebrity):
    SELECT id, created_at FROM posts WHERE user_id = followee_id
    ORDER BY created_at DESC LIMIT 20
  Merge, sort, take top 20
  Write to Redis: ZADD feed:user_B ...
  
This is slow (200-500ms). Acceptable only on first load or after 7-day inactivity.
```

---

### Cursor-based Pagination Explained

**Why not offset pagination?**

Offset: `LIMIT 20 OFFSET 40` = skip 40, return 20. Simple, but breaks when new posts arrive during pagination:
```
User loads page 1 (posts 1-20) at t=0
3 new posts added at t=1
User loads page 2 (offset 20) at t=2
  → The "page 2" now includes posts that were on page 1
  → User sees duplicates AND misses posts
```

**Cursor-based pagination:**

The cursor encodes the last item you saw (its timestamp or ID). The next request says "give me posts OLDER THAN this cursor."

```
First load:
  ZREVRANGE feed:user_B 0 19   → posts sorted newest first
  Last post has timestamp: 1687388400
  Return cursor: base64_encode({ "last_ts": 1687388400, "last_id": "post_455" })

User scrolls down (requests next page):
  ZREVRANGEBYSCORE feed:user_B (1687388400 -inf LIMIT 0 20
  → Returns posts with score < 1687388400 (older than last seen)

New posts can be added without affecting pagination.
```

This is how every major feed (Twitter, Instagram, LinkedIn) implements infinite scroll pagination.

---

## Scale — What Breaks at 10x?

10x = 3B DAU, 170,000 reads/sec, 10,000 posts/sec, 578,500 fan-out writes/sec.

**Redis feed cache (2.4 TB → 24 TB):** Redis Cluster. Shard by `user_id`. Consistent hashing so adding new shards minimizes data movement. 24 TB across 12 nodes × 2 TB each. Each node handles a subset of user feeds.

**Fan-out workers:** 10,000 posts/sec × 500 followers avg = 5M Redis writes/sec just for fan-out. Scale fan-out workers horizontally in Kubernetes. Each worker is stateless — pull from Kafka, write to Redis. 50 worker pods × 100K Redis writes/sec each = 5M writes/sec total.

**MySQL read replicas for post store:** Feed hydration does 20 MySQL queries per feed load. At 170K reads/sec with 20 queries each = 3.4M MySQL queries/sec. Impossible on a single server. Cache post details in Redis (90%+ hit rate for popular posts). Add 10-20 MySQL read replicas for the rest.

**Like count consistency:** At 10M likes/sec on viral posts, updating MySQL on every like is impossible. Write likes to a Redis counter `INCR like_count:{post_id}`. Background job every 30 seconds syncs Redis counters to MySQL. User sees approximate like count (accurate to within 30 seconds). This is what Twitter/LinkedIn do — "4.2M likes" is always approximate.

---

## Trade-offs

**Consistency of like counts:**

Strong consistency would require a MySQL UPDATE on every like, with row-level locking. At 10M likes/sec on a viral post, the row would be locked millions of times per second — impossible.

Eventual consistency: Redis counter is incremented (atomic, fast), background job syncs to MySQL every 30 seconds. Users see counts that are slightly stale but accurate enough for the use case. Nobody cares if Twitter shows "4,200,000" vs "4,200,047" likes.

**Feed cache TTL vs event-driven invalidation:**

TTL (e.g., 7 days): simple, feed refreshes periodically. Risk: stale feed if user unfollows someone but cache still shows that person's posts until TTL.

Event-driven invalidation: when user unfollows A, immediately remove A's posts from their feed cache. More complex but more accurate. Implement with: `ZREMRANGEBYSCORE feed:user_B -inf +inf WHERE member in (A's post_ids)` — tricky to implement efficiently.

Best practice: TTL for staleness tolerance + event-driven for important actions (unfollow, block, post deletion).

**Algorithmic ranking:**

The infrastructure above delivers a chronological feed. To add ML ranking:
- After Step 4 (hydration), pass the 20 hydrated posts through a ranking model
- Model inputs: user engagement history, post age, author relationship strength, post media type
- Model output: ranked score per post → re-sort before returning
- This adds 20-50ms for inference — acceptable within the 200ms SLA

This is exactly how LinkedIn's feed works: infrastructure serves 100+ candidate posts, ranking model selects top 20. The infrastructure design doesn't change.

---

## Cross-Questions

**Q: How do you handle a user who follows 10,000 accounts?**

Fan-out on write for 10,000 followees × their posts = huge Redis sorted set and very slow cold start.

Solutions:
1. **Cap active fan-out:** Only fan out posts from the 500 followees the user interacts with most (recent likes, comments, messages). Less active followees are fetched on-demand at read time.
2. **Interest graph:** Feed ranking model down-weights accounts the user rarely engages with. Even if their posts are in the feed, they won't be shown first.
3. **Separate feed segments:** "Close friends" feed (always fan-out) vs "following" feed (only show when scrolling far down).

**Q: How do you implement post deletion from all feeds?**

**Soft delete (recommended):**
```
UPDATE posts SET is_deleted = TRUE WHERE id = post_id
```
Post stays in Redis feed caches (sorted sets still contain the post_id). When we hydrate post details in the read path, we check `is_deleted`. Deleted posts return null → client filters them from display.

No cache modification needed. Works automatically for all users. Cost: every feed hydration checks `is_deleted` (already included in the SELECT query).

**Hard delete (for compliance/GDPR requests):**
Publish `post.deleted` event to Kafka. Cleanup worker removes post_id from all Redis feed caches that contain it. Expensive for viral posts (millions of caches) — run as a low-priority background job over hours.

**Q: How do you handle "Trending Topics"?**

Trending is a global feed, not personalized. Entirely separate from the personalized feed.

```
All likes, shares, comments → Kafka topic "engagement.events"

Trending Service consumes:
  - Maintains a Count-Min Sketch per 5-minute window
    (probabilistic data structure: O(1) memory, ~1% error)
  - For each event: increment counter for associated post
  - Every 30 seconds: find top-N posts with highest engagement velocity
  - Write to Redis: ZADD trending:global {score} {post_id}

What is Count-Min Sketch?
  A 2D array of counters. Items are hashed into multiple positions.
  Count(item) = minimum across all its hash positions.
  Memory: constant regardless of how many items you track.
  Error bound: mathematically guaranteed < 1% error.
  
  Alternative: just use Redis INCR per post_id in a 5-min window.
  At 10M engagement events/sec, that's 10M Redis INCR/sec — too many.
  Count-Min Sketch reduces this by batching and sampling.

Trending feed in Redis:
  Key: trending:global
  Type: Sorted Set (same as user feed, but global)
  Score: engagement velocity in last 5 minutes
  
  Users who want trending: read from trending:global instead of feed:{user_id}
```

**Q: What's the difference between this design and Twitter's actual architecture?**

Twitter (now X) uses the same hybrid fan-out. Their additional considerations:
1. **Timeline Mixer:** A separate service that merges the pre-built algorithmic feed with real-time celebrity tweet injection. Same concept as our hybrid read.
2. **ML Ranking at read time:** Twitter ranks 1,500 candidate tweets through a neural network for each feed load. The infrastructure serves candidates; ML selects what to show.
3. **"For You" vs "Following":** Two separate feeds. "Following" = chronological fan-out on write. "For You" = algorithmic, includes content from non-followed accounts.

The core infrastructure decision (hybrid fan-out, Redis sorted sets, eventually consistent) is the same.
