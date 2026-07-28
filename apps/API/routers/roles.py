from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.roles import (
    CreateRolRequest,
    RolListResponse,
    RolResponse,
    UpdateRolRequest,
)
from apps.API.services import roles_service

router = APIRouter(prefix="/roles", tags=["roles"])


def _extract_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


@router.get(
    "",
    response_model=RolListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_roles(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "leer")),
) -> RolListResponse:
    roles = await roles_service.list_roles(session)
    items = [RolResponse.model_validate(r) for r in roles]
    return RolListResponse(items=items, total=len(items))


@router.get(
    "/{rol_id}",
    response_model=RolResponse,
    status_code=status.HTTP_200_OK,
)
async def get_rol(
    rol_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "leer")),
) -> RolResponse:
    rol = await roles_service.get_rol(session, rol_id)
    return RolResponse.model_validate(rol)


@router.post(
    "",
    response_model=RolResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_rol(
    payload: CreateRolRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "escribir")),
) -> RolResponse:
    rol = await roles_service.create_rol(
        session,
        codigo=payload.codigo,
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return RolResponse.model_validate(rol)


@router.put(
    "/{rol_id}",
    response_model=RolResponse,
    status_code=status.HTTP_200_OK,
)
async def update_rol(
    rol_id: int,
    payload: UpdateRolRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "escribir")),
) -> RolResponse:
    kwargs: dict = {
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "nombre" in payload.model_fields_set:
        kwargs["nombre"] = payload.nombre
    if "descripcion" in payload.model_fields_set:
        kwargs["descripcion"] = payload.descripcion

    rol = await roles_service.update_rol(session, rol_id, **kwargs)
    return RolResponse.model_validate(rol)


@router.delete(
    "/{rol_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rol(
    rol_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "eliminar")),
) -> None:
    await roles_service.deactivate_rol(
        session,
        rol_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
