from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import httpx
import pytest

from apps.Desktop.api.token_client import TokenClient, TokenClientError, TokenRecibido


def _mock_response(json_payload, status_code=200):
    response = MagicMock(spec=httpx.Response)
    response.json.return_value = json_payload
    response.status_code = status_code
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "error", request=MagicMock(), response=response
        )
    return response


def _login_response():
    return _mock_response({
        "access_token": "fake-jwt",
        "refresh_token": "fake-refresh",
        "token_type": "bearer",
    })


def test_solicitar_token_returns_parsed_token_unmodified():
    token_payload = {
        "token": "tok-abc",
        "codigo_alfa": "A1B2C3",
        "generado_en": "2026-01-01T08:00:00+00:00",
        "expira_en": "2026-01-01T08:00:30+00:00",
    }

    def side_effect(url, **kwargs):
        if "/auth/login" in url:
            return _login_response()
        return _mock_response(token_payload)

    with patch("apps.Desktop.api.token_client.httpx.post", side_effect=side_effect) as mock_post:
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", username="test", password="test")
        recibido = client.solicitar_token()

    assert recibido == TokenRecibido(
        token="tok-abc",
        codigo_alfa="A1B2C3",
        generado_en=datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
        expira_en=datetime(2026, 1, 1, 8, 0, 30, tzinfo=timezone.utc),
    )
    calls = mock_post.call_args_list
    assert any("/auth/login" in str(c) for c in calls)
    assert any("/desktop/tokens" in str(c) for c in calls)


def test_solicitar_token_raises_token_client_error_on_connection_failure():
    def side_effect(url, **kwargs):
        if "/auth/login" in url:
            return _login_response()
        raise httpx.ConnectError("boom")

    with patch("apps.Desktop.api.token_client.httpx.post", side_effect=side_effect):
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", username="test", password="test")
        with pytest.raises(TokenClientError):
            client.solicitar_token()


def test_solicitar_token_raises_token_client_error_on_http_error_status():
    def side_effect(url, **kwargs):
        if "/auth/login" in url:
            return _login_response()
        return _mock_response({}, status_code=500)

    with patch("apps.Desktop.api.token_client.httpx.post", side_effect=side_effect):
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", username="test", password="test")
        with pytest.raises(TokenClientError):
            client.solicitar_token()
