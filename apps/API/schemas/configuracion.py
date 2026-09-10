from pydantic import BaseModel


class PasoSetup(BaseModel):
    clave: str
    descripcion: str
    completado: bool


class EstadoInicialResponse(BaseModel):
    setup_completado: bool
    pasos: list[PasoSetup]
