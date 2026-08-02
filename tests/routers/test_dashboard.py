from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from apps.API.schemas.dashboard import DashboardResponse

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "DASHBOARD"


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


async def test_get_dashboard_returns_200(client):
    response_data = DashboardResponse(
        empleados_activos=25,
        asistencias_hoy=10,
        novedades_hoy=3,
        tardanzas_hoy=2,
    )
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.dashboard.dashboard_service.get_indicadores",
            new=AsyncMock(return_value=response_data),
        ),
    ):
        resp = client.get("/dashboard", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["empleados_activos"] == 25
    assert body["asistencias_hoy"] == 10
    assert body["novedades_hoy"] == 3
    assert body["tardanzas_hoy"] == 2


async def test_get_dashboard_all_zeros(client):
    response_data = DashboardResponse(
        empleados_activos=0,
        asistencias_hoy=0,
        novedades_hoy=0,
        tardanzas_hoy=0,
    )
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.dashboard.dashboard_service.get_indicadores",
            new=AsyncMock(return_value=response_data),
        ),
    ):
        resp = client.get("/dashboard", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["empleados_activos"] == 0
    assert body["asistencias_hoy"] == 0
    assert body["novedades_hoy"] == 0
    assert body["tardanzas_hoy"] == 0


async def test_get_dashboard_returns_all_four_indicators(client):
    response_data = DashboardResponse(
        empleados_activos=100,
        asistencias_hoy=90,
        novedades_hoy=5,
        tardanzas_hoy=3,
    )
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.dashboard.dashboard_service.get_indicadores",
            new=AsyncMock(return_value=response_data),
        ),
    ):
        resp = client.get("/dashboard", headers=_HEADERS)
    body = resp.json()
    assert set(body.keys()) == {
        "empleados_activos",
        "asistencias_hoy",
        "novedades_hoy",
        "tardanzas_hoy",
    }


async def test_dashboard_without_token_returns_403():
    app.dependency_overrides[get_session] = _fake_session
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    try:
        with TestClient(app) as test_client:
            resp = test_client.get("/dashboard")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


async def test_dashboard_without_permission_returns_403(client):
    no_perm = _FakePermiso()
    no_perm.modulo = _FakeModulo(codigo="OTRO")
    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeAuthUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[no_perm]),
        ),
    ):
        resp = client.get("/dashboard", headers=_HEADERS)
    assert resp.status_code == 403
