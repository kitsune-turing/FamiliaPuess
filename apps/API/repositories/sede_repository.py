from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.sede import Sede


async def get_by_id(session: AsyncSession, sede_id: int) -> Sede | None:
    stmt = select(Sede).where(Sede.id == sede_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_nombre(session: AsyncSession, nombre: str) -> Sede | None:
    stmt = select(Sede).where(Sede.nombre == nombre)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    direccion: str | None = None,
    id_estado: int | None = None,
) -> Sequence[Sede]:
    stmt = select(Sede).order_by(Sede.nombre)
    if nombre is not None:
        stmt = stmt.where(Sede.nombre.ilike(f"%{nombre}%"))
    if direccion is not None:
        stmt = stmt.where(Sede.direccion.ilike(f"%{direccion}%"))
    if id_estado is not None:
        stmt = stmt.where(Sede.id_estado == id_estado)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create(
    session: AsyncSession,
    *,
    nombre: str,
    direccion: str,
    id_estado: int,
    now: datetime | None = None,
) -> Sede:
    sede = Sede(
        nombre=nombre,
        direccion=direccion,
        id_estado=id_estado,
    )
    if now is not None:
        sede.created_at = now
        sede.updated_at = now
    session.add(sede)
    await session.flush()
    return sede


async def update_sede(
    session: AsyncSession,
    sede_id: int,
    *,
    nombre: str | None = None,
    direccion: str | None = None,
    id_estado: int | None = None,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if nombre is not None:
        values["nombre"] = nombre
    if direccion is not None:
        values["direccion"] = direccion
    if id_estado is not None:
        values["id_estado"] = id_estado
    if now is not None:
        values["updated_at"] = now
    if not values:
        return
    stmt = update(Sede).where(Sede.id == sede_id).values(**values)
    await session.execute(stmt)


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Sede)
        .where(Sede.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()
