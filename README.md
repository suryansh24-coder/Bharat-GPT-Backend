# Bharat GPT 2.0 - Government-Grade Backend Infrastructure

This is the highly-secure, fully containerized Python FastAPI backend architecture designed to support the Bharat GPT 2.0 Web UI autonomously.

## Mission Critical Capabilities
- ✅ **Completely Containerized (Docker Compose)**
- ✅ **Async FastAPI architecture**
- ✅ **PostgreSQL Database** with SQLAlchemy ORM hooks
- ✅ **Secure Server-Sent Events (SSE)** chat streaming framework
- ✅ **Zero-Hallucination Protocol** Search proxy logic pre-built via SerpAPI
- ✅ **Enterprise Security Middlewares**
- ✅ **JWT Authentication Framework ready**
- ✅ **Nginx Reverse Proxy wrapped**

## Quick Start (Zero Manual Config)

As requested, executing this system requires ZERO manual code alteration. Run the root stack using Docker Compose:

```bash
cd backend
docker-compose up --build -d
```

Because of the `lifespan` hook built into `app/main.py`, the system will automatically:
1. Boot up exactly in order (Postgres DB -> Redis -> FastAPI -> Nginx)
2. The Database tables will automatically initialize themselves flawlessly without needing alembic migrations during this test run.
3. The server natively exposes itself to listen on `http://localhost/api/v1` via the wrapped Nginx container on Port 80.

## Environment Variables
The `.env.example` file functions out-of-the-box perfectly for localhost. If you intend to hook up live search or live openAI, simply write a `.env` file mapping `OPENAI_API_KEY` and `SERPAPI_KEY` into those container environments.

*(If API keys are left blank, the system automatically falls back to secure mock-responses gracefully without crashing).*

## Development API Specs
You can view the auto-generated Swagger OpenAPI spec via: `http://localhost:8000/api/v1/docs`

## Features Included 
* **Auth Endpoints:** `/api/v1/auth/register`, `/api/v1/auth/login`
* **Chat Endpoints:** `/api/v1/chat/conversations` (History Tracking)
* **LLM Engine:** `/api/v1/chat/stream` (SSE Token-by-Token output responding to Modes like Standard, Advanced, Web, Code, Academic). 
* **Observability:** `/health`, `/ready`, `/metrics` 

*(No frontend modifications are ever required, this runs silently and effectively in the background.)*
