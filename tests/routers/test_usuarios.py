from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.roles import RolNoEncontradoError
from shared.exceptions.usuarios import (
    AutoDesactivacionError,
    CorreoDuplicadoError,
    RolInactivoError,
    UltimoSuperAdminError,
    UsernameDuplicadoError,
    UsuarioNoEncontradoError,
)

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeRol:
    id: int = 1
    codigo: str = "SUPER_ADMIN"
    nombre: str = "Super Usuario"


@dataclass
class _FakeUsuario:
    id: int = 10
    id_rol: int = 1
    id_estado: int = 1
    nombre: str = "Admin Test"
    correo: str = "admin@test.com"
    username: str = "admin"
    password_hash: str = "hashed"
    debe_cambiar_pw: bool = True
    ultimo_login: datetime | None = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW
    rol: _FakeRol | None = None

    def __post_init__(self):
        if self.rol is None:
            self.rol = _FakeRol()


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "USUARIOS"


@dataclass
class _FakePermiso:
    modulo: _FakeModulo = None
    puede_leer: bool = True
    puede_escribir: bool = True
    puede_eliminar: bool = True
    puede_administrar: bool = True

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeModulo()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides[get_current_user] = _fake_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _permission_patches():
    return (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeAuthUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    )


_HEADERS = {"Authorization": "Bearer valid.jwt"}


# ── GET /usuarios ──


def test_list_usuarios_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.list_usuarios",
            new=AsyncMock(return_value=[_FakeUsuario()]),
        ),
    ):
        response = client.get("/usuarios", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["username"] == "admin"
    assert body["items"][0]["rol_codigo"] == "SUPER_ADMIN"


def test_list_usuarios_with_filters(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.list_usuarios",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/usuarios?nombre=test&id_rol=1&id_estado=1",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["total"] == 0


# ── GET /usuarios/{id} ──


def test_get_usuario_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.get_usuario",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
    ):
        response = client.get("/usuarios/10", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == 10


def test_get_usuario_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.get_usuario",
            new=AsyncMock(side_effect=UsuarioNoEncontradoError(999)),
        ),
    ):
        response = client.get("/usuarios/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /usuarios ──


def test_create_usuario_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.create_usuario",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
    ):
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "nuevo@test.com",
                "username": "nuevo",
                "password": "password123",
                "id_rol": 1,
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["debe_cambiar_pw"] is True


def test_create_usuario_returns_409_duplicate_correo(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.create_usuario",
            new=AsyncMock(side_effect=CorreoDuplicadoError("admin@test.com")),
        ),
    ):
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "admin@test.com",
                "username": "nuevo",
                "password": "password123",
                "id_rol": 1,
            },
        )

    assert response.status_code == 409


def test_create_usuario_returns_409_duplicate_username(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.create_usuario",
            new=AsyncMock(side_effect=UsernameDuplicadoError("admin")),
        ),
    ):
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "nuevo@test.com",
                "username": "admin",
                "password": "password123",
                "id_rol": 1,
            },
        )

    assert response.status_code == 409


def test_create_usuario_returns_404_rol_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.create_usuario",
            new=AsyncMock(side_effect=RolNoEncontradoError(999)),
        ),
    ):
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "nuevo@test.com",
                "username": "nuevo",
                "password": "password123",
                "id_rol": 999,
            },
        )

    assert response.status_code == 404


def test_create_usuario_returns_422_invalid_email(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "not-an-email",
                "username": "nuevo",
                "password": "password123",
                "id_rol": 1,
            },
        )

    assert response.status_code == 422


def test_create_usuario_returns_422_missing_fields(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={"nombre": "Solo nombre"},
        )

    assert response.status_code == 422


def test_create_usuario_returns_422_rol_inactivo(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.create_usuario",
            new=AsyncMock(side_effect=RolInactivoError(5)),
        ),
    ):
        response = client.post(
            "/usuarios",
            headers=_HEADERS,
            json={
                "nombre": "Nuevo",
                "correo": "nuevo@test.com",
                "username": "nuevo",
                "password": "password123",
                "id_rol": 5,
            },
        )

    assert response.status_code == 422


# ── PUT /usuarios/{id} ──


def test_update_usuario_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.update_usuario",
            new=AsyncMock(return_value=_FakeUsuario(nombre="Actualizado")),
        ),
    ):
        response = client.put(
            "/usuarios/10",
            headers=_HEADERS,
            json={"nombre": "Actualizado"},
        )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Actualizado"


def test_update_usuario_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.update_usuario",
            new=AsyncMock(side_effect=UsuarioNoEncontradoError(999)),
        ),
    ):
        response = client.put(
            "/usuarios/999",
            headers=_HEADERS,
            json={"nombre": "Test"},
        )

    assert response.status_code == 404


# ── DELETE /usuarios/{id} ──


def test_deactivate_usuario_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.deactivate_usuario",
            new=AsyncMock(return_value=False),
        ),
    ):
        response = client.delete("/usuarios/10", headers=_HEADERS)

    assert response.status_code == 204


def test_deactivate_self_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.deactivate_usuario",
            new=AsyncMock(return_value=True),
        ),
    ):
        response = client.delete("/usuarios/1", headers=_HEADERS)

    assert response.status_code == 200
    assert "sesion" in response.json()["detail"].lower()


def test_deactivate_ultimo_super_admin_returns_409(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.deactivate_usuario",
            new=AsyncMock(side_effect=UltimoSuperAdminError()),
        ),
    ):
        response = client.delete("/usuarios/10", headers=_HEADERS)

    assert response.status_code == 409


# ── POST /usuarios/{id}/activar ──


def test_activate_usuario_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.activate_usuario",
            new=AsyncMock(return_value=_FakeUsuario(id_estado=1)),
        ),
    ):
        response = client.post("/usuarios/10/activar", headers=_HEADERS)

    assert response.status_code == 200


def test_activate_usuario_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.usuarios.usuarios_service.activate_usuario",
            new=AsyncMock(side_effect=UsuarioNoEncontradoError(999)),
        ),
    ):
        response = client.post("/usuarios/999/activar", headers=_HEADERS)

    assert response.status_code == 404
