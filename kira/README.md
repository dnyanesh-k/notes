# KIRA
- KIRA — Knowledge Intelligence Retrieval Agent

A working POC of an enterprise AI assistant with semantic knowledge routing, MCP tool calling, and persona-based guardrails. Built to demonstrate the core architecture of the KIRA platform.

---

## What it does

A user asks a question → the agent **must** call `search_kb` first → semantic search finds the most relevant knowledge card → agent reads it → answers based only on that content. Every tool call passes through a guardrail that checks persona and environment before execution.

---

## Architecture

```
User question
     │
     ▼
 search_kb (MCP tool)                 ← semantic routing via MiniLM + cosine similarity
     │                                   routing table: trigger phrases → knowledge files
     ▼
 read_file (built-in tool)            ← reads matched brain/ file
     │
     ▼
 Groq LLM (llama-3.3-70b)            ← generates answer from retrieved content only
     │
 [every tool call]
     │
 hooks.py → persona.yaml             ← checks allowed tools + environment before execution
```

**Key design points:**
- `search_kb` is enforced first — the system prompt + LLM instruction, not hardcoded logic
- Guardrails run as a separate hook, not inside the model — the model cannot bypass them
- System prompt lives in `system_prompt.md`, editable without touching code
- Brain has two card types: knowledge cards (reference) and playbooks (step-by-step procedures)
- MCP server runs as a real subprocess over stdio — same transport pattern as production

---

## Setup

```bash
pip install -r requirements.txt

# Get a free API key at https://console.groq.com (no credit card)
export GROQ_API_KEY=your_key_here        # Mac/Linux
set GROQ_API_KEY=your_key_here           # Windows CMD
$env:GROQ_API_KEY = "your_key_here"      # Windows PowerShell
```

> First run downloads the MiniLM embedding model (~100MB). One-time only, then cached.

---

## Run

```bash
python run.py                            # engineer persona, dev environment
python run.py --persona viewer           # read-only — bash tool is blocked
python run.py --persona engineer --env staging
```

**Try these questions:**
```
How do I deploy my service to Kubernetes?
My pod is in CrashLoopBackOff — what do I check?
There is a production outage — what are the steps?
```

**Test the guardrail** — run as viewer and ask something that would trigger bash:
```
python run.py --persona viewer
> My pod is failing, run kubectl get pods
```
You will see: `[Guardrail] BLOCKED — Tool 'bash' is explicitly denied for persona 'viewer'`

---

## Test individual components

```bash
python routing_core.py     # smoke test: search for "deploy service" and see scores
python hooks.py            # smoke test: prints allow/block decisions for 3 test cases
python mcp_server.py       # run MCP server standalone (Ctrl+C to stop)
```

---

## File structure

```
kira/
├── requirements.txt
├── system_prompt.md          — agent rules and persona, loaded at runtime
├── persona.yaml              — viewer / engineer: allowed tools + environments
├── run.py                    — entry point: MCP client + Groq agent loop + guardrails
├── mcp_server.py             — FastMCP server exposing search_kb over stdio
├── routing_core.py           — MiniLM embeddings + cosine similarity search
├── hooks.py                  — pre-tool authorization: persona × environment × tool
└── brain/
    ├── routing.md            — trigger table → knowledge file mapping
    ├── knowledge_card.md     — reference card: deploy, pods, docker commands
    └── playbook_incident_response.md  — step-by-step production incident procedure
```

---

## Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Embeddings | MiniLM (fastembed) | Small, fast, runs offline on CPU |
| Similarity | NumPy cosine | Sufficient at this scale, no vector DB needed |
| MCP | FastMCP (stdio) | Same protocol as production KIRA |
| LLM | Groq + llama-3.3-70b | Free tier, fast inference, OpenAI-compatible API |
| Guardrails | hooks.py + persona.yaml | Code-enforced, not prompt-based |


>In the POC I kept external integrations out intentionally — the goal was to demonstrate the routing, MCP, and guardrail layers cleanly without needing credentials or risking side effects. In production, the same agent calls Jira, AWS, and kubectl through the same tool interface — the architecture is identical, just more tools registered.