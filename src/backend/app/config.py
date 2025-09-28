# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "workflow-automation-engine"
    environment: str = "development"
    version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

def get_settings() -> Settings:
    return Settings()
