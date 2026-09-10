from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.novedad_repository import (
    create,
    get_all,
    get_by_asistencia,
    get_by_id,
)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


async def test_get_by_id_returns_scalar_result(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "novedad-encontrada"
    session.execute.return_value = execute_result

    result = await get_by_id(session, 1)
    assert result == "novedad-encontrada"


async def test_get_by_id_returns_none_when_not_found(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: None
    session.execute.return_value = execute_result

    result = await get_by_id(session, 999)
    assert result is None


async def test_get_all_returns_list(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["n1", "n2"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all(session)
    assert result == ["n1", "n2"]


async def test_get_all_with_empleado_filter(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["n1"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all(session, id_empleado=5)
    assert result == ["n1"]


async def test_get_all_with_fecha_range(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["n1"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all(
        session,
        fecha_desde=date(2026, 7, 1),
        fecha_hasta=date(2026, 7, 31),
    )
    assert result == ["n1"]


async def test_get_by_asistencia_returns_scalar(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "novedad-asistencia"
    session.execute.return_value = execute_result

    result = await get_by_asistencia(session, 10)
    assert result == "novedad-asistencia"


async def test_create_adds_and_flushes(session):
    now = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)
    result = await create(
        session,
        id_empleado=1,
        id_tipo_novedad=2,
        id_asistencia=10,
        fecha=date(2026, 7, 28),
        observacion="Llegada tarde",
        now=now,
    )
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result.id_empleado == 1
    assert result.id_tipo_novedad == 2
    assert result.id_asistencia == 10
    assert result.fecha == date(2026, 7, 28)
    assert result.observacion == "Llegada tarde"
    assert result.created_at == now


async def test_create_without_asistencia(session):
    result = await create(
        session,
        id_empleado=1,
        id_tipo_novedad=3,
        fecha=date(2026, 7, 28),
    )
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result.id_asistencia is None
    assert result.observacion is None
