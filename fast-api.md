## Q1. What is FastAPI? How is it different from Flask and Django?

- FastAPI is a **modern**, **high-performance** Python web framework built on top of Starlette for the web layer and Pydantic for data validation. 
- It's designed specifically for building APIs quickly with type safety, automatic documentation and async support out of the box.

The key differences come down to three things:

**1. performance** — FastAPI is built on ASGI and supports async natively, making it significantly faster than Flask which is WSGI-based and synchronous by default. In benchmarks FastAPI is comparable to NodeJS and Go for I/O heavy workloads.

**2. automatic validation and docs** — FastAPI uses Python type hints to automatically validate requests and generate Swagger and ReDoc documentation. 
In Flask you'd need separate libraries like Marshmallow and Flasgger to achieve the same.

**3. Django is a full framework** — it comes with ORM, admin panel, auth system, templating — everything. FastAPI is intentionally minimal, just the API layer. You bring your own ORM, auth, etc. Django is better for monolithic web apps, FastAPI is better for microservices and API-first backends.

---

### Key Comparison Table

| Feature | FastAPI | Flask | Django |
|---|---|---|---|
| Type | API framework | Micro framework | Full framework |
| Protocol | ASGI | WSGI | WSGI (ASGI in 3.0+) |
| Async | ✅ Native | ⚠️ Limited | ⚠️ Limited |
| Validation | ✅ Pydantic built-in | ❌ Manual/Marshmallow | ⚠️ Forms/DRF |
| Auto docs | ✅ Swagger + ReDoc | ❌ Manual | ❌ Manual |
| ORM | ❌ Bring your own | ❌ Bring your own | ✅ Built-in |
| Best for | Microservices, AI APIs | Simple APIs, scripts | Monolithic web apps |

---
## Q2. What makes FastAPI fast?

- FastAPI's performance comes from three layers working together.

**1. Starlette** — FastAPI is built on top of Starlette which is an ASGI framework. ASGI allows handling multiple requests concurrently in a single thread using Python's event loop, unlike WSGI which handles one request at a time per worker. This is the biggest performance factor.

**2. async/await natively** — because FastAPI is ASGI based, you can write async route handlers that don't block the event loop during I/O operations like DB queries or external API calls. So while one request waits for a DB response, the event loop serves other requests simultaneously.

**3. Pydantic v2** — Pydantic v2 was rewritten in Rust. So all request validation, serialization and deserialization happens at near-native speed instead of pure Python, which is significantly faster than alternatives like Marshmallow.

*In benchmarks FastAPI handles around 50,000-100,000 requests per second for simple endpoints — comparable to NodeJS and Go"*

---

### The 3 Layers Visually

```
Request comes in
      ↓
Starlette (ASGI) — handles concurrency via event loop
      ↓
FastAPI routing — matches path, method
      ↓
Pydantic v2 (Rust) — validates and parses request data
      ↓
Your route handler (async) — business logic
      ↓
Pydantic v2 — serializes response
      ↓
Response goes out
```

---

### Key Concepts to Remember

| Component | What it does | Why it's fast |
|---|---|---|
| **Starlette** | ASGI web layer | Concurrent requests via event loop |
| **Pydantic v2** | Validation + serialization | Rewritten in Rust |
| **async/await** | Non-blocking I/O | No thread blocking during waits |
| **Uvicorn** | ASGI server | Handles async connections efficiently |

---

### Follow-up They Might Ask

*"But Python has GIL, so how is it truly concurrent?"*

Answer:
> *"GIL blocks CPU-bound threads but async I/O doesn't use threads — it uses the event loop. So GIL is irrelevant for async I/O operations. For CPU-bound tasks we'd use multiprocessing or offload to a worker like Celery."*

## Q3. What is ASGI? How is it different from WSGI?

"WSGI and ASGI are both interface specifications that define how a Python web application communicates with a web server — but they handle concurrency completely differently.

WSGI — Web Server Gateway Interface — was introduced in 2003 and is synchronous. It handles one request at a time per worker process. So if you have 4 Gunicorn workers, you can handle 4 simultaneous requests. If a request is waiting for a DB call, that worker is completely blocked doing nothing. To scale you just add more workers — which means more memory and processes.

ASGI — Asynchronous Server Gateway Interface — is the modern successor. It's async first, so a single worker can handle thousands of concurrent connections using Python's event loop. When a request is waiting for I/O — DB, external API, file read — the worker doesn't block, it switches to serving another request. This is especially powerful for AI applications where you're waiting on LLM responses or vector DB queries which can take 200-500ms.

---

### The Core Difference Visually

**WSGI — Synchronous**
```
Worker 1: Request A → waiting for DB... (BLOCKED) ← wasting time
Worker 2: Request B → waiting for DB... (BLOCKED) ← wasting time
Worker 3: Request C → waiting for DB... (BLOCKED) ← wasting time

Need 100 concurrent requests? Need 100 workers. 💀
```

**ASGI — Asynchronous**
```
Worker 1: Request A → waiting for DB...
          → switches to Request B → waiting for LLM...
          → switches to Request C → processing...
          → DB responds → back to Request A ✅

1 worker handling hundreds of concurrent requests. 🚀
```

---

### Key Comparison Table

| Feature | WSGI | ASGI |
|---|---|---|
| Type | Synchronous | Asynchronous |
| Introduced | 2003 | 2019 |
| Concurrency model | One request per worker | Event loop, thousands per worker |
| Blocking I/O | ❌ Blocks worker | ✅ Non-blocking |
| WebSockets | ❌ Not supported | ✅ Native support |
| Best for | Simple web apps | APIs, AI, real-time, microservices |
| Servers | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |
| Frameworks | Flask, Django | FastAPI, Starlette, Django 3.0+ |

---

### Follow-up They Might Ask

*"Can Django use ASGI?"*
> *"Yes, Django added ASGI support in version 3.0, but it's retrofitted — not native like FastAPI. You need to explicitly write async views, otherwise it falls back to sync behavior. FastAPI was designed async-first from day one."*

*"When would you still choose WSGI?"*
> *"For simple CRUD apps with low concurrency, or when team is more comfortable with Flask/Django and the workload doesn't justify async complexity. WSGI is simpler to debug and reason about."*

---

4. How does FastAPI auto-generate OpenAPI/Swagger documentation?
5. What is Uvicorn? What role does it play in FastAPI?
6. What is the difference between `async def` and `def` route handlers in FastAPI?
7. How do you define path parameters and query parameters in FastAPI?
8. What is the request lifecycle in FastAPI?
9. How do you run a FastAPI app in production? (Uvicorn + Gunicorn)
10. What are the advantages of FastAPI over Flask for AI/ML applications?

---

## 🟢 PYDANTIC & VALIDATION (11–18)

11. What is Pydantic? How does FastAPI use it?
12. What is a Pydantic `BaseModel`? How do you define one?
13. How do you add field validation in Pydantic? (`Field`, `validator`, `model_validator`)
14. What is the difference between Pydantic v1 and v2? (FastAPI uses v2 now)
15. How do you handle optional fields in Pydantic?
16. What is `model_dump()` vs `dict()` in Pydantic v2?
17. How do you validate nested models in Pydantic?
18. What is `response_model` in FastAPI? Why is it important?

---

## 🟡 DEPENDENCY INJECTION (19–25)

19. What is dependency injection in FastAPI?
20. How does `Depends()` work? Write a simple example.
21. How do you share a DB session across a request using `Depends`?
22. What is the difference between function dependencies and class dependencies?
23. How do you handle dependency caching? (`use_cache` parameter)
24. How do you write a reusable auth dependency?
25. Can dependencies have dependencies? How does FastAPI resolve them?

---

## 🔴 AUTHENTICATION & SECURITY (26–31)

26. How do you implement JWT authentication in FastAPI?
27. What is OAuth2PasswordBearer? How does it work?
28. How do you implement role-based access control (RBAC) in FastAPI?
29. How do you secure FastAPI endpoints? (API keys, JWT, OAuth2)
30. How do you handle CORS in FastAPI?
31. What is `HTTPException`? How do you raise custom errors?

---

## 🟣 DATABASE & ORM (32–38)

32. How do you connect FastAPI to PostgreSQL using SQLAlchemy?
33. What is the difference between sync and async SQLAlchemy in FastAPI?
34. How do you manage DB sessions in FastAPI? (per-request session pattern)
35. What is Alembic? How do you run migrations?
36. How do you connect FastAPI to MongoDB? (Motor async driver)
37. How do you implement pagination in FastAPI with SQLAlchemy?
38. What is the N+1 query problem? How do you avoid it in SQLAlchemy?

---

## 🔵 MIDDLEWARE & BACKGROUND TASKS (39–44)

39. What is middleware in FastAPI? Write a simple request logging middleware.
40. What is the difference between middleware and dependencies?
41. What are background tasks in FastAPI? When would you use them?
42. How is `BackgroundTasks` different from Celery?
43. How do you add rate limiting in FastAPI?
44. How do you implement request timeout in FastAPI?

---

## 🟢 TESTING & PROJECT STRUCTURE (45–50)

45. How do you test FastAPI endpoints using `TestClient`?
46. How do you test async FastAPI routes using `AsyncClient` (httpx)?
47. How do you mock dependencies in FastAPI tests? (`app.dependency_overrides`)
48. What is the recommended project structure for a large FastAPI application?
49. How do you use `APIRouter` to organize routes?
50. How do you handle environment variables and config in FastAPI? (`pydantic-settings`)

---

## 📌 Priority Guide for Your Interviews

| Priority | Questions | Why |
|---|---|---|
| 🔥 Must nail | Q1–10, Q19–25 | Asked in every FastAPI interview |
| ⚡ High | Q11–18, Q32–38 | Backend + DB heavy roles |
| 📚 Good to know | Q26–31, Q39–50 | Senior/architecture rounds |

---

## 🎯 Your Advantage Questions

These map directly to your CitiusTech work — answer these with real examples:

- **Q6** — async def routes (your retrieval pipeline)
- **Q20** — Depends (your auth chains and session management)
- **Q24** — reusable auth dependency (your persona-based guardrails)
- **Q41** — background tasks (your ETL pipeline workflows)
- **Q45/46** — testing (your Pytest suites at CitiusTech)

---

*Always end FastAPI answers with a real example from your work. That's what separates you.*
