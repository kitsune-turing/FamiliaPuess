from datetime import datetime, timezone
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.token_qr import TokenQR
from apps.API.repositories.token_qr_repository import create


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
