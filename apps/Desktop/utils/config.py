from __future__ import annotations

import configparser
import os
import platform
import uuid
from pathlib import Path

_CONFIG_DIR = Path.home() / ".familia_puess"
_CONFIG_FILE = _CONFIG_DIR / "config.ini"


def _read_local_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    if _CONFIG_FILE.is_file():
        cfg.read(str(_CONFIG_FILE), encoding="utf-8")
    return cfg


def _write_local_config(cfg: configparser.ConfigParser) -> None:
    _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        cfg.write(f)


def get_api_key() -> str:
    """Resolve the API key: env var > local config file."""
    from_env = os.getenv("DESKTOP_API_KEY", "")
    if from_env:
        return from_env
    cfg = _read_local_config()
    return cfg.get("auth", "api_key", fallback="")


def save_api_key(key: str) -> None:
    """Persist the API key to ~/.familia_puess/config.ini."""
    cfg = _read_local_config()
    if not cfg.has_section("auth"):
        cfg.add_section("auth")
    cfg.set("auth", "api_key", key)
    _write_local_config(cfg)


def get_device_id() -> str:
    """Resolve device ID: env var > local config file > generate new."""
    from_env = os.getenv("DESKTOP_DISPOSITIVO_ID", "")
    if from_env:
        return from_env

    cfg = _read_local_config()
    stored = cfg.get("device", "id", fallback="")
    if stored:
        return stored

    # Migrate from legacy file (~/.familia_puess_device_id)
    legacy = Path.home() / ".familia_puess_device_id"
    if legacy.is_file():
        stored = legacy.read_text(encoding="utf-8").strip()
        if stored:
            save_device_id(stored)
            return stored

    hostname = platform.node() or "DESKTOP"
    new_id = hostname if len(hostname) >= 5 else f"DESK-{hostname}"
    save_device_id(new_id)
    return new_id


def save_device_id(device_id: str) -> None:
    """Persist the device ID to ~/.familia_puess/config.ini."""
    cfg = _read_local_config()
    if not cfg.has_section("device"):
        cfg.add_section("device")
    cfg.set("device", "id", device_id)
    _write_local_config(cfg)
