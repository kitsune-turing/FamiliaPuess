from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user_enforce_pw
from apps.API.schemas.configuracion import EstadoInicialResponse, PasoSetup
from apps.API.services import configuracion_service

router = APIRouter(prefix="/configuracion", tags=["configuracion"])


def _extract_ip(request: Request) -> str | None:
    if request.client:
        return request.client.host
    return None


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
