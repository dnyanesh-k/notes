# Dnyaneshwar Kanake
+91 9096100340 | dkanke12@gmail.com | [LinkedIn](https://linkedin.com) | [GitHub](https://github.com) | Pune, India

---

## Professional Summary

Software Engineer with 2.6 years of experience in enterprise AI engineering and backend development. Built production RAG pipelines, LLM orchestration systems with MCP tooling, and full-stack SaaS products. Skilled in Python, FastAPI, Next.js, PostgreSQL, AWS, and deploying AI systems used in production.

---

## Work Experience

### Software Engineer | CitiusTech Healthcare Technology Pvt. Ltd. | Sept 2024 – Present

**Enterprise AI Assistant Platform**
- Built a multi-agent AI system with MCP-based tool calling — given a production bug Jira ticket, the agent queries Grafana/Loki logs, inspects source code on GitHub, and raises PRs or Jira comments autonomously; a session-aware KB routing layer grounds every response before any tool executes.
- Built semantic search and knowledge routing using FastMCP and FastEmbed (MiniLM) — cosine similarity search on a live-updating embedding index grounds LLM responses in verified internal docs before every tool call; enforced role-based guardrails with fail-closed policy per tool execution.
- Built an eval framework using LLM-as-judge scoring retrieval and generation quality across ~200 tickets and Slack queries, measuring precision and recall for semantic search and assessing LLM response relevance, grounding, and hallucination to validate production readiness. 

**Error Automation & ETL Pipeline**
- Built a production error monitoring system that ingests daily error logs, classifies and deduplicates them, and automatically creates structured Jira tickets with Slack alerts — replacing a fully manual triage process across 180+ errors per day.
- Automated end-to-end error monitoring and Jira ticketing workflows, reducing 8 hours of daily manual effort and automating 180+ daily ticket creations previously handled manually. 

---

### Junior Developer | Hudl India Pvt. Ltd. | June 2019 – Feb 2020
- Built Python-based backend features and data processing utilities, contributing to code reviews, bug fixing, and unit testing.

---

## Projects

**VidyaTrack — Institute ERP SaaS** | FastAPI · Next.js · PostgreSQL · AWS | [GitHub](#)
- Built and deployed a production multi-tenant institute management SaaS covering fee management, attendance, test scores, admissions, and a parent-facing QR portal — actively used by schools and coaching institutes with automated fee reminders and schema-managed production deployments.
- Implemented tenant-level data isolation using JWT-based RBAC and scoped database queries, ensuring complete separation of institute data across all API endpoints.

---

## Skills

**Languages:** Python, SQL, JavaScript, TypeScript  
**AI / GenAI:** RAG, LLM Orchestration, MCP, FastMCP, Semantic Search, Vector Databases, LangChain, LiteLLM, FastEmbed  
**Backend:** FastAPI, Flask, REST APIs, ETL Pipelines, Redis, Pytest  
**Frontend:** Next.js, React  
**Cloud / DevOps:** AWS (S3, RDS, EKS), Docker, Kubernetes, GitHub Actions, ArgoCD  
**Databases:** PostgreSQL, MySQL, MongoDB  

---

## Education

**Post Graduate Diploma in Advanced Computing** | CDAC | 2024  
**Bachelor of Engineering** | SPPU | 2016 – 2019
