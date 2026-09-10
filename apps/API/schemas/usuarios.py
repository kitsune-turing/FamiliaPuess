import re
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUsuarioRequest(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150)
    correo: EmailStr = Field(..., max_length=255)
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=12, max_length=128)
    id_rol: int = Field(..., gt=0)

    @field_validator("password")
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


class UpdateUsuarioRequest(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=150)
    correo: EmailStr | None = Field(None, max_length=255)
    username: str | None = Field(None, min_length=1, max_length=50)
    id_rol: int | None = Field(None, gt=0)
    updated_at: datetime = Field(...)


class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    correo: str
    username: str
    id_rol: int
    rol_codigo: str
    rol_nombre: str
    id_estado: int
    debe_cambiar_pw: bool
    ultimo_login: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, usuario) -> "UsuarioResponse":
        return cls(
            id=usuario.id,
            nombre=usuario.nombre,
            correo=usuario.correo,
            username=usuario.username,
            id_rol=usuario.id_rol,
            rol_codigo=usuario.rol.codigo,
            rol_nombre=usuario.rol.nombre,
            id_estado=usuario.id_estado,
            debe_cambiar_pw=usuario.debe_cambiar_pw,
            ultimo_login=usuario.ultimo_login,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at,
        )


class UsuarioListResponse(BaseModel):
    items: list[UsuarioResponse]
    total: int
