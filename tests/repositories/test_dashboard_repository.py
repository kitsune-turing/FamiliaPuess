from datetime import date
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.dashboard_repository import (
    contar_asistencias_fecha,
    contar_empleados_activos,
    contar_novedades_fecha,
    contar_tardanzas_fecha,
)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


async def test_contar_empleados_activos(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 25
    session.execute.return_value = execute_result

    result = await contar_empleados_activos(session)
    assert result == 25


async def test_contar_asistencias_fecha(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 10
    session.execute.return_value = execute_result

    result = await contar_asistencias_fecha(session, date(2026, 8, 1))
    assert result == 10


async def test_contar_novedades_fecha(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 3
    session.execute.return_value = execute_result

    result = await contar_novedades_fecha(session, date(2026, 8, 1))
    assert result == 3


async def test_contar_tardanzas_fecha(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 2
    session.execute.return_value = execute_result

    result = await contar_tardanzas_fecha(session, date(2026, 8, 1))
    assert result == 2


async def test_contar_empleados_activos_zero(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 0
    session.execute.return_value = execute_result

    result = await contar_empleados_activos(session)
    assert result == 0


async def test_contar_asistencias_fecha_zero(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 0
    session.execute.return_value = execute_result

    result = await contar_asistencias_fecha(session, date(2026, 8, 1))
    assert result == 0
