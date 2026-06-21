# Behavioral Interview Prep
> Role: AI Engineer / Python Backend | Target: 15–20 LPA
> Format: STAR — Situation, Task, Action, Result
> Read this the morning of the interview. Don't memorize word for word — know the story, tell it naturally.

---

## The 3 Core Stories (use for all behavioral questions)

### Story 1 — Origin Story (Gap + VidyaTrack)
> Use for: "Tell me about yourself", "Why did you switch to tech?", "Tell me about a side project"

**The story:**
> "After my first job, I took a break and ran a small coaching institute in Maharashtra for a few years — teaching Math and Science to school students. I was managing 100+ students manually — attendance in notebooks, fees in Excel, parent communication on WhatsApp. It was genuinely painful. That experience is what led me to build VidyaTrack. I did CDAC in late 2023 to strengthen my engineering skills, then joined CitiusTech where I got into production AI engineering. VidyaTrack is now deployed on AWS, used by real institutes, handles fee installments, attendance, parent QR portals, and I built the entire thing solo — FastAPI, Next.js, PostgreSQL, Alembic migrations."

**Why it works:** Authentic, memorable, connects gap to product, shows entrepreneurial thinking.

---

### Story 2 — ARIA (Complex Technical System)
> Use for: "Tell me about a challenging project", "How did you build a production AI system?", "Tell me about RAG"

**The story:**
> "At CitiusTech I built the core components of ARIA — an enterprise AI assistant for healthcare operations. The hardest part was making retrieval reliable. Our knowledge base had 200+ documents and users asked questions in ways that didn't match how the documents were written. I built a custom routing pipeline — a semantic search tool using cosine similarity on a local embedding index. When a user asks anything, we extract key phrases, embed them using MiniLM, and retrieve the most relevant knowledge cards before the LLM does anything. This grounds the response — the model can't hallucinate facts it doesn't have in context. I also built the evaluation framework: 200 test cases, precision/recall for retrieval, LLM-as-judge for response quality. When retrieval precision dropped below threshold, the pipeline rejected the response rather than let a wrong answer through."

**Result:** "We took the system from internal demo to production-ready, with measurable eval scores that the team used to track regression across knowledge base updates."

---

### Story 3 — Engineering Problem Solved (Practical, Real)
> Use for: "Tell me about a bug you fixed", "When did you have to make a difficult technical decision?", "How do you handle ambiguity?"

**Two options — use whichever fits the question better:**

**Option A — Partial payment bug (VidyaTrack):**
> "I had a fee payment bug where paying ₹800 on a ₹500 installment would mark it paid, store ₹800 as paid_amount, and the extra ₹300 just... disappeared from accounting. The root cause was that payment distribution logic was applying the full amount to the first installment regardless of its remaining balance. I redesigned the distribution: identify the clicked installment, apply only what it needs, overflow to subsequent installments in due-date order, and cap the total at the plan balance. Added proper `partial` status with its own UI state. The fix required touching the service layer, repository eager loading, schema validation, and frontend together — I traced it through all four layers to make sure accounting stayed consistent."

**Option B — N+1 query fix (ARIA/VidyaTrack admin):**
> "The platform admin dashboard was making N+1 database queries — one per institute to fetch users, so 50 institutes = 51 queries. I spotted it by looking at query logs. Fixed it by batch-loading all users for all institutes in a single `WHERE institute_id IN (...)` query, then grouping them in-memory. Went from 51 queries to 2. Simple change, measurable improvement."

---

## Common Behavioral Questions + Short Answers

**Q: Why are you looking to switch?**
> "I've grown a lot at CitiusTech — built production RAG, MCP tooling, eval frameworks. I want to go deeper into AI infrastructure and work at a company where AI is the core product, not a side initiative."

**Q: What's your biggest weakness?**
> "I tend to want to understand systems deeply before I'm satisfied with a solution, which sometimes makes me slower on the first implementation. I've gotten better at identifying when 'good enough and shipped' is the right call versus when depth matters — production systems taught me that."

**Q: Where do you see yourself in 3 years?**
> "Technically, I want to be the person on the team who owns the AI layer end to end — not just calling APIs but understanding retrieval quality, eval pipelines, latency tradeoffs. Practically, I'm building a side project (VidyaTrack) and eventually want to run my own thing — but that's a 5–7 year horizon. Right now I want to be in an environment where I'm learning fast."

**Q: Tell me about a time you disagreed with your team.**
> "In ARIA, the initial approach was to load the full knowledge base into every prompt. I disagreed — it wasted context window and made evaluation harder because you couldn't tell which document the model was using. I proposed the routing approach: retrieve only the 2–3 most relevant cards per query. I built a small prototype showing precision improved and latency dropped. The team adopted it. The disagreement was about approach, not ego — I made sure to show data, not just argue."

**Q: How do you handle ambiguous requirements?**
> "I ask exactly two things: what is the user problem we're solving, and how will we know we solved it. Everything else is implementation detail. On VidyaTrack I didn't have a product manager — I had to talk to actual institute owners to understand what they needed. Sometimes what they said they wanted and what they actually needed were different. You learn to listen for the problem, not the feature request."

**Q: Tell me about a time you had to learn something fast.**
> "When I joined CitiusTech I had no production MCP tooling experience. I had two weeks to build the first version of the semantic search tool. I read the FastMCP docs, looked at how other MCP servers were structured, then just built it. If I got stuck I went deep on the specific part I was stuck on, not broad. The first version was working in 10 days. The second version — with hot-reload, dedup, and eval — took another 3 weeks."

---

## Questions to Ask the Interviewer
> Always ask 2–3 questions. Shows genuine interest. Avoid questions you could Google.

1. "What does the AI stack look like today — are you building RAG, fine-tuning, or mostly prompt engineering?"
2. "What's the biggest reliability problem you're solving in your AI systems right now?"
3. "How do engineers typically ramp up — is there a lot of domain context to absorb first, or do you jump into tickets early?"
4. "What does a good first 3 months look like for someone in this role?"

---

## Salary Negotiation Script

**When HR asks current CTC:**
> "My current CTC is 6L, but I'm targeting 18L for this role based on market rates for AI engineering at your scale. Is that in your band?"

**If they push for lower:**
> "I've done some research and for production AI engineering experience — RAG pipelines, LLM orchestration, deployed systems — the market range is 15–20L. I'd need to be in that range to make a move."

**If they say "we'll match your current + X%":**
> "I appreciate that, but I'm looking for a role-based offer, not a percentage hike on my current CTC. The work I'll be doing is materially different from what my current package reflects."

**If they ask your expected:**
> "18L. I'm flexible on structure — base, variable split, ESOP — as long as the total is in that range."

---

## Day-of Checklist
- [ ] Re-read Story 1, 2, 3 in the morning
- [ ] Review the company's AI product or tech blog (10 min)
- [ ] Have 2 questions ready to ask
- [ ] Know your numbers: 18L target, 15L bottom, don't say the bottom
- [ ] For technical rounds: clarify before coding, speak your thinking out loud
