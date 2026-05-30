# SLA, SLO, and SLI

A comprehensive guide to Service Level Agreements (SLA), Service Level Objectives (SLO), and Service Level Indicators (SLI) for measuring and managing service reliability and performance.

---

## Table of Contents

1. [What are SLA, SLO, and SLI?](#what-are-sla-slo-and-sli)
2. [Service Level Indicator (SLI)](#service-level-indicator-sli)
3. [Service Level Objective (SLO)](#service-level-objective-slo)
4. [Service Level Agreement (SLA)](#service-level-agreement-sla)
5. [Relationship Between SLI, SLO, and SLA](#relationship-between-sli-slo-and-sla)
6. [Common SLIs and SLOs](#common-slis-and-slos)
7. [Error Budgets](#error-budgets)
8. [Measuring and Monitoring](#measuring-and-monitoring)
9. [Real-World Examples](#real-world-examples)
10. [Interview Tips](#interview-tips)

---

# What are SLA, SLO, and SLI?

## Overview

**SLI, SLO, and SLA** are three related concepts used to define, measure, and agree upon service reliability and performance. They form a hierarchy from measurement (SLI) to objectives (SLO) to agreements (SLA).

**Simple definition:** 
- **SLI** = What you measure (e.g., "99% of requests succeed")
- **SLO** = What you aim for (e.g., "We aim for 99.9% availability")
- **SLA** = What you promise (e.g., "We guarantee 99.9% availability or refund")

These metrics help teams understand service reliability, set targets, and make commitments to users. They are essential for building reliable systems and managing user expectations.

## Quick Comparison

| Term | Definition | Purpose | Audience |
|------|-----------|---------|----------|
| **SLI** | A quantitative measure of service behavior | Measure actual service performance | Engineering teams |
| **SLO** | A target value for an SLI | Define reliability goals | Engineering teams, product |
| **SLA** | A commitment with consequences if not met | Legal/business agreement | Customers, business |

---

# Service Level Indicator (SLI)

## What is SLI?

**Service Level Indicator (SLI)** is a quantitative measure of some aspect of the level of service that is provided. It's a metric that describes how well a service is performing.

**Simple definition:** A measurement that tells you how your service is actually performing, like a speedometer in a car that shows your current speed.

SLIs are the raw measurements that describe service behavior. They answer the question: "How is the service performing right now?"

## Characteristics of Good SLIs

### 1. Measurable

**What does Measurable mean?**

An SLI must be something that can be quantitatively measured, not subjective or qualitative.

**Examples:**
- ✅ Request latency (measurable in milliseconds)
- ✅ Error rate (measurable as percentage)
- ❌ User satisfaction (subjective, not directly measurable)

### 2. Relevant to Users

**What does Relevant mean?**

An SLI should measure something that directly impacts user experience, not just internal metrics.

**Examples:**
- ✅ Request success rate (users care if requests fail)
- ✅ Response time (users care about speed)
- ❌ CPU usage (internal metric, users don't directly care)

### 3. Actionable

**What does Actionable mean?**

An SLI should be something that, when it changes, you can take action to improve it.

**Examples:**
- ✅ P95 latency (can optimize slow requests)
- ✅ Availability (can add redundancy)
- ❌ Number of servers (not directly actionable for users)

## Common SLIs

### 1. Availability

**What is Availability SLI?**

Availability measures the percentage of time a service is operational and able to serve requests.

**How to measure:**
- Count successful requests / Total requests
- Or: Uptime / (Uptime + Downtime)
- Usually measured over a time window (e.g., 30 days)

**Example:**
- Total requests in month: 1,000,000
- Successful requests: 999,000
- Availability SLI: 99.9%

**Formula:**
```
Availability = (Successful Requests / Total Requests) × 100%
```

### 2. Latency

**What is Latency SLI?**

Latency measures how long it takes for a service to respond to requests. Usually measured as percentile (P50, P95, P99).

**How to measure:**
- P50 (median): 50% of requests faster than this
- P95: 95% of requests faster than this
- P99: 99% of requests faster than this

**Example:**
- P50 latency: 100ms (half of requests < 100ms)
- P95 latency: 500ms (95% of requests < 500ms)
- P99 latency: 1000ms (99% of requests < 1000ms)

**Why percentiles?**
- Average can hide outliers
- P95/P99 show worst-case experience
- Better represents user experience

### 3. Error Rate

**What is Error Rate SLI?**

Error rate measures the percentage of requests that result in errors (4xx, 5xx status codes).

**How to measure:**
- Error requests / Total requests
- Usually measured over time window
- Can be broken down by error type

**Example:**
- Total requests: 1,000,000
- Error requests: 1,000 (500 4xx, 500 5xx)
- Error rate: 0.1%

**Formula:**
```
Error Rate = (Error Requests / Total Requests) × 100%
```

### 4. Throughput

**What is Throughput SLI?**

Throughput measures the number of requests a service can handle per unit of time.

**How to measure:**
- Requests per second (RPS)
- Requests per minute (RPM)
- Transactions per second (TPS)

**Example:**
- Service handles 10,000 requests per second
- Throughput SLI: 10,000 RPS

### 5. Freshness (for Data Services)

**What is Freshness SLI?**

Freshness measures how up-to-date data is, important for data pipelines and caches.

**How to measure:**
- Time since last update
- Age of data
- Staleness percentage

**Example:**
- Data updated within last 5 minutes: 99%
- Freshness SLI: 99% of data < 5 minutes old

---

# Service Level Objective (SLO)

## What is SLO?

**Service Level Objective (SLO)** is a target value or range of values for a service level that is measured by an SLI. It's a goal that the service should meet.

**Simple definition:** A target you set for your service performance, like aiming to drive at 60 mph (the SLO) while your speedometer shows your current speed (the SLI).

SLOs define what "good enough" means for your service. They answer the question: "What level of service do we want to provide?"

## Characteristics of Good SLOs

### 1. Based on SLIs

**What does Based on SLIs mean?**

SLOs must be based on measurable SLIs, not vague goals.

**Examples:**
- ✅ "99.9% availability" (based on availability SLI)
- ✅ "P95 latency < 500ms" (based on latency SLI)
- ❌ "Fast response times" (vague, not measurable)

### 2. Realistic and Achievable

**What does Realistic mean?**

SLOs should be achievable with current resources and architecture, not aspirational goals.

**Examples:**
- ✅ "99.9% availability" (achievable with redundancy)
- ❌ "100% availability" (impossible, not realistic)
- ❌ "99.999% availability" (may require excessive resources)

### 3. User-Focused

**What does User-Focused mean?**

SLOs should reflect what users actually care about, not just internal metrics.

**Examples:**
- ✅ "99.9% of requests succeed" (users care about success)
- ✅ "P95 latency < 500ms" (users care about speed)
- ❌ "CPU usage < 80%" (internal metric, users don't care)

### 4. Time-Bounded

**What does Time-Bounded mean?**

SLOs should specify the time window over which they are measured.

**Examples:**
- ✅ "99.9% availability over 30 days"
- ✅ "P95 latency < 500ms over 1 week"
- ❌ "99.9% availability" (no time window specified)

## Common SLO Examples

### Availability SLOs

**Example 1: High Availability Service**
- SLO: 99.9% availability over 30 days
- Means: Service can be down for 43.2 minutes per month
- Use case: Critical business services

**Example 2: Standard Service**
- SLO: 99% availability over 30 days
- Means: Service can be down for 7.2 hours per month
- Use case: Non-critical services

**Example 3: Ultra-High Availability**
- SLO: 99.99% availability over 30 days
- Means: Service can be down for 4.32 minutes per month
- Use case: Mission-critical services

### Latency SLOs

**Example 1: API Service**
- SLO: P95 latency < 500ms over 1 week
- Means: 95% of requests complete in under 500ms
- Use case: User-facing APIs

**Example 2: Database Service**
- SLO: P99 latency < 100ms over 1 week
- Means: 99% of queries complete in under 100ms
- Use case: Database queries

**Example 3: Batch Processing**
- SLO: P50 latency < 5 seconds over 1 day
- Means: Half of batch jobs complete in under 5 seconds
- Use case: Background processing

### Error Rate SLOs

**Example 1: API Service**
- SLO: Error rate < 0.1% over 1 week
- Means: Less than 0.1% of requests result in errors
- Use case: User-facing APIs

**Example 2: Data Pipeline**
- SLO: Error rate < 1% over 1 day
- Means: Less than 1% of pipeline runs fail
- Use case: ETL pipelines

---

# Service Level Agreement (SLA)

## What is SLA?

**Service Level Agreement (SLA)** is a commitment between a service provider and a customer that includes consequences if the SLO is not met. It's a business/legal agreement.

**Simple definition:** A promise you make to customers with penalties if you break it, like a warranty that says "We guarantee 99.9% uptime or we'll refund your money."

SLAs are external-facing commitments with business consequences. They answer the question: "What do we promise our customers?"

## Key Differences: SLO vs SLA

| Aspect | SLO | SLA |
|--------|-----|-----|
| **Purpose** | Internal goal | External commitment |
| **Audience** | Engineering, product | Customers, business |
| **Consequences** | None (internal) | Penalties, refunds, credits |
| **Strictness** | Can be more aggressive | Usually more conservative |
| **Flexibility** | Can adjust based on needs | Contractual, harder to change |

## SLA Components

### 1. Service Level Commitment

**What is Service Level Commitment?**

The specific SLO that is being committed to in the SLA.

**Example:**
- "We guarantee 99.9% availability"
- "We guarantee P95 latency < 500ms"

### 2. Measurement Method

**What is Measurement Method?**

How the service level will be measured and verified.

**Example:**
- "Measured as percentage of successful requests over 30-day rolling window"
- "Measured as P95 latency over 1-week rolling window"

### 3. Consequences

**What are Consequences?**

What happens if the SLA is not met. Usually financial penalties.

**Examples:**
- Service credits (e.g., 10% credit for month)
- Refunds (e.g., full refund if SLA not met)
- Extended service (e.g., free month)
- No consequences (goodwill, reputation)

### 4. Exclusions

**What are Exclusions?**

Situations where the SLA doesn't apply (force majeure, planned maintenance, etc.).

**Examples:**
- Planned maintenance windows
- Force majeure events
- Customer-caused issues
- Third-party service failures

## Common SLA Examples

### Cloud Provider SLA

**Example: AWS EC2 SLA**
- Commitment: 99.99% availability
- Measurement: Monthly uptime percentage
- Consequence: Service credit (10-100% of monthly fee)
- Exclusions: Planned maintenance, force majeure

### SaaS Product SLA

**Example: SaaS Application SLA**
- Commitment: 99.9% availability
- Measurement: Successful requests over 30 days
- Consequence: Service credit or refund
- Exclusions: Planned maintenance, customer errors

### API Service SLA

**Example: Payment API SLA**
- Commitment: 99.95% availability, P95 latency < 500ms
- Measurement: Monthly metrics
- Consequence: Service credits
- Exclusions: Planned maintenance, DDoS attacks

---

# Relationship Between SLI, SLO, and SLA

## The Hierarchy

```
SLA (External Commitment)
    ↓ Based on
SLO (Internal Objective)
    ↓ Measured by
SLI (Actual Measurement)
```

## How They Work Together

### Step 1: Define SLI

**What to do:** Choose what to measure that matters to users.

**Example:**
- SLI: Availability (percentage of successful requests)

### Step 2: Set SLO

**What to do:** Set a target based on the SLI that is achievable and user-focused.

**Example:**
- SLO: 99.9% availability over 30 days

### Step 3: Create SLA

**What to do:** Make a commitment (usually more conservative than SLO) with consequences.

**Example:**
- SLA: Guarantee 99.9% availability or provide service credit

## The Gap: SLO vs SLA

**Why SLO is usually higher than SLA:**

- **SLO:** Internal target (e.g., 99.95%)
- **SLA:** External commitment (e.g., 99.9%)

**Reason:** Buffer between internal target and external promise. If SLO is 99.95% and SLA is 99.9%, you have a 0.05% buffer before breaking SLA.

**Example:**
- Internal SLO: 99.95% (engineering target)
- External SLA: 99.9% (customer promise)
- Buffer: 0.05% (safety margin)

---

# Common SLIs and SLOs

## By Service Type

### Web Application

**SLIs:**
- Availability: Percentage of successful HTTP requests
- Latency: P95 response time
- Error rate: Percentage of 5xx errors

**SLOs:**
- Availability: 99.9% over 30 days
- Latency: P95 < 500ms over 1 week
- Error rate: < 0.1% over 1 week

### API Service

**SLIs:**
- Availability: Percentage of successful API calls
- Latency: P99 response time
- Throughput: Requests per second

**SLOs:**
- Availability: 99.95% over 30 days
- Latency: P99 < 1000ms over 1 week
- Throughput: Handle 10,000 RPS

### Database Service

**SLIs:**
- Availability: Percentage of successful queries
- Latency: P95 query time
- Error rate: Percentage of failed queries

**SLOs:**
- Availability: 99.99% over 30 days
- Latency: P95 < 100ms over 1 week
- Error rate: < 0.01% over 1 week

### Data Pipeline

**SLIs:**
- Freshness: Age of data
- Throughput: Records processed per hour
- Error rate: Percentage of failed pipeline runs

**SLOs:**
- Freshness: 99% of data < 1 hour old
- Throughput: Process 1M records/hour
- Error rate: < 1% over 1 day

---

# Error Budgets

## What is Error Budget?

**Error Budget** is the amount of unreliability a service can tolerate before violating its SLO. It's calculated as 100% minus the SLO.

**Simple definition:** The "allowable downtime" or "allowable errors" before you break your SLO, like a budget for mistakes.

Error budgets help teams make informed decisions about when to prioritize reliability work vs. feature work.

## How Error Budgets Work

### Calculation

**Formula:**
```
Error Budget = 100% - SLO
```

**Example:**
- SLO: 99.9% availability
- Error Budget: 100% - 99.9% = 0.1%
- Over 30 days: 0.1% of 30 days = 43.2 minutes of downtime allowed

### Using Error Budgets

**When Error Budget is High:**
- Team can take risks (deploy new features, experiment)
- Can prioritize feature development
- Can do risky changes

**When Error Budget is Low:**
- Team must focus on reliability
- Defer risky changes
- Prioritize stability over features
- May need to stop deployments

### Example Scenario

**SLO:** 99.9% availability (43.2 minutes downtime/month)

**Month 1:**
- Used: 20 minutes downtime
- Remaining: 23.2 minutes
- Status: ✅ Healthy budget, can take risks

**Month 2:**
- Used: 40 minutes downtime
- Remaining: 3.2 minutes
- Status: ⚠️ Low budget, focus on reliability

**Month 3:**
- Used: 45 minutes downtime
- Remaining: -1.8 minutes (over budget)
- Status: ❌ SLO violated, must focus on reliability

---

# Measuring and Monitoring

## How to Measure SLIs

### 1. Instrumentation

**What is Instrumentation?**

Adding code to measure SLIs in your application.

**Examples:**
- Log request start/end times for latency
- Count successful/failed requests for availability
- Track error responses for error rate

### 2. Metrics Collection

**What is Metrics Collection?**

Collecting SLI measurements into a metrics system.

**Tools:**
- Prometheus (metrics collection)
- StatsD (metrics aggregation)
- CloudWatch (AWS metrics)
- Datadog (monitoring platform)

### 3. Aggregation

**What is Aggregation?**

Combining individual measurements into SLI values.

**Examples:**
- Calculate percentage for availability
- Calculate percentiles for latency
- Calculate averages for throughput

### 4. Visualization

**What is Visualization?**

Displaying SLIs in dashboards for monitoring.

**Tools:**
- Grafana (dashboards)
- CloudWatch Dashboards
- Custom dashboards

## Monitoring SLOs

### SLO Dashboards

**What to show:**
- Current SLI value
- SLO target
- Error budget remaining
- Trend over time
- Alerts when approaching SLO violation

### Alerts

**When to alert:**
- SLI approaching SLO threshold
- Error budget running low
- SLO violation imminent
- SLO violation occurred

**Example:**
- Alert when availability drops below 99.95% (SLO is 99.9%)
- Alert when error budget < 10%
- Alert when SLO violated

---

# Real-World Examples

## Google SRE Book Examples

### Request Availability

**SLI:** Fraction of requests that succeed
**SLO:** 99.9% success rate
**SLA:** 99.9% or service credit

### Request Latency

**SLI:** Distribution of request latencies
**SLO:** P99 latency < 400ms
**SLA:** P99 latency < 500ms (more conservative)

## AWS Service SLAs

### EC2 SLA

**SLO:** 99.99% availability
**Measurement:** Monthly uptime percentage
**Consequence:** 10-100% service credit

### S3 SLA

**SLO:** 99.99% availability
**Measurement:** Monthly uptime percentage
**Consequence:** Service credit

## Netflix Examples

### Streaming Service

**SLI:** Video start success rate
**SLO:** 99.9% of videos start within 5 seconds
**Focus:** User experience, not just uptime

---

# Interview Tips

## Common Questions

**Q: What is the difference between SLI, SLO, and SLA?**
- **SLI:** Quantitative measure of service behavior (what you measure)
- **SLO:** Target value for an SLI (what you aim for)
- **SLA:** Commitment with consequences (what you promise)
- SLI measures, SLO targets, SLA commits

**Q: What makes a good SLI?**
- Measurable (quantitative, not subjective)
- Relevant to users (impacts user experience)
- Actionable (can take action when it changes)
- Examples: Availability, latency, error rate

**Q: How do you set SLOs?**
- Based on SLIs (measurable metrics)
- Realistic and achievable (not aspirational)
- User-focused (what users care about)
- Time-bounded (specify measurement window)
- Example: "99.9% availability over 30 days"

**Q: What is an error budget?**
- Amount of unreliability allowed before SLO violation
- Calculated as 100% minus SLO
- Helps prioritize reliability vs. features
- When high: can take risks, when low: focus on reliability

**Q: Why is SLO usually higher than SLA?**
- SLO is internal target (e.g., 99.95%)
- SLA is external commitment (e.g., 99.9%)
- Buffer between target and promise
- Provides safety margin before SLA violation

**Q: How do you measure availability?**
- Count successful requests / Total requests
- Or: Uptime / (Uptime + Downtime)
- Usually over time window (e.g., 30 days)
- Example: 999,000 successful / 1,000,000 total = 99.9%

**Q: What are common SLIs for a web service?**
- Availability: Percentage of successful requests
- Latency: P95/P99 response time
- Error rate: Percentage of failed requests
- Throughput: Requests per second

## Key Points to Remember

- **SLI** = What you measure (availability, latency, error rate)
- **SLO** = What you aim for (target value for SLI)
- **SLA** = What you promise (commitment with consequences)
- **Error Budget** = Allowable unreliability (100% - SLO)
- **SLO > SLA** = Buffer between target and promise
- **Good SLIs** = Measurable, relevant, actionable
- **Use SLI/SLO/SLA** for reliability management, user expectations, prioritization

---

## Related Topics

- [Availability](./Availability.md) - Availability concepts and metrics
- [Monitoring & Observability](./Monitoring-Observability.md) - Measuring and monitoring SLIs
- [Architecture Patterns](./Architecture-Patterns.md) - Building reliable systems
- [Circuit Breaker](./Circuit-Breaker.md) - Resilience patterns for meeting SLOs
