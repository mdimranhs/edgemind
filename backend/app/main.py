from contextlib import asynccontextmanager
import logging
import re
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.dependencies import init_services
from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger("edgemind.access")

MAX_BODY_BYTES = 100 * 1024  # 100 KB limit for chat requests


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-warm models and FAISS index so the first request experiences zero cold start
    logger.info("Initializing EdgeMind services on startup...")
    start = time.perf_counter()
    try:
        init_services()
    except Exception:
        logger.exception("EdgeMind service initialization failed")
        raise
    logger.info("EdgeMind services initialized in %.2fs", time.perf_counter() - start)
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

# Configure CORS for portfolio frontend
origins = (
    ["*"]
    if settings.cors_allowed_origins.strip() == "*"
    else [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def observability_and_limits_middleware(request: Request, call_next):
    # Guard against oversized payloads
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            body_size = int(content_length)
        except ValueError:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid Content-Length header."},
            )
        if body_size < 0 or body_size > MAX_BODY_BYTES:
            return JSONResponse(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                content={"detail": "Request payload exceeds maximum allowed size (100KB)."},
            )


    # Privacy-safe request correlation
    supplied_request_id = request.headers.get("x-request-id", "")
    request_id = (
        supplied_request_id
        if re.fullmatch(r"[A-Za-z0-9._-]{1,64}", supplied_request_id)
        else str(uuid.uuid4())
    )
    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id

    # Privacy-conscious structured logging (never logs prompt contents or credentials)
    logger.info(
        "request_id=%s method=%s path=%s status=%d duration_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


app.include_router(api_router)


@app.get("/")
async def root():
    """Return a lightweight service welcome message."""
    return {"message": "Welcome to EdgeMind 🚀"}

