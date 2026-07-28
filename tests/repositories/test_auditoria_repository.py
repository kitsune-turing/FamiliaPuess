from datetime import datetime, timezone
from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.auditoria import Auditoria
from apps.API.repositories.auditoria_repository import create

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
