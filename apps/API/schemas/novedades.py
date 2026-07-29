from datetime import date, datetime

from pydantic import BaseModel, Field


class NovedadResponse(BaseModel):
    id: int
    id_empleado: int
    empleado_nombre: str
    empleado_documento: str
    id_tipo_novedad: int
    tipo_codigo: str
    tipo_nombre: str
    tipo_color: str | None
    tipo_icono: str | None
    id_asistencia: int | None
    fecha: date
    observacion: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, novedad) -> "NovedadResponse":
        return cls(
            id=novedad.id,
            id_empleado=novedad.id_empleado,
            empleado_nombre=novedad.empleado.nombre,
            empleado_documento=novedad.empleado.documento,
            id_tipo_novedad=novedad.id_tipo_novedad,
            tipo_codigo=novedad.tipo_novedad.codigo,
            tipo_nombre=novedad.tipo_novedad.nombre,
            tipo_color=novedad.tipo_novedad.color,
            tipo_icono=novedad.tipo_novedad.icono,
            id_asistencia=novedad.id_asistencia,
            fecha=novedad.fecha,
            observacion=novedad.observacion,
            created_at=novedad.created_at,
        )


class NovedadListResponse(BaseModel):
    items: list[NovedadResponse]
    total: int


class DetectarNovedadRequest(BaseModel):
    id_asistencia: int = Field(..., gt=0)
