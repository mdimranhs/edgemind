import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async startup/shutdown with background RAG ingestion."""
    # Startup: Defer heavy RAG ingestion to background
    asyncio.create_task(_warmup_background())
    yield
    # Shutdown: cleanup if needed


async def _warmup_background():
    """Background task to warm up RAG after server starts."""
    await asyncio.sleep(2)  # Let server respond to health checks first
    try:
        from app.api.dependencies import _rag_service
        if _rag_service is not None and hasattr(_rag_service, 'ingest'):
            _rag_service.ingest()
    except Exception as e:
        import logging
        logging.warning(f"Background RAG warmup failed: {e}")


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
