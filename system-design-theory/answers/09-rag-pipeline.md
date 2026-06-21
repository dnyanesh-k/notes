# Q9: Design RAG Pipeline at Scale

> Direct from production experience — ARIA at CitiusTech is this system. Anchor every answer in that.

---

## Clarifying Questions

A few things to clarify. What's the knowledge base — structured documents like PDFs and Word files, or unstructured like web pages and wikis? The ingestion pipeline differs significantly.

How large is the knowledge base — hundreds of documents or millions? This determines whether we need approximate nearest neighbor search or can get away with exhaustive search.

What's the query latency requirement? Sub-second for a chat interface, or a few seconds for a batch report generation pipeline? Real-time RAG needs a very different serving architecture than batch.

Is this multi-tenant — multiple organizations with isolated knowledge bases? Or single-tenant? Multi-tenant adds data isolation complexity at the vector store level.

Do we need to handle knowledge base updates in real-time (document changed = results update immediately) or can there be a delay?

*Assuming: enterprise knowledge base (PDFs, Markdown, internal wikis), 100K documents, sub-2-second query latency, multi-tenant, knowledge base updates within minutes of document change.*

---

## Scope

I'll design two pipelines: the ingestion pipeline (document → chunks → embeddings → vector store) and the query pipeline (user question → retrieval → context packing → LLM → response). I'll include evaluation, caching, and guardrails since those are what separate a toy RAG from a production one.

---

## High Level Design

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                                   │
│                                                                              │
│  Documents  ──▶  Doc Loader  ──▶  Chunker  ──▶  Embedder  ──▶  Vector DB   │
│  (S3, Wiki,      (PDF, MD,        (fixed/         (MiniLM,       (Pinecone,  │
│   SharePoint)     HTML parser)    semantic)        OpenAI)        pgvector)  │
│                                       │                                      │
│                               Metadata Store (MySQL)                         │
│                               doc_id, chunk_id, source_url, updated_at      │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│                         QUERY PIPELINE                                       │
│                                                                              │
│  User Query                                                                  │
│      │                                                                       │
│      ▼                                                                       │
│  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐    ┌────────────┐ │
│  │ Query        │──▶ │ Semantic     │──▶ │ Re-ranker   │──▶ │ Context   │ │
│  │ Rewriter     │    │ Cache        │    │ (cross-     │    │ Packer    │ │
│  │ (optional)   │    │ (Redis)      │    │  encoder)   │    │           │ │
│  └──────────────┘    └──────┬───────┘    └─────────────┘    └─────┬─────┘ │
│                      miss   │                                       │       │
│                             ▼                                       ▼       │
│                      ┌──────────────┐                       ┌────────────┐ │
│                      │ Vector DB    │                       │    LLM     │ │
│                      │ ANN Search   │                       │  (GPT-4,   │ │
│                      └──────────────┘                       │   Claude)  │ │
│                                                              └─────┬──────┘ │
│                                                                    │        │
│                                                             ┌──────▼──────┐ │
│                                                             │  Guardrails │ │
│                                                             │  + Eval Log │ │
│                                                             └─────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Deep Dive 1 — Ingestion Pipeline

### Document Loading

Different document types need different parsers:
- PDF: PyMuPDF or pdfplumber (preserve text layout, handle multi-column)
- Word/DOCX: python-docx
- HTML/Wiki: BeautifulSoup (strip nav, footer; keep content)
- Markdown: direct text with frontmatter parsing

Each document gets a fingerprint (SHA256 of content). On re-ingestion, skip if fingerprint unchanged — no redundant embedding calls, which are expensive.

```python
class DocLoader:
    def load(self, source: str) -> Document:
        raw_text = self._parse(source)
        fingerprint = sha256(raw_text)
        if self.store.get_fingerprint(source) == fingerprint:
            return None  # unchanged, skip
        return Document(text=raw_text, source=source, fingerprint=fingerprint)
```

### Chunking — The Most Underestimated Step

How you chunk determines retrieval quality more than which embedding model you use. Poor chunking = poor answers, regardless of the model.

**Fixed-size chunking:** Split every N tokens (say 512) with M tokens overlap. Simple but cuts sentences mid-thought — the chunk boundary might split a key sentence, losing context.

**Sentence-based chunking:** Split at sentence boundaries. Chunks are semantically coherent. Variable size (50–200 tokens per sentence group). This is what ARIA uses.

**Semantic chunking:** Embed each sentence, measure embedding similarity between adjacent sentences. When similarity drops significantly, start a new chunk. Groups semantically related content together. More expensive but highest quality. Use for high-value knowledge bases.

**Chunk size trade-off:** Small chunks (128 tokens) → precise retrieval, but the chunk might not contain enough context for the LLM to answer. Large chunks (1024 tokens) → more context but retrieval is noisier (more irrelevant content in chunk). Empirically, 256–512 tokens works best for most enterprise knowledge bases. Add 10% overlap between chunks to prevent losing information at boundaries.

```
Document: "The refund policy applies to all purchases. Items must be returned within 30 days. 
           Digital products are non-refundable. For hardware..."

Chunk 1 (0-512 tokens, overlap with chunk 2):
  "The refund policy applies to all purchases. Items must be returned within 30 days.
   Digital products are non-refundable."

Chunk 2 (462-1024 tokens, starts in overlap):
  "Digital products are non-refundable. For hardware..."
```

### Embedding

Each chunk is converted to a dense vector (768–1536 dimensions) using an embedding model.

**Model choices:**
- `sentence-transformers/all-MiniLM-L6-v2`: fast (80ms/chunk), 384 dimensions, good for English
- `text-embedding-3-small` (OpenAI): 1536 dimensions, better quality, costs money per token
- `BAAI/bge-large-en-v1.5`: open source, near-OpenAI quality

For ARIA, we used MiniLM with a local fastembed server — zero API cost, ~80ms per chunk, runs on CPU. For production at scale, use GPU inference servers (TorchServe, Triton) for 10–50ms/chunk.

### Storing in Vector DB

Each embedding is stored with metadata:
```json
{
  "id": "chunk_abc123",
  "embedding": [0.023, -0.145, ...],  // 384 floats
  "metadata": {
    "tenant_id": "org_xyz",           // multi-tenancy isolation
    "doc_id": "doc_456",
    "source_url": "https://wiki/page",
    "chunk_index": 3,
    "text": "Digital products are non-refundable...",  // store text alongside
    "created_at": "2026-06-21"
  }
}
```

**Multi-tenancy in vector DB:** Use namespace per tenant (Pinecone namespaces) or metadata filter at query time (`where: { tenant_id: "org_xyz" }`). Never allow cross-tenant retrieval — enforce tenant filter on every query. This is directly from ARIA's design.

---

## Deep Dive 2 — Query Pipeline

### Step 1: Query Rewriting (optional but powerful)

The user's question is often vague. "What is the policy?" is ambiguous. A query rewriter uses the conversation history to make it specific: "What is Acme Corp's refund policy for digital products?"

```python
rewritten = llm.complete(f"""
Given this conversation:
{conversation_history}

Rewrite the latest question to be self-contained and specific:
{user_question}
""")
```

This dramatically improves retrieval for follow-up questions in multi-turn conversations.

### Step 2: Semantic Cache

Before hitting the vector DB, check if a semantically similar question was recently asked.

```python
query_embedding = embedder.embed(query)
cached = redis.vector_search(query_embedding, threshold=0.95)
if cached:
    return cached.response  # exact semantic match
```

Redis with RediSearch supports vector similarity search. Cache key = embedding, cache value = the full LLM response. If user asks "what is the return policy?" and 5 minutes ago someone asked "how do I return an item?" — same semantic meaning, return cached response. Cache TTL: 5 minutes for dynamic knowledge, 1 hour for static.

This cuts LLM API costs by 30–50% in production.

### Step 3: Vector Search — ANN (Approximate Nearest Neighbor)

```python
results = vector_db.query(
    vector=query_embedding,
    top_k=20,                          # retrieve more than needed
    filter={"tenant_id": tenant_id},   # multi-tenant isolation
    include_metadata=True
)
```

We retrieve top-20 candidates, not top-5. Why? Because the vector similarity isn't perfect — we'll re-rank the 20 down to 5. Retrieving more gives the re-ranker better material to work with.

**HNSW (Hierarchical Navigable Small World):** The indexing algorithm used by most vector DBs. It builds a multi-layer graph where each node connects to its nearest neighbors. Search traverses from the top layer (coarse) to the bottom layer (fine), finding the approximate nearest vectors in O(log N) instead of O(N). Trade-off: approximate (might miss the true nearest neighbor), but at 100K documents, HNSW is 1000x faster than exhaustive search with >95% recall.

### Step 4: Re-ranking with Cross-Encoder

The bi-encoder (embedding model) is fast but scores query and document independently — it doesn't look at the relationship between them. A cross-encoder takes the query and each document together and scores them jointly — much more accurate but 10–50x slower.

```python
# First pass: bi-encoder ANN → top-20 candidates
candidates = vector_db.query(query_embedding, top_k=20)

# Second pass: cross-encoder re-ranking → top-5
scores = cross_encoder.predict([(query, chunk.text) for chunk in candidates])
top_5 = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)[:5]
```

This two-stage retrieval (fast approximate + slow accurate) is how Google's search works. ARIA uses this pattern — initial retrieval with cosine similarity, re-ranking with a fine-tuned cross-encoder.

### Step 5: Context Packing

Take the top-5 retrieved chunks and build the LLM prompt:

```
SYSTEM: You are a helpful assistant for Acme Corp. Answer only based on the 
provided context. If the answer is not in the context, say "I don't know."

CONTEXT:
[1] Source: refund-policy.pdf, Page 3
    "Digital products are non-refundable once downloaded..."

[2] Source: terms-of-service.md
    "All returns must be initiated within 30 days of purchase..."

[3] ...

USER QUESTION: Can I return a downloaded ebook?

Answer:
```

**Grounding instruction** ("Answer only based on provided context") is the primary hallucination guard. The LLM cannot invent facts it doesn't have in context — it can only synthesize from what's provided.

**Context window management:** If 5 chunks × 512 tokens = 2,560 tokens, plus system prompt and question, still within GPT-4's 128K context window. For very large retrievals, summarize chunks that exceed budget: `summarize(chunk, max_tokens=200)`.

### Step 6: LLM Response + Guardrails

```python
response = llm.complete(prompt, max_tokens=500, temperature=0.1)
# Low temperature = more deterministic, less creative = better for factual Q&A

# Guardrails check:
if confidence_score(response, retrieved_chunks) < 0.6:
    response = "I found some related information but I'm not confident enough to answer."

# Log for eval:
eval_logger.log({
    "query": query,
    "retrieved_chunks": [c.id for c in top_5],
    "response": response,
    "retrieval_scores": scores,
    "latency_ms": elapsed
})
```

---

## Evaluation Framework — How to Know if RAG is Good

Without eval, you're flying blind. Production RAG must be measurable.

**Retrieval metrics:**
- Precision@K: of the K retrieved chunks, what fraction are actually relevant? (requires labeled dataset)
- Recall@K: of all relevant chunks in the KB, what fraction did we retrieve?
- MRR (Mean Reciprocal Rank): how high up in the ranked list is the first correct answer?

**Generation metrics:**
- Faithfulness: does the answer only use facts from the retrieved context? (LLM-as-judge)
- Answer relevance: does the answer actually address the question? (LLM-as-judge)
- Context relevance: are the retrieved chunks relevant to the question?

**LLM-as-judge pattern:**
```python
judge_prompt = f"""
Rate the faithfulness of this answer on a scale of 1-5.
Context: {retrieved_context}
Question: {question}
Answer: {answer}
Rating (1-5):
"""
score = llm.complete(judge_prompt)
```

ARIA ran 200 test cases nightly. If precision@5 dropped below 0.8 or faithfulness below 0.85, it triggered an alert before any human noticed degraded quality.

---

## Scale — What Breaks at 10x?

At 10x users, ~50K queries/sec:

**Embedding inference:** 50K queries × 384 dimensions × ~50ms per embedding = need ~2,500 CPU cores or 50 GPUs. GPU inference servers (Triton, TorchServe) reduce to 5ms/embedding. Batch queries together — instead of embedding one query at a time, batch 32 queries and embed in one GPU forward pass.

**Vector DB:** Pinecone and Weaviate handle millions of vectors. At 100K documents × 10 chunks each × 384 floats = 384M floats = ~1.5 GB. Trivial. At 100M documents, HNSW still scales with sharding. Scale by adding index shards.

**LLM cost is the dominant bottleneck:** GPT-4 at $0.01/1K tokens. A 3,000 token prompt + 500 token response = $0.035/query. At 50K queries/sec = 4.3B queries/day = $150M/day. This is obviously a problem. Solutions: semantic cache (hit 50% of queries from cache), use smaller models for simple questions (route to GPT-3.5 or Claude Haiku for straightforward factual lookups, reserve GPT-4 for complex queries), fine-tune a smaller model on your domain.

---

## Trade-offs

**Dense retrieval vs sparse (BM25) vs hybrid:** Dense embeddings understand semantics ("how do I cancel" matches "subscription termination"). BM25 is exact keyword match — misses synonyms but catches specific terms exactly. Hybrid (combine both scores) outperforms either alone. For production, use hybrid retrieval: dense for semantic relevance, BM25 for keyword precision, combine with Reciprocal Rank Fusion (RRF). ARIA used dense-only; hybrid would have been better for technical term queries.

**Chunk overlap trade-off:** More overlap = fewer information gaps at boundaries, but more duplicate content retrieved. 10% overlap is a good default. At 50% overlap, retrieval recall improves but you're storing and embedding 50% more data.

**Re-ranking latency trade-off:** Cross-encoder re-ranking adds 50–200ms. For a 2-second SLA, this is acceptable. If latency SLA is 500ms, skip re-ranking and rely on bi-encoder alone — it's fast enough and good enough for most queries. Only add re-ranking when retrieval precision is insufficient.

---

## Cross-Questions

**How do you handle knowledge base updates in real-time?**

When a document is updated, re-ingest only that document. The ingestion pipeline checks the fingerprint — if changed, re-chunk, re-embed, upsert new vectors (overwrite by doc_id), delete old chunks that no longer exist. This is an incremental update — no full re-indexing needed. Propagation time: fingerprint detection (near-instant with S3 event triggers) + re-embedding (~1 second for a 10-page doc) + vector upsert (< 1 second). Total: under 5 seconds for document updates to be live.

**What if retrieved chunks are irrelevant — the question is outside the knowledge base?**

Set a similarity score threshold. If all top-K retrieved chunks score below 0.6 cosine similarity, the question has no good match in the knowledge base. Instead of passing low-quality context to the LLM and getting a hallucinated answer, return: "I don't have information about this topic in my knowledge base." This is what ARIA's retrieval confidence gate does. You can also add a classifier that detects out-of-scope questions before hitting the vector DB.

**How do you prevent the LLM from answering from its training data instead of retrieved context?**

The system prompt instruction ("Answer ONLY from the provided context") is the primary guard but is probabilistic — LLMs sometimes ignore it. Add a faithfulness check: after getting the response, verify each factual claim in the response appears in the retrieved chunks. A fast cross-encoder can score this. If faithfulness < threshold, reject the response and return a "not confident" fallback. This is the eval framework feedback loop.

**How does multi-tenant isolation work in the vector store?**

Every vector is stored with `tenant_id` metadata. Every query includes `filter: { tenant_id: current_tenant }`. This is enforced at the application layer — the query pipeline always injects the tenant filter. The tenant_id comes from the authenticated JWT, never from user input. In Pinecone, use namespaces (separate index per tenant for strong isolation at the cost of higher overhead) or metadata filters (shared index with per-query filtering — more efficient but relies on filter enforcement). For high-security use cases (healthcare, finance), separate indexes per tenant is safer despite the overhead.

**How would you handle a question that requires combining information from multiple documents?**

Multi-hop retrieval. First retrieval finds the most relevant chunk. The LLM partially answers and identifies what additional information is needed. Second retrieval targets that specific gap. This iterative retrieve-read cycle is how RAG agents work — not a single pass but a loop until the LLM has enough context. In ARIA, this was a simple two-hop: retrieve primary answer, retrieve supporting evidence. Full multi-hop agents can do 5–10 retrieval rounds for complex research questions.
