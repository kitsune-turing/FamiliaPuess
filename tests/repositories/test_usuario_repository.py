from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.usuario_repository import (
    get_by_id,
    get_by_username,
    update_password,
    update_ultimo_login,
)


async def test_get_by_username_returns_user_when_found():
    user_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_username(session, "admin")

    assert result is user_mock
    session.execute.assert_awaited_once()


async def test_get_by_username_returns_none_when_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_username(session, "nonexistent")

    assert result is None


async def test_get_by_id_returns_user_when_found():
    user_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = user_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_id(session, 1)

    assert result is user_mock


async def test_update_ultimo_login_executes_update():
    session = AsyncMock(spec=AsyncSession)
    ts = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)

    await update_ultimo_login(session, user_id=1, timestamp=ts)

    session.execute.assert_awaited_once()


async def test_update_password_executes_update():
    session = AsyncMock(spec=AsyncSession)
    ts = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)

    await update_password(session, user_id=1, new_hash="new_hash", timestamp=ts)

    session.execute.assert_awaited_once()
