from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, DirectoryPath
from typing import Literal, Optional
import os

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str = Field(..., min_length=30, description="Telegram Bot API token")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field("INFO", description="Logging level")
    INSPECTIONS_BASE_PATH: DirectoryPath = Field(..., description="Base path for structure_inspections")

    REDIS_HOST: str = Field("redis", description="Redis host")
    REDIS_PORT: int = Field(6379, description="Redis port")
    REDIS_DB: int = Field(0, description="Redis database number")
    REDIS_PASSWORD: Optional[str] = Field(None, description="Redis password (optional)")

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
