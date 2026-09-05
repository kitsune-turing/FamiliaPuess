from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_timezone: str = "America/Bogota"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/familia_puess"
    )

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 1440
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    desktop_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
