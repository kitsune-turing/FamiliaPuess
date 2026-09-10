from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.config import get_settings
from apps.API.core.timezone import now as tz_now
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    permiso_rol_repository,
    sesion_usuario_repository,
    usuario_repository,
)
from apps.API.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_token,
)
from apps.API.security.password import hash_password, verify_password
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.auth import (
    ContrasenaIgualError,
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    RefreshTokenInvalidoError,
    SesionNoEncontradaError,
    TokenInvalidoError,
    UsuarioInactivoError,
)

logger = logging.getLogger(__name__)

_failed_attempts: dict[str, list[float]] = {}


@dataclass
class LoginResult:
    access_token: str
    refresh_token: str
    token_type: str
    usuario_id: int
    nombre: str
    username: str
    rol_codigo: str
    rol_nombre: str
    debe_cambiar_pw: bool
    permisos: list[PermisoInfo]


@dataclass
class PermisoInfo:
    modulo_codigo: str
    modulo_nombre: str
    puede_leer: bool
    puede_escribir: bool
    puede_eliminar: bool
    puede_administrar: bool


@dataclass
class RefreshResult:
    access_token: str
    refresh_token: str
    token_type: str


def _check_lockout(username: str) -> None:
    settings = get_settings()
    attempts = _failed_attempts.get(username, [])
    if not attempts:
        return
    cutoff = tz_now().timestamp() - (settings.lockout_duration_minutes * 60)
    recent = [ts for ts in attempts if ts > cutoff]
    _failed_attempts[username] = recent
    if len(recent) >= settings.max_login_attempts:
        oldest_recent = min(recent)
        seconds_left = (oldest_recent + settings.lockout_duration_minutes * 60) - tz_now().timestamp()
        minutes_left = max(1, int(seconds_left / 60) + 1)
        raise CuentaBloqueadaError(minutes_left)


def _record_failed_attempt(username: str) -> None:
    _failed_attempts.setdefault(username, []).append(tz_now().timestamp())


def _clear_failed_attempts(username: str) -> None:
    _failed_attempts.pop(username, None)


async def login(
    session: AsyncSession,
    *,
    username: str,
    password: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> LoginResult:
    _check_lockout(username)

    usuario = await usuario_repository.get_by_username(session, username)

    if usuario is None or not verify_password(password, usuario.password_hash):
        _record_failed_attempt(username)
        await _audit_failed_login(session, username, ip_address)
        raise CredencialesInvalidasError()

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)

    if usuario.id_estado != activo_id:
        await _audit_failed_login(session, username, ip_address, detalle="Usuario inactivo")
        raise UsuarioInactivoError()

    existing = await sesion_usuario_repository.get_active_by_user(session, usuario.id)
    if existing is not None:
        await sesion_usuario_repository.deactivate(session, existing.id, tz_now())

    _clear_failed_attempts(username)

    settings = get_settings()
    fecha_expira = tz_now() + timedelta(minutes=settings.access_token_expire_minutes)

    temp_session_id = str(uuid.uuid4())

    access_token = create_access_token(usuario.id, temp_session_id)
    refresh_token = create_refresh_token(usuario.id, temp_session_id)

    sesion = await sesion_usuario_repository.create(
        session,
        id_usuario=usuario.id,
        token_hash=hash_token(access_token),
        refresh_token_hash=hash_token(refresh_token),
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent and len(user_agent) > 500 else user_agent,
        fecha_expira=fecha_expira,
    )

    await usuario_repository.update_ultimo_login(session, usuario.id, tz_now())

    permisos_db = await permiso_rol_repository.get_permisos_by_rol(session, usuario.id_rol)
    permisos = [
        PermisoInfo(
            modulo_codigo=p.modulo.codigo,
            modulo_nombre=p.modulo.nombre,
            puede_leer=p.puede_leer,
            puede_escribir=p.puede_escribir,
            puede_eliminar=p.puede_eliminar,
            puede_administrar=p.puede_administrar,
        )
        for p in permisos_db
    ]

    await auditoria_repository.create(
        session,
        id_usuario=usuario.id,
        recurso=RecursoAuditoria.SESION,
        id_recurso=str(sesion.id),
        operacion=OperacionAuditoria.LOGIN,
        ip_address=ip_address,
        timestamp_accion=tz_now(),
    )

    logger.info("Login exitoso: usuario=%s, sesion=%s", username, sesion.id)

    return LoginResult(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        usuario_id=usuario.id,
        nombre=usuario.nombre,
        username=usuario.username,
        rol_codigo=usuario.rol.codigo,
        rol_nombre=usuario.rol.nombre,
        debe_cambiar_pw=usuario.debe_cambiar_pw,
        permisos=permisos,
    )


async def refresh(
    session: AsyncSession,
    *,
    refresh_token_value: str,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> RefreshResult:
    payload = decode_refresh_token(refresh_token_value)
    user_id = int(payload["sub"])

    sesion_activa = await sesion_usuario_repository.get_by_refresh_hash(
        session, hash_token(refresh_token_value)
    )
    if sesion_activa is None:
        raise RefreshTokenInvalidoError()

    if sesion_activa.fecha_expira < tz_now():
        await sesion_usuario_repository.deactivate(session, sesion_activa.id, tz_now())
        raise RefreshTokenInvalidoError()

    usuario = await usuario_repository.get_by_id(session, user_id)
    if usuario is None:
        raise RefreshTokenInvalidoError()
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if usuario.id_estado != activo_id:
        await sesion_usuario_repository.deactivate(session, sesion_activa.id, tz_now())
        raise RefreshTokenInvalidoError()

    settings = get_settings()
    new_access = create_access_token(user_id, str(sesion_activa.id))
    new_refresh = create_refresh_token(user_id, str(sesion_activa.id))
    nueva_expira = tz_now() + timedelta(minutes=settings.access_token_expire_minutes)

    await sesion_usuario_repository.update_tokens(
        session,
        sesion_activa.id,
        token_hash=hash_token(new_access),
        refresh_token_hash=hash_token(new_refresh),
        fecha_expira=nueva_expira,
    )

    return RefreshResult(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
    )


async def logout(
    session: AsyncSession,
    *,
    access_token: str,
    ip_address: str | None = None,
) -> None:
    payload = decode_access_token(access_token)
    user_id = int(payload["sub"])

    sesion_activa = await sesion_usuario_repository.get_by_token_hash(
        session, hash_token(access_token)
    )
    if sesion_activa is None:
        raise SesionNoEncontradaError()

    await sesion_usuario_repository.deactivate(session, sesion_activa.id, tz_now())

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.SESION,
        id_recurso=str(sesion_activa.id),
        operacion=OperacionAuditoria.LOGOUT,
        ip_address=ip_address,
        timestamp_accion=tz_now(),
    )

    logger.info("Logout exitoso: usuario_id=%d, sesion=%s", user_id, sesion_activa.id)


async def validate_token(
    session: AsyncSession, access_token: str
) -> dict:
    payload = decode_access_token(access_token)
    sesion_activa = await sesion_usuario_repository.get_by_token_hash(
        session, hash_token(access_token)
    )
    if sesion_activa is None:
        raise TokenInvalidoError()
    if sesion_activa.fecha_expira < tz_now():
        await sesion_usuario_repository.deactivate(session, sesion_activa.id, tz_now())
        raise TokenInvalidoError()

    usuario = await usuario_repository.get_by_id(session, int(payload["sub"]))
    if usuario is None:
        raise TokenInvalidoError()
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if usuario.id_estado != activo_id:
        await sesion_usuario_repository.deactivate(session, sesion_activa.id, tz_now())
        raise UsuarioInactivoError()

    payload["debe_cambiar_pw"] = usuario.debe_cambiar_pw
    payload["id_rol"] = usuario.id_rol
    return payload


async def get_permisos_usuario(
    session: AsyncSession, id_rol: int
) -> list[PermisoInfo]:
    permisos_db = await permiso_rol_repository.get_permisos_by_rol(session, id_rol)
    return [
        PermisoInfo(
            modulo_codigo=p.modulo.codigo,
            modulo_nombre=p.modulo.nombre,
            puede_leer=p.puede_leer,
            puede_escribir=p.puede_escribir,
            puede_eliminar=p.puede_eliminar,
            puede_administrar=p.puede_administrar,
        )
        for p in permisos_db
    ]


async def change_password(
    session: AsyncSession,
    *,
    user_id: int,
    current_password: str,
    new_password: str,
    ip_address: str | None = None,
) -> None:
    usuario = await usuario_repository.get_by_id(session, user_id)
    if usuario is None:
        raise TokenInvalidoError()

    if not verify_password(current_password, usuario.password_hash):
        raise CredencialesInvalidasError()

    if current_password == new_password:
        raise ContrasenaIgualError()

    new_hash = hash_password(new_password)
    ahora = tz_now()
    await usuario_repository.update_password(session, user_id, new_hash, ahora)

    await sesion_usuario_repository.deactivate_all_for_user(session, user_id, ahora)

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=str(user_id),
        operacion=OperacionAuditoria.CAMBIO_CONTRASENA,
        ip_address=ip_address,
        timestamp_accion=ahora,
    )

    logger.info("Cambio de contraseña exitoso: usuario_id=%d", user_id)


async def _audit_failed_login(
    session: AsyncSession,
    username: str,
    ip_address: str | None,
    detalle: str | None = None,
) -> None:
    await auditoria_repository.create(
        session,
        id_usuario=None,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=None,
        operacion=OperacionAuditoria.LOGIN_FALLIDO,
        ip_address=ip_address,
        detalle=detalle or f"Intento fallido con username: {username}",
        timestamp_accion=tz_now(),
    )
