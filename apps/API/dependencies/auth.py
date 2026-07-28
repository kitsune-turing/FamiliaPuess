from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.repositories import permiso_rol_repository, usuario_repository
from apps.API.services import auth_service
from shared.exceptions.auth import PermisoInsuficienteError, TokenInvalidoError

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> dict:
    return await auth_service.validate_token(session, credentials.credentials)


def require_permission(modulo_codigo: str, operacion: str) -> Callable:
    async def _check(
        current_user: dict = Depends(get_current_user),
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        user_id = int(current_user["sub"])
        usuario = await usuario_repository.get_by_id(session, user_id)
        if usuario is None:
            raise TokenInvalidoError()

        permisos = await permiso_rol_repository.get_permisos_by_rol(
            session, usuario.id_rol
        )

        for p in permisos:
            if p.modulo.codigo != modulo_codigo:
                continue
            allowed = False
            if operacion == "leer" and p.puede_leer:
                allowed = True
            elif operacion == "escribir" and p.puede_escribir:
                allowed = True
            elif operacion == "eliminar" and p.puede_eliminar:
                allowed = True
            elif operacion == "administrar" and p.puede_administrar:
                allowed = True
            if allowed:
                return current_user

        raise PermisoInsuficienteError(modulo_codigo, operacion)

    return _check
