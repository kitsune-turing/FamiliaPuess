from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories.permiso_rol_repository import get_permisos_by_rol


async def test_get_permisos_by_rol_returns_list():
    p1 = MagicMock()
    p2 = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [p1, p2]
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_permisos_by_rol(session, id_rol=1)

    assert len(result) == 2
    assert result[0] is p1
    assert result[1] is p2


async def test_get_permisos_by_rol_returns_empty_list():
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = []
    result_mock = MagicMock()
    result_mock.scalars.return_value = scalars_mock

    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value = result_mock

    result = await get_permisos_by_rol(session, id_rol=999)

    assert result == []
