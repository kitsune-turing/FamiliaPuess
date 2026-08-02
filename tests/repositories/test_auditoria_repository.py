from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.auditoria import Auditoria
from apps.API.repositories.auditoria_repository import count, create, get_all

FIXED_NOW = datetime(2026, 7, 27, 8, 0, 0, tzinfo=timezone.utc)


async def test_create_adds_and_flushes_audit_record():
    session = AsyncMock(spec=AsyncSession)

    result = await create(
        session,
        id_usuario=1,
        recurso="USUARIO",
        id_recurso="5",
        operacion="LOGIN",
        ip_address="192.168.1.1",
        timestamp_accion=FIXED_NOW,
    )

    assert isinstance(result, Auditoria)
    assert result.recurso == "USUARIO"
    assert result.operacion == "LOGIN"
    assert result.id_usuario == 1
    session.add.assert_called_once_with(result)
    session.flush.assert_awaited_once()


async def test_create_allows_null_usuario_for_failed_login():
    session = AsyncMock(spec=AsyncSession)

    result = await create(
        session,
        id_usuario=None,
        recurso="USUARIO",
        id_recurso=None,
        operacion="LOGIN_FALLIDO",
        ip_address="10.0.0.1",
        detalle="Intento fallido con username: ghost",
        timestamp_accion=FIXED_NOW,
    )

    assert result.id_usuario is None
    assert result.operacion == "LOGIN_FALLIDO"
    assert result.detalle == "Intento fallido con username: ghost"


async def test_get_all_no_filters():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock(), MagicMock()]
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(session)
    assert len(results) == 2
    session.execute.assert_awaited_once()


async def test_get_all_with_usuario_filter():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(session, id_usuario=5)
    assert len(results) == 1


async def test_get_all_with_recurso_filter():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(session, recurso="EMPLEADO")
    assert len(results) == 1


async def test_get_all_with_operacion_filter():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(session, operacion="DELETE")
    assert results == []


async def test_get_all_with_date_range():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(
        session,
        fecha_desde=date(2026, 7, 1),
        fecha_hasta=date(2026, 8, 1),
    )
    assert len(results) == 1


async def test_get_all_combined_filters():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock()]
    session.execute = AsyncMock(return_value=mock_result)

    results = await get_all(
        session,
        id_usuario=1,
        recurso="SEDE",
        operacion="UPDATE",
        fecha_desde=date(2026, 8, 1),
        fecha_hasta=date(2026, 8, 1),
    )
    assert len(results) == 1


async def test_count_no_filters():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 42
    session.execute = AsyncMock(return_value=mock_result)

    total = await count(session)
    assert total == 42


async def test_count_with_filters():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 5
    session.execute = AsyncMock(return_value=mock_result)

    total = await count(session, id_usuario=1, recurso="USUARIO", operacion="INSERT")
    assert total == 5


async def test_count_zero():
    session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = 0
    session.execute = AsyncMock(return_value=mock_result)

    total = await count(session, recurso="INEXISTENTE")
    assert total == 0
