from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.roles import (
    RolCodigoDuplicadoError,
    RolNoEncontradoError,
    RolProtegidoError,
    RolTieneUsuariosError,
)

FIXED_NOW = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeRol:
    id: int = 5
    codigo: str = "OPERADOR"
    nombre: str = "Operador"
    id_estado: int = 1
    descripcion: str | None = "Rol de operador"
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW


@dataclass
class _FakeUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "ROLES"


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
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    )


# ── GET /roles ──


def test_list_roles_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.list_roles",
            new=AsyncMock(return_value=[_FakeRol()]),
        ),
    ):
        response = client.get(
            "/roles",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["codigo"] == "OPERADOR"


# ── GET /roles/{id} ──


def test_get_rol_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.get_rol",
            new=AsyncMock(return_value=_FakeRol()),
        ),
    ):
        response = client.get(
            "/roles/5",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 200
    assert response.json()["id"] == 5


def test_get_rol_returns_404_when_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.get_rol",
            new=AsyncMock(side_effect=RolNoEncontradoError(999)),
        ),
    ):
        response = client.get(
            "/roles/999",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 404


# ── POST /roles ──


def test_create_rol_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.create_rol",
            new=AsyncMock(return_value=_FakeRol()),
        ),
    ):
        response = client.post(
            "/roles",
            json={"codigo": "OPERADOR", "nombre": "Operador"},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 201
    assert response.json()["codigo"] == "OPERADOR"


def test_create_rol_returns_409_on_duplicate(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.create_rol",
            new=AsyncMock(side_effect=RolCodigoDuplicadoError("OPERADOR")),
        ),
    ):
        response = client.post(
            "/roles",
            json={"codigo": "OPERADOR", "nombre": "Operador"},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 409


# ── PUT /roles/{id} ──


def test_update_rol_returns_200(client):
    p_user, p_permisos = _permission_patches()
    updated = _FakeRol(nombre="Operador Actualizado")

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.update_rol",
            new=AsyncMock(return_value=updated),
        ),
    ):
        response = client.put(
            "/roles/5",
            json={"nombre": "Operador Actualizado"},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 200


# ── DELETE /roles/{id} ──


def test_delete_rol_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.deactivate_rol",
            new=AsyncMock(),
        ),
    ):
        response = client.delete(
            "/roles/5",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 204


def test_delete_rol_returns_403_on_protected(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.deactivate_rol",
            new=AsyncMock(side_effect=RolProtegidoError("SUPER_ADMIN")),
        ),
    ):
        response = client.delete(
            "/roles/1",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 403


def test_delete_rol_returns_409_when_has_users(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.roles.roles_service.deactivate_rol",
            new=AsyncMock(side_effect=RolTieneUsuariosError("OPERADOR")),
        ),
    ):
        response = client.delete(
            "/roles/5",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 409


# ── Authorization ──


def test_roles_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/roles")
    app.dependency_overrides.clear()
    assert response.status_code == 403
