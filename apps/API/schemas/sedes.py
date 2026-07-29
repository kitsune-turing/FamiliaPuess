from datetime import datetime

from pydantic import BaseModel, Field


class CreateSedeRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    direccion: str = Field(..., min_length=1, max_length=255)


class UpdateSedeRequest(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)
    direccion: str | None = Field(None, min_length=1, max_length=255)
    updated_at: datetime = Field(...)


class SedeResponse(BaseModel):
    id: int
    nombre: str
    direccion: str
    id_estado: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SedeListResponse(BaseModel):
    items: list[SedeResponse]
    total: int
