from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        extra='allow'
    )

    # Database settings
    CC_DATABASE_HOST: str = "10.201.8.179"
    CC_DATABASE_PORT: int = 8123
    CC_DATABASE_PASSWORD: str = ""
    
    # MySQL settings
    MYSQL_USER: str = "kkdatad"
    MYSQL_PASSWORD: str = "kkdatad"
    MYSQL_HOST: str = "10.201.8.179"
    MYSQL_PORT: int = 3306
    
    # Redis settings
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    
    # Security settings
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
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
    GM_TOKEN: str = ""
    LOCAL_MODE: bool = True  # Set to True to run in local mode without GM API
    
    # Factor computation settings
    DEFAULT_FIELDS: List[str] = [
        'open', 'high', 'low', 'close', 
        'volume', 'amount', 'factor'
    ]
    DEFAULT_ADJUST: str = 'none'
    
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{{db}}?charset=utf8mb4"

settings = Settings()

# Export all settings
__all__ = ["settings"]