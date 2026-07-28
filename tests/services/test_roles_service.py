from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import roles_service
from shared.exceptions.roles import (
    RolCodigoDuplicadoError,
    RolNoEncontradoError,
    RolProtegidoError,
    RolTieneUsuariosError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 27, 10, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeRol:
    id: int = 5
    codigo: str = "OPERADOR"
    nombre: str = "Operador"
    id_estado: int = ACTIVO_ID
    descripcion: str | None = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW


def _patches(
    rol=None,
    rol_by_codigo=None,
    user_count=0,
):
    if rol is None:
        rol = _FakeRol()

    return {
        "get_by_id": patch(
            "apps.API.repositories.cat_rol_repository.get_by_id",
            new=AsyncMock(return_value=rol),
        ),
        "get_by_codigo": patch(
            "apps.API.repositories.cat_rol_repository.get_by_codigo",
            new=AsyncMock(return_value=rol_by_codigo),
        ),
        "get_all": patch(
            "apps.API.repositories.cat_rol_repository.get_all",
            new=AsyncMock(return_value=[rol]),
        ),
        "create": patch(
            "apps.API.repositories.cat_rol_repository.create",
            new=AsyncMock(return_value=rol),
        ),
        "update_rol": patch(
            "apps.API.repositories.cat_rol_repository.update_rol",
            new=AsyncMock(),
        ),
        "deactivate": patch(
            "apps.API.repositories.cat_rol_repository.deactivate",
            new=AsyncMock(),
        ),
        "count_usuarios": patch(
            "apps.API.repositories.cat_rol_repository.count_usuarios_by_rol",
            new=AsyncMock(return_value=user_count),
        ),
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "now": patch(
            "apps.API.services.roles_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


# ── list_roles ──


async def test_list_roles_returns_all():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_all"]:
        result = await roles_service.list_roles(session)

    assert len(result) == 1


# ── get_rol ──


async def test_get_rol_returns_existing():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        result = await roles_service.get_rol(session, 5)

    assert result.codigo == "OPERADOR"


async def test_get_rol_raises_when_not_found():
    p = _patches(rol=None)
    p["get_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(RolNoEncontradoError):
            await roles_service.get_rol(session, 999)


# ── create_rol ──


async def test_create_rol_success():
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_codigo"],
        p["get_estado_id"],
        p["create"] as mock_create,
        p["auditoria"],
        p["now"],
    ):
        result = await roles_service.create_rol(
            session,
            codigo="OPERADOR",
            nombre="Operador",
            user_id=1,
        )

    assert result.codigo == "OPERADOR"
    mock_create.assert_awaited_once()


async def test_create_rol_raises_on_duplicate_codigo():
    existing = _FakeRol()
    p = _patches(rol_by_codigo=existing)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_codigo"]:
        with pytest.raises(RolCodigoDuplicadoError):
            await roles_service.create_rol(
                session,
                codigo="OPERADOR",
                nombre="Operador",
                user_id=1,
            )


# ── update_rol ──


async def test_update_rol_success():
    updated_rol = _FakeRol(nombre="Operador Actualizado")
    p = _patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["update_rol"] as mock_update,
        p["auditoria"],
        p["now"],
        patch(
            "apps.API.repositories.cat_rol_repository.get_by_id",
            new=AsyncMock(side_effect=[_FakeRol(), updated_rol]),
        ),
    ):
        result = await roles_service.update_rol(
            session,
            5,
            nombre="Operador Actualizado",
            user_id=1,
        )


async def test_update_rol_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(RolNoEncontradoError):
            await roles_service.update_rol(
                session, 999, nombre="test", user_id=1
            )


# ── deactivate_rol ──


async def test_deactivate_rol_success():
    p = _patches()
    p["get_estado_id"] = patch(
        "apps.API.repositories.cat_estado_repository.get_estado_id",
        new=AsyncMock(return_value=INACTIVO_ID),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_by_id"],
        p["count_usuarios"],
        p["get_estado_id"],
        p["deactivate"] as mock_deactivate,
        p["auditoria"],
        p["now"],
    ):
        await roles_service.deactivate_rol(session, 5, user_id=1)

    mock_deactivate.assert_awaited_once()


async def test_deactivate_rol_raises_when_not_found():
    p = _patches()
    p["get_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(RolNoEncontradoError):
            await roles_service.deactivate_rol(session, 999, user_id=1)


async def test_deactivate_rol_raises_on_protected_role():
    protected = _FakeRol(codigo="SUPER_ADMIN")
    p = _patches(rol=protected)
    p["get_by_id"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=protected),
    )
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"]:
        with pytest.raises(RolProtegidoError):
            await roles_service.deactivate_rol(session, 5, user_id=1)


async def test_deactivate_rol_raises_when_has_users():
    p = _patches(user_count=3)
    session = AsyncMock(spec=AsyncSession)

    with p["get_by_id"], p["count_usuarios"]:
        with pytest.raises(RolTieneUsuariosError):
            await roles_service.deactivate_rol(session, 5, user_id=1)
