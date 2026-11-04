"""Process health endpoint; external dependencies are not checked."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report that the application can serve HTTP requests."""
    return {"status": "ok", "service": "digitalent-ai"}
