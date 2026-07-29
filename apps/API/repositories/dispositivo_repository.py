from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.dispositivo import Dispositivo


async def get_by_id(session: AsyncSession, dispositivo_id: int) -> Dispositivo | None:
    stmt = (
        select(Dispositivo)
        .options(joinedload(Dispositivo.sede))
        .where(Dispositivo.id == dispositivo_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_identificador(session: AsyncSession, identificador: str) -> Dispositivo | None:
    stmt = select(Dispositivo).where(Dispositivo.identificador == identificador)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_by_sede(
    session: AsyncSession, id_sede: int, activo_id: int
) -> Dispositivo | None:
    stmt = (
        select(Dispositivo)
        .where(Dispositivo.id_sede == id_sede)
        .where(Dispositivo.id_estado == activo_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    identificador: str | None = None,
    id_sede: int | None = None,
    id_estado: int | None = None,
) -> Sequence[Dispositivo]:
    stmt = (
        select(Dispositivo)
        .options(joinedload(Dispositivo.sede))
        .order_by(Dispositivo.id_sede)
    )
    if identificador is not None:
        stmt = stmt.where(Dispositivo.identificador.ilike(f"%{identificador}%"))
    if id_sede is not None:
        stmt = stmt.where(Dispositivo.id_sede == id_sede)
    if id_estado is not None:
        stmt = stmt.where(Dispositivo.id_estado == id_estado)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def create(
    session: AsyncSession,
    *,
    identificador: str,
    id_sede: int,
    id_estado: int,
    descripcion: str | None = None,
    now: datetime | None = None,
) -> Dispositivo:
    dispositivo = Dispositivo(
        identificador=identificador,
        id_sede=id_sede,
        id_estado=id_estado,
        descripcion=descripcion,
    )
    if now is not None:
        dispositivo.created_at = now
        dispositivo.updated_at = now
    session.add(dispositivo)
    await session.flush()
    return dispositivo


async def update_dispositivo(
    session: AsyncSession,
    dispositivo_id: int,
    *,
    identificador: str | None = None,
    id_sede: int | None = None,
    id_estado: int | None = None,
    descripcion: str | None = None,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if identificador is not None:
        values["identificador"] = identificador
    if id_sede is not None:
        values["id_sede"] = id_sede
    if id_estado is not None:
        values["id_estado"] = id_estado
    if descripcion is not None:
        values["descripcion"] = descripcion
    if now is not None:
        values["updated_at"] = now
    if not values:
        return
    stmt = update(Dispositivo).where(Dispositivo.id == dispositivo_id).values(**values)
    await session.execute(stmt)


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Dispositivo)
        .where(Dispositivo.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()
