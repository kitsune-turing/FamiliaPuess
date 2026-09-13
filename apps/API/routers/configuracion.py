from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user_enforce_pw
from apps.API.repositories import auditoria_repository, config_general_repository
from apps.API.schemas.configuracion import EstadoInicialResponse, PasoSetup
from apps.API.services import configuracion_service
from shared.constants.configuracion import ConfigClave
from shared.constants.operacion_auditoria import OperacionAuditoria
from shared.constants.recurso_auditoria import RecursoAuditoria

from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/configuracion", tags=["configuracion"])

_CLAVES_EDITABLES = [
    ConfigClave.NOMBRE_EMPRESA,
    ConfigClave.NIT,
    ConfigClave.ZONA_HORARIA,
    ConfigClave.IDIOMA,
    ConfigClave.TOLERANCIA_MIN,
    ConfigClave.QR_EXPIRACION_SEG,
    ConfigClave.EXIGIR_CODIGO,
    ConfigClave.EXIGIR_SALIDA,
]


class ConfigGeneralResponse(BaseModel):
    valores: dict[str, str]


class ConfigUpdateRequest(BaseModel):
    valores: dict[str, str]


@router.get(
    "/estado-inicial",
    response_model=EstadoInicialResponse,
    status_code=status.HTTP_200_OK,
)
async def get_estado_inicial(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_enforce_pw),
) -> EstadoInicialResponse:
    result = await configuracion_service.get_setup_status(
        session, user_id=int(current_user["sub"])
    )
    return EstadoInicialResponse(
        setup_completado=result["setup_completado"],
        pasos=[PasoSetup(**p) for p in result["pasos"]],
    )


@router.post(
    "/completar-setup",
    status_code=status.HTTP_200_OK,
)
async def completar_setup(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_enforce_pw),
) -> dict:
    await configuracion_service.completar_setup(
        session,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return {"detail": "Configuracion inicial completada exitosamente"}


@router.get(
    "/general",
    response_model=ConfigGeneralResponse,
    status_code=status.HTTP_200_OK,
)
async def get_config_general(
    session: AsyncSession = Depends(get_session),
    _current_user: dict = Depends(get_current_user_enforce_pw),
) -> ConfigGeneralResponse:
    valores = await config_general_repository.get_many(session, _CLAVES_EDITABLES)
    return ConfigGeneralResponse(valores=valores)


@router.put(
    "/general",
    status_code=status.HTTP_200_OK,
)
async def update_config_general(
    payload: ConfigUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user_enforce_pw),
) -> dict:
    user_id = int(current_user["sub"])
    timestamp = tz_now()
    valor_anterior: dict[str, str] = {}
    valor_nuevo: dict[str, str] = {}

    for clave, valor in payload.valores.items():
        if clave not in _CLAVES_EDITABLES:
            continue
        old = await config_general_repository.get_valor_or_none(session, clave)
        if old == valor:
            continue
        valor_anterior[clave] = old or ""
        valor_nuevo[clave] = valor
        await config_general_repository.upsert(
            session,
            clave=clave,
            valor=valor,
            updated_by=user_id,
            now=timestamp,
        )

    if valor_nuevo:
        await auditoria_repository.create(
            session,
            id_usuario=user_id,
            recurso=RecursoAuditoria.CONFIGURACION,
            id_recurso="GENERAL",
            operacion=OperacionAuditoria.UPDATE,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            ip_address=_extract_ip(request),
            timestamp_accion=timestamp,
        )

    return {"detail": "Configuracion actualizada"}
