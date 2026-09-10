from datetime import datetime

from pydantic import BaseModel, Field


class CreateRolRequest(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=30)
    nombre: str = Field(..., min_length=1, max_length=50)
    descripcion: str | None = Field(None, max_length=255)


class UpdateRolRequest(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=50)
    descripcion: str | None = Field(None, max_length=255)
    updated_at: datetime = Field(...)


class RolResponse(BaseModel):
    id: int
    codigo: str
    nombre: str
    descripcion: str | None
    id_estado: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RolListResponse(BaseModel):
    items: list[RolResponse]
    total: int
