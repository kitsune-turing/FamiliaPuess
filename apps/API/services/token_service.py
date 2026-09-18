import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from apps.API.core import timezone
from apps.API.repositories import (
    cat_estado_repository,
    cat_estado_token_repository,
    config_general_repository,
    dispositivo_repository,
    horario_repository,
    token_qr_repository,
)
from apps.API.utils.codigo_generator import generate_codigo
from apps.API.utils.token_generator import generate_token_value
from shared.constants.estado import EstadoCodigo
from shared.constants.estado_token import EstadoTokenCodigo
from shared.constants.tipo_registro import TipoRegistroCodigo
from shared.exceptions.device import (
    DispositivoNoAutorizadoError,
    DispositivoNoEncontradoError,
    FueraDeHorarioError,
)

CLAVE_QR_EXPIRACION_SEG = "QR_EXPIRACION_SEG"
CLAVE_CODIGO_LONGITUD = "CODIGO_LONGITUD"
CLAVE_CODIGO_FORMATO = "CODIGO_FORMATO"
CLAVE_EXIGIR_CODIGO = "EXIGIR_CODIGO"
CLAVE_EXIGIR_SALIDA = "EXIGIR_SALIDA"
CLAVE_TOLERANCIA_MIN = "TOLERANCIA_MIN"


async def _leer_bool(session: AsyncSession, clave: str) -> bool:
    raw = await config_general_repository.get_valor(session, clave)
    return raw.lower() in ("true", "1", "si", "sí")


@dataclass(frozen=True)
class TokenGenerado:
    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime
    exigir_codigo: bool
    exigir_salida: bool
    tipo_registro: str


async def generate_token(session: AsyncSession, dispositivo_identificador: str) -> TokenGenerado:
    dispositivo = await dispositivo_repository.get_by_identificador(
        session, dispositivo_identificador
    )
    if dispositivo is None:
        raise DispositivoNoEncontradoError(dispositivo_identificador)

    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    if (
        dispositivo.id_estado != activo_id
        or dispositivo.sede is None
        or dispositivo.sede.id_estado != activo_id
    ):
        raise DispositivoNoAutorizadoError(dispositivo_identificador)

    ahora = timezone.now()
    exigir_salida = await _leer_bool(session, CLAVE_EXIGIR_SALIDA)

    horarios = await horario_repository.get_all(
        session,
        id_sede=dispositivo.id_sede,
        solo_vigentes=True,
        fecha_referencia=ahora.date(),
    )

    tipo_registro = TipoRegistroCodigo.ENTRADA
    logger.info(
        "Horarios para sede %s: %d encontrados, ahora=%s",
        dispositivo.id_sede, len(horarios), ahora.isoformat(),
    )
    if horarios:
        tolerancia = int(
            await config_general_repository.get_valor(session, CLAVE_TOLERANCIA_MIN)
        )
        en_ventana_entrada = False
        en_ventana_salida = False
        for h in horarios:
            entrada_dt = datetime.combine(ahora.date(), h.hora_entrada, tzinfo=ahora.tzinfo)
            limite_entrada = entrada_dt + timedelta(minutes=tolerancia)
            logger.info(
                "  Horario id=%s entrada=%s limite=%s salida=%s tolerancia=%d",
                h.id, entrada_dt.isoformat(), limite_entrada.isoformat(),
                h.hora_salida, tolerancia,
            )
            if entrada_dt <= ahora <= limite_entrada:
                en_ventana_entrada = True

            if h.hora_salida is not None:
                salida_dt = datetime.combine(ahora.date(), h.hora_salida, tzinfo=ahora.tzinfo)
                limite_salida = salida_dt + timedelta(minutes=tolerancia)
                if salida_dt <= ahora <= limite_salida:
                    en_ventana_salida = True

        logger.info(
            "  Resultado: en_ventana_entrada=%s, en_ventana_salida=%s",
            en_ventana_entrada, en_ventana_salida,
        )
        if en_ventana_entrada:
            tipo_registro = TipoRegistroCodigo.ENTRADA
        elif en_ventana_salida:
            tipo_registro = TipoRegistroCodigo.SALIDA
        else:
            raise FueraDeHorarioError(dispositivo_identificador)
    else:
        logger.info("  Sin horarios -> token sin restriccion")

    expiracion_seg = int(
        await config_general_repository.get_valor(session, CLAVE_QR_EXPIRACION_SEG)
    )
    codigo_longitud = int(
        await config_general_repository.get_valor(session, CLAVE_CODIGO_LONGITUD)
    )
    codigo_formato = await config_general_repository.get_valor(session, CLAVE_CODIGO_FORMATO)

    exigir_codigo = await _leer_bool(session, CLAVE_EXIGIR_CODIGO)

    expira_en = ahora + timedelta(seconds=expiracion_seg)

    token_value = generate_token_value()
    codigo_alfa = generate_codigo(codigo_formato, codigo_longitud) if exigir_codigo else ""

    estado_token_activo_id = await cat_estado_token_repository.get_estado_token_id(
        session, EstadoTokenCodigo.ACTIVO
    )

    await token_qr_repository.create(
        session,
        id_sede=dispositivo.id_sede,
        id_dispositivo=dispositivo.id,
        id_estado_token=estado_token_activo_id,
        token=token_value,
        codigo_alfa=codigo_alfa,
        generado_en=ahora,
        expira_en=expira_en,
    )

    return TokenGenerado(
        token=token_value,
        codigo_alfa=codigo_alfa,
        generado_en=ahora,
        expira_en=expira_en,
        exigir_codigo=exigir_codigo,
        exigir_salida=exigir_salida,
        tipo_registro=tipo_registro,
    )
