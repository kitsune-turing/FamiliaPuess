from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.database.session import get_session
from apps.API.dependencies.auth import require_permission
from apps.API.schemas.reportes import (
    ReporteAsistenciaResponse,
    ReporteSemanalListResponse,
    ReporteSemanalResponse,
    RegistroReporteResponse,
)
from apps.API.services import reportes_service

router = APIRouter(prefix="/reportes", tags=["reportes"])


@router.get(
    "/asistencia",
    response_model=ReporteAsistenciaResponse,
    status_code=status.HTTP_200_OK,
)
async def consultar_asistencia(
    id_empleado: int | None = Query(None, gt=0),
    id_sede: int | None = Query(None, gt=0),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "leer")),
) -> ReporteAsistenciaResponse:
    asistencias, novedades_map = await reportes_service.consultar_asistencia(
        session,
        id_empleado=id_empleado,
        id_sede=id_sede,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    items = [
        RegistroReporteResponse.from_model(a, novedades_map.get(a.id))
        for a in asistencias
    ]
    return ReporteAsistenciaResponse(items=items, total=len(items))


@router.get(
    "/asistencia/excel",
    status_code=status.HTTP_200_OK,
)
async def descargar_asistencia_excel(
    id_empleado: int | None = Query(None, gt=0),
    id_sede: int | None = Query(None, gt=0),
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "leer")),
) -> Response:
    asistencias, novedades_map = await reportes_service.consultar_asistencia(
        session,
        id_empleado=id_empleado,
        id_sede=id_sede,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )
    content = reportes_service.generar_excel(
        asistencias, novedades_map,
        fecha_desde=fecha_desde, fecha_hasta=fecha_hasta,
    )
    filename = reportes_service.generar_nombre_archivo(fecha_desde, fecha_hasta)
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/semanales",
    response_model=ReporteSemanalListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_reportes_semanales(
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "leer")),
) -> ReporteSemanalListResponse:
    reportes = await reportes_service.list_reportes_semanales(session)
    items = [ReporteSemanalResponse.from_model(r) for r in reportes]
    return ReporteSemanalListResponse(items=items, total=len(items))


@router.get(
    "/semanales/{reporte_id}",
    response_model=ReporteSemanalResponse,
    status_code=status.HTTP_200_OK,
)
async def get_reporte_semanal(
    reporte_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "leer")),
) -> ReporteSemanalResponse:
    reporte = await reportes_service.get_reporte_semanal(session, reporte_id)
    return ReporteSemanalResponse.from_model(reporte)


@router.post(
    "/semanales/generar",
    response_model=ReporteSemanalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generar_reporte_semanal(
    fecha_referencia: date | None = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "escribir")),
) -> ReporteSemanalResponse:
    id_usuario = int(current_user.get("sub", 0))
    reporte = await reportes_service.generar_reporte_semanal(
        session, fecha_referencia=fecha_referencia, id_usuario=id_usuario,
    )
    return ReporteSemanalResponse.from_model(reporte)


@router.get(
    "/semanales/{reporte_id}/excel",
    status_code=status.HTTP_200_OK,
)
async def descargar_reporte_semanal_excel(
    reporte_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(require_permission("REPORTES", "leer")),
) -> Response:
    reporte = await reportes_service.get_reporte_semanal(session, reporte_id)
    asistencias, novedades_map = await reportes_service.consultar_asistencia(
        session,
        fecha_desde=reporte.fecha_inicio,
        fecha_hasta=reporte.fecha_fin,
    )
    content = reportes_service.generar_excel(
        asistencias, novedades_map,
        fecha_desde=reporte.fecha_inicio, fecha_hasta=reporte.fecha_fin,
    )
    filename = reportes_service.generar_nombre_archivo(
        reporte.fecha_inicio, reporte.fecha_fin,
    )
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
