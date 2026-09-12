from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug: bool = False
    app_timezone: str
    database_url: str
    cors_origins: list[str]

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 1440
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    desktop_api_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
