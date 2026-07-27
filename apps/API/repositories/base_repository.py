from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped

from apps.API.repositories.cat_estado_repository import get_estado_id
from shared.constants.estado import EstadoCodigo


class EntidadConEstado(Protocol):
    id: Mapped[int]
    id_estado: Mapped[int]


ModelT = TypeVar("ModelT", bound=EntidadConEstado)


class BaseRepository(Generic[ModelT]):
    """Base para repositorios de entidades con eliminacion logica (HU-TRV-001).

    No expone ningun metodo de borrado fisico: la unica forma de "eliminar"
    una entidad es desactivarla mediante `deactivate`.
    """

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    async def deactivate(self, entity_id: int) -> None:
        inactivo_id = await get_estado_id(self.session, EstadoCodigo.INACTIVO)
        stmt = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(id_estado=inactivo_id)
        )
        await self.session.execute(stmt)

    async def list_active(self) -> Sequence[ModelT]:
        activo_id = await get_estado_id(self.session, EstadoCodigo.ACTIVO)
        stmt = select(self.model).where(self.model.id_estado == activo_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(self, id_estado: int | None = None) -> Sequence[ModelT]:
        stmt = select(self.model)
        if id_estado is not None:
            stmt = stmt.where(self.model.id_estado == id_estado)
        result = await self.session.execute(stmt)
        return result.scalars().all()
