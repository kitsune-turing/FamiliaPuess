from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.cat_rol import CatRol
from apps.API.models.usuario import Usuario


async def get_by_codigo(session: AsyncSession, codigo: str) -> CatRol | None:
    stmt = select(CatRol).where(CatRol.codigo == codigo)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, rol_id: int) -> CatRol | None:
    stmt = select(CatRol).where(CatRol.id == rol_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(session: AsyncSession) -> Sequence[CatRol]:
    stmt = select(CatRol).order_by(CatRol.nombre)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create(
    session: AsyncSession,
    *,
    codigo: str,
    nombre: str,
    id_estado: int,
    descripcion: str | None = None,
    now: datetime | None = None,
) -> CatRol:
    rol = CatRol(
        codigo=codigo,
        nombre=nombre,
        id_estado=id_estado,
        descripcion=descripcion,
    )
    if now is not None:
        rol.created_at = now
        rol.updated_at = now
    session.add(rol)
    await session.flush()
    return rol


async def update_rol(
    session: AsyncSession,
    rol_id: int,
    *,
    nombre: str | None = None,
    descripcion: str | None = ...,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if nombre is not None:
        values["nombre"] = nombre
    if descripcion is not ...:
        values["descripcion"] = descripcion
    if now is not None:
        values["updated_at"] = now
    if not values:
        return
    stmt = update(CatRol).where(CatRol.id == rol_id).values(**values)
    await session.execute(stmt)


async def deactivate(
    session: AsyncSession,
    rol_id: int,
    id_estado_inactivo: int,
    now: datetime | None = None,
) -> None:
    values: dict = {"id_estado": id_estado_inactivo}
    if now is not None:
        values["updated_at"] = now
    stmt = update(CatRol).where(CatRol.id == rol_id).values(**values)
    await session.execute(stmt)


async def count_usuarios_by_rol(session: AsyncSession, rol_id: int) -> int:
    stmt = select(func.count()).select_from(Usuario).where(Usuario.id_rol == rol_id)
    result = await session.execute(stmt)
    return result.scalar_one()


async def hard_delete(session: AsyncSession, rol_id: int) -> None:
    stmt = delete(CatRol).where(CatRol.id == rol_id)
    await session.execute(stmt)
