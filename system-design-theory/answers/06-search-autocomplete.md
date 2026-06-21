# Q6: Design Search Autocomplete (Google Search Bar)

---

## Clarifying Questions

First — what triggers autocomplete? Keystroke by keystroke as the user types, or only on pause? Keystroke is harder — you need sub-100ms responses for every character.

What are we autocompleting — search queries (like Google), product names (like Amazon), or user names (like Twitter's @mention)? The data source changes significantly.

Do suggestions need to be personalized per user, or are they global? Global trending queries are much simpler. Personalized suggestions require per-user history which adds storage and latency.

How many queries/sec are we handling? And do we need to handle multiple languages and unicode?

*Assuming: global trending search queries (not personalized), 10M DAU, each user types ~5 searches/day triggering ~10 keystrokes each = 500M autocomplete requests/day = 5,800/sec, top 10 suggestions, sub-100ms response, English only to start.*

---

## Scope

I'll design the data pipeline that collects search queries and computes suggestions, and the serving layer that returns top suggestions for a prefix in real-time. I'll skip spell correction, semantic understanding, and personalization — those are separate ML systems.

---

## High Level Design

```
┌──────────┐  Keystrokes  ┌─────────────┐          ┌──────────────────────┐
│  Client  │─────────────▶│  API GW /   │          │   Data Pipeline      │
│  (browser│◀─────────────│  CDN Cache  │          │                      │
│  /app)   │  top-10 list └──────┬──────┘          │  Search Logs         │
└──────────┘                     │                  │       │              │
                                 ▼                  │       ▼              │
                        ┌────────────────┐          │  Kafka (raw queries) │
                        │ Autocomplete   │          │       │              │
                        │ Service        │          │       ▼              │
                        └────────┬───────┘          │  Spark (hourly agg)  │
                                 │                  │       │              │
                    ┌────────────┼──────────┐       │       ▼              │
                    ▼           ▼          ▼        │  Trie Builder        │
              ┌──────────┐ ┌────────┐ ┌───────┐   │  (batch, daily)      │
              │   Trie   │ │ Redis  │ │  DB   │   └──────────────────────┘
              │  (in     │ │(prefix │ │(MySQL │              │
              │  memory) │ │ cache) │ │ freq) │   ◀──────────┘
              └──────────┘ └────────┘ └───────┘   (trie loaded into memory
                                                    from DB on startup)
```

Two separate concerns: **data pipeline** (computing what the top suggestions are) and **serving layer** (returning them fast). Both need to be designed independently.

---

## Low Level Design

### The Core Data Structure — Trie

A Trie (prefix tree) is the natural structure for prefix-based lookups. Each node represents a character. A path from root to node represents a prefix. Each node stores the top-K query suggestions for that prefix.

```
Root
 ├── 'a'
 │    ├── 'p'
 │    │    ├── 'p' → ["apple", "application", "apple iphone"] (top-3 for "app")
 │    │    └── 'l' → ["apple", "apple watch"]
 │    └── 'm' → ["amazon", "amazon prime"]
 └── 'g'
      ├── 'o' → ["google", "google maps", "google drive"]
      └── 'i' → ["github", "gmail"]
```

Each node stores up to K (say 10) query strings with their frequency scores — not recursively computed on the fly, but pre-computed and cached at build time. This makes lookup O(length of prefix) — extremely fast.

**Why pre-cache top-K at each node?**

Naive approach: for prefix "ap", traverse all children and descendants, collect all queries, sort by frequency. This is O(n) where n = number of queries in the subtree — too slow for real-time serving.

Pre-computed approach: during Trie building, propagate top-K suggestions up the tree. Each node knows its top-K without traversing children. Lookup is O(L) where L = length of the typed prefix, typically 1–10 characters. Extremely fast.

---

### Data Pipeline — How Suggestions Are Computed

**Step 1: Collect search queries**

Every search query the user completes (not every keystroke) goes to Kafka as a raw event: `{ query: "apple watch", user_id: 123, timestamp: ... }`. Volume: 50M searches/day = 580/sec.

**Step 2: Aggregate frequencies**

A Spark job runs hourly. Reads the last 7 days of raw queries from Kafka/HDFS. Computes frequency of each query. Weights recent queries higher (queries from today count more than queries from 7 days ago — use exponential decay). Filters out queries with frequency below threshold (removes spam and sensitive terms).

Output: a table of `(query, frequency_score)` pairs.

**Step 3: Build the Trie**

Daily (or on-demand): read the frequency table, build a Trie in memory, serialize to disk/S3. Each autocomplete serving node loads the Trie from S3 on startup or on a trie refresh signal.

For updates without downtime: maintain two Trie objects in memory (blue/green). Update the inactive one, atomically swap the pointer. Zero downtime Trie refresh.

```
MySQL table:
CREATE TABLE query_frequencies (
    query       VARCHAR(200) PRIMARY KEY,
    frequency   BIGINT NOT NULL,
    updated_at  DATETIME NOT NULL,
    INDEX idx_freq (frequency DESC)
);
```

---

### Serving Layer — Returning Results Fast

**Lookup in Trie:** User types "app" → traverse root → 'a' → 'p' → 'p' → return pre-cached top-10 list. Single tree traversal, sub-millisecond.

**Redis cache as first layer:**

```
Key:   autocomplete:{prefix}
Value: JSON list of top-10 suggestions
TTL:   5 minutes
```

Before hitting the Trie, check Redis. Cache hit rate for common prefixes ("app", "goo", "the") will be extremely high — maybe 95%. Only misses (rare prefixes) reach the Trie.

**CDN caching for common prefixes:**

For prefixes of length ≤ 3 characters, results change slowly (daily). Cache these at the CDN edge with a 1-hour TTL. "app", "goo", "the" — thousands of users will type these and all get the CDN-cached response. Zero server load for these ultra-common prefixes.

---

### API Design

```
GET /v1/autocomplete?q=app&limit=10
  Response 200: {
    "suggestions": [
      { "query": "apple", "frequency": 9823000 },
      { "query": "application", "frequency": 4521000 },
      ...
    ]
  }

Headers:
  Cache-Control: public, max-age=300  (5 min cache at CDN/browser)
```

The client debounces keystrokes — doesn't fire a request for every character. Typically waits 100–200ms after the last keystroke before sending. This reduces server load by 50–80% since most users type quickly through short prefixes.

---

## Scale — What Breaks at 10x?

At 58,000 autocomplete requests/sec:

**Redis:** Each prefix lookup is a single GET. Redis handles 500K ops/sec. 58K requests → comfortable single Redis node, add replica for redundancy. Shard by prefix hash if needed.

**Trie in memory:** A Trie with 10M unique queries and top-10 pre-cached = roughly 2–5 GB in memory. This fits on a single server. Each autocomplete server holds a full copy of the Trie — no coordination needed between servers. Just load balance requests across them.

**Trie refresh:** When the daily Trie rebuild completes, push a refresh signal to all autocomplete servers. Each server downloads the new Trie from S3 and swaps atomically. Refresh takes ~30 seconds. During refresh, the old Trie continues serving — no downtime.

**Write path (new trending queries):** If a breaking news event makes "earthquake 2026" suddenly trend, it takes until the next hourly Spark job to propagate. For faster updates, add a "real-time trending" layer: a sliding window counter in Redis for the last 15 minutes, injected into results alongside Trie suggestions. Hot queries bubble up in near-real-time without waiting for the batch job.

---

## Trade-offs

**Trie vs Elasticsearch for prefix search:** Elasticsearch with prefix queries is simpler to implement and handles fuzzy matching and multi-language. But at 58K req/sec, Elasticsearch latency (10–50ms per query) doesn't meet the sub-100ms budget when combined with network hops. In-memory Trie is sub-millisecond. Trade-off: Trie is a custom data structure requiring more engineering effort, but is orders of magnitude faster. For a global search product, worth it.

**Batch vs real-time frequency computation:** Batch (hourly/daily) means trending queries take time to appear. Real-time streaming (Flink on Kafka) can propagate new queries in seconds but is operationally complex. The hybrid approach — batch for the Trie, Redis sliding window for real-time trending — gives the best of both at manageable complexity.

**Top-K selection: exact vs approximate:** Maintaining exact top-10 for every prefix globally is expensive. For the long tail of rare prefixes, approximate counts (using count-min sketch) are fine. Users typing "xylop" don't need perfectly accurate suggestions — they need something reasonable. Save exact counting for high-frequency prefixes.

---

## Cross-Questions

**How do you handle typos — "gogle" should suggest "google"?**

The Trie approach doesn't handle typos — it's purely prefix-based. For fuzzy matching, layer a separate system: BK-tree (a metric tree for edit distance queries) or Elasticsearch with fuzzy queries. When the Trie returns no or few results for a prefix, fall back to the fuzzy layer. This is exactly how Google works — straight prefix match first, fuzzy fallback if needed. The UI shows "Did you mean: google?"

**How do you filter out offensive or illegal query suggestions?**

Maintain a blocklist of banned terms in Redis (a Set). After the Trie returns top-10, filter out any suggestions in the blocklist before returning to the client. Blocklist is small (maybe 100K terms), Redis lookup is O(1). Updates to the blocklist are instant — no Trie rebuild needed. For legal compliance (GDPR right-to-be-forgotten), if a user's specific search query must be removed, add it to the blocklist and it immediately stops appearing in suggestions.

**How would you make suggestions personalized per user?**

Two approaches. Simple: inject the user's recent searches as top candidates before the global Trie results. Store the last 10 searches per user in Redis. Mix personal results with global trending using a weighted score. Complex: train a ranking model per user using their click-through history — for the same prefix, different users see different orderings based on their profile. Personal preferences are a separate model, but the infrastructure (Trie + Redis) remains the same.

**How do you handle Chinese or Arabic characters in the Trie?**

A standard Trie with ASCII characters uses a fixed 26-slot array per node. Unicode characters (Chinese: 50,000+ characters) can't use fixed arrays — use a HashMap per node instead. `children: HashMap<char, TrieNode>`. Memory per node increases (HashMap overhead vs fixed array), but the algorithm is the same. A Chinese character is just a unicode codepoint — the Trie handles it like any other character. For space efficiency, use a compressed Trie (Patricia Trie) that collapses single-child paths into one edge.

**What happens if the Trie server crashes?**

Each Trie server is stateless with respect to requests — the Trie is built from S3, not from request history. A crashed server is replaced by a new one that downloads the Trie from S3 on startup (takes ~30 seconds). During that 30 seconds, the load balancer routes to other healthy servers. Scale horizontally — run enough servers so losing one doesn't impact capacity. Redis cache also acts as a fallback if the Trie is temporarily unavailable — cached suggestions serve most requests while a server recovers.
