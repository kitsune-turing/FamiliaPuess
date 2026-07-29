from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.dispositivo import Dispositivo
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    dispositivo_repository,
    sede_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.device import (
    DispositivoNoEncontradoPorIdError,
    IdentificadorDuplicadoError,
    IdentificadorFormatoInvalidoError,
    SedeYaTieneDispositivoError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

logger = logging.getLogger(__name__)

_IDENTIFICADOR_RE = re.compile(r"^[a-zA-Z0-9\.\-\_\:]+$")


def _validar_identificador(identificador: str) -> None:
    if not _IDENTIFICADOR_RE.match(identificador):
        raise IdentificadorFormatoInvalidoError()


async def list_dispositivos(
    session: AsyncSession,
    *,
    identificador: str | None = None,
    id_sede: int | None = None,
    id_estado: int | None = None,
) -> Sequence[Dispositivo]:
    return await dispositivo_repository.get_all(
        session,
        identificador=identificador,
        id_sede=id_sede,
        id_estado=id_estado,
    )


async def get_dispositivo(session: AsyncSession, dispositivo_id: int) -> Dispositivo:
    dispositivo = await dispositivo_repository.get_by_id(session, dispositivo_id)
    if dispositivo is None:
        raise DispositivoNoEncontradoPorIdError(dispositivo_id)
    return dispositivo


async def create_dispositivo(
    session: AsyncSession,
    *,
    identificador: str,
    id_sede: int,
    descripcion: str | None = None,
    user_id: int,
    ip_address: str | None = None,
) -> Dispositivo:
    _validar_identificador(identificador)

    existing = await dispositivo_repository.get_by_identificador(session, identificador)
    if existing is not None:
        raise IdentificadorDuplicadoError(identificador)

    sede = await sede_repository.get_by_id(session, id_sede)
    if sede is None:
        raise SedeNoEncontradaError(id_sede)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if sede.id_estado != activo_id:
        raise SedeInactivaError(id_sede)

    active_device = await dispositivo_repository.get_active_by_sede(
        session, id_sede, activo_id
    )
    if active_device is not None:
        raise SedeYaTieneDispositivoError(id_sede)

    timestamp = tz_now()

    dispositivo = await dispositivo_repository.create(
        session,
        identificador=identificador,
        id_sede=id_sede,
        id_estado=activo_id,
        descripcion=descripcion,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.DISPOSITIVO,
        id_recurso=str(dispositivo.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "identificador": identificador,
            "id_sede": id_sede,
            "descripcion": descripcion,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info(
        "Dispositivo creado: identificador=%s, sede=%d, id=%d",
        identificador,
        id_sede,
        dispositivo.id,
    )
    return dispositivo


async def update_dispositivo(
    session: AsyncSession,
    dispositivo_id: int,
    *,
    identificador: str | None = None,
    descripcion: str | None = None,
    updated_at: datetime,
    user_id: int,
    ip_address: str | None = None,
) -> Dispositivo:
    dispositivo = await dispositivo_repository.get_by_id(session, dispositivo_id)
    if dispositivo is None:
        raise DispositivoNoEncontradoPorIdError(dispositivo_id)

    if dispositivo.updated_at != updated_at:
        raise ConflictoConcurrenciaError("dispositivo", dispositivo_id)

    valor_anterior = {
        "identificador": dispositivo.identificador,
        "descripcion": dispositivo.descripcion,
    }

    if identificador is not None:
        _validar_identificador(identificador)
        if identificador != dispositivo.identificador:
            existing = await dispositivo_repository.get_by_identificador(
                session, identificador
            )
            if existing is not None:
                raise IdentificadorDuplicadoError(identificador)

    timestamp = tz_now()
    await dispositivo_repository.update_dispositivo(
        session,
        dispositivo_id,
        identificador=identificador,
        descripcion=descripcion,
        now=timestamp,
    )

    valor_nuevo: dict = {}
    if identificador is not None:
        valor_nuevo["identificador"] = identificador
    if descripcion is not None:
        valor_nuevo["descripcion"] = descripcion

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.DISPOSITIVO,
        id_recurso=str(dispositivo_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Dispositivo actualizado: id=%d", dispositivo_id)
    updated = await dispositivo_repository.get_by_id(session, dispositivo_id)
    return updated


async def deactivate_dispositivo(
    session: AsyncSession,
    dispositivo_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    dispositivo = await dispositivo_repository.get_by_id(session, dispositivo_id)
    if dispositivo is None:
        raise DispositivoNoEncontradoPorIdError(dispositivo_id)

    inactivo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.INACTIVO
    )
    timestamp = tz_now()

    await dispositivo_repository.update_dispositivo(
        session, dispositivo_id, id_estado=inactivo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.DISPOSITIVO,
        id_recurso=str(dispositivo_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={
            "identificador": dispositivo.identificador,
            "id_sede": dispositivo.id_sede,
            "id_estado": dispositivo.id_estado,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info(
        "Dispositivo desactivado: id=%d, identificador=%s",
        dispositivo_id,
        dispositivo.identificador,
    )


async def activate_dispositivo(
    session: AsyncSession,
    dispositivo_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> Dispositivo:
    dispositivo = await dispositivo_repository.get_by_id(session, dispositivo_id)
    if dispositivo is None:
        raise DispositivoNoEncontradoPorIdError(dispositivo_id)

    activo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.ACTIVO
    )

    active_device = await dispositivo_repository.get_active_by_sede(
        session, dispositivo.id_sede, activo_id
    )
    if active_device is not None and active_device.id != dispositivo_id:
        raise SedeYaTieneDispositivoError(dispositivo.id_sede)

    timestamp = tz_now()

    await dispositivo_repository.update_dispositivo(
        session, dispositivo_id, id_estado=activo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.DISPOSITIVO,
        id_recurso=str(dispositivo_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior={"id_estado": dispositivo.id_estado},
        valor_nuevo={"id_estado": activo_id},
        detalle="Reactivacion de dispositivo",
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Dispositivo reactivado: id=%d", dispositivo_id)
    updated = await dispositivo_repository.get_by_id(session, dispositivo_id)
    return updated
