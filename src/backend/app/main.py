# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Use absolute imports
from app.config import get_settings
from app.logger import get_logger
from app.api import router as api_router


def create_app():
    # Load settings
    settings = get_settings()

    # Create FastAPI app with metadata
    app = FastAPI(title=settings.app_name, version=settings.version)

    # Attach settings and logger to app state
    app.state.settings = settings
    app.state.logger = get_logger("app")

    # Include API router
    app.include_router(api_router)

    # Root endpoint
    @app.get("/", response_class=JSONResponse)
    async def root():
        return {
            "message": f"{settings.app_name} is running!",
            "version": settings.version,
            "endpoints": [route.path for route in app.routes if route.path != "/"]
        }

    return app


# Create app instance
app = create_app()
