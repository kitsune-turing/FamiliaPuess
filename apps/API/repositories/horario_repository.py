from collections.abc import Sequence
from datetime import date, datetime, time

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.horario import Horario


async def get_by_id(session: AsyncSession, horario_id: int) -> Horario | None:
    stmt = (
        select(Horario)
        .options(joinedload(Horario.sede))
        .where(Horario.id == horario_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    id_sede: int | None = None,
    solo_vigentes: bool = False,
    fecha_referencia: date | None = None,
) -> Sequence[Horario]:
    stmt = (
        select(Horario)
        .options(joinedload(Horario.sede))
        .order_by(Horario.id_sede, Horario.vigente_desde.desc())
    )
    if id_sede is not None:
        stmt = stmt.where(Horario.id_sede == id_sede)
    if solo_vigentes:
        ref = fecha_referencia if fecha_referencia is not None else date.today()
        stmt = stmt.where(Horario.vigente_desde <= ref)
        stmt = stmt.where(
            (Horario.vigente_hasta.is_(None)) | (Horario.vigente_hasta >= ref)
        )
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def get_vigente_by_sede(
    session: AsyncSession, id_sede: int, fecha: date
) -> Horario | None:
    stmt = (
        select(Horario)
        .options(joinedload(Horario.sede))
        .where(Horario.id_sede == id_sede)
        .where(Horario.vigente_desde <= fecha)
        .where(
            (Horario.vigente_hasta.is_(None)) | (Horario.vigente_hasta >= fecha)
        )
        .order_by(Horario.vigente_desde.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    id_sede: int,
    hora_entrada: time,
    hora_salida: time | None = None,
    tolerancia_min: int = 15,
    nombre: str | None = None,
    vigente_desde: date,
    vigente_hasta: date | None = None,
    now: datetime | None = None,
) -> Horario:
    horario = Horario(
        id_sede=id_sede,
        nombre=nombre,
        hora_entrada=hora_entrada,
        hora_salida=hora_salida,
        tolerancia_min=tolerancia_min,
        vigente_desde=vigente_desde,
        vigente_hasta=vigente_hasta,
    )
    if now is not None:
        horario.created_at = now
    session.add(horario)
    await session.flush()
    return horario


async def set_vigente_hasta(
    session: AsyncSession,
    horario_id: int,
    vigente_hasta: date,
) -> None:
    stmt = (
        update(Horario)
        .where(Horario.id == horario_id)
        .values(vigente_hasta=vigente_hasta)
    )
    await session.execute(stmt)


async def hard_delete(session: AsyncSession, horario_id: int) -> None:
    stmt = delete(Horario).where(Horario.id == horario_id)
    await session.execute(stmt)
