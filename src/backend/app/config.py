from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "workflow-automation-engine"
    environment: str = "development"
    version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # For TrustedHostMiddleware
    allowed_hosts: list[str] = ["*"]
    
    # For CORS middleware
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

def get_settings() -> Settings:
    return Settings()
