from datetime import datetime

from pydantic import BaseModel, Field


class TokenValidarResponse(BaseModel):
    token: str
    sede_nombre: str
    exigir_codigo: bool
    exigir_salida: bool
    tipo_registro: str


class RegistroRequest(BaseModel):
    token: str = Field(..., min_length=1)
    documento: str = Field(..., min_length=1, max_length=20)
    codigo_alfa: str = Field("", max_length=20)


class RegistroResponse(BaseModel):
    mensaje: str
    empleado_nombre: str
    sede_nombre: str
    registrado_en: datetime
    tipo_registro: str
