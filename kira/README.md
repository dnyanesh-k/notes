# KIRA Mini

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
- Hot-reload: a background thread watches `brain/routing.md`; when the file changes it rebuilds the index in the background and atomically swaps the reference — no query ever hits a partial index
- Mock proxy: evals intercept tool calls and return canned responses from the scenario YAML — the LLM reasoning runs for real, only tool results are faked, making evals fast and deterministic

---

## How it works — Key Concepts

### 1. Multi-phrase embedding
Each routing entry in `brain/routing.md` has a trigger like:
```
deploy service, kubernetes deployment, release new version, kubectl deploy
```
This gets split into 4 individual phrases **plus** the full string kept as-is — 5 texts total.
MiniLM embeds each one into a 384-dimensional vector, producing a matrix of shape `[5, 384]`.

At search time, the user's query (e.g. "how do I push my service?") is embedded to `[1, 384]`.
The dot product of query × all 5 phrase vectors gives 5 similarity scores. The **maximum** score wins for that entry. This means a partial match against any one phrase is enough to surface the card — you don't need to match the full trigger string.

### 2. Cosine similarity and the threshold
Vectors are unit-normalized before storage, so dot product = cosine similarity (range −1 to 1, typically 0–1 for language).
Any entry scoring **below 0.40** is dropped before the result reaches the agent. This prevents weakly related cards from polluting the context. The threshold is tunable — lower it and more cards pass through; raise it and only high-confidence matches survive.

### 3. Hot-reload — atomic swap
When the agent is running and you edit `brain/routing.md`, a background thread detects the file change via `mtime` polling every 2 seconds. It builds a **new index object** in the background while the old one stays live and serves queries. Only when the new index is fully built does it swap the reference (`_index = new_index`) under a lock. No query ever reads a partially built index. `brain/index_snapshot.json` is rewritten at the same moment — open it in your editor to watch the index update live.

### 4. Agent loop (ReAct pattern)
The agent does not answer immediately. It loops:
```
Think → call a tool → observe result → think again → … → answer
```
The LLM decides which tool to call and with what arguments. The loop continues until the model produces a response with no tool calls. The system prompt instructs the model to always call `search_kb` first — this is an instruction to the LLM, not a hardcoded check. The hard gate in eval verifies the model actually followed it.

### 5. Guardrails — persona × environment × tool
Every tool call passes through `hooks.py` before execution. It checks three things in order:
- Is the environment allowed for this persona? (`viewer` → dev only)
- Is the tool explicitly denied? (`bash` is denied for `viewer`)
- Is the tool explicitly allowed? (if not in allow list, default block)

The model never sees this logic — it cannot bypass it by rephrasing its output.

### 6. Mock proxy
During eval, real tool calls are expensive and non-deterministic. The mock proxy intercepts tool calls at the execution layer in `_agent_loop` and returns pre-defined strings from the scenario YAML instead. The LLM reasoning still runs against real Groq. Only the tool results are faked. This makes evals run in seconds and produce identical results on every run — same input, same tool output, same LLM behaviour.

### 7. Hard gates vs LLM critic
Two different kinds of checks serve different purposes:

| | Hard gate | LLM critic |
|---|---|---|
| What it checks | Did the agent behave correctly? | Was the answer good? |
| Example | `search_kb` called first | Topics covered, not hallucinated |
| Output | Pass / Fail (binary) | Score 0–100 |
| Speed | Instant (trace inspection) | One LLM call |

A scenario must pass **both** to be considered passing.

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
## Eval Framework

The eval system tests the full agent loop without a human in the loop. Run all scenarios:

```bash
python evals/run_evals.py                         # run all scenarios
python evals/run_evals.py --scenario deploy_service  # run one
```

Each scenario YAML defines three things:

```yaml
prompt: "How do I deploy my service to Kubernetes?"

hard_gates:
  search_kb_must_be_first: true      # agent must call search_kb before anything else
  required_cards: [knowledge_card.md]  # this file must be read by the agent

expected_topics: [docker build, kubectl apply, rollout status]
expected_answer_theme: "build image, push, deploy, verify"
pass_threshold: 75
```

**How scoring works:**

```
Hard gates (binary — fail immediately if violated)
  ├── Was search_kb the first tool called?
  └── Did the agent read all required knowledge cards?

LLM Critic (0–100)
  ├── Correctness  /40  — does the answer solve the problem?
  ├── Completeness /30  — are expected topics covered?
  └── Groundedness /30  — is the answer based on retrieved knowledge, not hallucinated?

Scenario passes if: no gate failures AND critic total ≥ pass_threshold
```

Sample output:
```
  ═══════════════════════════════════════════════════════
  Scenario : deploy_service
  Status   : ✓  PASS   (need ≥75, got 88/100)
  ─────────────────────────────────────────────────────
  Hard gates  : all passed
  ─────────────────────────────────────────────────────
  Correctness  36/40  ████████████████████░░░░
  Completeness 27/30  ████████████████████░░░
  Groundedness 25/30  ██████████████████░░░░░
  Total        88/100
```

**Mock proxy** — each scenario YAML includes canned `mock_responses` for `search_kb` and `read_file`. The eval runner passes these to the agent loop instead of calling real tools. No MiniLM warm-up, no MCP subprocess overhead — evals finish in seconds and produce the same result every run.

Add a new scenario by creating `evals/scenarios/your_name.yaml` — no code changes needed.

---

## File structure

```
mini-KIRA/
├── requirements.txt
├── system_prompt.md          — agent rules and persona, loaded at runtime
├── persona.yaml              — viewer / engineer: allowed tools + environments
├── run.py                    — entry point: MCP client + Groq agent loop + guardrails
├── mcp_server.py             — FastMCP server exposing search_kb over stdio
├── routing_core.py           — MiniLM embeddings + cosine similarity search
├── hooks.py                  — pre-tool authorization: persona × environment × tool
├── brain/
│   ├── routing.md            — trigger table → knowledge file mapping
│   ├── knowledge_card.md     — reference card: deploy, pods, docker commands
│   └── playbook_incident_response.md  — step-by-step production incident procedure
└── evals/
    ├── critic.py             — LLM-as-judge scorer (correctness/completeness/groundedness)
    ├── run_evals.py          — eval orchestrator: hard gates + critic + summary report
    └── scenarios/
        ├── deploy_service.yaml
        └── incident_response.yaml
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
| Eval | Hard gates + LLM critic | Binary behaviour check + semantic quality score |
| Hot-reload | Background thread + atomic swap | Index stays live during rebuild, zero downtime |
| Mock proxy | Canned YAML responses | Evals run fast, offline, deterministic |
