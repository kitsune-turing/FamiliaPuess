from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core import timezone
from apps.API.database.session import get_session
from apps.API.dependencies.desktop_auth import require_desktop_api_key
from apps.API.repositories import (
    cat_estado_repository,
    config_general_repository,
    dispositivo_repository,
    horario_repository,
    token_qr_repository,
)
from apps.API.schemas.dispositivos import DispositivoResponse
from apps.API.schemas.token_qr import TokenGenerarRequest, TokenGenerarResponse
from apps.API.services import dispositivos_service, token_service
from shared.constants.estado import EstadoCodigo
from shared.exceptions.device import DispositivoNoEncontradoError

router = APIRouter(prefix="/desktop", tags=["desktop"])


class DesktopRegisterRequest(BaseModel):
    identificador: str = Field(..., min_length=5, max_length=255)
    descripcion: str | None = Field(None, max_length=255)


class TokenUsedResponse(BaseModel):
    used: bool


class DesktopStatusResponse(BaseModel):
    id: int
    identificador: str
    id_sede: int | None
    sede_nombre: str | None
    id_estado: int
    activo: bool


@router.post(
    "/register",
    response_model=DispositivoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_device(
    payload: DesktopRegisterRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
    _api_key: str = Depends(require_desktop_api_key),
) -> DispositivoResponse:
    existing = await dispositivo_repository.get_by_identificador(
        session, payload.identificador
    )
    if existing is not None:
        response.status_code = status.HTTP_200_OK
        return DispositivoResponse.from_model(existing)

    dispositivo = await dispositivos_service.create_dispositivo(
        session,
        identificador=payload.identificador,
        descripcion=payload.descripcion,
        forzar_inactivo=True,
    )
    return DispositivoResponse.from_model(dispositivo)


@router.get(
    "/status/{identificador}",
    response_model=DesktopStatusResponse,
    status_code=status.HTTP_200_OK,
)
async def device_status(
    identificador: str,
    session: AsyncSession = Depends(get_session),
    _api_key: str = Depends(require_desktop_api_key),
) -> DesktopStatusResponse:
    dispositivo = await dispositivo_repository.get_by_identificador(session, identificador)
    if dispositivo is None:
        raise DispositivoNoEncontradoError(identificador)
    activo_id = await cat_estado_repository.get_estado_id(session, EstadoCodigo.ACTIVO)
    return DesktopStatusResponse(
        id=dispositivo.id,
        identificador=dispositivo.identificador,
        id_sede=dispositivo.id_sede,
        sede_nombre=dispositivo.sede.nombre if dispositivo.sede else None,
        id_estado=dispositivo.id_estado,
        activo=(
            dispositivo.id_estado == activo_id
            and dispositivo.sede is not None
            and dispositivo.sede.id_estado == activo_id
        ),
    )


@router.post(
    "/tokens", response_model=TokenGenerarResponse, status_code=status.HTTP_201_CREATED
)
async def generar_token(
    payload: TokenGenerarRequest,
    session: AsyncSession = Depends(get_session),
    _api_key: str = Depends(require_desktop_api_key),
) -> TokenGenerarResponse:
    generado = await token_service.generate_token(session, payload.dispositivo_identificador)
    return TokenGenerarResponse(
        token=generado.token,
        codigo_alfa=generado.codigo_alfa,
        generado_en=generado.generado_en,
        expira_en=generado.expira_en,
        exigir_codigo=generado.exigir_codigo,
        exigir_salida=generado.exigir_salida,
        tipo_registro=generado.tipo_registro,
    )


@router.get(
    "/debug/horarios/{identificador}",
    status_code=status.HTTP_200_OK,
)
async def debug_horarios(
    identificador: str,
    session: AsyncSession = Depends(get_session),
    _api_key: str = Depends(require_desktop_api_key),
) -> dict:
    dispositivo = await dispositivo_repository.get_by_identificador(session, identificador)
    if dispositivo is None:
        return {"error": "dispositivo no encontrado"}
    ahora = timezone.now()
    horarios = await horario_repository.get_all(
        session,
        id_sede=dispositivo.id_sede,
        solo_vigentes=True,
        fecha_referencia=ahora.date(),
    )
    tolerancia_raw = await config_general_repository.get_valor(session, "TOLERANCIA_MIN")
    return {
        "server_time": ahora.isoformat(),
        "server_date": str(ahora.date()),
        "id_sede": dispositivo.id_sede,
        "tolerancia_min": tolerancia_raw,
        "horarios_count": len(horarios),
        "horarios": [
            {
                "id": h.id,
                "nombre": h.nombre,
                "hora_entrada": str(h.hora_entrada),
                "hora_salida": str(h.hora_salida) if h.hora_salida else None,
                "vigente_desde": str(h.vigente_desde),
                "vigente_hasta": str(h.vigente_hasta) if h.vigente_hasta else None,
            }
            for h in horarios
        ],
    }


@router.get(
    "/tokens/{token_value}/used",
    response_model=TokenUsedResponse,
    status_code=status.HTTP_200_OK,
)
async def check_token_used(
    token_value: str,
    session: AsyncSession = Depends(get_session),
    _api_key: str = Depends(require_desktop_api_key),
) -> TokenUsedResponse:
    token_qr = await token_qr_repository.get_by_token(session, token_value)
    if token_qr is None:
        return TokenUsedResponse(used=True)
    return TokenUsedResponse(used=token_qr.consumido_en is not None)
