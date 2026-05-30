# Rapid Fire — On the Spot, Direct, Clarity-Checking Questions

> Read this the morning of the interview. Answers are short on purpose — 3 to 5 sentences, spoken naturally. No memorizing, just understand the idea and say it in your own words.

---

## Part 1 — "Tell Me N Things About X"

These test whether you have real depth. Fire them naturally without pausing too long.

---

### Q. Tell me 5 problems with RAG in production.

One — retrieval misses. The right document exists but the query doesn't match it because the user phrased it differently than the document. Two — chunk boundaries cut context at the wrong place, so the retrieved chunk has the answer split across two pieces and neither one is useful alone. Three — stale index. The knowledge base gets updated but the vector index isn't rebuilt, so the model retrieves outdated information confidently. Four — context overload. You retrieve too many chunks, the model gets confused by noise, and the important part gets ignored. Five — silent failure. The model gives a confident, fluent answer that is just wrong, and there is no error or warning — the user walks away with bad information and you don't find out until something breaks in production.

---

### Q. Give me 3 reasons chunking is hard to get right.

First, fixed-size chunking cuts in the middle of a sentence or idea, so the retrieved chunk loses its meaning without the surrounding context. Second, the right chunk size depends on both the document type and the embedding model — what works for dense technical docs doesn't work for conversational text. Third, chunk overlap helps with boundary issues but adds duplication in the index, which means the model may receive nearly identical chunks that waste context window space and add noise.

---

### Q. What are 3 things that make an LLM agent unreliable?

The biggest one is that the model can decide to skip a step it should always do — like loading relevant knowledge first — because nothing in the architecture forces it. Second is error accumulation: if an early tool call returns wrong data, every subsequent step reasons on top of that bad data, and the final answer is confidently wrong in a way that's hard to trace. Third is non-determinism — the same input can produce different tool-calling sequences on different runs, which makes testing and debugging genuinely hard.

---

### Q. Name 3 cases where semantic search fails.

First, very short queries like single words or abbreviations — the embedding doesn't capture enough signal to distinguish meaning, so results are random. Second, domain-specific jargon that the embedding model has never seen during training — it maps the term to the wrong region of vector space. Third, when the user asks for something precise and transactional, like "what is order ID 12345" — semantic search finds vague thematic matches instead of the exact record, which is better served by a SQL query or API call.

---

### Q. What breaks when you move an AI POC to production?

The demo works because you handpicked clean documents, controlled the questions, and ran it yourself. In production, users ask things you never anticipated, documents are inconsistent or outdated, latency matters, cost matters, and the model starts returning wrong answers with confidence. The things that break first are usually retrieval quality (real queries don't match clean triggers), cost (you didn't cache anything), and trust (one confident wrong answer loses a user permanently). Most POCs also have no monitoring, so you don't even know when it starts failing.

---

### Q. What are 3 downsides of a very large context window?

First, cost — you pay per token, and loading 100K tokens per query gets expensive fast. Second, quality — LLMs are empirically worse at attending to information buried in the middle of a very long context, which is called the lost-in-the-middle problem. Third, latency — larger prompts take longer to process, both for the model and for any prefill caching layer, which hurts real-time user experience.

---

## Part 2 — Explain It Simply

These test whether you actually understand something or just know the words.

---

### Q. Explain embeddings to a non-technical person.

An embedding is a way of turning words or sentences into numbers so a computer can measure how similar two pieces of text are. Imagine plotting every word on a map where words with similar meanings are placed close together — "cat" and "dog" would be near each other, far from "rocket." An embedding is just that map location, expressed as a list of numbers. When you search for something, we convert your search into its map location and find whatever documents are closest to it on the map.

---

### Q. What is hallucination — what is actually happening inside the model?

The model is a next-token predictor. It was trained on billions of documents to predict what word comes next given everything before it. When it doesn't have the right information in its context, it doesn't say "I don't know" — it predicts the most statistically plausible next token based on patterns in training data. That prediction sounds fluent and confident but may be factually wrong. It's not lying — it genuinely has no mechanism to check whether its output is true. That's why grounding through retrieval matters: you give it the facts and ask it to use only those.

---

### Q. Explain what a vector database is in simple terms.

A regular database stores rows and columns and you search by exact match or range. A vector database stores numbers that represent the meaning of text, and you search by similarity — "find me things that mean something close to this query." Under the hood it uses approximate nearest neighbor algorithms to do this search fast across millions of entries. The key word is approximate — you trade a small chance of missing the best match for the ability to search at real-world speed.

---

### Q. What is the difference between a chatbot and an AI agent — in one sentence?

A chatbot responds. An agent decides what to do, calls tools to gather information or take action, observes the results, and repeats until the goal is met — it is a reasoning loop, not a question-answer machine.

---

## Part 3 — Opinion and Personal

These test whether you have a point of view. Don't hedge — give a clear answer.

---

### Q. If you had to build a chatbot today, what would you use?

For a quick POC I'd use a cloud LLM API directly with a simple retrieval layer — OpenAI embeddings, pgvector on Postgres if I'm already using it, and FastAPI to serve it. No framework overhead. If it needs to go to production with tool calling and more complex flows, I'd consider LangGraph for the state machine or build a custom agent loop depending on how much control I need over the exact tool-call sequence. The decision depends on whether flexibility or speed matters more.

---

### Q. Would you use LangChain or build from scratch?

LangChain is a good starting point when you want to prototype fast and the built-in chains match your use case closely. But once you hit production and need precise control over tool-call order, custom retry logic, exact token counting, or specific guardrails, the abstraction becomes a liability — you spend more time fighting the framework than building the product. For KIRA we built from scratch using MCP because we needed full control over what the agent could and couldn't do. I'd use LangChain for a POC and evaluate whether to keep it based on how much the production requirements diverge from the default behavior.

---

### Q. If RAG is so good, why do companies still fine-tune?

RAG solves the knowledge problem — giving the model access to current, domain-specific information. Fine-tuning solves the behavior problem — changing how the model responds, what tone it uses, how it structures answers, or making it deeply fluent in a very specific domain. They solve different things. If your model keeps giving answers in the wrong format, retrieves the right facts but explains them badly, or needs to internalize style and persona deeply, RAG doesn't help with that — fine-tuning does. Most production systems actually use both: RAG for knowledge freshness, fine-tuning for style and domain fluency.

---

### Q. What is the easiest thing to get wrong in a RAG system?

The chunk size. Teams almost always start with arbitrary fixed sizes — 512 tokens, 1000 tokens — without checking whether their actual documents split sensibly at that boundary. Then they wonder why retrieval is bad, and the real answer is that every important piece of information is getting cut in half. The second most common mistake is not having a test set — people evaluate RAG by asking it a few questions themselves and thinking it looks good, when in reality they've selected the easy cases and missed all the hard ones.

---

## Part 4 — Conceptual Clarity Checks

These catch people who know the words but not the idea.

---

### Q. Is a bigger context window always better?

No. A bigger context window means you *can* give the model more information, but more information is not the same as better information. If you fill a 200K token window with loosely relevant documents, the model's attention dilutes and it performs worse than if you had carefully selected 5 highly relevant documents in a 4K window. Context window size is a ceiling, not a target. The real skill is deciding what belongs in the context, not maximizing how much you can fit.

---

### Q. Why does an LLM sometimes give a confidently wrong answer?

Because confidence and correctness are unrelated in these models. The model generates text token by token based on learned patterns. When it is uncertain about a fact, it doesn't output uncertainty — it outputs the most statistically probable continuation of the text, which often sounds fluent and assertive. The model has no internal truth-checker. This is why grounding through retrieval, output validation, and evals exist — the model itself cannot tell you when it is wrong.

---

### Q. What's the real difference between semantic search and keyword search?

Keyword search finds documents that contain the exact words you typed. Semantic search finds documents that mean the same thing as what you typed, even if they use completely different words. If you search "how to restart a service" — keyword search only finds documents with those exact words, semantic search also finds documents that say "bring the process back up" or "reboot the daemon." The tradeoff is that semantic search can be fuzzy in ways you don't expect — it sometimes matches things that sound related but aren't, while keyword search is precise but rigid.

---

### Q. When does RAG fail silently?

RAG fails silently when the retrieved document looks relevant on the surface but is actually from a slightly different context than what the user asked — similar topic, different product version, different environment, different time period. The model reads the retrieved content, generates a fluent answer based on it, and has no way to know the document was the wrong one. The answer sounds correct and confident. This is worse than a retrieval miss, because a miss returns "I don't know" but a wrong retrieval returns a confident wrong answer. The fix is metadata filtering — scoping retrieval by version, date, tenant, or domain before doing vector search.

---

### Q. What's the difference between faithfulness and relevance in RAG evaluation?

Faithfulness asks: is the answer supported by the retrieved documents? Did the model make up anything that wasn't in the context? Relevance asks: does the answer actually address what the user asked? A model can be faithful but irrelevant — it accurately summarizes a document that wasn't the right one. It can also be relevant but unfaithful — it gives the right answer but adds facts that weren't in the retrieved context. You need both. In KIRA we specifically checked faithfulness through hard gates and LLM critic scoring, because in an enterprise system a confident hallucination is worse than no answer at all.

---
