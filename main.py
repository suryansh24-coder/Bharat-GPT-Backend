from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.database import init_db
from app.middleware.security import RequestLoggingMiddleware
from app.middleware.sla import SLATrackingMiddleware
from app.routes import auth, chat, compliance

import sys
import os
from openai import AsyncOpenAI
from app.utils.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # SECTION 2 & 5: VERIFY ENVIRONMENT VARIABLES & STARTUP VALIDATION
    api_key = os.environ.get("OPENAI_API_KEY", settings.OPENAI_API_KEY)
    if not api_key:
        logger.error("FatalError: OPENAI_API_KEY missing - Server will continue to boot but LLM requests will fail gracefully")
    elif len(api_key) < 20:
        logger.error("FatalError: OPENAI_API_KEY invalid - Server will continue to boot but LLM requests will fail gracefully")
    else:
        masked_key = api_key[:6] + "..."
        logger.info(f"Using OPENAI_API_KEY spanning: {masked_key}")
        logger.info("Provider: OpenAI | Primary Model: gpt-4o-mini")

    # SECTION 3: VALIDATE MODEL CALL
    try:
        from openai import AsyncOpenAI
        test_client = AsyncOpenAI(api_key=api_key, timeout=10.0)
        await test_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        logger.info("Startup Validation: LLM API Connection Successful.")
    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "unauthorized" in err_str:
            logger.error("FatalError: Invalid API key")
        elif "429" in err_str or "quota" in err_str:
            logger.error("FatalError: Quota exceeded")
        elif "404" in err_str or "invalid model" in err_str:
            logger.error("FatalError: Invalid model name")
        elif "timeout" in err_str:
            logger.error("FatalError: Network failure")
        else:
            logger.error(f"Error: Startup LLM Validation Failed - {e}")
            
    # Do not sys.exit(1) so the FastAPI server stays online to stream the error back to the UI

    # Initialize DB (Auto-migration for this setup)
    await init_db()
    
    # Initialize Redis for Rate Limiting
    redis_conn = redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_conn)
    
    yield
    
    # Cleanup on shutdown
    await FastAPILimiter.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# High-Performance Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom Security Logging Middleware
app.add_middleware(RequestLoggingMiddleware)

# SLA Distributed Tracing Middleware
app.add_middleware(SLATrackingMiddleware)

# Expose Prometheus Metrics
Instrumentator().instrument(app).expose(app)

# API Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])

# Observability endpoints
@app.get("/health", tags=["system"])
async def health_check():
    return {"status": "ok"}

@app.get("/ready", tags=["system"])
async def readiness_check():
    # Extend to ping db & redis in prod
    return {"status": "ready"}
    
@app.get("/metrics", tags=["system"])
async def metrics():
    # Stub for prometheus
    return {"status": "metrics_available"}
