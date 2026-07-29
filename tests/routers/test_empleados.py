from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.empleados import (
    DocumentoDuplicadoError,
    DocumentoFormatoInvalidoError,
    EmpleadoNoEncontradoError,
    NombreInvalidoError,
)
from shared.exceptions.sedes import SedeInactivaError, SedeNoEncontradaError

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


@dataclass
class _FakeEmpleado:
    id: int = 10
    documento: str = "12345678"
    nombre: str = "Juan"
    apellido: str = "Perez"
    cargo: str = "Operario"
    id_estado: int = 1
    id_sede: int = 1
    sede: _FakeSede = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW

    def __post_init__(self):
        if self.sede is None:
            self.sede = _FakeSede()


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "EMPLEADOS"


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


# ── GET /empleados ──


def test_list_empleados_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.list_empleados",
            new=AsyncMock(return_value=[_FakeEmpleado()]),
        ),
    ):
        response = client.get("/empleados", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["documento"] == "12345678"
    assert body["items"][0]["sede_nombre"] == "Sede Central"


def test_list_empleados_with_filters(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.list_empleados",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/empleados?nombre=Juan&cargo=Operario&id_estado=1",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_empleados_no_results(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.list_empleados",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/empleados?documento=99999999",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


# ── GET /empleados/{id} ──


def test_get_empleado_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.get_empleado",
            new=AsyncMock(return_value=_FakeEmpleado()),
        ),
    ):
        response = client.get("/empleados/10", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == 10
    assert response.json()["cargo"] == "Operario"


def test_get_empleado_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.get_empleado",
            new=AsyncMock(side_effect=EmpleadoNoEncontradoError(999)),
        ),
    ):
        response = client.get("/empleados/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /empleados ──


def test_create_empleado_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(return_value=_FakeEmpleado()),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "12345678",
                "nombre": "Juan",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 1,
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["documento"] == "12345678"
    assert body["nombre"] == "Juan"


def test_create_empleado_returns_409_duplicate_documento(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(side_effect=DocumentoDuplicadoError("12345678")),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "12345678",
                "nombre": "Juan",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 1,
            },
        )

    assert response.status_code == 409


def test_create_empleado_returns_422_invalid_documento(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(side_effect=DocumentoFormatoInvalidoError()),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "ABC123",
                "nombre": "Juan",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 1,
            },
        )

    assert response.status_code == 422


def test_create_empleado_returns_422_invalid_nombre(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(side_effect=NombreInvalidoError("nombre")),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "12345678",
                "nombre": "Juan123",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 1,
            },
        )

    assert response.status_code == 422


def test_create_empleado_returns_422_missing_fields(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={"documento": "12345678"},
        )

    assert response.status_code == 422


def test_create_empleado_returns_404_sede_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "12345678",
                "nombre": "Juan",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 999,
            },
        )

    assert response.status_code == 404


def test_create_empleado_returns_422_sede_inactiva(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.create_empleado",
            new=AsyncMock(side_effect=SedeInactivaError(1)),
        ),
    ):
        response = client.post(
            "/empleados",
            headers=_HEADERS,
            json={
                "documento": "12345678",
                "nombre": "Juan",
                "apellido": "Perez",
                "cargo": "Operario",
                "id_sede": 1,
            },
        )

    assert response.status_code == 422


# ── PUT /empleados/{id} ──


def test_update_empleado_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.update_empleado",
            new=AsyncMock(return_value=_FakeEmpleado(cargo="Jefe")),
        ),
    ):
        response = client.put(
            "/empleados/10",
            headers=_HEADERS,
            json={
                "cargo": "Jefe",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 200


def test_update_empleado_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.update_empleado",
            new=AsyncMock(side_effect=EmpleadoNoEncontradoError(999)),
        ),
    ):
        response = client.put(
            "/empleados/999",
            headers=_HEADERS,
            json={
                "nombre": "Test",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 404


def test_update_empleado_returns_409_concurrency(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.update_empleado",
            new=AsyncMock(side_effect=ConflictoConcurrenciaError("empleado", 10)),
        ),
    ):
        response = client.put(
            "/empleados/10",
            headers=_HEADERS,
            json={
                "nombre": "Test",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_empleado_returns_409_duplicate_documento(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.update_empleado",
            new=AsyncMock(side_effect=DocumentoDuplicadoError("99999999")),
        ),
    ):
        response = client.put(
            "/empleados/10",
            headers=_HEADERS,
            json={
                "documento": "99999999",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_empleado_returns_422_missing_updated_at(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.put(
            "/empleados/10",
            headers=_HEADERS,
            json={"nombre": "Test"},
        )

    assert response.status_code == 422


# ── DELETE /empleados/{id} ──


def test_deactivate_empleado_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.deactivate_empleado",
            new=AsyncMock(),
        ),
    ):
        response = client.delete("/empleados/10", headers=_HEADERS)

    assert response.status_code == 204


def test_deactivate_empleado_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.deactivate_empleado",
            new=AsyncMock(side_effect=EmpleadoNoEncontradoError(999)),
        ),
    ):
        response = client.delete("/empleados/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /empleados/{id}/activar ──


def test_activate_empleado_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.activate_empleado",
            new=AsyncMock(return_value=_FakeEmpleado(id_estado=1)),
        ),
    ):
        response = client.post("/empleados/10/activar", headers=_HEADERS)

    assert response.status_code == 200


def test_activate_empleado_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.empleados.empleados_service.activate_empleado",
            new=AsyncMock(side_effect=EmpleadoNoEncontradoError(999)),
        ),
    ):
        response = client.post("/empleados/999/activar", headers=_HEADERS)

    assert response.status_code == 404


# ── Authorization ──


def test_empleados_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/empleados")
    app.dependency_overrides.clear()
    assert response.status_code == 403
