"""
Application configuration management.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./aislice.db"
    DATABASE_URL_ASYNC: str = "sqlite+aiosqlite:///./aislice.db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Configuration
    OPENAI_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    USE_LOCAL_LLM: bool = True
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Application
    APP_NAME: str = "AI-Slice"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # VIP Settings
    VIP_SPENDING_THRESHOLD: float = 100.0
    VIP_ORDER_THRESHOLD: int = 3
    VIP_DISCOUNT_PERCENTAGE: float = 5.0
    VIP_FREE_DELIVERY_FREQUENCY: int = 3
    
    # Reputation Settings
    WARNING_THRESHOLD_DEREGISTER: int = 3
    WARNING_THRESHOLD_VIP_DEMOTION: int = 2
    BLACKLIST_REPUTATION_THRESHOLD: int = -50
    VIP_REPUTATION_THRESHOLD: int = 100
    
    # Performance Rules
    CHEF_LOW_RATING_THRESHOLD: float = 2.0
    CHEF_HIGH_RATING_THRESHOLD: float = 4.0
    COMPLAINTS_FOR_DEMOTION: int = 3
    COMPLIMENTS_FOR_BONUS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

