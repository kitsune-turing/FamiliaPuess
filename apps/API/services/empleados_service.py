from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.models.cat_cargo import CatCargo
from apps.API.models.empleado import Empleado
from apps.API.repositories import (
    auditoria_repository,
    cat_estado_repository,
    empleado_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
from apps.API.utils.concurrency import check_concurrency
from shared.exceptions.empleados import (
    DocumentoDuplicadoError,
    DocumentoFormatoInvalidoError,
    EmpleadoNoEncontradoError,
    NombreInvalidoError,
)

logger = logging.getLogger(__name__)

_DOCUMENTO_RE = re.compile(r"^[A-Za-z0-9\-]{4,30}$")
_NOMBRE_RE = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-]+$")

DEFAULT_TIPO_DOCUMENTO = 1  # CC


def _validar_documento(documento: str) -> None:
    if not _DOCUMENTO_RE.match(documento):
        raise DocumentoFormatoInvalidoError()


def _validar_nombre(valor: str, campo: str) -> None:
    if not _NOMBRE_RE.match(valor):
        raise NombreInvalidoError(campo)


async def _resolve_cargo_id(session: AsyncSession, cargo_nombre: str) -> int:
    stmt = select(CatCargo).where(CatCargo.nombre == cargo_nombre)
    result = await session.execute(stmt)
    cargo = result.scalar_one_or_none()
    if cargo is not None:
        return cargo.id
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    codigo = cargo_nombre.upper().replace(" ", "_").replace("-", "_")[:30]
    nuevo = CatCargo(codigo=codigo, nombre=cargo_nombre, id_estado=activo_id)
    session.add(nuevo)
    await session.flush()
    return nuevo.id


def _detect_tipo_documento(documento: str) -> int:
    upper = documento.upper()
    if upper.startswith("PPT"):
        return 2  # PPT
    if upper.startswith("PP"):
        return 2  # PPT
    if upper.startswith("CE"):
        return 3  # CE
    return 1  # CC


async def list_empleados(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    documento: str | None = None,
    cargo: str | None = None,
    id_estado: int | None = None,
    id_sede: int | None = None,
) -> Sequence[Empleado]:
    return await empleado_repository.get_all(
        session,
        nombre=nombre,
        documento=documento,
        cargo=cargo,
        id_estado=id_estado,
        id_sede=id_sede,
    )


async def get_empleado(session: AsyncSession, empleado_id: int) -> Empleado:
    empleado = await empleado_repository.get_by_id(session, empleado_id)
    if empleado is None:
        raise EmpleadoNoEncontradoError(empleado_id)
    return empleado


async def create_empleado(
    session: AsyncSession,
    *,
    documento: str,
    nombre: str,
    apellido: str,
    cargo: str,
    user_id: int,
    ip_address: str | None = None,
) -> Empleado:
    _validar_documento(documento)
    _validar_nombre(nombre, "nombre")
    _validar_nombre(apellido, "apellido")

    existing = await empleado_repository.get_by_documento(session, documento)
    if existing is not None:
        raise DocumentoDuplicadoError(documento)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    id_cargo = await _resolve_cargo_id(session, cargo)
    id_tipo_documento = _detect_tipo_documento(documento)
    timestamp = tz_now()

    empleado = await empleado_repository.create(
        session,
        id_tipo_documento=id_tipo_documento,
        numero_documento=documento,
        nombre=nombre,
        apellido=apellido,
        id_cargo=id_cargo,
        id_estado=activo_id,
        now=timestamp,
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.EMPLEADO,
        id_recurso=str(empleado.id),
        operacion=OperacionAuditoria.INSERT,
        valor_nuevo={
            "documento": documento,
            "nombre": nombre,
            "apellido": apellido,
            "cargo": cargo,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Empleado creado: documento=%s, id=%d", documento, empleado.id)
    return empleado


async def update_empleado(
    session: AsyncSession,
    empleado_id: int,
    *,
    documento: str | None = None,
    nombre: str | None = None,
    apellido: str | None = None,
    cargo: str | None = None,
    updated_at: datetime,
    user_id: int,
    ip_address: str | None = None,
) -> Empleado:
    empleado = await empleado_repository.get_by_id(session, empleado_id)
    if empleado is None:
        raise EmpleadoNoEncontradoError(empleado_id)

    check_concurrency(empleado.updated_at, updated_at, "empleado", empleado_id)

    valor_anterior = {
        "documento": empleado.numero_documento,
        "nombre": empleado.nombre,
        "apellido": empleado.apellido,
        "cargo": empleado.cargo.nombre if empleado.cargo else "",
    }

    if documento is not None:
        _validar_documento(documento)
        if documento != empleado.numero_documento:
            existing = await empleado_repository.get_by_documento(session, documento)
            if existing is not None:
                raise DocumentoDuplicadoError(documento)

    if nombre is not None:
        _validar_nombre(nombre, "nombre")

    if apellido is not None:
        _validar_nombre(apellido, "apellido")

    id_cargo: int | None = None
    if cargo is not None:
        id_cargo = await _resolve_cargo_id(session, cargo)

    id_tipo_documento: int | None = None
    if documento is not None:
        id_tipo_documento = _detect_tipo_documento(documento)

    timestamp = tz_now()
    await empleado_repository.update_empleado(
        session,
        empleado_id,
        id_tipo_documento=id_tipo_documento,
        numero_documento=documento,
        nombre=nombre,
        apellido=apellido,
        id_cargo=id_cargo,
        id_estado=None,
        now=timestamp,
    )

    valor_nuevo: dict = {}
    if documento is not None:
        valor_nuevo["documento"] = documento
    if nombre is not None:
        valor_nuevo["nombre"] = nombre
    if apellido is not None:
        valor_nuevo["apellido"] = apellido
    if cargo is not None:
        valor_nuevo["cargo"] = cargo

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.EMPLEADO,
        id_recurso=str(empleado_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior=valor_anterior,
        valor_nuevo=valor_nuevo,
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Empleado actualizado: id=%d", empleado_id)
    updated = await empleado_repository.get_by_id(session, empleado_id)
    return updated


async def deactivate_empleado(
    session: AsyncSession,
    empleado_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> None:
    empleado = await empleado_repository.get_by_id(session, empleado_id)
    if empleado is None:
        raise EmpleadoNoEncontradoError(empleado_id)

    inactivo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.INACTIVO
    )
    timestamp = tz_now()

    await empleado_repository.update_empleado(
        session, empleado_id, id_estado=inactivo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.EMPLEADO,
        id_recurso=str(empleado_id),
        operacion=OperacionAuditoria.DELETE,
        valor_anterior={
            "documento": empleado.numero_documento,
            "nombre": empleado.nombre,
            "apellido": empleado.apellido,
            "id_estado": empleado.id_estado,
        },
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info(
        "Empleado desactivado: id=%d, documento=%s",
        empleado_id,
        empleado.numero_documento,
    )


async def activate_empleado(
    session: AsyncSession,
    empleado_id: int,
    *,
    user_id: int,
    ip_address: str | None = None,
) -> Empleado:
    empleado = await empleado_repository.get_by_id(session, empleado_id)
    if empleado is None:
        raise EmpleadoNoEncontradoError(empleado_id)

    activo_id = await cat_estado_repository.get_estado_id(
        session, EstadoCodigo.ACTIVO
    )
    timestamp = tz_now()

    await empleado_repository.update_empleado(
        session, empleado_id, id_estado=activo_id, now=timestamp
    )

    await auditoria_repository.create(
        session,
        id_usuario=user_id,
        recurso=RecursoAuditoria.EMPLEADO,
        id_recurso=str(empleado_id),
        operacion=OperacionAuditoria.UPDATE,
        valor_anterior={"id_estado": empleado.id_estado},
        valor_nuevo={"id_estado": activo_id},
        detalle="Reactivacion de empleado",
        ip_address=ip_address,
        timestamp_accion=timestamp,
    )

    logger.info("Empleado reactivado: id=%d", empleado_id)
    updated = await empleado_repository.get_by_id(session, empleado_id)
    return updated
