# Python Service Deployment Guide

## Overview
This guide covers how to deploy a Python FastAPI service to our Kubernetes cluster.
Use these steps whenever you need to release a new version or troubleshoot a failing pod.

## Prerequisites
- Docker installed and logged in to the registry
- kubectl configured with cluster access
- Service code committed and merged to main

---

## Steps

### 1. Build and Push Docker Image
```
docker build -t my-service:latest .
docker tag my-service:latest registry.company.com/my-service:v1.0.0
docker push registry.company.com/my-service:v1.0.0
```

### 2. Deploy to Kubernetes
```
kubectl set image deployment/my-service my-service=registry.company.com/my-service:v1.0.0
kubectl rollout status deployment/my-service
```
Wait for "successfully rolled out" before proceeding.

### 3. Verify the Deployment
```
kubectl get pods -l app=my-service
kubectl logs -l app=my-service --tail=50
```

---

## Common Issues

### Pod in CrashLoopBackOff
The pod keeps restarting. Almost always one of three causes:
- Missing environment variable — check `kubectl describe pod <pod-name>` for errors
- Wrong port — make sure Dockerfile EXPOSE and the app's bind port match
- Dependency error on startup — check logs with `kubectl logs <pod-name> --previous`

### Pod in ImagePullBackOff
Kubernetes cannot pull the image. Check:
- Image name and tag are exactly correct
- Registry credentials are configured: `kubectl describe pod <pod-name>`

### Rollback if Something Breaks
```
kubectl rollout undo deployment/my-service
kubectl rollout status deployment/my-service
```

---

## Health Check
After any deployment, verify the service is healthy:
```
kubectl get pods -l app=my-service   # all pods should be Running
curl http://service-url/health        # should return 200
```
