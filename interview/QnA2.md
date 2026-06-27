# AI Engineering — Production Deep Dive

> This file covers production AI engineering concepts at implementation depth. Every answer is grounded in KIRA's actual code. Read QnA.md first for KIRA system overview and core concepts. Read GenAI.md for generic LLM concepts. This file is for the questions that separate a junior AI developer from a production AI engineer.

---

## Table of Contents

- [Q1. What is HITL and how do you implement it in a production agent?](#q1-what-is-hitl-and-how-do-you-implement-it-in-a-production-agent)
- [Q2. What is memory management in an LLM agent and how do you implement it?](#q2-what-is-memory-management-in-an-llm-agent-and-how-do-you-implement-it)
- [Q3. What is context engineering and how do you handle context compaction in a long-running agent?](#q3-what-is-context-engineering-and-how-do-you-handle-context-compaction-in-a-long-running-agent)
- [Q4. How do you implement RBAC for an AI agent?](#q4-how-do-you-implement-rbac-for-an-ai-agent)
- [Q5. How does multi-agent DAG orchestration work?](#q5-how-does-multi-agent-dag-orchestration-work)
- [Q6. How do you implement multi-tenancy in an AI agent system?](#q6-how-do-you-implement-multi-tenancy-in-an-ai-agent-system)
- [Q7. What is fail-closed design and why does it matter for AI agents?](#q7-what-is-fail-closed-design-and-why-does-it-matter-for-ai-agents)
- [Q8. How do you implement observability and audit trails for an AI agent?](#q8-how-do-you-implement-observability-and-audit-trails-for-an-ai-agent)
- [Q9. How do you handle structured output and schema validation in an agent?](#q9-how-do-you-handle-structured-output-and-schema-validation-in-an-agent)
- [Q10. How do you handle agent retry and error propagation?](#q10-how-do-you-handle-agent-retry-and-error-propagation)
- [Q11. How do you build an eval framework for an AI agent?](#q11-how-do-you-build-an-eval-framework-for-an-ai-agent)
- [Q12. What is the difference between prompt caching and semantic caching?](#q12-what-is-the-difference-between-prompt-caching-and-semantic-caching)
- [Q13. What is KV Cache in transformers and why does it matter?](#q13-what-is-kv-cache-in-transformers-and-why-does-it-matter)
- [Q14. How do you measure retrieval quality — RAGAS, MRR, Recall@K?](#q14-how-do-you-measure-retrieval-quality--ragas-mrr-recallk)
- [Q15. How do you build an LLM-as-judge evaluator?](#q15-how-do-you-build-an-llm-as-judge-evaluator)
- [Q16. What agentic patterns exist beyond ReAct?](#q16-what-agentic-patterns-exist-beyond-react)
- [Q17. What are the 4 types of memory in an agentic system?](#q17-what-are-the-4-types-of-memory-in-an-agentic-system)
- [Q18. How do you design a good tool schema for an AI agent?](#q18-how-do-you-design-a-good-tool-schema-for-an-ai-agent)
- [Q19. What is quantization and how does RLHF align LLMs?](#q19-what-is-quantization-and-how-does-rlhf-align-llms)
- [Q20. How do you deploy an AI agent to production?](#q20-how-do-you-deploy-an-ai-agent-to-production)

---

## Q1. What is HITL and how do you implement it in a production agent?

### What it is

HITL — Human-in-the-Loop — is a design pattern where an AI agent pauses execution and waits for explicit human approval before taking an action that cannot be easily undone. It is not a confidence scorer or a soft suggestion. It is a hard gate: the action does not happen until a human says yes.

The reason HITL exists is simple: autonomous agents make mistakes, and some mistakes are irreversible. Deleting a database record, sending an email to a customer, merging a pull request, running `terraform apply` in production — none of these can be undone with a simple rollback. For these actions, you need a human checkpoint regardless of how confident the model is. A model that is 95% confident and wrong is still wrong.

HITL sits at the **action boundary** — between the agent deciding what to do and the agent actually doing it. Everything before this point (reasoning, tool reads, data gathering) runs autonomously. Only write operations or destructive actions require the pause.

**Two types of HITL:**
1. **Pre-execution approval** — agent plans the action, shows it to the user, waits for "yes" before executing. This is the standard pattern.
2. **Post-execution review** — agent executes, human reviews the result and either accepts or triggers a rollback. Used when the action is safe to attempt but the output needs verification (e.g. a drafted email before sending).

---

### How KIRA implements it

KIRA has two independent HITL mechanisms working at different levels.

**Mechanism 1 — DAG node approval (`dag_engine.py`)**

Every node in KIRA's DAG has a `mutating` flag. When a node is flagged as mutating, it requires explicit `dag_approve()` before the `complete()` call will succeed. No confidence score, no threshold — if `mutating=True`, the gate is always active.

```
flowchart LR
    A["dag_next() returns runnable nodes"] --> B{node.mutating?}
    B -- No --> C["Execute immediately"]
    B -- Yes --> D["Return requires_user_approval=True\n+ confirmation_template message"]
    D --> E["Agent shows message to user\nand waits"]
    E --> F{User says yes?}
    F -- Yes --> G["Call dag_approve(plan_id, node_id)"]
    F -- No --> H["Task cancelled"]
    G --> I["node.approved = True"]
    I --> J["Call dag_complete() → succeeds"]
```

Reading this: when `dag_next()` returns a mutating node, the orchestrator does NOT execute it immediately. Instead it surfaces a `requires_user_approval=True` flag and a human-readable message to the agent. The agent shows this to the user and waits. Only after the user confirms does the orchestrator call `dag_approve()`, which flips `node.approved = True`. Only then does `dag_complete()` succeed — if you call `dag_complete()` without approving first, it hard-fails with an error. The gate cannot be bypassed.

The key code pattern from `dag_engine.py`:

```python
# In next() — what the orchestrator receives for a mutating node
entry["requires_user_approval"] = node.mutating and not node.approved
entry["confirmation_template"] = (
    "Node X is mutating. Show this to the user and wait for "
    "explicit approval before calling dag_approve."
)

# In complete() — the hard gate
if node.mutating and not node.approved:
    return {"status": "error", "error": "Node is mutating — call dag_approve first."}

# approve() — the only way through the gate
def approve(self, plan_id, node_id):
    node.approved = True
    self._checkpoint(plan_id, "node_approved", node_id=node_id)
```

The `approved` flag is set at the node level, persisted to disk (`plan.json`), and checkpointed to a JSONL state file. If the process crashes between approval and completion, the state is recoverable — the approval is not lost.

**Mechanism 2 — Pre-tool production write guard (`pre_tool_use.py` + `_persona_lib.py`)**

For Bash commands in production environments, KIRA runs pattern matching against known destructive command patterns:

```python
_PRODUCTION_WRITE_PATTERNS = [
    r"terraform\s+apply",
    r"terraform\s+destroy",
    r"kubectl\s+apply",
    r"kubectl\s+delete",
    r"argo\s+submit",
]

# In authorize() — step 8 of the authorization chain
if (
    environment == "production"
    and persona in _APPROVAL_REQUIRED_PERSONAS   # {"senior-engineer"}
    and tool_name == "Bash"
    and any(re.search(p, command) for p in _PRODUCTION_WRITE_PATTERNS)
):
    return {"decision": "ask", "reason": "Production action requires approval."}
```

The `ask` decision causes Claude Code to pause and show the confirmation to the user before the Bash command runs. The agent does not proceed until the user accepts.

**What happens in headless/automated mode:**

When KIRA runs as an automated agent (CI, scheduled job), there is no human to click "approve". The `ask` decision auto-approves in headless mode (`--dangerously-skip-permissions`). For DAG mutating nodes, the protection falls back to system-prompt rules and post-write audit reminders. This is a conscious tradeoff — automated agents have different guardrails (narrow tool scope, separate persona with fewer permissions) rather than interactive HITL.

---

### Design tradeoffs

**Always-on gate vs confidence threshold**

KIRA uses always-on HITL for mutating nodes — every mutating node requires approval, every time. The alternative is a confidence-based gate: only require approval when the model's confidence is below some threshold.

Always-on wins for destructive operations because:
- You cannot reliably score model confidence for "is this the right production record to delete?"
- A model that is 95% confident and wrong causes exactly the same damage as a model that is 10% confident and wrong
- The friction is worth it — one human approval takes 3 seconds; recovering from a wrong production action can take hours

Confidence thresholds make sense for **output quality** (should I show this response to the user, or regenerate?) but not for **action safety** (should I delete this record?).

**Where HITL sits in the pipeline**

```
flowchart LR
    A["Agent reasoning\n(fully autonomous)"] --> B["Tool reads\n(fully autonomous)"]
    B --> C["Action planning\n(fully autonomous)"]
    C --> D["HITL gate\n(human approval)"]
    D --> E["Write action\n(executes after approval)"]
```

Everything before the gate is autonomous — reasoning, reading data, calling APIs, loading knowledge. The gate only applies to the final write step. This keeps the system fast (most operations never hit the gate) while protecting the irreversible ones.

**Per-node vs per-plan approval**

KIRA approves at the node level, not the plan level. This matters because a plan may have 8 nodes, 2 of which are mutating. The user approves node 5 before it runs, and node 7 before it runs — not the entire plan upfront. This lets the user see the actual intermediate state (what did node 4 produce?) before deciding whether to approve node 5.

The alternative — show the full plan and get one approval at the start — is faster but riskier. The actual data the agent sees at runtime may differ from what the plan assumed, and the user approving upfront cannot know that.

---

### Interview questions this covers

- What is HITL and why do you need it in a production agent?
- Write pseudocode to implement a HITL gate in an agent workflow
- How do you decide which actions require human approval?
- What is the difference between HITL and a guardrail?
- How does HITL work when the agent runs autonomously in CI (no human present)?
- Why not use a confidence threshold instead of always requiring approval for mutating actions?
- How do you make HITL state recoverable if the process crashes?

---

## Q2. What is memory management in an LLM agent and how do you implement it?

### What it is

Memory management in an LLM agent is the problem of deciding what information to keep in the active context window, what to persist externally, and how to retrieve it back when needed. LLMs have a fixed context window — they can only process a limited number of tokens per call. In a long-running agent session, the conversation history, tool outputs, retrieved documents, and reasoning all compete for that limited space.

Without memory management, one of two things happens: either you hit the context limit and the agent fails, or you keep cramming everything in and performance degrades because the model loses track of what matters in a bloated context. Both are production failures.

**The 4 types of memory in an agentic system:**

| Type | What it stores | Where it lives | Lifetime |
|------|---------------|----------------|----------|
| **In-context (working)** | Current conversation, recent tool outputs, active reasoning | Context window (tokens) | Duration of one session |
| **External (episodic)** | Past sessions, prior investigation summaries | Database / file (persistent) | Cross-session |
| **Vector (semantic)** | Knowledge base, playbooks, documentation | Vector index | Long-term, updated by PRs |
| **Procedural** | How to do things — agent instructions, tool schemas | System prompt | Fixed until redeployed |

---

### How KIRA implements it

KIRA's memory strategy is explicit and layered. Each type is handled differently.

**In-context memory — the KB epoch ledger (`_kb_guard.py`)**

The most important in-context memory problem for KIRA is: after a context compaction (when the context window fills up and Claude Code summarizes old content), which knowledge cards does the agent still have accurate access to?

The answer: none of them, reliably. The compaction summary is lossy — it captures the gist of a card, not the exact authoritative content. KIRA solves this with an **epoch-based ledger**:

```
flowchart LR
    A["Session starts\nepoch = 0"] --> B["Agent reads card X\n→ record card X as verified"]
    B --> C["Context compaction\n→ bump epoch to 1\n→ clear verified set"]
    C --> D["Agent tries to edit card X\n→ check: is card X verified in epoch 1?"]
    D -- No --> E["Block edit\nask agent to re-read card X first"]
    D -- Yes --> F["Allow edit"]
```

Reading this: the ledger tracks which cards the agent has read in the current epoch. When a compaction happens, the epoch number increments and the verified set resets to empty — because the compaction summary is lossy, you can no longer trust that the agent has accurate content for any card it read before the compaction. If the agent then tries to write to a card it has not re-read in the new epoch, the guard blocks it and forces a re-read first. Only after re-reading the card in the current epoch is the write allowed.

```python
# post_compact.py — fires on every context compaction
def bump_epoch(session_id):
    ledger = _read_ledger(session_id)
    ledger = {"epoch": ledger["epoch"] + 1, "verified": []}
    _write_ledger(session_id, ledger)

# post_tool_use.py — fires after every Read tool call
def record_card_read(session_id, card_key):
    ledger = _read_ledger(session_id)
    if card_key not in ledger["verified"]:
        ledger["verified"].append(card_key)
        _write_ledger(session_id, ledger)

# pre_tool_use.py — fires before every Edit/Write tool call
def stale_card_write_key(tool_name, tool_input, session_id):
    card_key = written_card_key(tool_name, tool_input)
    ledger = _read_ledger(session_id)
    if ledger["epoch"] >= 1 and card_key not in ledger["verified"]:
        return card_key  # signal: this is a stale write
    return None
```

**Vector memory — the routing index**

KIRA's knowledge base (playbooks, runbooks, domain cards) lives as markdown files in `brain/`. These are the long-term vector memory. At query time, `search_kb` converts the query into an embedding, scores it against the pre-built routing index, and returns the most relevant cards. The model does not need to hold all this knowledge in context — it retrieves only what it needs per query.

**Episodic memory — handoff pattern**

When a session ends or a context is cleared, KIRA uses a `/handoff` pattern — the agent writes a structured summary of what was done, what was found, and what remains. The next session starts by reading this handoff document. `preserve-context-on-clear.py` guards against accidental `/clear` commands by warning the user and suggesting `/handoff` first.

**Procedural memory — system prompt**

The instructions for how KIRA should behave — always call `search_kb` first, never answer without grounding, mark assumptions explicitly — live in `system-prompt.md`. This is procedural memory: it defines the agent's behavior patterns and does not change at runtime.

---

### Design tradeoffs

**In-context vs external retrieval**

Keeping everything in context is simple but expensive and hits limits fast. Retrieving from external memory (vector store, DB) is cheaper but adds latency and retrieval errors. KIRA's approach: keep the active work in context, retrieve knowledge on demand, persist critical state to files (ledger, handoff doc).

**Compaction: summarize vs re-read**

When context fills up, Claude Code automatically summarizes old content. KIRA's problem is that summarized card content is lossy — you cannot safely edit a card based on a summary. The epoch ledger forces a re-read after compaction instead of trusting the summary. This is slightly more friction but prevents editing knowledge cards based on stale, lossy representations.

**Session dedup**

KIRA's MCP server tracks which knowledge cards were returned in the current session. If the same card would be returned again (because the user asks a similar follow-up question), it is skipped. This saves tokens but means the agent only gets fresh cards, not repeated reinforcement of the same knowledge.

---

### Interview questions this covers

- What are the different types of memory in an LLM agent?
- How do you handle context window limits in a long-running agent session?
- What happens to agent memory after context compaction?
- How do you implement session-level deduplication for retrieved knowledge?
- How do you persist agent state across sessions?

---

## Q3. What is context engineering and how do you handle context compaction in a long-running agent?

### What it is

Context engineering is the discipline of deliberately deciding what goes into an LLM's context window at each turn — what to include, what to exclude, in what order, and at what level of detail. In a simple chatbot, context is just the conversation history. In a production agent, context includes the system prompt, retrieved knowledge cards, tool call history, intermediate reasoning, user instructions, and external data. All of this competes for the same fixed token budget.

Poor context engineering causes: the model forgetting earlier instructions buried under tool outputs, the wrong knowledge cards crowding out the right ones, the context filling up mid-task and causing a compaction that loses critical state, or the model getting confused by contradictory information when too much is loaded at once.

Good context engineering answers three questions at every turn:
1. What does the model need right now to do its next step correctly?
2. What can be left out without hurting reasoning quality?
3. What must be explicitly re-stated because it may have been buried or lost?

---

### How KIRA implements it

**Rule 1 — search_kb must always be first**

The most important context engineering decision in KIRA is forcing knowledge retrieval before anything else. The system prompt enforces this as a hard rule: the agent calls `search_kb` before any reasoning or tool call. This ensures the context always starts with relevant domain knowledge, not general LLM guesses.

Without this rule, the model would often answer from its general training, producing confident but domain-wrong responses. The rule makes knowledge grounding structural — not dependent on the model remembering to do it.

**Rule 2 — sub-agents receive pre-loaded context**

When the main KIRA agent delegates to a sub-agent, it pre-loads the relevant knowledge cards and passes them inline rather than letting the sub-agent independently run `search_kb`. This matters because:

- The sub-agent would waste tokens re-discovering knowledge the parent already loaded
- The sub-agent's search might return different cards than the parent's (non-determinism)
- Pre-loading guarantees the sub-agent reasons on exactly the same knowledge as the parent

```
flowchart LR
    MAIN["Main agent\nloads card A + card B"] -->|"context: A, B"| SUB["Sub-agent\ngets A+B inline, no search_kb"]
    SUB --> MAIN
```

**Rule 3 — compaction boundary handling (`post_compact.py`)**

When the context window fills, Claude Code compacts old content into a summary. KIRA detects this event via the `PostCompact` hook and:
1. Signals the MCP server to reset its session-dedup state (so cards suppressed earlier become retrievable again)
2. Bumps the KB epoch ledger (so the agent is forced to re-read cards before editing them)

```python
def _is_compaction(payload):
    event = payload.get("hook_event_name", "")
    if event == "PostCompact":
        return True
    return event == "SessionStart" and payload.get("source") == "compact"

def main():
    payload = _read_payload()
    if _is_compaction(payload):
        kbg.bump_epoch(payload.get("session_id", ""))
```

**Rule 4 — protect against accidental /clear**

`preserve-context-on-clear.py` intercepts the `/clear` command. First `/clear`: blocked with a message suggesting `/handoff` first. Second `/clear` within 60 seconds: passes through. This prevents engineers from losing mid-investigation context accidentally.

---

### Design tradeoffs

**Stuffing vs selective retrieval**

Stuffing all knowledge into the system prompt is simple but: costs are high, the model degrades on long contexts (lost-in-the-middle problem), and updates require redeployment. KIRA uses selective retrieval — load only what the current query needs. The tradeoff is retrieval errors (wrong cards returned), which KIRA mitigates with a well-tuned routing index and threshold.

**Compaction: inevitable, not a failure**

Compaction is not a bug — for long investigations it will happen. The design question is: what state must survive compaction, and how? KIRA's answer: critical knowledge card integrity survives via the epoch ledger. Session dedup state survives via the MCP server reset. Everything else (intermediate reasoning) is considered acceptable to lose to the summary.

---

### Interview questions this covers

- What is context engineering and why does it matter?
- How do you handle context window limits in a production agent?
- What happens during context compaction and how do you recover state?
- Why does KIRA force search_kb to always run first?
- How do you pass context from a parent agent to a sub-agent efficiently?

---

## Q4. How do you implement RBAC for an AI agent?

### What it is

Role-Based Access Control (RBAC) for an AI agent means the agent's allowed actions are determined by who the user is, not by what the model decides to do. Without RBAC, any user who can talk to the agent can potentially trigger any action the agent is capable of — including destructive ones like deleting records, running deployments, or accessing confidential data.

RBAC for an agent is harder than RBAC for a traditional API because the agent's "requests" are not structured HTTP calls — they are tool invocations generated by an LLM. You cannot rely on the model to enforce access control. The model can be tricked via prompt injection, can misinterpret the user's authorization level, or can simply make a mistake. Authorization must be enforced in code, not in the prompt.

---

### How KIRA implements it

KIRA's authorization runs as a pre-tool hook (`pre_tool_use.py`) that fires before every single tool call. The hook evaluates an 8-step chain in order. The first step that fails returns `deny` immediately — no subsequent steps run.

```
flowchart TD
    A["Tool call arrives"] --> B["1. Environment allowed for this persona?"]
    B -- No --> DENY
    B -- Yes --> C["2. Tool in deny list?"]
    C -- Yes --> DENY
    C -- No --> D["3. Tool in allow list? (if list exists)"]
    D -- No --> DENY
    D -- Yes --> E["4. Bash: matches deny patterns?"]
    E -- Yes --> DENY
    E -- No --> F["5. Bash: matches allow patterns? (if defined)"]
    F -- No --> DENY
    F -- Yes --> G["6. Bulk operation limit exceeded?"]
    G -- Yes --> DENY
    G -- No --> H["7. Required capability present?"]
    H -- No --> DENY
    H -- Yes --> I["8. Production write + approval-required persona?"]
    I -- Yes --> ASK["ask (pause for human)"]
    I -- No --> ALLOW
```

```python
def authorize(tool_name, tool_input, persona, environment, profile, session_id):
    # Step 1: environment
    if environment not in profile.allowed_environments:
        return {"decision": "deny", "reason": f"Persona '{persona}' cannot access '{environment}'."}
    # Step 2: tool deny list
    if tool_name in profile.denied_tools:
        return {"decision": "deny", ...}
    # Step 3: tool allow list
    if profile.allowed_tools and tool_name not in profile.allowed_tools:
        return {"decision": "deny", ...}
    # Steps 4-5: bash pattern matching
    # Step 6: bulk limit (per-session write counter)
    # Step 7: capability gates (knowledge-base-write, production-deploy, etc.)
    # Step 8: production approval gate
    if environment == "production" and persona in _APPROVAL_REQUIRED_PERSONAS:
        if any(re.search(p, command) for p in _PRODUCTION_WRITE_PATTERNS):
            return {"decision": "ask", "reason": "Production action requires approval."}
    return {"decision": "allow"}
```

**Personas in KIRA:**

| Persona | What they can do |
|---------|-----------------|
| `viewer` | Read-only, dev environment only |
| `engineer` | Read + write, dev + uat |
| `senior-engineer` | All tools, all environments, production writes require confirmation |
| `analyst-engineer` | Data query tools + read, no infrastructure writes |
| `admin` | Everything, including knowledge base writes |

**Persona resolution happens at session start** — SSO token → list-account-roles → highest `arc-role-kira-*` permission set → persona. This is resolved once and injected as an environment variable. The hook reads it on every tool call. The model never sees or influences the persona.

**Fail-closed everywhere:**
- Registry YAML fails to load → drop to `viewer`
- Persona env var not set → block immediately
- Any exception in `authorize()` → block in production, allow in dev (explicit fail-open in dev to avoid breaking local work)

---

### Design tradeoffs

**Code-enforced vs prompt-enforced**

Prompt-based safety ("you must not run terraform destroy") can be bypassed by the model — via prompt injection, long context confusion, or a creative user. Code-enforced hooks run as a separate process before the tool executes. The model cannot bypass them. KIRA uses code enforcement exclusively for authorization.

**Granularity: tool-level vs command-level**

Some tools (like Bash) are too broad for simple allow/deny — a Bash allow covers both `cat file.txt` and `rm -rf /`. KIRA solves this with regex pattern matching on the command string: explicit deny patterns for destructive commands, optional allow patterns for scoped personas (e.g., analyst-engineer can only run specific query scripts).

**Bulk limits**

A persona allowed to write files could still cause damage by writing thousands of files in a single session (mass edit attack). KIRA tracks write operations per session using an atomic byte-append counter file. When the limit is exceeded, further writes are blocked for that session.

---

### Interview questions this covers

- How do you implement access control for an AI agent?
- Why can't you rely on the LLM to enforce authorization?
- How does KIRA's pre-tool hook authorization chain work?
- What is fail-closed design and how is it applied to RBAC?
- How do you handle different permission levels for different users of the same agent?

---

## Q5. How does multi-agent DAG orchestration work?

### What it is

Multi-agent DAG orchestration is a pattern for breaking a complex task into a directed acyclic graph of smaller subtasks, where each node is either a tool call, an LLM sub-agent, or an automated routing decision. Nodes execute when all their dependencies are complete. The orchestrator manages state, dependency resolution, and recovery — the individual nodes do not need to know about each other.

The reason to use a DAG instead of a single agent loop is complexity management. A single agent handling a 10-step investigation with branching conditions, parallel data fetches, and conditional skips becomes hard to test, debug, and recover from. A DAG makes the execution plan explicit, inspectable, and resumable.

---

### How KIRA implements it

KIRA's DAG engine (`dag_engine.py`) has three node types:

```
flowchart LR
    S["script node\n(tool call / script)"] --- L["llm node\n(sub-agent)"] --- G["gate node\n(auto-routing)"]
```

**Script nodes** run CLI tools or Python scripts. The orchestrator provides the command and resolved arguments. The node executes, produces a structured JSON summary, and marks itself done.

**LLM nodes** are sub-agents. The orchestrator pre-loads the required knowledge cards (`requires_kb`) and upstream summaries (`inputs_from`) and injects them inline. The sub-agent never calls `search_kb` itself — its knowledge is pre-provided.

**Gate nodes** are auto-evaluated by the framework without any LLM involvement. They read upstream summaries and apply decision rules:

```python
# Gate decision rule example in registry.yaml:
# "if check_result.status == failed → skip [deploy_node, notify_node]"

def _eval_gate(decision, summaries):
    # parse: "if <node>.<field> <op> <value> → skip [node1, node2]"
    # evaluate condition against upstream summaries
    # return list of node IDs to cancel
```

**Execution flow:**

```
flowchart TB
    A["dag_plan(skill, input, nodes)"] --> B["dag_next() returns runnable nodes"]
    B --> C{node kind?}
    C -- script --> D["Run script, dag_complete(summary)"]
    C -- llm --> E["Run sub-agent with pre-loaded KB\ndag_complete(summary)"]
    C -- gate --> F["Auto-evaluate, cancel skipped nodes"]
    D --> G["Refresh runnable — unlock dependents"]
    E --> G
    F --> G
    G --> B
    G --> H{all terminal?}
    H -- Yes --> I["dag_final() — report"]
```

Reading this diagram: `dag_plan()` builds the node graph once upfront. Then the orchestrator enters a loop: call `dag_next()` to get all nodes whose dependencies are currently satisfied, run each one (script, sub-agent, or gate), call `dag_complete()` with the result, which unlocks any nodes that were waiting on this one. The loop continues until every node is in a terminal state (done, failed, blocked, or cancelled), then `dag_final()` produces the report. The key insight: `dag_next()` may return multiple nodes simultaneously — those run in parallel. Only nodes with unmet dependencies wait.

**State is persisted to disk after every transition.** If the process crashes at node 5 of 10, the orchestrator can reload `plan.json` and resume from node 5. Checkpoints write to `state.jsonl` — an append-only log of every state transition.

**Mutating nodes (HITL integration):** Any node with `mutating=True` requires `dag_approve()` before `dag_complete()` will succeed. The two systems are independent — the DAG manages execution order, HITL manages human checkpoints.

---

### Design tradeoffs

**DAG vs sequential agent loop**

A sequential agent loop (think → act → observe → repeat) is simpler to build and debug for single-domain tasks. A DAG pays off when: tasks have parallelizable subtasks (fetch logs AND query DB simultaneously), conditional branches (skip deployment if validation failed), and recovery requirements (resume from step 5, not from step 1).

**Static plan vs dynamic plan**

KIRA allows adding nodes dynamically (`dag_add_node`) after the plan starts. This is useful when an early step reveals that more steps are needed than initially planned. The tradeoff: dynamic plans are harder to audit and test — you don't know the full plan before execution starts.

**Gate nodes vs LLM routing**

Gate nodes use deterministic rule evaluation (regex + comparison), not LLM judgment. This means routing decisions are fast, cheap, predictable, and testable. The tradeoff: complex routing conditions that require reasoning cannot be expressed as gate rules — those need an LLM node to decide.

---

### Interview questions this covers

- What is a DAG and why use it for agent orchestration?
- How do you make a multi-agent system resumable after a crash?
- What is the difference between a script node, LLM node, and gate node in KIRA?
- How do you handle conditional branching in an agent workflow without using an LLM for routing?
- How does KIRA pass context from one agent to another without redundant retrieval?

---

## Q6. How do you implement multi-tenancy in an AI agent system?

### What it is

Multi-tenancy is the ability for a single deployed system to serve multiple users or teams while keeping each user's data, context, and permissions completely isolated. In traditional web applications, multi-tenancy is well-understood: each user has a database row keyed by user ID, requests are authenticated via tokens, and access control is enforced by a middleware layer. The pattern is predictable because requests are structured — the same endpoint, the same auth header, the same DB query.

For AI agents, multi-tenancy is significantly harder. The problem is that an agent's "actions" are not structured HTTP calls — they are tool invocations generated by a non-deterministic LLM. You cannot statically enumerate what the agent will do for a given user. This creates three new isolation problems that do not exist in traditional multi-tenant systems:

1. **Context leakage**: If session state is not keyed per user, a knowledge card retrieved for User A's investigation may appear in User B's dedup cache and be suppressed — causing User B to miss that card entirely.
2. **Permission inheritance**: When a high-privilege user spawns a sub-agent, that sub-agent must not inherit more than the minimum permission needed for its specific task. Without explicit scope injection, sub-agents silently inherit the parent's full permission set.
3. **RAG document leakage**: The most dangerous failure — a retrieval system that does not enforce document-level access control can return confidential documents to a user who is not authorized to see them. The LLM will then reason on and quote those documents, leaking sensitive information.

Multi-tenancy in an AI agent is not one system — it is isolation enforced simultaneously at the identity layer (who can call what), the session layer (what state is shared between sessions), and the knowledge layer (what documents each persona can retrieve).

---

### How KIRA implements it

KIRA's multi-tenancy is enforced at three levels simultaneously.

**Level 1 — Persona isolation (per-user identity)**

Every session resolves to exactly one persona at startup via SSO. The persona determines what tools the user can call, what environments they can access, and what capabilities they have. This is enforced in code by the pre-tool hook on every tool call — not set once and trusted.

```
flowchart LR
    A["User A → SSO → arc-role-kira-engineer → persona: engineer"]
    B["User B → SSO → arc-role-kira-viewer → persona: viewer"]
    A --> C["Pre-tool hook: engineer profile\n→ can run kubectl read\n→ cannot run terraform apply"]
    B --> D["Pre-tool hook: viewer profile\n→ can only Read files\n→ cannot run any Bash"]
```

**Level 2 — Session isolation (per-session dedup)**

KIRA's MCP server (`search_kb`) tracks which knowledge cards have been returned in the current session. This dedup state is keyed by `session_id` — a unique identifier per Claude Code session. User A's session dedup does not affect User B's.

When a sub-agent is spawned, it gets its own isolated dedup scope. The main agent injects `scope = agent_id` into the `search_kb` call so the MCP server maintains separate dedup buckets per sub-agent, not one shared bucket for the whole plan.

```python
# pre_tool_use.py — scope injection for search_kb
if tool_name == "mcp__kira-brain__search_kb":
    scope = payload.get("agent_id", "default")
    updated_input = {**tool_input, "scope": scope}
    # MCP server uses scope to bucket dedup state per agent
```

**Level 3 — Knowledge isolation (capability gates)**

Some knowledge cards in KIRA's brain are tagged as sensitive — accessible only to users with the `knowledge-base-write` or `production-deploy` capability. The pre-tool hook checks `_required_capabilities()` before allowing writes to those paths. A viewer persona cannot write to `brain/knowledge/` regardless of what the model decides.

---

### Design tradeoffs

**Session-scoped vs user-scoped state**

KIRA keys dedup and epoch state by `session_id`, not by user identity. This means the same user opening two KIRA windows gets two independent sessions with no shared state. This is intentional — parallel sessions on the same machine (e.g., one for investigation, one for a PR review) should not interfere with each other.

**Shared knowledge base vs per-tenant knowledge**

All KIRA users share the same knowledge brain (same `brain/` directory). Isolation is access-control-based, not data-separation-based. This is a deliberate design choice — the knowledge base is a shared company asset, and maintaining per-team copies would fragment it and make updates expensive. The tradeoff: a knowledge card visible to one persona is visible to all personas at that level. Truly sensitive per-team documents are kept outside the brain.

---

### Interview questions this covers

- How do you prevent one user's context from leaking into another's in a shared agent system?
- How does KIRA isolate sub-agent retrieval from parent agent retrieval?
- What is the difference between user-level and session-level isolation?
- How do you enforce document-level access control in a RAG agent?

---

## Q7. What is fail-closed design and why does it matter for AI agents?

### What it is

Fail-closed design means that when a system component fails, errors out, or encounters an unexpected state, it defaults to the most restrictive safe action — not the most permissive one. In security and authorization systems, fail-closed is the standard: if you cannot verify authorization, deny access. The opposite, fail-open, means failures grant access — which is always the wrong default for production systems.

For AI agents specifically, fail-closed is critical because the failure modes are unusual. The LLM might generate a tool call with an unexpected format. The persona resolution might fail because SSO is unreachable. The authorization hook might encounter a YAML parsing error. In each case, the question is: what does the system do? Fail-open means the agent proceeds and potentially executes unauthorized actions. Fail-closed means the agent blocks and reports an error.

---

### How KIRA implements it

Fail-closed is applied at every layer where authorization or safety checks run.

**Session start — fail to viewer**
```python
def main():
    try:
        registry = lib.load_registry()
    except (FileNotFoundError, OSError, yaml.YAMLError) as exc:
        # Cannot load registry → cannot determine persona → default to viewer
        print(f"[session_start] registry load failed: {exc} — defaulting to viewer", file=sys.stderr)
        env_out = {"ARIA_PERSONA": "viewer", "ARIA_ENVIRONMENT": "dev", "ARIA_IDENTITY": "unknown"}
        print(json.dumps({"env": env_out}))
        return
```

`viewer` is the most restrictive persona — read-only, dev environment only. Any error in persona resolution makes you a viewer, not an admin.

**Pre-tool hook — fail to block in production**
```python
def _fail(environment, reason):
    if environment == "production":
        print(json.dumps({"decision": "block", "reason": f"KIRA guardrail error: {reason}"}))
    sys.exit(0)  # non-production: allow (fail-open in dev only)
```

In production, any exception inside the pre-tool hook blocks the tool call. In dev, it allows — because blocking every tool call due to a hook bug would make local development impossible. This is an explicit, documented asymmetry: production is fail-closed, dev is fail-open.

**KB guard — fail to allow (best-effort)**

The KB epoch ledger is fail-open because its failure mode is less dangerous: a missed re-read nudge, not an unauthorized action. If the ledger file is corrupt or unreadable, the guard silently skips enforcement. This is the correct choice for a quality nudge (not a security gate).

---

### Design tradeoffs

**Fail-closed vs fail-open by layer**

Not every system component should be fail-closed. KIRA applies fail-closed to authorization (pre-tool hook, session persona) and fail-open to quality nudges (KB guard, large output hints). The rule: if failure grants access to something the user should not have, fail-closed. If failure just means a helpful hint is skipped, fail-open is fine.

**Production vs dev asymmetry**

Requiring fail-closed in dev would make it impossible to work when there are hook bugs — every tool call would be blocked. KIRA explicitly fail-opens in non-production environments. This is safe because dev has no real production data or infrastructure. The tradeoff: a bug that only manifests in production (rare) would be fail-closed there but not caught in dev.

---

### Interview questions this covers

- What is fail-closed design and when should you use it?
- How does KIRA handle authorization failures at each layer?
- Why is fail-open sometimes acceptable? Give an example.
- How do you design a system where bugs in safety checks don't take down the whole service?

---

## Q8. How do you implement observability and audit trails for an AI agent?

### What it is

Observability for an AI agent means you can answer: what did the agent do, in what order, on whose behalf, at what cost, and did it succeed? This is harder than traditional service observability because agent actions are not standard HTTP requests — they are tool calls generated by an LLM, often in an unpredictable sequence. Without explicit instrumentation, you have no way to debug a bad investigation, prove compliance, or track down which tool call caused an unexpected side effect.

Audit trails go further: they provide a tamper-resistant record of every action for compliance and forensics. In healthcare, finance, or any regulated industry, this is not optional.

---

### How KIRA implements it

**Layer 1 — Per-tool audit log (`post_tool_use.py`)**

After every tool call completes, KIRA writes a JSONL entry to `logs/kira-policy-audit.jsonl`:

```python
entry = {
    "ts": datetime.now(UTC).isoformat(),
    "persona": os.environ.get("ARIA_PERSONA") or "unknown",
    "environment": os.environ.get("ARIA_ENVIRONMENT") or "unknown",
    "identity": os.environ.get("ARIA_IDENTITY") or "unknown",  # user email
    "tool_name": payload.get("tool_name", ""),
    "tool_use_id": payload.get("tool_use_id", ""),
    "session_id": payload.get("session_id", ""),
}
# Written with O_APPEND | O_WRONLY for atomic writes
# Concurrent post_tool_use hooks cannot produce interleaved lines
```

Every line tells you: who called it (identity + persona), what they called (tool name), when (timestamp), in which session and environment. This is the minimum viable audit trail.

**Layer 2 — Telemetry upload (`upload-session-telemetry.py`)**

Nightly, KIRA scrubs PII from session JSONL files and uploads to S3. What's kept: tool names, token counts (input/output/cache), model used, session IDs. What's scrubbed: all free-text content, tool inputs, tool results, cwd, git branch.

```python
def scrub_event(event):
    # Keep: type, timestamp, sessionId, message.role, message.model
    # Keep: message.usage (token counts only)
    # Keep: content[].type, content[].name (tool_use only)
    # Scrub: content strings, tool_use.input, tool_result.content, thinking
    # Result: structure preserved, all data redacted
```

This gives the platform team: which tools are used most, how many tokens per investigation, whether the agent is getting stuck in long loops, cost per user — without seeing any sensitive content.

**Layer 3 — DAG checkpoints (`dag_engine.py`)**

For multi-step investigations, every state transition is checkpointed to `state.jsonl`:

```python
def _checkpoint(self, plan_id, op, **kwargs):
    record = {"ts": _now(), "plan_id": plan_id, "op": op, **kwargs}
    # append to state.jsonl
```

Operations logged: `plan_created`, `node_done`, `node_failed`, `node_approved`, `node_cancelled`, `gate_done`. This gives a complete replay log for any investigation — you can reconstruct exactly what the agent did and in what order.

---

### Design tradeoffs

**What to log vs what to scrub**

Logging everything (including tool inputs and outputs) gives maximum debuggability but creates privacy and security risks — tool outputs often contain sensitive data (patient records, financial data, internal configs). KIRA's approach: log structure and metadata, scrub content. This means you can answer "did the agent call Athena?" but not "what did the Athena query return?" For content-level debugging, you rely on session replays in dev environments, not production logs.

**Audit log durability**

KIRA's audit log uses `O_APPEND` writes which are atomic on POSIX — concurrent hook processes cannot produce interleaved lines. The log is local to the engineer's machine, not centralized. Centralization would provide organization-wide compliance but add a network dependency that could slow every tool call. KIRA chose local-first for performance, with opt-in S3 upload for aggregated telemetry.

---

### Interview questions this covers

- How do you audit what an AI agent does in production?
- What is the minimum viable audit trail for a production agent?
- How do you balance observability with privacy in agent logs?
- How do you make audit writes atomic when multiple hook processes run concurrently?
- How do you give platform teams usage analytics without exposing sensitive content?

---

## Q9. How do you handle structured output and schema validation in an agent?

### What it is

Structured output means the LLM returns data in a defined format (JSON, not prose) that the system can parse and act on programmatically. In an agentic workflow, each step's output often feeds the next step as input — if the output is unstructured or malformed, the pipeline breaks. Schema validation is the enforcement mechanism: define what the output must look like, check it, and decide what to do if it fails.

The problem: LLMs do not reliably produce well-formed JSON. Even with explicit instructions, models occasionally produce trailing commas, missing required fields, wrong types, or extra prose around the JSON block. In a pipeline that runs 10 steps, one bad output can cascade.

---

### How KIRA implements it

**Registry-defined output schemas**

Each node in KIRA's DAG has an `output_schema` defined in `registry.yaml`. The schema specifies what fields the node's LLM output must contain and their types:

```yaml
# registry.yaml example
investigate_root_cause:
  kind: llm
  output_schema:
    root_cause: str
    confidence: enum[high, medium, low]
    affected_systems: list
    recommended_action: str
  schema_strictness: strict
```

**Validation in `dag_complete()`**

When the orchestrator calls `dag_complete(plan_id, node_id, summary)`, the engine validates the summary against the schema before accepting it:

```python
def complete(self, plan_id, node_id, summary):
    reg_entry = reg.get(node.tool, {})
    output_schema = reg_entry.get("output_schema")
    schema_errors = _validate_schema(summary, output_schema)

    if schema_errors and strictness == "strict":
        node.retry_count += 1
        if node.retry_count >= _RETRY_LIMIT:  # _RETRY_LIMIT = 2
            node.status = NodeStatus.FAILED
            # propagate blocked to all dependent nodes
            return {"status": "failed", "error": "Schema validation exhausted after 2 retries."}
        return {
            "status": "schema_error",
            "schema_errors": schema_errors,
            "retries_remaining": _RETRY_LIMIT - node.retry_count,
        }

    node.status = NodeStatus.DONE
    node.summary = summary
```

The orchestrator sees `schema_error` status and re-runs the LLM node with the validation errors in the prompt: "Your previous output was missing the field `confidence`. Return valid JSON with all required fields." This retry loop runs up to 2 times before failing permanently.

**Type system**

KIRA's schema notation is compact: `str`, `int`, `float`, `bool`, `list`, `dict`, `any`, and `enum[val1, val2]`. The validation converts these to JSON Schema and uses `jsonschema.Draft7Validator`. If `jsonschema` is not installed, it falls back to checking required field presence.

---

### Design tradeoffs

**Strict vs warn mode**

`schema_strictness: strict` means validation errors retry and eventually fail. `schema_strictness: warn` means validation errors are recorded but the node succeeds with the malformed output. Warn mode is useful during development when you want to see what the model produces without blocking the pipeline. Production should use strict.

**Schema in code vs system prompt**

You could put schema requirements in the prompt ("return JSON with these fields"). KIRA puts them in the registry and validates in code. The difference: prompt-based schemas are forgotten across compaction and can be misinterpreted. Code-based schemas are enforced regardless of what the model outputs.

**Retry count**

Two retries is enough to catch transient model errors (forgot a field) but stops infinite loops. The error message on retry includes the specific validation errors, which gives the model concrete correction instructions. Without the specific error, the retry often produces the same malformed output.

---

### Interview questions this covers

- How do you enforce structured output from an LLM in a multi-step pipeline?
- What happens when an LLM node returns malformed JSON?
- How does KIRA's retry loop work for schema validation failures?
- Why define output schemas in a registry rather than in the prompt?

---

## Q10. How do you handle agent retry and error propagation?

### What it is

In a multi-step agent workflow, failures are inevitable — a script times out, an API returns an error, an LLM produces invalid output, a network call fails. The question is: what does the system do? Options: retry immediately, retry with backoff, mark the node failed and stop, mark the node failed and cascade the failure to all dependent nodes, or allow the orchestrator to decide.

Error propagation matters because in a DAG, nodes depend on each other. If node 3 fails, nodes 5 and 7 that depend on node 3's output cannot run meaningfully — they should be blocked, not attempted with missing inputs.

---

### How KIRA implements it

**Retry at the node level**

Each node tracks `retry_count`. For schema validation errors (wrong output format), the node is retried up to `_RETRY_LIMIT = 2` times before being marked failed. The retry sends the validation errors back to the LLM as correction instructions.

For script failures (non-zero exit code, exception), the orchestrator calls `dag_fail(plan_id, node_id, reason)` explicitly. This does not auto-retry — the orchestrator decides whether to call `dag_retry()` or let it fail.

```python
def retry(self, plan_id, node_id):
    node.status = NodeStatus.PENDING
    node.summary = None
    node.summary_hash = None
    node.fail_reason = None
    node.approved = False
    node.retry_count = 0
    # Also un-block direct descendants that were blocked by this failure
    for other in plan.nodes.values():
        if other.fail_reason == f"ancestor {node_id} failed":
            other.status = NodeStatus.PENDING
            other.fail_reason = None
    plan.status = "active"
```

**Error propagation — `_propagate_blocked()`**

When a node fails, all nodes that transitively depend on it are marked `BLOCKED`:

```python
def _propagate_blocked(self, plan, failed_id):
    blocked_set = {failed_id}
    changed = True
    while changed:
        changed = False
        for node in plan.nodes.values():
            if node.id in blocked_set or node.status in _TERMINAL:
                continue
            if any(dep in blocked_set for dep in node.needs):
                node.status = NodeStatus.BLOCKED
                node.fail_reason = f"ancestor {failed_id} failed"
                blocked_set.add(node.id)
                changed = True
    return list(blocked_set - {failed_id})
```

Nodes that do NOT depend on the failed node continue running — parallel branches are not affected.

**Idempotent completion**

`dag_complete()` is idempotent if called twice with the same summary (same hash). This handles the case where the orchestrator sends the completion event twice (network retry, double delivery). If the summary hash differs, it returns an error instead of silently overwriting.

---

### Design tradeoffs

**Auto-retry vs orchestrator-controlled retry**

Schema errors auto-retry because the fix is simple and deterministic (add the missing field). Script failures do not auto-retry because the cause might be permanent (wrong credentials, missing data) — retrying immediately would just fail again and waste time. Letting the orchestrator decide gives it the chance to inspect the failure and route appropriately.

**Cascade fail vs isolate fail**

When node 3 fails, nodes 5 and 7 are blocked. This is safe but may discard useful work from parallel branches. KIRA only blocks transitive descendants — nodes on independent branches continue. If you want full plan failure on any node failure, the orchestrator can call `dag_cancel()`.

---

### Interview questions this covers

- How do you implement retry logic in a multi-step agent pipeline?
- When should errors propagate to dependent nodes and when should they be isolated?
- How do you make a multi-step pipeline resumable after partial failure?
- How do you handle duplicate completion events in a distributed agent system?

---

## Q11. How do you build an eval framework for an AI agent?

### What it is

An eval framework for an AI agent is a system that runs the agent against predefined scenarios and automatically checks whether it behaved correctly. For a traditional API, testing is straightforward — send input, check output. For an agent, the challenge is: agents call real external systems (databases, APIs, Kubernetes), are non-deterministic (same input can produce different tool sequences), and testing against real production systems is unsafe.

A good eval framework must: isolate the agent from real external systems (mocks), define what "correct" means for each scenario (expected behavior, not just expected output), and run automatically as a CI gate on every change.

---

### How KIRA implements it

**Mock environment — the key design decision**

KIRA's eval framework (`evals/investigation_runner.py`) runs the real KIRA agent (real Claude Code, real system prompt, real tools) inside a fully mocked environment. All external calls are intercepted by a local mitmproxy that returns pre-recorded fixture responses. The agent never touches real AWS, Jira, GitHub, or internal databases during an eval.

```
flowchart TB
    A["Test runner"] --> B["Start mitmproxy with fixture YAML files"]
    B --> C["Launch real Claude Code agent\n(real system prompt + real hooks)"]
    C --> D["Agent calls AWS Athena"]
    D --> E["mitmproxy intercepts\nreturns fixture YAML"]
    E --> C
    C --> F["Agent calls GitHub API"]
    F --> E
    C --> G["Agent produces final answer"]
    G --> H["Evaluate: hard gates + LLM critic"]
```

**Scenario definition**

Each scenario is a YAML file defining the test case:
```yaml
prompt: "Investigate why customer data is missing for org X"
expected_cards:
  - brain/knowledge/connector-troubleshooting.md
  - brain/playbooks/common/connector-install.md
expected_root_cause: "connector promotion was not validated after deploy"
mocks:
  aws/athena-results: fixtures/athena-missing-data.yaml
  jira/get-issue: fixtures/jira-DEV-1234.yaml
```

**Evaluation — two layers**

Hard gates (deterministic):
- Did `search_kb` fire before any other tool call? (required, not optional)
- Were the expected knowledge cards loaded and read?
- Did the agent avoid making real external calls (fixture_missing sentinel)?

LLM critic (semantic):
- Did the agent reach the correct root cause?
- Was the recommended action actionable?
- Did the answer cite specific evidence from the investigation?

Pass threshold: 80/100. Scores below this are flagged as regressions and block the merge.

**CI integration**

The eval runner is triggered on every PR that touches `brain/` (knowledge updates) or agent hooks. This ensures: updating a playbook does not break existing investigation scenarios, and adding a new hook does not break the tool call sequence. The eval is the quality gate before any knowledge or behavior change ships.

---

### Design tradeoffs

**Real agent vs stub agent**

KIRA evals run the real agent — real Claude Code, real system prompt, real hooks — not a stub or mock agent. This catches real failures: a prompt change that breaks tool ordering, a hook bug that blocks the agent, a knowledge card that confuses retrieval. The tradeoff is cost ($0.01–$0.10 per eval run) and flakiness (LLM non-determinism). Hard gate checks reduce flakiness by testing structure, not content.

**Fixture replay vs live APIs**

Fixture replay (mitmproxy returning YAML) means evals are deterministic and fast. The tradeoff: fixtures go stale if the real API changes its response format. KIRA detects this with a `fixture_missing` sentinel — if the agent makes a call that has no fixture, the eval kills immediately and reports what fixture is missing.

---

### Interview questions this covers

- How do you test an AI agent that calls real external systems?
- What is the difference between hard gate checks and LLM-as-judge checks in evals?
- How do you run agent evals in CI without touching production?
- How do you prevent knowledge base updates from breaking existing investigations?

---

## Q12. What is the difference between prompt caching and semantic caching?

### What it is

Both reduce LLM cost and latency, but they work differently and solve different problems. Confusing them is a common interview mistake.

**Prompt caching** is a feature provided by the LLM API provider (Anthropic, OpenAI). When you send a request with a long system prompt or context, the provider caches the computed key-value (KV) representations of that prefix on their infrastructure. If your next request starts with the same prefix, the provider reuses the cached KV states instead of recomputing them. You pay for the cache write once, then get a significant discount on subsequent reads. This is transparent to you — the model output is identical, just cheaper and slightly faster.

**Semantic caching** is something you build yourself at the application layer. When a user query comes in, you embed it, check whether a semantically similar query has been answered before (cosine similarity against cached query embeddings), and if the score is above a threshold, return the cached answer without calling the LLM at all. The cache key is meaning, not exact text — "how do I fix a broken connector" and "connector deployment failed, what do I do" may return the same cached answer.

| | Prompt caching | Semantic caching |
|--|--|--|
| Where | API provider infrastructure | Your application layer |
| What it caches | KV states for fixed prompt prefixes | LLM answers for similar queries |
| Savings | ~90% token cost for cached prefix | 100% LLM cost (no call made) |
| When it helps | Long system prompts sent repeatedly | Repeated similar user questions |
| Risk | None — output is identical | Wrong answer returned for superficially similar but different queries |

---

### How KIRA relates to both

**Prompt caching:** KIRA's system prompt is loaded on every turn. If Anthropic has cached the KV states for KIRA's system prompt prefix, repeated turns in the same session pay significantly less for that prefix. KIRA uses LiteLLM proxy which tracks `cache_creation_input_tokens` vs `cache_read_input_tokens` in usage data — this is logged in the telemetry.

**Semantic caching:** KIRA does not implement semantic caching for LLM answers. The reason: investigation answers are highly context-specific (they reference specific customer data, specific ticket IDs, specific log outputs). Returning a cached answer for a semantically similar but different investigation would be dangerous — wrong guidance in a production incident. The dedup in KIRA's `search_kb` is about knowledge cards, not about answers.

---

### Design tradeoffs

**Semantic cache staleness**

A cached answer might be correct today and wrong tomorrow — if the underlying system state changed, the same question has a different answer. Semantic caching is safe for stable knowledge ("what is our vacation policy?") and dangerous for dynamic state ("why is the pipeline failing right now?"). Never use semantic caching for agent answers that depend on live system state.

**Threshold sensitivity**

The similarity threshold for semantic cache hits is a critical parameter. Too high: cache never hits (no benefit). Too low: wrong answers returned for queries that are similar but not identical. There is no universal threshold — it depends on how diverse your query space is.

---

### Interview questions this covers

- What is the difference between prompt caching and semantic caching?
- When would you use each, and when would each be dangerous?
- How does Anthropic's prompt caching work under the hood?
- Why doesn't KIRA use semantic caching for investigation answers?

---

## Q13. What is KV Cache in transformers and why does it matter?

### What it is

Every time a transformer processes a sequence of tokens, it computes Query, Key, and Value matrices for each attention head at each layer. These computations are expensive — they scale quadratically with sequence length. The KV Cache stores the Key and Value matrices from all previous tokens so that when the model generates the next token, it only needs to compute Q, K, V for the new token, then attend over the cached K and V values for all previous tokens.

Without KV cache: generating a 1000-token response requires computing attention over the full sequence for each of the 1000 tokens — O(n²) work. With KV cache: only compute K and V once per input token, store them, and reuse them. Output generation becomes O(n) in attention computation.

```
flowchart LR
    A["Input: 500 tokens\n(prefill phase)"] --> B["Compute K, V for all 500 tokens\nStore in KV cache"]
    B --> C["Generate token 501\nCompute Q for token 501 only\nAttend over cached K, V 1-500"]
    C --> D["Generate token 502\nQ for 502 only\nAttend over cached K, V 1-501"]
    D --> E["...continues until EOS"]
```

**Why this matters practically:**

- **Latency**: KV cache reduces time-per-token during generation significantly
- **Prompt caching**: Anthropic and OpenAI's prompt caching feature works by persisting KV cache states on the server across requests. When you send the same system prompt prefix twice, they reuse the pre-computed KV states — no re-computation, lower cost
- **Memory**: KV cache consumes GPU memory proportional to context length × number of layers × batch size. At long context lengths, KV cache can consume more GPU memory than model weights. This is why context length is a deployment constraint, not just a model capability constraint
- **vLLM**: The open-source inference server vLLM implements paged KV cache attention — stores KV cache in non-contiguous memory pages (like OS virtual memory), allowing much higher throughput by eliminating memory fragmentation

---

### Design tradeoffs

**Context length vs memory**

A 100K context window sounds like a capability. In practice, it is a memory constraint: 100K tokens × 32 layers × 2 (K and V) × batch size × float16 = many gigabytes of GPU memory just for KV cache. This is why running large context models requires much more GPU memory than the model weights alone would suggest.

**Streaming and KV cache**

When you stream tokens to the user (seeing text appear word by word), the KV cache is being built incrementally as each token is generated. This is efficient — the model generates and caches simultaneously. The expensive part is the initial prefill (processing the full input prompt), not the generation.

---

### Interview questions this covers

- What is the KV cache in a transformer and why does it exist?
- Why does context length affect GPU memory requirements so much?
- How does Anthropic's prompt caching relate to the transformer KV cache?
- What is vLLM and how does paged attention improve inference throughput?

---

## Q14. How do you measure retrieval quality — RAGAS, MRR, Recall@K?

### What it is

Retrieval quality measures whether the right documents are being returned for a given query — before the LLM generates an answer. This is critical because in RAG systems, most answer quality failures are retrieval failures: the model confidently answers from the wrong document or produces hallucinations because the right document was never retrieved.

**Recall@K**: Of all the relevant documents for this query, what fraction were in the top K results? If there are 3 relevant documents and your retrieval returns 2 of them in the top 5, Recall@5 = 2/3 = 0.67. Measures: are we finding the right documents at all?

**Precision@K**: Of the K documents returned, what fraction are relevant? If 3 of your top 5 are relevant, Precision@5 = 3/5 = 0.6. Measures: are we returning noise alongside the right documents?

**MRR (Mean Reciprocal Rank)**: For each query, what is the rank of the first relevant document? If the first relevant document is at position 3, reciprocal rank = 1/3. MRR is the average across all queries. Measures: is the most relevant document appearing near the top?

**RAGAS**: A framework for evaluating full RAG pipeline quality across 4 dimensions:

| Metric | What it measures | How computed |
|--------|-----------------|--------------|
| **Faithfulness** | Does the answer only use information from retrieved context? | LLM check: is each claim in the answer supported by the context? |
| **Answer Relevance** | Does the answer address the actual question asked? | Embed answer, embed question, measure alignment |
| **Context Recall** | Were all relevant facts from the ground truth captured in retrieved context? | Compare retrieved context against reference answer |
| **Context Precision** | Are the retrieved chunks actually relevant to answering the question? | LLM check: is each chunk useful for answering? |

---

### How KIRA measures retrieval quality

KIRA's eval framework checks retrieval quality via **hard gates** — deterministic checks that don't require a ground truth answer:

- Did `search_kb` fire before any other tool call? (sequence check)
- Were the expected knowledge cards in the retrieval results? (recall check)
- Were unnecessary cards NOT returned? (precision signal)

For investigation evals, the scenario YAML defines `expected_cards`. After the run, the eval checks whether those cards appeared in the agent's retrieval results. This is a binary recall check per scenario — not a continuous metric across all queries, but it catches regressions (a routing index change that stops returning the connector card for connector failure queries).

---

### Design tradeoffs

**Recall vs Precision tradeoff**

Improving recall (returning more documents) hurts precision (returning more noise). In KIRA, the threshold (0.44 cosine similarity) is the tuning knob. Lowering it returns more cards (higher recall) but adds irrelevant ones (lower precision). KIRA's routing approach — curated triggers vs arbitrary chunking — helps precision: a trigger explicitly maps to the relevant card, not a fuzzy vector match against random document chunks.

**Offline vs online evaluation**

RAGAS metrics require ground truth answers and are computed offline (before deployment). KIRA's hard gate checks run in CI (on every PR). The two serve different purposes: RAGAS tells you retrieval quality in absolute terms; hard gates tell you whether a specific change broke a specific expected behavior.

---

### Interview questions this covers

- What is Recall@K and how is it different from Precision@K?
- What is MRR and when is it a better metric than recall?
- What does RAGAS measure and how is faithfulness different from relevance?
- How do you test retrieval quality in CI without RAGAS?
- What is the tradeoff between recall and precision in RAG retrieval?

---

## Q15. How do you build an LLM-as-judge evaluator?

### What it is

LLM-as-judge is a technique where you use an LLM to score the output of another LLM. Instead of writing deterministic rules for what a good answer looks like (hard for open-ended outputs), you write a scoring prompt that instructs a judge model to evaluate quality along specific dimensions. The judge returns a score (e.g. 0-10) and a reasoning trace explaining the score.

It is used when: output quality cannot be measured by exact match (agent investigation conclusions), reference answers are not available, or the evaluation dimension requires semantic understanding (is this answer faithful to the retrieved context?).

---

### How KIRA implements it

KIRA's eval framework uses an LLM critic alongside hard gate checks. The critic is a separate Claude call that receives:

1. The original user prompt (what the investigation was about)
2. The agent's final answer
3. The expected root cause (from scenario YAML)
4. The list of tool calls made (call log)

The critic prompt asks it to score three dimensions:

```
You are evaluating an AI investigation agent's output.

User prompt: {prompt}
Agent answer: {agent_answer}
Expected root cause: {expected_root_cause}
Tools used: {call_log}

Score each dimension 0-10:
1. Root cause accuracy: Does the agent's conclusion match the expected root cause?
2. Evidence quality: Does the agent cite specific data (logs, query results, ticket details)?
3. Actionability: Is the recommended action specific and executable?

Return JSON: {"root_cause": N, "evidence": N, "actionability": N, "reasoning": "..."}
```

The three scores are combined with the hard gate results (pass/fail) into a final score out of 100. Runs below 80 are flagged as regressions.

**Why a separate judge model?**

Using the same model to evaluate its own output produces inflated scores — models are systematically biased toward their own style and content. KIRA uses a different model tier or temperature setting for the critic. When available, an Opus-class model reviews Sonnet-class outputs.

---

### Design tradeoffs

**Judge model bias**

LLM judges have known biases: preference for longer, more detailed answers, preference for answers matching their own training distribution, and inconsistency across runs (the same answer scores differently on different runs). Mitigations: use explicit rubrics with clear definitions, ask for chain-of-thought reasoning before the score (anchors the score to reasoning), and run multiple judge calls and average.

**Hard gates first, LLM critic second**

Hard gates (did search_kb fire first? were required cards loaded?) are deterministic and cheap. LLM critic is probabilistic and costs money. KIRA runs hard gates first — if a hard gate fails, the run scores 0 and the critic is not invoked. This saves cost and ensures structural correctness is checked before semantic quality.

---

### Interview questions this covers

- What is LLM-as-judge and when do you use it?
- How do you design a scoring rubric for LLM evaluation?
- What biases do LLM judges have and how do you mitigate them?
- How does KIRA combine hard gate checks with LLM critic scoring?
- Why use a separate model as the judge instead of the same model?

---

## Q16. What agentic patterns exist beyond ReAct?

### What it is

ReAct (Reason + Act) is the baseline agent pattern: the model reasons about what to do, calls a tool, observes the result, reasons again, and repeats. It works well for linear investigations with a predictable tool sequence. But real tasks are more complex: they need planning ahead, recovering from mistakes, and structured decomposition. Three patterns extend ReAct meaningfully.

**Plan-and-Execute**

The agent first generates a full execution plan (list of steps), then executes each step in order. The planning step can be reviewed before execution starts. This is KIRA's DAG pattern — `dag_plan()` generates the full node graph, then `dag_next()` + `dag_complete()` execute it step by step.

```
flowchart LR
    A["User task"] --> B["Planning step\n(generate full DAG)"]
    B --> C["Human review (optional)"]
    C --> D["Execute step 1"]
    D --> E["Execute step 2"]
    E --> F["...until done"]
```

Advantage: the full plan is inspectable before any action runs. HITL can review the plan, not just individual steps. Disadvantage: the plan may become invalid as execution reveals new information — requires dynamic replanning.

**Reflexion**

After completing a task, the agent evaluates its own output, identifies mistakes, and generates a revised plan. The self-critique loop runs until the output meets a quality threshold or a max iteration count is hit.

```
flowchart LR
    A["Execute task"] --> B["Self-evaluate output"]
    B -- "quality < threshold" --> C["Generate improvement plan"]
    C --> A
    B -- "quality >= threshold" --> D["Return final output"]
```

Advantage: catches errors without human intervention. Disadvantage: the model may not catch its own mistakes reliably (same biases that produced the error may also affect the critique).

**Self-consistency**

Run the same task N times with temperature > 0 (non-deterministic), then aggregate results. For factual questions, take the majority answer. For actions, take the most frequent recommended action. Advantage: reduces hallucination for factual tasks. Disadvantage: expensive (N × cost of one run), not suitable for agentic tasks with side effects.

---

### How KIRA uses Plan-and-Execute

KIRA's DAG engine is a concrete implementation of Plan-and-Execute. The orchestrator generates the node graph at task start (`dag_plan`), optionally shows it to the user (`dag_plan_preview`), then executes nodes as their dependencies complete. Gate nodes handle branching (skip deployment if validation failed) without requiring LLM re-planning. Dynamic nodes (`dag_add_node`) handle cases where an early step reveals that more steps are needed.

---

### Interview questions this covers

- What agent patterns exist beyond ReAct?
- What is Plan-and-Execute and when is it better than ReAct?
- What is Reflexion and what are its limitations?
- How does KIRA's DAG orchestration relate to the Plan-and-Execute pattern?
- When would you use self-consistency and when would it be inappropriate?

---

## Q17. What are the 4 types of memory in an agentic system?

### What it is

When an interviewer asks "what are the types of memory in an agentic system?", they are probing whether you understand that LLM agents face a fundamental constraint that human cognition does not: a hard limit on what can be held in active memory at once.

A human expert working on a complex problem uses memory continuously and naturally — they remember what they did last week, apply expertise built over years, actively think about the current problem, and have ingrained habits for how to approach their domain. They do not need to explicitly manage any of this. An LLM agent has none of this implicit memory. It starts every session blank. Everything it knows must either be injected into the context window (expensive and limited) or explicitly retrieved from external storage on demand.

This creates a design problem: for a long-running agent working across multiple sessions, handling complex multi-step tasks, in a specific domain — how do you give it the right knowledge, at the right time, without overflowing its context window? The answer is to treat agent memory the same way computer architects treat memory hierarchies: different tiers with different speeds, capacities, and lifetimes.

The 4 types map directly to how humans store and use knowledge, which makes them intuitive to explain in an interview:

| Memory type | Human analogy | Agent equivalent | Lifetime |
|-------------|---------------|-----------------|----------|
| **In-context (working)** | What you're actively thinking about | Current conversation + tool outputs in context window | One session, one turn |
| **Episodic (external)** | Diary or memory of past events | Past session summaries, handoff docs, prior investigation notes | Across sessions |
| **Semantic (vector)** | Long-term knowledge and expertise | Knowledge base, documentation, playbooks in vector store | Long-term, updated by humans |
| **Procedural** | Habits and skills — how to do things | System prompt, tool definitions, agent behavior rules | Fixed until redeployed |

---

### Detailed breakdown

**In-context (working memory)**
- Everything between the start of the current context window and the current position
- Includes: system prompt (procedural), retrieved cards (semantic), tool call history, intermediate reasoning, conversation
- Limited by context window size — KIRA's session uses Claude's 200K token window
- Lost at session end unless explicitly persisted

**Episodic memory**
- What the agent did before, stored outside the context window
- KIRA's handoff docs are episodic memory — a previous session wrote a summary, the next session reads it
- Can also be structured: store investigation summaries in a database, retrieve relevant ones at query time ("what was the root cause last time this customer had a data issue?")
- Requires retrieval at the right time — an agent that never reads past episodes gains nothing from storing them

**Semantic memory**
- The knowledge base — playbooks, runbooks, domain documentation
- In KIRA: `brain/` directory indexed as vectors, retrieved via `search_kb`
- Updated by humans via PRs, not by the agent's experience
- The agent retrieves from semantic memory on every turn but does not write to it during normal operation

**Procedural memory**
- How to behave — the agent's learned skills and habits
- In KIRA: `system-prompt.md` (call search_kb first, mark assumptions, never answer without grounding)
- Also: tool schemas (how to call each tool), persona profiles (what is allowed)
- Cannot be updated at runtime — requires a code or config change and redeployment

---

### How they interact in KIRA

```
flowchart TB
    A["User question"] --> B["Procedural memory\n(system prompt: call search_kb first)"]
    B --> C["Semantic memory\n(search_kb → retrieve relevant cards)"]
    C --> D["In-context (working)\n(system prompt + retrieved cards + conversation)"]
    D --> E["Agent reasons and acts"]
    E --> F["Session ends\n→ /handoff → write episodic memory"]
    F --> G["Next session reads episodic memory\n(prior investigation summary)"]
```

---

### Interview questions this covers

- What are the 4 types of memory in an agentic system?
- What is the difference between episodic and semantic memory in an agent?
- How does procedural memory differ from in-context memory?
- How does KIRA use each type of memory?
- How do you persist episodic memory across agent sessions?

---

## Q18. How do you design a good tool schema for an AI agent?

### What it is

A tool schema is the definition the LLM reads to understand what a tool does, when to call it, and what parameters to provide. The schema is the interface between the model's reasoning and the tool's execution. A poorly designed schema causes the model to call the wrong tool, pass wrong parameters, or not call a tool when it should.

Tool schema design is underrated. Most agent reliability problems in production come from: vague tool descriptions (model doesn't know which tool to pick), missing or ambiguous parameter descriptions (model passes wrong values), and tools that do too many things (model doesn't know what to expect as output).

---

### How KIRA implements it

KIRA's primary tool is `search_kb`. Its schema is designed to be unambiguous:

```python
@mcp.tool()
def search_kb(queries: list[str]) -> str:
    """Search the KIRA knowledge base for relevant playbooks, runbooks, and domain cards.

    ALWAYS call this tool FIRST before any other action.
    Use 2-5 short keyword phrases, not full sentences.
    Example: ["connector deployment", "DFP validation", "prod data missing"]

    Returns: list of matching knowledge card paths to read next.
    """
```

Key design decisions:
- **"ALWAYS call this tool FIRST"** — not a suggestion. Forces ordering.
- **"2-5 short keyword phrases, not full sentences"** — MiniLM embeds short phrases better than long queries. Without this, the model sends paragraph-length queries that score poorly.
- **Example included** — models follow examples more reliably than abstract instructions.
- **Explicit output description** — "returns list of card paths to read next" tells the model what to do after this tool call.

**What makes a bad tool schema:**
- "Search the knowledge base" (too vague — search for what? when?)
- Parameters named `input` or `data` (no semantic meaning)
- Description mixes what the tool does and when to use it incoherently
- No example (model guesses parameter format)
- Too many tools with similar descriptions (model picks wrong one)

**MCP tool design principles KIRA follows:**
1. One tool, one clear purpose — not a Swiss Army knife
2. Parameter names are self-explanatory (`queries: list[str]`, not `q`)
3. Description answers: what does it do, when to call it, what format does input take
4. Output format explicitly described so the model knows what to do next
5. Critical ordering constraints stated directly in the description

---

### Design tradeoffs

**Descriptive vs concise**

Longer descriptions give more guidance but consume prompt tokens on every turn. KIRA's `search_kb` description is short and dense — every sentence is load-bearing. Verbose descriptions with redundancy waste context budget and train the model to skim tool schemas.

**General vs specialized tools**

A general "run_query" tool that handles SQL, NoSQL, and API calls is convenient to build but confusing for the model — it must infer which backend is being used from context. KIRA has specialized tools: `athena_query.py`, `console_query.py`, `mssql_query.py`. Each schema is specific to one backend with clear parameter formats for that backend.

---

### Interview questions this covers

- What makes a good tool schema for an LLM agent?
- Why does parameter naming matter in tool schemas?
- How do you force a specific tool calling order using the schema?
- What is MCP and how does it standardize tool schemas across different agents?
- What is the most common mistake in tool schema design?

---

## Q19. What is quantization and how does RLHF align LLMs?

### What it is — Quantization

Quantization reduces the numerical precision used to store model weights. A standard trained model uses 32-bit or 16-bit floating point numbers. Quantization converts these to 8-bit integers (INT8) or 4-bit integers (INT4). This reduces model size and GPU memory requirements significantly, at a small cost to output quality.

| Format | Memory per weight | Quality loss | Use case |
|--------|------------------|--------------|----------|
| FP32 | 4 bytes | None (baseline) | Training |
| FP16/BF16 | 2 bytes | Negligible | Standard inference |
| INT8 | 1 byte | Small | Production inference, cost reduction |
| INT4 | 0.5 bytes | Moderate | Local deployment, consumer hardware |

Why it matters: a 70B parameter model in FP16 requires ~140GB of GPU memory — multiple high-end GPUs. The same model in INT4 requires ~35GB — fits on a single consumer GPU. This is why tools like Ollama (which runs quantized models locally) are possible. The quality difference between FP16 and INT4 is often imperceptible for general tasks but noticeable for complex reasoning.

**GGUF** is the file format used by llama.cpp and Ollama for quantized models — it stores model weights alongside metadata in a single portable file designed for CPU/GPU inference.

---

### What it is — RLHF

RLHF (Reinforcement Learning from Human Feedback) is the technique used to align a pre-trained LLM to human preferences — making it helpful, harmless, and honest rather than just statistically likely to predict the next token.

The 3-step process:

```
flowchart LR
    A["Pre-trained LLM\n(predicts next token)"] --> B["Supervised Fine-Tuning\n(train on human-written examples)"]
    B --> C["Train Reward Model\n(humans rank model outputs)"]
    C --> D["RL with Reward Model\n(PPO: optimize for higher reward)"]
    D --> E["Aligned LLM\n(helpful, harmless, honest)"]
```

Step 1 — SFT: Fine-tune on examples of good responses written by humans. Teaches the model the format and style of helpful answers.

Step 2 — Reward Model: Human labelers are shown pairs of model outputs for the same prompt and asked which is better. A reward model is trained to predict human preferences.

Step 3 — RL (PPO): The SFT model generates outputs, the reward model scores them, and PPO (Proximal Policy Optimization) updates the model to produce outputs the reward model scores higher. This is repeated until quality converges.

**DPO (Direct Preference Optimization)** is a simpler alternative that skips the reward model entirely. It directly fine-tunes on preference data (A is better than B) without an RL loop. DPO is more stable to train and increasingly preferred over RLHF for alignment.

**Constitutional AI (Anthropic)**: Instead of human labelers ranking outputs, a set of principles (the "constitution") guides the model to critique and revise its own outputs. Reduces human labeling cost.

---

### Interview questions this covers

- What is quantization and why does it enable local model deployment?
- What is the difference between INT4 and INT8 quantization?
- What is RLHF and what problem does it solve?
- What is DPO and how is it different from RLHF?
- What is Constitutional AI and how does it reduce human feedback requirements?

---

## Q20. How do you deploy an AI agent to production?

### What it is

Deploying an AI agent to production is fundamentally different from deploying a traditional REST API. A REST API is deterministic — the same input produces the same output, behavior changes only when code changes, and a rollback means reverting a known diff. An AI agent has none of these properties.

**Why AI agent deployment is different:**

1. **Non-deterministic behavior** — the same user prompt can produce a different tool call sequence on each run. There is no "correct output" to regression test against — only behavioral quality (did it reach the right conclusion?). This means standard snapshot testing does not work.

2. **Behavior changes without code changes** — when the LLM provider updates their model (e.g. Claude 3.5 → Claude 3.7), the agent's behavior changes even if you changed zero lines of code. You must re-run evals on model updates, not just on code changes.

3. **Multiple moving dependencies** — the agent depends on: the LLM endpoint, the vector store (for RAG), tool integrations (APIs, databases), and the knowledge base. Each can fail or degrade independently. A deployment health check that only verifies HTTP 200 misses most real failure modes.

4. **Knowledge base is a separate release cycle** — for RAG agents, the knowledge base (playbooks, documentation, runbooks) changes independently of code. You need a pipeline for knowledge updates that runs evals, not just a file copy.

**Three deployment models for AI agents:**

| Model | What it looks like | Best for |
|-------|--------------------|----------|
| **Local client** | Agent runs on the engineer's machine; only LLM proxy is centralized | Internal tools, CLI agents, high-privacy requirements |
| **API service** | Agent exposed as a REST endpoint; scales on K8s | Customer-facing agents, multi-user products |
| **Embedded/sidecar** | Agent runs alongside another service, not exposed externally | Agents that augment an existing workflow (e.g., auto-triage in a support platform) |

**Model serving layer — what sits between your code and the LLM:**

Directly calling Anthropic or OpenAI APIs in production is fragile — no fallback, no cost control, no centralized auth. Production agents route through a model serving proxy:

- **LiteLLM** — unified proxy that routes to any LLM provider with a single OpenAI-compatible API. Handles: fallback (if Claude is down, route to GPT-4), cost tracking per user/team, auth via API keys, model aliasing (your code says `model: "kira-fast"`, LiteLLM resolves to `claude-haiku-3-5`).
- **vLLM** — open-source inference server for self-hosted models. Implements paged KV cache attention for high throughput. Use when: using open-weight models (Llama, Mistral), need data to stay on-prem, want to avoid per-token API costs at scale.
- **TGI (Text Generation Inference)** — HuggingFace's inference server, similar to vLLM, with tighter HF ecosystem integration.

**Deployment strategies for model/behavior updates:**

- **Rolling update** — replace pods one by one. Used for code changes with no behavior risk (bug fixes, dependency bumps). K8s default.
- **Blue-green** — spin up a full new environment, switch traffic at once. Used when: the change is large and you want instant rollback. Expensive (double resources during switchover).
- **Canary** — route 5% of traffic to the new version, monitor quality metrics (eval score, error rate, token cost), promote to 100% if metrics hold. Best practice for model version upgrades — lets you catch regressions on real traffic before full rollout.
- **Shadow mode** — new version runs on all traffic in parallel but its responses are not shown to users. Responses are evaluated offline. Zero user risk, expensive (double inference cost). Used to validate a new model before canary promotion.

---

### How KIRA is deployed

KIRA uses a **distributed client + centralized backend** architecture — not a monolith deployed to one server.

```
flowchart TB
    subgraph centralized ["Centralized (deployed services)"]
        LITELLM["LiteLLM Proxy\nlitellm-internal-prd-ai.ai.arcadiaanalytics.com\n(model routing, auth, cost tracking)"]
        S3["S3 Bucket\n(telemetry, scrubbed session data)"]
        GIT["Git Repository\n(brain/ knowledge base, versioned)"]
    end

    subgraph client ["Per-engineer (local install)"]
        LAUNCH["aria launcher\n(SSO, secrets, LLM token)"]
        AGENT["Claude Code agent\n(real-time, local)"]
        BRAIN["Local brain clone\n(git pull to update)"]
        HOOKS["Hooks\n(pre_tool_use, post_tool_use, session_start)"]
    end

    LAUNCH --> AGENT
    AGENT --> LITELLM
    AGENT --> BRAIN
    AGENT --> HOOKS
    HOOKS --> S3
    GIT --> BRAIN
```

**Knowledge updates — zero downtime:**
Knowledge base changes (new playbooks, updated runbooks) go through a PR review process. Once merged, engineers run `git pull` in their KIRA directory and restart — or the update applies on next `search_kb` index refresh. No service restart, no deployment pipeline, no downtime.

**LiteLLM proxy — the centralized LLM backend:**
All LLM inference routes through a centralized proxy. This gives: per-user authentication (SSO token → LiteLLM key), model routing (route to different models by persona or cost), cost tracking per user/team, and the ability to swap models without client changes.

**CI gate — evals before every merge:**
Every PR touching `brain/` or agent hooks runs the eval suite. A regression (score < 80/100) blocks the merge. This is the quality gate for behavior changes.

**Standard agent deployment pattern (API-service model):**

For agents deployed as APIs (not CLI tools), the standard pattern is:

```
flowchart LR
    A["Code change"] --> B["CI: run evals\n(mock env, LLM-as-judge)"]
    B -- "pass >= 80/100" --> C["Build Docker image\n(embed model + weights)"]
    C --> D["Push to registry"]
    D --> E["K8s rolling update\n(zero downtime)"]
    E --> F["Health check\n(/health endpoint)"]
    F --> G["HPA: scale on load"]
```

Key deployment considerations:
- **Model weights in image or mounted?** Small models (MiniLM) bake into the Docker image. Large models mount from a shared volume or download at startup.
- **Secrets**: LLM API keys, vector DB credentials, tool integration tokens — all injected via K8s Secrets, never in the image.
- **Health check**: not just HTTP 200 — check that the LLM endpoint is reachable and the embedding model is loaded.
- **Evals in CI**: run eval suite on every PR against a staging environment. Block merge on regression.
- **Model updates**: when the LLM provider releases a new model version, re-run evals before switching the proxy routing. Model updates can change agent behavior even without code changes.

---

### Design tradeoffs

**Local-first vs server-deployed**

KIRA chose local-first: each engineer installs and runs the agent on their machine. Advantages: no latency to a server, private (data stays local), each engineer controls their version. Disadvantages: distribution is via git pull (slower than automatic), no centralized session logging (unless opt-in telemetry is enabled), harder to enforce consistent version across teams.

Server-deployed agents (API service) have the opposite tradeoffs: centralized updates, centralized logging, but network latency on every tool call and a single availability dependency.

**Knowledge update frequency**

With server-deployed agents, a knowledge update requires a deployment. With KIRA's git-based approach, a knowledge update is a PR merge + git pull. For fast-moving operational knowledge (runbooks that change weekly), the git approach is much faster.

---

### Interview questions this covers

- How do you deploy an AI agent that has external dependencies (LLM, tools)?
- How does KIRA's client + centralized backend architecture work?
- How do you update an agent's knowledge base without downtime?
- What is a CI eval gate and why is it necessary for agent deployments?
- What is the difference between deploying a CLI agent and an API-service agent?
- Why is deploying an AI agent fundamentally different from deploying a REST API?
- What is LiteLLM and why do you use a proxy instead of calling the LLM API directly?
- What is vLLM and when would you use it over a managed LLM API?
- What is canary deployment and why is it the right strategy for model version upgrades?
- How do you handle the case where the LLM provider updates their model and behavior changes?

---
