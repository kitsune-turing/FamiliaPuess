from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

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
from shared.exceptions.device import (
    DispositivoNoAutorizadoError,
    DispositivoNoEncontradoError,
    FueraDeHorarioError,
)

CLAVE_QR_EXPIRACION_SEG = "QR_EXPIRACION_SEG"
CLAVE_CODIGO_LONGITUD = "CODIGO_LONGITUD"
CLAVE_CODIGO_FORMATO = "CODIGO_FORMATO"


@dataclass(frozen=True)
class TokenGenerado:
    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime


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

    horarios = await horario_repository.get_all(
        session,
        id_sede=dispositivo.id_sede,
        solo_vigentes=True,
        fecha_referencia=ahora.date(),
    )
    if horarios:
        dentro_de_ventana = any(
            ahora <= datetime.combine(ahora.date(), h.hora_entrada, tzinfo=ahora.tzinfo)
            + timedelta(minutes=h.tolerancia_min)
            for h in horarios
        )
        if not dentro_de_ventana:
            raise FueraDeHorarioError(dispositivo_identificador)

    expiracion_seg = int(
        await config_general_repository.get_valor(session, CLAVE_QR_EXPIRACION_SEG)
    )
    codigo_longitud = int(
        await config_general_repository.get_valor(session, CLAVE_CODIGO_LONGITUD)
    )
    codigo_formato = await config_general_repository.get_valor(session, CLAVE_CODIGO_FORMATO)

    expira_en = ahora + timedelta(seconds=expiracion_seg)

    token_value = generate_token_value()
    codigo_alfa = generate_codigo(codigo_formato, codigo_longitud)

    estado_token_activo_id = await cat_estado_token_repository.get_estado_token_id(
        session, EstadoTokenCodigo.ACTIVO
    )

    await token_qr_repository.create(
        session,
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
    )
