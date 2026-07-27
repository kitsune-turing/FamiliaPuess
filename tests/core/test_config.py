import pytest

from apps.API.core.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_default_timezone_matches_config_general_seed():
    # Debe coincidir con el seed de config_general.ZONA_HORARIA (RF-089, database.sql)
    assert get_settings().app_timezone == "America/Bogota"


def test_timezone_is_overridable_via_environment(monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "America/Mexico_City")
    get_settings.cache_clear()

    assert get_settings().app_timezone == "America/Mexico_City"


def test_get_settings_is_cached():
    assert get_settings() is get_settings()
