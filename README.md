# Bharat GPT - Backend Infrastructure

![Version](https://img.shields.io/badge/version-2.0.0-darkgreen)
![Backend](https://img.shields.io/badge/backend-FastAPI%20%7C%20Flask-blue)
![Database](https://img.shields.io/badge/database-PostgreSQL-informational)
![Cache](https://img.shields.io/badge/cache-Redis-red)
![Containerized](https://img.shields.io/badge/container-Docker-blueviolet)
![Status](https://img.shields.io/badge/status-production--grade-success)

---

# 🧠 Overview

The **Bharat GPT 2.0 Backend** is architected in two distinct layers:

1. ⚡ **Lightweight AI Search Proxy (Flask)**
2. 🏢 **Production-Grade Distributed Backend (FastAPI)**

This dual-structure enables:
- Rapid prototyping
- Enterprise scalability
- AI integration
- Secure API architecture
- Containerized deployment
- Observability & monitoring

---

# 🏗 System Architecture
                     ┌──────────────────────────┐
                     │        Frontend SPA      │
                     │  (Vanilla JS + Tailwind) │
                     └─────────────┬────────────┘
                                   │
                                   ▼
                ┌─────────────────────────────┐
                │        Reverse Proxy        │
                │            Nginx            │
                └─────────────┬───────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
 ⚡ Lightweight Proxy                    🏢 Production API
     Flask Server                          FastAPI Server
   (backend.py)                           (/backend/app)

            ▼                                   ▼
     SerpAPI + OpenAI                    PostgreSQL + Redis
                                          Celery + Prometheus



                                          
---

# ⚡ 1️⃣ Lightweight Proxy Backend (backend.py)

## 🎯 Purpose

A fast, minimal Flask-based AI search proxy designed for:

- Secure API key protection
- AI-powered summarization
- Search aggregation
- Quick deployment
- Hackathon-ready testing

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3 |
| Framework | Flask |
| CORS | flask-cors |
| HTTP Client | requests |
| AI Model | OpenAI (gpt-3.5-turbo) |
| Search API | SerpAPI |
| Cache | In-memory dictionary |

---

## 🔁 Core Workflow

1. Exposes endpoint:

2. Checks in-memory cache (`CACHE`)
   - TTL: 600 seconds
   - Reduces API cost

3. If cache miss:
   - Fetches search results from SerpAPI
   - Extracts:
     - Title
     - Snippet
     - Link
   - Special handling for Wikipedia references

4. Constructs **Strict Anti-Hallucination Prompt**
5. Sends structured prompt to OpenAI
6. Returns summarized, verified output

---

## 🔒 Security Model

- API keys stored server-side
- No frontend exposure
- Controlled CORS policy
- Basic cache protection

---

## 🌐 Deployment

Runs locally via:

Default:

---

# 🏢 2️⃣ Production-Grade Backend (/backend Directory)

This is the enterprise-level architecture built for scalability and long-term deployment.

---

# 🛠 Core Technology Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ASGI Server | Uvicorn + Gunicorn |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| ORM | SQLAlchemy 2.0 |
| Async Driver | asyncpg |
| Authentication | JWT (python-jose) |
| Password Hashing | passlib[bcrypt] |
| Background Tasks | Celery |
| Containerization | Docker |
| Reverse Proxy | Nginx |
| Monitoring | Prometheus |
| Testing | pytest |

---

# 🧩 Architecture Philosophy

This backend follows a **Clea/backend
├── app
│ ├── main.py
│ ├── auth/
│ ├── chat/
│ ├── compliance/
│ ├── models/
│ ├── schemas/
│ ├── services/
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txtn Modular Service Architecture**:

---

# ⚙️ FastAPI Application Logic

## 🔄 Lifespan Validation

At boot-time:

- Verifies environment variables
- Validates API keys
- Performs mock OpenAI test request
- Ensures system readiness before serving traffic

---

# 🧠 AI Layer

| Feature | Implementation |
|----------|----------------|
| Primary Model | gpt-4o-mini |
| Search Integration | SerpAPI |
| Anti-hallucination prompting | Strict structured prompts |
| Async API Calls | Fully non-blocking |

---

# 🔐 Authentication & Security

- JWT Token-based authentication
- Bcrypt password hashing
- Rate limiting via Redis
- CORS middleware enforcement
- Security logging middleware

---

# ⚡ Performance Enhancements

### Middlewares

- ✅ GZip Compression (>1000 bytes)
- ✅ SLA Tracking
- ✅ Custom logging
- ✅ Health state detection

---

# 📊 Observability & Monitoring

| Endpoint | Purpose |
|-----------|----------|
| `/health` | Basic service check |
| `/ready` | Kubernetes readiness check |
| `/metrics` | Prometheus metrics export |

Designed for:
- Docker Swarm
- Kubernetes
- Cloud orchestration
- Grafana dashboards

---

# 🧠 Background Task Processing

Uses **Celery** for:

- Deferred AI jobs
- Logging pipelines
- Data compliance checks
- Scalable async operations

---

# 🐳 Containerized Infrastructure

Managed via:

- Dockerfile
- docker-compose.yml

Services:
- FastAPI App
- PostgreSQL
- Redis
- Nginx Reverse Proxy

---

# 🔥 Rate Limiting & Anti-Abuse

- fastapi-limiter
- Redis-based throttling
- DDoS prevention
- API quota control

---

# 📈 Enterprise Capabilities

✔ Horizontal scalability  
✔ Async-first architecture  
✔ Observability ready  
✔ Production database integration  
✔ Container orchestration  
✔ Secure authentication  
✔ AI-safe prompting logic  
✔ Compliance routing  

---

# 🧪 Testing & Reliability

- pytest
- pytest-asyncio
- Structured validation via Pydantic
- SLA uptime tracking

---

# 🚀 Deployment Strategy

### Local Development

---

### Production

- Nginx reverse proxy
- Gunicorn worker pool
- Redis cache layer
- PostgreSQL persistent storage

---

# 🏆 Why Two Backends?

| Lightweight Proxy | Production Backend |
|------------------|--------------------|
| Rapid prototype | Enterprise deployment |
| Simple caching | Distributed caching |
| Minimal setup | Containerized stack |
| Flask | FastAPI |
| Hackathon-ready | Investor-ready |

---

# 🎯 Summary

Bharat GPT 2.0 Backend is architected with:

- Prototype agility
- Enterprise scalability
- AI reliability
- Secure authentication
- Full container orchestration
- Observability & monitoring

It transitions seamlessly from a hackathon MVP to a production-grade AI infrastructure.

---

# 👨‍💻 Author

**Suryansh Tiwari**  
AI Systems Engineer | Backend Architect  
Creator of Bharat GPT  

---

# 📜 License

License  
Open for innovation and contribution.
