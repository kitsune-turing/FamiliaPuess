from pydantic import BaseModel


class DashboardResponse(BaseModel):
    empleados_activos: int
    asistencias_hoy: int
    novedades_hoy: int
    tardanzas_hoy: int
