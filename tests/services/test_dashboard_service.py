from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services.dashboard_service import get_indicadores

FIXED_NOW = datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


def _patches(
    empleados=0,
    asistencias=0,
    novedades=0,
    tardanzas=0,
):
    return {
        "empleados": patch(
            "apps.API.services.dashboard_service.dashboard_repository.contar_empleados_activos",
            new=AsyncMock(return_value=empleados),
        ),
        "asistencias": patch(
            "apps.API.services.dashboard_service.dashboard_repository.contar_asistencias_fecha",
            new=AsyncMock(return_value=asistencias),
        ),
        "novedades": patch(
            "apps.API.services.dashboard_service.dashboard_repository.contar_novedades_fecha",
            new=AsyncMock(return_value=novedades),
        ),
        "tardanzas": patch(
            "apps.API.services.dashboard_service.dashboard_repository.contar_tardanzas_fecha",
            new=AsyncMock(return_value=tardanzas),
        ),
        "tz_now": patch(
            "apps.API.services.dashboard_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


async def test_get_indicadores_returns_all_counts(session):
    mocks = _patches(empleados=25, asistencias=10, novedades=3, tardanzas=2)
    with (
        mocks["empleados"],
        mocks["asistencias"],
        mocks["novedades"],
        mocks["tardanzas"],
        mocks["tz_now"],
    ):
        result = await get_indicadores(session)
    assert result.empleados_activos == 25
    assert result.asistencias_hoy == 10
    assert result.novedades_hoy == 3
    assert result.tardanzas_hoy == 2


async def test_get_indicadores_all_zeros(session):
    mocks = _patches(empleados=0, asistencias=0, novedades=0, tardanzas=0)
    with (
        mocks["empleados"],
        mocks["asistencias"],
        mocks["novedades"],
        mocks["tardanzas"],
        mocks["tz_now"],
    ):
        result = await get_indicadores(session)
    assert result.empleados_activos == 0
    assert result.asistencias_hoy == 0
    assert result.novedades_hoy == 0
    assert result.tardanzas_hoy == 0


async def test_get_indicadores_uses_today_date(session):
    asistencias_mock = AsyncMock(return_value=5)
    mocks = _patches(empleados=10, novedades=1, tardanzas=0)
    with (
        mocks["empleados"],
        patch(
            "apps.API.services.dashboard_service.dashboard_repository.contar_asistencias_fecha",
            new=asistencias_mock,
        ),
        mocks["novedades"],
        mocks["tardanzas"],
        mocks["tz_now"],
    ):
        await get_indicadores(session)
    call_args = asistencias_mock.call_args
    assert call_args[0][1] == date(2026, 8, 1)


async def test_get_indicadores_large_counts(session):
    mocks = _patches(empleados=500, asistencias=480, novedades=50, tardanzas=15)
    with (
        mocks["empleados"],
        mocks["asistencias"],
        mocks["novedades"],
        mocks["tardanzas"],
        mocks["tz_now"],
    ):
        result = await get_indicadores(session)
    assert result.empleados_activos == 500
    assert result.asistencias_hoy == 480
    assert result.novedades_hoy == 50
    assert result.tardanzas_hoy == 15
