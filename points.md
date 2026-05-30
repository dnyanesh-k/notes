Developed a semantic search MCP tool and retrieval pipeline using FastMCP and fastembed, with an embedding index builder and hot-reload on knowledge base changes.

Built persona-based AI guardrails with environment-aware access control and read/write tool restrictions per role.

Designed a knowledge routing pipeline that uses cosine similarity over a local embedding index to retrieve relevant knowledge cards and ground LLM responses before external tool calls.

Built an agent eval framework with hard gates and LLM-as-judge scoring for routing behavior, grounding, and response quality.

Integrated MCP tool calling with external systems (Jira, GitHub, Kubernetes) under guardrail-enforced access controls.