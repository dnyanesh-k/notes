# Q11: Design Semantic Search System

---

## Clarifying Questions

What are we searching over — documents, products, people, or code? The domain shapes the embedding model choice and indexing strategy significantly.

Are we replacing keyword search entirely, or augmenting it? Hybrid search (semantic + keyword) almost always outperforms either alone.

What's the scale — how many documents in the index, and how many search queries per second? And what's the latency requirement — sub-100ms for a search bar, or a few seconds for a batch pipeline?

Do we need to support filters alongside semantic search — e.g., "find documents about refunds that are from the last 30 days"? Pre-filtering before vector search, or post-filtering after, changes the architecture.

*Assuming: enterprise document search (legal contracts, internal wikis, support tickets), 10M documents, 1,000 queries/sec, sub-200ms latency, hybrid search (semantic + keyword), filter support by date/category.*

---

## Scope

I'll design the indexing pipeline and the query pipeline. The indexing pipeline processes raw documents into a searchable vector index. The query pipeline handles incoming search queries and returns ranked results. I'll cover the hybrid retrieval strategy and filtering.

---

## High Level Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INDEXING PIPELINE                              │
│                                                                     │
│  Documents  ──▶  Parser  ──▶  Chunker  ──▶  Dual Encoder           │
│  (S3, DB)         │                          │        │             │
│                   │                          ▼        ▼             │
│                   │                    Dense Index  Sparse Index    │
│                   │                    (Vector DB)  (Elasticsearch) │
│                   └──── Metadata ────▶  MySQL (filters, facets)     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      QUERY PIPELINE                                 │
│                                                                     │
│  User Query                                                         │
│      │                                                              │
│      ├──▶ Query Embedding ──▶ Vector DB (ANN) ──▶ top-K dense      │
│      │                                                   │          │
│      ├──▶ BM25 / TF-IDF ──▶ Elasticsearch ──▶ top-K sparse        │
│      │                                                   │          │
│      └──▶ Metadata filters (date range, category)       │          │
│                                                          ▼          │
│                                          Fusion (RRF or weighted)   │
│                                                          │           │
│                                          Re-ranker (cross-encoder)  │
│                                                          │           │
│                                          Top-10 results + snippets  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Deep Dive 1 — Why Hybrid Search?

**Dense (semantic) retrieval alone fails when:**
- User searches for a specific technical term: "PostgreSQL SKIP LOCKED" → embedding model might not understand it's a specific SQL clause
- Acronyms: "HIPAA compliance" — embedding might not distinguish from general compliance
- Exact product names, error codes, identifiers

**Sparse (keyword/BM25) retrieval alone fails when:**
- User doesn't use the exact words in the document: searching "cancel subscription" when the document says "terminate membership"
- Conceptual questions: "how to reduce latency" — doesn't match "performance optimization techniques"
- Typos: "refunds polcy" won't match "refund policy"

**Hybrid combines both strengths.** Dense handles semantics, sparse handles exact terms. The fusion algorithm merges the ranked lists.

**Reciprocal Rank Fusion (RRF):**

```
For each document d in either ranked list:
  rrf_score(d) = Σ 1 / (k + rank_in_list)
  
where k = 60 (empirically chosen constant)

Example:
  Doc A: rank 1 in dense, rank 5 in sparse
    → 1/(60+1) + 1/(60+5) = 0.01639 + 0.01538 = 0.03177

  Doc B: rank 3 in dense, rank 1 in sparse
    → 1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226
    
  Doc B wins despite being rank 3 in dense — its top sparse ranking compensates
```

RRF is parameter-free (no weights to tune) and robust. Alternative: weighted linear combination `α × dense_score + (1-α) × sparse_score` — requires tuning α on labeled data.

---

## Deep Dive 2 — Indexing at 10M Documents

### Vector Index (Dense)

```
Documents → chunks → embeddings → HNSW index

Index structure at 10M documents:
  Avg 5 chunks per document = 50M chunks
  384 dimensions × 4 bytes = 1,536 bytes per vector
  50M vectors × 1,536 bytes = 76.8 GB

Storage: sharded across 4 vector DB nodes (20 GB each with headroom)
HNSW parameters:
  M = 16 (connections per node — higher = better recall, more memory)
  ef_construction = 200 (index build quality — higher = slower build, better index)
  ef_search = 100 (search recall vs latency tradeoff — tune per latency SLA)
```

**HNSW recall vs latency:** At `ef_search=100`, recall@10 (fraction of true nearest neighbors returned) is ~0.95 at 5–10ms per query. At `ef_search=50`, recall drops to 0.90 but latency halves. This is a tunable parameter — start with 0.95 recall target and adjust.

### Elasticsearch for Sparse (BM25)

Elasticsearch maintains an inverted index natively. For 10M documents:
```
PUT /documents/_doc/{id}
{
  "text": "The refund policy applies to...",
  "title": "Refund Policy v2",
  "category": "legal",
  "created_at": "2026-01-15",
  "tenant_id": "org_xyz"
}
```

BM25 query:
```json
{
  "query": {
    "bool": {
      "must": { "match": { "text": "cancel subscription" } },
      "filter": [
        { "term": { "tenant_id": "org_xyz" } },
        { "range": { "created_at": { "gte": "2025-01-01" } } }
      ]
    }
  }
}
```

Filters are applied before scoring — only documents matching the filter are ranked. This is crucial for multi-tenant isolation and date-range filtering.

### Metadata Store (MySQL)

```sql
CREATE TABLE document_index (
    id              VARCHAR(36) PRIMARY KEY,
    tenant_id       VARCHAR(100) NOT NULL,
    title           VARCHAR(500),
    source_url      VARCHAR(1000),
    category        VARCHAR(100),
    author          VARCHAR(200),
    created_at      DATETIME NOT NULL,
    updated_at      DATETIME NOT NULL,
    chunk_count     INT,
    word_count      INT,
    INDEX idx_tenant_date (tenant_id, created_at DESC),
    INDEX idx_category (tenant_id, category)
);
```

---

## Deep Dive 3 — Query Pipeline Step by Step

```
1. User submits: "contracts with penalty clauses signed after 2024"

2. Query Analysis:
   - Extract filters: "signed after 2024" → created_at >= 2025-01-01
   - Core semantic query: "contracts with penalty clauses"

3. Parallel execution (both happen simultaneously):
   
   Thread A: Dense retrieval
   - Embed "contracts with penalty clauses" → 384-dim vector
   - Query vector DB: top-50 nearest neighbors
   - Apply post-filter: created_at >= 2025-01-01 (or pre-filter if supported)
   
   Thread B: Sparse retrieval  
   - BM25 query: "contracts penalty clauses"
   - Elasticsearch filter: created_at >= 2025-01-01, tenant_id = X
   - Returns: top-50 ranked documents

4. Fusion (RRF):
   - Merge two lists of 50 into one ranked list of unique documents
   - Score by RRF formula → top-20 candidates

5. Re-ranking:
   - Cross-encoder scores each of 20 candidates against original query
   - Re-sort by cross-encoder score → top-10

6. Snippet generation:
   - For each result, find the most relevant passage
   - Highlight query terms in the snippet
   - Return: document title, source, date, snippet, relevance score
```

Total latency: dense retrieval (10ms) ∥ sparse retrieval (20ms) → max 20ms + RRF (1ms) + re-ranking (50ms) + snippet (5ms) = ~76ms. Well within 200ms SLA.

---

### Snippet Extraction

After retrieving documents, finding the most relevant passage to show as a snippet:

```python
def extract_snippet(document_text: str, query: str, window: int = 150) -> str:
    # Find the sentence in the document most similar to the query
    sentences = split_into_sentences(document_text)
    sentence_embeddings = embedder.embed_batch(sentences)
    query_embedding = embedder.embed(query)
    
    similarities = cosine_similarity(query_embedding, sentence_embeddings)
    best_sentence_idx = argmax(similarities)
    
    # Return window of text around the best sentence
    start = max(0, best_sentence_idx - 1)
    end = min(len(sentences), best_sentence_idx + 2)
    snippet = " ".join(sentences[start:end])
    
    return highlight_terms(snippet, query)  # bold matching terms
```

---

## Scale — What Breaks at 10x?

At 10,000 queries/sec:

**Vector DB throughput:** HNSW query is CPU-bound. At 10ms per query, one CPU core handles 100 queries/sec. Need 100 cores for 10K QPS. With vector DB sharding across 4 nodes, each needs 25 cores — 32-core instances are reasonable. Horizontal scaling: add more nodes, route by query hash.

**Elasticsearch:** Designed for thousands of queries/sec. At 10K QPS, distribute across 6–10 data nodes. Each shard handles a portion of the index. For 10M documents across 5 primary shards, each shard has 2M documents — fast BM25 queries (< 10ms).

**Embedding the query:** 384 dimensions, one forward pass of MiniLM ≈ 5ms on CPU, 1ms on GPU. At 10K QPS, need 10,000 × 5ms = 50 CPU-seconds per second = 50 cores dedicated to query embedding. Better: GPU inference server with batching — batch 32 queries, embed in 5ms → 6,400 QPS per GPU. Two GPUs handle 10K QPS with headroom.

**Re-ranking is the bottleneck:** Cross-encoder at 50ms per batch of 20 candidates. At 10K QPS × 50ms = 500 CPU-seconds/sec = 500 cores just for re-ranking. Solution: lighter re-ranker model (use a smaller cross-encoder, sacrifice small amount of quality), or skip re-ranking for simple queries (route only complex queries through re-ranker based on a query classifier).

---

## Trade-offs

**Pre-filtering vs post-filtering in vector search:** Pre-filtering (only search within the filtered subset) is more accurate but requires the vector DB to support it natively (Pinecone and Weaviate do). Post-filtering (search all vectors, then filter results) might not return top-K after filtering if many results are filtered out. For large filter sets (e.g., filter to 1M of 10M docs), pre-filtering is correct. For small filter sets (filter to 100K of 10M), post-filtering with over-fetching (retrieve top-200, filter, return top-10) works.

**Chunk-level vs document-level retrieval:** We retrieve at the chunk level (specific passage) and return at the document level (full document with snippet). This is the correct architecture — ranking on chunk-level relevance gives more precise results, but the user navigates to the full document. Return the chunk text as snippet + link to the full document.

**Real-time index updates vs batch:** Embedding a new document takes 0.5–5 seconds. For real-time search (document immediately searchable after upload), trigger embedding asynchronously: document saved → Kafka event → embedding worker → upsert to vector DB → available for search within seconds. For batch pipelines, process overnight with Spark. Real-time is almost always required for user-facing search.

---

## Cross-Questions

**How do you measure if semantic search is actually better than keyword search?**

Online metrics: click-through rate (users click results from semantic search vs keyword search), dwell time (did they find what they wanted?), zero-result rate (fewer dead ends). Offline metrics: on a labeled dataset of query-document pairs, measure precision@K and NDCG (Normalized Discounted Cumulative Gain — a ranking quality metric). Run A/B test: 50% of users get keyword search, 50% get hybrid. Measure both online and offline metrics. NDCG is the standard academic metric for search quality.

**How do you handle queries in multiple languages?**

Use a multilingual embedding model (`multilingual-e5-large`, `paraphrase-multilingual-mpnet-base-v2`). These models embed text from 100+ languages into the same vector space — a French query can match an English document if they're semantically similar. Documents are indexed with their language detected and stored as metadata. For keyword search, configure Elasticsearch with language-specific analyzers (different stemmers for French vs English). The fusion layer is language-agnostic — it merges ranked lists regardless of language.

**How do you prevent stale search results after a document is deleted?**

Soft delete: mark document as deleted in MySQL. During result hydration (fetching document metadata for display), filter out deleted documents. The vector and Elasticsearch indexes still contain the deleted document's embeddings but they're hidden at the presentation layer. Hard delete: publish a `doc.deleted` event to Kafka. The indexer removes the embedding from the vector DB by document ID and deletes from Elasticsearch. Vector deletion in HNSW is implemented as marking the node inactive (HNSW doesn't physically remove nodes — it marks them as deleted and skips them during search). Periodic index compaction rebuilds the index without deleted nodes.

**How would you implement search within a specific section of a document (e.g., search only the "clauses" section of a contract)?**

Document-structure-aware chunking. When parsing a legal contract, identify sections (Preamble, Definitions, Terms, Penalty Clauses) using heading detection or a structural parser. Store `section_type` as metadata on each chunk. At search time, filter: `WHERE section_type = 'penalty_clause'`. This requires the document parser to understand document structure, which is more complex than simple text chunking but dramatically improves precision for structured documents.

**How would you rank results by both relevance and recency?**

Two-dimensional ranking. Pure semantic relevance doesn't account for document age — a highly relevant document from 5 years ago might be outdated. Introduce a recency decay factor:

```
final_score = relevance_score × recency_factor
recency_factor = e^(-λ × days_old)
  where λ = 0.01 (tune based on how fast your domain ages)
  
A document 100 days old: recency = e^(-0.01 × 100) = 0.368
A document 10 days old:  recency = e^(-0.01 × 10)  = 0.905
```

Apply this after re-ranking. The decay rate λ depends on the domain — news needs aggressive decay (λ=0.1), legal contracts need mild decay (λ=0.001). Expose λ as a configurable parameter in the search API.
