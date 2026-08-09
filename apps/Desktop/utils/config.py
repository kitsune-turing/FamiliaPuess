from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILE = _PROJECT_ROOT / ".env"


class DesktopSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_prefix="DESKTOP_",
        extra="ignore",
    )

    api_base_url: str = "http://localhost:8000"
    dispositivo_identificador: str = "KIOSK-001"
    registro_publico_url: str = "http://localhost:5173/registro"
    rotacion_fallback_segundos: int = 30
    api_username: str = ""
    api_password: str = ""


@lru_cache
def get_desktop_settings() -> DesktopSettings:
    return DesktopSettings()
