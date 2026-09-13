from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Do not accept traffic until RAG and the provider are warm."""
    from app.api.dependencies import initialize_for_startup

    await initialize_for_startup()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - ultra-lightweight for keepalive."""
    return {"message": "Welcome to EdgeMind 🚀"}


@app.get("/ping")
async def ping():
    """Lightweight keepalive endpoint - no dependencies loaded."""
    return {"status": "ok"}


@app.get("/warmup")
async def warmup():
    """Re-trigger provider warmup.

    Hit by keepalive/cron to keep the HuggingFace model replica warm between
    real requests, so /chat doesn't pay the model-load cost.
    """
    from app.api import dependencies as deps
    await deps.warm_provider()
    return {"status": "warmed"}
