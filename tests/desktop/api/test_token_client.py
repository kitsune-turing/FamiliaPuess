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


def test_solicitar_token_returns_parsed_token():
    token_payload = {
        "token": "tok-abc",
        "codigo_alfa": "A1B2C3",
        "generado_en": "2026-01-01T08:00:00+00:00",
        "expira_en": "2026-01-01T08:00:30+00:00",
    }

    with patch("apps.Desktop.api.token_client.httpx.post", return_value=_mock_response(token_payload)) as mock_post:
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", api_key="test-key")
        recibido = client.solicitar_token()

    assert recibido == TokenRecibido(
        token="tok-abc",
        codigo_alfa="A1B2C3",
        generado_en=datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc),
        expira_en=datetime(2026, 1, 1, 8, 0, 30, tzinfo=timezone.utc),
    )
    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["headers"]["X-Api-Key"] == "test-key"


def test_solicitar_token_sends_no_header_without_api_key():
    token_payload = {
        "token": "tok-abc",
        "codigo_alfa": "A1B2C3",
        "generado_en": "2026-01-01T08:00:00+00:00",
        "expira_en": "2026-01-01T08:00:30+00:00",
    }

    with patch("apps.Desktop.api.token_client.httpx.post", return_value=_mock_response(token_payload)) as mock_post:
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001")
        client.solicitar_token()

    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["headers"] == {}


def test_solicitar_token_raises_on_connection_failure():
    with patch("apps.Desktop.api.token_client.httpx.post", side_effect=httpx.ConnectError("boom")):
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", api_key="key")
        with pytest.raises(TokenClientError):
            client.solicitar_token()


def test_solicitar_token_raises_on_http_error_status():
    with patch("apps.Desktop.api.token_client.httpx.post", return_value=_mock_response({}, status_code=500)):
        client = TokenClient(base_url="http://api.local", dispositivo_identificador="KIOSK-001", api_key="key")
        with pytest.raises(TokenClientError):
            client.solicitar_token()
