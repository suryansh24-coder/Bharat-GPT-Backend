# System Architecture Document (SAD)

## 1. Executive Summary
This document outlines the architectural composition for Bharat GPT 2.0 Backend, designed as an enterprise-grade AI execution platform.

## 2. Platform Architecture
* **Frontend**: HTML5/Vanilla JS interface (Client Layer)
* **API Gateway / Proxy**: Nginx acting as reverse proxy over port 80/443 mapping strictly to the internal API network.
* **Core Application Engine**: Asynchronous FastAPI executing Python 3.11.
* **Database**: PostgreSQL 15 accessed via high-concurrency `asyncpg` combined with SQLAlchemy.
* **In-Memory Cache & Limiting**: Redis 7 powering Celery tasks, Session State, and `fastapi-limiter` IP/User quotas.
* **Monitoring Layer**: Prometheus `/metrics` exposition connected via Grafana JSON configs.

### Data Flow
1. User transmits standard payload (`/api/v1/chat/stream`).
2. Nginx routes to Uvicorn worker.
3. FastAPILimiter checks Redis for DDOS state.
4. Security middleware validates injection payloads and sanitizes context via `bleach`.
5. Request is routed locally or proxied to sub-services (SerpAPI / OpenAI).
6. Response yields via SSE (Server-Sent Events) dynamically bypassing chunked encoding delays.
