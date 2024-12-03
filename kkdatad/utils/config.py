from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Database settings
    CC_DATABASE_HOST: str = os.getenv("CC_DATABASE_HOST", "localhost")
    CC_DATABASE_PORT: int = int(os.getenv("CC_DATABASE_PORT", "8123"))
    CC_DATABASE_PASSWORD: str = os.getenv("CC_DATABASE_PASSWORD", "")
    
    # MySQL settings
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    
    # Redis settings
    REDIS_DATABASE_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_DATABASE_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://webui.kakiquant.icu"
    ]
    
    # Host settings
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # API settings
    DEFAULT_API_QUOTA: int = 1000
    
    # GM API settings
    GM_TOKEN: str = os.getenv("GM_TOKEN", "")
    LOCAL_MODE: bool = os.getenv("LOCAL_MODE", "").lower() == "true"
    
    # Factor computation settings
    DEFAULT_FIELDS: List[str] = [
        'open', 'high', 'low', 'close', 
        'volume', 'amount', 'factor'
    ]
    DEFAULT_ADJUST: str = 'none'
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{{db}}?charset=utf8mb4"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Export all settings
__all__ = ["settings"]