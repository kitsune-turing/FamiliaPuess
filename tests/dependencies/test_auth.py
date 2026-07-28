from dataclasses import dataclass
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.dependencies.auth import require_permission
from shared.exceptions.auth import PermisoInsuficienteError, TokenInvalidoError


@dataclass
class _FakeModulo:
    codigo: str = "DASHBOARD"


@dataclass
class _FakePermiso:
    puede_leer: bool = True
    puede_escribir: bool = False
    puede_eliminar: bool = False
    puede_administrar: bool = False
    modulo: _FakeModulo = None

    def __post_init__(self):
        if self.modulo is None:
            self.modulo = _FakeModulo()


@dataclass
class _FakeUsuario:
    id: int = 1
    id_rol: int = 1


async def test_require_permission_allows_authorized_user():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "leer")

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    ):
        result = await checker(current_user=current_user, session=session)

    assert result["sub"] == "1"


async def test_require_permission_denies_unauthorized_user():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "escribir")

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    ):
        with pytest.raises(PermisoInsuficienteError):
            await checker(current_user=current_user, session=session)


async def test_require_permission_denies_wrong_module():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("USUARIOS", "leer")

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
    ):
        with pytest.raises(PermisoInsuficienteError):
            await checker(current_user=current_user, session=session)


async def test_require_permission_raises_when_user_not_found():
    current_user = {"sub": "999", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "leer")

    with patch(
        "apps.API.dependencies.auth.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(TokenInvalidoError):
            await checker(current_user=current_user, session=session)


async def test_require_permission_allows_administrar():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "administrar")
    permiso = _FakePermiso(puede_administrar=True)

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[permiso]),
        ),
    ):
        result = await checker(current_user=current_user, session=session)

    assert result["sub"] == "1"
