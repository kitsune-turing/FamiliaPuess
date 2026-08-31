from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.cat_cargo import CatCargo
from apps.API.models.empleado import Empleado
from shared.utils.sql import escape_like


async def get_by_id(session: AsyncSession, empleado_id: int) -> Empleado | None:
    stmt = (
        select(Empleado)
        .options(joinedload(Empleado.sede_actual), joinedload(Empleado.cargo))
        .where(Empleado.id == empleado_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_documento(
    session: AsyncSession, numero_documento: str
) -> Empleado | None:
    stmt = select(Empleado).where(Empleado.numero_documento == numero_documento)
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
        .options(joinedload(Empleado.sede_actual), joinedload(Empleado.cargo))
        .order_by(Empleado.nombre, Empleado.apellido)
    )
    if nombre is not None:
        safe = escape_like(nombre)
        stmt = stmt.where(
            (Empleado.nombre + " " + Empleado.apellido).ilike(
                f"%{safe}%", escape="\\"
            )
        )
    if documento is not None:
        safe = escape_like(documento)
        stmt = stmt.where(Empleado.numero_documento.ilike(f"%{safe}%", escape="\\"))
    if cargo is not None:
        safe = escape_like(cargo)
        stmt = stmt.join(Empleado.cargo).where(
            CatCargo.nombre.ilike(f"%{safe}%", escape="\\")
        )
    if id_estado is not None:
        stmt = stmt.where(Empleado.id_estado == id_estado)
    if id_sede is not None:
        stmt = stmt.where(Empleado.id_sede_actual == id_sede)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def create(
    session: AsyncSession,
    *,
    id_tipo_documento: int,
    numero_documento: str,
    nombre: str,
    apellido: str,
    id_cargo: int,
    id_estado: int,
    id_sede_actual: int,
    now: datetime | None = None,
) -> Empleado:
    empleado = Empleado(
        id_tipo_documento=id_tipo_documento,
        numero_documento=numero_documento,
        nombre=nombre,
        apellido=apellido,
        id_cargo=id_cargo,
        id_estado=id_estado,
        id_sede_actual=id_sede_actual,
    )
    if now is not None:
        empleado.created_at = now
        empleado.updated_at = now
    session.add(empleado)
    await session.flush()
    await session.refresh(empleado, attribute_names=["sede_actual", "cargo"])
    return empleado


async def update_empleado(
    session: AsyncSession,
    empleado_id: int,
    *,
    id_tipo_documento: int | None = None,
    numero_documento: str | None = None,
    nombre: str | None = None,
    apellido: str | None = None,
    id_cargo: int | None = None,
    id_estado: int | None = None,
    id_sede_actual: int | None = None,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if id_tipo_documento is not None:
        values["id_tipo_documento"] = id_tipo_documento
    if numero_documento is not None:
        values["numero_documento"] = numero_documento
    if nombre is not None:
        values["nombre"] = nombre
    if apellido is not None:
        values["apellido"] = apellido
    if id_cargo is not None:
        values["id_cargo"] = id_cargo
    if id_estado is not None:
        values["id_estado"] = id_estado
    if id_sede_actual is not None:
        values["id_sede_actual"] = id_sede_actual
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
