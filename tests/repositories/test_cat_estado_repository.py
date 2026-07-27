from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.cat_estado_repository import get_estado_id
from shared.exceptions.catalog import EstadoNoEncontradoError


def _session_returning(scalar_value):
    session = AsyncMock(spec=AsyncSession)
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: scalar_value
    session.execute.return_value = execute_result
    return session


async def test_get_estado_id_returns_id_for_known_codigo():
    session = _session_returning(2)

    estado_id = await get_estado_id(session, "INACTIVO")

    assert estado_id == 2
    session.execute.assert_awaited_once()


async def test_get_estado_id_raises_when_codigo_does_not_exist():
    session = _session_returning(None)

    with pytest.raises(EstadoNoEncontradoError):
        await get_estado_id(session, "NO_EXISTE")
