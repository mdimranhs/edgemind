from fastapi import APIRouter, HTTPException, status

from app.api.dependencies import is_ready

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
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is still warming up",
        )
    return {"status": "ready", "service": "EdgeMind API"}
