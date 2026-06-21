# Q13: Design AI Agent with Tool Calling (MCP-based)

> This is your strongest answer. ARIA at CitiusTech is this exact system. Own it.

---

## Clarifying Questions

First — what kind of agent is this? A task-completion agent (given a goal, autonomously takes steps to achieve it) or a conversational agent that calls tools reactively? The loop structure is different.

What tools does the agent have access to — database queries, API calls, code execution, file system? And are there safety constraints on what the agent can do autonomously versus what requires human approval?

What's the latency model — synchronous (user waits for the full result) or async (agent works in the background, user gets notified)? Multi-step agents can take minutes, which changes how we present results.

Is this multi-tenant? Multiple organizations using the same agent with different tool permissions and knowledge bases?

*Assuming: enterprise AI agent that can query internal systems (Jira, GitHub, databases), answer complex questions via RAG, take actions (create tickets, post comments), multi-tenant with role-based tool permissions, async for multi-step tasks, sync for single-turn Q&A.*

---

## Scope

I'll design: the agent reasoning loop (plan → act → observe → repeat), the MCP (Model Context Protocol) layer for tool integration, guardrails and access control, and the serving infrastructure. This is a full agent system — not just tool calling, but a complete agentic loop with safety.

---

## High Level Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI AGENT SYSTEM                                     │
│                                                                              │
│  User Request                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌────────────────┐    ┌─────────────────────────────────────────────────┐ │
│  │  Agent Gateway │    │              Agent Core (Reasoning Loop)        │ │
│  │  - Auth/RBAC   │──▶ │                                                 │ │
│  │  - Rate limit  │    │  ┌─────────┐  ┌──────────┐  ┌───────────────┐ │ │
│  │  - Session mgmt│    │  │  Plan   │─▶│  Act     │─▶│  Observe      │ │ │
│  └────────────────┘    │  │  (LLM)  │  │ (tools)  │  │ (parse result)│ │ │
│                        │  └─────────┘  └──────────┘  └───────┬───────┘ │ │
│                        │       ▲                              │          │ │
│                        │       └──────────────────────────────┘          │ │
│                        │                 (loop until done)                │ │
│                        └─────────────────────────────────────────────────┘ │
│                                          │                                   │
│                               ┌──────────▼──────────────────────┐          │
│                               │       MCP Tool Layer            │          │
│                               │                                 │          │
│                               │  ┌─────────┐  ┌─────────┐      │          │
│                               │  │ Jira MCP│  │ GitHub  │      │          │
│                               │  │ Server  │  │ MCP Srvr│      │          │
│                               │  └─────────┘  └─────────┘      │          │
│                               │  ┌─────────┐  ┌─────────┐      │          │
│                               │  │  DB MCP │  │  RAG    │      │          │
│                               │  │ Server  │  │  MCP    │      │          │
│                               │  └─────────┘  └─────────┘      │          │
│                               └─────────────────────────────────┘          │
│                                          │                                   │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Supporting Systems                                                 │    │
│  │  - Agent State Store (Redis + PostgreSQL)                          │    │
│  │  - Guardrails Engine (input/output validation)                     │    │
│  │  - Eval Logger (trace every step for debugging)                    │    │
│  │  - Knowledge Base (RAG retrieval — see Q9)                         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Deep Dive 1 — The Agent Reasoning Loop

The agent loop is the core of the system. It's what makes an agent different from a single LLM call.

```
LOOP:
  1. THINK: LLM receives task + conversation history + available tools → 
            decides: "I should search Jira for open P1 tickets"
  
  2. ACT: Calls the decided tool with parameters:
          tool: "jira_search"
          params: { "project": "BACKEND", "priority": "P1", "status": "open" }
  
  3. OBSERVE: Receives tool result:
              [{ ticket: "BACK-123", title: "DB connection pool exhausted", ... }]
  
  4. EVALUATE: LLM sees result, decides:
               "I have the ticket list. Now I need the recent logs to understand the issue."
               → decides to call another tool
  
  5. REPEAT: Until the LLM decides the task is complete OR max_steps reached

OUTPUT: Final answer composed from all observations
```

**What makes the loop work: the system prompt with tool descriptions**

The LLM doesn't magically know what tools exist. We describe every available tool in the system prompt:

```
You are an AI assistant for Acme Corp engineering teams. You can use these tools:

jira_search(project, priority, status, assignee) → list of Jira tickets
jira_get_ticket(ticket_id) → full ticket details including comments
github_list_prs(repo, state, author) → list of pull requests
github_get_pr(pr_number, repo) → PR details, diff, review comments
db_query(sql, database) → execute read-only SQL query (SELECT only)
knowledge_search(query) → search internal documentation

Rules:
- Only use tools available above
- For destructive actions (create, update, delete), ask for user confirmation first
- If uncertain, ask a clarifying question rather than guessing
- When you have enough information, provide your final answer
```

The LLM uses this context to decide which tool to call next. This is the **ReAct pattern** (Reasoning + Acting): the LLM reasons about what it knows, decides what to do, acts, observes, and reasons again.

---

## Deep Dive 2 — MCP (Model Context Protocol) Layer

MCP is a standardized protocol for connecting LLMs to tools. Instead of hardcoding tool implementations in the agent, each tool is a separate MCP server with a standard interface.

**Why MCP instead of custom tool calling?**

Without MCP: every time you add a new tool, you modify the agent code. Testing is harder — the tool and agent are coupled. Permissioning is ad-hoc.

With MCP: each tool is an independently deployed server. The agent discovers tools dynamically. Permissions are enforced at the MCP server level. New tools don't require agent code changes.

**MCP Server structure:**

```python
# Example: Jira MCP Server (built with FastMCP)
from fastmcp import FastMCP

mcp = FastMCP("jira-server")

@mcp.tool()
def jira_search(project: str, priority: str = None, status: str = "open") -> list[dict]:
    """
    Search Jira tickets. Returns list of tickets matching criteria.
    
    Args:
        project: Jira project key (e.g., "BACKEND", "FRONTEND")
        priority: Optional filter by priority (P1, P2, P3)
        status: Filter by status (open, in_progress, closed)
    """
    # Actual Jira API call with service account credentials
    jira_client = get_jira_client()
    jql = f"project = {project} AND status = {status}"
    if priority:
        jql += f" AND priority = {priority}"
    results = jira_client.search_issues(jql)
    return [format_ticket(t) for t in results]

@mcp.tool()
def jira_create_ticket(project: str, title: str, description: str, priority: str) -> dict:
    """
    Create a new Jira ticket. REQUIRES user confirmation before calling.
    
    Args:
        project: Jira project key
        title: Ticket title
        description: Ticket description
        priority: P1, P2, or P3
    """
    # This is a write tool — agent must confirm with user before calling
    pass
```

**Tool discovery:** The agent queries each registered MCP server for its tool manifest:

```json
{
  "tools": [
    {
      "name": "jira_search",
      "description": "Search Jira tickets...",
      "parameters": {
        "project": { "type": "string", "required": true },
        "priority": { "type": "string", "required": false }
      }
    }
  ]
}
```

The agent includes these tool descriptions in the LLM system prompt. The LLM then calls tools by name with parameters.

---

## Deep Dive 3 — Guardrails and Access Control

An agent with tool calling is powerful — and dangerous without guardrails. This is what separates a toy agent from a production one.

### Input Guardrails

Before the agent loop starts, validate the user's request:

```python
class InputGuardrail:
    def check(self, user_input: str, user_role: str) -> GuardrailResult:
        
        # 1. Harmful intent detection
        if self.harm_classifier.predict(user_input) > 0.7:
            return GuardrailResult.REJECT("Request contains harmful intent")
        
        # 2. Scope check — is this within the agent's domain?
        if not self.scope_classifier.is_in_scope(user_input):
            return GuardrailResult.REJECT("Request is outside my scope")
        
        # 3. PII in input
        if self.pii_detector.contains_pii(user_input):
            return GuardrailResult.WARN("Input may contain sensitive information")
        
        return GuardrailResult.ALLOW
```

### Role-Based Tool Permissions

Not all users should access all tools. A developer shouldn't be able to query HR databases:

```python
ROLE_TOOL_PERMISSIONS = {
    'engineer': ['jira_search', 'github_list_prs', 'knowledge_search', 'db_query'],
    'manager': ['jira_search', 'github_list_prs', 'knowledge_search'],
    'hr_team': ['hr_database_query', 'knowledge_search'],
    'admin': ['*']  # all tools
}

def get_allowed_tools(user_role: str) -> list[str]:
    allowed = ROLE_TOOL_PERMISSIONS.get(user_role, [])
    return [t for t in ALL_TOOLS if t.name in allowed or '*' in allowed]
```

The LLM system prompt only includes tool descriptions for tools the current user is allowed to use. The agent literally cannot call a tool the user isn't permitted for — it doesn't know it exists.

### Destructive Action Confirmation

Write tools (create, update, delete) must never execute autonomously:

```python
class AgentLoop:
    async def execute_tool(self, tool_name: str, params: dict) -> str:
        tool = self.tool_registry.get(tool_name)
        
        if tool.is_destructive:
            # Pause loop, ask user for confirmation
            confirmation = await self.request_user_confirmation(
                action=f"I want to {tool_name} with params {params}",
                reversible=tool.is_reversible
            )
            if not confirmation.approved:
                return f"Action cancelled by user"
        
        result = await tool.execute(params)
        return result
```

In ARIA, this pattern prevented the agent from accidentally creating Jira tickets or modifying GitHub branches without explicit confirmation.

### Output Guardrails

After the agent produces a response:

```python
class OutputGuardrail:
    def check(self, response: str, retrieved_context: list) -> str:
        
        # 1. Faithfulness: does the answer use only retrieved/observed data?
        if not self.is_grounded(response, retrieved_context):
            return "I found relevant information but cannot provide a confident answer."
        
        # 2. PII in output — redact before sending
        response = self.pii_redactor.redact(response)
        
        # 3. Confidential data check
        if self.contains_confidential_patterns(response):
            return "I found relevant information but it contains confidential details I cannot share."
        
        return response
```

---

## Deep Dive 4 — Agent State and Session Management

Multi-step agents can run for minutes. State must be durable — if the agent server crashes mid-loop, the agent should resume.

```sql
CREATE TABLE agent_sessions (
    id              UUID PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    status          ENUM('running','completed','failed','waiting_confirmation'),
    task            TEXT NOT NULL,
    max_steps       INT DEFAULT 10,
    current_step    INT DEFAULT 0,
    created_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP
);

CREATE TABLE agent_steps (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_id      UUID NOT NULL,
    step_number     INT NOT NULL,
    thought         TEXT,                -- LLM's reasoning (CoT)
    tool_name       VARCHAR(100),
    tool_params     JSON,
    tool_result     TEXT,
    duration_ms     INT,
    created_at      TIMESTAMP NOT NULL,
    PRIMARY KEY (session_id, step_number)
);
```

Each step is logged before execution. If the system crashes after step 3, the agent can be resumed from step 4 by replaying the step history into the LLM context.

**Step trace format stored in Redis for active sessions:**

```json
{
  "session_id": "abc",
  "task": "Find all P1 bugs assigned to me and summarize them",
  "steps": [
    {
      "thought": "I need to search Jira for P1 tickets assigned to the user",
      "action": { "tool": "jira_search", "params": { "priority": "P1", "assignee": "jdoe" } },
      "observation": "[BACK-123: DB timeout, BACK-145: Memory leak...]"
    },
    {
      "thought": "I have the tickets. Let me get details on each",
      "action": { "tool": "jira_get_ticket", "params": { "ticket_id": "BACK-123" } },
      "observation": "Title: DB connection pool exhausted. Root cause: missing connection release..."
    }
  ],
  "status": "running",
  "current_step": 2
}
```

---

## Scale — What Breaks at 10x?

At 10,000 concurrent agent sessions:

**LLM calls are the bottleneck:** Each loop iteration calls the LLM. A 5-step agent makes 5 LLM calls per session. At 10K sessions × 5 calls = 50K LLM calls/minute. OpenAI's rate limits are per-organization. Solution: multiple OpenAI API keys (within ToS for multiple team projects), priority queuing (critical agents get LLM access first), or self-hosted LLM for agent reasoning (Llama 3 70B is competitive with GPT-3.5 for reasoning tasks).

**Tool call latency adds up:** If each tool call takes 200ms and the agent makes 5 tool calls sequentially, that's 1 second just in tool latency. Optimize by identifying independent tool calls and running them in parallel: "I need data from Jira AND from GitHub" → call both simultaneously.

**Session state in Redis:** 10K active sessions × 50KB state = 500MB. Fine. The issue is write throughput — each step update requires a Redis write. 10K sessions × 1 step/sec = 10K writes/sec. Redis handles this easily.

**Observability:** 10K sessions running simultaneously, each with up to 10 steps = 100K events/sec in the eval log. Write to Kafka → async consumers write to ClickHouse for analytics. Never write eval logs synchronously in the agent loop — it adds latency to every step.

---

## Trade-offs

**ReAct vs CoT vs Plan-and-Execute:** ReAct (interleaved reasoning and acting) is the most flexible — the agent adapts its plan based on what tools return. Plan-and-Execute (make a full plan first, then execute all steps) is faster for simple tasks but brittle — if step 2 fails, the whole plan needs replanning. For enterprise agents with unpredictable tool results, ReAct is correct. Plan-and-Execute works for well-defined workflows.

**Autonomous vs supervised agents:** Fully autonomous agents (no human confirmation) are fast but risky. Supervised agents (confirm every action) are safe but slow. The hybrid — confirm only for destructive/irreversible actions — balances both. In production, start with all write actions requiring confirmation. As trust is built (via eval metrics showing low error rates), selectively enable autonomous write operations for specific low-risk actions.

**MCP vs direct tool integration:** MCP adds a network hop per tool call (agent → MCP server). This adds 5–20ms per tool call. For latency-critical agents, in-process tool implementations are faster. MCP is worth the overhead for: independent deployment of tools, polyglot tool servers (some tools in Python, some in Go), and clean permission enforcement. Direct integration is acceptable for simple 2–3 tool agents.

---

## Cross-Questions

**How do you prevent the agent from getting into an infinite loop?**

Hard limits: `max_steps = 10` (configurable per task type). If the agent hasn't completed the task in 10 steps, it terminates with a "could not complete" message and the step trace for debugging. Soft detection: if the last 3 tool calls are identical (same tool, same params), the agent is looping — terminate early. Also track unique tool call fingerprints in the session state; on repeat, inject a hint: "You've tried this already. Try a different approach."

**How do you debug a wrong answer from the agent?**

The step trace in PostgreSQL shows everything: every thought, every tool call, every tool result. Replay the session by reloading the step history into the LLM. Change one variable (different tool parameter, different model, different prompt) and observe the outcome. This is exactly how ARIA debugging worked — the eval log was the root cause analysis tool. Without full step logging, debugging agent behavior is guesswork.

**How do you handle a tool that returns an error mid-loop?**

The agent sees the error as an observation: `"Error: Jira API timeout. Try again later."` The LLM then decides: retry with backoff, try an alternative approach, or tell the user. If the LLM retries the same failing tool 3 times, inject a circuit breaker: "Tool jira_search is unavailable. Do not call it again in this session." The agent then either completes with available information or asks the user to try later.

**How would you implement multi-agent collaboration?**

Hierarchical agents: a orchestrator agent receives the high-level task, breaks it into subtasks, delegates to specialized sub-agents (a "Jira agent," a "GitHub agent," a "knowledge agent"), collects their results, and synthesizes the final answer. The orchestrator communicates with sub-agents via the same MCP protocol — each sub-agent is a tool to the orchestrator. Sub-agents can run in parallel (orchestrator calls all simultaneously), reducing total latency. The orchestrator's system prompt includes the sub-agent descriptions and how to delegate.

**How do you ensure the agent doesn't leak data between tenants in a multi-tenant setup?**

Tenant isolation is enforced at every layer. The agent session is created with `tenant_id` from the authenticated JWT. Each MCP server receives the tenant context and enforces it: the Jira MCP server only queries the tenant's Jira project, the DB MCP server only queries tables with `WHERE tenant_id = current_tenant`. The knowledge base RAG filters by `tenant_id` (from Q9). The agent LLM prompt never contains cross-tenant data — it's impossible by construction. Audit log records every tool call with `tenant_id` for compliance.
