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
## Q6. Difference Between `async def` and `def` in FastAPI
---
In FastAPI both `async def` and `def` work for route handlers but FastAPI treats them completely differently internally.

When you define a route with `async def`, FastAPI runs it directly on the event loop. The handler can use `await` for I/O operations — DB calls, external APIs, LLM calls — without blocking the event loop. Other requests get served while this one waits.

When you define a route with `def`, FastAPI assumes it's a blocking/CPU-bound operation and automatically runs it in a threadpool executor — separate threads outside the event loop — so it doesn't block other async requests. FastAPI does this automatically, you don't configure anything.

The dangerous mistake is using `def` with blocking I/O like a synchronous DB call — FastAPI runs it in threadpool which has limited threads, so under high load you exhaust the threadpool and requests start queuing. The other dangerous mistake is using `async def` with blocking code like `time.sleep()` or a sync DB driver — this blocks the event loop entirely and freezes ALL requests.

At CitiusTech all our retrieval pipeline endpoints were `async def` because we were hitting vector DB, PostgreSQL, and LLM APIs — pure I/O bound operations. The only `def` handlers we had were for CPU-heavy data transformation tasks.

---

### How FastAPI Handles Each Internally

```
REQUEST COMES IN
       │
       ▼
FastAPI checks route handler type
       │
       ├─────────────────────────────────────────┐
       │                                         │
       ▼                                         ▼
  async def handler                         def handler
       │                                         │
       ▼                                         ▼
Runs directly on                    FastAPI calls
event loop                          run_in_executor()
       │                                         │
       ▼                                         ▼
await pauses handler          Runs in ThreadPoolExecutor
event loop serves             (separate thread)
other requests                event loop not blocked
meanwhile                              │
       │                               ▼
       ▼                     Thread completes
handler resumes                        │
       │                               ▼
       ▼                     Result returned to
response sent                  event loop
```
---

### The 4 Combinations — What's Safe and What's Not

```
┌─────────────────┬──────────────┬───────────────────────────┐
│   Handler Type  │  Code Inside │      Result               │
├─────────────────┼──────────────┼───────────────────────────┤
│                 │  await DB    │                           │
│   async def     │  await API   │  ✅ PERFECT               │
│                 │  await LLM   │  Event loop free          │
├─────────────────┼──────────────┼───────────────────────────┤
│                 │  time.sleep()│                           │
│   async def     │  sync DB     │  💀 DANGEROUS             │
│                 │  requests.get│  Blocks entire event loop │
│                 │              │  ALL requests freeze      │
├─────────────────┼──────────────┼───────────────────────────┤
│                 │  CPU heavy   │                           │
│     def         │  computation │  ✅ CORRECT USE           │
│                 │  sync libs   │  Runs in threadpool       │
│                 │              │  Event loop stays free    │
├─────────────────┼──────────────┼───────────────────────────┤
│                 │  await DB    │                           │
│     def         │  await API   │  ❌ WRONG                 │
│                 │              │  Can't use await in       │
│                 │              │  regular def              │
└─────────────────┴──────────────┴───────────────────────────┘
```

---

### Real Code Example

```python
# ✅ CORRECT — async def with async I/O
@app.get("/search")
async def search(query: str, db: AsyncSession = Depends(get_db)):
    # await is non-blocking
    # event loop serves other requests while waiting
    results = await db.execute(select(Document).filter(...))
    response = await llm_client.complete(query)
    return response

# ✅ CORRECT — def for CPU bound work
@app.post("/process")
def process_data(data: HeavyData):
    # CPU heavy — runs in threadpool automatically
    # doesn't block event loop
    result = heavy_numpy_computation(data)
    return result

# 💀 DANGEROUS — async def with blocking I/O
@app.get("/bad")
async def bad_handler():
    # blocks entire event loop
    # ALL other requests freeze until this completes
    time.sleep(5)
    response = requests.get("https://api.example.com")
    return response

# ✅ CORRECT — if you must use sync library in async context
@app.get("/correct")
async def correct_handler():
    # run blocking code in threadpool manually
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        blocking_function
    )
    return result
```

---

### ThreadPool in FastAPI — Important Detail

```
FastAPI's ThreadPool for def handlers
──────────────────────────────────────
Default size → 40 threads (Python default)

Under normal load:
Request → free thread available → runs immediately ✅

Under high load with slow def handlers:
Request 1  → Thread 1 (slow DB call, 2 seconds)
Request 2  → Thread 2 (slow DB call, 2 seconds)
...
Request 40 → Thread 40 (slow DB call, 2 seconds)
Request 41 → ⏳ WAITING — no free threads
Request 42 → ⏳ WAITING
...
💀 Threadpool exhausted — requests queuing up

Solution → use async def + async DB driver instead
```

---

### Key Decision Rule

```
What does my handler do?
         │
         ├── Calls DB / API / LLM / File I/O?
         │          │
         │          ▼
         │     Use async def
         │     + async libraries
         │     (asyncpg, httpx, aiofiles)
         │
         └── CPU heavy computation?
                    │
                    ▼
               Use def
               FastAPI runs it
               in threadpool
               automatically
```
```
Event Loop is a single infinite loop
that keeps checking:
"is any task ready to continue?"

┌─────────────────────────────────────┐
│           EVENT LOOP                 │
│                                      │
│  while True:                         │
│      tasks = get_ready_tasks()       │
│      for task in tasks:              │
│          task.run_until_next_await() │
│                                      │
└─────────────────────────────────────┘

Single thread. Single loop.
Runs one thing at a time.
But switches between tasks extremely fast.
```
What Happens Step by Step
```
@app.get("/search")
async def search():
    result = await db.query()    # line 2
    response = await llm.call() # line 3
    return response              # line 4
```
```
STEP 1 — Request arrives
──────────────────────────────────────
Event loop creates a Task for search()
Starts executing search() 
Runs normally until it hits await

STEP 2 — Hits await db.query()
──────────────────────────────────────
await tells event loop:
"I'm waiting for DB response
 go do something else
 come back when DB responds"

FastAPI saves entire state of search():
  • local variables
  • current line number (line 2)
  • call stack

This saved state = COROUTINE OBJECT
Coroutine gets SUSPENDED here

STEP 3 — Event loop is free
──────────────────────────────────────
Event loop picks up OTHER waiting tasks

  Task 2 (another request) → runs
  Task 3 (another request) → runs
  Task 4 (another request) → runs

Meanwhile DB is processing query
in background (OS/network handles it)

STEP 4 — DB responds
──────────────────────────────────────
OS signals event loop:
"hey DB responded for search() task"

Event loop marks search() task
as READY TO RESUME

STEP 5 — search() resumes
──────────────────────────────────────
Event loop picks up search() task
RESTORES exact saved state:
  • all local variables intact
  • resumes from LINE 2 exactly
    where it left off

result = db response  ← assigned here

Continues to line 3
hits await llm.call()
SUSPENDS again → same cycle repeats

STEP 6 — llm responds
──────────────────────────────────────
Same as step 4
Event loop marks task ready
Resumes from line 3
response = llm response

STEP 7 — return response
──────────────────────────────────────
No more awaits
Runs to completion
Returns response to Uvicorn
Uvicorn sends to client
Task is destroyed
```
---
```
Your FastAPI app is a process
running on the OS

When you await db.query():

STEP 1 — Python makes a syscall
──────────────────────────────────────
Python tells OS:
"open a TCP connection to PostgreSQL
 send this SQL query
 DON'T block me
 notify me when response arrives"

This is called NON-BLOCKING I/O syscall
(specifically epoll on Linux)

STEP 2 — OS takes over
──────────────────────────────────────
OS handles the network communication
completely independently:

  OS → TCP packet → Network → PostgreSQL
                               │
                               │ executes query
                               │
  OS ← TCP packet ← Network ← PostgreSQL

Your Python process does NOTHING here
OS is doing all the work
Your event loop is free to run other tasks

STEP 3 — OS gets response
──────────────────────────────────────
PostgreSQL sends response back
OS receives TCP packet
OS puts it in a buffer

Now OS needs to tell your app
"your data is ready"

STEP 4 — How OS notifies Python
──────────────────────────────────────
This is where epoll comes in
```
**What is epoll?**
```
epoll is a Linux kernel mechanism
for monitoring multiple file descriptors
and notifying when they're ready

File descriptor = OS representation of
  • network socket (DB connection)
  • file handle
  • pipe

┌─────────────────────────────────────┐
│           LINUX KERNEL               │
│                                      │
│  epoll instance watches:            │
│  ┌────────────────────────────┐     │
│  │ fd1 → PostgreSQL socket    │     │
│  │ fd2 → Redis socket         │     │
│  │ fd3 → LLM API socket       │     │
│  │ fd4 → another request...   │     │
│  └────────────────────────────┘     │
│                                      │
│  When any fd has data ready:        │
│  epoll_wait() returns immediately   │
│  with list of ready fds             │
└─────────────────────────────────────┘
```
**What PVM Actually Is?**
```
Your Python Code (.py)
         │
         ▼
  Python Compiler
         │
         ▼
  Bytecode (.pyc)
         │
         ▼
┌─────────────────────────────────────┐
│         PVM                          │
│   (Python Virtual Machine)          │
│                                      │
│  • Executes bytecode                │
│  • Manages memory                   │
│  • Handles objects                  │
│  • Is just a C program              │
│    running on OS                    │
└──────────────────┬──────────────────┘
                   │
                   │ PVM is still a
                   │ normal OS process
                   ▼
┌─────────────────────────────────────┐
│         OPERATING SYSTEM             │
│                                      │
│  Sees PVM as just another process   │
│  Like any C/Java/Go program         │
└─────────────────────────────────────┘
```

### Follow-up They Might Ask

*"What if I have both I/O and CPU work in same handler?"*
> *"Split them — do I/O in async def handler, offload CPU work to `run_in_executor()` or better a Celery worker for heavy tasks."*

*"What async DB drivers do you use?"*
> *"For PostgreSQL — asyncpg or SQLAlchemy async with asyncpg driver. For MongoDB — Motor. For Redis — aioredis."*

*"How does run_in_executor work?"*
> *"It submits a blocking function to a threadpool and returns an awaitable — so the event loop can continue serving other requests while the thread runs the blocking code."*

---
## Q7. Path Parameters and Query Parameters in FastAPI

In FastAPI, path parameters and query parameters are defined purely through function signature — no decorators or extra config needed.

Path parameters are part of the URL itself — you define them in the route path with curly braces and FastAPI automatically maps them to function arguments with the same name. Type hints handle validation — if you say `id: int` and someone passes a string, FastAPI returns a 422 automatically.

Query parameters are everything after the `?` in the URL — you define them as function arguments that are NOT in the path. If they have a default value they're optional, if they don't they're required.

FastAPI figures out which is which purely by comparing function argument names against the path string — if the name is in the path it's a path parameter, if it's not it's a query parameter. No extra annotation needed for basic cases.
---

### Path Parameters

```python
# Basic path parameter
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # URL: /users/123
    # user_id = 123 (auto converted to int)
    # /users/abc → 422 Unprocessable Entity
    return {"user_id": user_id}

# Multiple path parameters
@app.get("/pipelines/{pipeline_id}/documents/{doc_id}")
async def get_document(pipeline_id: str, doc_id: int):
    # URL: /pipelines/rag-v1/documents/42
    # pipeline_id = "rag-v1"
    # doc_id = 42
    return {"pipeline": pipeline_id, "doc": doc_id}

# Path parameter with validation
from fastapi import Path

@app.get("/users/{user_id}")
async def get_user(
    user_id: int = Path(
        ...,           # required
        gt=0,          # greater than 0
        le=1000,       # less than or equal 1000
        description="User ID must be positive"
    )
):
    return {"user_id": user_id}
```

---

### Query Parameters

```python
# Basic query parameter
@app.get("/search")
async def search(query: str):
    # URL: /search?query=hello
    # query = "hello"
    # /search → 422 (required, no default)
    return {"query": query}

# Optional query parameter with default
@app.get("/search")
async def search(
    query: str,
    top_k: int = 5,          # optional, default 5
    threshold: float = 0.7,  # optional, default 0.7
):
    # URL: /search?query=hello
    # URL: /search?query=hello&top_k=10&threshold=0.8
    return {"query": query, "top_k": top_k}

# Optional that can be None
from typing import Optional

@app.get("/search")
async def search(
    query: str,
    filter: Optional[str] = None  # truly optional
):
    # URL: /search?query=hello
    # filter = None if not provided
    return {"query": query, "filter": filter}

# Query parameter with validation
from fastapi import Query

@app.get("/search")
async def search(
    query: str = Query(
        ...,           # required
        min_length=3,  # minimum 3 chars
        max_length=100,
        description="Search query"
    ),
    top_k: int = Query(
        default=5,
        ge=1,          # greater or equal 1
        le=20          # less or equal 20
    )
):
    return {"query": query, "top_k": top_k}
```

---

### How FastAPI Decides Which is Which

```
@app.get("/pipelines/{pipeline_id}/search")
async def search(
    pipeline_id: str,    ← in path → PATH PARAMETER
    query: str,          ← not in path → QUERY PARAMETER
    top_k: int = 5,      ← not in path → QUERY PARAMETER
    db = Depends(get_db) ← Depends → DEPENDENCY
):

FastAPI logic at startup:
──────────────────────────────────────
1. parse route path → find {pipeline_id}
2. scan function arguments
3. pipeline_id in path? → YES → path param
4. query in path?       → NO  → query param
5. top_k in path?       → NO  → query param
6. has Depends?         → YES → dependency
```

---

### Path vs Query — When to Use Which

```
┌─────────────────┬─────────────────────────────────────┐
│  PATH PARAMETER │  QUERY PARAMETER                     │
├─────────────────┼─────────────────────────────────────┤
│ Identifies a    │ Filters, options, pagination        │
│ specific        │                                     │
│ resource        │                                     │
├─────────────────┼─────────────────────────────────────┤
│ /users/123      │ /users?role=admin&page=2            │
│ /docs/abc       │ /search?q=hello&top_k=5             │
│ /pipeline/rag   │ /items?sort=price&order=asc         │
├─────────────────┼─────────────────────────────────────┤
│ Always required │ Can be optional with defaults       │
├─────────────────┼─────────────────────────────────────┤
│ Part of         │ After ? in URL                      │
│ URL structure   │                                     │
└─────────────────┴─────────────────────────────────────┘
```

---

### Common Mistake — List as Query Parameter

```python
# Receiving multiple values for same key
# URL: /search?tags=python&tags=fastapi&tags=ai

from typing import List

@app.get("/search")
async def search(
    tags: List[str] = Query(default=[])
):
    # tags = ["python", "fastapi", "ai"]
    return {"tags": tags}

# Without Query() wrapper
# tags: List[str] = []  ← WONT WORK for query params
# Must use Query() for list query params
```

---

### Follow-up They Might Ask

*"What's the difference between Path() and just type hint?"*
> *"Type hint alone handles basic type validation and required/optional. Path() and Query() give you additional constraints like min/max values, string length limits, regex patterns, and custom descriptions that appear in Swagger docs."*

*"What happens if path parameter type doesn't match?"*
> *"FastAPI automatically returns 422 Unprocessable Entity with a detailed error message showing exactly which field failed and why — this is handled by Pydantic internally."*

*"Can query parameters be complex types like dict or list?"*
> *"Lists yes — using `Query()` wrapper. Dicts no — for complex nested input you should use a request body with a Pydantic model instead."*

---
## Q8. What is the Request Lifecycle in FastAPI?
The request lifecycle in FastAPI is the complete journey of a request from the moment it hits the server to the moment the response goes back — passing through multiple layers each with a specific job.

- It starts at Uvicorn which receives raw TCP bytes and translates them into ASGI format. 
- Then middleware runs — every registered middleware executes in order before the request reaches your route. 
- Then FastAPI's dependency injection resolves all dependencies. 
- Then Pydantic validates the request data. 
- Then your actual route handler executes. 
- Then the response model serializes the output. 
- Then middleware runs again on the way out. 
- Finally Uvicorn converts back to HTTP and sends to client.

The important thing to understand is middleware wraps the entire request like an onion — outermost middleware runs first on the way in and last on the way out. Dependencies run per-request just before the handler. And response_model validation happens after your handler returns — so you can return more data than the model exposes, Pydantic will strip the extra fields.

### Complete Request Lifecycle

```
CLIENT sends HTTP Request
         │
         ▼
┌─────────────────────────────────────┐
│         UVICORN                      │
│                                      │
│  • Receives raw TCP bytes           │
│  • Parses HTTP using httptools      │
│  • Builds ASGI scope dict           │
│  • Calls FastAPI with               │
│    (scope, receive, send)           │
└──────────────────┬──────────────────┘
                   │ ASGI scope
                   ▼
┌─────────────────────────────────────┐
│      MIDDLEWARE LAYER (IN)           │
│                                      │
│  Middleware 1 (outermost)           │
│  └── Middleware 2                   │
│      └── Middleware 3 (innermost)   │
│                                      │
│  Each middleware can:               │
│  • Read/modify request              │
│  • Add headers                      │
│  • Log request                      │
│  • Short circuit (return early)     │
│  • Pass to next via call_next()     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         ROUTING                      │
│                                      │
│  FastAPI matches:                   │
│  • HTTP method (GET/POST/etc)       │
│  • URL path pattern                 │
│  • Finds the right route handler    │
│                                      │
│  No match → 404 Not Found           │
│  Wrong method → 405 Not Allowed     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      DEPENDENCY INJECTION            │
│                                      │
│  FastAPI resolves dependency tree   │
│  bottom up:                         │
│                                      │
│  get_db() → get_current_user()      │
│          → get_permissions()        │
│                                      │
│  All dependencies execute BEFORE    │
│  your handler runs                  │
│                                      │
│  Dependency fails → handler never   │
│  executes, error returned           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      REQUEST VALIDATION              │
│         (Pydantic)                   │
│                                      │
│  • Path parameters validated        │
│  • Query parameters validated       │
│  • Request body parsed + validated  │
│  • Type coercion applied            │
│                                      │
│  Validation fails → 422             │
│  Unprocessable Entity               │
│  Handler never executes             │
└──────────────────┬──────────────────┘
                   │ clean validated data
                   ▼
┌─────────────────────────────────────┐
│      YOUR ROUTE HANDLER              │
│                                      │
│  @app.post("/search")               │
│  async def search(                  │
│      query: SearchRequest,          │
│      db = Depends(get_db),          │
│      user = Depends(get_user)       │
│  ):                                 │
│      result = await db.query()      │
│      return result                  │
│                                      │
│  Your actual business logic runs    │
└──────────────────┬──────────────────┘
                   │ raw return value
                   ▼
┌─────────────────────────────────────┐
│      RESPONSE MODEL VALIDATION       │
│         (Pydantic)                   │
│                                      │
│  If response_model defined:         │
│  • Filters fields not in model      │
│  • Validates output types           │
│  • Serializes to JSON               │
│                                      │
│  Extra fields stripped              │
│  Missing required fields → 500      │
└──────────────────┬──────────────────┘
                   │ clean response
                   ▼
┌─────────────────────────────────────┐
│      MIDDLEWARE LAYER (OUT)          │
│                                      │
│  Same middleware runs in reverse:   │
│                                      │
│  Middleware 3 (innermost first)     │
│  └── Middleware 2                   │
│      └── Middleware 1 (outermost)   │
│                                      │
│  Each middleware can:               │
│  • Modify response                  │
│  • Add response headers             │
│  • Log response time                │
│  • Handle errors                    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         UVICORN                      │
│                                      │
│  • Receives response from FastAPI   │
│  • Converts to raw HTTP bytes       │
│  • Sends back to client over TCP    │
└──────────────────┬──────────────────┘
                   │
                   ▼
            CLIENT gets response
```

---

### Middleware — Onion Model

```
REQUEST IN                    RESPONSE OUT
──────────►                  ◄──────────
                                        
  ┌─────────────────────────────────┐   
  │  Middleware 1 (Logging)         │   
  │  ┌─────────────────────────┐   │   
  │  │  Middleware 2 (Auth)    │   │   
  │  │  ┌───────────────────┐  │   │   
  │  │  │  Middleware 3     │  │   │   
  │  │  │  (CORS)           │  │   │   
  │  │  │  ┌─────────────┐  │  │   │   
  │  │  │  │  YOUR ROUTE │  │  │   │   
  │  │  │  │  HANDLER    │  │  │   │   
  │  │  │  └─────────────┘  │  │   │   
  │  │  └───────────────────┘  │   │   
  │  └─────────────────────────┘   │   
  └─────────────────────────────────┘   

Request travels INWARD through layers
Response travels OUTWARD through layers
```

---

### Lifecycle Timing — Real Numbers

```
Total request time breakdown
for a typical AI API endpoint:

Uvicorn parse          ~0.1ms
Middleware (in)        ~1-2ms   (logging, auth check)
Routing                ~0.1ms
Dependency injection   ~1-5ms   (DB session, user lookup)
Pydantic validation    ~0.5ms   (Rust speed)
Your handler           ~200-500ms (DB + LLM calls)
Response model         ~0.5ms
Middleware (out)       ~0.5ms   (add headers, log)
Uvicorn serialize      ~0.1ms
──────────────────────────────
Total                  ~205-515ms

Your handler dominates
Everything else is negligible
```

---

### Exception Handling in Lifecycle

```
Exception raised anywhere
         │
         ├── HTTPException
         │         │
         │         ▼
         │   FastAPI catches it
         │   Returns proper HTTP response
         │   (404, 401, 422 etc)
         │   Middleware OUT still runs
         │
         └── Unhandled Exception
                   │
                   ▼
             FastAPI catches it
             Returns 500 Internal Server Error
             Middleware OUT still runs
             Your exception handler fires
             if registered
```

---

### Code — Seeing the Lifecycle

```python
import time
from fastapi import FastAPI, Request

app = FastAPI()

# Middleware — wraps everything
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    
    # BEFORE handler (request in)
    print(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)  # entire lifecycle runs here
    
    # AFTER handler (response out)
    duration = time.time() - start
    print(f"Completed in {duration:.3f}s")
    response.headers["X-Process-Time"] = str(duration)
    
    return response

# Dependency — runs just before handler
async def get_db():
    db = SessionLocal()
    try:
        yield db        # handler runs here
    finally:
        db.close()      # cleanup after handler

# Handler — your business logic
@app.post("/search", response_model=SearchResponse)
async def search(
    query: SearchRequest,        # validated by Pydantic
    db = Depends(get_db),        # injected dependency
    user = Depends(get_user)     # injected dependency
):
    result = await db.execute()
    return result                # filtered by response_model
```

---

### Follow-up They Might Ask

*"What is the difference between middleware and dependency?"*
> *"Middleware wraps every request regardless of route — good for cross cutting concerns like logging, CORS, auth token extraction. Dependencies are per-route and per-handler — good for route specific logic like DB sessions, user authorization, feature flags."*

*"When does Pydantic validation happen exactly?"*
> *"After routing and dependency injection but before your handler executes. If validation fails, your handler never runs — FastAPI returns 422 immediately with detailed field errors."*

*"Can middleware short circuit the request?"*
> *"Yes — if you return a response without calling call_next(), the request never reaches your handler. Used for things like blocking banned IPs or returning cached responses."*
---
## Q9. How to Run FastAPI in Production?
Running FastAPI in production involves multiple layers — you don't just run uvicorn directly like in development. The standard production setup depends on your deployment target — bare metal/VM, Docker, or Kubernetes.

The core is always Gunicorn as process manager with Uvicorn workers. Gunicorn handles process lifecycle, crash recovery, and graceful restarts while each Uvicorn worker runs its own async event loop serving concurrent requests. In front of that you put Nginx as reverse proxy handling SSL termination, static files, and connection management.

In containerized environments like Docker or Kubernetes, the setup changes slightly — you typically run one Uvicorn process per container and let the orchestrator handle scaling and restarts instead of Gunicorn.

---

### Development vs Production

```
DEVELOPMENT                    PRODUCTION
───────────────                ──────────────────────

uvicorn main:app               Nginx
  --reload                       +
  --port 8000                  Gunicorn
                                 +
Single process                 Uvicorn Workers
Auto reload on                   +
file change                    FastAPI
No SSL
No process mgmt
Not scalable
```

---

### Option 1 — Bare Metal / VM

```
┌─────────────────────────────────────┐
│              NGINX                   │
│                                      │
│  server {                           │
│    listen 443 ssl;                  │
│    server_name myapp.com;           │
│                                      │
│    location / {                     │
│      proxy_pass http://127.0.0.1:8000│
│    }                                │
│  }                                  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│     GUNICORN + UVICORN WORKERS       │
│                                      │
│  gunicorn main:app \                │
│    --workers 4 \                    │
│    --worker-class \                 │
│    uvicorn.workers.UvicornWorker \  │
│    --bind 0.0.0.0:8000 \           │
│    --timeout 120 \                  │
│    --keepalive 5 \                  │
│    --max-requests 1000 \            │
│    --max-requests-jitter 100        │
└─────────────────────────────────────┘
```

---

### Option 2 — Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Production command
CMD ["gunicorn", "main:app",
     "--workers", "4",
     "--worker-class", "uvicorn.workers.UvicornWorker",
     "--bind", "0.0.0.0:8000",
     "--timeout", "120"]
```

```yaml
# docker-compose.yml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    deploy:
      replicas: 3          # 3 containers
      resources:
        limits:
          memory: 512M

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

---

### Option 3 — Kubernetes (Modern Preferred)

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: fastapi
        image: myapp:latest
        command: ["uvicorn"]      # single uvicorn per pod
        args:
          - "main:app"
          - "--host=0.0.0.0"
          - "--port=8000"
          - "--workers=1"         # K8s handles scaling
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:            # K8s health check
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:           # ready to serve traffic?
          httpGet:
            path: /health
            port: 8000

---
# hpa.yaml — auto scaling
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapi-hpa
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70   # scale when CPU > 70%
```

---

### Important Production Config

```python
# main.py — production ready FastAPI

from fastapi import FastAPI
from contextlib import asynccontextmanager

# startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    await db.connect()
    await redis.connect()
    load_ml_models()        # load AI models once at startup
    print("App started")
    
    yield                   # app runs here
    
    # SHUTDOWN
    await db.disconnect()
    await redis.close()
    print("App shutting down")

app = FastAPI(
    title="AI Search API",
    lifespan=lifespan,
    docs_url=None,          # disable swagger in production
    redoc_url=None,         # disable redoc in production
)

# health check endpoint — required for K8s probes
@app.get("/health")
async def health():
    return {"status": "healthy"}
```

---

### Key Production Settings

```bash
# Gunicorn config file — gunicorn.conf.py
workers = 4                    # (2 x CPU) + 1
worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8000"
timeout = 120                  # worker timeout seconds
keepalive = 5                  # keep connection alive
max_requests = 1000            # restart worker after N requests
max_requests_jitter = 100      # add randomness to avoid
                               # all workers restarting together
worker_tmp_dir = "/dev/shm"    # use RAM for temp files, faster
accesslog = "-"                # log to stdout
errorlog = "-"                 # log to stdout
loglevel = "info"
```

---

### Why max_requests Matters

```
Without max_requests:
──────────────────────
Worker runs forever
Memory leaks accumulate
After 10k requests →
worker using 2GB RAM 💀

With max_requests = 1000:
──────────────────────────
Worker handles 1000 requests
Gracefully restarts itself
Fresh memory state
No memory leak buildup ✅

max_requests_jitter = 100:
──────────────────────────
Workers restart at:
  Worker 1 → after 1000-1100 requests
  Worker 2 → after 1000-1100 requests
  Worker 3 → after 1000-1100 requests
  
Staggered → never all restart simultaneously
No traffic spike during restart ✅
```

---

### Deployment Comparison

```
┌──────────────┬───────────┬───────────┬───────────┐
│              │  Bare VM  │  Docker   │    K8s    │
├──────────────┼───────────┼───────────┼───────────┤
│ Scaling      │ Manual    │ Manual    │ Automatic │
│ Recovery     │ Manual    │ Limited   │ Automatic │
│ SSL          │ Nginx     │ Nginx     │ Ingress   │
│ Gunicorn     │ Yes       │ Yes       │ Optional  │
│ Complexity   │ Low       │ Medium    │ High      │
│ Best for     │ Simple    │ Dev/Small │ Production│
│              │ apps      │ teams     │ at scale  │
└──────────────┴───────────┴───────────┴───────────┘
```
---
### Follow-up They Might Ask

*"Why disable Swagger in production?"*
> *"Security — Swagger exposes your entire API surface, parameter types, and sometimes internal field names. In production you don't want attackers having a detailed map of your API. Disable with `docs_url=None`."*

*"What is a liveness vs readiness probe in K8s?"*
> *"Liveness probe checks if the app is alive — if it fails K8s restarts the pod. Readiness probe checks if the app is ready to serve traffic — if it fails K8s removes the pod from load balancer rotation but doesn't restart it. Important distinction for AI apps that need time to load ML models at startup."*

*"How do you do zero downtime deployment?"*
> *"In K8s — rolling updates replace pods gradually, new pod must pass readiness probe before old pod is killed. In bare metal — Gunicorn supports graceful reload with `kill -HUP <pid>` which spawns new workers before killing old ones."*

---
## Q10. Advantages of FastAPI Over Flask for AI/ML Applications

Flask was the default Python API framework for years, but for AI/ML applications specifically FastAPI has significant advantages that make it a much better choice.

The biggest one is async support. AI/ML endpoints are inherently I/O heavy — you're waiting on vector DB queries, LLM API calls, embedding generation, model inference. Flask is synchronous by default — each request blocks the worker until the AI operation completes. FastAPI's async support means one worker can handle hundreds of concurrent AI requests simultaneously while waiting on those I/O operations.

Second is automatic validation through Pydantic. AI endpoints typically have complex request bodies — query text, model parameters, filter conditions, retrieval config. In Flask you manually validate everything with if statements or a separate library. In FastAPI you define a Pydantic model and validation, type coercion, and error responses are completely automatic.

Third is performance. FastAPI with Uvicorn is 2-3x faster than Flask with Gunicorn for I/O heavy workloads — which is exactly what AI applications are.

Fourth is developer experience — auto docs, type safety, editor autocomplete. For AI teams iterating fast on complex APIs this matters a lot.

At CitiusTech the decision was straightforward — our RAG pipeline endpoints needed concurrent handling of vector DB and LLM calls, complex Pydantic models for retrieval config, and fast iteration with auto docs for frontend team integration. Flask simply couldn't meet those requirements without significant extra tooling.

---

### Head to Head Comparison

```
AI/ML ENDPOINT REQUIREMENTS
─────────────────────────────────────────────────

1. Handle concurrent LLM calls        →  ASYNC critical
2. Complex request/response models    →  VALIDATION critical  
3. Fast iteration with auto docs      →  DX critical
4. High throughput                    →  PERFORMANCE critical
5. Type safety for ML parameters      →  TYPE HINTS critical
```

---

### Advantage 1 — Async for AI Workloads

```python
# FLASK — Synchronous
# One request blocks entire worker
@app.route("/search", methods=["POST"])
def search():
    # Each of these BLOCKS the worker
    embedding = embed_model.encode(query)    # 50ms blocked
    results = vector_db.search(embedding)    # 100ms blocked
    response = openai.chat(results)          # 500ms blocked
    return jsonify(response)
    # Total: 650ms, worker doing nothing 90% of time
    # 4 workers = max 4 concurrent requests 😢

# FASTAPI — Asynchronous
# Event loop serves other requests while waiting
@app.post("/search")
async def search(query: SearchRequest):
    # Each await frees event loop for other requests
    embedding = await embed_model.encode(query)    # 50ms free
    results = await vector_db.search(embedding)    # 100ms free
    response = await llm_client.complete(results)  # 500ms free
    return response
    # Total: 650ms but worker serves hundreds concurrently 🚀
```

---

### Advantage 2 — Pydantic for Complex AI Models

```python
# FLASK — Manual validation nightmare
@app.route("/search", methods=["POST"])
def search():
    data = request.json
    
    # Manual validation for every field
    if not data.get("query"):
        return jsonify({"error": "query required"}), 400
    if not isinstance(data.get("top_k", 5), int):
        return jsonify({"error": "top_k must be int"}), 400
    if data.get("threshold", 0.7) < 0 or data.get("threshold", 0.7) > 1:
        return jsonify({"error": "threshold 0-1"}), 400
    # 20 lines of validation for a simple request 😢

# FASTAPI — Automatic validation
class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    filters: Optional[dict] = None
    rerank: bool = False

@app.post("/search")
async def search(request: SearchRequest):
    # Already validated, typed, defaults applied ✅
    # Invalid request → automatic 422 with field details
    pass
```

---

### Advantage 3 — Performance Numbers

```
BENCHMARK — I/O Heavy Workload
(typical AI API — DB + external API calls)

Framework          Requests/sec    Latency p99
──────────────────────────────────────────────
FastAPI+Uvicorn    ~45,000 rps     ~12ms
Flask+Gunicorn     ~15,000 rps     ~35ms
Django+Gunicorn    ~10,000 rps     ~45ms

FastAPI is 3x faster than Flask
for I/O heavy AI workloads

Why?
• Uvicorn (ASGI) vs Gunicorn (WSGI)
• Pydantic v2 (Rust) vs Marshmallow (Python)
• Native async vs sync + threading
```

---

### Advantage 4 — Auto Docs for AI Teams

```
FLASK                           FASTAPI
──────────────────              ──────────────────────
No built-in docs                Auto Swagger at /docs
Must write manually             Auto ReDoc at /redoc
Must maintain separately        Always in sync with code
Extra library needed            Zero extra config
  (Flasgger, Flask-RESTX)
Docs get out of sync            Impossible to be out of sync
  with code

For AI teams:
Frontend team can test          Frontend team can test
LLM endpoints manually          LLM endpoints directly
only after reading docs         in browser via Swagger
```

---

### Advantage 5 — Type Safety for ML

```python
# Type hints make AI code safer and IDE friendly

class RAGConfig(BaseModel):
    # IDE autocompletes these fields
    # Wrong type = caught at request time not runtime
    chunk_size: int = 512
    chunk_overlap: int = 50
    embedding_model: str = "minilm"
    top_k: int = 5
    rerank: bool = True
    llm_model: Literal["gpt-4", "gpt-3.5", "llama3"] = "gpt-4"

# Flask has none of this — plain dicts everywhere
# Typo in field name? Silent bug in production 💀
```

---

### When Flask is Still Fine

```
Use Flask when:                 Use FastAPI when:
──────────────────              ──────────────────────
Simple CRUD app                 AI/ML endpoints
Low concurrency                 High concurrency
Quick prototype                 Production AI system
Team knows Flask well           New project
No complex validation           Complex request models
No AI/ML involved               LLM/vector DB calls
Single developer                Team with frontend
```
---
### Follow-up They Might Ask

*"Can Flask do async?"*
> *"Flask added async support in 2.0 but it's retrofitted — you need to install extra dependencies, it uses threading under the hood not a true event loop, and the ecosystem of async libraries doesn't integrate as cleanly as FastAPI's native async. It's async in name but not in spirit."*

*"Would you ever use Flask over FastAPI today?"*
> *"For quick internal scripts or prototypes where I need an HTTP endpoint fast and don't care about performance or validation — Flask's simplicity is still appealing. But for any production AI system, FastAPI is the clear choice."*

*"What about Django REST Framework for AI APIs?"*
> *"Django is too heavy for AI microservices — it brings ORM, admin, auth, templating, all of which you don't need for an AI API endpoint. FastAPI's minimal footprint is much better suited for focused AI microservices."*

---

## Q11. What is Pydantic? How Does FastAPI Use It?
Pydantic is a Python data validation library that uses type hints to define data schemas and automatically validates, parses, and serializes data against those schemas. It's not FastAPI specific — it's used across the Python ecosystem for config management, data pipelines, and API validation.

Pydantic v2 was completely rewritten in Rust, which makes validation extremely fast — we're talking microsecond level parsing even for complex nested models.

FastAPI uses Pydantic in four specific places. 
**1. for request body validation** — you define a BaseModel and FastAPI automatically validates incoming JSON against it. 

**2. for response serialization** — response_model filters and validates what goes back to the client. 

**3. for settings and config management** using BaseSettings. 

**4. for path and query parameter validation** when you use Field() with constraints.

The key insight is FastAPI doesn't write its own validation logic at all — it completely delegates that responsibility to Pydantic. 
FastAPI's job is routing and dependency injection. 
Pydantic's job is everything data related.


### What Pydantic Does

```
RAW INPUT                    PYDANTIC                    YOUR CODE
(JSON, dict,    ─────────────────────────────►   Clean typed Python
 form data)                                        objects

{                            BaseModel               SearchRequest(
  "query": "hello",  ──►    validates      ──►        query="hello",
  "top_k": "5",             coerces types             top_k=5,
  "threshold": 0.8          applies defaults           threshold=0.8,
}                           checks constraints          filters=None
                            raises errors             )
                            if invalid
```

---

### Pydantic v1 vs v2 Internally

```
PYDANTIC V1                    PYDANTIC V2
────────────────               ──────────────────────
Pure Python                    Core rewritten in Rust
~5-50x slower                  Microsecond validation
.dict()                        .model_dump()
.json()                        .model_dump_json()
@validator                     @field_validator
@root_validator                @model_validator
schema()                       model_json_schema()

FastAPI uses Pydantic v2
from FastAPI 0.100.0+
```

---

### How FastAPI Uses Pydantic — 4 Places

---

#### Place 1 — Request Body Validation

```python
from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str                                    # required
    top_k: int = Field(default=5, ge=1, le=20)   # optional, validated
    threshold: float = Field(default=0.7, ge=0, le=1)
    filters: Optional[dict] = None

@app.post("/search")
async def search(request: SearchRequest):
    # FastAPI sees SearchRequest in signature
    # Reads incoming JSON
    # Passes to Pydantic for validation
    # If valid → SearchRequest object handed to handler
    # If invalid → 422 returned, handler never runs
    pass

# Valid request:
# {"query": "hello", "top_k": 10}
# → SearchRequest(query="hello", top_k=10,
#                 threshold=0.7, filters=None) ✅

# Invalid request:
# {"top_k": 10}
# → 422: query field required ❌

# Type coercion:
# {"query": "hello", "top_k": "5"}
# → top_k coerced from "5" to 5 ✅
# Pydantic is lenient about string→int
```

---

#### Place 2 — Response Model

```python
class UserDB(BaseModel):
    id: int
    name: str
    email: str
    password_hash: str      # sensitive field
    internal_score: float   # internal field

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    # no password_hash
    # no internal_score

@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int):
    user = await db.get_user(id)
    return user
    # Even though user has password_hash and internal_score
    # Pydantic filters them out via response_model
    # Client only sees id, name, email ✅
    # Security through response_model ✅
```

---

#### Place 3 — Settings and Config

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str              # required
    redis_url: str                 # required
    openai_api_key: str            # required
    llm_model: str = "gpt-4"      # optional with default
    max_tokens: int = 1000
    debug: bool = False

    class Config:
        env_file = ".env"          # reads from .env file

# Pydantic reads from environment variables automatically
# DATABASE_URL=postgresql://... → settings.database_url
# Type validation on env vars too
# Missing required var → error at startup not runtime

settings = Settings()             # fails fast if config wrong
```

---

#### Place 4 — Query and Path Validation

```python
from fastapi import Query, Path
from pydantic import Field

@app.get("/search")
async def search(
    # Query uses Pydantic Field internally
    query: str = Query(..., min_length=3, max_length=100),
    top_k: int = Query(default=5, ge=1, le=20),
):
    pass

# Same Pydantic validation engine
# Just applied to query params instead of body
```

---

### Pydantic Validation Flow Internally

```
Incoming JSON
      │
      ▼
FastAPI extracts body
      │
      ▼
Calls Pydantic:
SearchRequest.model_validate(data)
      │
      ├── Field exists?          No  → ValidationError
      │                               (field required)
      ├── Type matches?          No  → Try coercion
      │     │                         Still fails → ValidationError
      │     └── Coercion works?  Yes → use coerced value
      ├── Constraints pass?      No  → ValidationError
      │   (ge, le, min_length)        (value too small etc)
      ├── Validators pass?       No  → ValidationError
      │   (@field_validator)          (custom message)
      └── All pass?              Yes → SearchRequest object ✅

ValidationError
      │
      ▼
FastAPI catches it automatically
Returns 422 Unprocessable Entity:
{
  "detail": [
    {
      "loc": ["body", "top_k"],
      "msg": "Input should be greater than or equal to 1",
      "type": "greater_than_equal"
    }
  ]
}
```
---
### Follow-up They Might Ask

*"What is the difference between Pydantic BaseModel and dataclasses?"*
> *"Python dataclasses provide structure but no validation — wrong types are silently accepted. Pydantic BaseModel validates types, coerces where possible, and raises errors on invalid data. Also Pydantic has JSON serialization, schema generation, and nested model support built in — dataclasses have none of that."*

*"What is model_validate vs direct instantiation?"*
> *"Both validate. Direct instantiation `SearchRequest(query="hello")` is for creating models in code. `model_validate(dict)` is for parsing external data like JSON from requests. FastAPI uses model_validate internally when parsing request bodies."*

*"Can Pydantic validate after model creation?"*
> *"By default Pydantic v2 models are immutable after creation. You can allow mutation with `model_config = ConfigDict(validate_assignment=True)` which re-runs validation when you set a field value."*


> *"@field_validator validates one field in isolation. @model_validator(mode='after') runs after all fields are validated and gives you the complete model object — use it when validation logic spans multiple fields like requiring field B when field A is True."*
---


12. What is a Pydantic `BaseModel`? How do you define one?
13. How do you add field validation in Pydantic? (`Field`, `validator`, `model_validator`)
14. What is the difference between Pydantic v1 and v2? (FastAPI uses v2 now)
15. How do you handle optional fields in Pydantic?
16. What is `model_dump()` vs `dict()` in Pydantic v2?
17. How do you validate nested models in Pydantic?
18. What is `response_model` in FastAPI? Why is it important?

All of these questions are covered above.

---

## Q19. What is dependency injection in FastAPI?

Dependency Injection (DI) is a design pattern where a component declares *what it needs*, and a framework automatically provides (injects) those needs at runtime — rather than the component creating them itself.

In FastAPI, the DI system is built into the framework. You declare dependencies as function parameters using `Depends()`, and FastAPI resolves, calls, and injects them before your route handler runs. This lets you cleanly separate concerns like auth, DB sessions, config, and validation.

Why it matters:
- Avoids code duplication across routes
- Makes logic testable (you can override dependencies in tests)
- Centralizes cross-cutting concerns (auth, logging, rate limiting)

---

## Q20. How does `Depends()` work?

`Depends(callable)` wraps any callable — a function, async function, or class — and tells FastAPI: *"Call this first, and inject its return value into my parameter."*

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_query_params(q: str = "default", limit: int = 10):
    return {"q": q, "limit": limit}

@app.get("/search")
def search(params: dict = Depends(get_query_params)):
    return params
```

When `GET /search?q=python&limit=5` is called:
1. FastAPI sees `Depends(get_query_params)`
2. It calls `get_query_params(q="python", limit=5)` — resolving its own params from the request
3. The return value `{"q": "python", "limit": 5}` is injected into `params`
4. Your route handler runs with `params` already populated

`Depends` also supports `yield`-based dependencies (for resource lifecycle), class instances, and async functions.

---

## Q21. Sharing a DB session across a request using `Depends`

The classic pattern. You use a `yield`-based dependency so the session is created before the route and cleaned up after — even if an exception occurs.

```python
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()   # open session
    try:
        yield db          # inject into route
    finally:
        db.close()        # always runs, even on error

@app.get("/users/{id}")
def get_user(id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).first()
```

Key points:
- `yield` makes it a *context manager dependency* — code after `yield` is teardown
- The session is opened once per request and shared across all dependencies that declare `Depends(get_db)` in the same request (due to caching — covered in Q23)
- FastAPI guarantees the `finally` block runs regardless of success or exception

---

## Q22. Function vs Class dependencies

**Function dependency** — a plain function (sync or async). Stateless, lightweight.

```python
def verify_token(token: str = Header(...)):
    if token != "secret":
        raise HTTPException(401)
    return token
```

**Class dependency** — a class whose `__init__` receives parameters. Use this when you need *configurable*, stateful, or reusable logic with shared setup.

```python
class Paginator:
    def __init__(self, page: int = 1, size: int = 10):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size

@app.get("/items")
def list_items(p: Paginator = Depends(Paginator)):
    return {"offset": p.offset, "size": p.size}
```

FastAPI calls `Paginator(page=..., size=...)` automatically — the class instance is the injected value. You're passing the *class itself* to `Depends()`, not an instance. This is sometimes called a *callable class dependency*.

Use class dependencies when:
- You need configurable behavior (pass constructor args)
- You want to group related query params as a reusable schema
- You need to share state within a single dependency resolution

---

## Q23. Dependency caching — the `use_cache` parameter

By default, FastAPI caches dependency results within a single request. If multiple places in the same request declare `Depends(get_db)`, the dependency is called **once** and the same result is reused.

```python
# Both use the SAME db session — get_db() called once per request
@app.get("/data")
def endpoint(
    db1: Session = Depends(get_db),
    db2: Session = Depends(get_db),   # same object as db1
):
    assert db1 is db2  # True
```

To **disable** caching and force a fresh call every time:

```python
def endpoint(
    db: Session = Depends(get_db, use_cache=False)
):
    ...
```

When to disable caching:
- The dependency has side effects you want repeated (e.g. timestamps, nonces)
- You genuinely need two independent DB transactions in one request
- Testing scenarios where isolation matters

Default `use_cache=True` is almost always what you want — it prevents redundant DB connections and ensures transactional consistency within a request.

---

## Q24. Reusable auth dependency

The standard pattern for JWT/Bearer token auth across protected routes:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate")

# Protect any route — just add it as a dependency
@app.get("/profile")
def profile(user_id: str = Depends(get_current_user)):
    return {"user": user_id}

@app.delete("/account")
def delete_account(user_id: str = Depends(get_current_user)):
    ...
```

For role-based access, you can make it a factory:

```python
def require_role(role: str):
    def checker(user=Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(403)
        return user
    return checker

@app.delete("/admin/users/{id}")
def admin_delete(user=Depends(require_role("admin"))):
    ...
```
---
## Q25. Can dependencies have dependencies? How does FastAPI resolve them?

Yes — and this is one of FastAPI's most powerful features. Dependencies can declare their own `Depends()`, forming a **dependency graph** that FastAPI resolves automatically using a topological sort.

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db)):
    # uses the db to fetch user from token
    token = ...
    return db.query(User).filter(...).first()

def get_admin_user(user: User = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403)
    return user

@app.delete("/admin/data")
def delete_data(admin=Depends(get_admin_user)):
    ...
```

Resolution order for this route:
1. `get_db()` — called first (deepest dependency)
2. `get_current_user(db=...)` — gets the db session
3. `get_admin_user(user=...)` — gets the user
4. Route handler runs with `admin`

FastAPI builds the entire graph, resolves it in dependency order, applies caching (same dependency = one call), and handles teardown in reverse order after the response.

---

Now let me show you this visually:
![alt text](image-2.png)

Now the dependency graph with caching — showing how `get_db` is only called once even though two things need it:

![alt text](image-1.png)

And finally the auth dependency chain — the most common real-world pattern you'll be asked about in interviews:---

![alt text](image.png)

The key interview insight: **dependency caching is scoped to a single request**. Across requests, each gets its own fresh resolution. Within a request, the same `Depends(x)` is evaluated once. That's how you safely share a DB session without accidentally sharing state between users.
---

## Q32. How to Connect FastAPI to PostgreSQL Using SQLAlchemy?
Connecting FastAPI to PostgreSQL involves three things — 
**1. creating the engine** which is the connection pool, 
**2. defining a session factory for per-request DB sessions**, and 
**3. using dependency injection to provide sessions to route handlers**.

The engine manages a pool of actual TCP connections to PostgreSQL — you don't create a new connection per request, you borrow one from the pool and return it when done. SQLAlchemy handles this automatically.

### Complete Setup

```
PROJECT STRUCTURE
─────────────────
app/
├── database.py      ← engine + session factory
├── models.py        ← SQLAlchemy table models
├── schemas.py       ← Pydantic models
├── dependencies.py  ← get_db dependency
└── main.py          ← FastAPI app
```

```python
# database.py
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.orm import DeclarativeBase

# ── Engine — connection pool ──
# postgresql+asyncpg = async PostgreSQL driver
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    pool_size=10,          # max persistent connections
    max_overflow=20,       # extra connections under load
    pool_timeout=30,       # wait this long for free connection
    pool_recycle=1800,     # recycle connections every 30 mins
    echo=False             # True = log all SQL (dev only)
)

# ── Session Factory ──
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False  # don't expire objects after commit
)

# ── Base class for all models ──
class Base(DeclarativeBase):
    pass
```

```python
# models.py
from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .database import Base

class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(String)
    embedding_id: Mapped[str] = mapped_column(
        String(100), unique=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
```

```python
# dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session          # handler runs here
            await session.commit() # commit if no exception
        except Exception:
            await session.rollback() # rollback on error
            raise
```

```python
# main.py
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .dependencies import get_db
from .models import Document

app = FastAPI()

@app.get("/documents/{doc_id}")
async def get_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Document).where(Document.id == doc_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404)
    return doc
```

---

### Connection Pool Visual

```
FastAPI App
    │
    │ request comes in
    ▼
get_db() dependency
    │
    │ borrows connection
    ▼
┌─────────────────────────────────┐
│      CONNECTION POOL             │
│                                  │
│  conn1 ● (in use)               │
│  conn2 ● (in use)               │
│  conn3 ○ (free) ◄── borrowed    │
│  conn4 ○ (free)                 │
│  conn5 ○ (free)                 │
│                                  │
│  pool_size=10                   │
│  max_overflow=20                │
│  (up to 30 total under load)    │
└──────────────┬──────────────────┘
               │ TCP connection
               ▼
         PostgreSQL
```

---

## Q33. Sync vs Async SQLAlchemy in FastAPI

This is one of the most important architectural decisions in a FastAPI app. Sync SQLAlchemy blocks the thread — when you execute a query, that thread sits idle waiting for PostgreSQL to respond. In FastAPI's async architecture this is catastrophic because you're blocking the event loop, freezing all other requests.

Async SQLAlchemy using asyncpg driver sends the query and awaits the response — the event loop is free to serve other requests while PostgreSQL processes the query. For an AI platform making frequent DB calls this is the difference between handling 100 concurrent requests and 10,000.

---

### The Core Difference

```
SYNC SQLAlchemy                ASYNC SQLAlchemy
───────────────────            ──────────────────────

from sqlalchemy import         from sqlalchemy.ext.asyncio
  create_engine                  import create_async_engine

engine = create_engine(        engine = create_async_engine(
  "postgresql://..."             "postgresql+asyncpg://..."
)                              )

Session = sessionmaker(        AsyncSession = async_sessionmaker(
  bind=engine                    bind=engine
)                              )

# route handler               # route handler
def get_docs(                  async def get_docs(
  db: Session                    db: AsyncSession
    = Depends(get_db)              = Depends(get_db)
):                             ):
  # BLOCKS event loop            # frees event loop
  docs = db.execute(             docs = await db.execute(
    select(Document)               select(Document)
  )                              )
  return docs                    return docs
```

---

### Performance Impact

```
SYNC under 100 concurrent requests:
─────────────────────────────────────
Each request hits DB query (100ms)
Event loop BLOCKED for 100ms per request
Requests queue up
Response time degrades exponentially

100 requests × 100ms = 10 seconds total 💀

ASYNC under 100 concurrent requests:
─────────────────────────────────────
All 100 requests fire DB queries
Event loop FREE during all 100ms waits
All queries run concurrently in PostgreSQL
All responses return ~100ms

100 requests ≈ 100ms total 🚀
```

---

### Driver Comparison

```
┌──────────────┬─────────────┬──────────────────────────┐
│ Driver       │ Sync/Async  │ Use with                 │
├──────────────┼─────────────┼──────────────────────────┤
│ psycopg2     │ Sync        │ Flask, Django, sync apps │
│ psycopg3     │ Both        │ Modern apps              │
│ asyncpg      │ Async only  │ FastAPI async (fastest)  │
│ aiopg        │ Async       │ Older async apps         │
└──────────────┴─────────────┴──────────────────────────┘

```

---

## Q34. How to Manage DB Sessions in FastAPI?

The standard pattern is per-request session — one DB session created when request starts, used throughout the request lifecycle, committed or rolled back when request ends, then closed. This is implemented as a FastAPI dependency using yield.

The key insight is the yield dependency acts like a context manager — code before yield is setup, your handler runs at yield, code after yield is teardown. This guarantees the session is always closed even if the handler raises an exception."*

---

### Per-Request Session Pattern

```
REQUEST LIFECYCLE WITH DB SESSION
───────────────────────────────────

HTTP Request arrives
        │
        ▼
get_db() dependency starts
        │
        ▼
Session created from pool
        │
        ▼
    yield session ──────────────────┐
        │                           │
        │                    Handler executes
        │                    uses session
        │                    for DB operations
        │                           │
        ◄───────────────────────────┘
        │
        ▼
Success? → commit()
Error?   → rollback()
        │
        ▼
Session closed → connection returned to pool
        │
        ▼
HTTP Response sent
```

```python
# dependencies.py — three patterns

# ── Pattern 1: Basic (most common) ──
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        # session.close() called automatically
        # by async context manager

# ── Pattern 2: Read only session ──
async def get_read_db():
    async with AsyncSessionLocal() as session:
        yield session
        # no commit needed for read only
        # saves a round trip to PostgreSQL

# ── Pattern 3: Transaction control in handler ──
async def get_db_no_autocommit():
    async with AsyncSessionLocal() as session:
        yield session
        # handler controls commit/rollback
        # useful for complex multi-step transactions

# Usage in handler:
@app.post("/documents")
async def create_document(
    doc: DocumentCreate,
    db: AsyncSession = Depends(get_db)
):
    new_doc = Document(**doc.model_dump())
    db.add(new_doc)
    # commit happens automatically in get_db()
    return new_doc
```

---

### Common Session Mistakes

```python
# ❌ WRONG — session created outside dependency
# shared across requests — race conditions!
db = AsyncSessionLocal()

@app.get("/docs")
async def get_docs():
    return await db.execute(select(Document))

# ❌ WRONG — session not closed on error
async def get_db():
    session = AsyncSessionLocal()
    yield session
    await session.close()  # never runs if handler raises!

# ✅ CORRECT — async context manager guarantees cleanup
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

## Q35. What is Alembic? How Do You Run Migrations?

Alembic is the database migration tool for SQLAlchemy. When your data models change — new table, new column, changed type — you need to apply those changes to your production database without losing existing data. That's what Alembic does.

It works by tracking a version history of your schema changes in a special table called alembic_version in your database. Each migration is a Python file with upgrade() and downgrade() functions — upgrade applies the change, downgrade reverts it.

In production you never run raw ALTER TABLE SQL manually — you create Alembic migrations, test them in staging, then apply in production.

---

### Alembic Flow

```
Your SQLAlchemy Model Changes
          │
          ▼
alembic revision --autogenerate
          │
          │ Alembic compares:
          │ current models vs database schema
          │ generates migration file automatically
          ▼
migrations/versions/abc123_add_score_column.py
          │
          ▼
alembic upgrade head
          │
          │ applies migration to database
          ▼
Database schema updated ✅
alembic_version table updated ✅
```

```python
# migrations/versions/abc123_add_score_column.py
# Auto-generated by Alembic

from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'   # previous migration

def upgrade():
    # add new column to documents table
    op.add_column(
        'documents',
        sa.Column('score', sa.Float(), nullable=True)
    )
    # add index
    op.create_index(
        'ix_documents_score',
        'documents',
        ['score']
    )

def downgrade():
    # reverse the change
    op.drop_index('ix_documents_score')
    op.drop_column('documents', 'score')
```

```bash
# Common Alembic commands

# Initial setup
alembic init alembic

# Generate migration from model changes
alembic revision --autogenerate -m "add score column"

# Apply all pending migrations
alembic upgrade head

# Apply one migration forward
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# See current version
alembic current

# See migration history
alembic history
```

---

### Migration Version Chain

```
Database alembic_version table:
─────────────────────────────────
current: f3a9b2

Migration chain:
base
 │
 ▼
a1b2c3 ← "create documents table"
 │
 ▼
d4e5f6 ← "add embedding_id column"
 │
 ▼
f3a9b2 ← "add score column" (current)
 │
 ▼
new_migration ← pending, not applied yet

alembic upgrade head → applies new_migration
alembic downgrade -1 → reverts to f3a9b2
```

---

## Q36. How to Connect FastAPI to MongoDB?

For MongoDB in FastAPI you use Motor — the official async MongoDB driver for Python. Motor is built on top of PyMongo but fully async, so it integrates naturally with FastAPI's event loop without blocking.

The pattern is similar to SQLAlchemy — create a client at startup, close it at shutdown, inject database reference via dependency. Unlike SQLAlchemy there's no ORM or session concept — you work directly with collections and documents.

---

### Complete Setup

```python
# database.py — Motor setup
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import FastAPI

# ── Client lifecycle with lifespan ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — create client once
    app.mongodb_client = AsyncIOMotorClient(
        "mongodb://localhost:27017",
        maxPoolSize=10,
        minPoolSize=2
    )
    app.mongodb = app.mongodb_client["ai_platform"]
    print("MongoDB connected")

    yield

    # SHUTDOWN — close client
    app.mongodb_client.close()
    print("MongoDB disconnected")

app = FastAPI(lifespan=lifespan)

# ── Dependency ──
async def get_db(request: Request):
    return request.app.mongodb
```

```python
# CRUD operations with Motor
from fastapi import APIRouter, Depends
from bson import ObjectId

router = APIRouter()

# ── Create ──
@router.post("/documents")
async def create_document(
    doc: DocumentCreate,
    db = Depends(get_db)
):
    result = await db["documents"].insert_one(
        doc.model_dump()
    )
    return {"id": str(result.inserted_id)}

# ── Read ──
@router.get("/documents/{doc_id}")
async def get_document(
    doc_id: str,
    db = Depends(get_db)
):
    doc = await db["documents"].find_one(
        {"_id": ObjectId(doc_id)}
    )
    if not doc:
        raise HTTPException(status_code=404)
    doc["id"] = str(doc.pop("_id"))  # convert ObjectId
    return doc

# ── Search with filter ──
@router.get("/documents")
async def search_documents(
    query: str,
    limit: int = 10,
    db = Depends(get_db)
):
    cursor = db["documents"].find(
        {"$text": {"$search": query}}
    ).limit(limit)

    docs = await cursor.to_list(length=limit)
    return docs
```

---

### SQLAlchemy vs Motor

```
┌─────────────────┬──────────────────┬──────────────────┐
│                 │   SQLAlchemy     │     Motor        │
├─────────────────┼──────────────────┼──────────────────┤
│ Database        │ PostgreSQL/MySQL │ MongoDB          │
│ Data model      │ ORM (classes)    │ Raw dicts/docs   │
│ Schema          │ Strict           │ Flexible         │
│ Sessions        │ Yes              │ No               │
│ Transactions    │ Full ACID        │ Limited          │
│ Migrations      │ Alembic          │ Manual/scripts   │
│ Query language  │ SQLAlchemy ORM   │ MongoDB query    │
│ Best for        │ Structured data  │ Flexible/nested  │
└─────────────────┴──────────────────┴──────────────────┘
```

---

## Q37. How to Implement Pagination in FastAPI?

Pagination is essential for any endpoint returning lists — you never return all records at once. 
There are two main approaches — offset pagination which is simple but has performance issues at scale, and cursor based pagination which is efficient even for millions of records.

Offset pagination uses LIMIT and OFFSET in SQL — skip N records, take M. Simple to implement but slow for large offsets because PostgreSQL still scans all skipped rows. Cursor pagination uses a pointer to the last seen record — much faster for deep pages.

---

### Offset Pagination

```python
from fastapi import Query
from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar("T")

# ── Reusable pagination response ──
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

# ── Reusable pagination params ──
class PaginationParams:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

@app.get("/documents", response_model=PaginatedResponse[DocumentOut])
async def list_documents(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # ── Count total ──
    count_result = await db.execute(
        select(func.count(Document.id))
    )
    total = count_result.scalar()

    # ── Fetch page ──
    result = await db.execute(
        select(Document)
        .offset(pagination.offset)
        .limit(pagination.page_size)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return PaginatedResponse(
        items=documents,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=ceil(total / pagination.page_size),
        has_next=pagination.page * pagination.page_size < total,
        has_previous=pagination.page > 1
    )

# URL: /documents?page=2&page_size=20
```

---

### Cursor Pagination — For Scale

```python
# More efficient for large datasets
# Uses last seen ID as cursor instead of offset

@app.get("/documents/stream")
async def list_documents_cursor(
    cursor: Optional[int] = Query(default=None),
    limit: int = Query(default=20, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Document).order_by(Document.id.asc())

    if cursor:
        # start AFTER the cursor ID
        query = query.where(Document.id > cursor)

    query = query.limit(limit + 1)  # fetch one extra
    result = await db.execute(query)
    docs = result.scalars().all()

    # check if there's a next page
    has_next = len(docs) > limit
    if has_next:
        docs = docs[:limit]  # remove the extra one

    next_cursor = docs[-1].id if has_next else None

    return {
        "items": docs,
        "next_cursor": next_cursor,
        "has_next": has_next
    }

# First page:  /documents/stream
# Next page:   /documents/stream?cursor=20
# Next page:   /documents/stream?cursor=40
```

---

### Offset vs Cursor

```
┌─────────────────┬──────────────────┬──────────────────┐
│                 │ Offset Pagination│ Cursor Pagination│
├─────────────────┼──────────────────┼──────────────────┤
│ Implementation  │ Simple           │ Moderate         │
│ Performance     │ Slow at depth    │ Fast always      │
│ Deep pages      │ O(offset+limit)  │ O(limit)         │
│ Random access   │ ✅ any page      │ ❌ sequential    │
│ New items issue │ Items can shift  │ Stable           │
│ Best for        │ Admin panels     │ Feeds, APIs      │
│                 │ Small datasets   │ Large datasets   │
└─────────────────┴──────────────────┴──────────────────┘
```

---

## Q38. What is the N+1 Problem? How to Avoid It?

N+1 is one of the most common and damaging performance bugs in ORM-based applications. 
It happens when you fetch a list of N records and then make an additional query for each record to fetch related data — resulting in 1 query for the list plus N queries for the relations, total N+1 queries.

For example fetch 100 documents and their authors — naively that's 101 queries. With eager loading using `joinedload` or `selectinload` it's 1 or 2 queries total. At scale N+1 can turn a 10ms endpoint into a 10 second one.

---

### N+1 Visualized

```
# Documents table          # Authors table
# ───────────────          # ──────────────
# id | title               # id | name
# 1  | "RAG intro"         # 1  | "Raj"
# 2  | "FastAPI guide"     # 2  | "Priya"
# 3  | "Python tips"       # 3  | "Amit"

# ❌ N+1 Problem
───────────────────────────────────────────

Query 1: SELECT * FROM documents
# returns 3 documents

Query 2: SELECT * FROM authors WHERE id=1  ← for doc 1
Query 3: SELECT * FROM authors WHERE id=2  ← for doc 2
Query 4: SELECT * FROM authors WHERE id=3  ← for doc 3

Total: 4 queries for 3 documents 💀
For 1000 documents = 1001 queries 💀💀💀
```

---

### Solutions

```python
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import select

# ── Solution 1: joinedload (SQL JOIN) ──
# Best for many-to-one (document → author)
# Single query with JOIN

result = await db.execute(
    select(Document)
    .options(joinedload(Document.author))
    # SELECT documents.*, authors.*
    # FROM documents
    # LEFT JOIN authors ON documents.author_id = authors.id
)
docs = result.unique().scalars().all()
# 1 query total ✅


# ── Solution 2: selectinload (IN clause) ──
# Best for one-to-many (author → documents)
# 2 queries but avoids JOIN duplication

result = await db.execute(
    select(Author)
    .options(selectinload(Author.documents))
    # Query 1: SELECT * FROM authors
    # Query 2: SELECT * FROM documents
    #          WHERE author_id IN (1, 2, 3)
)
authors = result.scalars().all()
# 2 queries total ✅ much better than N+1


# ── Solution 3: Explicit JOIN for filtering ──
result = await db.execute(
    select(Document, Author)
    .join(Author, Document.author_id == Author.id)
    .where(Author.name == "Raj")
)


# ── Solution 4: contains_eager ──
# When you write the JOIN yourself
from sqlalchemy.orm import contains_eager

result = await db.execute(
    select(Document)
    .join(Document.author)
    .options(contains_eager(Document.author))
    .where(Author.active == True)
)
```

---

### Detecting N+1

```python
# Development — enable SQL logging
engine = create_async_engine(
    DATABASE_URL,
    echo=True  # logs every SQL query
)

# What you see with N+1:
# INFO: SELECT * FROM documents
# INFO: SELECT * FROM authors WHERE id=1
# INFO: SELECT * FROM authors WHERE id=2
# ... 100 more lines 💀

# What you see with eager loading:
# INFO: SELECT documents.*, authors.*
#       FROM documents
#       LEFT JOIN authors... ✅
```

---

### Quick Decision Guide

```
What relationship?
        │
        ├── Many-to-one (doc → author)
        │   One foreign key on your table
        │           │
        │           ▼
        │       joinedload ✅
        │
        ├── One-to-many (author → docs)
        │   Many records on other table
        │           │
        │           ▼
        │       selectinload ✅
        │       (avoids row duplication)
        │
        └── Need to filter by relation?
                    │
                    ▼
                explicit join ✅
```

---
## 🔴 AUTHENTICATION & SECURITY (26–31)

26. How do you implement JWT authentication in FastAPI?
27. What is OAuth2PasswordBearer? How does it work?
28. How do you implement role-based access control (RBAC) in FastAPI?
29. How do you secure FastAPI endpoints? (API keys, JWT, OAuth2)
30. How do you handle CORS in FastAPI?
31. What is `HTTPException`? How do you raise custom errors?

---
Let me build this entire guide now — complete theory + diagrams across all 6 questions.

---

## Q26. JWT Authentication in FastAPI

JWT (JSON Web Token) is a self-contained token: all claims are encoded inside it, so the server doesn't need a database lookup to validate it — just a signature check.

A JWT has 3 parts:
 **Header** (algorithm) · **Payload** (claims: `sub`, `exp`, `role`) · **Signature** (HMAC of header+payload using your secret key).

The full flow:
1. User `POST /auth/token` with username + password(login)
2. Server verifies credentials, creates JWT signed with `SECRET_KEY`
3. Client stores token, sends it as `Authorization: Bearer <token>` on every request
4. Server decodes + verifies signature on each protected route — no DB hit needed

```python
# pip install python-jose[cryptography] passlib[bcrypt]
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"])

def create_access_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not pwd_context.verify(form.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
```

---

## Q27. What is OAuth2PasswordBearer?

`OAuth2PasswordBearer` is a FastAPI utility that implements the OAuth2 "password flow" — it tells FastAPI: *"extract the Bearer token from the `Authorization` header of this request."*

It does two things:
- **Extraction** — pulls the raw token string from `Authorization: Bearer <token>`
- **OpenAPI docs** — marks the endpoint as requiring Bearer auth in the Swagger UI (adds the "Authorize" button)

It does **not** validate the token — that's your job inside `get_current_user`.

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
# tokenUrl is only used for the Swagger UI "Authorize" button

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token payload")
        return db.query(User).filter(User.id == user_id).first()
    except JWTError:
        raise HTTPException(401, "Token validation failed")
```

If no `Authorization` header is present, `OAuth2PasswordBearer` automatically raises a `401`(Unauthorized) before your code even runs.

---

## Q28. Role-Based Access Control (RBAC)

RBAC restricts routes based on what role a user has (`admin`, `editor`, `viewer`). The cleanest FastAPI pattern is a **dependency factory** — a function that *returns* a dependency:

```python
def require_role(*roles: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(403, f"Requires one of: {roles}")
        return user
    return checker

# Usage — clean and declarative
@app.get("/admin/dashboard")
def admin_dashboard(user = Depends(require_role("admin"))):
    return {"user": user.email}

@app.put("/content/{id}")
def edit_content(id: int, user = Depends(require_role("admin", "editor"))):
    ...

@app.get("/reports")
def view_reports(user = Depends(require_role("admin", "editor", "viewer"))):
    ...
```

For more complex RBAC (permission-based, not just role-based), store permissions in the JWT payload and check them:

```python
def require_permission(permission: str):
    def checker(user: User = Depends(get_current_user)):
        if permission not in user.permissions:  # e.g. ["read:reports", "write:content"]
            raise HTTPException(403, "Insufficient permissions")
        return user
    return checker
```

---

## Q29. Securing FastAPI endpoints

Three main strategies, often layered together:

**API Key** — simplest, for machine-to-machine:

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Depends(api_key_header)):
    if key != settings.API_KEY:
        raise HTTPException(403, "Invalid API key")
    return key
```

**JWT** — covered above — for user-facing auth with expiry and claims.

**OAuth2 (third-party)** — for "Login with Google/GitHub". Use `authlib` or `python-social-auth` — outside FastAPI's built-in scope.

**Layering strategies** — you can combine them:

```python
# Require BOTH a valid JWT AND a specific role
@app.delete("/admin/users/{id}")
def delete_user(
    user = Depends(require_role("admin")),  # checks JWT + role
    _key = Depends(verify_api_key),         # also checks API key
):
    ...
```

---

## Q30. CORS in FastAPI

CORS (Cross-Origin Resource Sharing) is a browser security mechanism. When your React frontend at `https://app.example.com` calls your API at `https://api.example.com`, the browser sends a preflight `OPTIONS` request to check if the server allows it. Without CORS headers, the browser blocks the response.

FastAPI uses Starlette's `CORSMiddleware`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # NEVER use ["*"] in production with credentials
    allow_credentials=True,   # allows cookies / Authorization headers
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

Key rules:
- `allow_origins=["*"]` + `allow_credentials=True` is **invalid** — browsers reject it. You must list explicit origins when using credentials.
- For development: `allow_origins=["http://localhost:3000"]`
- CORS is a **browser** restriction only. Postman, curl, and server-to-server calls ignore it entirely.

---

## Q31. HTTPException and custom errors

`HTTPException` is FastAPI's standard way to return error responses with a proper HTTP status code:

```python
from fastapi import HTTPException

@app.get("/users/{id}")
def get_user(id: int, db = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

**Custom exception handlers** — for app-wide consistent error responses:

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}}
    )

# Usage
raise AppException(404, "USER_NOT_FOUND", "No user with that ID exists")
# → {"error": {"code": "USER_NOT_FOUND", "message": "No user with that ID exists"}}
```

**Override the default 422 validation error** (Pydantic parse errors):
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "VALIDATION_ERROR", "fields": exc.errors()}}
    )
```

---

First, the full JWT flow end-to-end:
Now the diagrams. 

![alt text](image-3.png)

![alt text](image-4.png)


Now the RBAC dependency factory pattern — how roles map to routes:
![alt text](image-5.png)


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
