from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.horarios import (
    CreateHorarioRequest,
    HorarioListResponse,
    HorarioResponse,
    UpdateHorarioRequest,
)
from apps.API.services import horarios_service
from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/horarios", tags=["horarios"])


@router.get(
    "",
    response_model=HorarioListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_horarios(
    id_sede: int | None = Query(None, gt=0),
    solo_vigentes: bool = Query(False),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("HORARIOS", "leer")),
) -> HorarioListResponse:
    horarios = await horarios_service.list_horarios(
        session,
        id_sede=id_sede,
        solo_vigentes=solo_vigentes,
    )
    items = [HorarioResponse.from_model(h) for h in horarios]
    return HorarioListResponse(items=items, total=len(items))


@router.get(
    "/{horario_id}",
    response_model=HorarioResponse,
    status_code=status.HTTP_200_OK,
)
async def get_horario(
    horario_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("HORARIOS", "leer")),
) -> HorarioResponse:
    horario = await horarios_service.get_horario(session, horario_id)
    return HorarioResponse.from_model(horario)


@router.post(
    "",
    response_model=HorarioResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_horario(
    payload: CreateHorarioRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("HORARIOS", "escribir")),
) -> HorarioResponse:
    horario = await horarios_service.create_horario(
        session,
        id_sede=payload.id_sede,
        hora_entrada=payload.hora_entrada,
        hora_salida=payload.hora_salida,
        tolerancia_min=payload.tolerancia_min,
        nombre=payload.nombre,
        vigente_desde=payload.vigente_desde,
        vigente_hasta=payload.vigente_hasta,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return HorarioResponse.from_model(horario)


@router.put(
    "/{horario_id}",
    response_model=HorarioResponse,
    status_code=status.HTTP_200_OK,
)
async def update_horario(
    horario_id: int,
    payload: UpdateHorarioRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("HORARIOS", "escribir")),
) -> HorarioResponse:
    kwargs: dict = {
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "nombre" in payload.model_fields_set:
        kwargs["nombre"] = payload.nombre
    if "hora_entrada" in payload.model_fields_set:
        kwargs["hora_entrada"] = payload.hora_entrada
    if "hora_salida" in payload.model_fields_set:
        kwargs["hora_salida"] = payload.hora_salida
    if "tolerancia_min" in payload.model_fields_set:
        kwargs["tolerancia_min"] = payload.tolerancia_min
    if "vigente_hasta" in payload.model_fields_set:
        kwargs["vigente_hasta"] = payload.vigente_hasta

    horario = await horarios_service.update_horario(
        session, horario_id, **kwargs
    )
    return HorarioResponse.from_model(horario)


@router.delete(
    "/{horario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def finalizar_horario(
    horario_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("HORARIOS", "eliminar")),
) -> None:
    await horarios_service.finalizar_horario(
        session,
        horario_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
