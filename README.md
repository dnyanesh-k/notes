# notes

I am preparing for System Design interviews for AI Engineer / 
Backend Engineer roles at Indian product companies and GCCs 
(targeting 18-22 LPA). I have 2.6 years experience in enterprise 
AI systems - RAG pipelines, MCP tooling, semantic search, LLM 
orchestration, ETL automation, FastAPI, AWS, Docker, Kubernetes.

Generate interview-ready answers for each system design question 
below. For EACH question follow this exact structure:

1. CLARIFYING QUESTIONS (what to ask interviewer first)
2. SCOPE DEFINITION (what to cover and skip, scale estimation)
3. HIGH LEVEL DESIGN (ASCII diagram with components)
4. DEEP DIVE (2-3 most complex components with data models, APIs, 
   failure handling)
5. SCALE & TRADE-OFFS (how to scale 10x, SQL vs NoSQL choice, 
   sync vs async, consistency decisions)
6. TOP 3 CROSS-CUTTING FOLLOW-UP QUESTIONS with answers 
   (multi-tenancy, sharding, caching, rate limiting etc.)

Keep answers interview-conversational - not textbook. 
I should be able to speak these answers out loud naturally.
Include Mermaid diagrams for HLD wherever possible.

---

QUESTIONS LIST:

CLASSIC SYSTEM DESIGN:
1. Design URL Shortener (Bitly)
2. Design Rate Limiter
3. Design Notification System
4. Design Chat System (WhatsApp)
5. Design News Feed (Twitter/LinkedIn)
6. Design Search Autocomplete
7. Design File Upload System (S3-like)
8. Design Job Scheduler

AI/GENAI SPECIFIC:
9. Design RAG Pipeline at Scale
10. Design LLM Chatbot at Scale (ChatGPT-like)
11. Design Semantic Search System
12. Design Document Processing Pipeline
13. Design AI Agent with Tool Calling (MCP-based)
14. Design ETL Pipeline at Scale
15. Design Real-time Error Monitoring and Alerting System

---

FRAMEWORK PATTERN I FOLLOW (apply this to every answer):
Mental trigger: Clarify → Scope → HLD → Deep Dive → Scale & Trade-offs

CROSS-CUTTING TOPICS to address in follow-ups for each question:
- Multi-tenancy (data isolation strategies)
- Horizontal scaling (stateless services, load balancing)
- Database sharding (shard key selection, hotspot problem)
- Caching strategies (write-through, write-back, eviction)
- Rate limiting (token bucket, sliding window)
- CAP theorem (consistency vs availability trade-offs)
- Message queues (Kafka vs SQS, when async over sync)
- Authentication at scale (JWT, OAuth, API keys)

Generate one question at a time and wait for me to say 
"next" before proceeding to the next question.
