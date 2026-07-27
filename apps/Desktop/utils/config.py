from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DesktopSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="DESKTOP_", extra="ignore")

    api_base_url: str = "http://localhost:8000"
    dispositivo_identificador: str = "KIOSK-001"
    registro_publico_url: str = "http://localhost:5173/registro"
    rotacion_fallback_segundos: int = 30


@lru_cache
def get_desktop_settings() -> DesktopSettings:
    return DesktopSettings()
