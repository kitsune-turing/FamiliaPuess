from datetime import datetime

from pydantic import BaseModel, Field


class CreateEmpleadoRequest(BaseModel):
    documento: str = Field(..., min_length=4, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=100)
    apellido: str = Field(..., min_length=1, max_length=100)
    cargo: str = Field(..., min_length=1, max_length=100)
    id_sede: int = Field(..., gt=0)


class UpdateEmpleadoRequest(BaseModel):
    documento: str | None = Field(None, min_length=4, max_length=30)
    nombre: str | None = Field(None, min_length=1, max_length=100)
    apellido: str | None = Field(None, min_length=1, max_length=100)
    cargo: str | None = Field(None, min_length=1, max_length=100)
    id_sede: int | None = Field(None, gt=0)
    updated_at: datetime = Field(...)


class EmpleadoResponse(BaseModel):
    id: int
    documento: str
    nombre: str
    apellido: str
    cargo: str
    id_estado: int
    id_sede: int
    sede_nombre: str
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
            id_sede=empleado.id_sede_actual,
            sede_nombre=(
                empleado.sede_actual.nombre
                if empleado.sede_actual
                else "Sin asignar"
            ),
            created_at=empleado.created_at,
            updated_at=empleado.updated_at,
        )


class EmpleadoListResponse(BaseModel):
    items: list[EmpleadoResponse]
    total: int
