from fastapi import APIRouter, Depends, Request, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.desktop_auth import require_desktop_api_key
from apps.API.repositories import cat_estado_repository, dispositivo_repository
from apps.API.schemas.dispositivos import DispositivoResponse
from apps.API.schemas.token_qr import TokenGenerarRequest, TokenGenerarResponse
from apps.API.services import dispositivos_service, token_service
from shared.constants.estado import EstadoCodigo
from shared.exceptions.device import DispositivoNoEncontradoError

router = APIRouter(prefix="/desktop", tags=["desktop"])


class DesktopRegisterRequest(BaseModel):
    identificador: str = Field(..., min_length=5, max_length=255)
    descripcion: str | None = Field(None, max_length=255)


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
    )
