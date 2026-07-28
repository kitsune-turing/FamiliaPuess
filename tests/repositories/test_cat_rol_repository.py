from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.cat_rol_repository import get_by_codigo


async def test_get_by_codigo_returns_rol_when_found():
    rol_mock = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = rol_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_codigo(session, "ADMIN")

    assert result is rol_mock
    session.execute.assert_awaited_once()


async def test_get_by_codigo_returns_none_when_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_codigo(session, "NO_EXISTE")

    assert result is None
