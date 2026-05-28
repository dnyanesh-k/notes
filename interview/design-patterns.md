Here is a concise list of **design patterns used in ARIA**, whether they are useful, and a short reference table you can use for interviews or docs.

**Verdict:** Yes — most of these are **genuinely useful**, especially for **enterprise/local-first AI assistants**. A few are ARIA-specific optimizations rather than universal patterns.

---

## Are they useful?

| Category | Useful? | Why |
|----------|---------|-----|
| RAG / retrieval patterns | **Yes** | Directly improves answer quality |
| Agent / MCP patterns | **Yes** | Standard way to build tool-using agents |
| Security / guardrails | **Yes** | Required for production enterprise AI |
| Knowledge architecture | **Yes** | Makes domain knowledge maintainable |
| Eval / testing patterns | **Yes** | Prevents regressions in agent behavior |
| Local-first simplifications | **Sometimes** | Great for dev tools; may not scale to 250K users without changes |

---

## ARIA design patterns (short table)

| # | Design pattern | What it is in ARIA | Useful? |
|---|----------------|-------------------|---------|
| 1 | **RAG routing (not full-doc RAG)** | Semantic search maps user intent → curated knowledge cards/playbooks, not raw PDF chunks | **Yes** — simpler and more controllable for enterprise SOPs |
| 2 | **Retrieve-before-act gate** | Agent must search knowledge base before any other tool/action | **Yes** — reduces hallucination and wrong playbook usage |
| 3 | **Semantic search / embedding router** | MiniLM embeddings + cosine similarity to rank routing triggers | **Yes** — core RAG pattern for intent → knowledge matching |
| 4 | **Multi-phrase embedding** | Long triggers split into phrases; best phrase score wins | **Yes** — fixes short-query vs long-doc mismatch |
| 5 | **Multi-keyword merge search** | Multiple query phrases searched independently; max score kept | **Yes** — better recall for multi-topic requests |
| 6 | **Threshold-based retrieval** | Only return matches above similarity cutoff | **Yes** — filters noise from LLM context |
| 7 | **MCP tool protocol** | Knowledge search exposed as standard MCP tool | **Yes** — modular, reusable tool integration |
| 8 | **Local MCP server (stdio)** | Brain/search runs as local process, not cloud microservice | **Yes for local dev**; may need HTTP/gateway at huge scale |
| 9 | **Lazy index refresh** | Rebuild embedding index when routing rules change (mtime check) | **Yes** — keeps retrieval fresh without manual restarts |
| 10 | **Atomic index persistence** | Write temp file → rename swap for safe index save | **Yes** — avoids corrupted index on crash |
| 11 | **Session-aware deduplication** | Don’t return same knowledge card twice in one session | **Yes** — saves tokens and repeated context |
| 12 | **Scoped dedup for sub-agents** | Parent and sub-agent have separate “already seen” buckets | **Yes** — sub-agents aren’t blocked by parent’s prior searches |
| 13 | **Modular knowledge cards (“brain”)** | Domain docs split into small cards/modules/playbooks | **Yes** — easier to maintain, review, and route to |
| 14 | **Routing table as source of truth** | Human-editable trigger → action mapping drives retrieval index | **Yes** — ops/engineers can update behavior via PRs |
| 15 | **Lazy-loaded modules** | Only load workflow/domain module after routing match | **Yes** — smaller context, faster/cheaper agent runs |
| 16 | **Playbook / SOP pattern** | Repeatable investigation/runbooks encoded as structured guides | **Yes** — great for support/engineering workflows |
| 17 | **Skills vs playbooks split** | Invocable skills for automation; playbooks for guided workflows | **Yes** — separates “run tool” from “follow procedure” |
| 18 | **Sub-agent delegation** | Main agent spawns specialists with pre-loaded context | **Yes** — parallel work, less redundant KB fetching |
| 19 | **Pre-loaded context for sub-agents** | Pass already-fetched knowledge into sub-agent prompt | **Yes** — avoids 2–3x duplicate retrieval |
| 20 | **Persona-based RBAC** | SSO role maps to persona (viewer/engineer/admin) | **Yes** — enterprise must-have |
| 21 | **Pre-tool authorization hook** | Every tool call checked against persona + environment before run | **Yes** — fail-closed security |
| 22 | **Environment-aware permissions** | Same user may have different access in dev vs prod | **Yes** — prevents accidental prod damage |
| 23 | **Allow/deny tool patterns** | Regex/rules for permitted bash/API/MCP actions | **Yes** — practical policy enforcement |
| 24 | **Confirmation gate for destructive ops** | Explicit user approval before delete/write/S3 changes | **Yes** — critical safety pattern |
| 25 | **LLM gateway / proxy** | All model calls through internal LiteLLM proxy with per-user token | **Yes** — auth, cost control, central routing |
| 26 | **Runtime secret injection** | Credentials injected at session start from secret manager | **Yes** — no secrets in repo or prompts |
| 27 | **Session bootstrap hook** | Startup hook resolves identity, persona, env, credentials | **Yes** — consistent secure session setup |
| 28 | **Local-first brain** | Knowledge always read from local repo, not fetched remotely | **Yes for internal tools** — fast, versioned, reviewable |
| 29 | **PR-based knowledge updates** | Brain changes via reviewed PRs, not live edits | **Yes** — auditability and quality control |
| 30 | **Eval harness with mocks** | Agent runs against mocked Jira/AWS/kubectl/API traffic | **Yes** — safe regression testing |
| 31 | **LLM-as-judge (critic)** | Second model scores investigation quality and KB usage | **Yes** — scales quality review beyond manual checks |
| 32 | **Hard eval gates** | Automated pass/fail rules (e.g. search first, cards loaded) | **Yes** — catches obvious agent regressions |
| 33 | **Golden scenario regression suite** | YAML scenarios with expected root cause / required cards | **Yes** — continuous validation of agent behavior |
| 34 | **Assumption labeling** | Agent marks uncertain claims explicitly | **Yes** — improves trust and debugging |
| 35 | **Checkpoint during investigation** | Re-search knowledge when new domain appears mid-task | **Yes** — avoids tunnel vision |
| 36 | **Shared routing core library** | Same search/index logic used by MCP, CLI, and builder | **Yes** — DRY, one source of truth |
| 37 | **In-memory vector search (no vector DB)** | Brute-force cosine over small local index | **Useful at small scale** — simple; upgrade later for millions of chunks |
| 38 | **Investigate-don’t-defer rule** | Agent must use available tools before asking user to check | **Yes** — better UX and faster resolution |
| 39 | **Handoff / context compaction pattern** | Structured session handoff when context gets long | **Yes** — long-running agent sessions |
| 40 | **Automation registry pattern** | Central catalogue of automations, types, and routing | **Yes** — ops clarity at platform scale |

---

## Top 10 most interview-worthy patterns

If you want the **highest-value** ones to mention:

1. Retrieve-before-act gate  
2. RAG routing to curated playbooks  
3. MCP tool calling  
4. Persona RBAC + pre-tool hooks  
5. Multi-phrase semantic search  
6. Session dedup  
7. Sub-agent delegation with pre-loaded context  
8. LLM gateway/proxy  
9. Eval harness + hard gates  
10. PR-reviewed modular knowledge base  

---

## Patterns that are useful but ARIA-specific

| Pattern | Good for | Less ideal when |
|---------|----------|-----------------|
| Local-first brain | Internal engineering copilots | Public SaaS with dynamic tenant docs |
| In-memory vector search | Hundreds of routing entries | Millions of document chunks |
| stdio MCP server | Developer laptops / IDE agents | High-concurrency cloud API |
| Lazy mtime index rebuild | Local dev freshness | Real-time multi-tenant KB updates |

---

## One-line summary for interviews

> "ARIA combines **RAG routing**, **MCP tool calling**, **persona guardrails**, **modular knowledge cards**, and **eval-driven agent quality** — a practical enterprise pattern for grounded, auditable AI assistants."

Want this turned into a **1-page cheat sheet** (pattern → interview one-liner) for quick revision before your interview?