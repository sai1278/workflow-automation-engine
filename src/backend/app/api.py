from fastapi import APIRouter, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .config import get_settings
from .logger import get_logger
from .metrics import DATA_REQUESTS

router = APIRouter()

logger = get_logger("api")
settings = get_settings()

@router.get("/health")
async def health():
    return {"status": "ok"}

@router.get("/metrics")
async def metrics():
    # Export prometheus metrics (all global registry)
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

@router.get("/info")
async def info(request: Request):
    s = request.app.state.settings
    return {
        "name": s.app_name,
        "version": s.version,
        "environment": s.environment
    }

@router.get("/data")
async def get_data(request: Request):
    # Example business endpoint stub
    request.app.state.logger.info("data_requested", extra={"endpoint": "/data"})
    DATA_REQUESTS.inc()
    # placeholder payload
    return {"data": [], "meta": {"note": "stub"}}
