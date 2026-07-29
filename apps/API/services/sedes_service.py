from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.sede import Sede
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    sede_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.sedes import (
    SedeDireccionInvalidaError,
    SedeNoEncontradaError,
    SedeNombreDuplicadoError,
    SedeNombreInvalidoError,
)

logger = logging.getLogger(__name__)

_DIRECCION_RE = re.compile(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\.\,\#\-\/]+$")


_NOMBRE_RE = re.compile(r"^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-]+$")


def _validar_direccion(direccion: str) -> None:
    if not _DIRECCION_RE.match(direccion):
        raise SedeDireccionInvalidaError()


def _validar_nombre(nombre: str) -> None:
    if not _NOMBRE_RE.match(nombre):
        raise SedeNombreInvalidoError()


async def list_sedes(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    direccion: str | None = None,
    id_estado: int | None = None,
) -> Sequence[Sede]:
    return await sede_repository.get_all(
        session,
        nombre=nombre,
        direccion=direccion,
        id_estado=id_estado,
    )


async def get_sede(session: AsyncSession, sede_id: int) -> Sede:
    sede = await sede_repository.get_by_id(session, sede_id)
    if sede is None:
        raise SedeNoEncontradaError(sede_id)
    return sede


async def create_sede(
    session: AsyncSession,
    *,
    nombre: str,
    direccion: str,
    user_id: int,
    ip_address: str | None = None,
) -> Sede:
    _validar_nombre(nombre)
    _validar_direccion(direccion)

    existing = await sede_repository.get_by_nombre(session, nombre)
    if existing is not None:
        raise SedeNombreDuplicadoError(nombre)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    timestamp = tz_now()

    sede = await sede_repository.create(
        session,
        nombre=nombre,
        direccion=direccion,
        id_estado=activo_id,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.SEDE,
        id_recurso=str(sede.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "nombre": nombre,
            "direccion": direccion,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Sede creada: nombre=%s, id=%d", nombre, sede.id)
    return sede


async def update_sede(
    session: AsyncSession,
    sede_id: int,
    *,
    nombre: str | None = None,
    direccion: str | None = None,
    updated_at: datetime,
    user_id: int,
    ip_address: str | None = None,
) -> Sede:
    sede = await sede_repository.get_by_id(session, sede_id)
    if sede is None:
        raise SedeNoEncontradaError(sede_id)

    if sede.updated_at != updated_at:
        raise ConflictoConcurrenciaError("sede", sede_id)

    valor_anterior = {
        "nombre": sede.nombre,
        "direccion": sede.direccion,
    }

    if nombre is not None:
        _validar_nombre(nombre)
        if nombre != sede.nombre:
            existing = await sede_repository.get_by_nombre(session, nombre)
            if existing is not None:
                raise SedeNombreDuplicadoError(nombre)

    if direccion is not None:
        _validar_direccion(direccion)

    timestamp = tz_now()
    await sede_repository.update_sede(
        session,
        sede_id,
        nombre=nombre,
        direccion=direccion,
        now=timestamp,
    )

    valor_nuevo: dict = {}
    if nombre is not None:
        valor_nuevo["nombre"] = nombre
    if direccion is not None:
        valor_nuevo["direccion"] = direccion

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.SEDE,
        id_recurso=str(sede_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Sede actualizada: id=%d", sede_id)
    updated = await sede_repository.get_by_id(session, sede_id)
    return updated


async def deactivate_sede(
    session: AsyncSession,
    sede_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    sede = await sede_repository.get_by_id(session, sede_id)
    if sede is None:
        raise SedeNoEncontradaError(sede_id)

    inactivo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.INACTIVO
    )
    timestamp = tz_now()

    await sede_repository.update_sede(
        session, sede_id, id_estado=inactivo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.SEDE,
        id_recurso=str(sede_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={
            "nombre": sede.nombre,
            "id_estado": sede.id_estado,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Sede desactivada: id=%d, nombre=%s", sede_id, sede.nombre)


async def activate_sede(
    session: AsyncSession,
    sede_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> Sede:
    sede = await sede_repository.get_by_id(session, sede_id)
    if sede is None:
        raise SedeNoEncontradaError(sede_id)

    activo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.ACTIVO
    )
    timestamp = tz_now()

    await sede_repository.update_sede(
        session, sede_id, id_estado=activo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.SEDE,
        id_recurso=str(sede_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior={"id_estado": sede.id_estado},
        valor_nuevo={"id_estado": activo_id},
        detalle="Reactivacion de sede",
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Sede reactivada: id=%d", sede_id)
    updated = await sede_repository.get_by_id(session, sede_id)
    return updated
