from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.empleado import Empleado
from shared.utils.sql import escape_like


async def get_by_id(session: AsyncSession, empleado_id: int) -> Empleado | None:
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.sede))
        .where(Empleado.id == empleado_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_documento(session: AsyncSession, documento: str) -> Empleado | None:
    stmt = select(Empleado).where(Empleado.documento == documento)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    documento: str | None = None,
    cargo: str | None = None,
    id_estado: int | None = None,
    id_sede: int | None = None,
) -> Sequence[Empleado]:
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.sede))
        .order_by(Empleado.nombre, Empleado.apellido)
    )
    if nombre is not None:
        safe = escape_like(nombre)
        stmt = stmt.where(
            (Empleado.nombre.ilike(f"%{safe}%", escape="\\"))
            | (Empleado.apellido.ilike(f"%{safe}%", escape="\\"))
        )
    if documento is not None:
        safe = escape_like(documento)
        stmt = stmt.where(Empleado.documento.ilike(f"%{safe}%", escape="\\"))
    if cargo is not None:
        safe = escape_like(cargo)
        stmt = stmt.where(Empleado.cargo.ilike(f"%{safe}%", escape="\\"))
    if id_estado is not None:
        stmt = stmt.where(Empleado.id_estado == id_estado)
    if id_sede is not None:
        stmt = stmt.where(Empleado.id_sede == id_sede)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def create(
    session: AsyncSession,
    *,
    documento: str,
    nombre: str,
    apellido: str,
    cargo: str,
    id_estado: int,
    id_sede: int,
    now: datetime | None = None,
) -> Empleado:
    empleado = Empleado(
        documento=documento,
        nombre=nombre,
        apellido=apellido,
        cargo=cargo,
        id_estado=id_estado,
        id_sede=id_sede,
    )
    if now is not None:
        empleado.created_at = now
        empleado.updated_at = now
    session.add(empleado)
    await session.flush()
    await session.refresh(empleado, attribute_names=["sede"])
    return empleado


async def update_empleado(
    session: AsyncSession,
    empleado_id: int,
    *,
    documento: str | None = None,
    nombre: str | None = None,
    apellido: str | None = None,
    cargo: str | None = None,
    id_estado: int | None = None,
    id_sede: int | None = None,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if documento is not None:
        values["documento"] = documento
    if nombre is not None:
        values["nombre"] = nombre
    if apellido is not None:
        values["apellido"] = apellido
    if cargo is not None:
        values["cargo"] = cargo
    if id_estado is not None:
        values["id_estado"] = id_estado
    if id_sede is not None:
        values["id_sede"] = id_sede
    if now is not None:
        values["updated_at"] = now
    if not values:
        return
    stmt = update(Empleado).where(Empleado.id == empleado_id).values(**values)
    await session.execute(stmt)


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Empleado)
        .where(Empleado.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()
