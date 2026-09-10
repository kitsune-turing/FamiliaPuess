from datetime import datetime, time, timedelta, timezone

import pytest

from apps.API.core.config import get_settings
from apps.API.core.timezone import (
    extract_local_time,
    get_zoneinfo,
    now,
    to_configured_timezone,
)

BOGOTA_OFFSET = timedelta(hours=-5)


@pytest.fixture(autouse=True)
def _clear_caches(monkeypatch):
    monkeypatch.delenv("APP_TIMEZONE", raising=False)
    get_settings.cache_clear()
    get_zoneinfo.cache_clear()
    yield
    get_settings.cache_clear()
    get_zoneinfo.cache_clear()


def test_now_returns_timezone_aware_datetime_in_bogota_offset():
    instant = now()

    assert instant.tzinfo is not None
    assert instant.utcoffset() == BOGOTA_OFFSET


def test_to_configured_timezone_converts_utc_instant_to_bogota_wallclock():
    utc_instant = datetime(2026, 1, 1, 3, 0, 0, tzinfo=timezone.utc)

    converted = to_configured_timezone(utc_instant)

    assert converted.utcoffset() == BOGOTA_OFFSET
    assert converted.replace(tzinfo=None) == datetime(2025, 12, 31, 22, 0, 0)


def test_to_configured_timezone_rejects_naive_datetime():
    naive_dt = datetime(2026, 1, 1, 8, 0, 0)

    with pytest.raises(ValueError):
        to_configured_timezone(naive_dt)


def test_extract_local_time_uses_configured_timezone_not_utc():
    # Registro guardado como TIMESTAMPTZ en UTC que cae "de noche" en Bogota
    timestamp_registro = datetime(2026, 1, 1, 3, 5, 0, tzinfo=timezone.utc)

    local_time = extract_local_time(timestamp_registro)

    assert local_time == time(22, 5, 0)


def test_get_zoneinfo_respects_env_override(monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "UTC")
    get_settings.cache_clear()
    get_zoneinfo.cache_clear()

    instant = now()

    assert instant.utcoffset() == timedelta(0)
