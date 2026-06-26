# Q10: Design LLM Chatbot at Scale (ChatGPT-like)

---

## Introduction

An LLM-based chatbot at scale is a system that lets users have multi-turn conversations with a large language model — asking follow-up questions, referencing earlier parts of the conversation, and receiving coherent, context-aware responses. ChatGPT, Claude, and Gemini are the most visible examples, but the same architecture powers customer support bots, coding assistants, and internal Q&A tools inside organizations.

The core challenge is **context management**. Unlike a stateless API request, a conversation has history. The model needs to see previous messages to understand what the user is referring to. LLMs process a fixed-length context window — currently ranging from 8K to 200K tokens depending on the model. Every conversation turn, the system must decide what history to include, how to truncate or summarize older messages when the conversation grows too long, and how to store and retrieve that history efficiently.

At scale, inference is the dominant cost and latency bottleneck. LLMs are computationally expensive — running a single query against GPT-4 class models costs orders of magnitude more than a standard database lookup. The system must balance response quality (larger, more capable models), latency (streaming tokens to the user immediately rather than waiting for the full response), and cost (batching, caching repeated prompts, routing simple queries to smaller cheaper models).

Streaming is expected in production. Users should see tokens appearing word by word rather than waiting 10–20 seconds for a complete response. This requires server-sent events or WebSocket connections and changes how the frontend renders responses.

Session management, multi-user isolation, abuse prevention, content moderation, and prompt injection defense are all required in a production design. For enterprise deployments, conversation history must also be auditable and deletable to satisfy compliance requirements.

---

## How to Approach This in an Interview

LLM chatbot combines everything: RAG (Q9), streaming, session management, and cost control. The unique challenges here are: how do you stream tokens without dropping the connection (SSE), how do you manage conversation memory without ballooning prompt costs, and how do you control LLM API costs at scale (which is genuinely the limiting factor at production scale). Focus on these three.

---

## Clarifying Questions

**1. General purpose or domain-specific?**

"Is this a general chatbot that answers anything from training data, or a domain-specific chatbot grounded in your company's knowledge base?"

*Why this matters:* General = just call the LLM. Domain-specific = need RAG (Q9) to ground answers in your knowledge base. Most enterprise chatbots are domain-specific to avoid hallucination.

**2. Multi-turn with memory?**

"Should the chatbot remember what was said earlier in the conversation? And how long — 5 turns or 100?"

*Why this matters:* Multi-turn requires sending conversation history with each request. At 50 turns × 200 tokens/turn = 10,000 tokens of history — significant cost. Needs summarization strategy.

**3. Streaming or batch responses?**

"Should tokens appear one by one as generated (like ChatGPT), or wait for the full response?"

*Why this matters:* Streaming needs SSE/WebSocket infrastructure. Without streaming, a 500-token response takes 16 seconds of staring at a spinner. Streaming reduces perceived latency by 10x.

**4. Scale?**

"How many concurrent users? Peak concurrent conversations?"

*Why this matters:* Each streaming response holds an open HTTP connection. 100K concurrent connections = specific server configuration needed (async, non-blocking).

### Assumptions

```
- Domain-specific chatbot with RAG-grounded answers
- Multi-turn conversation: 20-turn memory window
- Streaming token delivery (SSE)
- 100K concurrent users
- Hosted LLM (OpenAI GPT-4 / Anthropic Claude) via API
- Multi-tenant (multiple organizations, isolated knowledge bases)
- Sub-2-second time-to-first-token (TTFT) target
```

---

## Back-of-Envelope Math

```
100K concurrent users
Each user active for ~5 minutes in a conversation
= 100K conversations active at once

LLM tokens per turn:
  Prompt: system (200) + history (2,000) + context (2,560) + question (100) = 4,860 tokens
  Response: 500 tokens
  Total per turn: 5,360 tokens

Cost (GPT-4 at $0.03/1K tokens):
  5,360 tokens × $0.03 / 1,000 = $0.161 per turn
  If each user makes 5 turns/conversation:
  $0.161 × 5 × 100K users = $80,500 per day (for 100K concurrent users)
  
  This is the dominant cost. Reducing LLM calls via caching is the #1 lever.

SSE connections:
  100K concurrent SSE connections
  Each holds an HTTP/2 stream
  1 server handles ~10K connections (with async Python/Go)
  Need 10 servers
```

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
  Redis     — active sessions (hot path), semantic response cache
  PostgreSQL — conversation history, user preferences, billing records
  S3        — long-term conversation archive (> 90 days)
```

---

## Part 1: Streaming with Server-Sent Events (SSE)

**Why streaming matters for UX:**

Without streaming: LLM takes 16 seconds to generate a 500-token response. User stares at a spinner for 16 seconds, then the entire response appears at once.

With streaming: First token appears within 1-2 seconds. User sees the response being "typed" in real-time. Even though total generation time is the same 16 seconds, perceived experience is dramatically better.

**What is SSE (Server-Sent Events)?**

SSE is a standard HTTP mechanism for unidirectional streaming from server to client. Unlike WebSocket (bidirectional), SSE works over a single HTTP response that stays open:

```
HTTP Protocol:
  Client: GET /v1/chat/stream
          Accept: text/event-stream
          Authorization: Bearer {token}
  
  Server: HTTP/1.1 200 OK
          Content-Type: text/event-stream
          Cache-Control: no-cache
          Connection: keep-alive
          
          data: {"token": "The", "done": false}\n\n
          
          data: {"token": " refund", "done": false}\n\n
          
          data: {"token": " policy", "done": false}\n\n
          
          (... continues token by token ...)
          
          data: {"token": ".", "done": true, "usage": {"prompt_tokens": 4860, "completion_tokens": 87}}\n\n
```

The `\n\n` (double newline) is the SSE event delimiter. The browser's `EventSource` API parses these automatically.

**Client JavaScript:**

```javascript
const eventSource = new EventSource('/v1/chat/stream', {
  headers: { 'Authorization': `Bearer ${token}` }
});

let responseText = '';

eventSource.addEventListener('message', (event) => {
  const data = JSON.parse(event.data);
  
  if (data.done) {
    eventSource.close();
    // Optionally: save conversation turn to localStorage
  } else {
    responseText += data.token;
    // Update UI: append token to the displayed message
    document.getElementById('response').textContent = responseText;
  }
});

eventSource.addEventListener('error', () => {
  // Connection closed or error — handle reconnection
  eventSource.close();
});
```

**Server-side streaming implementation:**

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/v1/chat/messages")
async def chat_stream(request: ChatRequest, user = Depends(get_current_user)):
    async def generate_stream():
        # Step 1: Load session
        session = await session_manager.get_session(request.conversation_id, user.id)
        
        # Step 2: RAG retrieval (see Q9)
        context_chunks = await rag_retriever.retrieve(
            query=request.message,
            tenant_id=user.tenant_id
        )
        
        # Step 3: Build prompt
        prompt = build_prompt(
            query=request.message,
            context=context_chunks,
            history=session.recent_messages,
            summary=session.rolling_summary
        )
        
        # Step 4: Stream from OpenAI
        full_response = ""
        async for chunk in openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=prompt,
            stream=True,
            max_tokens=500,
            temperature=0.1
        ):
            token = chunk.choices[0].delta.content
            if token:
                full_response += token
                # Send this token to the client as SSE
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
        
        # Stream complete
        yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"
        
        # Post-stream work (async, doesn't block the client)
        asyncio.create_task(save_conversation_turn(
            request.conversation_id,
            request.message,
            full_response,
            context_chunks
        ))
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        }
    )
```

**Why SSE over WebSocket for chatbots?**

SSE is unidirectional (server → client), which is all we need for streaming responses. It works over standard HTTP/2, which means: CDN compatibility, standard load balancers work, no special WebSocket configuration needed.

WebSocket is better if: users need to interrupt mid-generation (send a "stop" signal), or bidirectional events are needed. Most chatbots start with SSE, upgrade to WebSocket when needed.

**The `X-Accel-Buffering: no` header:**

Nginx buffers responses by default — it waits to accumulate data before sending to the client. This completely defeats streaming. This header tells Nginx to forward chunks immediately without buffering.

---

## Part 2: Conversation Memory

**The token cost problem:**

Each turn of conversation history adds ~200 tokens to the prompt. After 20 turns: 4,000 tokens just for history. At $0.03/1K tokens, that's $0.12 per turn just for history — 75% of the total cost.

**Strategy 1: Fixed sliding window (simplest)**

Keep only the last N turns. Simple but suffers from "memory cliff" — if user asks "remember when I said X earlier?" and X was 21 turns ago, the chatbot has no memory.

```python
WINDOW_SIZE = 10  # keep last 10 turns

def get_context_messages(history: list[dict]) -> list[dict]:
    return history[-WINDOW_SIZE:]  # take last 10
```

**Strategy 2: Rolling summarization (better)**

After every 10 turns, ask the LLM to summarize the conversation so far. Use the summary instead of full history for older turns.

```python
async def check_and_summarize(conversation_id: str, messages: list[dict]):
    if len(messages) % 10 == 0 and len(messages) > 10:
        # Every 10 turns, summarize the oldest 10
        turns_to_summarize = messages[:-10]  # all except last 10
        
        summary_prompt = f"""
        Summarize this conversation in 2-3 concise sentences, preserving:
        - Key information the user shared
        - Important topics discussed
        - Any commitments or decisions made
        
        Conversation:
        {format_conversation(turns_to_summarize)}
        """
        
        new_summary = await llm_cheap.complete(summary_prompt, max_tokens=200)
        
        # Update the session's rolling summary
        await session_store.update_summary(conversation_id, new_summary)

def build_prompt_with_summary(query: str, history: list[dict], 
                               summary: Optional[str], context: list[str]) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if summary:
        # Add summary of older conversation
        messages.append({
            "role": "system",
            "content": f"Earlier in this conversation: {summary}"
        })
    
    # Add recent context (RAG chunks)
    if context:
        messages.append({
            "role": "system",
            "content": f"Relevant knowledge base information:\n{format_chunks(context)}"
        })
    
    # Add recent conversation history (last 10 turns)
    messages.extend(history[-10:])
    
    # Add current question
    messages.append({"role": "user", "content": query})
    
    return messages
```

**Token comparison:**

```
Without summarization (20 turns):
  20 turns × 200 tokens = 4,000 tokens of history

With summarization (20 turns):
  10 recent turns × 200 = 2,000 tokens
  Summary of first 10 turns = 200 tokens
  Total history: 2,200 tokens — 45% reduction

After 50 turns:
  Without: 50 × 200 = 10,000 tokens of history
  With: 10 recent turns (2,000) + 4 summarized blocks (800) = 2,800 tokens
  78% reduction in history tokens
```

---

## Part 3: Session Management

**What needs to persist in a session?**

```python
@dataclass
class ConversationSession:
    conversation_id: str
    user_id: str
    tenant_id: str
    
    # The conversation itself
    messages: list[dict]        # full list of turns
    rolling_summary: str        # summary of older turns
    
    # Context
    user_preferences: dict      # preferred language, verbosity level
    
    # Metadata
    created_at: datetime
    last_active_at: datetime
    token_count_total: int      # for billing
```

**Two-tier storage:**

```python
class SessionManager:
    def get_session(self, conversation_id: str, user_id: str) -> ConversationSession:
        # Hot path: check Redis first (active session)
        cached = redis.get(f"session:{conversation_id}")
        if cached:
            return deserialize(cached)
        
        # Cold path: load from PostgreSQL
        session_data = pg.query(
            "SELECT * FROM conversations WHERE id = ? AND user_id = ?",
            (conversation_id, user_id)
        )
        
        if not session_data:
            raise NotFoundError("Conversation not found")
        
        messages = pg.query(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,)
        )
        
        session = ConversationSession(
            conversation_id=conversation_id,
            messages=messages,
            rolling_summary=session_data.summary,
            ...
        )
        
        # Cache in Redis for next request (1-hour TTL)
        redis.setex(f"session:{conversation_id}", 3600, serialize(session))
        
        return session
    
    async def save_turn(self, conversation_id: str, user_msg: str, 
                        assistant_msg: str, tokens_used: int):
        """Called after stream completes. Non-blocking."""
        
        # Update Redis immediately (next request needs this)
        session = await self.get_session(conversation_id, ...)
        session.messages.append({"role": "user", "content": user_msg})
        session.messages.append({"role": "assistant", "content": assistant_msg})
        session.last_active_at = datetime.now()
        redis.setex(f"session:{conversation_id}", 3600, serialize(session))
        
        # Persist to PostgreSQL (slightly slower, background task)
        await pg.execute(
            "INSERT INTO messages (conversation_id, role, content, token_count, created_at) VALUES ...",
            ...
        )
        
        # Trigger summarization if needed
        await check_and_summarize(conversation_id, session.messages)
```

**PostgreSQL schema:**

```sql
CREATE TABLE conversations (
    id              UUID         PRIMARY KEY,
    user_id         BIGINT       NOT NULL,
    tenant_id       VARCHAR(100) NOT NULL,
    summary         TEXT,                    -- rolling summary of older turns
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    last_active_at  TIMESTAMP    NOT NULL DEFAULT NOW(),
    token_count     INT          DEFAULT 0,  -- total tokens used (for billing)
    
    INDEX idx_user (user_id, last_active_at DESC),
    INDEX idx_tenant (tenant_id, last_active_at DESC)
);

CREATE TABLE messages (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID         NOT NULL REFERENCES conversations(id),
    role            VARCHAR(20)  NOT NULL,    -- 'user', 'assistant', 'system'
    content         TEXT         NOT NULL,
    token_count     INT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    
    INDEX idx_conversation (conversation_id, created_at ASC)
);
```

---

## Part 4: LLM Gateway

The LLM Gateway is a layer between your Chat Service and OpenAI/Anthropic. It handles cross-cutting concerns that shouldn't live in application code:

```
┌──────────────────────────────────────────────────────────────┐
│                        LLM Gateway                           │
│                                                              │
│  Input:  prompt, model_hint, user_context                    │
│                                                              │
│  1. Rate Limiting (per user, per tenant)                     │
│     "User X is on free tier: max 20 messages/day"            │
│     Check Redis counter: user_x today = 18 → allow           │
│                                                              │
│  2. Cost Estimation                                          │
│     Count prompt tokens (tiktoken): 4,860 tokens            │
│     Estimated cost: 4,860 × $0.03/1K = $0.146               │
│     Would this exceed user's budget? → proceed              │
│                                                              │
│  3. Model Routing                                            │
│     Is the query complex? Contains code? User on paid tier?  │
│     → Route to GPT-4 or GPT-3.5                              │
│     (80% of queries → GPT-3.5 → 15x cheaper)                │
│                                                              │
│  4. Retry with Backoff                                       │
│     OpenAI 429 (rate limited) → wait 1s → retry → wait 5s   │
│                                                              │
│  5. Fallback                                                 │
│     OpenAI timeout → try Anthropic Claude                    │
│     Claude timeout → return graceful error                   │
│                                                              │
│  6. Token Counting + Billing                                 │
│     After response: actual tokens = prompt + completion      │
│     Log to llm_usage table for billing                       │
│                                                              │
│  Output: streamed response or error                          │
└──────────────────────────────────────────────────────────────┘
```

**Model routing classifier:**

```python
def select_model(query: str, user_tier: str, estimated_complexity: str) -> str:
    # Rules-based routing (simple, cheap, fast)
    
    if user_tier == "free":
        return "gpt-3.5-turbo"  # always use cheap model for free users
    
    # Check for complexity signals
    if any([
        len(query) > 500,                         # long question
        "```" in query,                           # contains code
        any(w in query.lower() for w in ["analyze", "compare", "summarize complex"]),
        estimated_complexity == "high"
    ]):
        return "gpt-4-turbo"  # complex query needs smarter model
    
    return "gpt-3.5-turbo"  # default: cheap model

# Cost impact of model routing:
# Without routing: 100% GPT-4 → $80,500/day (example from above)
# With routing (80% GPT-3.5, 20% GPT-4):
#   GPT-3.5: 80K users × $0.013/turn × 5 turns = $5,200
#   GPT-4:   20K users × $0.161/turn × 5 turns = $16,100
#   Total: $21,300 → 74% cost reduction
```

---

## The Full Request Flow

```
Step 1: Client sends POST /v1/chat/messages
        { conversation_id: "abc", message: "What is the return policy for digital products?" }
        Opens SSE connection to receive streaming response

Step 2: Session Manager loads conversation state
        Redis hit → 0.5ms
        Returns: { last_10_messages, rolling_summary, user_tier: "paid" }

Step 3: RAG Retriever (from Q9)
        Check semantic cache → miss (new question)
        Embed query → ANN search → cross-encoder rerank
        Returns: 5 relevant chunks about return policy
        Time: ~130ms

Step 4: LLM Gateway
        Count tokens: 4,860 prompt tokens
        Route: no code, not too long → GPT-3.5-turbo
        Check rate limit: user has 15/20 messages used today → allow

Step 5: Prompt Assembly
        System prompt (200 tokens)
        + Rolling summary (if any)
        + Retrieved context (2,560 tokens)
        + Last 10 conversation turns (2,000 tokens)
        + Current question (50 tokens)
        Total: 4,810 tokens

Step 6: OpenAI streaming call
        First token arrives: 800ms after request (TTFT)
        Tokens stream at ~30 tokens/second
        Each token forwarded via SSE to client immediately
        Client renders tokens as they arrive

Step 7: Stream completes (87 completion tokens, 1,800ms later)
        Send done event: { "done": true, "usage": { "prompt": 4810, "completion": 87 } }

Step 8: Post-stream async tasks (don't block client):
        - Save turn to PostgreSQL (50ms)
        - Update Redis session (5ms)
        - Log to llm_usage (billing): 4,897 tokens × $0.002/1K = $0.0098
        - Update Redis cache: store response for semantic cache
        - Trigger summarization if 10 turns reached
        - Run faithfulness eval (background, for quality monitoring)

Client experience:
  First token: 0.9 seconds after sending (TTFT)
  Full response: 3.7 seconds
  With streaming: perceived as "instant" (vs 3.7 seconds without)
```

---

## Scale — What Breaks at 10x?

10x = 1M concurrent users, 1M SSE connections.

**SSE connections:** Each SSE connection is a persistent HTTP connection. With HTTP/2 multiplexing, one TCP connection can host multiple streams. But for chatbots, each user has exactly one active stream at a time. 1M connections × 1KB state each = 1 GB just for connection state.

Solutions:
- **Async server (FastAPI + uvicorn, Go, Node.js):** Handle 100K connections per server (async IO, no thread per connection). Need 10 servers.
- **Sticky sessions:** SSE connection is stateful — the same user must always route to the same server during an active stream. Load balancer must support sticky sessions (cookie or IP hash).

**OpenAI rate limits:** OpenAI enforces token-per-minute limits per organization. At 1M users, you'll need to negotiate custom limits with OpenAI or self-host.

**Redis session store:** 1M active sessions × 10KB state = 10 GB. Fine for Redis. 1M concurrent reads at stream start (all loading sessions simultaneously) = 1M ops/sec. Need Redis cluster: 3-5 nodes, shard by `conversation_id`.

**PostgreSQL message history:** Write-heavy only at stream completion (one INSERT per turn). 1M turns/session × 5 turns/session = 5M inserts per active period. Not simultaneous — staggered as conversations complete. Add write batching (collect 1,000 inserts, write in one transaction) and read replicas for session loading.

---

## Trade-offs

**Hosted LLM vs self-hosted:**

| | Hosted (OpenAI/Anthropic) | Self-hosted (Llama 3 70B) |
|---|---|---|
| Quality | GPT-4 class | Near-GPT-4 quality |
| Operational work | None | GPU cluster management |
| Data privacy | Prompts go to OpenAI | Full control |
| Cost at 1M users | ~$80K/day | ~$5K/day (GPU amortized) |
| Customization | Fine-tuning only | Full fine-tuning, RAG tuning |

At 100K users: hosted is fine (simplicity > cost). At 1M users: self-hosting pays for itself.

**SSE vs WebSocket for streaming:**

SSE: simpler, works over HTTP/2, standard load balancer support. Can't interrupt generation mid-stream (client can close connection, but server continues generating for a bit).

WebSocket: bidirectional — client can send "stop generating" signal. Better for interactive use cases. More complex routing through load balancers and Kubernetes ingress.

Most chatbots start with SSE, upgrade to WebSocket when users complain about inability to stop generation.

---

## Cross-Questions

**Q: What exactly happens if the user's context window is exceeded?**

GPT-4's context window is 128K tokens. A heavy user with 100 turns of history + RAG context might hit 50K tokens — still fine but expensive.

If they somehow exceed 128K:

```python
def build_prompt_safe(query, history, context, summary) -> list[dict]:
    import tiktoken
    encoder = tiktoken.encoding_for_model("gpt-4")
    
    CONTEXT_LIMIT = 120000  # leave 8K for response
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Always include: current question + retrieved context (non-negotiable)
    required_tokens = count_tokens(query) + count_tokens(context)
    remaining_budget = CONTEXT_LIMIT - required_tokens
    
    # Add summary (compact history)
    if summary and count_tokens(summary) < remaining_budget:
        messages.append({"role": "system", "content": f"Earlier context: {summary}"})
        remaining_budget -= count_tokens(summary)
    
    # Add recent history (until budget runs out)
    for turn in reversed(history):  # newest first
        turn_tokens = count_tokens(turn)
        if turn_tokens > remaining_budget:
            break
        messages.insert(-1, turn)  # insert before current question
        remaining_budget -= turn_tokens
    
    messages.append({"role": "user", "content": query})
    return messages
```

Always preserve: the current question and retrieved context. Trim: old conversation history. Never send a prompt that exceeds the context window.

**Q: How do you prevent one user's conversation data from leaking into another user's context?**

Multiple enforcement layers:

1. **Session key isolation:** Sessions are keyed by `conversation_id` which is a UUID. The session manager validates `conversation_id.user_id == authenticated_user_id`. Different users can't access each other's sessions.

2. **RAG filtering:** Vector DB queries filter by `tenant_id` from JWT. User A's knowledge base data never appears in User B's query results.

3. **Prompt construction:** The prompt is assembled from only the current user's session data + current tenant's knowledge base. No cross-user data is ever included.

4. **LLM statelessness:** OpenAI's API is stateless — it doesn't remember previous requests. Each API call is independent. Two users' prompts never mix.

**Q: How do you handle the chatbot generating harmful content?**

Two layers:

**Input guard (before LLM call):**

```python
def check_input(user_message: str) -> GuardResult:
    # OpenAI Moderation API (free, ~50ms)
    mod = openai.moderations.create(input=user_message)
    
    if mod.results[0].flagged:
        return GuardResult.REJECT("Request violates usage policy")
    
    # Custom classifier for domain-specific restrictions
    if is_out_of_scope(user_message):
        return GuardResult.REJECT("This is outside the scope of what I can help with")
    
    return GuardResult.ALLOW
```

**Output guard (after LLM response):**

```python
def check_output(response: str, context: list[str]) -> str:
    # Check if response contains PII (emails, phone numbers, SSNs)
    response = pii_redactor.redact(response)
    
    # Check faithfulness: does response use only retrieved context?
    faithfulness = compute_faithfulness(response, context)
    if faithfulness < 0.6:
        return "I found relevant information but I'm not confident enough to answer accurately."
    
    return response
```

For the most sensitive cases (healthcare, legal), add a review queue: responses with confidence < 0.8 are flagged for human review before being sent to the user.

**Q: How would you implement usage-based billing?**

```python
# Log every LLM call to billing database
async def log_llm_usage(user_id: str, conversation_id: str, 
                         model: str, prompt_tokens: int, 
                         completion_tokens: int):
    
    MODEL_PRICES = {
        "gpt-4-turbo": {"input": 0.03, "output": 0.06},   # per 1K tokens
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    }
    
    price = MODEL_PRICES[model]
    cost_usd = (
        prompt_tokens * price["input"] / 1000 +
        completion_tokens * price["output"] / 1000
    )
    
    await pg.execute("""
        INSERT INTO llm_usage 
        (user_id, conversation_id, model, prompt_tokens, completion_tokens, cost_usd, created_at)
        VALUES (?, ?, ?, ?, ?, ?, NOW())
    """, (user_id, conversation_id, model, prompt_tokens, completion_tokens, cost_usd))
    
    # Update user's monthly total in Redis (fast check for quota enforcement)
    month_key = f"usage:{user_id}:{datetime.now().strftime('%Y-%m')}"
    redis.incrbyfloat(month_key, cost_usd)
    redis.expireat(month_key, end_of_month())

# Check quota before each LLM call
def check_quota(user_id: str, user_plan: str) -> bool:
    PLAN_LIMITS = {"free": 1.0, "starter": 10.0, "pro": 100.0}  # USD/month
    
    month_key = f"usage:{user_id}:{datetime.now().strftime('%Y-%m')}"
    current_spend = float(redis.get(month_key) or 0)
    
    return current_spend < PLAN_LIMITS[user_plan]
```

This powers: billing dashboards (total cost by user, by model), quota enforcement (stop user at plan limit), and cost optimization analytics (which queries cost the most?).
