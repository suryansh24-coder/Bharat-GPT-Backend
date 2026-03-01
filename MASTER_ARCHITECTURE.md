# BHARAT GPT 2.0 - MASTER ARCHITECTURE OVERVIEW

## Phase Components
* **Phase 1: Foundational Framework.** FastAPI async core routing OpenAI LLM structures. PostgreSQL memory banks storing User / Chat History.
* **Phase 2: Enterprise Hardening.** Nginx reverse proxy wrapped. SerpAPI zero-hallucination hooks enabled. Multi-tenancy structures created. Bleach string sanitization deployed.
* **Phase 3: National Kubernetes Scaling.** Redis clustering prepared. HPA (Horizontal Pod Autoscalers) enabled. CI/CD Blue/Green routines mapped via Github. 
* **Finalization:** GZip compression applied. End-to-End SLA Metrics tracked globally.

## The Streaming Loop (Zero-Latency Guarantee)
To achieve sub-1.0 second native generation:
1. Client establishes Server-Sent Event (SSE) handshake asynchronously.
2. FastAPI intercepts stream chunk payload via `generator`.
3. AI Service (`services/llm.py`) calculates chunk delta, emits string.
4. Nginx proxy ignores chunk-binding (proxy_buffering off), transmitting token-by-token natively directly back into UI Javascript parser.

## Multi-Tenancy Architecture
1. Internal `Organization` maps API_KEY limits, usage restrictions natively.
2. `User` accounts inherently bound to Organization overrides preventing internal bill shock.
3. System Audit Logger captures metadata correlating User Email + Output Content + Confidence Scores feeding native BI dashboards safely.
