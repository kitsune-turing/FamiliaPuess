from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.core.timezone import now as tz_now
from apps.API.repositories import dashboard_repository
from apps.API.schemas.dashboard import DashboardResponse


async def get_indicadores(session: AsyncSession) -> DashboardResponse:
    hoy = tz_now().date()

    empleados_activos = await dashboard_repository.contar_empleados_activos(session)
    asistencias_hoy = await dashboard_repository.contar_asistencias_fecha(session, hoy)
    novedades_hoy = await dashboard_repository.contar_novedades_fecha(session, hoy)
    tardanzas_hoy = await dashboard_repository.contar_tardanzas_fecha(session, hoy)

    return DashboardResponse(
        empleados_activos=empleados_activos,
        asistencias_hoy=asistencias_hoy,
        novedades_hoy=novedades_hoy,
        tardanzas_hoy=tardanzas_hoy,
    )
