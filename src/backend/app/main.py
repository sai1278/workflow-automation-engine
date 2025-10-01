# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

# Use absolute imports
from app.config import get_settings
from app.logger import get_logger
from app.api import router as api_router


def create_app() -> FastAPI:
    # Load settings
    settings = get_settings()

    # Create FastAPI app with metadata
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Attach settings and logger to app state
    app.state.settings = settings
    app.state.logger = get_logger("app")

    # Security middlewares
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
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
    async def health():
        return {"status": "ok"}

    # Global error handling
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

    # Lifecycle events
    @app.on_event("startup")
    async def startup_event():
        app.state.logger.info(
            f"🚀 {settings.app_name} started in {settings.environment} mode"
        )

    @app.on_event("shutdown")
    async def shutdown_event():
        app.state.logger.info("🛑 Application shutdown")

    return app


# 👇 Expose default app instance for pytest/uvicorn
app = create_app()
