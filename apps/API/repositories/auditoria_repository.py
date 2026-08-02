from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.auditoria import Auditoria


async def create(
    session: AsyncSession,
    *,
    id_usuario: int | None,
    recurso: str,
    id_recurso: str | None,
    operacion: str,
    ip_address: str | None = None,
    detalle: str | None = None,
    valor_anterior: dict | None = None,
    valor_nuevo: dict | None = None,
    timestamp_accion: datetime,
) -> Auditoria:
    registro = Auditoria(
        id_usuario=id_usuario,
        recurso=recurso,
        id_recurso=id_recurso,
        operacion=operacion,
        ip_address=ip_address,
        detalle=detalle,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        timestamp_accion=timestamp_accion,
    )
    session.add(registro)
    await session.flush()
    return registro


async def get_all(
    session: AsyncSession,
    *,
    id_usuario: int | None = None,
    recurso: str | None = None,
    operacion: str | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Auditoria]:
    stmt = select(Auditoria)

    if id_usuario is not None:
        stmt = stmt.where(Auditoria.id_usuario == id_usuario)
    if recurso is not None:
        stmt = stmt.where(Auditoria.recurso == recurso)
    if operacion is not None:
        stmt = stmt.where(Auditoria.operacion == operacion)
    if fecha_desde is not None:
        stmt = stmt.where(func.date(Auditoria.timestamp_accion) >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(func.date(Auditoria.timestamp_accion) <= fecha_hasta)

    stmt = stmt.order_by(Auditoria.timestamp_accion.desc())
    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    return list(result.scalars().all())


async def count(
    session: AsyncSession,
    *,
    id_usuario: int | None = None,
    recurso: str | None = None,
    operacion: str | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> int:
    stmt = select(func.count(Auditoria.id))

    if id_usuario is not None:
        stmt = stmt.where(Auditoria.id_usuario == id_usuario)
    if recurso is not None:
        stmt = stmt.where(Auditoria.recurso == recurso)
    if operacion is not None:
        stmt = stmt.where(Auditoria.operacion == operacion)
    if fecha_desde is not None:
        stmt = stmt.where(func.date(Auditoria.timestamp_accion) >= fecha_desde)
    if fecha_hasta is not None:
        stmt = stmt.where(func.date(Auditoria.timestamp_accion) <= fecha_hasta)

    result = await session.execute(stmt)
    return result.scalar_one()
