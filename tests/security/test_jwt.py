import pytest

from apps.API.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_token,
)
from shared.exceptions.auth import RefreshTokenInvalidoError, TokenInvalidoError


def test_create_and_decode_access_token():
    token = create_access_token(user_id=1, session_id="sess-123")
    payload = decode_access_token(token)

    assert payload["sub"] == "1"
    assert payload["sid"] == "sess-123"
    assert payload["type"] == "access"


def test_create_and_decode_refresh_token():
    token = create_refresh_token(user_id=2, session_id="sess-456")
    payload = decode_refresh_token(token)

    assert payload["sub"] == "2"
    assert payload["sid"] == "sess-456"
    assert payload["type"] == "refresh"


def test_decode_access_token_rejects_refresh_token():
    refresh = create_refresh_token(user_id=1, session_id="s")

    with pytest.raises(TokenInvalidoError):
        decode_access_token(refresh)


def test_decode_refresh_token_rejects_access_token():
    access = create_access_token(user_id=1, session_id="s")

    with pytest.raises(RefreshTokenInvalidoError):
        decode_refresh_token(access)


def test_decode_access_token_raises_on_garbage():
    with pytest.raises(TokenInvalidoError):
        decode_access_token("not.a.valid.jwt")


def test_decode_refresh_token_raises_on_garbage():
    with pytest.raises(RefreshTokenInvalidoError):
        decode_refresh_token("not.a.valid.jwt")


def test_hash_token_is_deterministic():
    assert hash_token("abc") == hash_token("abc")


def test_hash_token_differs_for_different_inputs():
    assert hash_token("abc") != hash_token("def")
