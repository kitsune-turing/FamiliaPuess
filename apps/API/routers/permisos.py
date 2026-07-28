from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.permisos import (
    CreatePermisoRequest,
    PermisoRolListResponse,
    PermisoRolResponse,
    UpdatePermisoRequest,
)
from apps.API.services import permisos_service

router = APIRouter(prefix="/roles/{rol_id}/permisos", tags=["permisos"])


def _extract_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


def _to_response(p) -> PermisoRolResponse:
    return PermisoRolResponse(
        id=p.id,
        id_rol=p.id_rol,
        id_modulo=p.id_modulo,
        modulo_codigo=p.modulo.codigo,
        modulo_nombre=p.modulo.nombre,
        puede_leer=p.puede_leer,
        puede_escribir=p.puede_escribir,
        puede_eliminar=p.puede_eliminar,
        puede_administrar=p.puede_administrar,
    )


@router.get(
    "",
    response_model=PermisoRolListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_permisos(
    rol_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "leer")),
) -> PermisoRolListResponse:
    permisos = await permisos_service.list_permisos_by_rol(session, rol_id)
    items = [_to_response(p) for p in permisos]
    return PermisoRolListResponse(items=items, total=len(items))


@router.post(
    "",
    response_model=PermisoRolResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permiso(
    rol_id: int,
    payload: CreatePermisoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "administrar")),
) -> PermisoRolResponse:
    permiso = await permisos_service.create_permiso(
        session,
        rol_id,
        id_modulo=payload.id_modulo,
        puede_leer=payload.puede_leer,
        puede_escribir=payload.puede_escribir,
        puede_eliminar=payload.puede_eliminar,
        puede_administrar=payload.puede_administrar,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return _to_response(permiso)


@router.put(
    "/{permiso_id}",
    response_model=PermisoRolResponse,
    status_code=status.HTTP_200_OK,
)
async def update_permiso(
    rol_id: int,
    permiso_id: int,
    payload: UpdatePermisoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "administrar")),
) -> PermisoRolResponse:
    kwargs: dict = {
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "puede_leer" in payload.model_fields_set:
        kwargs["puede_leer"] = payload.puede_leer
    if "puede_escribir" in payload.model_fields_set:
        kwargs["puede_escribir"] = payload.puede_escribir
    if "puede_eliminar" in payload.model_fields_set:
        kwargs["puede_eliminar"] = payload.puede_eliminar
    if "puede_administrar" in payload.model_fields_set:
        kwargs["puede_administrar"] = payload.puede_administrar

    permiso = await permisos_service.update_permiso(session, permiso_id, **kwargs)
    return _to_response(permiso)


@router.delete(
    "/{permiso_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_permiso(
    rol_id: int,
    permiso_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("ROLES", "administrar")),
) -> None:
    await permisos_service.delete_permiso(
        session,
        permiso_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
