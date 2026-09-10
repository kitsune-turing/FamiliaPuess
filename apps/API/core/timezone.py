from datetime import datetime, time
from functools import lru_cache
from zoneinfo import ZoneInfo

from apps.API.core.config import get_settings


@lru_cache
def get_zoneinfo() -> ZoneInfo:
    return ZoneInfo(get_settings().app_timezone)


def now() -> datetime:
    return datetime.now(get_zoneinfo())


def to_configured_timezone(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("value must be timezone-aware; naive datetimes are not supported")
    return value.astimezone(get_zoneinfo())


def extract_local_time(value: datetime) -> time:
    return to_configured_timezone(value).timetz().replace(tzinfo=None)
