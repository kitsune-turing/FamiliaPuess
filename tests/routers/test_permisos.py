from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.permisos import (
    ModuloNoEncontradoError,
    PermisoDuplicadoError,
    PermisoNoEncontradoError,
)
from shared.exceptions.roles import RolNoEncontradoError

FIXED_NOW = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeModulo:
    id: int = 1
    codigo: str = "DASHBOARD"
    nombre: str = "Dashboard"


@dataclass
class _FakePermiso:
    id: int = 10
    id_rol: int = 1
    id_modulo: int = 1
    puede_leer: bool = True
    puede_escribir: bool = False
    puede_eliminar: bool = False
    puede_administrar: bool = False
    modulo: _FakeModulo = None

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeModulo()


@dataclass
class _FakeUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeAuthModulo:
    codigo: str = "ROLES"


@dataclass
class _FakeAuthPermiso:
    modulo: _FakeAuthModulo = None
    puede_leer: bool = True
    puede_escribir: bool = True
    puede_eliminar: bool = True
    puede_administrar: bool = True

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeAuthModulo()


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
            new=AsyncMock(return_value=[_FakeAuthPermiso()]),
        ),
    )


# ── GET /roles/{rol_id}/permisos ──


def test_list_permisos_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.list_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    ):
        response = client.get(
            "/roles/1/permisos",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["modulo_codigo"] == "DASHBOARD"


def test_list_permisos_returns_404_when_rol_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.list_permisos_by_rol",
            new=AsyncMock(side_effect=RolNoEncontradoError(999)),
        ),
    ):
        response = client.get(
            "/roles/999/permisos",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 404


# ── POST /roles/{rol_id}/permisos ──


def test_create_permiso_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.create_permiso",
            new=AsyncMock(return_value=_FakePermiso()),
        ),
    ):
        response = client.post(
            "/roles/1/permisos",
            json={"id_modulo": 1, "puede_leer": True},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 201
    assert response.json()["puede_leer"] is True


def test_create_permiso_returns_409_on_duplicate(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.create_permiso",
            new=AsyncMock(side_effect=PermisoDuplicadoError(1, "DASHBOARD")),
        ),
    ):
        response = client.post(
            "/roles/1/permisos",
            json={"id_modulo": 1},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 409


def test_create_permiso_returns_404_on_modulo_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.create_permiso",
            new=AsyncMock(side_effect=ModuloNoEncontradoError(999)),
        ),
    ):
        response = client.post(
            "/roles/1/permisos",
            json={"id_modulo": 999},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 404


# ── PUT /roles/{rol_id}/permisos/{permiso_id} ──


def test_update_permiso_returns_200(client):
    p_user, p_permisos = _permission_patches()
    updated = _FakePermiso(puede_escribir=True)

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.update_permiso",
            new=AsyncMock(return_value=updated),
        ),
    ):
        response = client.put(
            "/roles/1/permisos/10",
            json={"puede_escribir": True},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 200


def test_update_permiso_returns_404_when_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.update_permiso",
            new=AsyncMock(side_effect=PermisoNoEncontradoError(999)),
        ),
    ):
        response = client.put(
            "/roles/1/permisos/999",
            json={"puede_leer": True},
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 404


# ── DELETE /roles/{rol_id}/permisos/{permiso_id} ──


def test_delete_permiso_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.permisos.permisos_service.delete_permiso",
            new=AsyncMock(),
        ),
    ):
        response = client.delete(
            "/roles/1/permisos/10",
            headers={"Authorization": "Bearer valid.jwt"},
        )

    assert response.status_code == 204


# ── Authorization ──


def test_permisos_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/roles/1/permisos")
    app.dependency_overrides.clear()
    assert response.status_code == 403
