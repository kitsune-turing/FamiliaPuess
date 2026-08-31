from datetime import datetime

from pydantic import BaseModel, field_validator


class AuditoriaResponse(BaseModel):
    id: int
    id_usuario: int | None
    recurso: str
    id_recurso: str | None
    operacion: str
    valor_anterior: dict | None
    valor_nuevo: dict | None
    ip_address: str | None
    detalle: str | None
    timestamp_accion: datetime

    model_config = {"from_attributes": True}

    @field_validator("ip_address", mode="before")
    @classmethod
    def _coerce_ip(cls, v: object) -> str | None:
        if v is None:
            return None
        return str(v)


class AuditoriaListResponse(BaseModel):
    items: list[AuditoriaResponse]
    total: int
