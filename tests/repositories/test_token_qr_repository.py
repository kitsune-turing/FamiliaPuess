from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.token_qr import TokenQR
from apps.API.repositories.token_qr_repository import create, get_by_token, mark_consumed


async def test_create_adds_and_flushes_a_token_qr_row():
    session = AsyncMock(spec=AsyncSession)
    generado_en = datetime(2026, 1, 1, tzinfo=timezone.utc)
    expira_en = datetime(2026, 1, 1, 0, 0, 30, tzinfo=timezone.utc)

    token_qr = await create(
        session,
        id_sede=1,
        id_dispositivo=2,
        id_estado_token=3,
        token="opaque-token",
        codigo_alfa="ABC123",
        generado_en=generado_en,
        expira_en=expira_en,
    )

    assert isinstance(token_qr, TokenQR)
    assert token_qr.id_sede == 1
    assert token_qr.id_dispositivo == 2
    assert token_qr.id_estado_token == 3
    assert token_qr.token == "opaque-token"
    assert token_qr.codigo_alfa == "ABC123"
    session.add.assert_called_once_with(token_qr)
    session.flush.assert_awaited_once()


async def test_get_by_token_returns_token_when_found():
    token_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = token_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_token(session, "opaque-token")

    assert result is token_mock
    session.execute.assert_awaited_once()


async def test_get_by_token_returns_none_when_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_token(session, "no-existe")

    assert result is None


async def test_mark_consumed_executes_update():
    session = AsyncMock(spec=AsyncSession)
    consumido_en = datetime(2026, 7, 22, 8, 0, 0, tzinfo=timezone.utc)

    await mark_consumed(
        session,
        token_id=100,
        id_estado_consumido=10,
        consumido_en=consumido_en,
    )

    session.execute.assert_awaited_once()
