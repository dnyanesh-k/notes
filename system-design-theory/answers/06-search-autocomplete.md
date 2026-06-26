# Q6: Design Search Autocomplete (Google Search Bar)

---

## Introduction

Search autocomplete is the feature that suggests completions as a user types into a search box. Google shows query suggestions after every keystroke, e-commerce platforms suggest product names, and IDEs suggest code completions. The system must return relevant suggestions in under 100 milliseconds — fast enough that the user perceives it as instantaneous and the suggestions keep up with their typing speed.

The core data structure for autocomplete is the **trie** (prefix tree). A trie stores strings character by character, where each node represents a prefix and each path from root to a leaf represents a complete word or phrase. Given a prefix, traversing the trie to that node and collecting all leaf descendants gives all matching completions. The challenge is that a naive trie traversal can be slow at scale when there are billions of queries in the tree.

In production, the trie is enhanced with popularity scores at each node so the system can return the top-K most searched completions for a given prefix without scanning every match. This avoids sorting large result sets on every request. The trie is typically prebuilt offline from query logs, indexed by frequency, and served from an in-memory cache or a dedicated low-latency data store.

At scale, a single trie covering all possible prefixes is too large to fit on one machine and too slow to rebuild frequently. The solution is to shard the trie — for example, different servers handle different first-letter prefixes — and to update it periodically (every hour or day) from aggregated search logs rather than in real time. This makes the suggestions slightly stale but keeps latency predictable.

Additional considerations include typeahead for multiple languages, handling typos and fuzzy matches, personalization (surfacing queries based on the user's own history), and filtering out offensive or banned terms from suggestions.

---

## How to Approach This in an Interview

Autocomplete has two separate systems: a **data pipeline** (computing the top suggestions) and a **serving layer** (returning them in <100ms as the user types). Interviewers often conflate the two — make sure you design both independently. The core data structure is a Trie, and you need to explain it from scratch with code.

---

## Clarifying Questions

**1. What are we autocompleting?**

"Is this global search queries (like Google's search bar), product names (Amazon), or user mentions (Twitter's @)?"

*Why this matters:* Global search queries change over time (trending). Product names are mostly static. User mentions are a lookup in a user table. The data source and freshness requirements differ.

**2. Global or personalized?**

"Should everyone see the same suggestions, or should past searches influence what I see?"

*Why this matters:* Global = one Trie for all users, much simpler. Personalized = per-user history stored and injected into results, adds significant storage and latency.

**3. Response time requirement?**

"Sub-100ms per keystroke? Every keystroke triggers a request as the user types."

*Why this matters:* At 10M users typing 5 searches/day × 10 keystrokes each = 500M autocomplete requests/day = 5,800/sec. Each response must arrive within 100ms or the suggestions feel laggy.

**4. Languages?**

"English only, or multilingual?"

*Why this matters:* ASCII Trie nodes have 26 slots (a-z). Unicode (Chinese: 50,000+ characters) needs a HashMap per node instead of a fixed array. Memory requirements change significantly.

### Assumptions

```
- Global trending search queries (not personalized to start)
- 10M DAU, each user does 5 searches/day, 10 keystrokes per search
  = 500M autocomplete requests/day = 5,800 requests/sec
- Return top 10 suggestions per prefix
- Sub-100ms response time requirement
- English only to start
- New trending queries should appear within 1 hour (near-real-time enough)
```

---

## Back-of-Envelope Math

```
Autocomplete requests: 5,800/sec
Suggestions per request: 10
Response size: 10 × ~30 bytes/query = ~300 bytes per response
Bandwidth: 5,800 × 300 bytes = ~1.7 MB/sec (trivial)

Data pipeline:
  10M users × 5 searches/day = 50M search queries/day
  = 578 search events/sec entering the pipeline
  → Need to aggregate and compute top suggestions from these

Trie size:
  Top 10M unique queries × ~50 bytes per query string = 500MB
  Plus top-10 pre-cached at each node: much larger
  → Could be 2-5 GB in-memory Trie — fits on one server
  → Each autocomplete server holds a full copy
```

---

## High Level Design

```
┌──────────┐  keystroke  ┌───────────────┐          ┌──────────────────────┐
│  Client  │────────────▶│  CDN / Cache  │          │   Data Pipeline      │
│ (browser │◀────────────│               │          │                      │
│  / app)  │  top-10     └──────┬────────┘          │  Search Logs (Kafka) │
└──────────┘                   │                    │          │            │
                                ▼                    │          ▼            │
                       ┌────────────────┐           │  Spark (hourly agg.) │
                       │ Autocomplete   │           │          │            │
                       │ Service        │           │          ▼            │
                       └────────┬───────┘           │  Query Freq Table    │
                                │                   │  (MySQL)             │
                    ┌───────────┼──────────┐        │          │            │
                    ▼           ▼          ▼        │          ▼            │
              ┌──────────┐ ┌────────┐ ┌───────┐    │  Trie Builder        │
              │   Trie   │ │ Redis  │ │       │    │  (batch, daily)      │
              │  (in     │ │(prefix │ │       │    └──────────────────────┘
              │  memory) │ │ cache) │ │       │             │
              └──────────┘ └────────┘ └───────┘   ◀─────────┘
                                                   (Trie loaded from S3
                                                    on startup/refresh)

Two completely separate systems:
  1. Data Pipeline: computes what the top suggestions are
  2. Serving Layer:  returns them fast
```

---

## The Core Data Structure: Trie (Prefix Tree)

**What is a Trie?**

A Trie (pronounced "try" — from retrieval) is a tree where each path from root to node spells out a string. It's specifically designed for prefix lookups.

**Visual example:**

```
Root
 ├── 'a'
 │    ├── 'p'
 │    │    ├── 'p' (node for "app")
 │    │    │    ├── 'l'
 │    │    │    │    └── 'e' (node for "apple") ← stores ["apple pie", "apple watch", ...]
 │    │    │    └── 's' (node for "apps")
 │    │    └── 'r'
 │    │         └── 'i' (node for "apri...")
 │    └── 'm'
 │         └── 'a' (node for "ama...")
 └── 'g'
      ├── 'o'
      │    └── 'o' (node for "goo")
      │         └── 'g' (node for "goog")
      │              └── 'l' (node for "googl")
      │                   └── 'e' (node for "google") ← ["google maps", "google drive"]
      └── 'i' (node for "gi...")
```

**Lookup:** User types "goo" → traverse: root → 'g' → 'o' → 'o' → return node's pre-cached top-10 suggestions. O(L) where L = length of typed prefix.

---

### Building the Trie from Scratch

```python
class TrieNode:
    def __init__(self):
        self.children: dict[str, TrieNode] = {}
        # For each character, pointer to the next node
        # Using dict instead of fixed array → supports Unicode too
        
        self.top_k: list[tuple[str, int]] = []
        # Pre-cached top-K (query, frequency) pairs for this prefix
        # WHY pre-cache? Explained below.

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, query: str, frequency: int):
        """Insert a query with its frequency into the Trie."""
        node = self.root
        for char in query:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            
            # Update this node's top-K list
            node.top_k = self._merge_into_topk(node.top_k, query, frequency, k=10)
    
    def _merge_into_topk(self, current_topk, query, freq, k):
        """Keep only the top K (query, frequency) pairs, sorted by frequency."""
        # Add new query
        combined = current_topk + [(query, freq)]
        # Sort by frequency descending, take top K
        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:k]
    
    def search(self, prefix: str) -> list[str]:
        """Return top-10 suggestions for a prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []  # no suggestions for this prefix
            node = node.children[char]
        
        # Return pre-cached top-K — O(1) after traversal
        return [query for query, freq in node.top_k]
```

**Worked example — building a small Trie:**

```
Insert "apple", frequency=9823000
Insert "application", frequency=4521000
Insert "app store", frequency=3100000

After inserting "apple" (freq=9M):
  Root → 'a' node: top_k = [("apple", 9M)]
  Root → 'a' → 'p' node: top_k = [("apple", 9M)]
  Root → 'a' → 'p' → 'p' node: top_k = [("apple", 9M)]
  Root → 'a' → 'p' → 'p' → 'l' node: top_k = [("apple", 9M)]
  Root → 'a' → 'p' → 'p' → 'l' → 'e' node: top_k = [("apple", 9M)]

After inserting "application" (freq=4.5M):
  'a' node: top_k = [("apple", 9M), ("application", 4.5M)]
  'a' → 'p' node: top_k = [("apple", 9M), ("application", 4.5M)]
  'a' → 'p' → 'p' node: top_k = [("apple", 9M), ("application", 4.5M)]
  (shared path 'a','p','p' gets both)
  'a' → 'p' → 'p' → 'l' node: only "apple" goes here (diverges at 'l' vs 'i')

User types "app":
  traverse root → 'a' → 'p' → 'p'
  Return node.top_k = ["apple", "application", "app store"]  ← pre-computed!
```

**Why pre-cache top-K at each node?**

Without pre-caching: for prefix "ap", traverse to that node, then DFS all descendants, collect all queries, sort by frequency. At 10M queries, the subtree under "ap" might have 1M entries — sorting takes hundreds of milliseconds. Way too slow for real-time serving.

With pre-caching: at build time, propagate top-K up the tree. The "ap" node already knows its top-10. Lookup is O(L) traverse + O(1) return. Total: sub-millisecond.

---

## Data Pipeline — How Suggestions Are Computed

The suggestions don't come from thin air — they come from real search queries that users have made.

**Step 1: Collect search queries**

Every time a user completes a search (not every keystroke — just when they hit Enter or tap a suggestion), log it to Kafka:

```
kafka.produce("search.completed", {
    "query": "apple watch series 10",
    "user_id": 12345,         # for personalization later
    "timestamp": 1687391823
})
```

Volume: 10M users × 5 searches/day = 50M search events/day = 578/sec.

**Step 2: Aggregate frequencies (Spark job, runs hourly)**

```python
# PySpark job reads last 7 days of queries from S3
# (Kafka streams are archived to S3 hourly)

df = spark.read.parquet("s3://search-logs/2026-06-*/")

# Count frequency of each query, weighted by recency
# Recent queries count more than week-old queries
# Use exponential decay: queries from today weight 7x more than 7 days ago

df_weighted = df.withColumn(
    "weight", 
    pow(0.5, (current_timestamp() - df.timestamp) / (7 * 86400))
    # half-life of 7 days: a 7-day-old query counts half as much
)

freq_df = (df_weighted
    .groupBy("query")
    .agg(sum("weight").alias("frequency_score"))
    .filter(col("frequency_score") > 10)     # filter out very rare queries
    .orderBy(col("frequency_score").desc())
)

# Write to MySQL
freq_df.write.jdbc(mysql_url, "query_frequencies", mode="overwrite")
```

Output: table of (query, frequency_score) pairs.

**Step 3: Build the Trie (daily batch job)**

```python
def build_trie() -> Trie:
    trie = Trie()
    
    # Read top-10M queries by frequency
    cursor = mysql.execute(
        "SELECT query, frequency_score FROM query_frequencies "
        "ORDER BY frequency_score DESC LIMIT 10000000"
    )
    
    for row in cursor:
        trie.insert(row.query, int(row.frequency_score))
    
    return trie

def deploy_trie(trie: Trie):
    # Serialize to disk
    with open("/tmp/trie.pkl", "wb") as f:
        pickle.dump(trie, f)
    
    # Upload to S3 (all autocomplete servers will download this)
    s3.upload("/tmp/trie.pkl", "s3://autocomplete-data/trie_latest.pkl")
    
    # Signal all serving instances to refresh
    redis.publish("trie_refresh", "s3://autocomplete-data/trie_latest.pkl")
```

**Step 4: Zero-downtime Trie refresh on serving instances**

```python
class AutocompleteServer:
    def __init__(self):
        self.active_trie = self.load_trie_from_s3()
        self.standby_trie = None
        
        # Listen for refresh signals
        redis.subscribe("trie_refresh", self.handle_refresh)
    
    def handle_refresh(self, new_trie_path: str):
        # Load new Trie into standby slot (non-blocking)
        self.standby_trie = self.load_trie_from_s3(new_trie_path)
        
        # Atomically swap (pointer swap, no lock needed in Python with GIL)
        self.active_trie, self.standby_trie = self.standby_trie, self.active_trie
        self.standby_trie = None
        
        # Zero downtime: old Trie served requests during load
        # Swap is instant
    
    def search(self, prefix: str) -> list[str]:
        return self.active_trie.search(prefix)
```

---

## Serving Layer

### Three Cache Layers

**Layer 1: CDN cache for short common prefixes**

For prefixes ≤ 3 characters ("app", "goo", "the", "how"), results barely change day to day. Cache at CDN edge with 1-hour TTL.

```
Client types "app" → CDN checks cache
CDN HIT: Return ["apple", "application", "app store", ...] from edge
Zero server load, < 5ms response

CDN MISS (rare): Forward to Autocomplete Service
```

**Layer 2: Redis cache for medium-length prefixes**

For prefixes that are too specific for CDN but still common:

```
Key:   autocomplete:{prefix}
Value: JSON array of top-10 suggestions
TTL:   5 minutes

redis.set("autocomplete:appl", json.dumps(["apple", "apple watch", ...]), ex=300)
```

**Layer 3: In-memory Trie (cache miss fallback)**

The Trie is loaded fully in-memory on each Autocomplete Service instance. A lookup for any prefix not in Redis takes < 1ms.

```
Lookup order:
1. CDN edge (for ≤ 3 char prefixes)
2. Redis (for any prefix, 5-min TTL)
3. In-memory Trie (sub-millisecond)
```

**Cache hit rate analysis:**

```
"app" (3 chars): hit rate ~99% (CDN caches it)
"appl" (4 chars): hit rate ~90% (Redis caches it)
"apple " (6 chars): hit rate ~60% (many users type this; cached)
"apple watc" (10 chars): hit rate ~20% (less common; may hit Trie)
"xyloph" (rare prefix): 0% (goes to Trie, still < 1ms)
```

### API Design

```
GET /v1/autocomplete?q=apple+w&limit=10

Query is debounced by client: wait 150ms after last keystroke before firing.
This means a user typing "apple " at normal speed fires ~1 request/second,
not one per character.

Response:
{
  "query": "apple w",
  "suggestions": [
    { "text": "apple watch", "type": "query" },
    { "text": "apple watch series 10", "type": "query" },
    { "text": "apple wwdc", "type": "query" },
    ...
  ]
}

Headers:
  Cache-Control: public, max-age=300
  → Browser and CDN can cache this response for 5 minutes
  → If you type the same prefix again in 5 minutes, the browser serves it
     locally without hitting our servers at all
```

**Client-side debouncing:**

```javascript
// Without debouncing: every keystroke = one API request
// "apple watch" = 11 characters = 11 requests

// With debouncing: only fire after user pauses 150ms
let debounceTimer = null;

function onKeyPress(event) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        fetchSuggestions(event.target.value);
    }, 150);
}

// A fast typist types "apple watch" in 0.5 seconds
// Debounce means maybe 2-3 requests instead of 11
// 70-80% reduction in server load with no noticeable UX degradation
```

---

## Scale — What Breaks at 10x?

10x = 58,000 autocomplete requests/sec.

**Trie in memory:** 2-5 GB per server. Load balancer distributes requests across 10 Autocomplete Service instances. Each holds a full Trie copy — no cross-server coordination needed. Adding servers is instant (download Trie from S3, start serving).

**Redis:** 58K requests/sec × 1 GET per request = 58K Redis ops/sec. Single Redis node handles 500K ops/sec — no problem. Add a replica for HA. No cluster needed at this scale.

**CDN:** Short prefixes (≤3 chars) have the highest request volume (more users type "app" than "application"). CDN absorbs these with very high hit rates. Server load is dominated by longer prefixes that miss CDN — these are the minority.

**Real-time trending (new bottleneck):** If a breaking news event makes "earthquake 2026" suddenly popular, it takes up to 1 hour for the Spark job to incorporate it. For faster trending: add a Redis sliding window counter that tracks query frequency in the last 15 minutes. Inject these real-time trending queries into results alongside Trie suggestions. "Earthquake 2026" appears in suggestions within minutes.

```python
def search_with_realtime(prefix: str) -> list[str]:
    # Get Trie suggestions (from Trie or Redis cache)
    trie_suggestions = trie.search(prefix)  # historical, daily
    
    # Get real-time trending that match prefix
    trending_key = f"trending:15min"
    trending = [q for q in redis.zrevrange(trending_key, 0, 50) 
                if q.startswith(prefix)][:5]
    
    # Merge: trending first (freshness), then Trie (historical frequency)
    seen = set()
    merged = []
    for q in trending + trie_suggestions:
        if q not in seen:
            merged.append(q)
            seen.add(q)
    
    return merged[:10]
```

---

## Trade-offs

**Trie vs Elasticsearch for autocomplete:**

| Aspect | In-memory Trie | Elasticsearch |
|--------|---------------|---------------|
| Latency | < 1ms | 10-50ms |
| Supports fuzzy (typos) | No | Yes |
| Infrastructure | Custom code | Managed service |
| Memory footprint | 2-5 GB | 20-50 GB cluster |
| Prefix lookup performance | O(L) | O(log N) BTree |

For a high-traffic global search bar where 100ms budget is tight, in-memory Trie wins on latency. For a product with fewer queries or where fuzzy matching is critical (user typos), Elasticsearch is simpler to operate.

**Batch vs real-time frequency computation:**

Batch (hourly Spark): simple, cheap, well-understood. Trending queries take up to 1 hour to appear.

Real-time streaming (Flink/Spark Streaming on Kafka): queries appear in suggestions within minutes. Operationally more complex, higher infrastructure cost.

The hybrid (batch Trie + real-time Redis overlay) gives 90% of the benefit at 20% of the complexity. Most products are fine with this.

---

## Cross-Questions

**Q: How do you handle typos? "gogle" should suggest "google".**

The Trie doesn't handle typos — it's exact prefix matching. For fuzzy matching:

**Approach 1: BK-tree (Burkhard-Keller tree)**

A BK-tree organizes strings by edit distance. For query "gogle", search for all strings with edit distance ≤ 1 from "gogle". This finds "google" (one insertion). BK-trees support this in O(n^k) where n = similar terms found, k = distance threshold.

```python
# BK-tree lookup for edit distance ≤ 1
# Returns: ["google", "gale", "gouge", ...]
fuzzy_matches = bk_tree.search("gogle", max_distance=1)
```

**Approach 2: Elasticsearch fuzzy query**

Elasticsearch has built-in fuzzy search: `{ "fuzzy": { "query": "gogle", "fuzziness": 1 } }`. Returns "google" among other 1-edit-distance matches. Slower than Trie (20-50ms) but no custom code.

**Approach 3: Google's approach**

Detect when Trie returns few or low-frequency results. Fall back to fuzzy lookup. Show "Did you mean: google?" UI element. The correction is a separate system; the Trie remains fast for correct queries.

**Q: How do you filter offensive or illegal terms from suggestions?**

Blocklist in Redis:

```python
def search_safe(prefix: str) -> list[str]:
    suggestions = trie.search(prefix)
    
    # O(1) lookup per suggestion
    return [s for s in suggestions 
            if not redis.sismember("blocklist:queries", s)]

# Adding to blocklist (instant, no Trie rebuild needed):
redis.sadd("blocklist:queries", "offensive_term_here")
```

The blocklist is applied at serving time, not at Trie build time. This means blocked terms can be added/removed instantly without rebuilding the Trie (which takes hours).

For GDPR right-to-be-forgotten: if a user's personal query must be removed from suggestions, add it to the blocklist. It stops appearing within milliseconds, even though it's still technically in the Trie.

**Q: How do you make suggestions personalized per user?**

Inject the user's recent searches as priority suggestions:

```python
def search_personalized(prefix: str, user_id: str) -> list[str]:
    # User's recent searches from Redis (last 10)
    recent = [q for q in redis.lrange(f"recent_searches:{user_id}", 0, 9)
              if q.startswith(prefix)]
    
    # Global Trie suggestions
    global_suggestions = trie.search(prefix)
    
    # Merge: personal first, then global (dedup)
    seen = set()
    merged = []
    for q in recent + global_suggestions:
        if q not in seen and len(merged) < 10:
            merged.append(q)
            seen.add(q)
    
    return merged

# Store user's search history:
redis.lpush(f"recent_searches:{user_id}", search_query)
redis.ltrim(f"recent_searches:{user_id}", 0, 9)  # keep last 10
redis.expire(f"recent_searches:{user_id}", 604800)  # 7 day TTL
```

Full ML-based personalization (rerank based on user's click history) is a separate model that runs as a post-processing step — same infrastructure, just add a reranking layer.

**Q: What if a Trie server crashes?**

The Trie is downloaded from S3, not generated from user requests. A replacement server:
1. Downloads `trie_latest.pkl` from S3 (~2 GB, takes ~15 seconds)
2. Loads it into memory
3. Registers with the load balancer
4. Starts serving

During the 15 seconds: load balancer routes to remaining healthy servers. 9 remaining servers absorb the load. Redis cache also serves most requests during recovery.

The Trie server is stateless with respect to user data — losing a server loses nothing. S3 is the durable source of truth.

**Q: How would you handle Chinese queries where each character is a different unicode codepoint?**

```python
class TrieNodeUnicode:
    def __init__(self):
        # dict instead of fixed 26-slot array
        # Handles any unicode character
        self.children: dict[str, 'TrieNodeUnicode'] = {}
        self.top_k: list[tuple[str, int]] = []

# "苹果手表" (Apple Watch in Chinese) is inserted character by character:
# '苹' → '果' → '手' → '表'
# Each Chinese character maps to one dict entry

# For very large character sets (Japanese, Thai), use a compressed Trie
# (Patricia Trie / Radix Tree) that collapses single-child paths:
# Instead of storing each character as a separate node,
# store "苹果手表" as one edge label when there's no branching
# Saves 75% of node count in practice
```

The algorithm is identical to ASCII — just the key type changes from `char` to `str` (unicode codepoint).
