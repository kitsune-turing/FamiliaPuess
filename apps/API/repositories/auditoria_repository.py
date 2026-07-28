from datetime import datetime

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
