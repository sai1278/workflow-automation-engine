from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # App info
    app_name: str = "workflow-automation-engine"
    version: str = "0.1.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Server info
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging
    log_level: str = "INFO"

    # For TrustedHostMiddleware
    allowed_hosts: list[str] = ["*"]

    # For CORS middleware
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()
