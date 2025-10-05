# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
import time

from app.config import get_settings
from app.logger import get_logger
from app.api import router as api_router

# ---------------- Metrics (singletons) ----------------
REQUEST_COUNTER = Counter("app_requests_total", "Total requests")
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency in seconds")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.state.settings = settings
    app.state.logger = get_logger("app")

    # ---------------- Security Middlewares ----------------
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---------------- Rate Limiting ----------------
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ---------------- Metrics Middleware ----------------
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        REQUEST_COUNTER.inc()
        REQUEST_LATENCY.observe(time.time() - start_time)
        return response

    # Instrument app for Prometheus
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")

    # ---------------- Routers ----------------
    app.include_router(api_router)

    # Root endpoint
    @app.get("/", response_class=JSONResponse)
    async def root():
        return {
            "message": f"{settings.app_name} is running!",
            "version": settings.version,
            "endpoints": [route.path for route in app.routes if route.path != "/"],
        }

    # Health check endpoint
    @app.get("/health", response_class=JSONResponse)
    @limiter.limit("5/minute")
    async def health(request: Request):
        return {"status": "ok"}

    # ---------------- Error Handlers ----------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        app.state.logger.error(f"Unhandled error: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        app.state.logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    # ---------------- Lifecycle Events ----------------
    @app.on_event("startup")
    async def startup_event():
        app.state.logger.info(
            f"🚀 {settings.app_name} started in {settings.environment} mode"
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        app.state.logger.info("🛑 Application shutdown")

    return app


# Expose default app instance for uvicorn/pytest
app = create_app()
