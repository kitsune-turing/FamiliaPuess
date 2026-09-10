from datetime import date, datetime, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.reporte_repository import (
    contar_novedades_periodo,
    create_reporte,
    get_all_reportes,
    get_asistencias_filtradas,
    get_novedades_por_asistencia_ids,
    get_reporte_by_id,
    get_reporte_by_periodo,
)


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


async def test_get_asistencias_filtradas_returns_list(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["a1", "a2"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_asistencias_filtradas(session)
    assert result == ["a1", "a2"]


async def test_get_asistencias_filtradas_with_all_filters(session):
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    unique_mock.all = lambda: ["a1"]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_asistencias_filtradas(
        session,
        id_empleado=1,
        id_sede=2,
        fecha_desde=date(2026, 7, 1),
        fecha_hasta=date(2026, 7, 31),
    )
    assert result == ["a1"]


async def test_contar_novedades_periodo(session):
    execute_result = AsyncMock()
    execute_result.scalar_one = lambda: 5
    session.execute.return_value = execute_result

    result = await contar_novedades_periodo(
        session, date(2026, 7, 1), date(2026, 7, 7)
    )
    assert result == 5


async def test_get_novedades_por_asistencia_ids_empty(session):
    result = await get_novedades_por_asistencia_ids(session, [])
    assert result == {}


async def test_get_novedades_por_asistencia_ids_returns_map(session):
    class _FakeNovedad:
        id_asistencia = 10
    scalars_mock = AsyncMock()
    unique_mock = AsyncMock()
    fake = _FakeNovedad()
    unique_mock.all = lambda: [fake]
    scalars_mock.unique = lambda: unique_mock
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_novedades_por_asistencia_ids(session, [10, 20])
    assert 10 in result
    assert result[10] is fake


async def test_get_reporte_by_id_returns_scalar(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "reporte"
    session.execute.return_value = execute_result

    result = await get_reporte_by_id(session, 1)
    assert result == "reporte"


async def test_get_reporte_by_id_returns_none(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: None
    session.execute.return_value = execute_result

    result = await get_reporte_by_id(session, 999)
    assert result is None


async def test_get_reporte_by_periodo(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "reporte-periodo"
    session.execute.return_value = execute_result

    result = await get_reporte_by_periodo(
        session, date(2026, 7, 20), date(2026, 7, 26)
    )
    assert result == "reporte-periodo"


async def test_get_all_reportes(session):
    scalars_mock = AsyncMock()
    scalars_mock.all = lambda: ["r1", "r2"]
    execute_result = AsyncMock()
    execute_result.scalars = lambda: scalars_mock
    session.execute.return_value = execute_result

    result = await get_all_reportes(session)
    assert result == ["r1", "r2"]


async def test_create_reporte_adds_and_flushes(session):
    now = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)
    result = await create_reporte(
        session,
        fecha_inicio=date(2026, 7, 20),
        fecha_fin=date(2026, 7, 26),
        total_registros=50,
        total_novedades=3,
        now=now,
    )
    session.add.assert_called_once()
    session.flush.assert_awaited_once()
    assert result.fecha_inicio == date(2026, 7, 20)
    assert result.fecha_fin == date(2026, 7, 26)
    assert result.total_registros == 50
    assert result.total_novedades == 3
    assert result.created_at == now
