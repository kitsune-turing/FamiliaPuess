import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.sesion_usuario import SesionUsuario
from apps.API.repositories.sesion_usuario_repository import (
    create,
    deactivate,
    deactivate_all_for_user,
    get_active_by_user,
    get_by_refresh_hash,
    get_by_token_hash,
    update_tokens,
)

FIXED_NOW = datetime(2026, 7, 27, 8, 0, 0, tzinfo=timezone.utc)
EXPIRA = datetime(2026, 7, 27, 8, 30, 0, tzinfo=timezone.utc)


async def test_create_adds_and_flushes_session():
    session = AsyncMock(spec=AsyncSession)

    result = await create(
        session,
        id_usuario=1,
        token_hash="hash_access",
        refresh_token_hash="hash_refresh",
        ip_address="127.0.0.1",
        user_agent="TestAgent/1.0",
        fecha_expira=EXPIRA,
    )

    assert isinstance(result, SesionUsuario)
    assert result.id_usuario == 1
    assert result.token_hash == "hash_access"
    session.add.assert_called_once_with(result)
    session.flush.assert_awaited_once()


async def test_get_active_by_user_returns_session_when_found():
    sesion_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sesion_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_active_by_user(session, user_id=1)

    assert result is sesion_mock


async def test_get_active_by_user_returns_none_when_no_active():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_active_by_user(session, user_id=99)

    assert result is None


async def test_get_by_token_hash_returns_session():
    sesion_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sesion_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_token_hash(session, "some_hash")

    assert result is sesion_mock


async def test_get_by_refresh_hash_returns_session():
    sesion_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = sesion_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_refresh_hash(session, "refresh_hash")

    assert result is sesion_mock


async def test_deactivate_executes_update():
    session = AsyncMock(spec=AsyncSession)
    sid = uuid.uuid4()

    await deactivate(session, sid, FIXED_NOW)

    session.execute.assert_awaited_once()


async def test_deactivate_all_for_user_executes_update():
    session = AsyncMock(spec=AsyncSession)

    await deactivate_all_for_user(session, user_id=1, logout_time=FIXED_NOW)

    session.execute.assert_awaited_once()


async def test_update_tokens_executes_update():
    session = AsyncMock(spec=AsyncSession)
    sid = uuid.uuid4()

    await update_tokens(
        session,
        sid,
        token_hash="new_access_hash",
        refresh_token_hash="new_refresh_hash",
        fecha_expira=EXPIRA,
    )

    session.execute.assert_awaited_once()
