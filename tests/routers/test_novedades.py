from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.novedades import NovedadNoEncontradaError

FIXED_NOW = datetime(2026, 7, 28, 10, 0, 0, tzinfo=timezone.utc)

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@dataclass
class _FakeEmpleado:
    id: int = 1
    nombre: str = "Juan Perez"
    documento: str = "1234567890"


@dataclass
class _FakeCatNovedad:
    id: int = 1
    codigo: str = "TARDANZA"
    nombre: str = "Tardanza"
    color: str | None = "#FF0000"
    icono: str | None = "clock-alert"


@dataclass
class _FakeNovedad:
    id: int = 10
    id_empleado: int = 1
    id_tipo_novedad: int = 1
    id_asistencia: int | None = 100
    fecha: date = field(default_factory=lambda: date(2026, 7, 28))
    observacion: str | None = "Registro a las 08:30"
    created_at: datetime = field(default_factory=lambda: FIXED_NOW)
    empleado: _FakeEmpleado = field(default_factory=_FakeEmpleado)
    tipo_novedad: _FakeCatNovedad = field(default_factory=_FakeCatNovedad)


@dataclass
class _FakeAuthUsuario:
    id: int = 1
    id_rol: int = 1


@dataclass
class _FakeModulo:
    codigo: str = "NOVEDADES"


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


# --- GET /novedades ---


async def test_list_novedades_returns_200(client):
    fake_list = [_FakeNovedad(id=10), _FakeNovedad(id=11)]
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.list_novedades",
            new=AsyncMock(return_value=fake_list),
        ),
    ):
        resp = client.get("/novedades", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_list_novedades_with_filters(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.list_novedades",
            new=AsyncMock(return_value=[_FakeNovedad()]),
        ),
    ):
        resp = client.get(
            "/novedades?id_empleado=1&fecha_desde=2026-07-01&fecha_hasta=2026-07-31",
            headers=_HEADERS,
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1


async def test_list_novedades_empty(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.list_novedades",
            new=AsyncMock(return_value=[]),
        ),
    ):
        resp = client.get("/novedades", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


async def test_list_novedades_includes_visual_fields(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.list_novedades",
            new=AsyncMock(return_value=[_FakeNovedad()]),
        ),
    ):
        resp = client.get("/novedades", headers=_HEADERS)
    assert resp.status_code == 200
    item = resp.json()["items"][0]
    assert item["tipo_color"] == "#FF0000"
    assert item["tipo_icono"] == "clock-alert"
    assert item["tipo_codigo"] == "TARDANZA"
    assert item["tipo_nombre"] == "Tardanza"
    assert item["empleado_nombre"] == "Juan Perez"
    assert item["empleado_documento"] == "1234567890"


# --- GET /novedades/{id} ---


async def test_get_novedad_returns_200(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.get_novedad",
            new=AsyncMock(return_value=_FakeNovedad()),
        ),
    ):
        resp = client.get("/novedades/10", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == 10


async def test_get_novedad_not_found_returns_404(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.novedades.novedades_service.get_novedad",
            new=AsyncMock(side_effect=NovedadNoEncontradaError(999)),
        ),
    ):
        resp = client.get("/novedades/999", headers=_HEADERS)
    assert resp.status_code == 404


# --- Auth ---


async def test_novedades_without_token_returns_403():
    app.dependency_overrides[get_session] = _fake_session
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    try:
        with TestClient(app) as test_client:
            resp = test_client.get("/novedades")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()
