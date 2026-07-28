from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    config_general_repository,
    dispositivo_repository,
    empleado_repository,
    sede_repository,
    usuario_repository,
)
from shared.constants.configuracion import ConfigClave
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.configuration import SetupIncompletoError

logger = logging.getLogger(__name__)


async def get_setup_status(
    session: AsyncSession,
    user_id: int,
) -> dict:
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)

    setup_flag = await config_general_repository.get_valor_or_none(
        session, ConfigClave.SETUP_COMPLETADO
    )
    if setup_flag == "true":
        return {
            "setup_completado": True,
            "pasos": [],
        }

    usuario = await usuario_repository.get_by_id(session, user_id)
    pw_changed = usuario is not None and not usuario.debe_cambiar_pw

    sedes_count = await sede_repository.count_by_estado(session, activo_id)
    dispositivos_count = await dispositivo_repository.count_by_estado(session, activo_id)
    empleados_count = await empleado_repository.count_by_estado(session, activo_id)

    pasos = [
        {
            "clave": "CAMBIO_CONTRASENA",
            "descripcion": "Cambiar contrasena inicial",
            "completado": pw_changed,
        },
        {
            "clave": "SEDE_REGISTRADA",
            "descripcion": "Registrar al menos una sede",
            "completado": sedes_count > 0,
        },
        {
            "clave": "DISPOSITIVO_REGISTRADO",
            "descripcion": "Registrar al menos un dispositivo",
            "completado": dispositivos_count > 0,
        },
        {
            "clave": "EMPLEADO_REGISTRADO",
            "descripcion": "Registrar al menos un empleado",
            "completado": empleados_count > 0,
        },
    ]

    all_done = all(p["completado"] for p in pasos)

    return {
        "setup_completado": all_done,
        "pasos": pasos,
    }


async def completar_setup(
    session: AsyncSession,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    status = await get_setup_status(session, user_id)

    pasos_pendientes = [p for p in status["pasos"] if not p["completado"]]
    if pasos_pendientes:
        nombres = ", ".join(p["clave"] for p in pasos_pendientes)
        raise SetupIncompletoError(nombres)

    timestamp = tz_now()
    await config_general_repository.upsert(
        session,
        clave=ConfigClave.SETUP_COMPLETADO,
        valor="true",
        categoria="SISTEMA",
        tipo_dato="BOOLEAN",
        descripcion="Indica si la configuracion inicial fue completada",
        updated_by=user_id,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.CONFIGURACION,
        id_recurso=ConfigClave.SETUP_COMPLETADO,
        operacion=OperacionAuditoria.UPDATE,
        valor_nuevo={"SETUP_COMPLETADO": "true"},
        detalle="Configuracion inicial completada",
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Setup inicial completado por usuario id=%d", user_id)
