# Web Servers, Application Servers & Production Architecture

A comprehensive guide to understanding web servers, application servers, and how to build scalable production systems.

---

## Table of Contents

1. [Web Servers](#web-servers)
2. [Application Servers](#application-servers)
3. [Protocols: WSGI, ASGI, Servlet, CGI](#protocols)
4. [Complete Production Architecture](#complete-production-architecture)
5. [Scaling Strategies](#scaling-strategies)
6. [Handling Millions of Requests](#handling-millions-of-requests)
7. [Load Balancing](#load-balancing)
8. [Caching Layer](#caching-layer)
9. [Kubernetes Scaling](#kubernetes-scaling)
10. [Real-World Architecture Examples](#real-world-architecture-examples)
11. [Interview Tips](#interview-tips)

---

# Web Servers

A **web server** is software that handles HTTP/HTTPS requests from clients and returns responses. It's optimized for handling many concurrent connections and serving static content efficiently.

**Simple definition:** A program that listens on port 80/443 and responds to HTTP requests.

## What Web Servers Do

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WEB SERVER RESPONSIBILITIES                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. ACCEPT CONNECTIONS                                                     │
│      • Handle 10,000+ concurrent connections efficiently                   │
│      • Keep-alive connections                                              │
│      • Connection pooling                                                  │
│                                                                             │
│   2. SERVE STATIC FILES                                                     │
│      • HTML, CSS, JavaScript                                               │
│      • Images, videos, fonts                                               │
│      • Extremely fast (direct file system access)                          │
│                                                                             │
│   3. SSL/TLS TERMINATION                                                    │
│      • Decrypt HTTPS traffic                                               │
│      • Handle certificates                                                 │
│      • Offload encryption from app servers                                 │
│                                                                             │
│   4. REVERSE PROXY                                                          │
│      • Forward requests to application servers                             │
│      • Hide internal architecture                                          │
│      • Add headers (X-Real-IP, X-Forwarded-For)                           │
│                                                                             │
│   5. LOAD BALANCING                                                         │
│      • Distribute requests across multiple servers                         │
│      • Health checks                                                       │
│      • Failover                                                            │
│                                                                             │
│   6. COMPRESSION                                                            │
│      • Gzip/Brotli compression                                             │
│      • Reduce bandwidth                                                    │
│                                                                             │
│   7. CACHING                                                                │
│      • Cache responses                                                     │
│      • Set cache headers                                                   │
│                                                                             │
│   8. SECURITY                                                               │
│      • Rate limiting                                                       │
│      • IP blocking                                                         │
│      • Security headers (CORS, CSP, HSTS)                                 │
│                                                                             │
│   ❌ CANNOT run application code (Python, Java, Node.js)                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Popular Web Servers

| Web Server | Best For | Key Features |
|------------|----------|--------------|
| **Nginx** | High performance, reverse proxy | Event-driven, low memory, 10K+ connections |
| **Apache** | Feature-rich, legacy apps | .htaccess, modules, mod_php |
| **Caddy** | Simplicity, auto HTTPS | Automatic SSL certificates, simple config |
| **IIS** | Windows/.NET environments | Windows integration, ASP.NET |
| **LiteSpeed** | WordPress, PHP | Drop-in Apache replacement, faster PHP |
| **HAProxy** | Load balancing | Advanced LB algorithms, TCP/HTTP |
| **Traefik** | Kubernetes, Docker | Auto-discovery, cloud-native |

## Nginx vs Apache

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NGINX vs APACHE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    NGINX                              APACHE
              ┌─────────────────┐              ┌─────────────────┐
              │   Event-Driven  │              │  Process-Based  │
              │   Architecture  │              │  Architecture   │
              └────────┬────────┘              └────────┬────────┘
                       │                                │
    ┌──────────────────┴──────────────┐      ┌──────────┴────────────── ┐
    │                                 │      │                          │
    │  Single thread handles          │      │  Each connection =       │
    │  many connections               │      │  new process/thread      │
    │                                 │      │                          │
    │  ┌─────────────────────────┐    │      │  ┌─────┐ ┌─────┐ ┌─────┐ │
    │  │     Event Loop          │    │      │  │Proc1│ │Proc2│ │Proc3│ │
    │  │  ┌───┐ ┌───┐ ┌───┐      │    │      │  └──┬──┘ └──┬──┘ └──┬──┘ │
    │  │  │C1 │ │C2 │ │C3 │ ...  │    │      │     │       │       │    │
    │  │  └───┘ └───┘ └───┘      │    │      │   Conn1   Conn2   Conn3  │
    │  └─────────────────────────┘    │      │                          │
    │                                 │      │                          │
    │  Memory: ~2.5 MB per 10K conn   │      │  Memory: ~10 MB per conn │
    │  Concurrent: 10,000+            │      │  Concurrent: 1,000s      │
    │                                 │      │                          │
    └─────────────────────────────────┘      └──────────────────────────┘

┌──────────────────────┬─────────────────────┬─────────────────────────┐
│       Aspect         │        Nginx        │         Apache          │
├──────────────────────┼─────────────────────┼─────────────────────────┤
│ Architecture         │ Event-driven        │ Process/Thread-based    │
│ Memory usage         │ Low                 │ Higher                  │
│ Concurrent conns     │ Excellent (10K+)    │ Good (1000s)            │
│ Static files         │ Very fast           │ Fast                    │
│ Dynamic content      │ Needs proxy         │ mod_php built-in        │
│ Configuration        │ Centralized files   │ .htaccess per directory │
│ Modules              │ Compiled-in         │ Dynamic loading         │
│ Best for             │ High traffic, proxy │ Shared hosting, PHP     │
└──────────────────────┴─────────────────────┴─────────────────────────┘
```

## Web Server Configuration Examples

### Nginx - Reverse Proxy Configuration

```nginx
# /etc/nginx/nginx.conf

http {
    # Upstream application servers
    upstream app_servers {
        least_conn;  # Load balancing algorithm
        server app1:8000 weight=3;
        server app2:8000 weight=2;
        server app3:8000 weight=1;
        keepalive 32;
    }

    server {
        listen 80;
        listen 443 ssl;
        server_name example.com;

        # SSL Configuration
        ssl_certificate /etc/ssl/certs/example.crt;
        ssl_certificate_key /etc/ssl/private/example.key;

        # Serve static files directly
        location /static/ {
            root /var/www/html;
            expires 30d;
            add_header Cache-Control "public, immutable";
            gzip on;
            gzip_types text/css application/javascript;
        }

        # Proxy API requests to application servers
        location /api/ {
            proxy_pass http://app_servers;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            return 200 'healthy';
            add_header Content-Type text/plain;
        }
    }
}
```

---

# Application Servers

An **application server** runs your actual application code. It receives requests from the web server (or directly), executes your business logic, and returns responses.

**Simple definition:** A program that executes your Python/Java/Node.js code.

## What Application Servers Do

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      APPLICATION SERVER RESPONSIBILITIES                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   1. EXECUTE APPLICATION CODE                                               │
│      • Run your Python/Java/Node.js/Ruby code                              │
│      • Process business logic                                              │
│      • Handle routing                                                       │
│                                                                             │
│   2. MANAGE WORKER PROCESSES                                                │
│      • Spawn multiple workers                                              │
│      • Restart crashed workers                                             │
│      • Graceful shutdown/reload                                            │
│                                                                             │
│   3. HANDLE CONCURRENCY                                                     │
│      • Multiple requests simultaneously                                    │
│      • Thread/process pool management                                      │
│      • Async handling (where supported)                                    │
│                                                                             │
│   4. DATABASE CONNECTIONS                                                   │
│      • Connection pooling                                                  │
│      • Query execution                                                     │
│                                                                             │
│   5. SESSION MANAGEMENT                                                     │
│      • User sessions                                                       │
│      • Authentication state                                                │
│                                                                             │
│   ❌ NOT optimized for static files                                        │
│   ❌ NOT optimized for thousands of concurrent connections                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Application Servers by Language

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    APPLICATION SERVERS BY LANGUAGE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  PYTHON                                                                     │
│  ───────                                                                    │
│  Framework: Flask, Django, FastAPI                                         │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  Gunicorn      │  WSGI server, sync workers, production standard       ││
│  │  uWSGI         │  WSGI server, feature-rich, complex config            ││
│  │  Uvicorn       │  ASGI server, async, for FastAPI/Starlette           ││
│  │  Daphne        │  ASGI server, for Django Channels                     ││
│  │  Waitress      │  WSGI server, Windows compatible                      ││
│  │  Hypercorn     │  ASGI server, HTTP/2 support                          ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  Production command:                                                        │
│  $ gunicorn --workers 4 --bind 0.0.0.0:8000 app:app                        │
│  $ uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  JAVA                                                                       │
│  ────                                                                       │
│  Framework: Spring Boot, Jakarta EE, Micronaut                             │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  Tomcat        │  Servlet container, most popular, embedded in Spring  ││
│  │  Jetty         │  Lightweight, embedded, cloud-friendly                ││
│  │  Undertow      │  High performance, non-blocking, WildFly default      ││
│  │  WildFly       │  Full Jakarta EE server (formerly JBoss)              ││
│  │  GlassFish     │  Reference Jakarta EE implementation                  ││
│  │  WebLogic      │  Oracle enterprise server                             ││
│  │  WebSphere     │  IBM enterprise server                                ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  Spring Boot (embedded Tomcat):                                            │
│  $ java -jar myapp.jar --server.port=8080                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  NODE.JS                                                                    │
│  ───────                                                                    │
│  Framework: Express, Fastify, NestJS, Koa                                  │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  Node.js       │  Built-in HTTP server (no separate server needed)     ││
│  │  PM2           │  Process manager, clustering, monitoring              ││
│  │  Forever       │  Simple process manager                               ││
│  │  Cluster       │  Built-in Node.js clustering module                   ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  Node.js is unique - it HAS a built-in HTTP server!                        │
│  But PM2 adds process management:                                          │
│  $ pm2 start app.js -i max  # Run on all CPU cores                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  GO                                                                         │
│  ──                                                                         │
│  Framework: Gin, Echo, Fiber, Chi                                          │
│                                                                             │
│  Go compiles to a SINGLE BINARY with HTTP server built-in!                 │
│  No separate application server needed.                                    │
│                                                                             │
│  $ ./myapp  # Just run the binary                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  RUBY                                                                       │
│  ────                                                                       │
│  Framework: Ruby on Rails, Sinatra                                         │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  Puma          │  Default for Rails, threaded, fast                    ││
│  │  Unicorn       │  Process-based, copy-on-write                         ││
│  │  Passenger     │  Integrated with Nginx/Apache                         ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  $ bundle exec puma -C config/puma.rb                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  PHP                                                                        │
│  ───                                                                        │
│  Framework: Laravel, Symfony                                               │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  PHP-FPM       │  FastCGI Process Manager, production standard         ││
│  │  Apache+mod_php│  PHP embedded in Apache                               ││
│  │  Swoole        │  Async PHP extension, high performance                ││
│  │  RoadRunner    │  Go-based PHP app server                              ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  Nginx + PHP-FPM is the standard production setup                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  .NET                                                                       │
│  ────                                                                       │
│  Framework: ASP.NET Core                                                   │
│                                                                             │
│  ┌────────────────┬───────────────────────────────────────────────────────┐│
│  │  App Server    │  Description                                          ││
│  ├────────────────┼───────────────────────────────────────────────────────┤│
│  │  Kestrel       │  Built-in, cross-platform, production ready           ││
│  │  IIS           │  Windows only, full featured                          ││
│  │  HTTP.sys      │  Windows kernel-mode driver                           ││
│  └────────────────┴───────────────────────────────────────────────────────┘│
│                                                                             │
│  $ dotnet run --urls http://0.0.0.0:5000                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Why Development Server ≠ Production Server

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 DEVELOPMENT vs PRODUCTION SERVER                            │
└─────────────────────────────────────────────────────────────────────────────┘

❌ NEVER USE IN PRODUCTION:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Python:   $ flask run                                                    │
│             $ python manage.py runserver                                   │
│                                                                             │
│   Node.js:  $ node app.js  (without PM2/clustering)                        │
│                                                                             │
│   Java:     IDE's run button                                               │
│                                                                             │
│   Why? Development servers are:                                            │
│   • Single-threaded / single-process                                       │
│   • No crash recovery                                                      │
│   • No graceful reload                                                     │
│   • Security warnings disabled                                             │
│   • Auto-reloading (CPU overhead)                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

✅ USE IN PRODUCTION:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Python:   $ gunicorn --workers 4 app:app                                 │
│             $ uvicorn main:app --workers 4                                 │
│                                                                             │
│   Node.js:  $ pm2 start app.js -i max                                      │
│                                                                             │
│   Java:     $ java -jar app.jar (Spring Boot with embedded Tomcat)         │
│                                                                             │
│   Why? Production servers provide:                                         │
│   • Multiple workers (use all CPU cores)                                   │
│   • Automatic crash recovery                                               │
│   • Graceful restarts (zero-downtime deploys)                             │
│   • Process management                                                     │
│   • Better performance                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Protocols

Understanding the protocols that connect web servers to application servers.

## WSGI (Web Server Gateway Interface) - Python

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WSGI (Python)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

WSGI = Standard interface between web servers and Python applications

    Web Server                    WSGI Server                  Python App
    (Nginx)                      (Gunicorn)                   (Flask/Django)
       │                             │                             │
       │   HTTP Request              │                             │
       │ ───────────────────────────▶│                             │
       │                             │   WSGI call                 │
       │                             │   environ, start_response   │
       │                             │ ───────────────────────────▶│
       │                             │                             │
       │                             │                        Execute
       │                             │                        handler
       │                             │                             │
       │                             │◀─────────────────────────────│
       │                             │   Response iterator          │
       │◀────────────────────────────│                             │
       │   HTTP Response             │                             │


Simple WSGI Application:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   def application(environ, start_response):                                │
│       status = '200 OK'                                                    │
│       headers = [('Content-Type', 'text/plain')]                          │
│       start_response(status, headers)                                      │
│       return [b'Hello World']                                              │
│                                                                             │
│   Flask and Django implement this interface internally                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

WSGI Servers: Gunicorn, uWSGI, Waitress
Limitation: Synchronous only (one request per worker at a time)
```

## ASGI (Asynchronous Server Gateway Interface) - Python

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              ASGI (Python)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

ASGI = Async version of WSGI, supports WebSockets, HTTP/2

    Client                      ASGI Server                  Async Python App
                               (Uvicorn)                    (FastAPI/Starlette)
       │                             │                             │
       │   HTTP/WebSocket            │                             │
       │ ───────────────────────────▶│                             │
       │                             │   async call                │
       │                             │   scope, receive, send      │
       │                             │ ───────────────────────────▶│
       │                             │                             │
       │                             │                        await
       │                             │                        handler
       │                             │                             │
       │◀────────────────────────────┴─────────────────────────────│
       │         Response (can be streamed)                        │


ASGI Application:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   async def application(scope, receive, send):                             │
│       await send({                                                          │
│           'type': 'http.response.start',                                   │
│           'status': 200,                                                   │
│           'headers': [[b'content-type', b'text/plain']],                  │
│       })                                                                    │
│       await send({                                                          │
│           'type': 'http.response.body',                                    │
│           'body': b'Hello World',                                          │
│       })                                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

ASGI Servers: Uvicorn, Daphne, Hypercorn
Supports: Async/await, WebSockets, HTTP/2, long-polling
```

## Servlet API - Java

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SERVLET API (Java)                               │
└─────────────────────────────────────────────────────────────────────────────┘

Servlet = Java's standard for web request handling

    Web Server              Servlet Container                 Java Servlet
    (Nginx)                    (Tomcat)                     (Spring Controller)
       │                           │                              │
       │   HTTP Request            │                              │
       │ ─────────────────────────▶│                              │
       │                           │   service(request, response) │
       │                           │ ─────────────────────────────▶│
       │                           │                              │
       │                           │                         doGet()
       │                           │                         doPost()
       │                           │                              │
       │◀──────────────────────────┴──────────────────────────────│
       │        HTTP Response                                     │


Servlet Example:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   @WebServlet("/hello")                                                    │
│   public class HelloServlet extends HttpServlet {                          │
│       protected void doGet(HttpServletRequest request,                     │
│                           HttpServletResponse response) {                  │
│           response.setContentType("text/plain");                           │
│           response.getWriter().write("Hello World");                       │
│       }                                                                     │
│   }                                                                         │
│                                                                             │
│   Spring MVC abstracts this into @Controller and @RequestMapping           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Servlet Containers: Tomcat, Jetty, Undertow
Modern Java: Spring Boot embeds Tomcat, runs as single JAR
```

## Protocol Comparison

| Protocol | Language | Sync/Async | WebSocket | Servers |
|----------|----------|------------|-----------|---------|
| WSGI | Python | Sync | No | Gunicorn, uWSGI |
| ASGI | Python | Async | Yes | Uvicorn, Daphne |
| Servlet | Java | Both | Yes (3.1+) | Tomcat, Jetty |
| Rack | Ruby | Sync | No | Puma, Unicorn |
| CGI | Any | Sync | No | Apache mod_cgi |
| FastCGI | Any | Sync | No | PHP-FPM |

---

# Complete Production Architecture

Every layer explained from client to database.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE PRODUCTION ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────────┘


LAYER 0: CLIENT
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Browser, Mobile App, API Client                                    │
│   Does: Sends HTTP requests, renders responses                             │
│   Example: Chrome, iOS app, curl                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
LAYER 1: CDN (Content Delivery Network)
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Globally distributed cache                                         │
│   Does: Serve static content from edge locations near users                │
│   Examples: Cloudflare, AWS CloudFront, Akamai, Fastly                     │
│   Handles: Static files, DDoS protection, SSL termination                  │
│   Capacity: Millions of requests/second globally                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
LAYER 2: LOAD BALANCER
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Traffic distributor                                                │
│   Does: Distributes requests across multiple servers                       │
│   Examples: AWS ALB/NLB, GCP Load Balancer, HAProxy, Nginx                 │
│   Handles: Health checks, SSL termination, routing                         │
│   Capacity: 100,000+ requests/second                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
LAYER 3: WEB SERVER (Reverse Proxy)
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: HTTP connection handler                                            │
│   Does: Serve static files, proxy to app servers, compression              │
│   Examples: Nginx, Apache, Caddy                                           │
│   Handles: 10,000+ concurrent connections per instance                     │
│   Capacity: 50,000+ requests/second (static), 20,000+ (proxy)             │
│                                                                             │
│   Note: In Kubernetes, often combined with Ingress Controller              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
LAYER 4: APPLICATION SERVER
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Code executor                                                      │
│   Does: Run your application code, manage workers                          │
│   Examples: Gunicorn, Tomcat, PM2                                          │
│   Handles: Process management, crash recovery                              │
│   Capacity: 500-5,000 requests/second per instance                        │
│                                                                             │
│   Architecture:                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    Master Process                                    │  │
│   │                         │                                            │  │
│   │     ┌───────────────────┼───────────────────┐                       │  │
│   │     │                   │                   │                       │  │
│   │     ▼                   ▼                   ▼                       │  │
│   │  Worker 1           Worker 2           Worker 3                     │  │
│   │  (Your App)         (Your App)         (Your App)                   │  │
│   │                                                                      │  │
│   │  Workers = (2 × CPU cores) + 1                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
LAYER 5: APPLICATION FRAMEWORK
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Your code                                                          │
│   Does: Business logic, routing, validation, database queries              │
│   Examples: Flask, Django, Spring Boot, Express, Rails                     │
│   Handles: Request processing, response generation                         │
│                                                                             │
│   Request Lifecycle:                                                        │
│   Request → Middleware → Router → Controller → Service → Response          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
LAYER 6: CACHE                           LAYER 7: DATABASE
┌────────────────────────────┐   ┌────────────────────────────────────────────┐
│  What: In-memory store     │   │  What: Persistent storage                  │
│  Does: Cache frequent data │   │  Does: Store all application data          │
│  Examples: Redis, Memcached│   │  Examples: PostgreSQL, MySQL, MongoDB      │
│  Capacity: 100K+ ops/sec   │   │  Capacity: 10K-100K queries/sec (sharded)  │
│                            │   │                                            │
│  Used for:                 │   │  Architecture:                             │
│  • Session storage         │   │  ┌─────────┐    ┌─────────────────────┐   │
│  • Query result cache      │   │  │ Primary │───▶│ Replica 1,2,3...    │   │
│  • Rate limiting           │   │  │ (Write) │    │ (Read)              │   │
│  • Job queues              │   │  └─────────┘    └─────────────────────┘   │
└────────────────────────────┘   └────────────────────────────────────────────┘


LAYER 8: BACKGROUND WORKERS (Async Processing)
┌─────────────────────────────────────────────────────────────────────────────┐
│   What: Async task processors                                              │
│   Does: Handle long-running tasks outside request cycle                    │
│   Examples: Celery (Python), Sidekiq (Ruby), Bull (Node.js)               │
│   Used for: Emails, image processing, reports, notifications              │
│                                                                             │
│   Flow: API → Queue (Redis/RabbitMQ) → Worker → Complete                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

## When to Use Each Layer

| Layer | Always Needed? | Skip If... |
|-------|---------------|------------|
| CDN | Recommended | Internal-only API, no static assets |
| Load Balancer | Recommended | Single server, development |
| Web Server | Depends | App server handles static (Node.js, Go) |
| App Server | Yes | Go binaries (built-in) |
| Framework | Yes | - |
| Cache | Recommended | Low traffic, simple queries |
| Database | Yes | - |
| Workers | If needed | No async tasks needed |

---

# Scaling Strategies

## Vertical vs Horizontal Scaling

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VERTICAL vs HORIZONTAL SCALING                           │
└─────────────────────────────────────────────────────────────────────────────┘


VERTICAL SCALING (Scale Up)
─────────────────────────────
"Get a bigger server"

┌──────────────┐      ┌──────────────────┐      ┌────────────────────┐
│  4 CPU       │  →   │    16 CPU        │  →   │      64 CPU        │
│  16 GB RAM   │      │    64 GB RAM     │      │     256 GB RAM     │
│  1K req/sec  │      │    4K req/sec    │      │     16K req/sec    │
│  $100/month  │      │    $400/month    │      │    $2000/month     │
└──────────────┘      └──────────────────┘      └────────────────────┘
                                                         │
                                                    HIT LIMIT!
                                               (Can't buy bigger)

Pros:
✓ Simple - no code changes
✓ No distributed system complexity
✓ ACID transactions easy

Cons:
✗ Hardware limits exist
✗ Single point of failure
✗ Expensive at scale
✗ Downtime for upgrades


HORIZONTAL SCALING (Scale Out)
──────────────────────────────
"Add more servers"

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  Server 1    │   │  Server 2    │   │  Server 3    │   ... → ∞
│  1K req/sec  │ + │  1K req/sec  │ + │  1K req/sec  │
│  $100/month  │   │  $100/month  │   │  $100/month  │
└──────────────┘   └──────────────┘   └──────────────┘
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                    Load Balancer
                         │
                  Total: 3K req/sec
                  Cost: $300/month + LB

Pros:
✓ No hardware limits
✓ Better fault tolerance
✓ Cost-effective at scale
✓ Zero-downtime scaling

Cons:
✗ Requires stateless design
✗ Distributed system complexity
✗ Data consistency challenges
✗ More infrastructure to manage
```

## Stateless vs Stateful Applications

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STATELESS vs STATEFUL                                  │
└─────────────────────────────────────────────────────────────────────────────┘

STATEFUL (Cannot Scale Horizontally)
─────────────────────────────────────
Server stores user session/data in memory

    Request 1                Request 2
        │                        │
        ▼                        ▼
    ┌────────┐              ┌────────┐
    │Server A│              │Server B│
    │        │              │        │
    │Session:│              │Session:│
    │User123 │              │ (none) │  ← User123's session not here!
    └────────┘              └────────┘

Problem: User must always hit the same server (sticky sessions)


STATELESS (Can Scale Horizontally) ✓
─────────────────────────────────────
Server stores nothing - all state in external store

    Request 1                Request 2
        │                        │
        ▼                        ▼
    ┌────────┐              ┌────────┐
    │Server A│              │Server B│
    │        │              │        │
    │(no     │              │(no     │
    │ state) │              │ state) │
    └───┬────┘              └───┬────┘
        │                       │
        └───────────┬───────────┘
                    │
              ┌─────┴─────┐
              │   Redis   │  ← Session stored externally
              │ Session:  │
              │ User123   │
              └───────────┘

Any server can handle any request!


MAKING YOUR APP STATELESS:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ❌ Don't store in server memory:                                         │
│   • User sessions                                                          │
│   • Shopping carts                                                         │
│   • Uploaded files (temporarily)                                           │
│   • Cache data                                                             │
│                                                                             │
│   ✓ Store externally:                                                      │
│   • Sessions → Redis/Memcached                                             │
│   • Files → S3/GCS/Azure Blob                                             │
│   • Cache → Redis                                                          │
│   • Data → Database                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Handling Millions of Requests

## Single Instance Limits (Reality Check)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SINGLE INSTANCE CAPACITY                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Application Server Throughput (single instance):                         │
│                                                                             │
│   ┌────────────────────┬─────────────────────────────────────────────────┐ │
│   │  Server            │  Typical Throughput (requests/second)           │ │
│   ├────────────────────┼─────────────────────────────────────────────────┤ │
│   │  Gunicorn (Python) │  500 - 2,000 req/sec                           │ │
│   │  Uvicorn (Python)  │  1,000 - 5,000 req/sec (async)                 │ │
│   │  Tomcat (Java)     │  1,000 - 5,000 req/sec                         │ │
│   │  Node.js           │  5,000 - 15,000 req/sec                        │ │
│   │  Go                │  10,000 - 50,000 req/sec                       │ │
│   │  Nginx (static)    │  50,000 - 100,000 req/sec                      │ │
│   └────────────────────┴─────────────────────────────────────────────────┘ │
│                                                                             │
│   * Actual numbers depend on:                                              │
│     - Request complexity (DB queries, external APIs)                       │
│     - Response size                                                        │
│     - Server hardware (CPU, RAM, disk)                                     │
│     - Number of workers                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

A single Gunicorn instance CANNOT handle millions of requests!
```

## How to Handle 1 Million Requests/Second

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              ARCHITECTURE FOR 1 MILLION REQUESTS/SECOND                    │
└─────────────────────────────────────────────────────────────────────────────┘

                        1,000,000 requests/second
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: CDN                                                              │
│  Handles: 70% of requests (static content)                                 │
│  ───────────────────────────────────────────                               │
│  700,000 req/sec served from edge ✓                                        │
│  (Images, CSS, JS, cached API responses)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                         300,000 req/sec remain
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: LOAD BALANCER                                                    │
│  Distributes to app servers                                                │
│  ───────────────────────────────────────────                               │
│  AWS ALB/multiple HAProxy instances                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: APPLICATION SERVERS (300 instances)                              │
│  ───────────────────────────────────────────                               │
│  300 servers × 1,000 req/sec = 300,000 req/sec capacity ✓                 │
│                                                                             │
│  Each server:                                                               │
│  • Gunicorn with 4-8 workers                                               │
│  • Handles 1,000 req/sec                                                   │
│  • Kubernetes auto-scales based on CPU/memory                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: CACHE (Redis Cluster)                                            │
│  Handles: 80% of data reads                                                │
│  ───────────────────────────────────────────                               │
│  240,000 req/sec served from cache ✓                                       │
│  Only 60,000 req/sec hit database                                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                         60,000 req/sec to DB
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: DATABASE (Sharded + Replicated)                                  │
│  ───────────────────────────────────────────                               │
│  • Primary: handles writes                                                  │
│  • 6 read replicas: handle reads                                           │
│  • Sharded if needed for write scaling                                     │
│  60,000 ÷ 10,000 per replica = 6 replicas needed                          │
└─────────────────────────────────────────────────────────────────────────────┘


COST BREAKDOWN (approximate):
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   CDN:              $5,000/month (Cloudflare Pro/Business)                │
│   Load Balancer:    $500/month (AWS ALB)                                  │
│   300 App Servers:  $30,000/month (t3.medium @ $100 each)                │
│   Redis Cluster:    $2,000/month (ElastiCache)                            │
│   Database:         $5,000/month (RDS Multi-AZ + replicas)               │
│   ─────────────────────────────────────────────                           │
│   Total:            ~$42,500/month                                        │
│                                                                            │
│   Per million requests: $0.04                                             │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

## Scaling Strategies Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SCALING STRATEGIES                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. CACHING (Biggest Impact!)                                              │
│     • Cache database queries in Redis                                      │
│     • Cache API responses at CDN                                           │
│     • Cache computed results                                               │
│     • Goal: 80-99% cache hit rate                                         │
│                                                                             │
│  2. CDN FOR STATIC CONTENT                                                 │
│     • Serve JS, CSS, images from edge                                      │
│     • Reduces load on origin by 50-80%                                    │
│                                                                             │
│  3. HORIZONTAL SCALING                                                      │
│     • Add more app server instances                                        │
│     • Auto-scale based on metrics                                          │
│     • Stateless design required                                            │
│                                                                             │
│  4. DATABASE OPTIMIZATION                                                   │
│     • Read replicas for read-heavy workloads                              │
│     • Connection pooling                                                   │
│     • Query optimization & indexing                                        │
│     • Sharding for write-heavy workloads                                  │
│                                                                             │
│  5. ASYNC PROCESSING                                                        │
│     • Move slow operations to background workers                          │
│     • Use message queues (Redis, RabbitMQ, SQS)                           │
│     • Return immediately, process later                                    │
│                                                                             │
│  6. CODE OPTIMIZATION                                                       │
│     • Profile and optimize hot paths                                       │
│     • Reduce external API calls                                            │
│     • Efficient serialization                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Load Balancing

## Load Balancing Algorithms

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCING ALGORITHMS                              │
└─────────────────────────────────────────────────────────────────────────────┘

1. ROUND ROBIN
───────────────
Rotate through servers sequentially

Request 1 → Server A
Request 2 → Server B
Request 3 → Server C
Request 4 → Server A (repeat)

Best for: Equal capacity servers, similar request complexity


2. WEIGHTED ROUND ROBIN
────────────────────────
Assign more requests to powerful servers

Server A (weight: 3) → Gets 3x more requests
Server B (weight: 2) → Gets 2x more requests
Server C (weight: 1) → Gets 1x more requests

Best for: Servers with different capacities


3. LEAST CONNECTIONS
─────────────────────
Send to server with fewest active connections

Server A: 10 connections → ✓ Send here
Server B: 25 connections
Server C: 18 connections

Best for: Varying request duration, long-lived connections


4. IP HASH
───────────
Same client IP always goes to same server

hash(client_ip) % num_servers = target_server

Best for: Session persistence without external session store


5. LEAST RESPONSE TIME
──────────────────────
Send to fastest responding server

Server A: avg 50ms  → ✓ Send here
Server B: avg 120ms
Server C: avg 80ms

Best for: Heterogeneous servers, varying performance


6. RANDOM
─────────
Randomly select a server

Best for: Simple use cases, statistically even distribution
```

## Health Checks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HEALTH CHECKS                                     │
└─────────────────────────────────────────────────────────────────────────────┘

Load balancer periodically checks if servers are healthy

Types of Health Checks:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. TCP Check                                                               │
│     Can connect to port? (basic)                                           │
│                                                                             │
│  2. HTTP Check                                                              │
│     GET /health returns 200? (recommended)                                 │
│                                                                             │
│  3. Deep Health Check                                                       │
│     GET /health/ready - checks DB, cache, dependencies                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Health Endpoint Example:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  GET /health                                                                │
│  Response: 200 OK                                                           │
│  {                                                                          │
│    "status": "healthy",                                                    │
│    "database": "connected",                                                │
│    "redis": "connected",                                                   │
│    "uptime": "24h 30m"                                                     │
│  }                                                                          │
│                                                                             │
│  If unhealthy: 503 Service Unavailable                                     │
│  Load balancer removes server from pool                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

         Load Balancer
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│Server1│ │Server2│ │Server3│
│  ✓    │ │  ✓    │ │  ✗    │ ← Removed from pool
└───────┘ └───────┘ └───────┘
    │         │
    └────┬────┘
         │
    Traffic only goes
    to healthy servers
```

---

# Caching Layer

## Caching Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CACHING STRATEGIES                                  │
└─────────────────────────────────────────────────────────────────────────────┘


1. CACHE-ASIDE (Lazy Loading)
─────────────────────────────
Application manages cache reads/writes

    Request
       │
       ▼
    ┌──────────────────────────────────────┐
    │  1. Check cache                       │
    │     ┌─────────┐                      │
    │     │  Cache  │ ──── HIT ───▶ Return │
    │     └────┬────┘                      │
    │          │ MISS                      │
    │          ▼                           │
    │  2. Query database                   │
    │     ┌─────────┐                      │
    │     │Database │                      │
    │     └────┬────┘                      │
    │          │                           │
    │  3. Store in cache                   │
    │  4. Return data                      │
    │                                      │
    └──────────────────────────────────────┘

Pros: Only requested data cached, cache failures don't break app
Cons: Cache miss is slow (3 steps), potential for stale data


2. WRITE-THROUGH
────────────────
Write to cache and database together

    Write Request
         │
         ├────────────────┐
         ▼                ▼
    ┌─────────┐     ┌─────────┐
    │  Cache  │     │Database │
    └─────────┘     └─────────┘
         │                │
         └───── Both updated simultaneously

Pros: Cache always consistent with DB
Cons: Write latency increased, writes to cache that may never be read


3. WRITE-BEHIND (Write-Back)
────────────────────────────
Write to cache immediately, sync to DB later

    Write Request
         │
         ▼
    ┌─────────┐
    │  Cache  │ ──── Immediate return
    └────┬────┘
         │
    (Async, batched)
         │
         ▼
    ┌─────────┐
    │Database │
    └─────────┘

Pros: Fast writes, reduces DB load
Cons: Data loss risk if cache fails before sync


4. READ-THROUGH
───────────────
Cache handles DB reads transparently

    Request
       │
       ▼
    ┌─────────┐
    │  Cache  │ ──── HIT ───▶ Return
    │         │
    │  MISS   │
    │    │    │
    │    ▼    │
    │┌───────┐│
    ││  DB   ││ ← Cache fetches from DB
    │└───────┘│
    │         │
    └─────────┘

Pros: Application code simpler
Cons: First request slow, need cache that supports this
```

## What to Cache

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WHAT TO CACHE                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   HIGH VALUE (Cache These!)                                                │
│   ─────────────────────────                                                │
│   • Database query results (especially complex joins)                      │
│   • API responses from external services                                   │
│   • Computed/aggregated data                                               │
│   • User sessions                                                          │
│   • Configuration data                                                     │
│   • Static reference data (countries, categories)                         │
│                                                                             │
│   MEDIUM VALUE                                                              │
│   ────────────                                                              │
│   • User profile data                                                      │
│   • Recent activity                                                        │
│   • Search results                                                         │
│                                                                             │
│   LOW VALUE (Don't Cache)                                                  │
│   ───────────────────────                                                  │
│   • Rapidly changing data                                                  │
│   • Write-heavy data                                                       │
│   • User-specific transient data                                          │
│   • Large objects that are rarely accessed                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Cache Invalidation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CACHE INVALIDATION                                    │
│              "The two hardest problems in computer science:                │
│               cache invalidation and naming things"                        │
└─────────────────────────────────────────────────────────────────────────────┘

Strategies:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. TIME-BASED (TTL)                                                       │
│     cache.set("user:123", data, ttl=3600)  # Expires in 1 hour            │
│     Simple but may serve stale data                                        │
│                                                                             │
│  2. EVENT-BASED                                                             │
│     On data change → invalidate cache                                      │
│     def update_user(user_id, data):                                        │
│         db.update(user_id, data)                                          │
│         cache.delete(f"user:{user_id}")  # Invalidate                     │
│                                                                             │
│  3. VERSION-BASED                                                           │
│     Include version in cache key                                           │
│     cache.set(f"user:123:v{version}", data)                               │
│     On update, increment version → old cache orphaned                      │
│                                                                             │
│  4. WRITE-THROUGH                                                           │
│     Update cache when writing to DB                                        │
│     Always consistent but more writes                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Kubernetes Scaling

## Horizontal Pod Autoscaler (HPA)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   KUBERNETES AUTO-SCALING                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │  Metrics Server     │
                    │  (monitors CPU/mem) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  HPA Controller     │
                    │                     │
                    │  IF CPU > 70%:      │
                    │    scale up         │
                    │  IF CPU < 30%:      │
                    │    scale down       │
                    └──────────┬──────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT                                          │
│                                                                             │
│  Low Traffic (CPU: 20%)           High Traffic (CPU: 85%)                  │
│                                                                             │
│  ┌─────┐ ┌─────┐                  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ │
│  │Pod 1│ │Pod 2│       ───▶       │Pod 1│ │Pod 2│ │Pod 3│ │Pod 4│ │Pod 5│ │
│  └─────┘ └─────┘                  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ │
│                                                                             │
│  replicas: 2                      replicas: 5 (auto-scaled)                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘


HPA Configuration:
```

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 100
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
    scaleUp:
      stabilizationWindowSeconds: 0    # Scale up immediately
```

## Complete Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KUBERNETES PRODUCTION SETUP                              │
└─────────────────────────────────────────────────────────────────────────────┘

                              Internet
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Cloud Load Balancer  │
                    │   (AWS ALB / GCP LB)   │
                    └───────────┬────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER                                   │
│                                                                             │
│   ┌────────────────────────────────────────────────────────────────────┐   │
│   │                    INGRESS CONTROLLER                              │   │
│   │                    (Nginx Ingress)                                 │   │
│   │                                                                    │   │
│   │    Routes:                                                         │   │
│   │    /api/*  → backend-service                                      │   │
│   │    /*      → frontend-service                                     │   │
│   └────────────────────────────┬───────────────────────────────────────┘   │
│                                │                                            │
│           ┌────────────────────┴────────────────────┐                      │
│           │                                         │                      │
│           ▼                                         ▼                      │
│   ┌───────────────────────┐              ┌───────────────────────┐        │
│   │  BACKEND SERVICE      │              │  FRONTEND SERVICE     │        │
│   │                       │              │                       │        │
│   │  ┌─────┐ ┌─────┐     │              │  ┌─────┐ ┌─────┐     │        │
│   │  │Pod 1│ │Pod 2│ ... │              │  │Pod 1│ │Pod 2│     │        │
│   │  │App  │ │App  │     │              │  │Nginx│ │Nginx│     │        │
│   │  └─────┘ └─────┘     │              │  └─────┘ └─────┘     │        │
│   │                       │              │                       │        │
│   │  HPA: 2-50 replicas   │              │  HPA: 2-10 replicas  │        │
│   └───────────┬───────────┘              └───────────────────────┘        │
│               │                                                            │
│               ▼                                                            │
│   ┌───────────────────────┐     ┌───────────────────────────┐             │
│   │  REDIS (StatefulSet)  │     │  DATABASE (External/RDS)  │             │
│   │  Cache + Sessions     │     │  PostgreSQL               │             │
│   └───────────────────────┘     └───────────────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Real-World Architecture Examples

## Instagram (Python/Django)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INSTAGRAM ARCHITECTURE                                   │
│                    (Python/Django at Scale)                                │
└─────────────────────────────────────────────────────────────────────────────┘

Traffic: 1+ billion users, millions of requests/second

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Tech Stack:                                                               │
│   • Python/Django                                                          │
│   • Gunicorn (thousands of instances)                                      │
│   • PostgreSQL (heavily sharded)                                           │
│   • Cassandra (for high-write data)                                       │
│   • Memcached (for caching)                                                │
│   • Redis (for queues)                                                     │
│                                                                             │
│   Key Strategies:                                                           │
│   • Aggressive caching (99%+ cache hit rate)                              │
│   • Database sharding (thousands of shards)                               │
│   • Async task processing (Celery)                                        │
│   • CDN for images (Akamai/Facebook CDN)                                  │
│   • Microservices for specific features                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Netflix (Java + Microservices)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      NETFLIX ARCHITECTURE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

Traffic: 200+ million subscribers, 400K+ requests/second

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Tech Stack:                                                               │
│   • Java (Spring Boot)                                                     │
│   • Node.js (for some services)                                           │
│   • Cassandra (primary database)                                          │
│   • EVCache (Memcached-based)                                              │
│   • Kafka (event streaming)                                                │
│   • AWS (infrastructure)                                                   │
│                                                                             │
│   Key Strategies:                                                           │
│   • 1000+ microservices                                                    │
│   • Each service: 10-100+ instances                                       │
│   • Circuit breakers (Hystrix)                                            │
│   • Service mesh (Zuul for routing)                                       │
│   • Chaos engineering (Chaos Monkey)                                      │
│   • Multi-region deployment                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Uber (Microservices)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UBER ARCHITECTURE                                    │
└─────────────────────────────────────────────────────────────────────────────┘

Traffic: Millions of trips/day, 1M+ requests/second

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   Tech Stack:                                                               │
│   • Go (primary language)                                                  │
│   • Java (some services)                                                   │
│   • Python (data/ML)                                                       │
│   • Node.js (frontend)                                                     │
│   • MySQL (sharded)                                                        │
│   • Redis (caching)                                                        │
│   • Kafka (messaging)                                                      │
│                                                                             │
│   Key Strategies:                                                           │
│   • 4000+ microservices                                                    │
│   • 10,000+ servers                                                        │
│   • Domain-oriented architecture                                           │
│   • Ring-pop (consistent hashing)                                          │
│   • Custom service mesh                                                    │
│   • Geographic sharding                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

# Interview Tips

## Common Interview Questions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMMON INTERVIEW QUESTIONS                             │
└─────────────────────────────────────────────────────────────────────────────┘

Q: "What is the difference between a web server and an application server?"
───────────────────────────────────────────────────────────────────────────────
A: Web server (Nginx/Apache) handles HTTP connections, serves static files,
   and acts as a reverse proxy. Application server (Gunicorn/Tomcat) runs
   your application code. Web servers are optimized for many concurrent
   connections; app servers are optimized for code execution.


Q: "Why do we need Gunicorn/uWSGI in front of Flask/Django?"
───────────────────────────────────────────────────────────────────────────────
A: Flask's built-in server is single-threaded and meant for development only.
   Gunicorn provides:
   - Multiple worker processes (use all CPU cores)
   - Automatic worker restart on crash
   - Graceful reloads for zero-downtime deploys
   - Better performance and reliability


Q: "Can a single server handle millions of requests?"
───────────────────────────────────────────────────────────────────────────────
A: No. A single Gunicorn instance handles ~1,000 req/sec. For millions, you
   need:
   - CDN (serves 70% of static content)
   - Load balancer distributing to 100s-1000s of app servers
   - Caching (Redis) to reduce database load
   - Database sharding and replication


Q: "How would you scale a web application?"
───────────────────────────────────────────────────────────────────────────────
A: 1. Add caching (biggest impact) - 80%+ cache hit rate
   2. Use CDN for static content
   3. Horizontal scaling with load balancer
   4. Database read replicas for reads
   5. Async processing for slow operations
   6. Database sharding for write scaling


Q: "What is the difference between vertical and horizontal scaling?"
───────────────────────────────────────────────────────────────────────────────
A: Vertical = bigger server (limited by hardware, expensive)
   Horizontal = more servers (unlimited, requires stateless design)
   
   Horizontal is preferred because it:
   - Has no upper limit
   - Provides fault tolerance
   - Is cost-effective at scale


Q: "What does 'stateless' mean and why is it important?"
───────────────────────────────────────────────────────────────────────────────
A: Stateless means the server stores no user-specific data in memory.
   Sessions, files, and cache are stored externally (Redis, S3).
   
   Important because:
   - Any server can handle any request (load balancing)
   - Servers can be added/removed without session loss
   - Enables horizontal scaling


Q: "Explain caching strategies"
───────────────────────────────────────────────────────────────────────────────
A: Cache-Aside: App checks cache, if miss reads from DB and populates cache
   Write-Through: Write to cache and DB simultaneously
   Write-Behind: Write to cache, async sync to DB
   
   Cache-Aside is most common - simple and resilient to cache failures.


Q: "What load balancing algorithms do you know?"
───────────────────────────────────────────────────────────────────────────────
A: Round Robin: Rotate through servers
   Least Connections: Send to server with fewest active connections
   IP Hash: Same client always goes to same server
   Weighted: More traffic to powerful servers
   
   Least Connections is often best for varying request durations.


Q: "How do you handle session management in a distributed system?"
───────────────────────────────────────────────────────────────────────────────
A: Don't store sessions in server memory. Use:
   - Redis/Memcached for session storage
   - JWT tokens (stateless, session in token)
   - Database (slower, but simple)
   
   This allows any server to handle any user's request.
```

## Key Points to Remember

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       KEY POINTS TO REMEMBER                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  WEB SERVERS:                                                               │
│  • Handle HTTP connections efficiently (10K+ concurrent)                   │
│  • Serve static files (fast!)                                              │
│  • Cannot run application code                                             │
│  • Examples: Nginx, Apache, Caddy                                          │
│                                                                             │
│  APPLICATION SERVERS:                                                       │
│  • Run your application code                                               │
│  • Manage worker processes                                                 │
│  • Handle 500-5,000 req/sec per instance                                  │
│  • Examples: Gunicorn (Python), Tomcat (Java), PM2 (Node.js)              │
│                                                                             │
│  SCALING:                                                                   │
│  • Single instance cannot handle millions - need many instances           │
│  • Horizontal scaling > Vertical scaling                                   │
│  • Stateless design is required for horizontal scaling                    │
│  • Caching has the biggest impact on performance                          │
│                                                                             │
│  ARCHITECTURE LAYERS:                                                       │
│  • CDN → Load Balancer → Web Server → App Server → Cache → Database       │
│  • Each layer has its purpose and capacity limits                         │
│                                                                             │
│  PRODUCTION SETUP:                                                          │
│  • Never use development servers in production                             │
│  • Always use production app servers (Gunicorn, not flask run)            │
│  • Implement health checks                                                 │
│  • Use auto-scaling (Kubernetes HPA)                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

| Component | Examples | Capacity | Purpose |
|-----------|----------|----------|---------|
| CDN | Cloudflare, CloudFront | Millions req/sec | Static content, DDoS protection |
| Load Balancer | ALB, HAProxy, Nginx | 100K+ req/sec | Traffic distribution |
| Web Server | Nginx, Apache | 50K+ req/sec | HTTP, static files, proxy |
| App Server | Gunicorn, Tomcat, PM2 | 1-5K req/sec | Run application code |
| Cache | Redis, Memcached | 100K+ ops/sec | Speed up reads |
| Database | PostgreSQL, MySQL | 10K+ queries/sec | Persistent storage |

---

*Last updated: January 2026*

