from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.cat_rol import CatRol
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    cat_rol_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.constants.rol import RolCodigo
from apps.API.utils.concurrency import check_concurrency
from shared.exceptions.roles import (
    RolCodigoDuplicadoError,
    RolNoEncontradoError,
    RolProtegidoError,
    RolTieneUsuariosError,
)

logger = logging.getLogger(__name__)

PROTECTED_ROLES = {RolCodigo.SUPER_ADMIN, RolCodigo.ADMIN}


async def list_roles(session: AsyncSession) -> Sequence[CatRol]:
    return await cat_rol_repository.get_all(session)


async def get_rol(session: AsyncSession, rol_id: int) -> CatRol:
    rol = await cat_rol_repository.get_by_id(session, rol_id)
    if rol is None:
        raise RolNoEncontradoError(rol_id)
    return rol


async def create_rol(
    session: AsyncSession,
    *,
    codigo: str,
    nombre: str,
    descripcion: str | None = None,
    user_id: int,
    ip_address: str | None = None,
) -> CatRol:
    existing = await cat_rol_repository.get_by_codigo(session, codigo)
    if existing is not None:
        raise RolCodigoDuplicadoError(codigo)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    timestamp = tz_now()

    rol = await cat_rol_repository.create(
        session,
        codigo=codigo,
        nombre=nombre,
        id_estado=activo_id,
        descripcion=descripcion,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.ROL,
        id_recurso=str(rol.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={"codigo": codigo, "nombre": nombre, "descripcion": descripcion},
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Rol creado: codigo=%s, id=%d", codigo, rol.id)
    return rol


async def update_rol(
    session: AsyncSession,
    rol_id: int,
    *,
    nombre: str | None = None,
    descripcion: str | None = ...,
    updated_at: datetime,
    user_id: int,
    ip_address: str | None = None,
) -> CatRol:
    rol = await cat_rol_repository.get_by_id(session, rol_id)
    if rol is None:
        raise RolNoEncontradoError(rol_id)

    check_concurrency(rol.updated_at, updated_at, "rol", rol_id)

    valor_anterior = {
        "nombre": rol.nombre,
        "descripcion": rol.descripcion,
    }

    timestamp = tz_now()
    await cat_rol_repository.update_rol(
        session,
        rol_id,
        nombre=nombre,
        descripcion=descripcion,
        now=timestamp,
    )

    valor_nuevo: dict = {}
    if nombre is not None:
        valor_nuevo["nombre"] = nombre
    if descripcion is not ...:
        valor_nuevo["descripcion"] = descripcion

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.ROL,
        id_recurso=str(rol_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Rol actualizado: id=%d", rol_id)
    updated = await cat_rol_repository.get_by_id(session, rol_id)
    return updated


async def delete_rol(
    session: AsyncSession,
    rol_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    rol = await cat_rol_repository.get_by_id(session, rol_id)
    if rol is None:
        raise RolNoEncontradoError(rol_id)

    if rol.codigo in PROTECTED_ROLES:
        raise RolProtegidoError(rol.codigo)

    user_count = await cat_rol_repository.count_usuarios_by_rol(session, rol_id)
    if user_count > 0:
        raise RolTieneUsuariosError(rol.codigo)

    timestamp = tz_now()

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.ROL,
        id_recurso=str(rol_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={"codigo": rol.codigo, "nombre": rol.nombre},
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    await cat_rol_repository.hard_delete(session, rol_id)

    logger.info("Rol eliminado: id=%d, codigo=%s", rol_id, rol.codigo)
