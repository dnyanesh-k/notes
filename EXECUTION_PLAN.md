# Execution Plan — Job Switch 2026
> Target: 18–22L | Role: Java Full Stack / Lead Software Engineer | Timeline: 1 referral interview + broader applications
> Updated: July 2026 — pivoted from AI Engineer to Java Full Stack

---

## What You Have (Don't Rebuild, Just Execute)

| Area | File | Status |
|---|---|---|
| 169 Java interview questions | `interview/java-prep.md` | Ready — revise by block |
| Design Patterns (11 patterns) | `interview/design-patterns.md` | Ready — read + speak aloud |
| 15 System Design answers | `system-design-theory/answers/01–15` | Ready — Q1–Q8 are priority |
| DSA 67 problems | `dsa/DSA-Plan.md` | Ready — follow it |
| Behavioral stories | `interview/behavioral.md` | Needs update — rewrite for ReadyChairs |
| System design framework | `system-design-framework.html` | Open in browser, keep handy |
| WebJavaHelp material | `WebJavaHelp/day1–day15/` | Day 10–15 are priority |
| Company applications | `companies/master-list.md` | Updated for Java Full Stack |
| ReadyChairs codebase | `../readychairs/` | Live proof — walk through cold |
| VidyaTrack demo | personal project | Secondary proof — multi-tenant RBAC |

---

## What Is Genuinely Pending (Do These First)

### 1. Referral Interview (Priority Zero)
- Lead Software Engineer I, Java Full Stack — prep for this before applying anywhere else
- Use the 6-day plan below

### 2. Update LinkedIn
- Headline: `Full Stack Developer | Spring Boot · React · Next.js · PostgreSQL · AWS`
- About section: highlight ReadyChairs (production, real users) + CitiusTech AI integration work as differentiator
- Add ReadyChairs to Projects section
- Connect with 5 people per day at target companies

### 3. GitHub — ReadyChairs Already Cleaned
- README is done — keep it as is
- Pin ReadyChairs repo on GitHub profile
- Make sure VidyaTrack repo has a clean README too

### 4. Update behavioral.md
- Rewrite all stories with ReadyChairs as the primary project anchor
- Replace ARIA/VidyaTrack as primary with ReadyChairs — Spring Boot, booking engine, JWT, S3, AWS

---

## 6-Day Plan — Referral Interview Prep

> Use the java-prep.md revision order exactly. One block per session.

```
Day 1:  Block 11 (Java Core) + Block 17 (SOLID)
        → No material needed. Pure recall. Speak answers out loud.
        → Connect every SOLID principle to a ReadyChairs module.

Day 2:  Block 18 (Git) + Block 19 (TypeScript)
        → Open readychairs/frontend-web/ as reference for TypeScript
        → Know your own git history (161 commits, 15 PRs)

Day 3:  Block 1 (Spring Boot Internals) + Block 2 (IoC/DI)
        → WebJavaHelp/day15/Spring Boot Internals.pdf + day10/
        → Open ReadyChairsApplication.java, AdminProvisioner.java

Day 4:  Block 3 (MVC/REST) + Block 4 (Spring Security/JWT)
        → WebJavaHelp/day13/ + day14/ + day15/spring security/
        → Open SecurityConfig.java, JwtAuthenticationFilter.java, JwtUtil.java

Day 5:  Block 5 (JPA/Hibernate) + Block 12 (Design Patterns)
        → WebJavaHelp/day6/ + day7/ + day12/Spring Data JPA/
        → design-patterns.md — Proxy, Template Method, Chain of Responsibility
        → Open BookingRepository.java, BookingServiceImpl.java

Day 6:  Block 7 (SQL) + Block 9 (System Design) + Block 10 (Behavioral)
        → System design Q60 (Design a booking system) = ReadyChairs — know this cold
        → Practice: speak your ReadyChairs story in under 3 minutes
        → Speak your CitiusTech story (48 hrs/day automation) in under 2 minutes
```

---

## 4-Week Execution Calendar (After Referral Interview)

### Week 1 — Foundation + First Applications
> DSA: Two Pointer + Sliding Window (Patterns 1–2, 12 problems)
> Tech Prep: java-prep.md Blocks 1–6 (Spring core, Security, JPA)
> Apply: Tier 1 and Tier 2 companies (fintech + product)

| Day | DSA (45 min) | Tech Prep (45 min) | SD Reading (30 min) | Apply |
|---|---|---|---|---|
| Mon | Problems 1–2 | Block 1 (Spring Boot Internals) | Q1 URL Shortener | Tier 1 Fintech (1–4) |
| Tue | Problems 3–4 | Block 2 (IoC/DI) | Q2 Rate Limiter | Tier 1 Fintech (5–7) |
| Wed | Problems 5–6 | Block 3 (MVC/REST) | Q3 Notification | Tier 2 Product (8–12) |
| Thu | Problems 7–8 | Block 4 (Security/JWT) | Q4 Chat System | Tier 2 Product (13–16) |
| Fri | Problems 9–10 | Block 5 (JPA/Hibernate) | Q5 News Feed | Tier 3 SaaS (17–20) |
| Sat | Problems 11–12 | Block 17 (SOLID) | Q7 File Upload | Tier 3 SaaS (21–24) |
| Sun | Review Week 1 DSA | Block 18 (Git) | Re-read Q1–Q3 aloud | Tier 7 Remote (apply in parallel) |

### Week 2 — Binary Search + Hashing + More Applications
> DSA: Binary Search + Hashing (Patterns 3–4, 11 problems)
> Tech Prep: java-prep.md Blocks 7–8 (SQL, React/TypeScript)
> Apply: Tier 4 and Tier 5

| Day | DSA (45 min) | Tech Prep (45 min) | SD Reading (30 min) | Apply |
|---|---|---|---|---|
| Mon | Problems 13–14 | Block 7 (SQL) | Q8 Job Scheduler | Tier 4 Healthcare (25–28) |
| Tue | Problems 15–16 | Block 8 (React) | Q14 ETL Pipeline | Tier 4 Healthcare (29–32) |
| Wed | Problems 17–18 | Block 19 (TypeScript) | Q15 Error Monitoring | Tier 5 Banking GCC (33–36) |
| Thu | Problems 19–20 | Block 12 (Design Patterns) | Revise Q1–Q5 | Tier 5 Banking GCC (37–40) |
| Fri | Problems 21–22 | Block 13 (Testing) | Revise Q6–Q10 | Tier 6 Enterprise (41–44) |
| Sat | Problems 23–24 | Block 14 (Microservices) | Mock: 1 SD question verbal | Follow-ups week 1 |
| Sun | Review Week 2 | Block 6 (AOP) | Re-read Q5–Q8 aloud | Remote platforms |

### Week 3 — Stack + Linked List + Interviews Starting
> DSA: Stack + Linked List (Patterns 5–6, 11 problems)
> Expectation: first callbacks arriving this week from week 1 applications

| Day | DSA (45 min) | Interview Prep (1 hr) | Apply |
|---|---|---|---|
| Mon | Problems 25–26 | Block 15 (Docker/AWS) — ReadyChairs deployment story | Tier 7 DSA-light (45–48) |
| Tue | Problems 27–28 | Block 16 (Spring Advanced) — @Async, @Scheduled, Flyway | Tier 7 DSA-light (49–52) |
| Wed | Problems 29–30 | Speak Q1–Q5 aloud without notes (target: 3 min each) | Tier 8 Fintech-DSA (wk4+) |
| Thu | Problems 31–32 | Speak Q6–Q10 aloud without notes | Tier 8 Fintech-DSA (wk4+) |
| Fri | Problems 33–34 | Mock: 1 DSA (timed 20 min) + 1 SD question | Follow-ups |
| Sat | Problems 35–36 | Tell ReadyChairs story cold — time it (target: 3 min) | — |
| Sun | Full review | Rest | Follow up on week 1 applications |

### Week 4 — Trees + Graph + DSA-Heavy Companies Unlocked
> DSA: Trees + Graph (Patterns 7–8, 13 problems)
> This week apply to Razorpay, Groww, PhonePe, CRED, Zepto

| Day | DSA (60 min) | SD + Interview Prep | Apply |
|---|---|---|---|
| Mon | Problems 37–39 | Q1–Q3 verbal revision | Razorpay |
| Tue | Problems 40–42 | Q4–Q6 verbal revision | Groww |
| Wed | Problems 43–44 | Q7–Q8 verbal revision | PhonePe |
| Thu | Problems 45–46 | Q60–Q64 (SD booking, notification) verbal | CRED |
| Fri | Problems 47–48 | Mock full interview: behavioral + 1 DSA + 1 SD | Zepto, Zomato |
| Sat | Problems 49–50 | Salary negotiation practice (speak it out loud) | Follow-ups |
| Sun | LeetCode practice (1 medium timed) | — | — |

---

## Daily Structure (Non-Interview Weeks)

```
Block 1 — DSA (45 min)
  • 1–2 problems from DSA-Plan.md, in order
  • If stuck after 25 min → check NeetCode, understand pattern, re-solve tomorrow
  • Week 1–3: 30–45 min/problem. Week 4+: 45–60 min

Block 2 — Tech Prep / java-prep.md (45 min)
  • Follow the block schedule above — one block per session
  • After all blocks covered: rotate Blocks 1–6 weekly for refresh

Block 3 — System Design (30 min)
  • Weeks 1–2: Read 1 new answer from system-design-theory/answers/ (Q1–Q8 priority)
  • Weeks 3–4: Re-read previous answers — speak aloud without notes (target: 5 min per Q)
  • Always explain out loud, never read passively

Block 4 — Applications (45 min)
  • Apply to 2–3 companies from master-list following the tier schedule
  • Send 1–2 LinkedIn messages to referrals/connections at applied companies
  • Track status in master-list tracker

Block 5 — Buffer (rest of day)
  • ReadyChairs walkthrough / WebJavaHelp reading
  • GitHub/LinkedIn profile updates
  • If interview scheduled: use entire buffer for company-specific prep
```

---

## When You Get an Interview Scheduled

```
Day before:
  □ Read the company's product / engineering blog (30 min) — understand what they build
  □ Re-read behavioral.md
  □ Re-read 2–3 most relevant SD answers for that company type
  □ Open ReadyChairs codebase — trace the booking flow cold, no IDE help
  □ Sleep well

Morning of:
  □ Read behavioral.md again (15 min)
  □ Open system-design-framework.html — review the phase map
  □ Have water. Eat. No coffee if it makes you nervous.

In the interview:
  □ Clarify requirements before drawing anything
  □ Think out loud at every step
  □ Anchor to ReadyChairs for every Spring Boot / architecture answer
  □ Anchor to CitiusTech for AI-integrated features (differentiator, not primary pitch)
  □ For salary: anchor at 20L, don't say the bottom number first
```

---

## What "Done" Looks Like

```
✓ 67 DSA problems solved (pattern notes in DSA-Plan.md)
✓ Can speak all 15 SD answers without notes (5 min each)
✓ Can walk through ReadyChairs codebase cold — auth, booking, billing, notification
✓ Can answer all 19 blocks from java-prep.md fluently
✓ LinkedIn updated with ReadyChairs + Java Full Stack headline
✓ 40–50 companies applied (from master-list)
✓ 5–10 interviews scheduled
✓ Salary anchor: 20L, bottom 17L, know the script
```

---

## One Rule

> Apply every day. Prep without applying is just studying forever.
> The referral interview is this week — prep for it first.
> Start applying broadly from next week even if prep feels incomplete.
> A company that responds in week 3 gives you 3 weeks to prepare for their round.
