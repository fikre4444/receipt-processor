import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Automated Receipt Processor"
    API_V1_STR: str = "/api/v1"
    TESSERACT_PATH: str | None = None

    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str = "google/gemma-2-27b-it:free"
    
    SITE_URL: str = "http://localhost:8000"
    SITE_NAME: str = "ReceiptProcessor"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()