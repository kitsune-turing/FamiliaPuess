from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core import timezone
from apps.API.repositories import (
    asistencia_repository,
    cat_estado_repository,
    cat_estado_token_repository,
    cat_tipo_registro_repository,
    empleado_repository,
    token_qr_repository,
)
from shared.constants.estado import EstadoCodigo
from shared.constants.estado_token import EstadoTokenCodigo
from shared.constants.tipo_registro import TipoRegistroCodigo
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.employee import EmpleadoInactivoError, EmpleadoNoRegistradoError
from shared.exceptions.registration import (
    CodigoAlfaInvalidoError,
    DispositivoTokenNoAutorizadoError,
    SedeNoDisponibleError,
    TokenConsumidoError,
    TokenExpiradoError,
    TokenFormatoInvalidoError,
    TokenNoEncontradoError,
)

TOKEN_MIN_LENGTH = 10


@dataclass(frozen=True)
class TokenValidado:
    token: str
    sede_nombre: str


@dataclass(frozen=True)
class RegistroExitoso:
    empleado_nombre: str
    sede_nombre: str
    registrado_en: datetime


async def validar_token(session: AsyncSession, token_value: str) -> TokenValidado:
    """Validates token for initial page access (HU-REG-001, 002, 003)."""
    if not token_value or len(token_value) < TOKEN_MIN_LENGTH:
        raise TokenFormatoInvalidoError()

    token_qr = await token_qr_repository.get_by_token(session, token_value)
    if token_qr is None:
        raise TokenNoEncontradoError()

    consumido_id = await cat_estado_token_repository.get_estado_token_id(
        session, EstadoTokenCodigo.CONSUMIDO
    )
    if token_qr.id_estado_token == consumido_id:
        raise TokenConsumidoError()

    ahora = timezone.now()
    if ahora > token_qr.expira_en:
        raise TokenExpiradoError()

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if token_qr.sede.id_estado != activo_id:
        raise SedeNoDisponibleError()

    return TokenValidado(token=token_value, sede_nombre=token_qr.sede.nombre)


async def registrar_asistencia(
    session: AsyncSession,
    *,
    token_value: str,
    documento: str,
    codigo_alfa: str,
) -> RegistroExitoso:
    """Full registration flow (HU-REG-008 through 013)."""
    if not token_value or len(token_value) < TOKEN_MIN_LENGTH:
        raise TokenFormatoInvalidoError()

    token_qr = await token_qr_repository.get_by_token(session, token_value)
    if token_qr is None:
        raise TokenNoEncontradoError()

    consumido_id = await cat_estado_token_repository.get_estado_token_id(
        session, EstadoTokenCodigo.CONSUMIDO
    )
    if token_qr.id_estado_token == consumido_id:
        raise TokenConsumidoError()

    ahora = timezone.now()
    if ahora > token_qr.expira_en:
        raise TokenExpiradoError()

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)

    if token_qr.sede.id_estado != activo_id:
        raise SedeNoDisponibleError()

    empleado = await empleado_repository.get_by_documento(session, documento)
    if empleado is None:
        raise EmpleadoNoRegistradoError()

    if empleado.id_estado != activo_id:
        raise EmpleadoInactivoError()

    if token_qr.codigo_alfa != codigo_alfa:
        raise CodigoAlfaInvalidoError()

    if token_qr.dispositivo.id_estado != activo_id:
        raise DispositivoTokenNoAutorizadoError()
    if token_qr.dispositivo.id_sede != token_qr.id_sede:
        raise DispositivoTokenNoAutorizadoError()

    tipo_entrada_id = await cat_tipo_registro_repository.get_tipo_registro_id(
        session, TipoRegistroCodigo.ENTRADA
    )

    fecha_hoy = ahora.date()

    duplicado = await asistencia_repository.get_duplicado(
        session,
        id_empleado=empleado.id,
        fecha=fecha_hoy,
        id_tipo_registro=tipo_entrada_id,
    )
    if duplicado is not None:
        raise AsistenciaDuplicadaError(
            hora_anterior=duplicado.registrado_en,
            sede_anterior=duplicado.sede.nombre,
        )

    try:
        await asistencia_repository.create(
            session,
            id_empleado=empleado.id,
            id_token_qr=token_qr.id,
            id_tipo_registro=tipo_entrada_id,
            id_sede=token_qr.id_sede,
            fecha_registro=fecha_hoy,
            registrado_en=ahora,
        )
    except IntegrityError:
        raise AsistenciaDuplicadaError(
            hora_anterior=ahora,
            sede_anterior=token_qr.sede.nombre,
        )

    await token_qr_repository.mark_consumed(
        session,
        token_id=token_qr.id,
        id_estado_consumido=consumido_id,
        consumido_en=ahora,
    )

    return RegistroExitoso(
        empleado_nombre=f"{empleado.nombre} {empleado.apellido}",
        sede_nombre=token_qr.sede.nombre,
        registrado_en=ahora,
    )
