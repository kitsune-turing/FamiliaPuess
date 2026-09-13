from datetime import datetime

from pydantic import BaseModel, Field


class TokenGenerarRequest(BaseModel):
    dispositivo_identificador: str = Field(..., min_length=1, max_length=255)


class TokenGenerarResponse(BaseModel):
    token: str
    codigo_alfa: str
    generado_en: datetime
    expira_en: datetime
    exigir_codigo: bool
