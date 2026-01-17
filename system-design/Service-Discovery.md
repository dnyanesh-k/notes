# Service Discovery

A comprehensive guide to service discovery patterns and mechanisms for enabling dynamic service location and communication in distributed systems and microservices architectures.

---

## Table of Contents

1. [What is Service Discovery?](#what-is-service-discovery)
2. [Why Service Discovery?](#why-service-discovery)
3. [Service Discovery Patterns](#service-discovery-patterns)
4. [Service Registry](#service-registry)
5. [Client-Side Discovery](#client-side-discovery)
6. [Server-Side Discovery](#server-side-discovery)
7. [Service Mesh](#service-mesh)
8. [Health Checks](#health-checks)
9. [Service Discovery Solutions](#service-discovery-solutions)
10. [Interview Tips](#interview-tips)

---

# What is Service Discovery?

## What is Service Discovery?

**Service Discovery** is a mechanism that allows services in a distributed system to automatically find and communicate with each other without hardcoded network locations. Services register themselves and discover other services dynamically.

**Simple definition:** Like a phone book for services - services register their location (phone number), and other services can look them up (find their phone number) when they need to communicate.

In traditional systems, services had fixed IP addresses and ports. In modern distributed systems, services are dynamic - they can start, stop, move, and scale. Service discovery enables services to find each other in this dynamic environment.

## Why Service Discovery?

**Problems Without Service Discovery:**
- Hardcoded service locations (IP addresses, ports) break when services move
- Manual configuration needed for every service change
- Difficult to scale services (need to update all clients)
- No automatic failover when services fail
- Load balancing requires manual configuration
- Service instances come and go (containers, auto-scaling)

**Benefits With Service Discovery:**
- Automatic service location without hardcoded addresses
- Dynamic adaptation to service changes
- Easy scaling (new instances automatically discovered)
- Automatic failover (unhealthy services removed)
- Load balancing across service instances
- Works with container orchestration (Kubernetes, Docker Swarm)

---

# Service Discovery Patterns

## Two Main Patterns

There are two primary patterns for service discovery: client-side discovery and server-side discovery. Each has different trade-offs and use cases.

### Pattern Comparison

| Aspect | Client-Side Discovery | Server-Side Discovery |
|--------|---------------------|---------------------|
| **Discovery Logic** | Client queries registry | Load balancer queries registry |
| **Load Balancing** | Client selects instance | Load balancer selects instance |
| **Complexity** | More complex client | Simpler client |
| **Language Support** | Client must implement | Works with any client |
| **Flexibility** | More flexible | Less flexible |
| **Use Case** | Microservices, polyglot | Traditional, web applications |

---

# Service Registry

## What is Service Registry?

**Service Registry** is a centralized database that stores information about available service instances. Services register themselves when they start and deregister when they stop.

**Simple definition:** A central directory where services announce their availability and other services look them up, like a service directory or phone book.

The service registry is the heart of service discovery. It maintains a current list of all available service instances, their network locations, and health status.

## Service Registry Components

### 1. Service Registration

**What is Service Registration?**

Service registration is the process by which a service instance registers itself with the service registry when it starts up, providing its network location and metadata.

**Registration Information:**
- Service name (e.g., "user-service")
- Network location (IP address, port)
- Health check endpoint
- Metadata (version, region, tags)
- Lease/expiration time

**Registration Methods:**
- **Self-Registration:** Service registers itself (push model)
- **Third-Party Registration:** Registration service registers on behalf (pull model)

**Example:**
```
Service: user-service
IP: 192.168.1.10
Port: 8080
Health: /health
Version: v1.2.3
```

### 2. Service Deregistration

**What is Service Deregistration?**

Service deregistration is the process by which a service instance removes itself from the service registry when it shuts down gracefully.

**Deregistration Methods:**
- **Explicit Deregistration:** Service explicitly removes itself on shutdown
- **Automatic Expiration:** Registry removes service if heartbeat stops (lease expiration)
- **Health Check Failure:** Registry removes unhealthy services

**Why Important:**
- Prevents routing to unavailable services
- Keeps registry accurate
- Enables automatic cleanup

### 3. Service Lookup

**What is Service Lookup?**

Service lookup is the process by which a client queries the service registry to find available instances of a service it needs to call.

**Lookup Process:**
1. Client queries registry for service name
2. Registry returns list of available instances
3. Client selects instance (or uses load balancer)
4. Client makes request to selected instance

**Lookup Information:**
- Service name
- List of available instances
- Instance network locations
- Health status
- Metadata

## Service Registry Types

### 1. Application-Level Registry

**What is Application-Level Registry?**

Application-level registry is implemented as part of the application infrastructure, often using existing databases or specialized registry services.

**Examples:**
- Netflix Eureka
- HashiCorp Consul
- Apache Zookeeper
- etcd

**Characteristics:**
- Separate service/process
- Provides API for registration/lookup
- Maintains service catalog
- Can be clustered for high availability

### 2. Platform-Level Registry

**What is Platform-Level Registry?**

Platform-level registry is provided by the platform or orchestration system, integrated into the infrastructure.

**Examples:**
- Kubernetes Service Discovery
- Docker Swarm Service Discovery
- AWS ECS Service Discovery
- Cloud platform service registries

**Characteristics:**
- Built into platform
- Automatic registration
- Platform-managed
- Less application code needed

---

# Client-Side Discovery

## What is Client-Side Discovery?

**Client-Side Discovery** is a pattern where the client is responsible for querying the service registry, selecting a service instance, and making requests directly to that instance.

**Simple definition:** The client acts like a customer looking up a business in a phone book, then calling that business directly.

In client-side discovery, the client has the logic to discover services and load balance across instances. The client queries the registry, gets a list of instances, selects one (using load balancing algorithm), and makes the request.

## How Client-Side Discovery Works

### Step-by-Step Flow

1. **Service Registration:** Service instances register with service registry when they start
2. **Client Query:** Client queries service registry for service name (e.g., "user-service")
3. **Registry Response:** Registry returns list of available service instances
4. **Instance Selection:** Client selects instance using load balancing algorithm (round-robin, random, etc.)
5. **Direct Request:** Client makes request directly to selected instance
6. **Response:** Service instance responds directly to client

### Architecture Diagram

```
┌─────────┐         ┌──────────────┐         ┌─────────────┐
│ Client  │────────▶│   Registry   │         │   Service   │
│         │ Query   │              │         │  Instance 1 │
└────┬────┘         └──────┬───────┘         └─────────────┘
     │                     │
     │ 1. Query            │ 2. Return list
     │    "user-service"   │    [Instance1, Instance2]
     │                     │
     │ 3. Select Instance1 │
     │                     │
     │ 4. Request ────────┼─────────────────▶
     │                     │
     │ 5. Response ◀───────┼─────────────────
     │                     │
```

## Advantages

- **Flexibility:** Client has full control over instance selection
- **Load Balancing:** Client can implement custom load balancing
- **Direct Communication:** No intermediate proxy, lower latency
- **Language Agnostic:** Works with any client language (if registry API available)
- **Fine-Grained Control:** Client can implement retry, circuit breaker logic

## Disadvantages

- **Client Complexity:** Client must implement discovery and load balancing logic
- **Language Support:** Each client language needs discovery library
- **Coupling:** Client coupled to service registry
- **Scattered Logic:** Discovery logic in every client
- **Testing:** More complex to test (need to mock registry)

## Use Cases

- Microservices architectures
- Polyglot systems (multiple languages)
- When fine-grained control needed
- When direct service communication preferred
- When custom load balancing required

## Example Implementation

**Client Code (Pseudocode):**
```python
# Client queries registry
instances = registry.lookup("user-service")

# Client selects instance (round-robin)
instance = load_balancer.select(instances)

# Client makes request directly
response = http.get(f"http://{instance.ip}:{instance.port}/users/123")
```

---

# Server-Side Discovery

## What is Server-Side Discovery?

**Server-Side Discovery** is a pattern where a load balancer or API gateway queries the service registry and routes client requests to available service instances. The client doesn't know about the registry.

**Simple definition:** Like calling a company's main phone number - the receptionist (load balancer) looks up which department (service instance) to route you to, and you don't need to know the internal extensions.

In server-side discovery, the client makes requests to a well-known endpoint (load balancer), and the load balancer handles service discovery and routing. The client is simpler and doesn't need discovery logic.

## How Server-Side Discovery Works

### Step-by-Step Flow

1. **Service Registration:** Service instances register with service registry when they start
2. **Client Request:** Client makes request to load balancer (well-known endpoint)
3. **Load Balancer Query:** Load balancer queries service registry for service name
4. **Registry Response:** Registry returns list of available service instances
5. **Instance Selection:** Load balancer selects instance using load balancing algorithm
6. **Request Routing:** Load balancer routes request to selected instance
7. **Response:** Service instance responds through load balancer to client

### Architecture Diagram

```
┌─────────┐         ┌──────────────┐         ┌──────────────┐         ┌─────────────┐
│ Client  │────────▶│ Load Balancer│────────▶│   Registry   │         │   Service   │
│         │ Request │              │ Query   │              │         │  Instance 1 │
└─────────┘         └──────┬───────┘         └──────┬───────┘         └─────────────┘
                           │                        │
                           │ 1. Query               │ 2. Return list
                           │    "user-service"      │    [Instance1, Instance2]
                           │                        │
                           │ 3. Select Instance1    │
                           │                        │
                           │ 4. Route Request ─────┼─────────────────▶
                           │                        │
                           │ 5. Response ◀──────────┼─────────────────
                           │                        │
                           │ 6. Return to Client    │
```

## Advantages

- **Client Simplicity:** Client doesn't need discovery logic, just calls well-known endpoint
- **Centralized Logic:** Discovery and load balancing logic in one place
- **Language Agnostic:** Works with any client (HTTP, gRPC, etc.)
- **Easier Testing:** Client testing simpler (no registry mocking)
- **Platform Integration:** Can integrate with platform load balancers

## Disadvantages

- **Additional Hop:** Extra network hop through load balancer (slight latency)
- **Load Balancer Dependency:** Single point of failure (need HA)
- **Less Flexibility:** Client has less control over instance selection
- **Platform Lock-in:** May be tied to specific platform/cloud provider

## Use Cases

- Traditional web applications
- When client simplicity is priority
- When using platform load balancers (AWS ELB, GCP Load Balancer)
- REST APIs with HTTP load balancers
- When centralized control preferred

## Example Implementation

**Client Code (Simple):**
```python
# Client just calls well-known endpoint
response = http.get("https://api.example.com/users/123")
# Load balancer handles discovery and routing
```

**Load Balancer (Handles Discovery):**
```
1. Receives request for /users/123
2. Queries registry for "user-service"
3. Gets list of instances
4. Selects instance (round-robin)
5. Routes request to selected instance
```

---

# Service Mesh

## What is Service Mesh?

**Service Mesh** is an infrastructure layer that handles service-to-service communication, including service discovery, load balancing, security, and observability, transparently to the application.

**Simple definition:** Like a smart network layer that sits between your services and handles all the communication complexity, so your application code doesn't have to worry about it.

Service mesh provides service discovery as part of a comprehensive solution for microservices communication. It's transparent to the application - services don't need to implement discovery logic.

## How Service Mesh Works

### Architecture

Service mesh consists of:
- **Data Plane:** Sidecar proxies (Envoy, Linkerd-proxy) that handle traffic
- **Control Plane:** Management layer (Istio, Linkerd control plane) that configures proxies

### Service Discovery in Service Mesh

1. **Automatic Registration:** Services automatically registered when deployed
2. **Proxy-Based Discovery:** Sidecar proxies handle service discovery
3. **Transparent to Application:** Application code doesn't need discovery logic
4. **Platform Integration:** Works with Kubernetes, Docker, etc.

### Example: Istio Service Mesh

**How it works:**
- Istio control plane manages service registry
- Envoy sidecar proxies handle discovery and routing
- Services communicate through sidecar proxies
- Application code unchanged

**Benefits:**
- No application code changes
- Automatic service discovery
- Built-in load balancing, security, observability
- Works with any language

## Service Mesh vs Traditional Discovery

| Aspect | Traditional Discovery | Service Mesh |
|--------|---------------------|--------------|
| **Implementation** | Application code or load balancer | Infrastructure layer |
| **Code Changes** | May need code changes | No code changes |
| **Features** | Discovery only | Discovery + security + observability |
| **Complexity** | Simpler | More complex infrastructure |
| **Use Case** | Simple microservices | Complex microservices |

---

# Health Checks

## What are Health Checks?

**Health Checks** are mechanisms used by the service registry to determine if a service instance is healthy and should receive traffic. Unhealthy instances are removed from the registry.

**Simple definition:** Like a doctor checking if a patient is healthy - the registry periodically checks if services are responding, and removes sick ones from the directory.

Health checks are critical for service discovery. Without them, the registry might route traffic to dead or unresponsive service instances, causing failures.

## Health Check Types

### 1. HTTP Health Check

**How it works:**
- Registry makes HTTP GET request to health endpoint (e.g., `/health`)
- Service returns 200 OK if healthy, other status if unhealthy
- Registry marks service as healthy or unhealthy

**Example:**
```
GET /health
Response: 200 OK
Body: {"status": "healthy"}
```

**Advantages:**
- Simple to implement
- Standard HTTP protocol
- Can include detailed health information

**Disadvantages:**
- Requires HTTP server
- Network overhead
- May not detect all issues

### 2. TCP Health Check

**How it works:**
- Registry attempts TCP connection to service port
- If connection succeeds, service is healthy
- If connection fails, service is unhealthy

**Example:**
```
Registry → TCP Connect to port 8080
Success → Service healthy
Failure → Service unhealthy
```

**Advantages:**
- Simple and fast
- Works with any TCP service
- Low overhead

**Disadvantages:**
- Less detailed than HTTP
- May not detect application-level issues
- Only checks if port is open

### 3. Custom Health Check

**How it works:**
- Service implements custom health check logic
- Can check database connections, dependencies, etc.
- Returns detailed health status

**Example:**
```json
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "disk": "ok"
}
```

**Advantages:**
- Comprehensive health information
- Can check dependencies
- Detailed status

**Disadvantages:**
- More complex to implement
- Service-specific logic
- May be slower

## Health Check Configuration

### Check Interval

**What is Check Interval?**

Check interval is how often the registry performs health checks on service instances.

**Example:**
```
checkInterval: 10 seconds  // Check every 10 seconds
```

### Timeout

**What is Timeout?**

Timeout is how long to wait for health check response before considering it failed.

**Example:**
```
timeout: 5 seconds  // Wait 5 seconds for response
```

### Failure Threshold

**What is Failure Threshold?**

Failure threshold is how many consecutive health check failures before marking service as unhealthy.

**Example:**
```
failureThreshold: 3  // Mark unhealthy after 3 failures
```

### Success Threshold

**What is Success Threshold?**

Success threshold is how many consecutive successful health checks before marking service as healthy (after being unhealthy).

**Example:**
```
successThreshold: 2  // Mark healthy after 2 successes
```

---

# Service Discovery Solutions

## Popular Solutions

### 1. Netflix Eureka

**What is Eureka?**

Eureka is a service registry and discovery server developed by Netflix for their microservices architecture.

**Features:**
- Service registration and discovery
- Client-side discovery pattern
- Health checks
- High availability (peer-to-peer replication)
- REST API

**How it works:**
- Services register with Eureka server
- Clients query Eureka for service instances
- Eureka maintains service registry
- Supports multiple regions and zones

**Use Cases:**
- Java-based microservices
- Netflix-style architectures
- Client-side discovery

### 2. HashiCorp Consul

**What is Consul?**

Consul is a service mesh solution that provides service discovery, health checking, and key-value storage.

**Features:**
- Service discovery
- Health checking
- Key-value store
- Multi-datacenter support
- DNS and HTTP API

**How it works:**
- Services register with Consul agent
- Consul maintains service catalog
- Health checks via Consul agents
- DNS or HTTP API for service lookup

**Use Cases:**
- Multi-datacenter deployments
- Service discovery + configuration
- Health checking

### 3. etcd

**What is etcd?**

etcd is a distributed key-value store that can be used as a service registry.

**Features:**
- Distributed key-value store
- Watch/notify for changes
- Strong consistency
- Used by Kubernetes

**How it works:**
- Services store registration info in etcd
- Clients watch etcd for service changes
- etcd provides strong consistency
- Kubernetes uses etcd for service discovery

**Use Cases:**
- Kubernetes clusters
- When strong consistency needed
- Distributed systems

### 4. Kubernetes Service Discovery

**What is Kubernetes Service Discovery?**

Kubernetes provides built-in service discovery through Services and DNS.

**Features:**
- Automatic service registration
- DNS-based service discovery
- Load balancing
- Health checks (via probes)

**How it works:**
- Pods automatically registered as endpoints
- Kubernetes Service provides stable endpoint
- DNS resolves service names to IPs
- kube-proxy handles load balancing

**Use Cases:**
- Kubernetes deployments
- Container orchestration
- Platform-level discovery

### 5. AWS ECS Service Discovery

**What is AWS ECS Service Discovery?**

AWS ECS provides service discovery integrated with AWS Cloud Map.

**Features:**
- Automatic service registration
- DNS-based discovery
- Health checks
- Integration with AWS services

**How it works:**
- ECS tasks automatically registered
- Cloud Map maintains service registry
- DNS resolves service names
- Works with ECS, EKS, EC2

**Use Cases:**
- AWS deployments
- ECS/EKS clusters
- Cloud-native applications

---

# Interview Tips

## Common Questions

**Q: What is service discovery and why is it needed?**
- Mechanism for services to automatically find and communicate with each other
- Needed because services are dynamic (start, stop, move, scale)
- Replaces hardcoded IP addresses with dynamic lookup
- Enables automatic failover and load balancing

**Q: What is the difference between client-side and server-side discovery?**
- **Client-side:** Client queries registry, selects instance, makes direct request
- **Server-side:** Client calls load balancer, load balancer queries registry and routes
- Client-side: More flexible, client complexity
- Server-side: Simpler client, centralized logic

**Q: What is a service registry?**
- Centralized database storing available service instances
- Services register when starting, deregister when stopping
- Clients query registry to find services
- Maintains service catalog with network locations and health status

**Q: How do health checks work in service discovery?**
- Registry periodically checks if services are healthy
- Types: HTTP (GET /health), TCP (connection test), custom
- Unhealthy services removed from registry
- Configuration: interval, timeout, failure threshold, success threshold

**Q: What is service mesh and how does it relate to service discovery?**
- Infrastructure layer handling service-to-service communication
- Provides service discovery transparently to application
- Includes sidecar proxies (data plane) and control plane
- No application code changes needed
- Examples: Istio, Linkerd

**Q: How does Kubernetes service discovery work?**
- Pods automatically registered as endpoints
- Kubernetes Service provides stable endpoint
- DNS resolves service names to IPs
- kube-proxy handles load balancing
- Platform-level, no application code needed

**Q: What are the trade-offs of different service discovery patterns?**
- **Client-side:** Flexible but complex clients, direct communication
- **Server-side:** Simple clients but extra hop, centralized
- **Service mesh:** No code changes but infrastructure complexity
- **Platform-level:** Automatic but platform lock-in

## Key Points to Remember

- **Service Discovery** = Automatic service location in dynamic systems
- **Service Registry** = Central directory of available services
- **Client-Side** = Client queries registry, selects instance
- **Server-Side** = Load balancer queries registry, routes requests
- **Health Checks** = Determine if services are healthy
- **Service Mesh** = Infrastructure layer providing discovery transparently
- **Use service discovery** for microservices, dynamic systems, container orchestration

---

## Related Topics

- [Architecture Patterns](./Architecture-Patterns.md) - Microservices architecture
- [Load Balancing](./LoadBalancing.md) - Load balancing with service discovery
- [API Design](./API-Design.md) - API Gateway and service discovery
- [Circuit Breaker](./Circuit-Breaker.md) - Resilience with service discovery
