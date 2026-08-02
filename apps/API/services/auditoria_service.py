from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.repositories import auditoria_repository
from apps.API.schemas.auditoria import AuditoriaListResponse, AuditoriaResponse


async def list_auditoria(
    session: AsyncSession,
    *,
    id_usuario: int | None = None,
    recurso: str | None = None,
    operacion: str | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    limit: int = 50,
    offset: int = 0,
) -> AuditoriaListResponse:
    registros = await auditoria_repository.get_all(
        session,
        id_usuario=id_usuario,
        recurso=recurso,
        operacion=operacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )
    total = await auditoria_repository.count(
        session,
        id_usuario=id_usuario,
        recurso=recurso,
        operacion=operacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    items = [AuditoriaResponse.model_validate(r) for r in registros]
    return AuditoriaListResponse(items=items, total=total)
