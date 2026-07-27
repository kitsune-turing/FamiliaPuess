from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_timezone: str = "America/Bogota"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/familia_puess"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
