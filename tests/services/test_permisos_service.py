from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import permisos_service
from shared.exceptions.permisos import (
    ModuloNoEncontradoError,
    PermisoDuplicadoError,
    PermisoNoEncontradoError,
)
from shared.exceptions.roles import RolNoEncontradoError

FIXED_NOW = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeModulo:
    id: int = 1
    codigo: str = "DASHBOARD"
    nombre: str = "Dashboard"


@dataclass
class _FakeRol:
    id: int = 1
    codigo: str = "ADMIN"
    nombre: str = "Administrador"


@dataclass
class _FakePermiso:
    id: int = 10
    id_rol: int = 1
    id_modulo: int = 1
    puede_leer: bool = True
    puede_escribir: bool = False
    puede_eliminar: bool = False
    puede_administrar: bool = False
    modulo: _FakeModulo = None

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeModulo()


def _patches(
    rol=None,
    modulo=None,
    permiso=None,
    existing_permiso=None,
    permisos_list=None,
):
    if rol is None:
        rol = _FakeRol()
    if modulo is None:
        modulo = _FakeModulo()
    if permiso is None:
        permiso = _FakePermiso()
    if permisos_list is None:
        permisos_list = [permiso]

    return {
        "get_rol_by_id": patch(
            "apps.API.repositories.cat_rol_repository.get_by_id",
            new=AsyncMock(return_value=rol),
        ),
        "get_modulo_by_id": patch(
            "apps.API.repositories.modulo_repository.get_by_id",
            new=AsyncMock(return_value=modulo),
        ),
        "get_permiso_by_id": patch(
            "apps.API.repositories.permiso_rol_repository.get_by_id",
            new=AsyncMock(return_value=permiso),
        ),
        "get_by_rol_and_modulo": patch(
            "apps.API.repositories.permiso_rol_repository.get_by_rol_and_modulo",
            new=AsyncMock(return_value=existing_permiso),
        ),
        "get_permisos_by_rol": patch(
            "apps.API.repositories.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=permisos_list),
        ),
        "create": patch(
            "apps.API.repositories.permiso_rol_repository.create",
            new=AsyncMock(return_value=permiso),
        ),
        "update_permiso": patch(
            "apps.API.repositories.permiso_rol_repository.update_permiso",
            new=AsyncMock(),
        ),
        "remove": patch(
            "apps.API.repositories.permiso_rol_repository.remove",
            new=AsyncMock(),
        ),
        "auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "now": patch(
            "apps.API.services.permisos_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# ── list_permisos_by_rol ──


async def test_list_permisos_returns_list():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_rol_by_id"], p["get_permisos_by_rol"]:
        result = await permisos_service.list_permisos_by_rol(session, 1)

    assert len(result) == 1


async def test_list_permisos_raises_when_rol_not_found():
    p = _patches(rol=None)
    p["get_rol_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_rol_by_id"]:
        with pytest.raises(RolNoEncontradoError):
            await permisos_service.list_permisos_by_rol(session, 999)


# ── create_permiso ──


async def test_create_permiso_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_rol_by_id"],
        p["get_modulo_by_id"],
        p["get_by_rol_and_modulo"],
        p["create"] as mock_create,
        p["auditoria"],
        p["now"],
    ):
        result = await permisos_service.create_permiso(
            session,
            1,
            id_modulo=1,
            puede_leer=True,
            user_id=1,
        )

    assert result.puede_leer is True
    mock_create.assert_awaited_once()


async def test_create_permiso_raises_when_rol_not_found():
    p = _patches()
    p["get_rol_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_rol_by_id"]:
        with pytest.raises(RolNoEncontradoError):
            await permisos_service.create_permiso(
                session, 999, id_modulo=1, user_id=1
            )


async def test_create_permiso_raises_when_modulo_not_found():
    p = _patches()
    p["get_modulo_by_id"] = patch(
        "apps.API.repositories.modulo_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_rol_by_id"], p["get_modulo_by_id"]:
        with pytest.raises(ModuloNoEncontradoError):
            await permisos_service.create_permiso(
                session, 1, id_modulo=999, user_id=1
            )


async def test_create_permiso_raises_on_duplicate():
    existing = _FakePermiso()
    p = _patches(existing_permiso=existing)
    session = AsyncMock(spec=AsyncSession)

    with p["get_rol_by_id"], p["get_modulo_by_id"], p["get_by_rol_and_modulo"]:
        with pytest.raises(PermisoDuplicadoError):
            await permisos_service.create_permiso(
                session, 1, id_modulo=1, user_id=1
            )


# ── update_permiso ──


async def test_update_permiso_success():
    updated = _FakePermiso(puede_escribir=True)
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_permiso_by_id"],
        p["update_permiso"] as mock_update,
        p["auditoria"],
        p["now"],
        patch(
            "apps.API.repositories.permiso_rol_repository.get_by_id",
            new=AsyncMock(side_effect=[_FakePermiso(), updated]),
        ),
    ):
        result = await permisos_service.update_permiso(
            session, 10, puede_escribir=True, user_id=1
        )


async def test_update_permiso_raises_when_not_found():
    p = _patches()
    p["get_permiso_by_id"] = patch(
        "apps.API.repositories.permiso_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_permiso_by_id"]:
        with pytest.raises(PermisoNoEncontradoError):
            await permisos_service.update_permiso(
                session, 999, puede_leer=True, user_id=1
            )


# ── delete_permiso ──


async def test_delete_permiso_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_permiso_by_id"],
        p["remove"] as mock_remove,
        p["auditoria"],
        p["now"],
    ):
        await permisos_service.delete_permiso(session, 10, user_id=1)

    mock_remove.assert_awaited_once()


async def test_delete_permiso_raises_when_not_found():
    p = _patches()
    p["get_permiso_by_id"] = patch(
        "apps.API.repositories.permiso_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_permiso_by_id"]:
        with pytest.raises(PermisoNoEncontradoError):
            await permisos_service.delete_permiso(session, 999, user_id=1)
