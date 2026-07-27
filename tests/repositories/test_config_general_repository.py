from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.config_general_repository import get_valor
from shared.exceptions.configuration import ConfiguracionNoEncontradaError


def _session_returning(scalar_value):
    session = AsyncMock(spec=AsyncSession)
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: scalar_value
    session.execute.return_value = execute_result
    return session


async def test_get_valor_returns_value_for_known_clave():
    session = _session_returning("30")

    valor = await get_valor(session, "QR_EXPIRACION_SEG")

    assert valor == "30"


async def test_get_valor_raises_when_clave_does_not_exist():
    session = _session_returning(None)

    with pytest.raises(ConfiguracionNoEncontradaError):
        await get_valor(session, "NO_EXISTE")
