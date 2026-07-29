from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.novedades import (
    NovedadListResponse,
    NovedadResponse,
)
from apps.API.services import novedades_service

router = APIRouter(prefix="/novedades", tags=["novedades"])


@router.get(
    "",
    response_model=NovedadListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_novedades(
    id_empleado: int | None = Query(None, gt=0),
    id_tipo_novedad: int | None = Query(None, gt=0),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("NOVEDADES", "leer")),
) -> NovedadListResponse:
    novedades = await novedades_service.list_novedades(
        session,
        id_empleado=id_empleado,
        id_tipo_novedad=id_tipo_novedad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    items = [NovedadResponse.from_model(n) for n in novedades]
    return NovedadListResponse(items=items, total=len(items))


@router.get(
    "/{novedad_id}",
    response_model=NovedadResponse,
    status_code=status.HTTP_200_OK,
)
async def get_novedad(
    novedad_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("NOVEDADES", "leer")),
) -> NovedadResponse:
    novedad = await novedades_service.get_novedad(session, novedad_id)
    return NovedadResponse.from_model(novedad)
