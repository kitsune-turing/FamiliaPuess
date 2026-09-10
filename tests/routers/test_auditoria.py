from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from apps.API.schemas.auditoria import AuditoriaListResponse, AuditoriaResponse

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
    codigo: str = "AUDITORIA"


@dataclass
class _FakePermiso:
    modulo: _FakeModulo = None
    puede_leer: bool = True
    puede_escribir: bool = False
    puede_eliminar: bool = False
    puede_administrar: bool = False

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

_SAMPLE_RESPONSE = AuditoriaListResponse(
    items=[
        AuditoriaResponse(
            id=1,
            id_usuario=1,
            recurso="USUARIO",
            id_recurso="5",
            operacion="INSERT",
            valor_anterior=None,
            valor_nuevo={"nombre": "Admin"},
            ip_address="127.0.0.1",
            detalle=None,
            timestamp_accion=datetime(2026, 8, 1, 10, 0, 0, tzinfo=timezone.utc),
        ),
    ],
    total=1,
)


async def test_list_auditoria_returns_200(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.auditoria.auditoria_service.list_auditoria",
            new=AsyncMock(return_value=_SAMPLE_RESPONSE),
        ),
    ):
        resp = client.get("/auditoria", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["recurso"] == "USUARIO"


async def test_list_auditoria_with_filters(client):
    service_mock = AsyncMock(
        return_value=AuditoriaListResponse(items=[], total=0)
    )
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.auditoria.auditoria_service.list_auditoria",
            new=service_mock,
        ),
    ):
        resp = client.get(
            "/auditoria?id_usuario=5&recurso=EMPLEADO&operacion=UPDATE"
            "&fecha_desde=2026-07-01&fecha_hasta=2026-08-01&limit=10&offset=5",
            headers=_HEADERS,
        )
    assert resp.status_code == 200
    call_kwargs = service_mock.call_args[1]
    assert call_kwargs["id_usuario"] == 5
    assert call_kwargs["recurso"] == "EMPLEADO"
    assert call_kwargs["operacion"] == "UPDATE"
    assert call_kwargs["limit"] == 10
    assert call_kwargs["offset"] == 5


async def test_list_auditoria_empty(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.auditoria.auditoria_service.list_auditoria",
            new=AsyncMock(
                return_value=AuditoriaListResponse(items=[], total=0)
            ),
        ),
    ):
        resp = client.get("/auditoria", headers=_HEADERS)
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["items"] == []


async def test_auditoria_without_token_returns_403():
    app.dependency_overrides[get_session] = _fake_session
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    try:
        with TestClient(app) as test_client:
            resp = test_client.get("/auditoria")
        assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()


async def test_auditoria_without_permission_returns_403(client):
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
        patch(
            "apps.API.dependencies.auth.auditoria_repository.create",
            new=AsyncMock(),
        ),
    ):
        resp = client.get("/auditoria", headers=_HEADERS)
    assert resp.status_code == 403


async def test_list_auditoria_response_has_all_fields(client):
    p1, p2 = _permission_patches()
    with (
        p1,
        p2,
        patch(
            "apps.API.routers.auditoria.auditoria_service.list_auditoria",
            new=AsyncMock(return_value=_SAMPLE_RESPONSE),
        ),
    ):
        resp = client.get("/auditoria", headers=_HEADERS)
    item = resp.json()["items"][0]
    expected_keys = {
        "id",
        "id_usuario",
        "recurso",
        "id_recurso",
        "operacion",
        "valor_anterior",
        "valor_nuevo",
        "ip_address",
        "detalle",
        "timestamp_accion",
    }
    assert set(item.keys()) == expected_keys
