# app/api.py
from fastapi import APIRouter, Request, Response, HTTPException, status
from pydantic import BaseModel, constr, conint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.config import get_settings
from app.logger import get_logger
from app.metrics import DATA_REQUESTS

router = APIRouter()

logger = get_logger("api")
settings = get_settings()


# ---------------- Models ----------------
class DataPayload(BaseModel):
    name: constr(min_length=1, max_length=100)
    value: conint(ge=0, le=1_000_000)
    metadata: dict | None = None


# ---------------- Endpoints ----------------
@router.get("/health")
async def health(request: Request):
    """Health check endpoint"""
    request.app.state.logger.info("health_check")
    return {"status": "ok"}


@router.get("/metrics")
async def metrics():
    """Export Prometheus metrics (all global registry)"""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get("/info")
async def info(request: Request):
    """Application info endpoint"""
    s = request.app.state.settings
    return {
        "name": s.app_name,
        "version": s.version,
        "environment": s.environment,
    }


@router.get("/data")
async def get_data(request: Request):
    """Example GET business endpoint"""
    cid = getattr(request.state, "correlation_id", "N/A")
    request.app.state.logger.info(
        "data_requested", extra={"endpoint": "/data", "correlation_id": cid}
    )
    DATA_REQUESTS.inc()

    # Example static payload (replace with DB lookup later)
    return {"data": {"message": "Sample data response"}}


@router.post("/data", status_code=status.HTTP_201_CREATED)
async def post_data(payload: DataPayload, request: Request):
    """Receive and validate data payload"""
    cid = getattr(request.state, "correlation_id", "N/A")

    # Business validation
    if payload.name.strip() == "":
        raise HTTPException(status_code=400, detail="Name must not be empty")

    # Log and increment metrics
    request.app.state.logger.info(
        "data_posted",
        extra={"payload": payload.dict(), "correlation_id": cid},
    )
    DATA_REQUESTS.inc()

    # Return accepted payload (you can replace with DB save)
    return {"status": "accepted", "data": payload.dict()}
