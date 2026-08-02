from datetime import datetime

from pydantic import BaseModel


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


class AuditoriaListResponse(BaseModel):
    items: list[AuditoriaResponse]
    total: int
