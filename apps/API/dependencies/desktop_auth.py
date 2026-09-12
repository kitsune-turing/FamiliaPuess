import hmac

from fastapi import Header

from apps.API.core.config import get_settings
from shared.exceptions.auth import TokenInvalidoError


async def require_desktop_api_key(
    x_api_key: str = Header(..., alias="X-Api-Key"),
) -> str:
    settings = get_settings()
    if not settings.desktop_api_key or not hmac.compare_digest(
        x_api_key.encode(), settings.desktop_api_key.encode()
    ):
        raise TokenInvalidoError()
    return x_api_key
