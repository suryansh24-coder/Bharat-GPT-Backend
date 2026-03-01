from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "Bharat GPT 2.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "super_secret_government_grade_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30 # 30 days securely rotated
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:secure_password@db:5432/bharatgpt"
    REDIS_URL: str = "redis://redis:6379/0"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "dummy_key")
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "dummy_key")
    
    ALLOWED_ORIGINS: str = "http://localhost,http://localhost:80,http://127.0.0.1,*"

    @property
    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
             return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
