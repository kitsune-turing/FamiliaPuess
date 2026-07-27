from unittest.mock import AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.dispositivo_repository import get_by_identificador


async def test_get_by_identificador_returns_scalar_result():
    session = AsyncMock(spec=AsyncSession)
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "dispositivo-encontrado"
    session.execute.return_value = execute_result

    dispositivo = await get_by_identificador(session, "KIOSK-001")

    assert dispositivo == "dispositivo-encontrado"
    session.execute.assert_awaited_once()


async def test_get_by_identificador_returns_none_when_missing():
    session = AsyncMock(spec=AsyncSession)
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: None
    session.execute.return_value = execute_result

    dispositivo = await get_by_identificador(session, "NO-EXISTE")

    assert dispositivo is None
