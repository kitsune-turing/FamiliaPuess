from datetime import datetime

from pydantic import BaseModel, Field


class CreateDispositivoRequest(BaseModel):
    identificador: str = Field(..., min_length=5, max_length=255)
    id_sede: int = Field(..., gt=0)
    descripcion: str | None = Field(None, max_length=255)


class UpdateDispositivoRequest(BaseModel):
    identificador: str | None = Field(None, min_length=5, max_length=255)
    descripcion: str | None = Field(None, max_length=255)
    id_sede: int | None = Field(None, gt=0)
    updated_at: datetime = Field(...)


class DispositivoResponse(BaseModel):
    id: int
    identificador: str
    id_sede: int | None
    sede_nombre: str | None
    id_estado: int
    descripcion: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, dispositivo) -> "DispositivoResponse":
        return cls(
            id=dispositivo.id,
            identificador=dispositivo.identificador,
            id_sede=dispositivo.id_sede,
            sede_nombre=dispositivo.sede.nombre if dispositivo.sede else None,
            id_estado=dispositivo.id_estado,
            descripcion=dispositivo.descripcion,
            created_at=dispositivo.created_at,
            updated_at=dispositivo.updated_at,
        )


class DispositivoListResponse(BaseModel):
    items: list[DispositivoResponse]
    total: int
