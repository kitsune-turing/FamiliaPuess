from datetime import datetime

from pydantic import BaseModel, Field


class TokenValidarResponse(BaseModel):
    token: str
    sede_nombre: str


class RegistroRequest(BaseModel):
    token: str = Field(..., min_length=1)
    documento: str = Field(..., min_length=1, max_length=20)
    codigo_alfa: str = Field(..., min_length=1, max_length=20)


class RegistroResponse(BaseModel):
    mensaje: str
    empleado_nombre: str
    sede_nombre: str
    registrado_en: datetime


class RegistroErrorResponse(BaseModel):
    detail: str
