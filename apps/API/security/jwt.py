import hashlib
import uuid
from datetime import datetime, timedelta

from jose import JWTError, jwt

from apps.API.core.config import get_settings
from apps.API.core.timezone import now as tz_now
from shared.exceptions.auth import RefreshTokenInvalidoError, TokenInvalidoError


def _settings():
    return get_settings()


def create_access_token(user_id: int, session_id: str) -> str:
    expire = tz_now() + timedelta(minutes=_settings().access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "type": "access",
        "exp": expire,
        "iat": tz_now(),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, _settings().jwt_secret_key, algorithm=_settings().jwt_algorithm)


def create_refresh_token(user_id: int, session_id: str) -> str:
    expire = tz_now() + timedelta(minutes=_settings().refresh_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "type": "refresh",
        "exp": expire,
        "iat": tz_now(),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, _settings().jwt_secret_key, algorithm=_settings().jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, _settings().jwt_secret_key, algorithms=[_settings().jwt_algorithm]
        )
    except JWTError:
        raise TokenInvalidoError()
    if payload.get("type") != "access":
        raise TokenInvalidoError()
    return payload


def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, _settings().jwt_secret_key, algorithms=[_settings().jwt_algorithm]
        )
    except JWTError:
        raise RefreshTokenInvalidoError()
    if payload.get("type") != "refresh":
        raise RefreshTokenInvalidoError()
    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
