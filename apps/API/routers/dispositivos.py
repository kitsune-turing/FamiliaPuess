from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.dispositivos import (
    CreateDispositivoRequest,
    DispositivoListResponse,
    DispositivoResponse,
    UpdateDispositivoRequest,
)
from apps.API.services import dispositivos_service
from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/dispositivos", tags=["dispositivos"])


@router.get(
    "",
    response_model=DispositivoListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_dispositivos(
    identificador: str | None = Query(None),
    id_sede: int | None = Query(None, gt=0),
    id_estado: int | None = Query(None, gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "leer")),
) -> DispositivoListResponse:
    dispositivos = await dispositivos_service.list_dispositivos(
        session,
        identificador=identificador,
        id_sede=id_sede,
        id_estado=id_estado,
    )
    items = [DispositivoResponse.from_model(d) for d in dispositivos]
    return DispositivoListResponse(items=items, total=len(items))


@router.get(
    "/{dispositivo_id}",
    response_model=DispositivoResponse,
    status_code=status.HTTP_200_OK,
)
async def get_dispositivo(
    dispositivo_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "leer")),
) -> DispositivoResponse:
    dispositivo = await dispositivos_service.get_dispositivo(session, dispositivo_id)
    return DispositivoResponse.from_model(dispositivo)


@router.post(
    "",
    response_model=DispositivoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dispositivo(
    payload: CreateDispositivoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "escribir")),
) -> DispositivoResponse:
    dispositivo = await dispositivos_service.create_dispositivo(
        session,
        identificador=payload.identificador,
        id_sede=payload.id_sede,
        descripcion=payload.descripcion,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return DispositivoResponse.from_model(dispositivo)


@router.put(
    "/{dispositivo_id}",
    response_model=DispositivoResponse,
    status_code=status.HTTP_200_OK,
)
async def update_dispositivo(
    dispositivo_id: int,
    payload: UpdateDispositivoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "escribir")),
) -> DispositivoResponse:
    kwargs: dict = {
        "updated_at": payload.updated_at,
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "identificador" in payload.model_fields_set:
        kwargs["identificador"] = payload.identificador
    if "descripcion" in payload.model_fields_set:
        kwargs["descripcion"] = payload.descripcion
    if "id_sede" in payload.model_fields_set:
        kwargs["id_sede"] = payload.id_sede

    dispositivo = await dispositivos_service.update_dispositivo(
        session, dispositivo_id, **kwargs
    )
    return DispositivoResponse.from_model(dispositivo)


@router.delete(
    "/{dispositivo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_dispositivo(
    dispositivo_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "eliminar")),
) -> None:
    await dispositivos_service.delete_dispositivo(
        session,
        dispositivo_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )


@router.post(
    "/{dispositivo_id}/activar",
    response_model=DispositivoResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_dispositivo(
    dispositivo_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("DISPOSITIVOS", "escribir")),
) -> DispositivoResponse:
    dispositivo = await dispositivos_service.activate_dispositivo(
        session,
        dispositivo_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return DispositivoResponse.from_model(dispositivo)
