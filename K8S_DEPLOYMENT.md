# Kubernetes Deployment Blueprint (National Scale)

## 1. High Availability Architecture
Bharat GPT 2.0 is designed for multi-region active-active deployments.
The manifest files inside `backend/k8s/` provide the foundational footprint to boot this into EKS (AWS), GKE (Google Cloud), or self-hosted bare metal servers.

## 2. Stateless API Scaling
The `FastAPI` (uvicorn) containers are entirely stateless. Context windows and memory states are passed via Client/Postgres hooks and throttled securely by Redis. This means horizontal scaling is unrestrained.

The active **HorizontalPodAutoscaler (HPA)** automatically watches:
- `cpu_average_utilization`: Mapped at `70%`. If requests spike, K8s triggers instant pod duplication up to a hard cap of 50 replica sets per zone, guaranteeing Zero-Downtime on load.

## 3. Database Persistence
PostgreSQL is scaled via a **StatefulSet** (`postgres-statefulset.yaml`).
- Storage is pinned to a persistent volume claim block ensuring 50GB active rapid-access mounts.
- *Note: In Government Production*, replace this single-replica StatefulSet with a managed Regional Aurora / CloudSQL instance using synchronous multi-zone replicas. Auto-failover logic handles node deaths beneath the application layer.

## 4. Reverse Proxying ingress
The NGINX ingress (`ingress.yaml`) intercepts edge traffic on `api.bharatgpt.local`. Crucially, Server-Sent Events (SSE) logic has been deeply protected by disabling connection limits and chunked-encoding specifically on Nginx, allowing real-time LLM typing streams.
