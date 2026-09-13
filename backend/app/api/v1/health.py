from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import is_ready, startup_error

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "EdgeMind API"
    }


@router.get("/ready")
async def ready():
    """Readiness check for monitors and load balancers."""
    if not is_ready():
        detail = startup_error() or "Service is still warming up"
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
    return {"status": "ready", "service": "EdgeMind API"}
