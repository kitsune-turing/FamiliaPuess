from datetime import date, time
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.horario_repository import (
    create,
    get_all,
    get_by_id,
    get_vigente_by_sede,
    set_vigente_hasta,
)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


async def test_get_by_id_returns_scalar_result(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "horario-encontrado"
    session.execute.return_value = execute_result

    result = await get_by_id(session, 1)
    assert result == "horario-encontrado"


async def test_get_by_id_returns_none_when_not_found(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: None
    session.execute.return_value = execute_result

    result = await get_by_id(session, 999)
    assert result is None


async def test_get_all_returns_list(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["h1", "h2"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all(session)
    assert result == ["h1", "h2"]


async def test_get_all_with_sede_filter(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["h1"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all(session, id_sede=5)
    assert result == ["h1"]


async def test_get_vigente_by_sede_returns_scalar(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "vigente"
    session.execute.return_value = execute_result

    result = await get_vigente_by_sede(session, 1, date(2026, 7, 28))
    assert result == "vigente"


async def test_create_adds_and_flushes(session):
    result = await create(
        session,
        id_sede=1,
        hora_entrada=time(8, 0),
        tolerancia_min=15,
        vigente_desde=date(2026, 7, 28),
    )
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result.id_sede == 1
    assert result.hora_entrada == time(8, 0)


async def test_set_vigente_hasta_executes_update(session):
    await set_vigente_hasta(session, 1, date(2026, 8, 1))
    session.execute.assert_awaited_once()
