from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.asistencia import Asistencia
from apps.API.repositories.asistencia_repository import create, get_duplicado


async def test_create_adds_and_flushes_an_asistencia_row():
    session = AsyncMock(spec=AsyncSession)
    registrado_en = datetime(2026, 7, 22, 8, 0, 0, tzinfo=timezone.utc)

    asistencia = await create(
        session,
        id_empleado=10,
        id_token_qr=20,
        id_tipo_registro=1,
        id_sede=3,
        fecha_registro=date(2026, 7, 22),
        registrado_en=registrado_en,
    )

    assert isinstance(asistencia, Asistencia)
    assert asistencia.id_empleado == 10
    assert asistencia.id_token_qr == 20
    assert asistencia.id_tipo_registro == 1
    assert asistencia.id_sede == 3
    assert asistencia.fecha_registro == date(2026, 7, 22)
    session.add.assert_called_once_with(asistencia)
    session.flush.assert_awaited_once()


async def test_get_duplicado_returns_record_when_found():
    existing = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = existing

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_duplicado(
        session,
        id_empleado=10,
        fecha=date(2026, 7, 22),
        id_tipo_registro=1,
    )

    assert result is existing


async def test_get_duplicado_returns_none_when_no_duplicate():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_duplicado(
        session,
        id_empleado=10,
        fecha=date(2026, 7, 22),
        id_tipo_registro=1,
    )

    assert result is None
