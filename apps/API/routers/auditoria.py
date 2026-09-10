from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.auditoria import AuditoriaListResponse
from apps.API.services import auditoria_service

router = APIRouter(prefix="/auditoria", tags=["auditoria"])


@router.get(
    "",
    response_model=AuditoriaListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_auditoria(
    id_usuario: int | None = Query(None, gt=0),
    recurso: str | None = Query(None, max_length=100),
    operacion: str | None = Query(None, max_length=30),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("AUDITORIA", "leer")),
) -> AuditoriaListResponse:
    return await auditoria_service.list_auditoria(
        session,
        id_usuario=id_usuario,
        recurso=recurso,
        operacion=operacion,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )
