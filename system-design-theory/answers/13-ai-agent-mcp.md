# Q13: Design AI Agent with Tool Calling (MCP-based)

> This is your strongest answer. ARIA at CitiusTech is this exact system. Own it completely.

---

> **Interview Phase Map** → Phase 1: Requirements (5 min) · Phase 2: Core Entities (2 min) · Phase 3: API Design (5 min) · Phase 4: High Level Design (12 min) · Phase 5: Deep Dives (10 min)

---

## Introduction

An AI agent is a system where a large language model does not just answer questions — it takes actions. Given a goal, the agent reasons about what steps to take, calls tools to gather information or perform operations, observes the results, and continues reasoning until the task is complete. This is fundamentally different from a chatbot: a chatbot responds, an agent acts.

The agent loop follows a pattern called **ReAct** (Reason + Act). At each step, the model receives the current state — the original goal, the history of what has been done, and the latest observations — and decides either to call a tool or to return a final answer. A tool could be a code executor, a database query, a web search, a file reader, an API call, or anything else the system exposes to the agent. The loop continues until the model decides it has enough information to respond.

**Model Context Protocol (MCP)** is a standardized interface for connecting LLMs to tools and data sources. Instead of every agent integration being custom-built, MCP defines a common protocol so any MCP-compatible tool can be plugged into any MCP-compatible agent without custom glue code. This dramatically simplifies building multi-tool agents, enables tool reuse across different agents, and allows safe, auditable tool access with defined schemas and permissions.

The hardest design problems in AI agents are safety and reliability. An autonomous agent can call destructive tools — deleting records, sending emails, executing code. Without guardrails, a single misunderstood instruction can cause irreversible damage. Production systems implement role-based tool access (an agent handling read-only queries should not have access to write tools), require confirmation for destructive actions, sandbox code execution, and maintain complete audit logs of every tool call made.

Session management, context window pressure as the conversation grows, and graceful degradation when a tool fails or times out are all important production concerns.

---

## How to Approach This in an Interview

AI agents go beyond chatbots: they take actions, use tools, and loop until a task is complete. The key is explaining: (1) the ReAct loop (think → act → observe → repeat), (2) why MCP is a better architecture than custom tool integration, and (3) the safety controls that prevent autonomous agents from doing dangerous things. You built ARIA — lead with concrete examples.

---

## Clarifying Questions

**1. Task-completion agent or reactive assistant?**

"Are we designing an agent that autonomously takes multiple steps to complete a goal (like 'analyze all P1 bugs and create a report'), or a conversational assistant that reactively calls tools based on each message?"

*Why this matters:* Task-completion = autonomous loop with state persistence across steps. Reactive = single-turn, tool call, return. The infrastructure is very different.

**2. What tools does it need?**

"What systems can the agent query and act upon? Read-only (search, query) or read-write (create tickets, post comments, modify data)?"

*Why this matters:* Read-only tools are safe to call autonomously. Write tools (create, update, delete) need explicit user confirmation. This is the critical safety boundary.

**3. Latency model — sync or async?**

"Should the user wait for the result (sync), or does the agent work in the background and notify when done (async)?"

*Why this matters:* Multi-step agents can take 30 seconds to 5 minutes. Nobody wants to wait 5 minutes for a response. Async (with progress updates) is better UX.

**4. Multi-tenant?**

"Multiple organizations using the same agent, each with their own tools and knowledge base?"

*Why this matters:* Tool permissions are per-tenant. A Jira MCP server for Org A should never touch Org B's Jira project.

### Assumptions

```
- Enterprise AI agent for engineering teams
- Tools: Jira, GitHub, internal databases (read-only + some write with confirmation)
- RAG over internal knowledge base (same as Q9)
- Async for multi-step tasks (background processing with progress updates)
- Sync for single-turn Q&A (< 2 seconds)
- Multi-tenant with role-based tool permissions
- Max 10 steps per session (prevents infinite loops)
```

---

## Functional Requirements

- Users should be able to invoke an AI agent that reads from and writes to connected tools (Jira, GitHub, internal DBs) using natural language
- The agent should request explicit user confirmation before executing any write or destructive action
- Users should be able to track the status and step-by-step progress of multi-step async agent tasks

> **How to say this in the interview:** *"I see three core things users need — invoke an AI agent that can read from and write to connected tools using natural language, receive explicit confirmation requests before any write or destructive action executes, and track the status and progress of multi-step async tasks. Does that capture it?"* The confirmation-before-write requirement is the most important safety constraint in the whole system — stating it as a first-class functional requirement, not just an NFR, tells the interviewer you're thinking about this seriously.

## Non-functional Requirements

> **NFR = Non-Functional Requirements.** These answer *how the system behaves*, not *what it does*. FR = "users should be able to post a tweet" (the feature). NFR = "the feed must load in under 200ms" (the quality). Same system, completely different axis.

- **Sync path < 2 seconds TTFT**: single-turn Q&A must feel immediate — tool call overhead hidden via streaming
- **HITL for all writes (non-negotiable)**: no destructive action executes without explicit human approval
- **Multi-tenant tool isolation**: user A's credentials and permissions must never be visible to user B's session
- **Max 10 steps per session**: hard limit to prevent infinite loops and runaway LLM cost
- **Full auditability**: every tool call, approval decision, and reasoning step logged with actor + timestamp

> **How to say this in the interview:** After agreeing on FRs, transition with: *"Now let me think about the non-functional requirements — the qualities the system needs to have, not just the features."* Then state each of the points above with its specific constraint attached. Always quantify — "the system should be secure" signals nothing; "no write action executes without explicit human approval, non-negotiable" shows you're serious about safety. Close with: *"Any specific constraints I should factor into my design?"*
>
> **Mental checklist for any system — pick your top 3:** Run through these mentally every time: *Is stale data acceptable, or must it always be correct?* (CAP — AP or CP?), *Which specific path must be fastest, and what is the millisecond target?* (Latency), *What is the read-to-write ratio and peak QPS?* (Scale). Add Durability, Security, or Compliance only when they are the defining constraint for that particular system — here, HITL safety and auditability are the defining constraints, so they earn their place.

---

## Core Entities

- **AgentSession** — user + initial prompt + tool permissions + step history
- **ToolCall** — tool name + input + output + approval_status + timestamp
- **ApprovalRequest** — pending write action + human-readable context shown to user
- **StepLog** — ordered record of reasoning steps and tool invocations

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## API Design

> **Why REST + SSE:** Session management and approval operations are standard request-response — REST is right for those. For streaming the agent's reasoning and tool call events in real time, SSE is better than WebSocket because the stream is server-to-client only. The approval endpoint is a synchronous POST because the agent is paused and waiting for the human response — that is a clear request-response. Say: *"I'll use REST for session management and approvals. For streaming the agent's reasoning as it works, SSE is the right choice over WebSocket — the event stream is one-directional, server pushing to client, so bidirectional WebSocket is unnecessary complexity. The approval endpoint is a plain POST because at that point the agent is stopped, waiting for a yes or no."*

```
POST /v1/sessions
body: { "initial_prompt": string, "tools": string[] }
→ 201: { "session_id": string }

POST /v1/sessions/{id}/messages
body: { "content": string }
→ 200 text/event-stream (SSE): streaming agent reasoning + tool call events

GET /v1/sessions/{id}/steps
→ 200: { "steps": StepLog[] }

POST /v1/sessions/{id}/approve
body: { "approval_id": string, "approved": bool }
→ 200: { "status": "approved|rejected" }

GET /v1/sessions/{id}/status
→ 200: { "status": "running|waiting_approval|complete|failed", "current_step": int }
```

---

## High Level Design

> **How to build this diagram in the interview — this phase matters most:** Do not draw the complete architecture upfront. Start by saying: *"Let me build the architecture by going through each endpoint one at a time."* For each endpoint: draw only the components it needs, talk through the data flow out loud as you draw — the interviewer needs to follow your reasoning, not just see boxes appearing — and add the relevant schema fields directly next to the database component in the diagram. When you spot a need for a cache, queue, or additional component mid-drawing, say *"I can see we'll need a cache here — I'm going to note that and come back to it in deep dives"*, then keep moving. Do not solve deep dive problems during this phase. Finish High Level Design only when all three functional requirements have a working data path through the diagram. The diagram above is your reference for what the final state looks like.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI AGENT SYSTEM                                     │
│                                                                              │
│  User Request                                                               │
│       │                                                                      │
│       ▼                                                                      │
│  ┌────────────────┐    ┌─────────────────────────────────────────────────┐ │
│  │  Agent Gateway │    │              Agent Core (ReAct Loop)            │ │
│  │  - Auth/RBAC   │──▶ │                                                 │ │
│  │  - Rate limit  │    │  ┌──────────┐  ┌─────────┐  ┌───────────────┐  │ │
│  │  - Session mgmt│    │  │  Think   │─▶│  Act    │─▶│  Observe      │  │ │
│  └────────────────┘    │  │  (LLM)   │  │ (tools) │  │  (parse)      │  │ │
│                        │  └──────────┘  └─────────┘  └───────┬───────┘  │ │
│                        │       ▲                              │           │ │
│                        │       └──────────────────────────────┘           │ │
│                        │                 (loop max 10 steps)               │ │
│                        └─────────────────────────────────────────────────┘ │
│                                          │                                   │
│                               ┌──────────▼──────────────────────┐          │
│                               │       MCP Tool Layer            │          │
│                               │                                 │          │
│                               │  ┌─────────┐  ┌─────────────┐  │          │
│                               │  │ Jira MCP│  │ GitHub MCP  │  │          │
│                               │  │ Server  │  │ Server      │  │          │
│                               │  ├─────────┤  ├─────────────┤  │          │
│                               │  │ DB MCP  │  │  RAG MCP    │  │          │
│                               │  │ Server  │  │  Server     │  │          │
│                               │  └─────────┘  └─────────────┘  │          │
│                               └─────────────────────────────────┘          │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │  Supporting Systems                                                 │    │
│  │  - Agent State (Redis active, PostgreSQL persistent)               │    │
│  │  - Guardrails (input/output validation)                            │    │
│  │  - Eval Logger (full step trace for debugging)                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: The ReAct Loop — Think, Act, Observe

**What makes an agent different from a chatbot?**

A chatbot: user asks → LLM generates response → done. One LLM call.

An agent: user gives a task → LLM decides what to do → calls a tool → gets result → LLM decides what to do next → calls another tool → ... → LLM has enough info → produces final answer. Multiple LLM calls, real-world actions.

**The ReAct Pattern (Reasoning + Acting):**

```
Session: "Find all P1 bugs assigned to me and summarize root causes"

─────────────────────────────────────────────────
Step 1: THINK
  LLM receives:
    - Task: "Find all P1 bugs assigned to me..."
    - Available tools: [jira_search, jira_get_ticket, github_list_prs, knowledge_search]
    - No observations yet
  
  LLM outputs:
    Thought: "I need to search Jira for P1 tickets assigned to the current user."
    Action: jira_search
    Params: { "project": "BACKEND", "priority": "P1", "assignee": "current_user", "status": "open" }

Step 2: ACT
  Call MCP Jira server with the decided tool + params
  
Step 3: OBSERVE
  Tool returns:
    [
      { "key": "BACK-123", "title": "DB connection pool exhausted", "priority": "P1" },
      { "key": "BACK-145", "title": "Memory leak in payment service", "priority": "P1" }
    ]

─────────────────────────────────────────────────
Step 4: THINK (again, with observation)
  LLM receives previous step + new observation
  
  Thought: "I have 2 P1 tickets. I need to get the details of each to understand root causes."
  Action: jira_get_ticket
  Params: { "ticket_id": "BACK-123" }

Step 5: ACT + OBSERVE
  Returns: Full ticket details, description, comments, recent activity
  
─────────────────────────────────────────────────
Step 6: THINK + DECIDE
  After fetching both ticket details:
  Thought: "I now have enough information to summarize the root causes."
  Action: FINAL_ANSWER  ← agent decides it's done
  
  Final answer: "You have 2 open P1 bugs:
    1. BACK-123: DB connection pool exhausted — root cause is missing connection.close() 
       in the payment retry handler. Recent fix attempted in PR #456 but not merged.
    2. BACK-145: Memory leak in payment service — suspected to be event listener 
       accumulation in the webhook handler. No fix yet."
```

**Why is this better than a single LLM call?**

The LLM doesn't know the real-time state of Jira. It has training data up to a cutoff date. By calling tools, it gets live data — actual tickets, actual code, actual database state. The agent bridges the gap between the LLM's frozen knowledge and the real world.

---

## Part 2: MCP — Model Context Protocol

**What is MCP?**

MCP is a standardized protocol (like HTTP for APIs) for connecting LLMs to tools. Anthropic developed it; it's now open-source and widely adopted.

**Why not just build custom tool functions?**

```python
# Without MCP: custom tool integration
class AgentTools:
    def jira_search(self, project, priority):
        jira_client = JiraClient(api_key=settings.JIRA_API_KEY)
        return jira_client.search(project, priority)
    
    def github_list_prs(self, repo, state):
        github_client = GithubClient(token=settings.GITHUB_TOKEN)
        return github_client.list_prs(repo, state)
    # ... 20 more tools hard-coded in one class

# Problems:
# 1. Adding a new tool = modifying agent code, redeploying
# 2. Tool authentication is mixed into agent code
# 3. Testing requires mocking the entire agent
# 4. No standard permission enforcement
```

```python
# With MCP: each tool is an independent server

# Jira MCP Server (deployed independently)
# Can be in Python, Go, TypeScript — doesn't matter
from fastmcp import FastMCP

mcp = FastMCP("jira-server")

@mcp.tool()
def jira_search(
    project: str,
    priority: str = None,
    status: str = "open",
    assignee: str = None
) -> list[dict]:
    """
    Search Jira tickets. Returns matching tickets.
    
    Args:
        project: Jira project key (e.g., BACKEND, FRONTEND)
        priority: Filter by P1, P2, P3, or None for all
        status: open, in_progress, done
        assignee: Filter by assignee username, or None for all
    """
    jql = f"project = {project} AND status = {status}"
    if priority:
        jql += f" AND priority = {priority}"
    if assignee:
        jql += f" AND assignee = '{assignee}'"
    
    return jira_client.search_issues(jql, max_results=50)

# Agent discovers tools by querying each MCP server:
# GET /tools → returns list of tool descriptions with parameter schemas
# Agent includes these descriptions in its system prompt
```

**Benefits of MCP:**

1. **Add tools without changing agent code:** Deploy a new MCP server, register its URL with the agent, it auto-discovers the new tools.
2. **Independent deployment:** Jira MCP server can be updated without touching the agent.
3. **Permission enforcement at tool level:** The MCP server validates that the requesting user has permission before executing.
4. **Standardized tool description format:** LLM gets consistent tool descriptions regardless of implementation language.

**Tool discovery:**

```python
class MCPToolRegistry:
    def __init__(self, mcp_server_urls: list[str]):
        self.tools = {}
        for url in mcp_server_urls:
            # Each MCP server exposes its tools via HTTP
            response = requests.get(f"{url}/tools")
            for tool in response.json()['tools']:
                self.tools[tool['name']] = MCPTool(
                    name=tool['name'],
                    description=tool['description'],
                    parameters=tool['input_schema'],
                    server_url=url
                )
    
    def build_system_prompt(self, allowed_tools: list[str]) -> str:
        """Build the tool list section of the system prompt."""
        tool_descriptions = []
        for tool_name in allowed_tools:
            tool = self.tools[tool_name]
            tool_descriptions.append(
                f"{tool.name}({', '.join(tool.parameters.keys())}): {tool.description}"
            )
        return "\n".join(tool_descriptions)
    
    async def call_tool(self, tool_name: str, params: dict) -> str:
        tool = self.tools[tool_name]
        response = await http_client.post(
            f"{tool.server_url}/call",
            json={"tool": tool_name, "params": params}
        )
        return response.json()['result']
```

---

## Part 3: Guardrails and Access Control

### Role-Based Tool Permissions

```python
ROLE_TOOL_PERMISSIONS = {
    # Engineers: can read Jira/GitHub, query their own data
    'engineer': [
        'jira_search', 'jira_get_ticket',
        'github_list_prs', 'github_get_pr',
        'knowledge_search',
        'db_query'  # read-only SQL
    ],
    
    # Managers: can read everything, no write operations
    'engineering_manager': [
        'jira_search', 'jira_get_ticket',
        'github_list_prs', 'github_get_pr',
        'knowledge_search',
        'db_query',
        'jira_create_ticket'  # can create tickets
    ],
    
    # HR: can only access HR tools
    'hr_team': [
        'hr_database_query',
        'knowledge_search'  # limited to HR knowledge base
    ],
    
    'admin': ['*']  # all tools
}

def get_allowed_tools_for_user(user_role: str, tenant_id: str) -> list[MCPTool]:
    allowed_names = ROLE_TOOL_PERMISSIONS.get(user_role, [])
    
    if '*' in allowed_names:
        return all_tools_for_tenant(tenant_id)
    
    return [
        tool for tool in all_tools_for_tenant(tenant_id)
        if tool.name in allowed_names
    ]
```

**Critical:** The LLM's system prompt ONLY includes descriptions of tools the user is allowed to use. The LLM cannot call `hr_database_query` if it's not in the system prompt — it doesn't know it exists.

### Input Guardrails

```python
class InputGuardrail:
    def __init__(self):
        self.harm_classifier = load_harm_classifier()
        self.scope_classifier = load_scope_classifier()
    
    def check(self, user_input: str, user_context: dict) -> GuardrailResult:
        # 1. Harmful intent
        harm_score = self.harm_classifier.predict(user_input)
        if harm_score > 0.7:
            return GuardrailResult.REJECT(
                "I can't help with that request.",
                reason="harmful_intent"
            )
        
        # 2. Prompt injection attempt
        # "Ignore previous instructions and do X"
        if self.detect_prompt_injection(user_input):
            return GuardrailResult.REJECT(
                "This request appears to be attempting to manipulate my instructions.",
                reason="prompt_injection"
            )
        
        # 3. PII in input (warn but allow)
        pii_detected = self.pii_detector.detect(user_input)
        if pii_detected:
            return GuardrailResult.WARN(
                f"Input may contain sensitive data: {pii_detected}",
                allow=True
            )
        
        return GuardrailResult.ALLOW

def detect_prompt_injection(text: str) -> bool:
    """Detect attempts to override system instructions."""
    injection_patterns = [
        r"ignore (?:previous|prior|all) instructions",
        r"disregard (?:previous|prior) (?:instructions|prompt)",
        r"you are now",
        r"new role:",
        r"system prompt:",
    ]
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in injection_patterns)
```

### Destructive Action Confirmation

```python
# Tool manifest includes safety metadata
TOOL_SAFETY = {
    "jira_search": {"destructive": False, "reversible": True},
    "jira_get_ticket": {"destructive": False, "reversible": True},
    "jira_create_ticket": {"destructive": False, "reversible": True},  # can delete
    "jira_update_ticket": {"destructive": True, "reversible": True},   # can revert
    "jira_delete_ticket": {"destructive": True, "reversible": False},  # CANNOT revert
    "github_merge_pr": {"destructive": True, "reversible": False},     # cannot unmerge
    "db_query": {"destructive": False, "reversible": True},            # read-only
    "db_execute": {"destructive": True, "reversible": False},          # SQL execute
}

class AgentLoop:
    async def execute_tool(self, session_id: str, tool_name: str, 
                           params: dict) -> str:
        safety = TOOL_SAFETY.get(tool_name, {"destructive": True})
        
        if safety["destructive"]:
            # Pause agent, ask user for confirmation
            await self.send_confirmation_request(
                session_id=session_id,
                message=f"I want to: {tool_name}({params})",
                reversible=safety["reversible"],
                warning="" if safety["reversible"] 
                         else "⚠️ This action CANNOT be undone"
            )
            
            confirmation = await self.wait_for_confirmation(
                session_id=session_id,
                timeout=300  # 5 minutes
            )
            
            if not confirmation.approved:
                return f"Action cancelled by user. I'll continue with the information I have."
        
        # Execute the tool
        result = await self.mcp_client.call_tool(tool_name, params)
        return result
```

**This was ARIA's most important safety feature:** In ARIA, this prevented the agent from accidentally creating Jira tickets, posting GitHub comments, or modifying database records without the engineer explicitly confirming. In testing, the agent correctly suggested ticket creation 15 times — all 15 required confirmation before execution.

### Output Guardrails

```python
class OutputGuardrail:
    def process(self, response: str, observations: list[str]) -> str:
        # 1. Faithfulness check
        if not self.is_grounded_in_observations(response, observations):
            return ("I found relevant information but I'm not confident enough "
                    "to provide a definitive answer. Please verify the details.")
        
        # 2. PII redaction
        response = self.pii_redactor.redact(response)
        # Redacts: emails, phone numbers, SSNs, credit card numbers
        
        # 3. Confidential data patterns
        if self.contains_confidential_patterns(response):
            # e.g., AWS secret keys, API tokens, internal system credentials
            return ("I found relevant information but it contains sensitive data "
                    "I shouldn't share.")
        
        return response
    
    def is_grounded_in_observations(self, response: str, observations: list[str]) -> bool:
        """Check if the answer is based on actual tool results."""
        if not observations:
            # Agent answered without calling any tools — possible hallucination
            return len(response) < 200  # allow short answers, flag long ones
        
        # Quick heuristic: key entities in response should appear in observations
        response_entities = extract_entities(response)
        observation_text = ' '.join(observations)
        
        grounded_count = sum(
            1 for entity in response_entities 
            if entity.lower() in observation_text.lower()
        )
        
        return grounded_count / max(len(response_entities), 1) > 0.7
```

---

## Part 4: Agent State — Persistence Across Steps

Multi-step agents can take minutes. State must survive server crashes:

```sql
CREATE TABLE agent_sessions (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT       NOT NULL,
    tenant_id       VARCHAR(100) NOT NULL,
    status          ENUM('running', 'completed', 'failed', 
                         'waiting_confirmation', 'cancelled') NOT NULL DEFAULT 'running',
    task            TEXT         NOT NULL,
    max_steps       INT          DEFAULT 10,
    current_step    INT          DEFAULT 0,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMP
);

CREATE TABLE agent_steps (
    id              BIGINT       PRIMARY KEY AUTO_INCREMENT,
    session_id      UUID         NOT NULL REFERENCES agent_sessions(id),
    step_number     INT          NOT NULL,
    
    thought         TEXT,                  -- LLM's reasoning (Chain of Thought)
    tool_name       VARCHAR(100),          -- which tool was called (NULL = final answer)
    tool_params     JSON,                  -- parameters passed to tool
    tool_result     TEXT,                  -- what the tool returned
    
    duration_ms     INT,
    created_at      TIMESTAMP    NOT NULL DEFAULT NOW(),
    
    UNIQUE KEY uk_session_step (session_id, step_number)
);
```

**The step log in Redis (active session — fast access):**

```json
{
  "session_id": "abc",
  "task": "Find all P1 bugs assigned to me and summarize them",
  "current_step": 2,
  "max_steps": 10,
  "steps": [
    {
      "thought": "I need to search Jira for P1 tickets assigned to the user",
      "action": { "tool": "jira_search", "params": { "priority": "P1" } },
      "observation": "[BACK-123: DB timeout, BACK-145: Memory leak]"
    },
    {
      "thought": "I have the tickets. Getting details for BACK-123",
      "action": { "tool": "jira_get_ticket", "params": { "ticket_id": "BACK-123" } },
      "observation": "Title: DB connection pool... Root cause: missing connection.close()"
    }
  ]
}
```

**Resume after crash:**

```python
async def resume_agent_session(session_id: str):
    # Load step history from PostgreSQL (persistent)
    steps = db.get_agent_steps(session_id)
    
    # Reconstruct the LLM conversation from the step log
    # The LLM sees the full history as if it had been continuous
    messages = [{"role": "system", "content": build_system_prompt(tools)}]
    messages.append({"role": "user", "content": session.task})
    
    for step in steps:
        messages.append({
            "role": "assistant",
            "content": f"Thought: {step.thought}\nAction: {step.tool_name}({step.tool_params})"
        })
        messages.append({
            "role": "tool",
            "content": step.tool_result
        })
    
    # Resume from the next step — agent continues as if nothing happened
    await run_agent_loop(session_id, messages, starting_step=len(steps))
```

---

## Scale — What Breaks at 10x?

> **How to transition into deep dives:** Say: *"I now have a working system that satisfies all three functional requirements. Let me harden it by addressing the non-functional requirements I identified at the start."* Then work through the NFRs one by one, starting with the most important. For each one, state the problem it creates in the current design, then your solution. After each point, pause and let the interviewer probe before moving on — do not monologue for more than two minutes at a stretch. The interviewer has specific signals they are looking for; if you are talking, they cannot ask for them. For senior roles, proactively identify the next bottleneck without waiting to be prompted.


10K concurrent agent sessions:

**LLM calls:** 10K sessions × 5 steps average = 50K LLM calls/minute. OpenAI limits per organization. Solutions: multiple API keys (within ToS), self-hosted LLM (Llama 3 70B competitive with GPT-3.5 for reasoning), priority queue (critical sessions get LLM access first).

**Parallel tool calls:** Independent tools can run simultaneously:

```python
async def execute_parallel_tools(tool_calls: list[dict]) -> list[str]:
    """Run independent tool calls in parallel."""
    tasks = [
        asyncio.create_task(mcp_client.call_tool(tc['tool'], tc['params']))
        for tc in tool_calls
    ]
    results = await asyncio.gather(*tasks)
    return results

# Example: agent decides it needs both Jira AND GitHub data
# Instead of: Jira call (200ms) + GitHub call (200ms) = 400ms
# Parallel:   both calls simultaneously = 200ms
# 50% latency reduction for multi-tool steps
```

**Session state:** 10K sessions × 50KB state = 500MB in Redis. Fine. Write throughput: 10K sessions × 1 step/sec average = 10K Redis writes/sec. Redis handles this easily.

---

## Trade-offs

**ReAct vs Plan-and-Execute:**

ReAct: LLM decides one step at a time based on what it just observed. Adapts to unexpected tool results. Best when: tool results are unpredictable (Jira search might return 0 or 50 tickets), user's intent is ambiguous.

Plan-and-Execute: LLM creates a full plan first ("Step 1: search Jira, Step 2: get ticket details, Step 3: summarize"), then executes each step. Faster for straightforward tasks (less LLM overhead per step). Brittle: if Step 2 fails, the whole plan needs replanning.

ARIA used ReAct — engineering tasks are inherently unpredictable (P1 ticket search might return 0 results, requiring a plan change). For well-defined workflows (generate a specific report), Plan-and-Execute would be faster.

**Sync vs async for multi-step tasks:**

Sync: user waits. Good for < 5 second tasks. Bad for 30-second+ tasks.

Async with polling: user gets a session_id, polls `GET /v1/agents/{session_id}/status`. Agent runs in background. When done, user fetches result. Good for anything > 10 seconds.

Async with WebSocket: client connects to WebSocket, receives step-by-step progress as the agent works. Best UX (like watching the agent work in real-time). What Cursor's agent mode shows you.

---

## Cross-Questions

**Q: How do you prevent the agent from getting into an infinite loop?**

Three layers:

1. **Hard step limit:** `max_steps = 10`. After 10 steps, agent terminates with whatever it has. Never exceeded in practice for well-defined tasks.

2. **Repetition detection:** Before each step, check if the last 3 tool calls are identical (same tool, same params):

```python
def detect_loop(steps: list[dict]) -> bool:
    if len(steps) < 3:
        return False
    last_3 = steps[-3:]
    # Fingerprint each step: tool_name + params hash
    fingerprints = [f"{s['tool']}{hash(str(s['params']))}" for s in last_3]
    return len(set(fingerprints)) == 1  # all 3 identical
```

If loop detected: inject guidance: "You've tried this 3 times. Try a different approach or tell the user what you need."

3. **Timeout:** Each session has a max runtime (e.g., 5 minutes). Background job terminates sessions that exceed this.

**Q: How do you debug a wrong answer from the agent?**

The step log in PostgreSQL is the root cause analysis tool. For every session, you have:
- The exact task
- Every thought the LLM had
- Every tool call with exact parameters
- Every tool result (raw data)
- The final answer

Replay: load the step history, modify one variable (different model, different tool parameter, modified system prompt), run from that step, observe if output changes. This is exactly how ARIA debugging worked in production — "why did the agent say X?" → look at step 3's tool result → the Jira query returned stale data.

Without full step logging, debugging agentic behavior is impossible. It's not optional infrastructure — it's table stakes for production agents.

**Q: How would you implement multi-agent collaboration (orchestrator + sub-agents)?**

```python
class OrchestratorAgent:
    """High-level agent that delegates to specialists."""
    
    def __init__(self):
        # Sub-agents are just MCP tools to the orchestrator
        self.tools = {
            "jira_agent": JiraAgentMCP(),      # specialist in Jira operations
            "github_agent": GitHubAgentMCP(),   # specialist in code/PR operations
            "knowledge_agent": KnowledgeMCP()   # specialist in knowledge base search
        }
    
    async def handle_task(self, task: str) -> str:
        # ReAct loop, but tools are sub-agents
        # Orchestrator decides which sub-agent to delegate to
        # Sub-agents run their own ReAct loops internally
        
        # Example: "Analyze the P1 bug BACK-123 and find related knowledge articles"
        # Orchestrator:
        #   Step 1: delegate to jira_agent("get_ticket_details BACK-123")
        #   Step 2: delegate to knowledge_agent("search for 'connection pool exhaustion'")
        #   Step 3: synthesize results into final answer
        pass
```

Sub-agents run in parallel when their tasks are independent. The orchestrator waits for all sub-agent results before synthesizing. This is exactly how multi-agent frameworks like AutoGen and CrewAI work — the MCP protocol makes it clean and decoupled.

**Q: How do you ensure tenant isolation in multi-tenant deployments?**

ARIA's approach:

1. **Tenant ID from JWT (authentication layer):** The `tenant_id` is extracted from the authenticated JWT, never from user input.

2. **MCP server enforces tenant context:** Every tool call includes `tenant_id` as a parameter. The Jira MCP server validates: "does this user's token have access to this project?" The DB MCP server appends `WHERE tenant_id = current_tenant` to all queries.

3. **Knowledge base filtering:** RAG queries (from Q9) filter by `tenant_id`. Org A's documents never appear in Org B's search results.

4. **Step log isolation:** Agent sessions are stored with `tenant_id`. Queries to retrieve session history always filter by `tenant_id`.

5. **Audit log:** Every tool call logs `{session_id, user_id, tenant_id, tool_name, params, timestamp}`. Compliance team can audit exactly what the agent did on behalf of each tenant.
