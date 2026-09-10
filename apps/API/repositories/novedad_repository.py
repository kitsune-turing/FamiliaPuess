from collections.abc import Sequence
from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.novedad import Novedad


async def get_by_id(session: AsyncSession, novedad_id: int) -> Novedad | None:
    stmt = (
        select(Novedad)
        .options(joinedload(Novedad.empleado), joinedload(Novedad.tipo_novedad))
        .where(Novedad.id == novedad_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    id_empleado: int | None = None,
    id_tipo_novedad: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> Sequence[Novedad]:
    stmt = (
        select(Novedad)
        .options(joinedload(Novedad.empleado), joinedload(Novedad.tipo_novedad))
        .order_by(Novedad.fecha.desc())
    )
    if id_empleado is not None:
        stmt = stmt.where(Novedad.id_empleado == id_empleado)
    if id_tipo_novedad is not None:
        stmt = stmt.where(Novedad.id_tipo_novedad == id_tipo_novedad)
    if fecha_desde is not None:
        stmt = stmt.where(Novedad.fecha >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(Novedad.fecha <= fecha_hasta)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_by_asistencia(
    session: AsyncSession, id_asistencia: int
) -> Novedad | None:
    stmt = (
        select(Novedad)
        .options(joinedload(Novedad.tipo_novedad))
        .where(Novedad.id_asistencia == id_asistencia)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    id_empleado: int,
    id_tipo_novedad: int,
    id_asistencia: int | None = None,
    fecha: date,
    observacion: str | None = None,
    now: datetime | None = None,
) -> Novedad:
    novedad = Novedad(
        id_empleado=id_empleado,
        id_tipo_novedad=id_tipo_novedad,
        id_asistencia=id_asistencia,
        fecha=fecha,
        observacion=observacion,
    )
    if now is not None:
        novedad.created_at = now
    session.add(novedad)
    await session.flush()
    return novedad
