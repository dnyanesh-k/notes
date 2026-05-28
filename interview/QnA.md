---

## Q1. Tell Me About Yourself

**Say this:**

"I'm a Software Engineer with 2.6 years of experience, currently at CitiusTech where I work on enterprise AI systems.

My core focus is GenAI — specifically RAG pipelines, semantic search, LLM orchestration, and agentic workflows using MCP.

I built an Enterprise AI Assistant Platform from scratch — handling everything from embedding pipelines and retrieval to guardrails and LLM routing.

Before that I built an ETL-based error automation system using Flask, Argo Workflows, AWS, and Jira integration.

I'm now looking to move into a role where I can work on more complex AI solutioning and production-grade GenAI systems — which is exactly what this role at MGT is about."

---

## Q3. Hardest Technical Problem You Solved

**Say this:**

"The hardest problem was building a hot-reload embedding index that auto-rebuilds when the knowledge base changes — without downtime.

The challenge: if the index rebuilds while queries are running, you get stale or inconsistent results.

What I did:
- Built a file watcher that detects knowledge base changes
- Triggered a background rebuild into a separate index
- Used an atomic swap — old index stays live until new one is fully ready
- Then swapped references so zero queries hit a partial index

Result: zero downtime rebuilds, always-fresh retrieval, no query failures during rebuild."

---

## Q4. Why Are You Leaving CitiusTech?

**Say this:**

"CitiusTech gave me great foundational experience in GenAI and enterprise systems.

But it's primarily a healthcare IT services company — the AI work is one part of a larger services operation.

I want to be in a role where AI engineering is the core focus, not a supporting function.

This role at MGT — owning AI solutioning, building RAG systems, working on proposals and POCs — is exactly the kind of depth and ownership I'm looking for."

---
---

# ROUND 2 — Core Technical

---

## Q5. Explain RAG — How Does It Work and When Would You NOT Use It?

**How it works:**
- User query comes in
- Query is converted to an embedding vector
- Vector DB finds semantically similar chunks from your knowledge base
- Those chunks are passed as context to the LLM
- LLM generates a grounded response using that context

**When NOT to use RAG:**
- Knowledge base changes every few seconds — indexing can't keep up
- You need strict reasoning over structured data — use SQL instead
- Very short, factual lookups — direct DB query is faster and cheaper
- If the LLM already has the knowledge in training — RAG adds latency for no gain

---

## Q6. How Did You Implement Semantic Search? Why MiniLM?

**What I did:**
- Used FastEmbed with MiniLM model to generate embeddings
- Built a multi-phrase query merging strategy — break complex queries into sub-phrases, embed each, merge results
- Built an embedding index builder with hot-reload on knowledge base changes

**Why MiniLM:**
- Lightweight — fast inference, low memory
- Strong performance on semantic similarity benchmarks relative to its size
- No GPU needed — runs efficiently on CPU in production
- Good enough for enterprise domain search — no need for larger models like BGE or E5 for our use case

---

## Q7. What is MCP and How Did You Use FastMCP?

**What is MCP:**
- Model Context Protocol — a standard for exposing tools, resources, and data to LLMs
- Think of it as a plugin system — LLMs can call external tools through MCP interfaces
- Allows AI agents to interact with real systems like Git, Jira, AWS in a structured way

**How I used it:**
- Built a semantic search MCP tool — LLM calls it to retrieve relevant docs
- Exposed Jira, AWS, and Git integrations as MCP services
- Used FastMCP framework to define tools with typed schemas
- LLM decides which tool to call based on the query — full agentic routing

**Why this matters:**
- Decouples AI logic from tool implementation
- Tools are reusable across multiple agents or workflows
- Much cleaner than hardcoding tool calls inside prompt logic

---

## Q8. Chunking Strategy in RAG — What Chunk Size and Why?

**Key decisions in chunking:**
- Chunk size depends on your embedding model's context window and content type
- Too small — chunks lose context, retrieval is noisy
- Too large — chunks dilute relevance, LLM gets irrelevant content

**What I follow:**
- For technical docs: 512 tokens with 50–100 token overlap
- Overlap ensures context isn't lost at chunk boundaries
- Semantic chunking preferred over fixed size — split at paragraph or section boundaries when possible

**Advanced considerations:**
- Parent-child chunking — store small chunks for retrieval, return larger parent chunk to LLM
- Metadata tagging on chunks — source, section, date — helps with filtering

---

## Q9. What Are Guardrails? How Did You Implement Yours?

**What guardrails are:**
- Controls that prevent LLM from producing unsafe, off-topic, or unauthorized outputs
- Also controls what data a user can access based on their role

**What I built:**
- Persona-based guardrail system — each user tier has a defined persona
- Authorization chains — before LLM responds, request passes through access control checks
- Fail-closed design — if auth check fails or is unclear, request is denied, not allowed
- Session management — tracks user context, prevents privilege escalation across turns

**Types of guardrails in general:**
- Input guardrails — filter harmful or out-of-scope queries before hitting LLM
- Output guardrails — validate LLM response before returning to user
- Role-based access — control which knowledge sources a user can query

---

## Q10. How Do You Evaluate a RAG Pipeline?

**Offline metrics:**
- **Faithfulness** — is the answer grounded in retrieved context? No hallucination?
- **Answer relevance** — does the answer actually address the question?
- **Context precision** — are retrieved chunks relevant to the query?
- **Context recall** — did retrieval fetch all necessary chunks?

**Framework:**
- RAGAS is the standard framework for RAG evaluation
- Uses LLM-as-judge pattern to score each dimension

**What I did in practice:**
- Wrote Pytest suites covering retrieval pipeline integrity
- Tested that routing logic returned correct knowledge sources
- Regression tests to catch retrieval degradation after index rebuilds

---

## Q11. Fine-Tuning vs RAG — When to Use Which?

| | RAG | Fine-Tuning |
|---|---|---|
| Knowledge updates | Easy — just update index | Hard — retrain needed |
| Cost | Low | High |
| Use case | Dynamic, doc-based QA | Style, tone, domain behavior |
| Hallucination risk | Lower — grounded in docs | Higher if data is poor |

**Rule of thumb:**
- Use RAG when the knowledge changes or is proprietary
- Use fine-tuning when you want to change HOW the model responds — tone, format, domain behavior
- Often combine both — fine-tune for behavior, RAG for knowledge

---

## Q12. Vector Similarity Search — FAISS vs Pinecone vs pgvector

**FAISS:**
- Facebook's open source library
- Runs in-memory, no server needed
- Best for: prototypes, small-medium datasets, offline search
- No persistence out of the box

**Pinecone:**
- Managed cloud vector DB
- Handles scale, replication, metadata filtering
- Best for: production systems, large datasets, team environments
- Cost: paid service

**pgvector:**
- PostgreSQL extension for vector storage
- Best for: teams already using Postgres, want vectors alongside relational data
- Simpler ops — one DB for everything
- Scales reasonably well for most enterprise use cases

**What I'd recommend:**
- POC/dev: FAISS
- Production, already on Postgres: pgvector
- High scale, managed: Pinecone

---
---

# ROUND 3 — Cloud & Backend

---

## Q13. How Did You Use AWS S3, RDS, EKS Together in Your ETL Pipeline?

**Architecture:**
- Production error logs landed in **S3** as raw files
- **ETL pipeline** (Argo Workflows) picked up files on schedule
- Processed and transformed errors, stored structured records in **RDS** (PostgreSQL)
- From RDS, downstream jobs generated Jira tickets and Slack notifications
- Entire pipeline ran on **EKS** — containerized, scalable, Kubernetes-managed
- **GitHub Actions** handled CI/CD — build, test, deploy to EKS on merge

**Why this stack:**
- S3 for durable, cheap raw storage
- RDS for queryable structured data
- EKS for scalable, containerized pipeline execution

---

## Q14. Explain Your Argo Workflows Pipeline Architecture

**What Argo Workflows is:**
- Kubernetes-native workflow engine
- Each step runs as a container
- DAG-based — define dependencies between steps

**My pipeline:**
- Step 1: Fetch raw error logs from S3
- Step 2: Parse and classify errors by type
- Step 3: Deduplicate — don't create duplicate Jira tickets
- Step 4: Generate structured ticket payload
- Step 5: POST to Jira API, send Slack notification
- Entire DAG runs daily on cron schedule

**Benefits:**
- Each step is independent and retryable
- Failed step doesn't restart entire pipeline
- Full observability — each step has logs in Kubernetes

---

## Q15. How Do You Secure an LLM API Endpoint in Production?

**Key layers:**

- **Authentication** — API key or OAuth token required on every request
- **Authorization** — role-based access, users only query permitted knowledge sources
- **Input validation** — sanitize and length-limit inputs before hitting LLM
- **Rate limiting** — prevent abuse, control cost
- **Output filtering** — strip PII or sensitive content from responses
- **Prompt injection protection** — detect and block attempts to override system prompt
- **Audit logging** — log every request, user, and response for compliance
- **Secrets management** — API keys in AWS Secrets Manager, never in code

---
---

# ROUND 4 — System Design

---

## Q16. Design a RAG Chatbot for 10,000 Concurrent Users

**Components:**

```
User → Load Balancer → FastAPI (multiple instances)
         → Cache (Redis) — check if query answered before
         → Embedding Service — convert query to vector
         → Vector DB (Pinecone/pgvector) — retrieve top-k chunks
         → LLM API (OpenAI/Azure) — generate response
         → Response back to user
         → Async logging → S3/CloudWatch
```

**Key design decisions:**
- **Redis cache** — cache embeddings and frequent query responses, cuts LLM costs
- **Async processing** — don't block on logging or non-critical steps
- **Horizontal scaling** — FastAPI is stateless, add instances behind load balancer
- **Connection pooling** — for vector DB and RDS connections
- **Streaming responses** — stream LLM output to reduce perceived latency

---

## Q17. Scale Your AI Platform to 250K Users — What Breaks First?

**Bottlenecks in order:**

1. **LLM API** breaks first — rate limits, latency, cost
   - Fix: request queuing, multiple API keys, model routing (cheap model for simple queries)

2. **Embedding service** — CPU-bound, slow under load
   - Fix: dedicated embedding microservice, GPU inference, batch embedding

3. **Vector DB** — query latency degrades at scale
   - Fix: index sharding, approximate nearest neighbor (ANN) tuning, read replicas

4. **FastAPI instances** — memory pressure from concurrent sessions
   - Fix: horizontal autoscaling on EKS, stateless design

5. **Redis cache** — memory limits
   - Fix: eviction policy (LRU), Redis Cluster for horizontal scaling

**General principles:**
- Cache aggressively at every layer
- Decouple components — each scales independently
- Async everything non-critical
- Monitor token usage and cost — at 250K users LLM cost is your biggest risk

---

## Q18. How Would You Build an Agentic Workflow System With Tool Calling?

**Core components:**

- **Orchestrator** — LLM that decides which tool to call and in what order
- **Tool registry** — catalog of available tools with schemas (MCP)
- **Tool executor** — safely runs tool calls, handles errors, returns results
- **Memory** — short-term (conversation), long-term (vector store)
- **Guardrails** — validate tool inputs/outputs, prevent harmful actions

**Flow:**
```
User query → Orchestrator LLM
  → Thinks: what tools do I need?
  → Calls Tool 1 (e.g. search docs)
  → Gets result → decides next step
  → Calls Tool 2 (e.g. query DB)
  → Synthesizes final answer → returns to user
```

**What I built at CitiusTech:**
- Used FastMCP to expose Jira, Git, AWS as tools
- LLM routed queries to correct tool based on intent
- Knowledge routing pipeline ensured LLM always grounded in correct source

---
---

# ROUND 5 — Behavioral

---

## Q19. AI Output Was Wrong in Production — How Did You Handle It?

**Say this:**

"In our RAG system, the LLM started returning responses that mixed content from two different knowledge domains — engineering specs and operational docs — because chunk boundaries were causing retrieval overlap.

What I did:
- First, added metadata filtering to scope retrieval by domain tag
- Added a faithfulness check — automated test that flags responses citing chunks from wrong domain
- Improved chunking at semantic boundaries, not fixed token counts
- Added regression test to catch this class of error going forward

Key learning: RAG failures are usually retrieval failures, not LLM failures. Fix the retrieval first."

---

## Q20. How Do You Stay Current With GenAI?

**Say this:**

"I follow a few things actively:

- **MCP ecosystem** — I've been tracking protocol updates and new server implementations since I work with FastMCP daily
- **Agentic frameworks** — LangGraph, CrewAI, and how multi-agent orchestration is evolving
- **Applied papers** — RAGAS evaluation paper, HyDE (Hypothetical Document Embeddings) for better retrieval
- **Practical sources** — Simon Willison's blog, Hugging Face releases, LlamaIndex changelog

Most recently I've been looking at how agentic memory works — combining short-term session memory with long-term vector retrieval — which is directly relevant to this role."

---

**That's all 20. Want me to do mock interview style — I ask, you answer?**
