from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

app.include_router(api_router)


@app.get("/")
async def root():
    """Return a lightweight service welcome message."""
    return {"message": "Welcome to EdgeMind 🚀"}
