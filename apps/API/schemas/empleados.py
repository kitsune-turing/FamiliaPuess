from datetime import datetime

from pydantic import BaseModel, Field


class CreateEmpleadoRequest(BaseModel):
    documento: str = Field(..., min_length=4, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    cargo: str = Field(..., min_length=1, max_length=100)


class UpdateEmpleadoRequest(BaseModel):
    documento: str | None = Field(None, min_length=4, max_length=30)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    apellido: str | None = Field(None, min_length=1, max_length=100)
    cargo: str | None = Field(None, min_length=1, max_length=100)
    updated_at: datetime = Field(...)


class EmpleadoResponse(BaseModel):
    id: int
    documento: str
    nombre: str
    apellido: str
    cargo: str
    id_estado: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, empleado) -> "EmpleadoResponse":
        return cls(
            id=empleado.id,
            documento=empleado.numero_documento,
            nombre=empleado.nombre,
            apellido=empleado.apellido,
            cargo=empleado.cargo.nombre if empleado.cargo else "",
            id_estado=empleado.id_estado,
            created_at=empleado.created_at,
            updated_at=empleado.updated_at,
        )


class EmpleadoListResponse(BaseModel):
    items: list[EmpleadoResponse]
    total: int
