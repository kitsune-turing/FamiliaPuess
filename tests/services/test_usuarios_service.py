from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import usuarios_service
from shared.exceptions.roles import RolNoEncontradoError
from shared.exceptions.concurrencia import ConflictoConcurrenciaError
from shared.exceptions.usuarios import (
    CorreoDuplicadoError,
    RolInactivoError,
    UltimoSuperAdminError,
    UsernameDuplicadoError,
    UsuarioNoEncontradoError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 28, 8, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeRol:
    id: int = 1
    codigo: str = "SUPER_ADMIN"
    nombre: str = "Super Usuario"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeUsuario:
    id: int = 10
    id_rol: int = 1
    id_estado: int = ACTIVO_ID
    nombre: str = "Admin"
    correo: str = "admin@test.com"
    username: str = "admin"
    password_hash: str = "$argon2id$v=19$m=65536,t=3,p=4$mock"
    debe_cambiar_pw: bool = True
    ultimo_login: datetime | None = None
    created_at: datetime = FIXED_NOW
    updated_at: datetime = FIXED_NOW
    rol: _FakeRol | None = None

    def __post_init__(self):
        if self.rol is None:
            self.rol = _FakeRol()


def _base_patches(usuario=None, rol=None):
    if usuario is None:
        usuario = _FakeUsuario()
    if rol is None:
        rol = _FakeRol()

    return {
        "get_by_id": patch(
            "apps.API.repositories.usuario_repository.get_by_id",
            new=AsyncMock(return_value=usuario),
        ),
        "get_by_correo": patch(
            "apps.API.repositories.usuario_repository.get_by_correo",
            new=AsyncMock(return_value=None),
        ),
        "get_by_username": patch(
            "apps.API.repositories.usuario_repository.get_by_username",
            new=AsyncMock(return_value=None),
        ),
        "get_all": patch(
            "apps.API.repositories.usuario_repository.get_all",
            new=AsyncMock(return_value=[usuario]),
        ),
        "create": patch(
            "apps.API.repositories.usuario_repository.create",
            new=AsyncMock(return_value=usuario),
        ),
        "update_usuario": patch(
            "apps.API.repositories.usuario_repository.update_usuario",
            new=AsyncMock(),
        ),
        "count_super_admins": patch(
            "apps.API.repositories.usuario_repository.count_super_admins_activos",
            new=AsyncMock(return_value=2),
        ),
        "get_rol": patch(
            "apps.API.repositories.cat_rol_repository.get_by_id",
            new=AsyncMock(return_value=rol),
        ),
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(side_effect=lambda s, c: ACTIVO_ID if c == "ACTIVO" else INACTIVO_ID),
        ),
        "create_auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "hash_password": patch(
            "apps.API.services.usuarios_service.hash_password",
            return_value="hashed_pw",
        ),
        "now": patch(
            "apps.API.services.usuarios_service.tz_now",
            return_value=FIXED_NOW,
        ),
        "deactivate_all_sessions": patch(
            "apps.API.repositories.sesion_usuario_repository.deactivate_all_for_user",
            new=AsyncMock(),
        ),
    }


# ── list_usuarios ──


async def test_list_usuarios_returns_all():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with patches["get_all"] as mock_get:
        result = await usuarios_service.list_usuarios(session)

    assert len(result) == 1
    mock_get.assert_awaited_once()


# ── get_usuario ──


async def test_get_usuario_success():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_id"]:
        result = await usuarios_service.get_usuario(session, 10)

    assert result.id == 10


async def test_get_usuario_not_found():
    patches = _base_patches()
    patches["get_by_id"] = patch(
        "apps.API.repositories.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_id"]:
        with pytest.raises(UsuarioNoEncontradoError):
            await usuarios_service.get_usuario(session, 999)


# ── create_usuario ──


async def test_create_usuario_success():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_correo"],
        patches["get_by_username"],
        patches["get_rol"],
        patches["get_estado_id"],
        patches["create"],
        patches["create_auditoria"],
        patches["hash_password"],
        patches["now"],
    ):
        result = await usuarios_service.create_usuario(
            session,
            nombre="Nuevo",
            correo="nuevo@test.com",
            username="nuevo",
            password="password123",
            id_rol=1,
            user_id=1,
        )

    assert result.id == 10
    assert result.debe_cambiar_pw is True


async def test_create_usuario_duplicate_correo():
    patches = _base_patches()
    patches["get_by_correo"] = patch(
        "apps.API.repositories.usuario_repository.get_by_correo",
        new=AsyncMock(return_value=_FakeUsuario()),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_correo"]:
        with pytest.raises(CorreoDuplicadoError):
            await usuarios_service.create_usuario(
                session,
                nombre="Nuevo",
                correo="admin@test.com",
                username="nuevo",
                password="password123",
                id_rol=1,
                user_id=1,
            )


async def test_create_usuario_duplicate_username():
    patches = _base_patches()
    patches["get_by_username"] = patch(
        "apps.API.repositories.usuario_repository.get_by_username",
        new=AsyncMock(return_value=_FakeUsuario()),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_correo"],
        patches["get_by_username"],
    ):
        with pytest.raises(UsernameDuplicadoError):
            await usuarios_service.create_usuario(
                session,
                nombre="Nuevo",
                correo="nuevo@test.com",
                username="admin",
                password="password123",
                id_rol=1,
                user_id=1,
            )


async def test_create_usuario_rol_not_found():
    patches = _base_patches()
    patches["get_rol"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_correo"],
        patches["get_by_username"],
        patches["get_rol"],
    ):
        with pytest.raises(RolNoEncontradoError):
            await usuarios_service.create_usuario(
                session,
                nombre="Nuevo",
                correo="nuevo@test.com",
                username="nuevo",
                password="password123",
                id_rol=999,
                user_id=1,
            )


async def test_create_usuario_rol_inactivo():
    rol_inactivo = _FakeRol(id_estado=INACTIVO_ID)
    patches = _base_patches(rol=rol_inactivo)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_correo"],
        patches["get_by_username"],
        patches["get_rol"],
        patches["get_estado_id"],
    ):
        with pytest.raises(RolInactivoError):
            await usuarios_service.create_usuario(
                session,
                nombre="Nuevo",
                correo="nuevo@test.com",
                username="nuevo",
                password="password123",
                id_rol=1,
                user_id=1,
            )


# ── update_usuario ──


async def test_update_usuario_success():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["update_usuario"],
        patches["create_auditoria"],
        patches["now"],
    ):
        result = await usuarios_service.update_usuario(
            session, 10, nombre="Nuevo Nombre", updated_at=FIXED_NOW, user_id=1
        )

    assert result.id == 10


async def test_update_usuario_not_found():
    patches = _base_patches()
    patches["get_by_id"] = patch(
        "apps.API.repositories.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_id"]:
        with pytest.raises(UsuarioNoEncontradoError):
            await usuarios_service.update_usuario(
                session, 999, nombre="Test", updated_at=FIXED_NOW, user_id=1
            )


async def test_update_usuario_duplicate_correo():
    other = _FakeUsuario(id=20, correo="other@test.com")
    patches = _base_patches()
    patches["get_by_correo"] = patch(
        "apps.API.repositories.usuario_repository.get_by_correo",
        new=AsyncMock(return_value=other),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_by_correo"],
    ):
        with pytest.raises(CorreoDuplicadoError):
            await usuarios_service.update_usuario(
                session, 10, correo="other@test.com", updated_at=FIXED_NOW, user_id=1
            )


async def test_update_usuario_duplicate_username():
    other = _FakeUsuario(id=20, username="other")
    patches = _base_patches()
    patches["get_by_username"] = patch(
        "apps.API.repositories.usuario_repository.get_by_username",
        new=AsyncMock(return_value=other),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_by_username"],
    ):
        with pytest.raises(UsernameDuplicadoError):
            await usuarios_service.update_usuario(
                session, 10, username="other", updated_at=FIXED_NOW, user_id=1
            )


async def test_update_usuario_rol_not_found():
    patches = _base_patches()
    patches["get_rol"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_rol"],
    ):
        with pytest.raises(RolNoEncontradoError):
            await usuarios_service.update_usuario(
                session, 10, id_rol=999, updated_at=FIXED_NOW, user_id=1
            )


async def test_update_usuario_rol_inactivo():
    rol_inactivo = _FakeRol(id=5, id_estado=INACTIVO_ID)
    patches = _base_patches()
    patches["get_rol"] = patch(
        "apps.API.repositories.cat_rol_repository.get_by_id",
        new=AsyncMock(return_value=rol_inactivo),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_rol"],
        patches["get_estado_id"],
    ):
        with pytest.raises(RolInactivoError):
            await usuarios_service.update_usuario(
                session, 10, id_rol=5, updated_at=FIXED_NOW, user_id=1
            )


async def test_update_usuario_concurrency_conflict():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)
    stale_time = datetime(2026, 7, 27, 8, 0, 0, tzinfo=timezone.utc)

    with patches["get_by_id"]:
        with pytest.raises(ConflictoConcurrenciaError):
            await usuarios_service.update_usuario(
                session, 10, nombre="Test", updated_at=stale_time, user_id=1
            )


# ── deactivate_usuario ──


async def test_deactivate_usuario_success():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_estado_id"],
        patches["get_rol"],
        patches["count_super_admins"],
        patches["update_usuario"],
        patches["create_auditoria"],
        patches["now"],
    ):
        is_self = await usuarios_service.deactivate_usuario(
            session, 10, user_id=1
        )

    assert is_self is False


async def test_deactivate_usuario_not_found():
    patches = _base_patches()
    patches["get_by_id"] = patch(
        "apps.API.repositories.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_id"]:
        with pytest.raises(UsuarioNoEncontradoError):
            await usuarios_service.deactivate_usuario(
                session, 999, user_id=1
            )


async def test_deactivate_ultimo_super_admin():
    patches = _base_patches()
    patches["count_super_admins"] = patch(
        "apps.API.repositories.usuario_repository.count_super_admins_activos",
        new=AsyncMock(return_value=1),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_estado_id"],
        patches["get_rol"],
        patches["count_super_admins"],
    ):
        with pytest.raises(UltimoSuperAdminError):
            await usuarios_service.deactivate_usuario(
                session, 10, user_id=1
            )


async def test_deactivate_self_closes_sessions():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_estado_id"],
        patches["get_rol"],
        patches["count_super_admins"],
        patches["update_usuario"],
        patches["create_auditoria"],
        patches["now"],
        patches["deactivate_all_sessions"] as mock_deactivate,
    ):
        is_self = await usuarios_service.deactivate_usuario(
            session, 10, user_id=10
        )

    assert is_self is True
    mock_deactivate.assert_awaited_once()


# ── activate_usuario ──


async def test_activate_usuario_success():
    usuario = _FakeUsuario(id_estado=INACTIVO_ID)
    patches = _base_patches(usuario=usuario)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_id"],
        patches["get_estado_id"],
        patches["update_usuario"],
        patches["create_auditoria"],
        patches["now"],
    ):
        result = await usuarios_service.activate_usuario(
            session, 10, user_id=1
        )

    assert result.id == 10


async def test_activate_usuario_not_found():
    patches = _base_patches()
    patches["get_by_id"] = patch(
        "apps.API.repositories.usuario_repository.get_by_id",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_id"]:
        with pytest.raises(UsuarioNoEncontradoError):
            await usuarios_service.activate_usuario(
                session, 999, user_id=1
            )
