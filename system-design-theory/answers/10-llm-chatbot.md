# Q10: Design LLM Chatbot at Scale (ChatGPT-like)

---

## Clarifying Questions

A few things to clarify. Is this a general-purpose chatbot or domain-specific? General-purpose means the LLM answers from its training data; domain-specific adds RAG (see Q9). I'll design the infrastructure layer that's common to both.

Do we need conversation memory — multi-turn context where the bot remembers what was said earlier in the chat? And how long is the conversation window — 10 turns or 100?

What's the expected concurrency — how many simultaneous conversations? And what's the latency target? Streaming (tokens appear as generated) or wait for the full response?

Are we using a hosted LLM (OpenAI, Anthropic) or self-hosted? Self-hosted adds GPU cluster management which is a separate system.

*Assuming: domain-specific chatbot with RAG, multi-turn with 20-turn memory, 100K concurrent users, streaming responses, OpenAI/hosted LLM via API.*

---

## Scope

I'll design: conversation management, streaming response serving, session/memory storage, LLM gateway with rate limiting and cost tracking, and the serving layer that handles 100K concurrent streaming connections. I'll reference Q9 for the RAG retrieval layer — same design.

---

## High Level Design

```
┌──────────┐  HTTP/SSE  ┌─────────────┐   ┌──────────────────────────────────┐
│  Client  │───────────▶│  API GW     │   │        Chat Service               │
│ (browser,│◀── stream ─│  (nginx)    │──▶│                                   │
│  app)    │            └─────────────┘   │  ┌────────────┐  ┌─────────────┐ │
└──────────┘                              │  │  Session   │  │    RAG      │ │
                                          │  │  Manager   │  │  Retriever  │ │
                                          │  └─────┬──────┘  └──────┬──────┘ │
                                          │        │                 │        │
                                          │        ▼                 ▼        │
                                          │  ┌──────────────────────────────┐ │
                                          │  │       LLM Gateway            │ │
                                          │  │  (rate limit, cost track,    │ │
                                          │  │   model routing, retry)      │ │
                                          │  └──────────────┬───────────────┘ │
                                          └─────────────────┼─────────────────┘
                                                            │
                                          ┌─────────────────▼─────────────────┐
                                          │         LLM Providers             │
                                          │  OpenAI GPT-4 │ Anthropic Claude  │
                                          │  Fallback: GPT-3.5 (cost saving)  │
                                          └───────────────────────────────────┘

Data Stores:
  Redis     — active sessions, streaming state, rate limit counters
  PostgreSQL — conversation history, user preferences, cost logs
  S3        — long-term conversation archive
```

---

## Deep Dive 1 — Streaming with Server-Sent Events (SSE)

LLMs generate tokens one at a time. If we wait for the full response before sending it to the user, a 500-token response at 30 tokens/sec = 16 seconds of staring at a loading spinner. Terrible UX.

**Server-Sent Events (SSE):** A unidirectional HTTP stream from server to client. The server sends tokens as they're generated, the client renders them as they arrive. Feels like the bot is "typing."

```
Client: GET /v1/chat/stream
        Headers: Accept: text/event-stream

Server keeps the connection open and sends:
  data: {"token": "The", "done": false}\n\n
  data: {"token": " refund", "done": false}\n\n
  data: {"token": " policy", "done": false}\n\n
  ...
  data: {"token": ".", "done": true, "usage": {"prompt_tokens": 450, "completion_tokens": 87}}\n\n
```

**Why SSE over WebSocket for chatbots?**
SSE is unidirectional (server → client), which is exactly what we need for streaming responses. WebSocket is bidirectional — overkill for this use case and harder to scale through standard HTTP infrastructure (load balancers, CDN). SSE works over plain HTTP/2, which multiplexes many streams over one TCP connection.

**Handling SSE at scale:** 100K concurrent users × 1 SSE connection each. Each connection is a long-lived HTTP connection. Nginx handles this well in async mode — 100K connections on a single server with sufficient memory. The backend Chat Service holds one goroutine/coroutine per stream, proxying tokens from OpenAI's streaming API to the client.

---

## Deep Dive 2 — Conversation Memory

Multi-turn chat requires the LLM to remember previous turns. There are two models:

**Full context window:** Send the entire conversation history with every request.
```
System: You are a helpful assistant.
User: What is the refund policy?
Assistant: The refund policy allows returns within 30 days...
User: What about digital products?        ← current question
```
Simple but expensive — every turn adds tokens to the prompt. A 20-turn conversation might have 8,000 tokens of history, costing $0.08 per query just for history.

**Sliding window:** Keep only the last N turns. Simple implementation, but if something important was said in turn 1 and we're now at turn 25, it's forgotten.

**Summarization:** After every 10 turns, ask the LLM to summarize the conversation so far. Store the summary and use it instead of the full history. Compresses 10 turns into ~200 tokens. More complex to implement but handles long conversations gracefully.

**Memory storage:**
```sql
-- PostgreSQL
CREATE TABLE conversations (
    id              UUID PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    last_active_at  TIMESTAMP NOT NULL,
    summary         TEXT,           -- rolling summary of older turns
    INDEX idx_user (user_id, last_active_at DESC)
);

CREATE TABLE messages (
    id              UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id),
    role            VARCHAR(20) NOT NULL,   -- 'user', 'assistant', 'system'
    content         TEXT NOT NULL,
    token_count     INT,
    created_at      TIMESTAMP NOT NULL,
    INDEX idx_conversation (conversation_id, created_at ASC)
);
```

Active session state in Redis:
```
Key:   session:{conversation_id}
Value: { last_n_messages, rolling_summary, user_preferences }
TTL:   1 hour of inactivity
```

On each request: read from Redis (cache hit → fast). On cache miss: load from PostgreSQL, rebuild session state in Redis.

---

## Deep Dive 3 — LLM Gateway

The LLM Gateway sits between your application and OpenAI/Anthropic. It handles concerns that shouldn't live in your Chat Service.

**What the Gateway does:**

```
┌────────────────────────────────────────────────┐
│                LLM Gateway                     │
│                                                │
│  1. Rate limiting per user (OpenAI has global  │
│     limits; we enforce per-user limits first)  │
│                                                │
│  2. Cost tracking                              │
│     tokens_used × price_per_token → DB         │
│                                                │
│  3. Model routing                              │
│     simple query → GPT-3.5 ($0.002/1K tokens) │
│     complex query → GPT-4 ($0.03/1K tokens)   │
│     classifier decides which                   │
│                                                │
│  4. Retry with backoff                         │
│     OpenAI 429 → wait + retry with jitter      │
│                                                │
│  5. Fallback                                   │
│     OpenAI down → route to Anthropic Claude    │
│                                                │
│  6. Request/response logging                   │
│     for debugging, compliance, eval            │
└────────────────────────────────────────────────┘
```

**Model routing classifier:**

A small, fast text classifier (or simple heuristics) decides which model to use:
- Query contains code → GPT-4
- Query is a simple factual question → GPT-3.5
- User is on the free tier → GPT-3.5 always
- User is on paid tier → GPT-4 for complex, GPT-3.5 for simple

This can cut LLM costs by 60–80% without significant quality degradation for most queries.

**Cost tracking schema:**
```sql
CREATE TABLE llm_usage (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id         BIGINT NOT NULL,
    conversation_id UUID NOT NULL,
    model           VARCHAR(50) NOT NULL,
    prompt_tokens   INT NOT NULL,
    completion_tokens INT NOT NULL,
    cost_usd        DECIMAL(10,6) NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    INDEX idx_user_date (user_id, created_at)
);
```

Monthly cost per user = `SUM(cost_usd) WHERE user_id = X AND created_at >= month_start`. This powers billing and quota enforcement.

---

### The Full Request Flow

```
1. User sends message via HTTP POST /v1/chat/messages
   Body: { conversation_id: "abc", message: "What is the refund policy for digital products?" }

2. Session Manager loads conversation state from Redis (or PostgreSQL on miss)
   Returns: last 10 messages, rolling summary, user tier

3. RAG Retriever (see Q9):
   - Embed the user query
   - Search vector DB for relevant chunks
   - Re-rank top-20 → top-5
   - Returns: 5 relevant context chunks

4. Prompt Builder assembles:
   - System prompt (persona, instructions)
   - Rolling summary (if conversation is long)
   - Retrieved context chunks
   - Last 10 conversation turns
   - Current user message

5. LLM Gateway receives prompt:
   - Rate limit check (user's token budget)
   - Route to GPT-4 or GPT-3.5
   - Send to OpenAI streaming API

6. Streaming response:
   - OpenAI streams tokens back
   - Gateway proxies token stream to Chat Service
   - Chat Service forwards via SSE to client
   - Client renders tokens as they arrive

7. After stream completes:
   - Store full response in messages table (async, background)
   - Update rolling summary if conversation > 10 turns (background)
   - Log token usage for billing (background)
   - Run eval checks (faithfulness, relevance) (background)
```

Steps 7+ are all async — the user gets their response before any of this happens.

---

## Scale — What Breaks at 10x?

At 1M concurrent users, 1M SSE connections:

**SSE connection limit:** 1M open HTTP connections. With HTTP/2 multiplexing, a single server can handle 100K connections. Need 10 servers + load balancer. Key: the load balancer must support sticky sessions (same user always routes to the same server to maintain the SSE connection) — or use a reverse proxy that can forward SSE streams across a connection handoff.

**OpenAI rate limits:** OpenAI has per-organization token limits (e.g., 10M tokens/minute). At 1M users × 1,000 tokens/response = 1B tokens/minute — 100x above typical limits. Solutions: batch requests (not applicable for streaming), use multiple OpenAI organizations (against ToS), self-host an open-source model (Llama 3, Mistral) on your own GPU cluster. At this scale, self-hosting makes economic sense.

**Redis for sessions:** 1M active sessions × 5KB session state = 5 GB. Fine for Redis cluster. The issue is 1M simultaneous reads at request start. Redis handles ~500K ops/sec — add read replicas, shard by `conversation_id`.

**PostgreSQL for history:** Write path is light — only write when conversation ends or on background save. Read path (loading old conversations) is index-scanned. Add read replicas. Archive conversations older than 90 days to S3 Glacier.

---

## Trade-offs

**Hosted LLM vs self-hosted:** OpenAI API is operationally simple — no GPU management. But: unpredictable latency during peak hours, data privacy concerns (all prompts go to OpenAI), no customization. Self-hosted (Llama 3 on A100 GPUs) is more complex but gives control over data, latency, and cost at scale. At 100K users, hosted is fine. At 10M users, self-hosting is often cheaper despite GPU costs.

**SSE vs WebSocket for chat:** SSE works for response streaming (server → client). But if the user wants to interrupt the generation mid-response, SSE doesn't give them a clean channel to send a "stop" signal. WebSocket is better for bidirectional interaction (user types while bot is still generating). Most production chatbots use WebSocket for this reason, despite the added complexity.

**In-memory session vs DB session:** Keeping full session state in Redis is fast but expensive for long conversations. Hybrid: keep recent turns in Redis, archive older turns to PostgreSQL. The cost of a PostgreSQL query for older turns (50ms) is acceptable since it's a rare operation (only when user asks about something from early in the conversation).

---

## Cross-Questions

**How do you prevent the chatbot from revealing confidential information from one user's conversation to another?**

Conversation isolation is enforced at every layer. Sessions are keyed by `conversation_id` which is a UUID tied to `user_id`. The Chat Service validates: does `conversation_id` belong to the authenticated user? If not, 403. The RAG retriever filters by `tenant_id` from the JWT. The LLM prompt never includes other users' data — it's assembled from only the current user's conversation history and the tenant-scoped knowledge base. There's no cross-contamination possible by design.

**How do you handle the LLM generating harmful or inappropriate content?**

Two layers. Input guardrails: classify the user's input before sending to the LLM. OpenAI's Moderation API or a custom classifier detects harmful intent (violence, illegal requests, PII extraction attempts). Reject with a 400 error before any LLM call. Output guardrails: after the LLM generates a response, run a fast classifier on the output. If it's harmful, replace with a safe fallback: "I can't help with that." Also check for PII in outputs — if the bot accidentally includes someone's email or phone number, redact before sending to the client.

**How do you debug why the chatbot gave a wrong answer?**

Every request is logged: the full prompt sent to the LLM, the retrieved chunks, the response, and all intermediate scores (retrieval similarity, re-ranking scores, faithfulness score). This is stored in an eval log table. When a user reports a bad answer, you retrieve the exact prompt and context that produced it. You can replay the request with a different model or different retrieval parameters to see what would have changed. Without this logging, debugging LLM behavior is impossible.

**What happens when the LLM's context window is exceeded?**

GPT-4's context window is 128K tokens. A 20-turn conversation with RAG context might hit 10K tokens — well within limits. But edge cases exist: user pastes a 50-page document, or the rolling summary didn't kick in at the right time. Mitigation: always measure prompt token count before sending (OpenAI's `tiktoken` library counts tokens). If over budget, apply truncation strategy: drop oldest messages first, then summarize remaining, then trim RAG context. Always preserve the system prompt and the current user message — those are non-negotiable.

**How would you implement usage-based billing?**

Token usage is logged per request in `llm_usage`. At end of billing period, `SELECT SUM(cost_usd) FROM llm_usage WHERE user_id = X AND month = current_month`. Bill accordingly. For prepaid plans: maintain a `credit_balance` in Redis. The LLM Gateway checks balance before each request. Deduct estimated cost (prompt_tokens × rate) before sending to OpenAI. If balance depletes mid-stream, finish the current response (can't interrupt mid-generation gracefully) and reject the next request with a "credits depleted" error. Top-up events add to the Redis balance and the PostgreSQL ledger atomically.
