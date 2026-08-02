from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

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


def _fake_request(ip: str = "192.168.1.1"):
    request = MagicMock()
    request.client.host = ip
    return request


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
        result = await checker(
            request=_fake_request(),
            current_user=current_user,
            session=session,
        )

    assert result["sub"] == "1"


async def test_require_permission_denies_unauthorized_user():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "escribir")
    audit_mock = AsyncMock()

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
        patch(
            "apps.API.dependencies.auth.auditoria_repository.create",
            new=audit_mock,
        ),
    ):
        with pytest.raises(PermisoInsuficienteError):
            await checker(
                request=_fake_request(),
                current_user=current_user,
                session=session,
            )


async def test_require_permission_denies_wrong_module():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("USUARIOS", "leer")
    audit_mock = AsyncMock()

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
        patch(
            "apps.API.dependencies.auth.auditoria_repository.create",
            new=audit_mock,
        ),
    ):
        with pytest.raises(PermisoInsuficienteError):
            await checker(
                request=_fake_request(),
                current_user=current_user,
                session=session,
            )


async def test_require_permission_raises_when_user_not_found():
    current_user = {"sub": "999", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("DASHBOARD", "leer")

    with patch(
        "apps.API.dependencies.auth.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    ):
        with pytest.raises(TokenInvalidoError):
            await checker(
                request=_fake_request(),
                current_user=current_user,
                session=session,
            )


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
        result = await checker(
            request=_fake_request(),
            current_user=current_user,
            session=session,
        )

    assert result["sub"] == "1"


async def test_require_permission_logs_unauthorized_access():
    current_user = {"sub": "1", "type": "access"}
    session = AsyncMock(spec=AsyncSession)
    checker = require_permission("USUARIOS", "eliminar")
    audit_mock = AsyncMock()

    with (
        patch(
            "apps.API.dependencies.auth.usuario_repository.get_by_id",
            new=AsyncMock(return_value=_FakeUsuario()),
        ),
        patch(
            "apps.API.dependencies.auth.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=[_FakePermiso()]),
        ),
        patch(
            "apps.API.dependencies.auth.auditoria_repository.create",
            new=audit_mock,
        ),
    ):
        with pytest.raises(PermisoInsuficienteError):
            await checker(
                request=_fake_request("10.0.0.5"),
                current_user=current_user,
                session=session,
            )

    audit_mock.assert_awaited_once()
    call_kwargs = audit_mock.call_args[1]
    assert call_kwargs["id_usuario"] == 1
    assert call_kwargs["recurso"] == "SEGURIDAD"
    assert call_kwargs["operacion"] == "ACCESO_NO_AUTORIZADO"
    assert call_kwargs["ip_address"] == "10.0.0.5"
    assert "USUARIOS/eliminar" in call_kwargs["detalle"]
