from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.usuarios import (
    CreateUsuarioRequest,
    UpdateUsuarioRequest,
    UsuarioListResponse,
    UsuarioResponse,
)
from apps.API.services import usuarios_service
from shared.exceptions.usuarios import AutoDesactivacionError

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _extract_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


@router.get(
    "",
    response_model=UsuarioListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_usuarios(
    nombre: str | None = Query(None),
    username: str | None = Query(None),
    id_rol: int | None = Query(None, gt=0),
    id_estado: int | None = Query(None, gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "leer")),
) -> UsuarioListResponse:
    usuarios = await usuarios_service.list_usuarios(
        session,
        nombre=nombre,
        username=username,
        id_rol=id_rol,
        id_estado=id_estado,
    )
    items = [UsuarioResponse.from_model(u) for u in usuarios]
    return UsuarioListResponse(items=items, total=len(items))


@router.get(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
)
async def get_usuario(
    usuario_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "leer")),
) -> UsuarioResponse:
    usuario = await usuarios_service.get_usuario(session, usuario_id)
    return UsuarioResponse.from_model(usuario)


@router.post(
    "",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_usuario(
    payload: CreateUsuarioRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "escribir")),
) -> UsuarioResponse:
    usuario = await usuarios_service.create_usuario(
        session,
        nombre=payload.nombre,
        correo=payload.correo,
        username=payload.username,
        password=payload.password,
        id_rol=payload.id_rol,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return UsuarioResponse.from_model(usuario)


@router.put(
    "/{usuario_id}",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
)
async def update_usuario(
    usuario_id: int,
    payload: UpdateUsuarioRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "escribir")),
) -> UsuarioResponse:
    kwargs: dict = {
        "updated_at": payload.updated_at,
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "nombre" in payload.model_fields_set:
        kwargs["nombre"] = payload.nombre
    if "correo" in payload.model_fields_set:
        kwargs["correo"] = payload.correo
    if "username" in payload.model_fields_set:
        kwargs["username"] = payload.username
    if "id_rol" in payload.model_fields_set:
        kwargs["id_rol"] = payload.id_rol

    usuario = await usuarios_service.update_usuario(session, usuario_id, **kwargs)
    return UsuarioResponse.from_model(usuario)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_usuario(
    usuario_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "eliminar")),
) -> None:
    is_self = await usuarios_service.deactivate_usuario(
        session,
        usuario_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    if is_self:
        raise AutoDesactivacionError()


@router.post(
    "/{usuario_id}/activar",
    response_model=UsuarioResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_usuario(
    usuario_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("USUARIOS", "escribir")),
) -> UsuarioResponse:
    usuario = await usuarios_service.activate_usuario(
        session,
        usuario_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return UsuarioResponse.from_model(usuario)
