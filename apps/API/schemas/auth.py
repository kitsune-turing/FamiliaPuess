import re

from pydantic import BaseModel, Field, field_validator


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


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=12, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r"\d", v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v


class ChangePasswordResponse(BaseModel):
    message: str
