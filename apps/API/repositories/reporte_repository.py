from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.asistencia import Asistencia
from apps.API.models.novedad import Novedad
from apps.API.models.reporte_semanal import ReporteSemanal


async def get_asistencias_filtradas(
    session: AsyncSession,
    *,
    id_empleado: int | None = None,
    id_sede: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> Sequence[Asistencia]:
    stmt = (
        select(Asistencia)
        .options(
            joinedload(Asistencia.empleado),
            joinedload(Asistencia.sede),
            joinedload(Asistencia.tipo_registro),
        )
        .order_by(Asistencia.fecha_registro.desc(), Asistencia.registrado_en.desc())
    )
    if id_empleado is not None:
        stmt = stmt.where(Asistencia.id_empleado == id_empleado)
    if id_sede is not None:
        stmt = stmt.where(Asistencia.id_sede == id_sede)
    if fecha_desde is not None:
        stmt = stmt.where(Asistencia.fecha_registro >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(Asistencia.fecha_registro <= fecha_hasta)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def contar_novedades_periodo(
    session: AsyncSession,
    fecha_desde: date,
    fecha_hasta: date,
) -> int:
    stmt = (
        select(func.count())
        .select_from(Novedad)
        .where(Novedad.fecha >= fecha_desde, Novedad.fecha <= fecha_hasta)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def get_novedades_por_asistencia_ids(
    session: AsyncSession,
    asistencia_ids: Sequence[int],
) -> dict[int, Novedad]:
    if not asistencia_ids:
        return {}
    stmt = (
        select(Novedad)
        .options(joinedload(Novedad.tipo_novedad))
        .where(Novedad.id_asistencia.in_(asistencia_ids))
    )
    result = await session.execute(stmt)
    novedades = result.scalars().unique().all()
    return {n.id_asistencia: n for n in novedades if n.id_asistencia is not None}


async def get_reporte_by_id(
    session: AsyncSession, reporte_id: int
) -> ReporteSemanal | None:
    stmt = select(ReporteSemanal).where(ReporteSemanal.id == reporte_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_reporte_by_periodo(
    session: AsyncSession, fecha_inicio: date, fecha_fin: date
) -> ReporteSemanal | None:
    stmt = select(ReporteSemanal).where(
        ReporteSemanal.fecha_inicio == fecha_inicio,
        ReporteSemanal.fecha_fin == fecha_fin,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_reportes(session: AsyncSession) -> Sequence[ReporteSemanal]:
    stmt = select(ReporteSemanal).order_by(ReporteSemanal.fecha_inicio.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_reporte(
    session: AsyncSession,
    *,
    fecha_inicio: date,
    fecha_fin: date,
    total_registros: int,
    total_novedades: int,
    now: datetime | None = None,
) -> ReporteSemanal:
    reporte = ReporteSemanal(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total_registros=total_registros,
        total_novedades=total_novedades,
    )
    if now is not None:
        reporte.created_at = now
    session.add(reporte)
    await session.flush()
    return reporte
