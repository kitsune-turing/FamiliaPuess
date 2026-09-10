from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.dependencies.auth import get_current_user
from apps.API.main import app
from shared.exceptions.configuration import SetupIncompletoError

_CURRENT_USER = {"sub": "1", "type": "access"}


async def _fake_session():
    yield object()


async def _fake_current_user():
    return _CURRENT_USER


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    app.dependency_overrides[get_current_user] = _fake_current_user
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


_HEADERS = {"Authorization": "Bearer valid.jwt"}


def test_get_estado_inicial_completed(client):
    with patch(
        "apps.API.routers.configuracion.configuracion_service.get_setup_status",
        new=AsyncMock(return_value={"setup_completado": True, "pasos": []}),
    ):
        response = client.get("/configuracion/estado-inicial", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["setup_completado"] is True
    assert body["pasos"] == []


def test_get_estado_inicial_pending(client):
    pasos = [
        {"clave": "CAMBIO_CONTRASENA", "descripcion": "Cambiar contrasena inicial", "completado": False},
        {"clave": "SEDE_REGISTRADA", "descripcion": "Registrar al menos una sede", "completado": True},
        {"clave": "DISPOSITIVO_REGISTRADO", "descripcion": "Registrar al menos un dispositivo", "completado": True},
        {"clave": "EMPLEADO_REGISTRADO", "descripcion": "Registrar al menos un empleado", "completado": False},
    ]
    with patch(
        "apps.API.routers.configuracion.configuracion_service.get_setup_status",
        new=AsyncMock(return_value={"setup_completado": False, "pasos": pasos}),
    ):
        response = client.get("/configuracion/estado-inicial", headers=_HEADERS)

    assert response.status_code == 200
    body = response.json()
    assert body["setup_completado"] is False
    assert len(body["pasos"]) == 4


def test_completar_setup_returns_200(client):
    with patch(
        "apps.API.routers.configuracion.configuracion_service.completar_setup",
        new=AsyncMock(),
    ):
        response = client.post("/configuracion/completar-setup", headers=_HEADERS)

    assert response.status_code == 200
    assert "completada" in response.json()["detail"]


def test_completar_setup_returns_422_when_incomplete(client):
    with patch(
        "apps.API.routers.configuracion.configuracion_service.completar_setup",
        new=AsyncMock(side_effect=SetupIncompletoError("SEDE_REGISTRADA, EMPLEADO_REGISTRADO")),
    ):
        response = client.post("/configuracion/completar-setup", headers=_HEADERS)

    assert response.status_code == 422
    assert "pendientes" in response.json()["detail"].lower()
