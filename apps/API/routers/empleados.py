from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.empleados import (
    CreateEmpleadoRequest,
    EmpleadoListResponse,
    EmpleadoResponse,
    UpdateEmpleadoRequest,
)
from apps.API.services import empleados_service
from apps.API.utils.request import extract_ip as _extract_ip

router = APIRouter(prefix="/empleados", tags=["empleados"])


@router.get(
    "",
    response_model=EmpleadoListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_empleados(
    nombre: str | None = Query(None),
    documento: str | None = Query(None),
    cargo: str | None = Query(None),
    id_estado: int | None = Query(None, gt=0),
    id_sede: int | None = Query(None, gt=0),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "leer")),
) -> EmpleadoListResponse:
    empleados = await empleados_service.list_empleados(
        session,
        nombre=nombre,
        documento=documento,
        cargo=cargo,
        id_estado=id_estado,
        id_sede=id_sede,
    )
    items = [EmpleadoResponse.from_model(e) for e in empleados]
    return EmpleadoListResponse(items=items, total=len(items))


@router.get(
    "/{empleado_id}",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_200_OK,
)
async def get_empleado(
    empleado_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "leer")),
) -> EmpleadoResponse:
    empleado = await empleados_service.get_empleado(session, empleado_id)
    return EmpleadoResponse.from_model(empleado)


@router.post(
    "",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_empleado(
    payload: CreateEmpleadoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "escribir")),
) -> EmpleadoResponse:
    empleado = await empleados_service.create_empleado(
        session,
        documento=payload.documento,
        nombre=payload.nombre,
        apellido=payload.apellido,
        cargo=payload.cargo,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return EmpleadoResponse.from_model(empleado)


@router.put(
    "/{empleado_id}",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_200_OK,
)
async def update_empleado(
    empleado_id: int,
    payload: UpdateEmpleadoRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "escribir")),
) -> EmpleadoResponse:
    kwargs: dict = {
        "updated_at": payload.updated_at,
        "user_id": int(current_user["sub"]),
        "ip_address": _extract_ip(request),
    }
    if "documento" in payload.model_fields_set:
        kwargs["documento"] = payload.documento
    if "nombre" in payload.model_fields_set:
        kwargs["nombre"] = payload.nombre
    if "apellido" in payload.model_fields_set:
        kwargs["apellido"] = payload.apellido
    if "cargo" in payload.model_fields_set:
        kwargs["cargo"] = payload.cargo
    empleado = await empleados_service.update_empleado(
        session, empleado_id, **kwargs
    )
    return EmpleadoResponse.from_model(empleado)


@router.delete(
    "/{empleado_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_empleado(
    empleado_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "eliminar")),
) -> None:
    await empleados_service.deactivate_empleado(
        session,
        empleado_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )


@router.post(
    "/{empleado_id}/activar",
    response_model=EmpleadoResponse,
    status_code=status.HTTP_200_OK,
)
async def activate_empleado(
    empleado_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("EMPLEADOS", "escribir")),
) -> EmpleadoResponse:
    empleado = await empleados_service.activate_empleado(
        session,
        empleado_id,
        user_id=int(current_user["sub"]),
        ip_address=_extract_ip(request),
    )
    return EmpleadoResponse.from_model(empleado)
