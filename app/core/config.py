import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Money Saver API"
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration (Render uses PORT=10000, local development uses 8000)
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        env="CORS_ORIGINS"
    )
    
    @field_validator('CORS_ORIGINS')
    @classmethod
    def parse_cors_origins(cls, v: str) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Email Configuration (Gmail SMTP)
    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    EMAIL_FROM: Optional[str] = Field(default=None, env="EMAIL_FROM")
    EMAIL_FROM_NAME: str = Field(default="Money Saver App", env="EMAIL_FROM_NAME")
    EMAIL_USE_TLS: bool = Field(default=True, env="EMAIL_USE_TLS")
    
    # Email Feature Settings
    EMAIL_ENABLED: bool = Field(default=True, env="EMAIL_ENABLED")
    REMINDER_DAY: str = Field(default="monday", env="REMINDER_DAY")
    REMINDER_HOUR: int = Field(default=9, env="REMINDER_HOUR")
    REMINDER_MINUTE: int = Field(default=0, env="REMINDER_MINUTE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()