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

WSGI and ASGI are both interface specifications that define how a Python web application communicates with a web server — but they handle concurrency completely differently.

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
## Q4. How does FastAPI Auto-Generate OpenAPI/Swagger Documentation?

FastAPI generates documentation by inspecting three things at startup
- route definitions 
- Python type hints
- Pydantic models 
and building an OpenAPI schema from them without any extra code.

When you define a route with path parameters, query parameters, or a Pydantic request body, FastAPI reads the type annotations at import time and converts them into a JSON Schema. This JSON Schema becomes the OpenAPI spec, which is served at /openapi.json.

FastAPI then serves two UI tools on top of that spec — Swagger UI at /docs which is interactive, meaning you can actually call endpoints directly from the browser — and ReDoc at /redoc which is better for reading documentation.

The powerful part is it's always in sync with your code. Since the docs are generated from your actual type hints and Pydantic models, there's no separate documentation file to maintain. If you add a new field to your Pydantic model, it automatically appears in the docs.

> a type hint is a special syntax that allows you to explicitly state what data type a variable, function parameter, or return value is expected to be
---
### How It Works Internally

```
Step 1 — App Startup
─────────────────────────────────────────
@app.post("/search")
async def search(query: SearchRequest) -> SearchResponse:
    ...

FastAPI calls add_api_route() internally
Stores route metadata in app.routes list

         ↓

Step 2 — Route Inspection
─────────────────────────────────────────
FastAPI uses Python's inspect module to read:
- Function signature          → parameter names
- Type hints (if present)     → field types
- Pydantic models (if present)→ nested schema
- Default values              → optional/required
- Decorators metadata         → path, method, summary

         ↓

Step 3 — JSON Schema Generation
─────────────────────────────────────────
Pydantic models → .model_json_schema()
                → generates JSON Schema per model

No Pydantic?    → FastAPI infers basic schema
                  from type hints alone
No type hints?  → parameter exists but type = unknown

         ↓

Step 4 — OpenAPI Spec Assembly
─────────────────────────────────────────
FastAPI assembles everything into
one OpenAPI 3.0 compliant JSON object:

{
  "paths": {
    "/search": {
      "post": {
        "parameters": [...],
        "requestBody": {...},
        "responses": {...}
      }
    }
  },
  "components": {
    "schemas": {
      "SearchRequest": {...},
      "SearchResponse": {...}
    }
  }
}

Served at → /openapi.json

         ↓

Step 5 — UI Rendering
─────────────────────────────────────────
/docs   → Swagger UI reads /openapi.json → renders interactive UI
/redoc  → ReDoc reads /openapi.json      → renders readable UI

Both UIs are just static JS that consume /openapi.json
FastAPI doesn't generate HTML — the JS does it at runtime
```
---

### Quick Code Reference

```python
# Everything below auto-appears in docs

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="AI Search API",        # appears in docs header
    description="RAG search API", # appears in docs
    version="1.0.0"
)

class SearchRequest(BaseModel):
    """Search query model"""        # docstring appears in docs
    text: str                       # required field
    top_k: int = 5                  # optional with default
    filters: Optional[dict] = None  # optional field

@app.post(
    "/search",
    summary="Semantic Search",          # endpoint title in docs
    description="Search knowledge base" # endpoint description
)
async def search(query: SearchRequest):
    ...
```

---

### How to Customize Docs

```python
# Disable docs in production
app = FastAPI(docs_url=None, redoc_url=None)

# Custom docs URL
app = FastAPI(docs_url="/api-docs")

# Add auth to docs
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="My API",
        version="1.0.0",
        routes=app.routes
    )
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
```

---

### Follow-up They Might Ask

*"How do you hide certain endpoints from docs?"*
> *"Use `include_in_schema=False` in the route decorator — `@app.get("/internal", include_in_schema=False)`"*

*"How do you add authentication to Swagger UI?"*
> *"Use `SecurityScheme` in OpenAPI config — typically adding `OAuth2PasswordBearer` or `APIKeyHeader` which automatically adds an Authorize button in Swagger UI."*

*"Can you disable docs in production?"*
> *"Yes — set `docs_url=None` and `redoc_url=None` when initializing FastAPI. Common practice to disable in production for security."*

## Q5. What is Uvicorn? What role Does it Play in FastAPI?

Uvicorn is an ASGI server — it's the component that actually runs your FastAPI application and handles incoming HTTP connections from the outside world.

Think of it this way — FastAPI is just a Python application, it has no ability to listen on a port or accept network connections by itself. 
Uvicorn is what sits between the network and your FastAPI app. 
It listens on a port, accepts HTTP connections, translates them into ASGI scope/receive/send interface that FastAPI understands, and sends responses back.

Uvicorn is built on two libraries — **uvloop** which is a ultra fast replacement for Python's default event loop written in Cython, and **httptools** which is a fast HTTP parser written in C. These two together make Uvicorn significantly faster than older servers like Gunicorn with sync workers.

In development you run it directly — `uvicorn main:app --reload`. In production the standard pattern is Gunicorn as the process manager with Uvicorn workers — Gunicorn handles process management, restarts, and multiple workers while each worker is a Uvicorn ASGI worker handling async requests.

---
### How Uvicorn Fits in the Stack

```
Internet / Load Balancer
         ↓
      Nginx
(reverse proxy, SSL termination)
         ↓
      Gunicorn
(process manager, spawns workers)
         ↓  ↓  ↓  ↓
   Uvicorn Workers
(ASGI server, event loop per worker)
         ↓
      FastAPI
(your application code)
         ↓
   Pydantic + SQLAlchemy
(validation + DB)
```

---

### Uvicorn Internals

| Component | What it does | Why fast |
|---|---|---|
| **uvloop** | Replaces default asyncio event loop | Written in Cython, 2-4x faster than default |
| **httptools** | HTTP request parser | Written in C, faster than Python http.server |
| **ASGI interface** | scope/receive/send protocol | Standardized async communication with app |

---

### Dev vs Production Commands

```bash
# Development — single worker, auto reload
uvicorn main:app --reload --port 8000

# Production — Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

# How many workers?
# General rule → (2 x CPU cores) + 1
# 2 core machine → 5 workers
```
---
- 4 workers literally means 4 separate Python processes, each running a complete copy of your FastAPI app.
```
Gunicorn (master process)
├── Worker 1 → full FastAPI app → own memory, own event loop
├── Worker 2 → full FastAPI app → own memory, own event loop
├── Worker 3 → full FastAPI app → own memory, own event loop
└── Worker 4 → full FastAPI app → own memory, own event loop
```
Why Gunicorn then?
Uvicorn alone can only run one process. If that process crashes — your app is down. If you need 4 processes — you'd have to manage them manually.
Gunicorn is the process manager that:
- Spawns workers => Starts N Uvicorn worker processes
- Health monitoring => Restarts crashed workers automatically
- Graceful reload => Zero downtime deploys
- Signal handling => SIGTERM, SIGHUP for graceful shutdown

Q. Why 2x Cores + 1? Why Not Equal to Cores?
If workers were CPU-bound (heavy computation):
```
= number of cores makes sense
Each core handles one worker at a time
Adding more workers just causes context switching overhead
```
But web workers are I/O-bound (waiting on DB, LLM, APIs):
```
Worker lifecycle for an AI API request:

Active on CPU → 5ms   (routing, validation)
Waiting on DB  → 50ms  (worker is idle)
Waiting on LLM → 300ms (worker is idle)
Active on CPU → 5ms   (serialize response)

Worker is idle 95% of the time!
```
But monitor memory — each worker loads your full app into RAM.

```
┌─────────────────────────────────────────┐
│              CLIENT                      │
│     (Browser / Mobile / API caller)      │
└─────────────────┬───────────────────────┘
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────┐
│              NGINX                       │
│         (Reverse Proxy)                  │
│                                          │
│  • SSL termination (HTTPS → HTTP)        │
│  • Static file serving                   │
│  • Rate limiting                         │
│  • Load balancing between pods           │
└─────────────────┬───────────────────────┘
                  │ HTTP (plain, internal)
                  ▼
┌─────────────────────────────────────────┐
│             GUNICORN                     │
│         (Process Manager)                │
│                                          │
│  • Spawns and manages worker processes   │
│  • Restarts crashed workers              │
│  • Handles graceful shutdown             │
│  • Does NOT handle requests itself       │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ UVICORN  │ │ UVICORN  │ │ UVICORN  │
│ Worker 1 │ │ Worker 2 │ │ Worker 3 │
│          │ │          │ │          │
│ • Owns   │ │ • Owns   │ │ • Owns   │
│   event  │ │   event  │ │   event  │
│   loop   │ │   loop   │ │   loop   │
│          │ │          │ │          │
│ • Parses │ │ • Parses │ │ • Parses │
│   HTTP   │ │   HTTP   │ │   HTTP   │
│          │ │          │ │          │
│ • Speaks │ │ • Speaks │ │ • Speaks │
│   ASGI   │ │   ASGI   │ │   ASGI   │
└──────┬───┘ └──────┬───┘ └──────┬───┘
       │             │            │
       ▼             ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ FASTAPI  │ │ FASTAPI  │ │ FASTAPI  │
│  App 1   │ │  App 2   │ │  App 3   │
│          │ │          │ │          │
│ Routing  │ │ Routing  │ │ Routing  │
│ Pydantic │ │ Pydantic │ │ Pydantic │
│ Your     │ │ Your     │ │ Your     │
│ handlers │ │ handlers │ │ handlers │
└──────┬───┘ └──────┬───┘ └──────┬───┘
       │             │            │
       ▼             ▼            ▼
┌─────────────────────────────────────────┐
│           YOUR DEPENDENCIES              │
│                                          │
│   PostgreSQL   Redis   LLM API   S3      │
└─────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────┐
│                 WEB SERVER TYPES                      │
├─────────────────┬───────────────────────────────────┤
│   NGINX/Apache  │  Traditional Web Server            │
│                 │  • Serves static files             │
│                 │  • SSL, caching, load balancing    │
│                 │  • Does NOT run Python code        │
├─────────────────┼───────────────────────────────────┤
│    UVICORN      │  ASGI Application Server           │
│                 │  • Runs Python async apps          │
│                 │  • Owns the event loop             │
│                 │  • Translates HTTP → ASGI          │
│                 │  • Does NOT serve static files     │
├─────────────────┼───────────────────────────────────┤
│    GUNICORN     │  Process Manager                   │
│                 │  • Manages worker processes        │
│                 │  • Does NOT handle requests        │
│                 │  • Does NOT run async code         │
└─────────────────┴───────────────────────────────────┘
```
```
┌─────────────────────────────────────────────────────┐
│              WEB SERVER                              │
│                                                      │
│  • Serves STATIC content                            │
│    (HTML, CSS, JS, images, files)                   │
│  • Handles SSL termination                          │
│  • Does load balancing                              │
│  • Does NOT execute code                            │
│  • Does NOT talk to databases                       │
│                                                      │
│  Examples → Nginx, Apache                           │
└─────────────────────────────────────────────────────┘
                        +
┌─────────────────────────────────────────────────────┐
│           APPLICATION SERVER                         │
│                                                      │
│  • Runs your BUSINESS LOGIC                         │
│  • Executes code (Python, Java, Node)               │
│  • Talks to databases                               │
│  • Processes dynamic requests                       │
│  • Generates responses on the fly                   │
│                                                      │
│  Examples → Uvicorn, Gunicorn, Tomcat, Node         │
└─────────────────────────────────────────────────────┘
```
```
1 MILLION USERS
(browsers, mobile apps, API clients)
           │
           │ requests from all over internet
           ▼
┌─────────────────────────────────────────┐
│           DNS SERVER                     │
│                                          │
│  myapp.com → points to Load Balancer IP  │
│  This is just a phonebook               │
│  "where is myapp.com?" → "here's the IP"│
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         LOAD BALANCER                    │
│      (AWS ALB / Nginx LB)               │
│                                          │
│  • Single entry point for all traffic   │
│  • Distributes requests across servers  │
│  • If Server 1 dies → sends to Server 2 │
│  • Does SSL termination (HTTPS → HTTP)  │
│  • Does NOT run your code               │
│                                          │
│  Think → Traffic policeman              │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       │          │          │ distributes traffic
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ SERVER 1 │ │ SERVER 2 │ │ SERVER 3 │  ← Physical/Virtual
│  (EC2)   │ │  (EC2)   │ │  (EC2)   │    Machines on AWS
└──────┬───┘ └──────┬───┘ └──────┬───┘
       │             │            │
       │    same stack runs on each server
       ▼
┌─────────────────────────────────────────┐
│              NGINX                       │
│         (Web Server)                     │
│                                          │
│  • First thing running on the server    │
│  • Receives request from Load Balancer  │
│  • Serves static files directly         │
│    (images, CSS, JS → no Python needed) │
│  • Forwards API requests to Gunicorn    │
│  • Handles compression, caching         │
│                                          │
│  Think → Receptionist in the building  │
└─────────────────┬───────────────────────┘
                  │ only API requests
                  │ static files handled here itself
                  ▼
┌─────────────────────────────────────────┐
│             GUNICORN                     │
│         (Process Manager)                │
│                                          │
│  • Spawns multiple Uvicorn workers      │
│  • Monitors worker health               │
│  • Restarts crashed workers             │
│  • Does NOT handle requests itself      │
│                                          │
│  Think → Office manager                 │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ UVICORN  │ │ UVICORN  │ │ UVICORN  │  ← Workers
│ Worker 1 │ │ Worker 2 │ │ Worker 3 │
│          │ │          │ │          │
│ Owns     │ │ Owns     │ │ Owns     │
│ event    │ │ event    │ │ event    │
│ loop     │ │ loop     │ │ loop     │
│          │ │          │ │          │
│ HTTP →   │ │ HTTP →   │ │ HTTP →   │
│ ASGI     │ │ ASGI     │ │ ASGI     │
│          │ │          │ │          │
│ Think →  │ │ Think →  │ │ Think →  │
│ Desk     │ │ Desk     │ │ Desk     │
└──────┬───┘ └──────┬───┘ └──────┬───┘
       │             │            │
       ▼             ▼            ▼
┌─────────────────────────────────────────┐
│              FASTAPI APP                 │
│                                          │
│  • Your actual Python code runs here    │
│  • Routing, validation, business logic  │
│  • Pydantic validation                  │
│  • Calls your dependencies              │
│                                          │
│  Think → The actual worker at the desk  │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│PostgreSQL│ │  Redis   │ │ LLM API  │
│(database)│ │ (cache)  │ │(OpenAI)  │
└──────────┘ └──────────┘ └──────────┘
```

```
1 MILLION USERS
           │
           ▼
┌─────────────────────────────────────────┐
│           DNS SERVER                     │
│  myapp.com → points to Ingress IP        │
│  Same as before                         │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         INGRESS CONTROLLER               │
│      (Nginx Ingress / AWS ALB)          │
│                                          │
│  • Replaces both Load Balancer + Nginx  │
│  • SSL termination                      │
│  • Path based routing                   │
│    /api → FastAPI service               │
│    /static → static file service        │
│  • Rate limiting                        │
│                                          │
│  Think → Smart building gate            │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         K8S SERVICE                      │
│      (ClusterIP / LoadBalancer)         │
│                                          │
│  • Internal load balancer inside K8s   │
│  • Distributes traffic across pods      │
│  • Stable IP even if pods restart      │
│  • Does NOT know about your app         │
│                                          │
│  Think → Internal office switchboard    │
└──────┬──────────┬──────────┬────────────┘
       │          │          │
       ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│  POD 1   │ │  POD 2   │ │  POD 3   │
│          │ │          │ │          │
│ your     │ │ your     │ │ your     │
│ container│ │ container│ │ container│
└──────┬───┘ └──────┬───┘ └──────┬───┘
       │
       │ inside each pod
       ▼
┌─────────────────────────────────────────┐
│         GUNICORN(Optional)              │ ← still needed?
│              +                          │   see below
│         UVICORN WORKERS                 │
│              +                          │
│         FASTAPI APP                     │
└─────────────────────────────────────────┘
```
```
Pod
└── Gunicorn
    ├── Uvicorn Worker 1 → FastAPI
    ├── Uvicorn Worker 2 → FastAPI
    └── Uvicorn Worker 3 → FastAPI

Good when:
- You want multiple workers per pod
- Pod has high CPU/RAM (4+ cores)
- Less pods, more workers per pod
```
```
Pod 1                Pod 2                Pod 3
└── Uvicorn          └── Uvicorn          └── Uvicorn
    └── FastAPI           └── FastAPI          └── FastAPI

Good when:
- K8s handles all scaling
- One process per pod
- Simple, clean, cloud native
```
### Follow-up They Might Ask

*"Can you run FastAPI without Uvicorn?"*
> *"Yes — any ASGI server works. Hypercorn and Daphne are alternatives. But Uvicorn is the recommended and most widely used option for FastAPI specifically."*

*"Why not just use Gunicorn alone?"*
> *"Gunicorn alone uses sync workers — it doesn't understand ASGI. You need Uvicorn workers to get async support. Gunicorn just manages the processes, Uvicorn handles the actual async request processing."*

*"How many Uvicorn workers in production?"*
> *"Standard formula is 2 x CPU cores + 1. But for AI applications with heavy I/O waits like LLM calls, you can push more workers since they spend most time waiting not computing."*

---
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
