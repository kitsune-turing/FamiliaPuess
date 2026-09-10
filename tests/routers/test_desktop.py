from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from apps.API.database.session import get_session
from apps.API.main import app
from apps.API.services.token_service import TokenGenerado
from shared.exceptions.device import DispositivoNoAutorizadoError, DispositivoNoEncontradoError

_TEST_API_KEY = "test-desktop-api-key"
_HEADERS = {"X-Api-Key": _TEST_API_KEY}


async def _fake_session():
    yield object()


@pytest.fixture
def client():
    app.dependency_overrides[get_session] = _fake_session
    with patch("apps.API.dependencies.desktop_auth.get_settings") as mock_settings:
        mock_settings.return_value.desktop_api_key = _TEST_API_KEY
        with TestClient(app) as test_client:
            yield test_client
    app.dependency_overrides.clear()


def test_generar_token_returns_201_with_expected_payload(client):
    generado_en = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
    expira_en = generado_en + timedelta(seconds=30)
    resultado = TokenGenerado(
        token="tok-123", codigo_alfa="A1B2C3", generado_en=generado_en, expira_en=expira_en
    )

    with patch(
        "apps.API.routers.desktop.token_service.generate_token",
        new=AsyncMock(return_value=resultado),
    ):
        response = client.post(
            "/desktop/tokens",
            headers=_HEADERS,
            json={"dispositivo_identificador": "KIOSK-001"},
        )

    assert response.status_code == 201
    body = response.json()
    assert body["token"] == "tok-123"
    assert body["codigo_alfa"] == "A1B2C3"


def test_generar_token_returns_404_when_dispositivo_not_found(client):
    with patch(
        "apps.API.routers.desktop.token_service.generate_token",
        new=AsyncMock(side_effect=DispositivoNoEncontradoError("NO-EXISTE")),
    ):
        response = client.post(
            "/desktop/tokens",
            headers=_HEADERS,
            json={"dispositivo_identificador": "NO-EXISTE"},
        )

    assert response.status_code == 404


def test_generar_token_returns_403_when_dispositivo_no_autorizado(client):
    with patch(
        "apps.API.routers.desktop.token_service.generate_token",
        new=AsyncMock(side_effect=DispositivoNoAutorizadoError("KIOSK-001")),
    ):
        response = client.post(
            "/desktop/tokens",
            headers=_HEADERS,
            json={"dispositivo_identificador": "KIOSK-001"},
        )

    assert response.status_code == 403


def test_generar_token_requires_dispositivo_identificador(client):
    response = client.post("/desktop/tokens", headers=_HEADERS, json={})
    assert response.status_code == 422


def test_generar_token_rejects_missing_api_key(client):
    with patch(
        "apps.API.routers.desktop.token_service.generate_token",
        new=AsyncMock(return_value=None),
    ):
        response = client.post(
            "/desktop/tokens",
            json={"dispositivo_identificador": "KIOSK-001"},
        )

    assert response.status_code == 422


def test_generar_token_rejects_wrong_api_key(client):
    with patch(
        "apps.API.routers.desktop.token_service.generate_token",
        new=AsyncMock(return_value=None),
    ):
        response = client.post(
            "/desktop/tokens",
            headers={"X-Api-Key": "wrong-key"},
            json={"dispositivo_identificador": "KIOSK-001"},
        )

    assert response.status_code == 401
