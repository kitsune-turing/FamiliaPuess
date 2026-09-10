from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy import Update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from apps.API.models.base import Base
from apps.API.repositories.base_repository import BaseRepository


class _EntidadPrueba(Base):
    __tablename__ = "entidad_prueba"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_estado: Mapped[int] = mapped_column()


def _compiled(stmt) -> str:
    return str(stmt.compile(compile_kwargs={"literal_binds": True}))


def test_base_repository_never_exposes_a_physical_delete_method():
    forbidden_names = {"delete", "hard_delete", "remove", "drop"}

    assert forbidden_names.isdisjoint(vars(BaseRepository))


@patch("apps.API.repositories.base_repository.get_estado_id", new_callable=AsyncMock)
async def test_deactivate_updates_id_estado_and_never_deletes(mock_get_estado_id):
    mock_get_estado_id.return_value = 2
    session = AsyncMock(spec=AsyncSession)
    repo = BaseRepository(session, _EntidadPrueba)

    await repo.deactivate(42)

    session.execute.assert_awaited_once()
    stmt = session.execute.call_args.args[0]
    assert isinstance(stmt, Update)
    sql = _compiled(stmt)
    assert "entidad_prueba" in sql
    assert "id_estado=2" in sql.replace(" ", "")
    assert "id = 42" in sql
    session.delete.assert_not_called()


@patch("apps.API.repositories.base_repository.get_estado_id", new_callable=AsyncMock)
async def test_list_active_filters_by_activo_state(mock_get_estado_id):
    mock_get_estado_id.return_value = 1
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["entidad-activa"]
    session.execute.return_value = result
    repo = BaseRepository(session, _EntidadPrueba)

    entities = await repo.list_active()

    assert entities == ["entidad-activa"]
    stmt = session.execute.call_args.args[0]
    assert "id_estado = 1" in _compiled(stmt)


async def test_list_all_without_filter_returns_every_estado():
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["activa", "inactiva"]
    session.execute.return_value = result
    repo = BaseRepository(session, _EntidadPrueba)

    entities = await repo.list_all()

    assert entities == ["activa", "inactiva"]
    stmt = session.execute.call_args.args[0]
    assert "WHERE" not in _compiled(stmt)


async def test_list_all_with_filter_restricts_by_estado():
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalars.return_value.all.return_value = ["inactiva"]
    session.execute.return_value = result
    repo = BaseRepository(session, _EntidadPrueba)

    await repo.list_all(id_estado=2)

    stmt = session.execute.call_args.args[0]
    assert "id_estado = 2" in _compiled(stmt)
