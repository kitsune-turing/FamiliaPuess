from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.device import (
    DispositivoNoEncontradoPorIdError,
    IdentificadorDuplicadoError,
    IdentificadorFormatoInvalidoError,
    SedeYaTieneDispositivoError,
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
class _FakeDispositivo:
    id: int = 10
    identificador: str = "DEVICE-001-ABC"
    id_sede: int = 1
    id_estado: int = 1
    descripcion: str = "Celular Samsung"
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
    codigo: str = "DISPOSITIVOS"


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


# ── GET /dispositivos ──


def test_list_dispositivos_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.list_dispositivos",
            new=AsyncMock(return_value=[_FakeDispositivo()]),
        ),
    ):
        response = client.get("/dispositivos", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["identificador"] == "DEVICE-001-ABC"
    assert body["items"][0]["sede_nombre"] == "Sede Central"


def test_list_dispositivos_with_filters(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.list_dispositivos",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/dispositivos?id_sede=1&id_estado=1",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_list_dispositivos_no_results(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.list_dispositivos",
            new=AsyncMock(return_value=[]),
        ),
    ):
        response = client.get(
            "/dispositivos?identificador=NOEXISTE",
            headers=_HEADERS,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 0
    assert body["items"] == []


# ── GET /dispositivos/{id} ──


def test_get_dispositivo_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.get_dispositivo",
            new=AsyncMock(return_value=_FakeDispositivo()),
        ),
    ):
        response = client.get("/dispositivos/10", headers=_HEADERS)

    assert response.status_code == 200
    assert response.json()["id"] == 10
    assert response.json()["identificador"] == "DEVICE-001-ABC"


def test_get_dispositivo_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.get_dispositivo",
            new=AsyncMock(side_effect=DispositivoNoEncontradoPorIdError(999)),
        ),
    ):
        response = client.get("/dispositivos/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /dispositivos ──


def test_create_dispositivo_returns_201(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(return_value=_FakeDispositivo()),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-001-ABC",
                "id_sede": 1,
                "descripcion": "Celular Samsung",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["identificador"] == "DEVICE-001-ABC"
    assert body["sede_nombre"] == "Sede Central"


def test_create_dispositivo_returns_409_duplicate_identificador(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(side_effect=IdentificadorDuplicadoError("DEVICE-001-ABC")),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-001-ABC",
                "id_sede": 1,
            },
        )

    assert response.status_code == 409


def test_create_dispositivo_returns_422_invalid_identificador(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(side_effect=IdentificadorFormatoInvalidoError()),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEV @#$!",
                "id_sede": 1,
            },
        )

    assert response.status_code == 422


def test_create_dispositivo_returns_422_missing_fields(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={"identificador": "DEVICE-001"},
        )

    assert response.status_code == 422


def test_create_dispositivo_returns_404_sede_not_found(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(side_effect=SedeNoEncontradaError(999)),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-002-XYZ",
                "id_sede": 999,
            },
        )

    assert response.status_code == 404


def test_create_dispositivo_returns_422_sede_inactiva(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(side_effect=SedeInactivaError(1)),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-002-XYZ",
                "id_sede": 1,
            },
        )

    assert response.status_code == 422


def test_create_dispositivo_returns_409_sede_already_has_device(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.create_dispositivo",
            new=AsyncMock(side_effect=SedeYaTieneDispositivoError(1)),
        ),
    ):
        response = client.post(
            "/dispositivos",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-002-XYZ",
                "id_sede": 1,
            },
        )

    assert response.status_code == 409


# ── PUT /dispositivos/{id} ──


def test_update_dispositivo_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.update_dispositivo",
            new=AsyncMock(
                return_value=_FakeDispositivo(identificador="DEVICE-003-NEW")
            ),
        ),
    ):
        response = client.put(
            "/dispositivos/10",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-003-NEW",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 200


def test_update_dispositivo_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.update_dispositivo",
            new=AsyncMock(side_effect=DispositivoNoEncontradoPorIdError(999)),
        ),
    ):
        response = client.put(
            "/dispositivos/999",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-NEW",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 404


def test_update_dispositivo_returns_409_concurrency(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.update_dispositivo",
            new=AsyncMock(
                side_effect=ConflictoConcurrenciaError("dispositivo", 10)
            ),
        ),
    ):
        response = client.put(
            "/dispositivos/10",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-NEW",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_dispositivo_returns_409_duplicate_identificador(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.update_dispositivo",
            new=AsyncMock(side_effect=IdentificadorDuplicadoError("DEVICE-OTHER")),
        ),
    ):
        response = client.put(
            "/dispositivos/10",
            headers=_HEADERS,
            json={
                "identificador": "DEVICE-OTHER",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 409


def test_update_dispositivo_returns_422_missing_updated_at(client):
    p_user, p_permisos = _permission_patches()

    with p_user, p_permisos:
        response = client.put(
            "/dispositivos/10",
            headers=_HEADERS,
            json={"identificador": "DEVICE-NEW"},
        )

    assert response.status_code == 422


def test_update_dispositivo_returns_422_invalid_identificador(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.update_dispositivo",
            new=AsyncMock(side_effect=IdentificadorFormatoInvalidoError()),
        ),
    ):
        response = client.put(
            "/dispositivos/10",
            headers=_HEADERS,
            json={
                "identificador": "DEV @#$",
                "updated_at": FIXED_NOW.isoformat(),
            },
        )

    assert response.status_code == 422


# ── DELETE /dispositivos/{id} ──


def test_deactivate_dispositivo_returns_204(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.deactivate_dispositivo",
            new=AsyncMock(),
        ),
    ):
        response = client.delete("/dispositivos/10", headers=_HEADERS)

    assert response.status_code == 204


def test_deactivate_dispositivo_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.deactivate_dispositivo",
            new=AsyncMock(side_effect=DispositivoNoEncontradoPorIdError(999)),
        ),
    ):
        response = client.delete("/dispositivos/999", headers=_HEADERS)

    assert response.status_code == 404


# ── POST /dispositivos/{id}/activar ──


def test_activate_dispositivo_returns_200(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.activate_dispositivo",
            new=AsyncMock(return_value=_FakeDispositivo(id_estado=1)),
        ),
    ):
        response = client.post("/dispositivos/10/activar", headers=_HEADERS)

    assert response.status_code == 200


def test_activate_dispositivo_returns_404(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.activate_dispositivo",
            new=AsyncMock(side_effect=DispositivoNoEncontradoPorIdError(999)),
        ),
    ):
        response = client.post("/dispositivos/999/activar", headers=_HEADERS)

    assert response.status_code == 404


def test_activate_dispositivo_returns_409_sede_already_has_active(client):
    p_user, p_permisos = _permission_patches()

    with (
        p_user,
        p_permisos,
        patch(
            "apps.API.routers.dispositivos.dispositivos_service.activate_dispositivo",
            new=AsyncMock(side_effect=SedeYaTieneDispositivoError(1)),
        ),
    ):
        response = client.post("/dispositivos/10/activar", headers=_HEADERS)

    assert response.status_code == 409


# ── Authorization ──


def test_dispositivos_returns_403_without_token():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides.pop(get_current_user, None)
    with TestClient(app) as c:
        response = c.get("/dispositivos")
    app.dependency_overrides.clear()
    assert response.status_code == 403
