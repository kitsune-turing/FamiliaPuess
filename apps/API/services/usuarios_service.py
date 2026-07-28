from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.usuario import Usuario
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    cat_rol_repository,
    sesion_usuario_repository,
    usuario_repository,
)
from apps.API.security.password import hash_password
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.constants.rol import RolCodigo
from shared.exceptions.roles import RolNoEncontradoError
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.usuarios import (
    AutoDesactivacionError,
    CorreoDuplicadoError,
    RolInactivoError,
    UltimoSuperAdminError,
    UsernameDuplicadoError,
    UsuarioNoEncontradoError,
)

logger = logging.getLogger(__name__)


async def list_usuarios(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    username: str | None = None,
    id_rol: int | None = None,
    id_estado: int | None = None,
) -> Sequence[Usuario]:
    return await usuario_repository.get_all(
        session,
        nombre=nombre,
        username=username,
        id_rol=id_rol,
        id_estado=id_estado,
    )


async def get_usuario(session: AsyncSession, usuario_id: int) -> Usuario:
    usuario = await usuario_repository.get_by_id(session, usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError(usuario_id)
    return usuario


async def create_usuario(
    session: AsyncSession,
    *,
    nombre: str,
    correo: str,
    username: str,
    password: str,
    id_rol: int,
    user_id: int,
    ip_address: str | None = None,
) -> Usuario:
    existing_correo = await usuario_repository.get_by_correo(session, correo)
    if existing_correo is not None:
        raise CorreoDuplicadoError(correo)

    existing_username = await usuario_repository.get_by_username(session, username)
    if existing_username is not None:
        raise UsernameDuplicadoError(username)

    rol = await cat_rol_repository.get_by_id(session, id_rol)
    if rol is None:
        raise RolNoEncontradoError(id_rol)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if rol.id_estado != activo_id:
        raise RolInactivoError(id_rol)

    timestamp = tz_now()
    pw_hash = hash_password(password)

    usuario = await usuario_repository.create(
        session,
        nombre=nombre,
        correo=correo,
        username=username,
        password_hash=pw_hash,
        id_rol=id_rol,
        id_estado=activo_id,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=str(usuario.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "nombre": nombre,
            "correo": correo,
            "username": username,
            "id_rol": id_rol,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Usuario creado: username=%s, id=%d", username, usuario.id)
    return usuario


async def update_usuario(
    session: AsyncSession,
    usuario_id: int,
    *,
    nombre: str | None = None,
    correo: str | None = None,
    username: str | None = None,
    id_rol: int | None = None,
    updated_at: datetime,
    user_id: int,
    ip_address: str | None = None,
) -> Usuario:
    usuario = await usuario_repository.get_by_id(session, usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError(usuario_id)

    if usuario.updated_at != updated_at:
        raise ConflictoConcurrenciaError("usuario", usuario_id)

    valor_anterior = {
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "username": usuario.username,
        "id_rol": usuario.id_rol,
    }

    if correo is not None and correo != usuario.correo:
        existing = await usuario_repository.get_by_correo(session, correo)
        if existing is not None:
            raise CorreoDuplicadoError(correo)

    if username is not None and username != usuario.username:
        existing = await usuario_repository.get_by_username(session, username)
        if existing is not None:
            raise UsernameDuplicadoError(username)

    if id_rol is not None and id_rol != usuario.id_rol:
        rol = await cat_rol_repository.get_by_id(session, id_rol)
        if rol is None:
            raise RolNoEncontradoError(id_rol)
        activo_id = await cat_estado_repository.get_estado_id(
            session, EstadoCodigo.ACTIVO
        )
        if rol.id_estado != activo_id:
            raise RolInactivoError(id_rol)

    timestamp = tz_now()
    await usuario_repository.update_usuario(
        session,
        usuario_id,
        nombre=nombre,
        correo=correo,
        username=username,
        id_rol=id_rol,
        now=timestamp,
    )

    valor_nuevo: dict = {}
    if nombre is not None:
        valor_nuevo["nombre"] = nombre
    if correo is not None:
        valor_nuevo["correo"] = correo
    if username is not None:
        valor_nuevo["username"] = username
    if id_rol is not None:
        valor_nuevo["id_rol"] = id_rol

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=str(usuario_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Usuario actualizado: id=%d", usuario_id)
    updated = await usuario_repository.get_by_id(session, usuario_id)
    return updated


async def deactivate_usuario(
    session: AsyncSession,
    usuario_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> bool:
    """Deactivate a user. Returns True if the user deactivated themselves."""
    usuario = await usuario_repository.get_by_id(session, usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError(usuario_id)

    activo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.ACTIVO
    )

    rol = await cat_rol_repository.get_by_id(session, usuario.id_rol)
    if rol is not None and rol.codigo == RolCodigo.SUPER_ADMIN:
        super_admin_rol = rol
        count = await usuario_repository.count_super_admins_activos(
            session, activo_id, super_admin_rol.id
        )
        if count <= 1:
            raise UltimoSuperAdminError()

    inactivo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.INACTIVO
    )
    timestamp = tz_now()

    await usuario_repository.update_usuario(
        session, usuario_id, id_estado=inactivo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=str(usuario_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={
            "username": usuario.username,
            "nombre": usuario.nombre,
            "id_estado": usuario.id_estado,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    is_self = user_id == usuario_id
    if is_self:
        await sesion_usuario_repository.deactivate_all_for_user(
            session, usuario_id, timestamp
        )
        logger.info("Usuario desactivo su propia cuenta: id=%d", usuario_id)

    logger.info("Usuario desactivado: id=%d, username=%s", usuario_id, usuario.username)
    return is_self


async def activate_usuario(
    session: AsyncSession,
    usuario_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> Usuario:
    usuario = await usuario_repository.get_by_id(session, usuario_id)
    if usuario is None:
        raise UsuarioNoEncontradoError(usuario_id)

    activo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.ACTIVO
    )
    timestamp = tz_now()

    await usuario_repository.update_usuario(
        session, usuario_id, id_estado=activo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.USUARIO,
        id_recurso=str(usuario_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior={"id_estado": usuario.id_estado},
        valor_nuevo={"id_estado": activo_id},
        detalle="Reactivacion de usuario",
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Usuario reactivado: id=%d", usuario_id)
    updated = await usuario_repository.get_by_id(session, usuario_id)
    return updated
