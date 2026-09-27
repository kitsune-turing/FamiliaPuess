from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.horario import Horario
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    horario_repository,
    sede_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from shared.exceptions.horarios import (
    HorarioInmutableError,
    HorarioNoEncontradoError,
    HorarioToleranciaInvalidaError,
    HorarioVigenciaInvalidaError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

logger = logging.getLogger(__name__)

_TOLERANCIA_MAX = 120


def _validar_tolerancia(valor: int) -> None:
    if valor < 0 or valor > _TOLERANCIA_MAX:
        raise HorarioToleranciaInvalidaError()


def _validar_vigencia(vigente_desde: date, vigente_hasta: date | None) -> None:
    if vigente_hasta is not None and vigente_hasta < vigente_desde:
        raise HorarioVigenciaInvalidaError()


async def _validar_sede_activa(session: AsyncSession, id_sede: int) -> None:
    sede = await sede_repository.get_by_id(session, id_sede)
    if sede is None:
        raise SedeNoEncontradaError(id_sede)
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if sede.id_estado != activo_id:
        raise SedeInactivaError(id_sede)


async def list_horarios(
    session: AsyncSession,
    *,
    id_sede: int | None = None,
    solo_vigentes: bool = False,
) -> Sequence[Horario]:
    return await horario_repository.get_all(
        session,
        id_sede=id_sede,
        solo_vigentes=solo_vigentes,
    )


async def get_horario(session: AsyncSession, horario_id: int) -> Horario:
    horario = await horario_repository.get_by_id(session, horario_id)
    if horario is None:
        raise HorarioNoEncontradoError(horario_id)
    return horario


async def get_horarios_vigentes_sede(
    session: AsyncSession, id_sede: int, fecha: date
) -> Sequence[Horario]:
    return await horario_repository.get_vigentes_by_sede(session, id_sede, fecha)


async def create_horario(
    session: AsyncSession,
    *,
    id_sede: int,
    hora_entrada: time,
    hora_salida: time | None = None,
    tolerancia_min: int = 15,
    nombre: str | None = None,
    vigente_desde: date,
    vigente_hasta: date | None = None,
    user_id: int,
    ip_address: str | None = None,
) -> Horario:
    _validar_tolerancia(tolerancia_min)
    _validar_vigencia(vigente_desde, vigente_hasta)

    await _validar_sede_activa(session, id_sede)

    timestamp = tz_now()

    horario = await horario_repository.create(
        session,
        id_sede=id_sede,
        hora_entrada=hora_entrada,
        hora_salida=hora_salida,
        tolerancia_min=tolerancia_min,
        nombre=nombre,
        vigente_desde=vigente_desde,
        vigente_hasta=vigente_hasta,
        now=timestamp,
    )

    await session.refresh(horario, attribute_names=["sede"])

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.HORARIO,
        id_recurso=str(horario.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "id_sede": id_sede,
            "nombre": nombre,
            "hora_entrada": str(hora_entrada),
            "hora_salida": str(hora_salida) if hora_salida else None,
            "tolerancia_min": tolerancia_min,
            "vigente_desde": str(vigente_desde),
            "vigente_hasta": str(vigente_hasta) if vigente_hasta else None,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info(
        "Horario creado: id=%d, sede=%d, entrada=%s, tolerancia=%d",
        horario.id,
        id_sede,
        hora_entrada,
        tolerancia_min,
    )
    return horario


async def update_horario(
    session: AsyncSession,
    horario_id: int,
    *,
    id_sede: int | None = None,
    nombre: str | None = None,
    hora_entrada: time | None = None,
    hora_salida: time | None = None,
    tolerancia_min: int | None = None,
    vigente_desde: date | None = None,
    vigente_hasta: date | None = None,
    user_id: int,
    ip_address: str | None = None,
) -> Horario:
    horario = await horario_repository.get_by_id(session, horario_id)
    if horario is None:
        raise HorarioNoEncontradoError(horario_id)

    if id_sede is not None:
        await _validar_sede_activa(session, id_sede)

    if tolerancia_min is not None:
        _validar_tolerancia(tolerancia_min)

    nueva_desde = vigente_desde if vigente_desde is not None else horario.vigente_desde
    nueva_hasta = vigente_hasta if vigente_hasta is not None else horario.vigente_hasta
    _validar_vigencia(nueva_desde, nueva_hasta)

    valor_anterior = {
        "id_sede": horario.id_sede,
        "nombre": horario.nombre,
        "hora_entrada": str(horario.hora_entrada),
        "hora_salida": str(horario.hora_salida) if horario.hora_salida else None,
        "tolerancia_min": horario.tolerancia_min,
        "vigente_desde": str(horario.vigente_desde),
        "vigente_hasta": str(horario.vigente_hasta) if horario.vigente_hasta else None,
    }

    if id_sede is not None:
        horario.id_sede = id_sede
    if nombre is not None:
        horario.nombre = nombre
    if hora_entrada is not None:
        horario.hora_entrada = hora_entrada
    if hora_salida is not None:
        horario.hora_salida = hora_salida
    if tolerancia_min is not None:
        horario.tolerancia_min = tolerancia_min
    if vigente_desde is not None:
        horario.vigente_desde = vigente_desde
    if vigente_hasta is not None:
        horario.vigente_hasta = vigente_hasta

    await session.flush()

    valor_nuevo: dict = {}
    if id_sede is not None:
        valor_nuevo["id_sede"] = id_sede
    if nombre is not None:
        valor_nuevo["nombre"] = nombre
    if hora_entrada is not None:
        valor_nuevo["hora_entrada"] = str(hora_entrada)
    if hora_salida is not None:
        valor_nuevo["hora_salida"] = str(hora_salida)
    if tolerancia_min is not None:
        valor_nuevo["tolerancia_min"] = tolerancia_min
    if vigente_desde is not None:
        valor_nuevo["vigente_desde"] = str(vigente_desde)
    if vigente_hasta is not None:
        valor_nuevo["vigente_hasta"] = str(vigente_hasta)

    timestamp = tz_now()

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.HORARIO,
        id_recurso=str(horario_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Horario actualizado: id=%d", horario_id)
    await session.refresh(horario, attribute_names=["sede"])
    return horario


async def finalizar_horario(
    session: AsyncSession,
    horario_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    horario = await horario_repository.get_by_id(session, horario_id)
    if horario is None:
        raise HorarioNoEncontradoError(horario_id)

    timestamp = tz_now()

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.HORARIO,
        id_recurso=str(horario_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={
            "id_sede": horario.id_sede,
            "nombre": horario.nombre,
            "hora_entrada": str(horario.hora_entrada),
            "tolerancia_min": horario.tolerancia_min,
            "vigente_desde": str(horario.vigente_desde),
            "vigente_hasta": str(horario.vigente_hasta) if horario.vigente_hasta else None,
        },
        valor_nuevo=None,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    await horario_repository.hard_delete(session, horario_id)

    logger.info("Horario eliminado: id=%d", horario_id)
