from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core import timezone
from apps.API.repositories import (
    asistencia_repository,
    auditoria_repository,
    cat_estado_repository,
    cat_estado_token_repository,
    cat_tipo_registro_repository,
    config_general_repository,
    empleado_repository,
    horario_repository,
    token_qr_repository,
)
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria
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
CLAVE_EXIGIR_CODIGO = "EXIGIR_CODIGO"
CLAVE_EXIGIR_SALIDA = "EXIGIR_SALIDA"


async def _leer_bool(session: AsyncSession, clave: str) -> bool:
    raw = await config_general_repository.get_valor(session, clave)
    return raw.lower() in ("true", "1", "si", "sí")


def _determinar_tipo_registro(
    ahora: datetime,
    horarios,
) -> str:
    if not horarios:
        return TipoRegistroCodigo.ENTRADA

    for h in horarios:
        entrada_dt = datetime.combine(ahora.date(), h.hora_entrada, tzinfo=ahora.tzinfo)
        limite_entrada = entrada_dt + timedelta(minutes=h.tolerancia_min)
        if entrada_dt <= ahora <= limite_entrada:
            return TipoRegistroCodigo.ENTRADA

    for h in horarios:
        if h.hora_salida is not None:
            salida_dt = datetime.combine(ahora.date(), h.hora_salida, tzinfo=ahora.tzinfo)
            limite_salida = salida_dt + timedelta(minutes=h.tolerancia_min)
            if salida_dt <= ahora <= limite_salida:
                return TipoRegistroCodigo.SALIDA

    return TipoRegistroCodigo.ENTRADA


@dataclass(frozen=True)
class TokenValidado:
    token: str
    sede_nombre: str
    exigir_codigo: bool
    exigir_salida: bool
    tipo_registro: str


@dataclass(frozen=True)
class RegistroExitoso:
    empleado_nombre: str
    sede_nombre: str
    registrado_en: datetime
    tipo_registro: str


async def validar_token(session: AsyncSession, token_value: str) -> TokenValidado:
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
    sede = token_qr.dispositivo.sede
    if sede is None or sede.id_estado != activo_id:
        raise SedeNoDisponibleError()

    exigir_codigo = await _leer_bool(session, CLAVE_EXIGIR_CODIGO)
    exigir_salida = await _leer_bool(session, CLAVE_EXIGIR_SALIDA)

    horarios = await horario_repository.get_vigentes_by_sede(
        session, sede.id, ahora.date()
    )
    tipo_registro = _determinar_tipo_registro(ahora, horarios)

    return TokenValidado(
        token=token_value,
        sede_nombre=sede.nombre,
        exigir_codigo=exigir_codigo,
        exigir_salida=exigir_salida,
        tipo_registro=tipo_registro,
    )


async def registrar_asistencia(
    session: AsyncSession,
    *,
    token_value: str,
    documento: str,
    codigo_alfa: str,
) -> RegistroExitoso:
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

    sede = token_qr.dispositivo.sede
    if sede is None or sede.id_estado != activo_id:
        raise SedeNoDisponibleError()

    empleado = await empleado_repository.get_by_documento(session, documento)
    if empleado is None:
        raise EmpleadoNoRegistradoError()

    if empleado.id_estado != activo_id:
        raise EmpleadoInactivoError()

    exigir_codigo = await _leer_bool(session, CLAVE_EXIGIR_CODIGO)
    if exigir_codigo and token_qr.codigo_alfa != codigo_alfa:
        raise CodigoAlfaInvalidoError()

    if token_qr.dispositivo.id_estado != activo_id:
        raise DispositivoTokenNoAutorizadoError()

    activo_token_id = await cat_estado_token_repository.get_estado_token_id(
        session, EstadoTokenCodigo.ACTIVO
    )
    consumed = await token_qr_repository.try_consume_atomically(
        session,
        token_id=token_qr.id,
        id_estado_activo=activo_token_id,
        id_estado_consumido=consumido_id,
        consumido_en=ahora,
        expira_en_min=ahora,
    )
    if not consumed:
        raise TokenConsumidoError()

    exigir_salida = await _leer_bool(session, CLAVE_EXIGIR_SALIDA)
    horarios = await horario_repository.get_vigentes_by_sede(
        session, token_qr.dispositivo.id_sede, ahora.date()
    )
    tipo_codigo = _determinar_tipo_registro(ahora, horarios)

    tipo_id = await cat_tipo_registro_repository.get_tipo_registro_id(
        session, tipo_codigo
    )

    fecha_hoy = ahora.date()

    duplicado = await asistencia_repository.get_duplicado(
        session,
        id_empleado=empleado.id,
        fecha=fecha_hoy,
        id_tipo_registro=tipo_id,
    )
    if duplicado is not None:
        raise AsistenciaDuplicadaError(
            hora_anterior=duplicado.registrado_en,
            sede_anterior=duplicado.sede.nombre,
        )

    try:
        asistencia = await asistencia_repository.create(
            session,
            id_empleado=empleado.id,
            id_token_qr=token_qr.id,
            id_tipo_registro=tipo_id,
            id_sede=token_qr.dispositivo.id_sede,
            fecha_registro=fecha_hoy,
            registrado_en=ahora,
        )
    except IntegrityError:
        raise AsistenciaDuplicadaError(
            hora_anterior=ahora,
            sede_anterior=sede.nombre,
        )

    await auditoria_repository.create(
        session,
        id_usuario=None,
        recurso=RecursoAuditoria.ASISTENCIA,
        id_recurso=str(asistencia.id),
        operacion=OperacionAuditoria.INSERT,
        detalle=f"{empleado.nombre} {empleado.apellido} - {tipo_codigo} en {sede.nombre}",
        valor_nuevo={
            "empleado_documento": documento,
            "empleado_nombre": f"{empleado.nombre} {empleado.apellido}",
            "sede": sede.nombre,
            "tipo_registro": tipo_codigo,
            "fecha": str(fecha_hoy),
            "hora": ahora.strftime("%H:%M:%S"),
        },
        timestamp_accion=ahora,
    )

    return RegistroExitoso(
        empleado_nombre=f"{empleado.nombre} {empleado.apellido}",
        sede_nombre=sede.nombre,
        registrado_en=ahora,
        tipo_registro=tipo_codigo,
    )
