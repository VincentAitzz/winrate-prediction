from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    riot_api_key: Optional[str] = Field(
        default=None,
        env="RIOT_API_KEY",
    )
    riot_region: str = Field(
        default="la1",
        env="RIOT_REGION",
    )
    model_path: str = Field(
        default="models/winrate_model.pkl",
        env="MODEL_PATH",
    )
    log_level: str = Field(
        default="info",
        env="LOG_LEVEL",
    )

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia singleton de Settings."""
    return Settings()
