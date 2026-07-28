from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


class PermisoResponse(BaseModel):
    modulo_codigo: str
    modulo_nombre: str
    puede_leer: bool
    puede_escribir: bool
    puede_eliminar: bool
    puede_administrar: bool


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    usuario_id: int
    nombre: str
    username: str
    rol_codigo: str
    rol_nombre: str
    debe_cambiar_pw: bool
    permisos: list[PermisoResponse]


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class MeResponse(BaseModel):
    usuario_id: int
    nombre: str
    username: str
    rol_codigo: str
    rol_nombre: str
    permisos: list[PermisoResponse]
