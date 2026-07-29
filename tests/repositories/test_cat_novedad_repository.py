from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.cat_novedad_repository import get_by_codigo


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


async def test_get_by_codigo_returns_result(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: "tardanza-cat"
    session.execute.return_value = execute_result

    result = await get_by_codigo(session, "TARDANZA")
    assert result == "tardanza-cat"


async def test_get_by_codigo_returns_none_when_not_found(session):
    execute_result = AsyncMock()
    execute_result.scalar_one_or_none = lambda: None
    session.execute.return_value = execute_result

    result = await get_by_codigo(session, "INEXISTENTE")
    assert result is None
