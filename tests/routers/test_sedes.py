from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.sedes import (
    SedeDireccionInvalidaError,
    SedeNoEncontradaError,
    SedeNombreDuplicadoError,
    SedeNombreInvalidoError,
)

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeSede:
    id: int = 1
    nombre: str = "Sede Central"
    direccion: str = "Calle 100 #15-20"
    id_estado: int = 1
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "SEDES"


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


# ── GET /sedes ──


def test_list_sedes_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.list_sedes",
            new=AsyncMock(return_value=[_FakeSede()]),
        ),
    ):
        response = client.get("/sedes", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["nombre"] == "Sede Central"
    assert body["items"][0]["direccion"] == "Calle 100 #15-20"


def test_list_sedes_with_filters(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.list_sedes",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/sedes?nombre=Central&id_estado=1",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_sedes_no_results(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.list_sedes",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/sedes?direccion=NoExiste",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


# ── GET /sedes/{id} ──


def test_get_sede_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.get_sede",
            new=AsyncMock(return_value=_FakeSede()),
        ),
    ):
        response = client.get("/sedes/1", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["nombre"] == "Sede Central"


def test_get_sede_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.get_sede",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.get("/sedes/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /sedes ──


def test_create_sede_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.create_sede",
            new=AsyncMock(return_value=_FakeSede()),
        ),
    ):
        response = client.post(
            "/sedes",
            headers=_HEADERS,
            json={
                "nombre": "Sede Central",
                "direccion": "Calle 100 #15-20",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Sede Central"
    assert body["direccion"] == "Calle 100 #15-20"


def test_create_sede_returns_409_duplicate_nombre(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.create_sede",
            new=AsyncMock(side_effect=SedeNombreDuplicadoError("Sede Central")),
        ),
    ):
        response = client.post(
            "/sedes",
            headers=_HEADERS,
            json={
                "nombre": "Sede Central",
                "direccion": "Calle 200 #10-5",
            },
        )

    assert response.status_code == 409


def test_create_sede_returns_422_invalid_nombre(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.create_sede",
            new=AsyncMock(side_effect=SedeNombreInvalidoError()),
        ),
    ):
        response = client.post(
            "/sedes",
            headers=_HEADERS,
            json={
                "nombre": "Sede @#$!",
                "direccion": "Calle 100 #15-20",
            },
        )

    assert response.status_code == 422


def test_create_sede_returns_422_invalid_direccion(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.create_sede",
            new=AsyncMock(side_effect=SedeDireccionInvalidaError()),
        ),
    ):
        response = client.post(
            "/sedes",
            headers=_HEADERS,
            json={
                "nombre": "Sede Norte",
                "direccion": "Calle 100 @$%&",
            },
        )

    assert response.status_code == 422


def test_create_sede_returns_422_missing_fields(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.post(
            "/sedes",
            headers=_HEADERS,
            json={"nombre": "Sede Norte"},
        )

    assert response.status_code == 422


# ── PUT /sedes/{id} ──


def test_update_sede_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(return_value=_FakeSede(direccion="Carrera 80 #10-5")),
        ),
    ):
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={
                "direccion": "Carrera 80 #10-5",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 200


def test_update_sede_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.put(
            "/sedes/999",
            headers=_HEADERS,
            json={
                "nombre": "Test",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 404


def test_update_sede_returns_409_concurrency(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(side_effect=ConflictoConcurrenciaError("sede", 1)),
        ),
    ):
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={
                "nombre": "Test",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_sede_returns_409_duplicate_nombre(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(side_effect=SedeNombreDuplicadoError("Sede Sur")),
        ),
    ):
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={
                "nombre": "Sede Sur",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_sede_returns_422_missing_updated_at(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={"nombre": "Test"},
        )

    assert response.status_code == 422


def test_update_sede_returns_422_invalid_nombre(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(side_effect=SedeNombreInvalidoError()),
        ),
    ):
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={
                "nombre": "Sede @!#",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 422


def test_update_sede_returns_422_invalid_direccion(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.update_sede",
            new=AsyncMock(side_effect=SedeDireccionInvalidaError()),
        ),
    ):
        response = client.put(
            "/sedes/1",
            headers=_HEADERS,
            json={
                "direccion": "Calle @$%&",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 422


# ── DELETE /sedes/{id} ──


def test_deactivate_sede_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.deactivate_sede",
            new=AsyncMock(),
        ),
    ):
        response = client.delete("/sedes/1", headers=_HEADERS)

    assert response.status_code == 204


def test_deactivate_sede_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.deactivate_sede",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.delete("/sedes/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /sedes/{id}/activar ──


def test_activate_sede_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.activate_sede",
            new=AsyncMock(return_value=_FakeSede(id_estado=1)),
        ),
    ):
        response = client.post("/sedes/1/activar", headers=_HEADERS)

    assert response.status_code == 200


def test_activate_sede_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.sedes.sedes_service.activate_sede",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.post("/sedes/999/activar", headers=_HEADERS)

    assert response.status_code == 404


# ── Authorization ──


def test_sedes_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/sedes")
    app.dependency_overrides.clear()
    assert response.status_code == 403
