# Playbook — Production Incident Response

## When to use this
Follow this playbook whenever a production service is degraded, down, or behaving unexpectedly.
This is the standard procedure — do not skip steps even if you think you know the cause.

---

## Step 1 — Acknowledge and communicate (first 5 minutes)

1. Post in the team incident channel: "Investigating issue with [service]. ETA for update: 10 min."
2. Assign one person as Incident Commander (IC) — they own communication.
3. Do not start fixing before you have acknowledged. Others need to know it is being handled.

---

## Step 2 — Assess impact

```bash
# Check if pods are running
kubectl get pods -l app=<service-name>

# Check recent events
kubectl describe deployment/<service-name> | tail -30

# Check error rate from logs (last 5 minutes)
kubectl logs -l app=<service-name> --since=5m | grep -i error | wc -l
```

Determine:
- Is the service completely down or degraded?
- Which users / tenants are affected?
- When did it start? Check deployment history.

```bash
kubectl rollout history deployment/<service-name>
```

---

## Step 3 — Identify root cause

Common root causes in order of likelihood:

1. **Bad deployment** — check if a release happened recently
   ```bash
   kubectl rollout history deployment/<service-name>
   ```
2. **Pod crash / OOM** — check pod logs and resource usage
   ```bash
   kubectl logs <pod-name> --previous
   kubectl top pods -l app=<service-name>
   ```
3. **Downstream dependency down** — DB, external API, message queue
4. **Config / env var change** — someone changed a secret or configmap
5. **Traffic spike** — check HPA and request metrics

---

## Step 4 — Mitigate (stop the bleeding)

If a bad deployment caused it — rollback immediately, investigate later:
```bash
kubectl rollout undo deployment/<service-name>
kubectl rollout status deployment/<service-name>
```

If pods are OOM — scale up temporarily:
```bash
kubectl scale deployment/<service-name> --replicas=5
```

If a downstream dependency is down — enable fallback mode if available, or redirect traffic.

**Post mitigation**: confirm service is recovering:
```bash
kubectl get pods -l app=<service-name>   # all Running
curl http://<service-url>/health          # returns 200
```

---

## Step 5 — Communicate resolution

Post in incident channel: "Service restored at [time]. Root cause: [brief summary]. Follow-up: [ticket link]."

---

## Step 6 — Post-incident review (within 48 hours)

Write a brief post-mortem covering:
- What happened (timeline)
- Root cause
- How it was detected
- How it was resolved
- What we will do to prevent recurrence

File the post-mortem as a Jira ticket tagged `post-mortem`.
