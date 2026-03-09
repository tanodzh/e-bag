from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=True)

    PROJECT_NAME: str = "E-Bag E-commerce Service"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DB_USERNAME: str = Field(default="root", min_length=1)
    DB_PASSWORD: str = Field(default="", min_length=1)
    DB_NAME: str = Field(default="ecommerce_db", min_length=1)
    DB_HOST: str = Field(default="db", min_length=1)
    DB_PORT: int = Field(default=3306, gt=0)

    UPLOAD_DIR: str = "media/products"
    BASE_URL: str = "http://localhost:8000"

    @property
    def DATABASE_URL(self) -> str:
        # Handle password: if empty, use empty string
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mariadb+asyncmy://{self.DB_USERNAME}{password_part}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()