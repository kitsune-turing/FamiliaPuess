from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.empleado_repository import get_by_documento


async def test_get_by_documento_returns_employee_when_found():
    empleado_mock = MagicMock()
    empleado_mock.documento = "123456"

    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = empleado_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_documento(session, "123456")

    assert result is empleado_mock
    session.execute.assert_awaited_once()


async def test_get_by_documento_returns_none_when_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_by_documento(session, "000000")

    assert result is None
