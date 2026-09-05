from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.desktop_auth import require_desktop_api_key
from apps.API.schemas.token_qr import TokenGenerarRequest, TokenGenerarResponse
from apps.API.services import token_service

router = APIRouter(prefix="/desktop", tags=["desktop"])


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
