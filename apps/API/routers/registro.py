from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.schemas.registro import RegistroRequest, RegistroResponse, TokenValidarResponse
from apps.API.services import registro_service

router = APIRouter(prefix="/registro", tags=["registro"])


@router.get(
    "/validar/{token}",
    response_model=TokenValidarResponse,
    status_code=status.HTTP_200_OK,
)
async def validar_token(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> TokenValidarResponse:
    resultado = await registro_service.validar_token(session, token)
    return TokenValidarResponse(
        token=resultado.token,
        sede_nombre=resultado.sede_nombre,
    )


@router.post(
    "/registrar",
    response_model=RegistroResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registrar_asistencia(
    payload: RegistroRequest,
    session: AsyncSession = Depends(get_session),
) -> RegistroResponse:
    resultado = await registro_service.registrar_asistencia(
        session,
        token_value=payload.token,
        documento=payload.documento,
        codigo_alfa=payload.codigo_alfa,
    )
    return RegistroResponse(
        mensaje="Asistencia registrada correctamente",
        empleado_nombre=resultado.empleado_nombre,
        sede_nombre=resultado.sede_nombre,
        registrado_en=resultado.registrado_en,
    )
