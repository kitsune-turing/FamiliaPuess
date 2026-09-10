from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.sedes import (
    CreateSedeRequest,
    SedeListResponse,
    SedeResponse,
    UpdateSedeRequest,
)
from apps.API.services import sedes_service
from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/sedes", tags=["sedes"])


@router.get(
    "",
    response_model=SedeListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_sedes(
    nombre: str | None = Query(None),
    direccion: str | None = Query(None),
    id_estado: int | None = Query(None, gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "leer")),
) -> SedeListResponse:
    sedes = await sedes_service.list_sedes(
        session,
        nombre=nombre,
        direccion=direccion,
        id_estado=id_estado,
    )
    items = [SedeResponse.model_validate(s) for s in sedes]
    return SedeListResponse(items=items, total=len(items))


@router.get(
    "/{sede_id}",
    response_model=SedeResponse,
    status_code=status.HTTP_200_OK,
)
async def get_sede(
    sede_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "leer")),
) -> SedeResponse:
    sede = await sedes_service.get_sede(session, sede_id)
    return SedeResponse.model_validate(sede)


@router.post(
    "",
    response_model=SedeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_sede(
    payload: CreateSedeRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "escribir")),
) -> SedeResponse:
    sede = await sedes_service.create_sede(
        session,
        nombre=payload.nombre,
        direccion=payload.direccion,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return SedeResponse.model_validate(sede)


@router.put(
    "/{sede_id}",
    response_model=SedeResponse,
    status_code=status.HTTP_200_OK,
)
async def update_sede(
    sede_id: int,
    payload: UpdateSedeRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "escribir")),
) -> SedeResponse:
    kwargs: dict = {
        "updated_at": payload.updated_at,
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "nombre" in payload.model_fields_set:
        kwargs["nombre"] = payload.nombre
    if "direccion" in payload.model_fields_set:
        kwargs["direccion"] = payload.direccion

    sede = await sedes_service.update_sede(session, sede_id, **kwargs)
    return SedeResponse.model_validate(sede)


@router.delete(
    "/{sede_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_sede(
    sede_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "eliminar")),
) -> None:
    await sedes_service.delete_sede(
        session,
        sede_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )


@router.post(
    "/{sede_id}/activar",
    response_model=SedeResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_sede(
    sede_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("SEDES", "escribir")),
) -> SedeResponse:
    sede = await sedes_service.activate_sede(
        session,
        sede_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return SedeResponse.model_validate(sede)
