# Q9: Design RAG Pipeline at Scale

> Anchor every answer in ARIA at CitiusTech — this is production experience, not theory.

---

> **Interview Phase Map** → Phase 1: Requirements (5 min) · Phase 2: Core Entities (2 min) · Phase 3: API Design (5 min) · Phase 4: High Level Design (12 min) · Phase 5: Deep Dives (10 min)

---

## Introduction

A Retrieval-Augmented Generation (RAG) pipeline is an architecture that makes a large language model answer questions using a specific set of documents rather than relying solely on what it learned during training. Instead of asking an LLM a question directly, the system first retrieves the most relevant documents from a knowledge base, injects them into the prompt as context, and then asks the LLM to generate an answer grounded in that retrieved material.

The problem RAG solves is fundamental to deploying LLMs in enterprise settings. LLMs have a training cutoff — they do not know about events or documents created after that date. More importantly, they have no access to private, internal knowledge: a company's runbooks, tickets, documentation, or codebase. RAG bridges this gap by giving the LLM dynamic access to curated, up-to-date, and domain-specific information at query time.

The pipeline has two distinct phases. The **ingestion pipeline** runs offline: raw documents are loaded, split into smaller chunks, converted into vector embeddings using an embedding model, and stored in a vector database. This is a one-time or periodic process. The **query pipeline** runs in real time: when a user asks a question, it is also converted into an embedding, the vector database is searched for the most semantically similar chunks, and those chunks are assembled into a prompt that the LLM uses to generate a response.

The hard problems in production RAG are not the retrieval itself — they are the quality of what you retrieve. Chunking strategy matters enormously: chunks that are too large lose precision, too small lose context. Embedding model choice affects whether similar concepts actually map to similar vectors. Re-ranking retrieved chunks before passing them to the LLM can dramatically improve answer quality. Evaluation — measuring whether the system retrieves the right documents and generates correct, grounded answers — is what separates a working demo from a production system.

---

## How to Approach This in an Interview

RAG (Retrieval-Augmented Generation) is the architecture of every enterprise AI product right now. The question tests whether you understand: why RAG exists (LLMs hallucinate without grounding), the two-pipeline structure (ingestion vs query), and the production concerns that separate a demo from a real system (evaluation, caching, chunking quality, multi-tenancy). If you built ARIA, you've lived all of this — lead with that.

---

## Clarifying Questions

**1. What's in the knowledge base?**

"Are we indexing structured documents (PDFs, Word files), semi-structured (HTML pages, wikis), or database tables? The parsing strategy changes significantly."

*Why this matters:* PDFs need text extraction (PyMuPDF). Scanned PDFs need OCR first. HTML needs scraping + noise removal. Database rows need structured formatting.

**2. Knowledge base size?**

"Are we talking about hundreds of documents or millions? And how often does the knowledge base change — static (rare updates) or dynamic (documents updated daily)?"

*Why this matters:* Hundreds of docs = exhaustive vector search is fine. Millions of docs = Approximate Nearest Neighbor (ANN) search is required. Dynamic = incremental re-ingestion, fingerprint-based deduplication.

**3. Latency requirement?**

"Sub-second for a chat interface, or a few seconds for a report generation pipeline?"

*Why this matters:* Sub-second means: query embedding + ANN search + LLM call must all happen within ~1 second. Aggressive caching and model selection matter. A few seconds allows larger models, more re-ranking, multi-hop retrieval.

**4. Multi-tenant?**

"Multiple organizations with isolated knowledge bases, or single-tenant?"

*Why this matters:* Multi-tenant = every query must be filtered to the current tenant. Cross-tenant data leakage is a security incident. ARIA had this requirement — enforced at the vector DB query level.

### Assumptions

```
- Enterprise knowledge base: PDFs, Markdown, internal wiki pages
- 100K documents per tenant (manageable but still needs ANN)
- Multi-tenant (multiple organizations, fully isolated)
- Sub-2-second query latency
- Knowledge base updates within minutes of document change
- At-least 100 queries/sec per tenant, 10 tenants = 1,000 queries/sec total
```

---

## Functional Requirements

- Users should be able to query the knowledge base in natural language and receive grounded answers with source citations
- Operators should be able to ingest, update, and delete documents from the knowledge base
- The system should enforce strict tenant isolation — one tenant's documents must never appear in another's results

> **How to say this in the interview:** *"I see three core things here — query the knowledge base in natural language and get grounded answers with source citations, ingest and remove documents from the knowledge base, and enforce strict tenant isolation so one organization's documents can never surface in another's results. Does that capture it?"* The tenant isolation point is worth stating as a first-class requirement because it fundamentally changes the retrieval architecture — confirm scope before you design around it.

## Non-functional Requirements

> **NFR = Non-Functional Requirements.** These answer *how the system behaves*, not *what it does*. FR = "users should be able to post a tweet" (the feature). NFR = "the feed must load in under 200ms" (the quality). Same system, completely different axis.

- **Query latency < 2 seconds end-to-end**: includes retrieval + LLM generation — must feel responsive
- **Knowledge freshness**: document updates must be searchable within minutes of ingestion
- **Multi-tenant isolation (hard requirement)**: pre-filter by tenant_id before ANN search — never post-filter
- **Scale**: 1,000 queries/sec total (100 queries/sec × 10 tenants)
- **Retrieval accuracy over raw speed**: a wrong answer is worse than a slow one — recall and precision matter most

> **How to say this in the interview:** After agreeing on FRs, transition with: *"Now let me think about the non-functional requirements — the qualities the system needs to have, not just the features."* Then state each of the points listed above with its specific number or reason attached. Always quantify — "the system should be fast" signals nothing; the specific path and millisecond target is what shows you understand the system. Close with: *"Any specific constraints I should factor into my design?"*
>
> **Mental checklist for any system — pick your top 3:** Run through these mentally every time: *Is stale data acceptable, or must it always be correct?* (CAP — AP or CP?), *Which specific path must be fastest, and what is the millisecond target?* (Latency), *What is the read-to-write ratio and peak QPS?* (Scale). Add Durability, Security, or Compliance only when they are the defining constraint for that particular system — do not list all eight just to look thorough.

---

## Back-of-Envelope Math

> **Interview note:** Skip this section out loud. Say: *"I'll skip capacity estimation upfront — I'll do the math only if a specific number would directly change a design decision."* Then move on. The calculations above are study material — they show you the scale of this system and tell you what to optimize for.

```
Ingestion:
  100K documents × 10 pages average × 512 tokens/page
  = 100K × 5,120 tokens = 512M tokens total
  
  With 512 tokens per chunk and 10% overlap:
  ~1M chunks per tenant

  Embedding: 1M chunks × 50ms/chunk (CPU MiniLM) = 50,000 seconds = 14 hours
  → Use GPU inference: 5ms/chunk = 1,400 seconds = 23 minutes for full re-index
  → Incremental updates: only re-embed changed documents → seconds per update

Vector storage:
  1M chunks × 384 floats × 4 bytes = 1.5 GB per tenant
  10 tenants = 15 GB total → fits on one vector DB node

Query latency budget (2 second SLA):
  Query embedding: 10ms
  ANN vector search: 20ms
  Re-ranking (cross-encoder): 100ms
  LLM call (GPT-4 streaming): 1,000ms
  Overhead (network, context packing): 100ms
  Total: ~1,230ms ← within 2 second budget
```

---

## Core Entities

- **Document** — raw source file + metadata (tenant_id, source, created_at, content type)
- **Chunk** — text segment extracted from a document + embedding vector + document reference
- **VectorIndex** — per-tenant ANN index over chunk embeddings (e.g. HNSW in Qdrant/Weaviate)
- **QueryResult** — retrieved chunks + LLM-generated answer + source citations

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## Data Flow

> **When to use this in the interview:** For pipeline-style systems, sketch the data flow as a numbered list before drawing boxes. Say: *"Let me walk through the sequence of operations before I draw the architecture."* This makes the HLD diagram much easier to follow because the interviewer already knows what each box is for.

**Ingestion path (document → indexed chunks):**

1. Client uploads document → API returns 202 Accepted with `document_id`
2. Upload triggers a message onto the ingestion queue (Kafka)
3. Document Processor pulls the message, fetches the raw file from object storage
4. Parser splits the document into overlapping text chunks (e.g. 512 tokens, 50-token overlap)
5. Embedding model converts each chunk into a dense vector
6. Chunks + vectors written to the vector database, indexed under `tenant_id`
7. Document status updated to "indexed" in the metadata store

**Query path (question → grounded answer):**

1. Client sends natural language query → API receives it
2. Query embedded using the same embedding model as ingestion
3. Vector database performs ANN search, pre-filtered by `tenant_id`
4. Top-k chunks retrieved and ranked
5. Chunks injected into the LLM prompt as context
6. LLM generates a grounded answer
7. Response + source chunk references returned to client

---

## API Design

> **Why REST (sync query, async ingestion):** The query endpoint is synchronous — a user asks a question and waits for the answer. REST POST with a body works well for structured queries with filters. Document ingestion is different: processing a PDF takes seconds to minutes, so the API accepts the file, returns 202 Accepted immediately, and processes it asynchronously. Say: *"I'll use REST. The query is a POST with a structured body — it has filters and parameters that don't fit cleanly into a GET query string. Ingestion is async: the API accepts the document and returns 202 Accepted immediately. The client polls for status rather than waiting, because file processing can take several minutes."*

```
POST /v1/query
body: { "query": string, "top_k"?: int, "filters"?: object }
→ 200: { "answer": string, "sources": [{ "chunk_id": string, "text": string, "score": float }] }

POST /v1/documents
body: multipart/form-data { file, metadata: { source, tags } }
→ 202 Accepted: { "document_id": string, "status": "processing" }

GET /v1/documents/{document_id}/status
→ 200: { "status": "processing|indexed|failed", "chunks_created": int }

DELETE /v1/documents/{document_id}
→ 202 Accepted  (async — removes all chunks from vector index)
```

---

## High Level Design

> **How to build this diagram in the interview — this phase matters most:** Do not draw the complete architecture upfront. Start by saying: *"Let me build the architecture by going through each endpoint one at a time."* For each endpoint: draw only the components it needs, talk through the data flow out loud as you draw — the interviewer needs to follow your reasoning, not just see boxes appearing — and add the relevant schema fields directly next to the database component in the diagram. When you spot a need for a cache, queue, or additional component mid-drawing, say *"I can see we'll need a cache here — I'm going to note that and come back to it in deep dives"*, then keep moving. Do not solve deep dive problems during this phase. Finish High Level Design only when all three functional requirements have a working data path through the diagram. The diagram above is your reference for what the final state looks like.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         INGESTION PIPELINE                                   │
│                                                                              │
│  Documents  ──▶  Doc Loader  ──▶  Chunker  ──▶  Embedder  ──▶  Vector DB   │
│  (S3, Wiki,      (PDF, MD,        (fixed/         (MiniLM,       (Pinecone,  │
│   SharePoint)     HTML parser)    semantic)        OpenAI)        pgvector)  │
│                                       │                                      │
│                               Metadata Store (MySQL)                         │
│                               doc_id, chunk_id, source_url, fingerprint     │
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
│                                                                    ▼        │
│                                                             ┌────────────┐  │
│                                                             │ Guardrails │  │
│                                                             │ + Eval Log │  │
│                                                             └────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Ingestion Pipeline — Deep Dive

### Step 1: Document Loading and Fingerprinting

Before anything else, detect whether the document actually changed (avoid re-ingesting unchanged documents — embedding calls cost money):

```python
class DocLoader:
    def load(self, source: str) -> Optional[Document]:
        """Returns None if document hasn't changed."""
        
        # Fetch raw content based on source type
        if source.endswith('.pdf'):
            raw_bytes = s3.get_object(source)
            raw_text = self._extract_pdf_text(raw_bytes)
        elif source.endswith('.md'):
            raw_text = s3.get_object_text(source)
        elif source.startswith('http'):
            raw_text = self._scrape_and_clean(source)
        
        # Fingerprint = SHA256 of the content
        # If fingerprint unchanged since last ingestion: skip
        fingerprint = hashlib.sha256(raw_text.encode()).hexdigest()
        
        stored_fp = db.get_fingerprint(source)
        if stored_fp == fingerprint:
            return None  # unchanged, skip
        
        return Document(
            text=raw_text,
            source=source,
            fingerprint=fingerprint,
            title=self._extract_title(source, raw_text)
        )
```

**PDF extraction options:**

- `PyMuPDF (fitz)`: Fast, preserves layout, handles multi-column. Best for most PDFs.
- `pdfplumber`: Better for tables, extracts structured table data.
- `pdfminer`: Slower but most accurate for complex layouts.

If `len(extracted_text) < 100` and document has pages → scanned PDF → route to OCR (AWS Textract).

### Step 2: Chunking — The Most Impactful Decision

How you split documents into chunks determines retrieval quality more than which embedding model you use.

**Why chunking matters:**

```
Too-small chunks (< 100 tokens):
  "is non-refundable." ← Not enough context to be useful
  
Too-large chunks (> 1000 tokens):
  "The return policy covers all digital products, physical goods, subscription
   services, and enterprise licenses. Each category has specific rules. Digital
   products downloaded are non-refundable. Physical goods can be returned within
   30 days in original packaging. Subscriptions can be cancelled..." (continues)
  
  Retrieval matches chunk because it mentions "digital products"
  But LLM context is polluted with irrelevant return policy details
  
Sweet spot (256-512 tokens):
  "Digital products, including software licenses and downloaded content, are 
   non-refundable once activated or downloaded. This applies to all digital
   purchases including ebooks, software licenses, and streaming subscriptions."
  Dense, specific, useful.
```

**Strategy 1: Fixed-size with overlap (simplest)**

```python
def fixed_size_chunk(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunks.append(' '.join(chunk_words))
        i += (chunk_size - overlap)  # step forward, but overlap with next chunk
    
    return chunks
```

Problem: cuts sentences mid-thought. "The policy states that refunds are... / ...only available within 30 days" — broken sentence, confusing for both embedding and LLM.

**Strategy 2: Sentence-based chunking (ARIA's approach)**

```python
import spacy
nlp = spacy.load("en_core_web_sm")

def sentence_chunk(text: str, max_tokens: int = 512) -> list[str]:
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents]
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_tokens = len(sentence.split())
        
        if current_length + sentence_tokens > max_tokens and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0
        
        current_chunk.append(sentence)
        current_length += sentence_tokens
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks
```

Respects sentence boundaries. Chunks are semantically coherent. Variable size (50-600 tokens typically) — that's fine.

**Strategy 3: Semantic chunking (highest quality, highest cost)**

Split where embedding similarity drops significantly between adjacent sentences. Groups semantically related content together.

```python
def semantic_chunk(text: str, threshold: float = 0.85) -> list[str]:
    sentences = split_sentences(text)
    embeddings = embedder.embed_batch(sentences)  # O(n) embedding calls
    
    chunks = [sentences[0]]
    current_chunk_sentences = [sentences[0]]
    
    for i in range(1, len(sentences)):
        similarity = cosine_similarity(embeddings[i-1], embeddings[i])
        
        if similarity < threshold:
            # Semantic break detected — start new chunk
            chunks.append(' '.join(current_chunk_sentences))
            current_chunk_sentences = [sentences[i]]
        else:
            current_chunk_sentences.append(sentences[i])
    
    return chunks
```

Cost: requires embedding every sentence (10x more embedding calls). Worth it for high-value knowledge bases where retrieval quality is critical (legal, medical).

### Step 3: Embedding

Convert each text chunk to a dense vector:

```python
class Embedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # bge-small: 384 dimensions, 33M params, fast on CPU
        # bge-large: 1024 dimensions, 335M params, better quality
        # OpenAI text-embedding-3-small: 1536 dims, API cost, best quality
        from fastembed import TextEmbedding
        self.model = TextEmbedding(model_name)
    
    def embed(self, text: str) -> list[float]:
        return list(self.model.embed([text]))[0].tolist()
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        # More efficient than embedding one at a time
        return [emb.tolist() for emb in self.model.embed(texts)]
```

**Embedding model comparison:**

| Model | Dimensions | Speed (CPU) | Quality | Cost |
|-------|-----------|-------------|---------|------|
| all-MiniLM-L6-v2 | 384 | 50ms/chunk | Good | Free |
| BAAI/bge-small-en-v1.5 | 384 | 40ms/chunk | Better | Free |
| BAAI/bge-large-en-v1.5 | 1024 | 200ms/chunk | Best OSS | Free |
| OpenAI text-embedding-3-small | 1536 | ~100ms/call | Excellent | $0.02/1M tokens |

ARIA used MiniLM with fastembed on CPU — zero API cost, good quality for English medical documentation, 50ms/chunk is fast enough.

### Step 4: Storing in Vector DB

```python
# Each chunk stored with:
{
    "id": "chunk_abc123",
    "values": [0.023, -0.145, ...],  # 384 floats
    "metadata": {
        "tenant_id": "org_xyz",        # CRITICAL: multi-tenancy isolation
        "doc_id": "doc_456",
        "source_url": "https://wiki/page",
        "chunk_index": 3,              # which chunk within the document
        "text": "Digital products are non-refundable...",  # store text for retrieval
        "title": "Refund Policy",
        "created_at": "2026-06-22",
        "word_count": 87
    }
}
```

**Multi-tenancy enforcement:** Every vector MUST have `tenant_id`. Every query MUST filter by `tenant_id`. This is enforced in code — you cannot query without passing the current authenticated tenant's ID.

```python
# ALWAYS filter by tenant — never allow a query without it
results = pinecone_index.query(
    vector=query_embedding,
    top_k=20,
    filter={"tenant_id": {"$eq": current_tenant_id}},  # NEVER skip this
    include_metadata=True,
    include_values=False  # don't return the vectors, just metadata
)
```

---

## Part 2: Query Pipeline — Deep Dive

### Step 1: Query Rewriting

The user's raw question is often context-dependent and vague. In a multi-turn conversation, "What about digital products?" is meaningless without the previous context.

```python
def rewrite_query(conversation_history: list[dict], current_question: str) -> str:
    if len(conversation_history) == 0:
        return current_question  # no history, keep as-is
    
    system_prompt = """
    You are a query rewriter. Given the conversation history and the latest user question,
    rewrite the question to be completely self-contained and specific.
    Return ONLY the rewritten question, nothing else.
    """
    
    user_prompt = f"""
    Conversation history:
    {format_conversation(conversation_history[-4:])}  # last 4 turns
    
    Latest question: {current_question}
    
    Rewritten question:
    """
    
    rewritten = llm_fast.complete(system_prompt + user_prompt, max_tokens=100)
    return rewritten.strip()

# Example:
# History: "Q: What's your return policy? A: Returns within 30 days..."
# Current: "What about digital products?"
# Rewritten: "What is the return policy for digital products?"
```

Use a fast, cheap model (GPT-3.5-turbo or Claude Haiku) for rewriting — it's a small, well-defined task.

### Step 2: Semantic Cache

Before hitting the vector DB (which takes 20ms) and the LLM (which takes 1,000ms), check if this question was recently asked:

```python
def check_semantic_cache(query: str, tenant_id: str) -> Optional[str]:
    # Embed the query
    query_embedding = embedder.embed(query)
    
    # Search Redis for a semantically similar recent query
    # Redis with RedisSearch supports vector similarity
    similar = redis.ft("cache_index").search(
        Query(f"*=>[KNN 1 @embedding $vec AS score]")
        .return_fields("response", "score")
        .paging(0, 1),
        query_params={"vec": serialize_embedding(query_embedding)}
    ).docs
    
    if similar and float(similar[0].score) > 0.95:
        # Cosine similarity > 0.95 = essentially the same question
        return similar[0].response
    
    return None  # cache miss

def store_in_cache(query: str, response: str, tenant_id: str):
    query_embedding = embedder.embed(query)
    cache_key = f"cache:{tenant_id}:{hashlib.md5(query.encode()).hexdigest()}"
    
    redis.hset(cache_key, mapping={
        "query": query,
        "response": response,
        "embedding": serialize_embedding(query_embedding),
        "tenant_id": tenant_id
    })
    redis.expire(cache_key, 300)  # 5 minute TTL
```

**Cache hit rate in production:**

ARIA saw ~35% cache hit rate in production. Enterprises tend to ask the same questions repeatedly (new employee onboarding, policy lookups, FAQ-type queries). This translates to 35% reduction in LLM API costs and 35% of queries returning in < 10ms instead of 2 seconds.

### Step 3: Vector Search — ANN Explained

**What is ANN (Approximate Nearest Neighbor)?**

The query vector is a point in 384-dimensional space. We want the 20 most similar points (stored chunk vectors). Exact nearest neighbor = compute distance to all 1M stored vectors = O(1M × 384 float operations) ≈ 400ms per query. Too slow.

ANN algorithms find the approximate nearest neighbors in O(log N) using clever indexing. The standard is **HNSW (Hierarchical Navigable Small World)**:

```
HNSW structure (conceptual):

Layer 2 (coarse): 
  Node A ─── Node F ─── Node K
  (long-range connections, few nodes)

Layer 1 (medium):
  A─B─C   F─G─H   K─L─M
  (medium connections)

Layer 0 (fine):
  A-B-C-D-E  F-G-H-I-J  K-L-M-N-O  (all nodes, dense connections)

Search: enter at top layer (coarse approximation)
        greedily move toward query vector
        drop to next layer, repeat
        at Layer 0: do local exhaustive search
        
Result: ~95% recall vs exact search, 100x faster
```

**What does 95% recall mean?**

Of the true 20 nearest neighbors, we return ~19 of them. The 20th might be missed. That's acceptable — the LLM can work with 19 great chunks rather than needing all 20.

### Step 4: Re-ranking with Cross-Encoder

```
Bi-encoder (embedding model): 
  Query → embedding
  Document → embedding
  Similarity = cosine(query_emb, doc_emb)
  
  Fast: can precompute doc embeddings
  Less accurate: computes query and document independently
  
Cross-encoder:
  Input: "[query] + [document]" (concatenated)
  Output: relevance score (0-1)
  
  Slow: can't precompute, must run at query time for each pair
  More accurate: sees query and document together, captures interaction
```

```python
from sentence_transformers import CrossEncoder

cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    # Candidates: top-20 from ANN search
    pairs = [(query, chunk['metadata']['text']) for chunk in candidates]
    
    # Cross-encoder scores each pair jointly
    scores = cross_encoder.predict(pairs)  # ~100ms for 20 pairs
    
    # Sort by cross-encoder score (descending), take top-k
    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    
    return [chunk for chunk, score in ranked[:top_k]]
```

**Why the two-stage approach (ANN + re-ranking)?**

ANN retrieval is fast but imperfect. Cross-encoder is accurate but slow. Two stages:
1. ANN gets top-20 candidates quickly (20ms, ~95% recall)
2. Cross-encoder selects the best 5 from those 20 (100ms, near-perfect precision)

Total: 120ms for high-quality retrieval. Pure ANN would be 20ms but lower quality. Pure cross-encoder over 1M chunks would be hours.

This is the same two-stage pattern Google's search uses.

### Step 5: Context Packing and LLM Call

```python
def build_prompt(query: str, chunks: list[dict], 
                 conversation_history: list[dict]) -> str:
    context = "\n\n".join([
        f"[{i+1}] Source: {c['metadata']['source_url']}\n{c['metadata']['text']}"
        for i, c in enumerate(chunks)
    ])
    
    history = format_conversation(conversation_history[-4:])
    
    return f"""You are a helpful assistant for this organization's knowledge base.
Answer ONLY based on the provided context. If the answer is not in the context,
say "I don't have information about this in the knowledge base."

CONTEXT:
{context}

CONVERSATION HISTORY:
{history}

USER QUESTION: {query}

Answer:"""

# LLM call
response = openai_client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.1,   # low temperature = deterministic, factual
    max_tokens=500,
    stream=True        # stream tokens as they're generated
)
```

**Context window budget:**

- System prompt: ~200 tokens
- Retrieved chunks (5 × 512 tokens): 2,560 tokens
- Conversation history (4 turns × 200 tokens): 800 tokens
- Current question: ~50 tokens
- Total: ~3,610 tokens

GPT-4's context window is 128K tokens. We're well within budget. For very large retrieval sets, truncate older conversation turns first, then reduce chunk count.

---

## Evaluation Framework

Without evaluation, you don't know if your RAG is improving or degrading. ARIA ran nightly evals.

**Retrieval evaluation:**

```python
# Given test set: (query, expected_relevant_doc_ids)
def evaluate_retrieval(test_cases: list[dict]) -> dict:
    precision_at_5 = []
    recall_at_5 = []
    
    for case in test_cases:
        retrieved = retriever.search(case['query'], top_k=5)
        retrieved_ids = {c['metadata']['doc_id'] for c in retrieved}
        relevant_ids = set(case['expected_doc_ids'])
        
        # Precision@5: of what we retrieved, what fraction is relevant?
        precision = len(retrieved_ids & relevant_ids) / len(retrieved_ids)
        
        # Recall@5: of all relevant docs, what fraction did we retrieve?
        recall = len(retrieved_ids & relevant_ids) / len(relevant_ids)
        
        precision_at_5.append(precision)
        recall_at_5.append(recall)
    
    return {
        "precision_at_5": mean(precision_at_5),
        "recall_at_5": mean(recall_at_5)
    }
```

**LLM-as-judge for generation quality:**

```python
def evaluate_faithfulness(query: str, retrieved_chunks: list[str], 
                           answer: str) -> float:
    """Rate if the answer only uses information from the context."""
    judge_prompt = f"""
    Rate the faithfulness of this answer from 1-5.
    5 = Answer uses ONLY information from context, no hallucination
    1 = Answer contains significant information not in the context
    
    Context: {' '.join(retrieved_chunks)}
    Question: {query}
    Answer: {answer}
    
    Rating (just the number 1-5):
    """
    score = int(judge_llm.complete(judge_prompt).strip())
    return score / 5.0  # normalize to 0-1

# ARIA's production thresholds:
# precision@5 < 0.80 → alert (retrieval degraded)
# faithfulness < 0.85 → alert (LLM hallucinating)
# Both checked nightly against 200 test cases
```

---

## Scale — What Breaks at 10x?

> **How to transition into deep dives:** Say: *"I now have a working system that satisfies all three functional requirements. Let me harden it by addressing the non-functional requirements I identified at the start."* Then work through the NFRs one by one, starting with the most important. For each one, state the problem it creates in the current design, then your solution. After each point, pause and let the interviewer probe before moving on — do not monologue for more than two minutes at a stretch. The interviewer has specific signals they are looking for; if you are talking, they cannot ask for them. For senior roles, proactively identify the next bottleneck without waiting to be prompted.


10x = 10,000 queries/sec, 1M documents per tenant.

**Embedding inference (query side):** 10K queries × 10ms/embedding (GPU) = 100 GPU-seconds/second = 100 GPU-cores dedicated to query embedding. With NVIDIA T4 GPUs (cost-effective), each handles ~500 embeddings/sec. Need 20 GPUs for 10K QPS. Use a dedicated embedding inference server (Triton, TorchServe) with request batching.

**Vector DB throughput:** Pinecone and Weaviate handle thousands of QPS per pod. Shard by tenant_id — each tenant's vectors on a dedicated pod for strong isolation. At 10 tenants × 1K QPS = 10K QPS total, 2-4 vector DB pods per tenant.

**LLM API cost at scale:**

10K queries/sec × 3,500 tokens/query × $0.03/1K tokens (GPT-4) = $1,050/sec = $90M/day. Obviously impossible.

Solutions:
1. **Semantic cache** cuts 30-50% of LLM calls
2. **Model routing**: Use GPT-3.5 for simple factual queries (~80% of queries), GPT-4 only for complex multi-step reasoning (~20%). Cost reduction: 80%.
3. **Self-hosted model**: Run Llama 3 70B or Mistral on your own GPU cluster. At this scale, GPU hardware costs less than API fees.

---

## Trade-offs

**Dense-only vs Hybrid Search (Dense + BM25):**

ARIA used dense-only (embedding similarity). This works well for semantic questions ("how do I cancel?") but misses exact term matching ("HIPAA violation 45 CFR 164.512"). Adding BM25 (keyword search) via Elasticsearch + fusing results with Reciprocal Rank Fusion (RRF) improves precision for technical queries.

ARIA's precision@5 was 0.85. With hybrid search, we estimated 0.91+ based on offline experiments. The 6% improvement in precision translates directly to better answers. In hindsight, hybrid search would have been worth the added infrastructure (Elasticsearch + RRF fusion code).

**Re-ranking latency vs accuracy:**

Cross-encoder re-ranking adds 100ms but significantly improves precision (from ~0.85 to ~0.93 in our testing). For a 2-second SLA, 100ms is affordable. For a 500ms SLA, skip re-ranking and rely on bi-encoder alone.

**Chunk overlap impact:**

10% overlap: some information at chunk boundaries is captured in both adjacent chunks. Retrieval recall improves slightly (fewer "edge cases" where the answer spans a boundary).

50% overlap: much better boundary coverage, but you're storing and embedding 50% more data, and retrieved chunks have duplicate content (LLM gets the same sentence twice). 10-15% overlap is the sweet spot.

---

## Cross-Questions

**Q: How do you handle knowledge base updates in real-time?**

```
Document updated in S3/Wiki → S3 Event Notification → SQS → Ingestion Worker

Ingestion Worker:
  1. Download the document
  2. Compute new fingerprint
  3. Compare with stored fingerprint
     If unchanged: skip (no re-ingestion)
     If changed:
       4. Delete old chunks from vector DB:
          vector_db.delete(filter={"doc_id": "doc_456", "tenant_id": "org_xyz"})
       5. Re-parse, re-chunk, re-embed
       6. Insert new chunks into vector DB
       7. Update fingerprint in MySQL
  
  Total update time for a 10-page document:
    Parse: 100ms
    Chunk: 50ms  
    Embed (20 chunks × 10ms GPU): 200ms
    Vector DB upsert: 100ms
    Total: ~450ms → document updated in knowledge base within 1 second
```

**Q: What if retrieved chunks are irrelevant (question outside knowledge base)?**

```python
def check_retrieval_confidence(chunks: list[dict]) -> bool:
    """Return False if no relevant chunks found."""
    if not chunks:
        return False
    
    # Check the top chunk's similarity score
    top_score = chunks[0]['score']  # cosine similarity
    
    if top_score < 0.60:
        # Even the best match is below threshold — question isn't in KB
        return False
    
    return True

# In query pipeline:
if not check_retrieval_confidence(retrieved_chunks):
    return "I don't have information about this topic in my knowledge base."
    # Don't call LLM — would hallucinate or make something up
```

This was one of ARIA's most impactful improvements. Before adding this gate, ARIA would confidently answer questions outside its knowledge base using LLM training data, leading to hallucinations. After: graceful "I don't know" responses.

**Q: How does multi-tenant isolation work in the vector store?**

Three levels of isolation:

**Application layer (weakest but always present):** Every query is constructed with the current tenant's ID from JWT. Code never allows a query without `tenant_id` filter.

**Metadata filter (Pinecone/Weaviate):** At query time, `filter: {"tenant_id": "org_xyz"}`. Vectors for other tenants exist in the same index but are filtered out before ANN search. Fast but relies on filter correctness.

**Namespace isolation (strongest):** Pinecone namespaces = completely separate index per tenant. A namespace is like a separate index. Queries in namespace `org_xyz` cannot return results from `org_abc` even if filters are misconfigured. Higher infrastructure overhead but stronger security guarantee.

For HIPAA/SOC2 compliance, use namespace isolation. For general enterprise, metadata filtering with code-level enforcement is sufficient.

**Q: How would you handle a question that requires combining information from 3 separate documents?**

This is multi-hop retrieval:

```
Hop 1: Retrieve top-5 chunks for the original question
  Answer is partial: "The policy applies to..."
  
LLM identifies gap: "I need to know the definition of X to complete this answer"
  
Hop 2: Retrieve top-5 chunks for the identified gap
  "What is the definition of X in policy context?"

LLM now has enough context to compose a complete answer

# Implementation: agentic loop
def multi_hop_rag(query: str, max_hops: int = 3) -> str:
    context_chunks = []
    current_query = query
    
    for hop in range(max_hops):
        new_chunks = retrieve_and_rerank(current_query)
        context_chunks.extend(new_chunks)
        
        # Ask LLM: can you answer now, or do you need more info?
        response = llm.complete(f"""
        Context: {format_chunks(context_chunks)}
        Question: {query}
        
        If you can answer fully, do so.
        If you need more information, respond with:
        NEED_MORE: [what specific information is missing]
        """)
        
        if not response.startswith("NEED_MORE:"):
            return response  # answered fully
        
        # Extract what's needed and search again
        current_query = response.replace("NEED_MORE:", "").strip()
    
    return llm.complete(final_prompt_with_all_context)
```

ARIA used a simplified 2-hop version. Full multi-hop is standard in RAG agent frameworks (LangGraph, LlamaIndex's ReAct agent).
