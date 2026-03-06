from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "E-Bag E-commerce Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "sqlite+aiosqlite://./e_bag.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()