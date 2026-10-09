from datetime import date, datetime

from pydantic import BaseModel


class RegistroReporteResponse(BaseModel):
    id: int
    id_empleado: int
    empleado_nombre: str
    empleado_documento: str
    id_sede: int
    sede_nombre: str
    tipo_registro: str
    fecha_registro: date
    registrado_en: datetime
    dispositivo_nombre: str | None = None
    novedad_tipo: str | None = None
    novedad_nombre: str | None = None
    novedad_color: str | None = None
    novedad_icono: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, asistencia, novedad=None) -> "RegistroReporteResponse":
        novedad_fields: dict = {}
        if novedad is not None:
            novedad_fields = {
                "novedad_tipo": novedad.tipo_novedad.codigo,
                "novedad_nombre": novedad.tipo_novedad.nombre,
                "novedad_color": novedad.tipo_novedad.color,
                "novedad_icono": novedad.tipo_novedad.icono,
            }

        dispositivo_nombre = None
        if asistencia.token_qr and asistencia.token_qr.dispositivo:
            d = asistencia.token_qr.dispositivo
            dispositivo_nombre = d.descripcion or d.identificador

        return cls(
            id=asistencia.id,
            id_empleado=asistencia.id_empleado,
            empleado_nombre=f"{asistencia.empleado.nombre} {asistencia.empleado.apellido}",
            empleado_documento=asistencia.empleado.numero_documento,
            id_sede=asistencia.id_sede,
            sede_nombre=asistencia.sede.nombre,
            tipo_registro=asistencia.tipo_registro.nombre,
            fecha_registro=asistencia.fecha_registro,
            registrado_en=asistencia.registrado_en,
            dispositivo_nombre=dispositivo_nombre,
            **novedad_fields,
        )


class ReporteAsistenciaResponse(BaseModel):
    items: list[RegistroReporteResponse]
    total: int


class ReporteSemanalResponse(BaseModel):
    id: int
    fecha_inicio: date
    fecha_fin: date
    total_registros: int
    total_novedades: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, reporte) -> "ReporteSemanalResponse":
        return cls(
            id=reporte.id,
            fecha_inicio=reporte.fecha_inicio,
            fecha_fin=reporte.fecha_fin,
            total_registros=reporte.total_registros,
            total_novedades=reporte.total_novedades,
            created_at=reporte.created_at,
        )


class ReporteSemanalListResponse(BaseModel):
    items: list[ReporteSemanalResponse]
    total: int
