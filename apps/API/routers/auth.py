from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user, get_current_user_enforce_pw
from apps.API.schemas.auth import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    LoginRequest,
    LoginResponse,
    MeResponse,
    PermisoResponse,
    RefreshRequest,
    RefreshResponse,
)
from apps.API.repositories import usuario_repository
from apps.API.services import auth_service
from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    result = await auth_service.login(
        session,
        username=payload.username,
        password=payload.password,
        ip_address=_extract_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return LoginResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        usuario_id=result.usuario_id,
        nombre=result.nombre,
        username=result.username,
        rol_codigo=result.rol_codigo,
        rol_nombre=result.rol_nombre,
        debe_cambiar_pw=result.debe_cambiar_pw,
        permisos=[
            PermisoResponse(
                modulo_codigo=p.modulo_codigo,
                modulo_nombre=p.modulo_nombre,
                puede_leer=p.puede_leer,
                puede_escribir=p.puede_escribir,
                puede_eliminar=p.puede_eliminar,
                puede_administrar=p.puede_administrar,
            )
            for p in result.permisos
        ],
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> RefreshResponse:
    result = await auth_service.refresh(
        session,
        refresh_token_value=payload.refresh_token,
        ip_address=_extract_ip(request),
        user_agent=request.headers.get("user-agent"),
    )
    return RefreshResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> None:
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    await auth_service.logout(
        session,
        access_token=token,
        ip_address=_extract_ip(request),
    )


@router.post(
    "/change-password",
    response_model=ChangePasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
) -> ChangePasswordResponse:
    user_id = int(current_user["sub"])
    await auth_service.change_password(
        session,
        user_id=user_id,
        current_password=payload.current_password,
        new_password=payload.new_password,
        ip_address=_extract_ip(request),
    )
    return ChangePasswordResponse(message="Contrasena actualizada exitosamente")


@router.get(
    "/me",
    response_model=MeResponse,
    status_code=status.HTTP_200_OK,
)
async def me(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_enforce_pw),
) -> MeResponse:
    user_id = int(current_user["sub"])
    usuario = await usuario_repository.get_by_id(session, user_id)
    permisos = await auth_service.get_permisos_usuario(session, usuario.id_rol)

    return MeResponse(
        usuario_id=usuario.id,
        nombre=usuario.nombre,
        username=usuario.username,
        rol_codigo=usuario.rol.codigo,
        rol_nombre=usuario.rol.nombre,
        permisos=[
            PermisoResponse(
                modulo_codigo=p.modulo_codigo,
                modulo_nombre=p.modulo_nombre,
                puede_leer=p.puede_leer,
                puede_escribir=p.puede_escribir,
                puede_eliminar=p.puede_eliminar,
                puede_administrar=p.puede_administrar,
            )
            for p in permisos
        ],
    )
