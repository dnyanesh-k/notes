# Q11: Design Semantic Search System

---

## Introduction

Semantic search is a search system that finds results based on the meaning of a query rather than matching exact keywords. Traditional keyword search looks for the literal words in the query — if a user searches "car repair," only documents containing those exact words rank highly. Semantic search understands that "auto maintenance," "vehicle servicing," and "fixing my Toyota" all express the same intent and returns relevant results for all of them.

The technology that makes this possible is **vector embeddings**. A trained neural model converts text — both the documents and the query — into high-dimensional numerical vectors that capture semantic meaning. Documents with similar meaning produce vectors that are close to each other in this vector space. Semantic search works by converting the user's query into a vector and finding the stored document vectors nearest to it, a process called approximate nearest neighbor (ANN) search.

The ingestion side involves taking a corpus of documents, splitting them into meaningful chunks, passing each chunk through an embedding model, and storing the resulting vectors in a vector database like Pinecone, Weaviate, Qdrant, or pgvector. The embedding model must be chosen carefully — it determines what "similarity" means. A general-purpose model might not capture the nuances of medical or legal language as well as a domain-specific one.

At query time, the user's input is embedded using the same model, and the vector database returns the top-K most similar vectors using ANN algorithms like HNSW or IVF-Flat. These approximate algorithms trade a small amount of accuracy for a large improvement in query speed, making million-scale search feasible in under 100 milliseconds.

Hybrid search — combining semantic similarity with keyword (BM25) ranking using a re-ranker — typically outperforms either approach alone. Metadata filtering (restrict results to a specific date range, category, or tenant) is a critical production requirement, especially in multi-tenant enterprise deployments.

---

## How to Approach This in an Interview

Semantic search is RAG without the LLM generation step — you're returning ranked documents instead of generated answers. The core challenge is hybrid retrieval: combining dense (semantic) search with sparse (keyword) search via Reciprocal Rank Fusion. Know RRF inside-out. Also understand why HNSW parameters matter and how filtering interacts with vector search.

---

## Clarifying Questions

**1. What are we searching over?**

"Are we searching documents, products, people, or code? The choice of embedding model depends heavily on the domain."

*Why this matters:* A general-purpose embedding model (MiniLM) works for enterprise documents. Code search needs a code-specific model (CodeBERT). Product search needs product-specific features (color, category, price as vector components).

**2. Hybrid search or semantic only?**

"Should we augment keyword search with semantic understanding, or replace keyword search entirely?"

*Why this matters:* Pure semantic search misses exact technical terms. Pure keyword search misses synonyms and paraphrases. Hybrid almost always wins.

**3. Scale and latency?**

"How many documents in the index? How many searches per second? What's the max acceptable latency?"

*Why this matters:* 100K docs = single-node vector DB fine. 100M docs = sharded cluster with ANN index tuning.

**4. Filters?**

"Can users filter by date, category, author, etc.? How should filters interact with semantic search?"

*Why this matters:* Pre-filtering (narrow corpus before search) vs post-filtering (search then filter) changes the architecture and affects recall significantly.

### Assumptions

```
- Enterprise document search (legal contracts, internal wikis, support tickets)
- 10M documents, 1,000 queries/sec, sub-200ms latency
- Hybrid search: dense (semantic) + sparse (BM25/keyword)
- Filters: date range, category, author, document type
- Pre-filtering by tenant (multi-tenant, strict isolation)
```

---

## Back-of-Envelope Math

```
10M documents × 5 chunks/doc average = 50M vectors
Vector dimensions: 384 floats × 4 bytes = 1,536 bytes/vector
Storage: 50M × 1,536 bytes = 76.8 GB → needs 4 nodes × 20 GB each

Query latency budget (200ms):
  Query embedding: 10ms (GPU)
  Dense ANN search: 15ms (HNSW)
  Sparse BM25 search: 20ms (Elasticsearch)
  (Dense + sparse in parallel: max 20ms)
  RRF fusion: 2ms
  Cross-encoder reranking: 80ms (top-20 candidates)
  Snippet extraction: 10ms
  Total: ~122ms ← within 200ms budget

Elasticsearch for 10M documents:
  10M × 1KB text average = 10 GB raw text
  BM25 inverted index: ~3-5x raw text = 30-50 GB
  5-shard Elasticsearch cluster handles this easily
```

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
│                   │                    (Vector DB:  (Elasticsearch: │
│                   │                     HNSW)        BM25)          │
│                   └──── Metadata ────▶  MySQL (filters, facets)     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      QUERY PIPELINE                                 │
│                                                                     │
│  User Query  ──▶  Query Analysis                                    │
│                    │             │                                   │
│                    ▼             ▼                                   │
│              Embed query    Extract filters                         │
│                    │                                                 │
│         ┌──────────┴──────────────────────────┐                    │
│         ▼ (parallel)                          ▼ (parallel)          │
│   Dense ANN search              Sparse BM25 search                  │
│   (Vector DB, top-50)           (Elasticsearch, top-50)            │
│         │                                     │                     │
│         └──────────────┬──────────────────────┘                    │
│                         ▼                                           │
│                   RRF Fusion → top-20                              │
│                         │                                           │
│                   Cross-encoder reranking → top-10                 │
│                         │                                           │
│                   Snippet extraction + highlighting                 │
│                         │                                           │
│                   Return results                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Why Hybrid Search?

**Dense-only search fails for:**

```
Query: "PostgreSQL SKIP LOCKED clause"
Embedding model sees this as generic text about databases.
Might return results about "database locking mechanisms" or "MySQL transactions"
Missing: the specific Postgres syntax is an exact match need

Query: "HIPAA 45 CFR 164.512"
Regulatory citation — embedding might not understand this specific code
Returns generic HIPAA documents
Missing: the exact regulation document that cites this specific section
```

**Sparse-only (BM25) fails for:**

```
Query: "cancel my subscription"
Document says: "terminate your membership" or "end your plan"
BM25 finds nothing — different words, same meaning

Query: "fix slow app"
Documents say: "performance optimization techniques", "latency reduction strategies"
BM25 misses these — no word overlap
```

**Hybrid captures both:**

Dense handles semantic similarity ("cancel" ↔ "terminate"). Sparse handles exact term matching ("SKIP LOCKED" ↔ "SKIP LOCKED"). The fusion algorithm combines both rankings.

---

## Reciprocal Rank Fusion (RRF) — Explained from Scratch

RRF is the algorithm for merging two ranked lists into one. It's parameter-free and empirically robust.

**The intuition:**

A document that appears as rank 1 in the dense list AND rank 1 in the sparse list should score very highly. A document that appears at rank 50 in dense and rank 50 in sparse should score poorly. RRF encodes this with a formula that gives high weight to high ranks.

**The formula:**

```
For each document d that appears in either or both ranked lists:

  RRF_score(d) = Σ  1 / (k + rank_i(d))
                over all lists i where d appears

where k = 60 (a constant — empirically found to work well)
```

**Why k = 60?**

The k constant prevents the formula from being too extreme for top-ranked documents. Without k, rank 1 would give score 1.0, rank 2 would give 0.5, rank 3 = 0.33 — the scores decay very rapidly, making rank 2 worth only 50% of rank 1. With k=60, rank 1 = 1/(60+1) = 0.0164, rank 2 = 1/(60+2) = 0.0161, rank 61 = 1/(60+61) = 0.0083. More graceful decay.

**Worked example:**

```
Dense search (semantic) results: [DocA, DocB, DocC, DocD, DocE, ...]
Sparse search (BM25) results:    [DocC, DocA, DocF, DocB, DocG, ...]

RRF calculation:
                Dense rank  Sparse rank   RRF score
DocA:              1           2          1/(60+1) + 1/(60+2) = 0.01639 + 0.01613 = 0.03252
DocB:              2           4          1/(60+2) + 1/(60+4) = 0.01613 + 0.01563 = 0.03176
DocC:              3           1          1/(60+3) + 1/(60+1) = 0.01587 + 0.01639 = 0.03226
DocD:              4          N/A         1/(60+4) + 0        = 0.01563 + 0       = 0.01563
DocF:             N/A          3          0 + 1/(60+3)        = 0 + 0.01587       = 0.01587

Final ranking:
  1. DocA: 0.03252 (top-2 in both lists)
  2. DocC: 0.03226 (top-3 in both, rank 1 in sparse compensates)
  3. DocB: 0.03176 (top-4 in both)
  4. DocF: 0.01587 (only in sparse, but rank 3)
  5. DocD: 0.01563 (only in dense, rank 4)
```

DocA wins because it's in the top of both lists. DocC is close because its rank-1 in sparse compensates for rank-3 in dense. Documents appearing in only one list still get ranked based on that list.

**Implementation:**

```python
def reciprocal_rank_fusion(dense_results: list[dict], 
                           sparse_results: list[dict], 
                           k: int = 60) -> list[dict]:
    """
    dense_results: list of {id, metadata} in rank order
    sparse_results: list of {id, metadata} in rank order
    Returns: merged list ordered by RRF score
    """
    scores: dict[str, float] = defaultdict(float)
    metadata: dict[str, dict] = {}
    
    # Score from dense results
    for rank, doc in enumerate(dense_results, start=1):
        doc_id = doc['id']
        scores[doc_id] += 1.0 / (k + rank)
        metadata[doc_id] = doc['metadata']
    
    # Score from sparse results
    for rank, doc in enumerate(sparse_results, start=1):
        doc_id = doc['id']
        scores[doc_id] += 1.0 / (k + rank)
        if doc_id not in metadata:
            metadata[doc_id] = doc['metadata']
    
    # Sort by RRF score (highest first)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {'id': doc_id, 'rrf_score': score, 'metadata': metadata[doc_id]}
        for doc_id, score in ranked
    ]
```

---

## Indexing Pipeline

### Vector Index (Dense)

```python
# Build HNSW index in Pinecone (or Weaviate, Qdrant, pgvector)
def index_document(doc: Document, tenant_id: str):
    chunks = chunker.chunk(doc.text)
    embeddings = embedder.embed_batch([c.text for c in chunks])
    
    vectors = [
        {
            "id": f"{doc.id}_chunk_{i}",
            "values": embedding,
            "metadata": {
                "tenant_id": tenant_id,          # MUST include for filtering
                "doc_id": doc.id,
                "chunk_index": i,
                "text": chunk.text,               # store text for retrieval
                "title": doc.title,
                "source_url": doc.url,
                "created_at": doc.created_at.isoformat(),
                "category": doc.category,         # for category filters
                "author": doc.author              # for author filters
            }
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
    ]
    
    # Upsert (update or insert) — safe for re-indexing
    pinecone_index.upsert(vectors=vectors, namespace=tenant_id)
```

**HNSW parameters explained:**

```
M = 16: Each node connects to 16 nearest neighbors during index construction.
  Higher M → better recall but more memory (each connection is ~8 bytes)
  M=16: standard choice, good recall, reasonable memory
  M=64: high-quality index but 4x more memory for graph structure

ef_construction = 200: During construction, consider 200 candidates per node.
  Higher → better index quality but slower build time
  ef_construction=200: good quality, ~2x slower than ef_construction=100

ef_search = 100: During search, explore 100 candidates.
  Higher → better recall but slower search
  ef_search=100: ~95% recall at ~15ms
  ef_search=50:  ~90% recall at ~8ms
  Trade-off: tune based on latency budget
```

### Elasticsearch for Sparse (BM25)

```python
# Index document in Elasticsearch
es.index(
    index="documents",
    id=doc.id,
    body={
        "text": doc.text,
        "title": doc.title,
        "tenant_id": tenant_id,
        "category": doc.category,
        "author": doc.author,
        "created_at": doc.created_at.isoformat()
    }
)

# BM25 search query
def bm25_search(query: str, tenant_id: str, 
                date_from: Optional[str], 
                category: Optional[str],
                top_k: int = 50) -> list[dict]:
    
    must_filters = [
        {"term": {"tenant_id": tenant_id}},  # ALWAYS filter by tenant
    ]
    if date_from:
        must_filters.append({"range": {"created_at": {"gte": date_from}}})
    if category:
        must_filters.append({"term": {"category": category}})
    
    result = es.search(
        index="documents",
        body={
            "query": {
                "bool": {
                    "must": {"match": {"text": query}},  # BM25 scoring on text
                    "filter": must_filters                 # exact filters, no scoring
                }
            },
            "size": top_k
        }
    )
    
    return [
        {"id": hit["_id"], "metadata": hit["_source"], "score": hit["_score"]}
        for hit in result["hits"]["hits"]
    ]
```

**Why are filters in `filter` clause, not `must`?**

`must` contributes to BM25 score calculation. `filter` applies exact matching without affecting scores, and Elasticsearch caches filter results. Using filters for tenant_id, date, and category:
1. Doesn't dilute the relevance score (only text matching determines ranking)
2. Benefits from Elasticsearch's filter cache (repeated filter queries are near-instant)
3. Correct semantic: these are hard constraints, not relevance signals

---

## Query Pipeline — Step by Step

```python
async def search(query: str, tenant_id: str, 
                 date_from: Optional[str] = None,
                 category: Optional[str] = None,
                 top_k: int = 10) -> list[SearchResult]:
    
    # Step 1: Query Analysis
    # Extract explicit filters from query: "contracts signed after 2024"
    filters = extract_filters_from_query(query)
    # → { date_from: "2024-01-01" } (extracted and removed from query)
    
    semantic_query = remove_filter_phrases(query)  
    # → "contracts with penalty clauses"
    
    # Merge extracted filters with explicit filters
    date_from = date_from or filters.get("date_from")
    category = category or filters.get("category")
    
    # Step 2: Parallel retrieval
    dense_task = asyncio.create_task(
        dense_search(semantic_query, tenant_id, date_from, category, top_k=50)
    )
    sparse_task = asyncio.create_task(
        bm25_search(semantic_query, tenant_id, date_from, category, top_k=50)
    )
    
    dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)
    # Both complete in parallel: max of 15ms + 20ms = 20ms total
    
    # Step 3: RRF Fusion
    fused = reciprocal_rank_fusion(dense_results, sparse_results, k=60)
    candidates = fused[:20]  # top-20 for reranking
    
    # Step 4: Cross-encoder reranking
    reranked = cross_encoder_rerank(semantic_query, candidates, top_k=top_k)
    
    # Step 5: Snippet extraction
    results = []
    for doc in reranked:
        snippet = extract_best_snippet(doc['metadata']['text'], semantic_query)
        results.append(SearchResult(
            id=doc['id'],
            title=doc['metadata']['title'],
            source_url=doc['metadata']['source_url'],
            snippet=snippet,
            relevance_score=doc['cross_encoder_score'],
            created_at=doc['metadata']['created_at'],
            category=doc['metadata']['category']
        ))
    
    return results
```

---

## Snippet Extraction

After finding relevant documents, show the most relevant passage as a preview:

```python
def extract_best_snippet(document_text: str, query: str, 
                          window_sentences: int = 3) -> str:
    """Find the most relevant passage in the document for the query."""
    
    sentences = split_into_sentences(document_text)
    
    if not sentences:
        return document_text[:300]
    
    # Embed query and all sentences
    query_embedding = embedder.embed(query)
    sentence_embeddings = embedder.embed_batch(sentences)
    
    # Find sentence most similar to query
    similarities = [
        cosine_similarity(query_embedding, sent_emb) 
        for sent_emb in sentence_embeddings
    ]
    best_idx = max(range(len(similarities)), key=lambda i: similarities[i])
    
    # Extract window around best sentence
    start = max(0, best_idx - 1)
    end = min(len(sentences), best_idx + window_sentences)
    snippet = ' '.join(sentences[start:end])
    
    # Highlight query terms
    snippet = highlight_query_terms(snippet, query)
    
    return snippet

def highlight_query_terms(text: str, query: str) -> str:
    """Bold the query terms in the snippet."""
    query_words = set(query.lower().split())
    highlighted = []
    
    for word in text.split():
        clean_word = word.lower().strip('.,!?;:')
        if clean_word in query_words:
            highlighted.append(f"**{word}**")
        else:
            highlighted.append(word)
    
    return ' '.join(highlighted)
```

---

## Scale — What Breaks at 10x?

10x = 10,000 queries/sec, 100M documents.

**Vector DB at 100M documents:**

```
100M docs × 5 chunks = 500M vectors
500M × 1,536 bytes = 768 GB storage

Sharding strategy:
  Shard by tenant_id (natural boundary for isolation)
  10 tenants × 10M docs each = 10 shards, one per tenant
  
  For a single very large tenant:
  Shard by document hash → 4 shards × 192 GB each
  Query all 4 shards in parallel, merge results
```

**Query embedding bottleneck:**

10K queries/sec × 10ms/GPU embedding = 100 GPU-seconds/sec = 100 GPU cores.

With batch inference: each GPU processes 32 queries simultaneously in one forward pass (5ms for the batch = 0.16ms per query). 10K queries / 32 = 313 batches/sec. At 5ms/batch, need 313 × 5ms = 1.5 GPU-seconds/sec = 2 A10G GPUs. Very manageable.

**Re-ranking bottleneck:**

Cross-encoder at 80ms per query (batch of 20). 10K queries/sec × 0.08 seconds = 800 CPU-seconds/sec = 800 CPU cores dedicated to re-ranking.

Solutions:
1. Lighter cross-encoder model (accept 5% quality drop, 3x speed gain)
2. Only re-rank when top dense+sparse results disagree significantly
3. Route simple keyword queries (high overlap between dense and sparse) directly without reranking

---

## Trade-offs

**Pre-filtering vs post-filtering for vector search:**

*Pre-filtering:* Before ANN search, narrow the corpus to only documents matching the filter (e.g., only documents from 2024). ANN search runs only within the filtered subset.

```
Before: 50M chunks
Filter to 2024: 5M chunks
ANN search on 5M: faster, results guaranteed to match filter
```

Problem: if the filter selects a very small subset (1K documents), HNSW performs poorly — it's designed for large indexes. Below ~10K vectors, exhaustive search may actually be faster.

*Post-filtering:* Run ANN on full 50M vectors, then filter results.

```
ANN returns top-50 from 50M
Filter to 2024: might return only 5 results (not enough)
```

Problem: over-fetching required. Retrieve top-200, filter, hope enough remain.

**Best practice:** Use pre-filtering for large filter sets (filtering to > 100K documents). Use post-filtering with over-fetching for small filter sets. Vector DBs like Qdrant and Weaviate support hybrid pre/post-filtering based on selectivity estimation.

**Chunk-level retrieval vs document-level:**

We retrieve at chunk level (specific passage), rank by relevance, but return the full document with the chunk as a snippet. This gives:
- Precise relevance ranking (chunk-level matching is more accurate than document-level)
- Useful result display (users navigate to the full document)
- Snippet from the most relevant chunk (guides users to the right part)

---

## Cross-Questions

**Q: How do you measure if semantic search is actually better than keyword search?**

**Offline evaluation (before deployment):**

Label 500 query-document pairs as relevant/not-relevant. For each query, measure:

- **Precision@K:** Of top K results, what fraction is relevant? (accuracy)
- **Recall@K:** Of all relevant documents, what fraction is in top K? (coverage)
- **NDCG@K** (Normalized Discounted Cumulative Gain): Rewards highly relevant results ranked higher. Standard academic metric for information retrieval.

```python
def ndcg_at_k(ranked_docs: list[str], relevant_docs: dict[str, int], k: int) -> float:
    """relevant_docs: {doc_id: relevance_score (0-3)}"""
    dcg = sum(
        relevant_docs.get(doc_id, 0) / math.log2(rank + 2)
        for rank, doc_id in enumerate(ranked_docs[:k])
    )
    ideal_dcg = sum(
        score / math.log2(rank + 2)
        for rank, score in enumerate(sorted(relevant_docs.values(), reverse=True)[:k])
    )
    return dcg / ideal_dcg if ideal_dcg > 0 else 0
```

**Online evaluation (A/B test after deployment):**

Split users 50/50. Group A gets keyword search, Group B gets hybrid. Measure:
- Click-through rate (do users click on results?)
- Dwell time (how long do they spend on the clicked result?)
- Zero-result rate (how often does search return nothing?)
- Follow-up queries (do users refine their search? suggests first result wasn't good)

**Q: How do you handle multilingual documents?**

Use a multilingual embedding model:

```python
# multilingual-e5-large: supports 100+ languages, same vector space
# A French query can match an English document
from fastembed import TextEmbedding
model = TextEmbedding("intfloat/multilingual-e5-large")

# Embed French query: "politique de remboursement"
# Embed English doc: "refund policy"
# Cosine similarity: ~0.87 (high — they mean the same thing)
```

For BM25: configure Elasticsearch with language-specific analyzers (French uses different stemming than English: "remboursements" → "rembours", "refunds" → "refund").

Multi-language RRF works naturally — dense vectors are in a shared multilingual space, BM25 handles language-specific term matching. Results from both are RRF-fused regardless of language.

**Q: How do you rank results by both relevance AND recency?**

After re-ranking by cross-encoder, apply a recency decay multiplier:

```python
def apply_recency_decay(results: list[dict], decay_rate: float = 0.01) -> list[dict]:
    """
    decay_rate: how fast relevance decays with age
    - News: 0.1 (aggressive decay, last week matters, last month doesn't)
    - Legal contracts: 0.001 (slow decay, 5-year-old contract still relevant)
    - Technical docs: 0.01 (moderate, outdated docs less relevant but not ignored)
    """
    today = datetime.now()
    
    for result in results:
        doc_date = datetime.fromisoformat(result['metadata']['created_at'])
        days_old = (today - doc_date).days
        
        # Exponential decay: e^(-decay_rate × days_old)
        # At 0 days: factor = 1.0 (full relevance)
        # At 30 days (decay=0.01): factor = e^(-0.3) = 0.74
        # At 365 days (decay=0.01): factor = e^(-3.65) = 0.026
        recency_factor = math.exp(-decay_rate * days_old)
        
        result['final_score'] = result['cross_encoder_score'] * recency_factor
    
    return sorted(results, key=lambda r: r['final_score'], reverse=True)
```

Expose `decay_rate` as a parameter — different use cases need different rates. Let the UI offer "Recent" vs "Most Relevant" toggle that changes the decay rate.
