from datetime import date, datetime, time

from pydantic import BaseModel, Field


class CreateHorarioRequest(BaseModel):
    id_sede: int = Field(..., gt=0)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    hora_entrada: time = Field(...)
    hora_salida: time | None = Field(None)
    vigente_desde: date = Field(...)
    vigente_hasta: date | None = Field(None)


class UpdateHorarioRequest(BaseModel):
    id_sede: int | None = Field(None, gt=0)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    hora_entrada: time | None = Field(None)
    hora_salida: time | None = Field(None)
    vigente_desde: date | None = Field(None)
    vigente_hasta: date | None = Field(None)


class HorarioResponse(BaseModel):
    id: int
    id_sede: int
    sede_nombre: str
    nombre: str | None
    hora_entrada: time
    hora_salida: time | None
    vigente_desde: date
    vigente_hasta: date | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, horario) -> "HorarioResponse":
        return cls(
            id=horario.id,
            id_sede=horario.id_sede,
            sede_nombre=horario.sede.nombre,
            nombre=horario.nombre,
            hora_entrada=horario.hora_entrada,
            hora_salida=horario.hora_salida,
            vigente_desde=horario.vigente_desde,
            vigente_hasta=horario.vigente_hasta,
            created_at=horario.created_at,
        )


class HorarioListResponse(BaseModel):
    items: list[HorarioResponse]
    total: int
