from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.main import app
from apps.API.services.registro_service import RegistroExitoso, TokenValidado
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.employee import EmpleadoInactivoError, EmpleadoNoRegistradoError
from shared.exceptions.registration import (
    CodigoAlfaInvalidoError,
    DispositivoTokenNoAutorizadoError,
    SedeNoDisponibleError,
    TokenConsumidoError,
    TokenExpiradoError,
    TokenFormatoInvalidoError,
    TokenNoEncontradoError,
)

FIXED_NOW = datetime(2026, 7, 22, 8, 0, 0, tzinfo=timezone.utc)


async def _fake_session():
    yield object()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ── GET /registro/validar/{token} ──


def test_validar_token_returns_200_with_sede(client):
    resultado = TokenValidado(token="tok-abc", sede_nombre="Sede Central")

    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(return_value=resultado),
    ):
        response = client.get("/registro/validar/tok-abc")

    assert response.status_code == 200
    body = response.json()
    assert body["token"] == "tok-abc"
    assert body["sede_nombre"] == "Sede Central"


def test_validar_token_returns_404_when_not_found(client):
    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(side_effect=TokenNoEncontradoError()),
    ):
        response = client.get("/registro/validar/invalid-token")

    assert response.status_code == 404


def test_validar_token_returns_404_when_format_invalid(client):
    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(side_effect=TokenFormatoInvalidoError()),
    ):
        response = client.get("/registro/validar/x")

    assert response.status_code == 404


def test_validar_token_returns_410_when_expired(client):
    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(side_effect=TokenExpiradoError()),
    ):
        response = client.get("/registro/validar/expired-token")

    assert response.status_code == 410


def test_validar_token_returns_410_when_consumed(client):
    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(side_effect=TokenConsumidoError()),
    ):
        response = client.get("/registro/validar/consumed-token")

    assert response.status_code == 410


def test_validar_token_returns_403_when_sede_unavailable(client):
    with patch(
        "apps.API.routers.registro.registro_service.validar_token",
        new=AsyncMock(side_effect=SedeNoDisponibleError()),
    ):
        response = client.get("/registro/validar/some-token")

    assert response.status_code == 403


# ── POST /registro/registrar ──


def test_registrar_returns_201_on_success(client):
    resultado = RegistroExitoso(
        empleado_nombre="Juan Perez",
        sede_nombre="Sede Central",
        registrado_en=FIXED_NOW,
    )

    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(return_value=resultado),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["empleado_nombre"] == "Juan Perez"
    assert body["sede_nombre"] == "Sede Central"
    assert body["mensaje"] == "Asistencia registrada correctamente"


def test_registrar_returns_422_when_body_missing(client):
    response = client.post("/registro/registrar", json={})

    assert response.status_code == 422


def test_registrar_returns_404_when_empleado_not_found(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(side_effect=EmpleadoNoRegistradoError()),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "000000", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 404


def test_registrar_returns_403_when_empleado_inactive(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(side_effect=EmpleadoInactivoError()),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 403


def test_registrar_returns_422_when_codigo_alfa_invalid(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(side_effect=CodigoAlfaInvalidoError()),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "WRONG"},
        )

    assert response.status_code == 422


def test_registrar_returns_403_when_dispositivo_not_authorized(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(side_effect=DispositivoTokenNoAutorizadoError()),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 403


def test_registrar_returns_409_when_duplicate_attendance(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(
            side_effect=AsistenciaDuplicadaError(
                hora_anterior=FIXED_NOW, sede_anterior="Sede Central"
            )
        ),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 409


def test_registrar_returns_410_when_token_expired(client):
    with patch(
        "apps.API.routers.registro.registro_service.registrar_asistencia",
        new=AsyncMock(side_effect=TokenExpiradoError()),
    ):
        response = client.post(
            "/registro/registrar",
            json={"token": "tok-abc", "documento": "123456", "codigo_alfa": "A1B2C3"},
        )

    assert response.status_code == 410
