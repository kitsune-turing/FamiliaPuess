from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from apps.Desktop.api.token_client import TokenClientError, TokenRecibido
from apps.Desktop.workers.token_rotation_worker import TokenRotationWorker


def _token(seconds_valid: float = 30) -> TokenRecibido:
    now = datetime.now(timezone.utc)
    return TokenRecibido(
        token="tok",
        codigo_alfa="ABC123",
        generado_en=now,
        expira_en=now + timedelta(seconds=seconds_valid),
    )


def test_start_emits_token_ready_on_success(qtbot):
    client = MagicMock()
    client.solicitar_token.return_value = _token()
    worker = TokenRotationWorker(client=client, fallback_interval_seconds=30)

    with qtbot.waitSignal(worker.token_ready, timeout=2000) as blocker:
        worker.start()

    assert blocker.args[0].token == "tok"


def test_start_emits_token_error_on_failure(qtbot):
    client = MagicMock()
    client.solicitar_token.side_effect = TokenClientError("network down")
    worker = TokenRotationWorker(client=client, fallback_interval_seconds=30)

    with qtbot.waitSignal(worker.token_error, timeout=2000) as blocker:
        worker.start()

    assert "network down" in blocker.args[0]


def test_next_interval_uses_server_provided_validity_window():
    worker = TokenRotationWorker(client=MagicMock(), fallback_interval_seconds=99)

    interval = worker._next_interval_seconds(_token(seconds_valid=45))

    assert interval == 45


def test_next_interval_falls_back_when_token_already_expired():
    worker = TokenRotationWorker(client=MagicMock(), fallback_interval_seconds=99)

    interval = worker._next_interval_seconds(_token(seconds_valid=-5))

    assert interval == 99
