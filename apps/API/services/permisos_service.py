from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.permiso_rol import PermisoRol
from apps.API.repositories import (
    auditoria_repository,
    cat_rol_repository,
    modulo_repository,
    permiso_rol_repository,
)
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.permisos import (
    ModuloNoEncontradoError,
    PermisoDuplicadoError,
    PermisoNoEncontradoError,
)
from shared.exceptions.roles import RolNoEncontradoError

logger = logging.getLogger(__name__)


async def list_permisos_by_rol(
    session: AsyncSession, rol_id: int
) -> list[PermisoRol]:
    rol = await cat_rol_repository.get_by_id(session, rol_id)
    if rol is None:
        raise RolNoEncontradoError(rol_id)
    return await permiso_rol_repository.get_permisos_by_rol(session, rol_id)


async def create_permiso(
    session: AsyncSession,
    rol_id: int,
    *,
    id_modulo: int,
    puede_leer: bool = False,
    puede_escribir: bool = False,
    puede_eliminar: bool = False,
    puede_administrar: bool = False,
    user_id: int,
    ip_address: str | None = None,
) -> PermisoRol:
    rol = await cat_rol_repository.get_by_id(session, rol_id)
    if rol is None:
        raise RolNoEncontradoError(rol_id)

    modulo = await modulo_repository.get_by_id(session, id_modulo)
    if modulo is None:
        raise ModuloNoEncontradoError(id_modulo)

    existing = await permiso_rol_repository.get_by_rol_and_modulo(
        session, rol_id, id_modulo
    )
    if existing is not None:
        raise PermisoDuplicadoError(rol_id, modulo.codigo)

    permiso = await permiso_rol_repository.create(
        session,
        id_rol=rol_id,
        id_modulo=id_modulo,
        puede_leer=puede_leer,
        puede_escribir=puede_escribir,
        puede_eliminar=puede_eliminar,
        puede_administrar=puede_administrar,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.PERMISO,
        id_recurso=str(permiso.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "id_rol": rol_id,
            "modulo": modulo.codigo,
            "puede_leer": puede_leer,
            "puede_escribir": puede_escribir,
            "puede_eliminar": puede_eliminar,
            "puede_administrar": puede_administrar,
        },
        ip_address=ip_address,
        timestamp_accion=tz_now(),
    )

    logger.info(
        "Permiso creado: rol=%d, modulo=%s, id=%d",
        rol_id,
        modulo.codigo,
        permiso.id,
    )
    return permiso


async def update_permiso(
    session: AsyncSession,
    permiso_id: int,
    *,
    puede_leer: bool | None = None,
    puede_escribir: bool | None = None,
    puede_eliminar: bool | None = None,
    puede_administrar: bool | None = None,
    user_id: int,
    ip_address: str | None = None,
) -> PermisoRol:
    permiso = await permiso_rol_repository.get_by_id(session, permiso_id)
    if permiso is None:
        raise PermisoNoEncontradoError(permiso_id)

    valor_anterior = {
        "puede_leer": permiso.puede_leer,
        "puede_escribir": permiso.puede_escribir,
        "puede_eliminar": permiso.puede_eliminar,
        "puede_administrar": permiso.puede_administrar,
    }

    values: dict[str, bool] = {}
    if puede_leer is not None:
        values["puede_leer"] = puede_leer
    if puede_escribir is not None:
        values["puede_escribir"] = puede_escribir
    if puede_eliminar is not None:
        values["puede_eliminar"] = puede_eliminar
    if puede_administrar is not None:
        values["puede_administrar"] = puede_administrar

    if values:
        await permiso_rol_repository.update_permiso(session, permiso_id, **values)

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.PERMISO,
        id_recurso=str(permiso_id),
        operacion=OperacionAuditoria.CAMBIO_PERMISOS,
        valor_anterior=valor_anterior,
        valor_nuevo=values,
        ip_address=ip_address,
        timestamp_accion=tz_now(),
    )

    logger.info("Permiso actualizado: id=%d", permiso_id)
    updated = await permiso_rol_repository.get_by_id(session, permiso_id)
    return updated


async def delete_permiso(
    session: AsyncSession,
    permiso_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    permiso = await permiso_rol_repository.get_by_id(session, permiso_id)
    if permiso is None:
        raise PermisoNoEncontradoError(permiso_id)

    valor_anterior = {
        "id_rol": permiso.id_rol,
        "id_modulo": permiso.id_modulo,
        "puede_leer": permiso.puede_leer,
        "puede_escribir": permiso.puede_escribir,
        "puede_eliminar": permiso.puede_eliminar,
        "puede_administrar": permiso.puede_administrar,
    }

    await permiso_rol_repository.remove(session, permiso_id)

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.PERMISO,
        id_recurso=str(permiso_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior=valor_anterior,
        ip_address=ip_address,
        timestamp_accion=tz_now(),
    )

    logger.info("Permiso eliminado: id=%d", permiso_id)
