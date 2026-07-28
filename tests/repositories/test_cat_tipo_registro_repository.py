from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.cat_tipo_registro_repository import get_tipo_registro_id


async def test_get_tipo_registro_id_returns_id_when_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = 5

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    tipo_id = await get_tipo_registro_id(session, "ENTRADA")

    assert tipo_id == 5


async def test_get_tipo_registro_id_raises_when_not_found():
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    with pytest.raises(ValueError, match="SALIDA"):
        await get_tipo_registro_id(session, "SALIDA")
