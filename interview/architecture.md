Here are **3 architectural views of ARIA** — each answers a different systems-thinking question.

---

## Diagram 1 — System Context (What is ARIA in the bigger picture?)

**Question it answers:** *Who uses it, what does it connect to, and where are the boundaries?*

```mermaid
flowchart TB
    subgraph users ["Users"]
        ENG["Engineers / Analysts / Ops"]
        BOT["Automated Workers\n(task queue agents)"]
    end

    subgraph aria ["ARIA Platform"]
        LAUNCH["Session Launcher\n(SSO identity + secrets + model token)"]
        AGENT["AI Agent Runtime\n(Claude Code)"]
        BRAIN["Local Knowledge Brain\n(cards, playbooks, routing rules)"]
        GUARD["Guardrails / Persona Policy"]
    end

    subgraph tools ["Tool & Integration Layer"]
        MCP_BRAIN["MCP: Knowledge Search"]
        MCP_DOCS["MCP: Product Docs"]
        MCP_ATL["MCP: Jira / Confluence"]
        CLI["Shell / AWS / kubectl / gh"]
    end

    subgraph external ["External Systems"]
        LLM["LLM Proxy\n(per-user auth + routing)"]
        JIRA["Jira / Confluence"]
        AWS["AWS / Data Lake / K8s"]
        DB["Internal DBs\n(QDW, Console, Redshift)"]
        DOCS["Docs Portal"]
    end

    ENG --> LAUNCH
    BOT --> LAUNCH
    LAUNCH --> AGENT
    LAUNCH --> GUARD
    AGENT --> BRAIN
    AGENT --> MCP_BRAIN
    AGENT --> MCP_DOCS
    AGENT --> MCP_ATL
    AGENT --> CLI
    MCP_BRAIN --> BRAIN
    MCP_DOCS --> DOCS
    MCP_ATL --> JIRA
    CLI --> AWS
    CLI --> DB
    AGENT --> LLM
    GUARD --> AGENT
```

**Systems thinking takeaway:**
- ARIA is **not just an LLM chatbot** — it is an **orchestrated agent platform**
- The **brain stays local** (versioned, reviewable knowledge)
- The **LLM is behind a proxy** (auth, cost, routing)
- **Tools are the action layer**; the model is the reasoning layer
- **Guardrails sit between intent and action**

---

## Diagram 2 — RAG & Knowledge Routing (How does ARIA stay grounded?)

**Question it answers:** *How does a user question become the right playbook before the agent acts?*

```mermaid
flowchart TB
    subgraph input ["Input"]
        Q["User question / ticket / task"]
    end

    subgraph routing ["Semantic Routing Layer"]
        KW["Keyword phrases extracted"]
        EMB["Query embedding\n(MiniLM)"]
        IDX["Local routing index\n(trigger vectors)"]
        SCORE["Cosine similarity + threshold"]
        DEDUP["Session dedup\n(skip already-seen cards)"]
    end

    subgraph knowledge ["Knowledge Layer"]
        ROUTE["Routing rules\n(trigger → action)"]
        CARD1["Knowledge card A"]
        CARD2["Knowledge card B"]
        MOD["Workflow module"]
        PB["Playbook / SOP"]
    end

    subgraph agent ["Agent Execution"]
        READ["Agent reads matched cards"]
        PLAN["Plan next steps"]
        ACT["Call tools / run commands"]
        ANS["Grounded answer / resolution"]
    end

    Q --> KW --> EMB --> SCORE
    IDX --> SCORE
    ROUTE --> IDX
    SCORE --> DEDUP
    DEDUP --> CARD1
    DEDUP --> CARD2
    DEDUP --> MOD
    DEDUP --> PB
    CARD1 --> READ
    CARD2 --> READ
    MOD --> READ
    PB --> READ
    READ --> PLAN --> ACT --> ANS
```

**Index build (offline path):**

```mermaid
flowchart LR
    A["Routing rules updated"] --> B["Parse triggers"]
    B --> C["Split into phrases"]
    C --> D["Embed triggers"]
    D --> E["Save local index"]
    E --> F["Ready for search_kb"]
```

**Systems thinking takeaway:**
- ARIA uses **routing RAG**, not “dump whole wiki into prompt”
- Flow is: **intent → semantic match → curated knowledge → action**
- **Multi-phrase indexing** improves short-query matching
- **Dedup** reduces token waste in long sessions
- Knowledge updates flow through **reviewed changes → index refresh**

---

## Diagram 3 — Agent Loop, Security & Quality (How is it safe and reliable?)

**Question it answers:** *What happens on each turn, and what stops bad actions or bad answers?*

```mermaid
flowchart TB
    subgraph session ["Session Start"]
        SSO["SSO login"]
        PERSONA["Resolve persona\n(viewer / engineer / admin)"]
        SECRETS["Inject secrets\n(Jira, QDW, GitHub)"]
        TOKEN["Fetch LLM token"]
    end

    subgraph loop ["Agent Turn Loop"]
        UIN["User input"]
        KB["1. search_kb FIRST"]
        LOAD["2. Read knowledge cards"]
        DECIDE["3. LLM decides next action"]
        HOOK["4. Pre-tool policy check"]
        TOOL["5. Execute allowed tool"]
        OBS["6. Observe result"]
        REPEAT{"Goal done?"}
        OUT["Final response"]
    end

    subgraph safety ["Safety Controls"]
        ENV["Environment check\ndev / staging / prod"]
        RBAC["Tool allow/deny by persona"]
        CONF["Confirmation gate\n(destructive actions)"]
        ASSUME["Mark assumptions explicitly"]
    end

    subgraph quality ["Quality Controls"]
        TRACE["Trace tool sequence"]
        EVAL["Eval scenarios\n(mocked external systems)"]
        CRITIC["LLM critic / hard gates"]
        REG["Regression on brain changes"]
    end

    SSO --> PERSONA --> SECRETS --> TOKEN --> UIN
    UIN --> KB --> LOAD --> DECIDE --> HOOK
    HOOK --> ENV
    HOOK --> RBAC
    HOOK --> CONF
    HOOK -->|allow| TOOL --> OBS --> REPEAT
    REPEAT -->|no| DECIDE
    REPEAT -->|yes| OUT
    DECIDE --> ASSUME
    TOOL --> TRACE
    TRACE --> EVAL --> CRITIC --> REG
```

**Sub-agent pattern (when work splits):**

```mermaid
flowchart LR
    MAIN["Main Agent"] -->|"pre-loaded context"| SUB1["Sub-agent: logs"]
    MAIN -->|"pre-loaded context"| SUB2["Sub-agent: data"]
    SUB1 --> MAIN
    SUB2 --> MAIN
    MAIN --> FINAL["Merged answer"]
```

**Systems thinking takeaway:**
- Production safety = **policy before tool execution**, not prompt pleading
- Reliability = **retrieve first + trace everything + eval regressions**
- Persona + environment = **defense in depth**
- Sub-agents work best with **pre-loaded context**, not rediscovery

---

## How the 3 diagrams fit together

| Diagram | Lens | Think of it as |
|--------|------|----------------|
| **1. System Context** | Macro | ARIA’s place in the enterprise ecosystem |
| **2. RAG Routing** | Knowledge | How answers stay grounded and relevant |
| **3. Agent + Guardrails + Eval** | Runtime | How each turn is executed safely and tested |

**One mental model:**

> **Diagram 1** = *where ARIA lives*  
> **Diagram 2** = *how ARIA knows what to read*  
> **Diagram 3** = *how ARIA acts safely and improves over time*

---

## Interview one-liner for all 3

> "ARIA is a local-first enterprise agent: a launcher sets up identity and secrets, the agent routes questions through semantic search into curated knowledge cards, then executes MCP and CLI tools under persona guardrails, with evals ensuring it searches first and loads the right context before acting."

Want these exported as a **single revision page** with 5 likely interviewer follow-ups per diagram?