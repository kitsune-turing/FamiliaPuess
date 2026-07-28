from pydantic import BaseModel, Field


class CreatePermisoRequest(BaseModel):
    id_modulo: int = Field(..., gt=0)
    puede_leer: bool = False
    puede_escribir: bool = False
    puede_eliminar: bool = False
    puede_administrar: bool = False


class UpdatePermisoRequest(BaseModel):
    puede_leer: bool | None = None
    puede_escribir: bool | None = None
    puede_eliminar: bool | None = None
    puede_administrar: bool | None = None


class PermisoRolResponse(BaseModel):
    id: int
    id_rol: int
    id_modulo: int
    modulo_codigo: str
    modulo_nombre: str
    puede_leer: bool
    puede_escribir: bool
    puede_eliminar: bool
    puede_administrar: bool


class PermisoRolListResponse(BaseModel):
    items: list[PermisoRolResponse]
    total: int
