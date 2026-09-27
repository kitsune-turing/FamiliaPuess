from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import date, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.novedad import Novedad
from apps.API.repositories import (
    cat_novedad_repository,
    horario_repository,
    novedad_repository,
)
from shared.constants.novedad import NovedadCodigo
from shared.exceptions.novedades import (
    NovedadNoEncontradaError,
    SedesSinHorarioError,
    TipoNovedadNoEncontradoError,
)

logger = logging.getLogger(__name__)


def _sumar_tolerancia(hora_entrada: time, tolerancia_min: int) -> time:
    dt = timedelta(hours=hora_entrada.hour, minutes=hora_entrada.minute + tolerancia_min)
    total_seconds = int(dt.total_seconds())
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    return time(hours, minutes)


async def detectar_novedad_asistencia(
    session: AsyncSession,
    *,
    id_asistencia: int,
    id_empleado: int,
    id_sede: int,
    fecha_registro: date,
    hora_registro: time,
) -> Novedad | None:
    horarios = await horario_repository.get_vigentes_by_sede(
        session, id_sede, fecha_registro
    )
    if not horarios:
        logger.warning(
            "Sede %d sin horario vigente para fecha %s, omitiendo deteccion",
            id_sede,
            fecha_registro,
        )
        return None

    horario_aplicable = None
    for h in horarios:
        limite = _sumar_tolerancia(h.hora_entrada, h.tolerancia_min)
        if hora_registro <= limite:
            return None
        if horario_aplicable is None:
            horario_aplicable = h

    if horario_aplicable is None:
        return None

    tipo = await cat_novedad_repository.get_by_codigo(session, NovedadCodigo.TARDANZA)
    if tipo is None:
        raise TipoNovedadNoEncontradoError(NovedadCodigo.TARDANZA)

    timestamp = tz_now()

    observacion = (
        f"Registro a las {hora_registro.strftime('%H:%M')} - "
        f"Entrada programada: {horario_aplicable.hora_entrada.strftime('%H:%M')} "
        f"(tolerancia: {horario_aplicable.tolerancia_min} min)"
    )

    novedad = await novedad_repository.create(
        session,
        id_empleado=id_empleado,
        id_tipo_novedad=tipo.id,
        id_asistencia=id_asistencia,
        fecha=fecha_registro,
        observacion=observacion,
        now=timestamp,
    )

    logger.info(
        "Novedad TARDANZA registrada: empleado=%d, asistencia=%d, hora=%s",
        id_empleado,
        id_asistencia,
        hora_registro,
    )

    await session.refresh(novedad, attribute_names=["empleado", "tipo_novedad"])
    return novedad


async def list_novedades(
    session: AsyncSession,
    *,
    id_empleado: int | None = None,
    id_tipo_novedad: int | None = None,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> Sequence[Novedad]:
    return await novedad_repository.get_all(
        session,
        id_empleado=id_empleado,
        id_tipo_novedad=id_tipo_novedad,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


async def get_novedad(session: AsyncSession, novedad_id: int) -> Novedad:
    novedad = await novedad_repository.get_by_id(session, novedad_id)
    if novedad is None:
        raise NovedadNoEncontradaError(novedad_id)
    return novedad


async def get_novedad_by_asistencia(
    session: AsyncSession, id_asistencia: int
) -> Novedad | None:
    return await novedad_repository.get_by_asistencia(session, id_asistencia)
