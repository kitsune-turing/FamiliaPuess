import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import auth_service
from shared.exceptions.auth import (
    CredencialesInvalidasError,
    CuentaBloqueadaError,
    RefreshTokenInvalidoError,
    SesionNoEncontradaError,
    TokenInvalidoError,
    UsuarioInactivoError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
FIXED_NOW = datetime(2026, 7, 27, 8, 0, 0, tzinfo=timezone.utc)
VALID_HASH = "$argon2id$v=19$m=65536,t=3,p=4$mock"


@dataclass
class _FakeRol:
    id: int = 1
    codigo: str = "SUPER_ADMIN"
    nombre: str = "Super Usuario"


@dataclass
class _FakeModulo:
    codigo: str = "DASHBOARD"
    nombre: str = "Dashboard"


@dataclass
class _FakePermiso:
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


@dataclass
class _FakeUsuario:
    id: int = 10
    id_rol: int = 1
    id_estado: int = ACTIVO_ID
    nombre: str = "Admin"
    correo: str = "admin@test.com"
    username: str = "admin"
    password_hash: str = VALID_HASH
    debe_cambiar_pw: bool = False
    ultimo_login: datetime | None = None
    rol: _FakeRol = None

    def __post_init__(self):
        if self.rol is None:
            self.rol = _FakeRol()


@dataclass
class _FakeSesion:
    id: uuid.UUID = None
    id_usuario: int = 10
    token_hash: str = "hash_access"
    refresh_token_hash: str = "hash_refresh"
    activa: bool = True
    fecha_expira: datetime = None

    def __post_init__(self):
        if self.id is None:
            self.id = uuid.uuid4()
        if self.fecha_expira is None:
            self.fecha_expira = FIXED_NOW + timedelta(minutes=30)


def _base_patches(
    usuario=None,
    sesion_activa=None,
    permisos=None,
):
    if usuario is None:
        usuario = _FakeUsuario()
    if permisos is None:
        permisos = [_FakePermiso()]

    return {
        "get_by_username": patch(
            "apps.API.repositories.usuario_repository.get_by_username",
            new=AsyncMock(return_value=usuario),
        ),
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "get_active_by_user": patch(
            "apps.API.repositories.sesion_usuario_repository.get_active_by_user",
            new=AsyncMock(return_value=sesion_activa),
        ),
        "deactivate": patch(
            "apps.API.repositories.sesion_usuario_repository.deactivate",
            new=AsyncMock(),
        ),
        "create_sesion": patch(
            "apps.API.repositories.sesion_usuario_repository.create",
            new=AsyncMock(return_value=_FakeSesion()),
        ),
        "update_ultimo_login": patch(
            "apps.API.repositories.usuario_repository.update_ultimo_login",
            new=AsyncMock(),
        ),
        "get_permisos": patch(
            "apps.API.repositories.permiso_rol_repository.get_permisos_by_rol",
            new=AsyncMock(return_value=permisos),
        ),
        "create_auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "verify_password": patch(
            "apps.API.services.auth_service.verify_password",
            return_value=True,
        ),
        "now": patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


@pytest.fixture(autouse=True)
def _clear_lockout():
    auth_service._failed_attempts.clear()
    yield
    auth_service._failed_attempts.clear()


# ── login happy path ──


async def test_login_success():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_username"],
        patches["get_estado_id"],
        patches["get_active_by_user"],
        patches["create_sesion"],
        patches["update_ultimo_login"],
        patches["get_permisos"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        result = await auth_service.login(
            session,
            username="admin",
            password="secret",
            ip_address="127.0.0.1",
        )

    assert result.token_type == "bearer"
    assert result.username == "admin"
    assert result.rol_codigo == "SUPER_ADMIN"
    assert len(result.permisos) == 1
    assert result.permisos[0].modulo_codigo == "DASHBOARD"


# ── login failures ──


async def test_login_raises_on_wrong_password():
    patches = _base_patches()
    patches["verify_password"] = patch(
        "apps.API.services.auth_service.verify_password",
        return_value=False,
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_username"],
        patches["get_estado_id"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        with pytest.raises(CredencialesInvalidasError):
            await auth_service.login(
                session, username="admin", password="wrong"
            )


async def test_login_raises_on_nonexistent_user():
    patches = _base_patches(usuario=None)
    patches["get_by_username"] = patch(
        "apps.API.repositories.usuario_repository.get_by_username",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_username"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        with pytest.raises(CredencialesInvalidasError):
            await auth_service.login(
                session, username="ghost", password="any"
            )


async def test_login_raises_on_inactive_user():
    usuario = _FakeUsuario(id_estado=INACTIVO_ID)
    patches = _base_patches(usuario=usuario)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_username"],
        patches["get_estado_id"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        with pytest.raises(UsuarioInactivoError):
            await auth_service.login(
                session, username="admin", password="secret"
            )


# ── lockout ──


async def test_login_lockout_after_max_attempts():
    session = AsyncMock(spec=AsyncSession)
    patches = _base_patches()
    patches["verify_password"] = patch(
        "apps.API.services.auth_service.verify_password",
        return_value=False,
    )

    with (
        patches["get_by_username"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        for _ in range(5):
            with pytest.raises(CredencialesInvalidasError):
                await auth_service.login(
                    session, username="admin", password="wrong"
                )

        with pytest.raises(CuentaBloqueadaError):
            await auth_service.login(
                session, username="admin", password="any"
            )


# ── deactivate existing session ──


async def test_login_deactivates_existing_session():
    existing = _FakeSesion()
    patches = _base_patches(sesion_activa=existing)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_username"],
        patches["get_estado_id"],
        patches["get_active_by_user"],
        patches["deactivate"] as mock_deactivate,
        patches["create_sesion"],
        patches["update_ultimo_login"],
        patches["get_permisos"],
        patches["create_auditoria"],
        patches["verify_password"],
        patches["now"],
    ):
        await auth_service.login(
            session, username="admin", password="secret"
        )

    mock_deactivate.assert_awaited_once()


# ── logout ──


async def test_logout_success():
    sesion = _FakeSesion()
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_access_token",
            return_value={"sub": "10", "sid": str(sesion.id), "type": "access"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_token_hash",
            new=AsyncMock(return_value=sesion),
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.deactivate",
            new=AsyncMock(),
        ) as mock_deactivate,
        patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        await auth_service.logout(
            session, access_token="valid.jwt.token", ip_address="127.0.0.1"
        )

    mock_deactivate.assert_awaited_once()


async def test_logout_raises_when_session_not_found():
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_access_token",
            return_value={"sub": "10", "sid": "some-id", "type": "access"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_token_hash",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        with pytest.raises(SesionNoEncontradaError):
            await auth_service.logout(
                session, access_token="valid.jwt.token"
            )


# ── validate_token ──


async def test_validate_token_success():
    sesion = _FakeSesion()
    usuario = _FakeUsuario()
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_access_token",
            return_value={"sub": "10", "sid": str(sesion.id), "type": "access"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_token_hash",
            new=AsyncMock(return_value=sesion),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
        patch(
            "apps.API.repositories.usuario_repository.get_by_id",
            new=AsyncMock(return_value=usuario),
        ),
        patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
    ):
        payload = await auth_service.validate_token(session, "valid.jwt")

    assert payload["sub"] == "10"
    assert payload["debe_cambiar_pw"] == False
    assert payload["id_rol"] == 1


async def test_validate_token_raises_when_session_not_found():
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_access_token",
            return_value={"sub": "10", "sid": "some-id", "type": "access"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_token_hash",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        with pytest.raises(TokenInvalidoError):
            await auth_service.validate_token(session, "valid.jwt")


async def test_validate_token_raises_when_session_expired():
    sesion = _FakeSesion(fecha_expira=FIXED_NOW - timedelta(seconds=1))
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_access_token",
            return_value={"sub": "10", "sid": str(sesion.id), "type": "access"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_token_hash",
            new=AsyncMock(return_value=sesion),
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.deactivate",
            new=AsyncMock(),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        with pytest.raises(TokenInvalidoError):
            await auth_service.validate_token(session, "expired.jwt")


# ── refresh ──


async def test_refresh_success():
    sesion = _FakeSesion()
    usuario = _FakeUsuario()
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_refresh_token",
            return_value={"sub": "10", "sid": str(sesion.id), "type": "refresh"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_refresh_hash",
            new=AsyncMock(return_value=sesion),
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.update_tokens",
            new=AsyncMock(),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
        patch(
            "apps.API.repositories.usuario_repository.get_by_id",
            new=AsyncMock(return_value=usuario),
        ),
        patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
    ):
        result = await auth_service.refresh(
            session, refresh_token_value="refresh.jwt"
        )

    assert result.token_type == "bearer"
    assert result.access_token is not None
    assert result.refresh_token is not None


async def test_refresh_raises_when_session_not_found():
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_refresh_token",
            return_value={"sub": "10", "sid": "some-id", "type": "refresh"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_refresh_hash",
            new=AsyncMock(return_value=None),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        with pytest.raises(RefreshTokenInvalidoError):
            await auth_service.refresh(
                session, refresh_token_value="bad.refresh"
            )


async def test_refresh_raises_when_session_expired():
    sesion = _FakeSesion(fecha_expira=FIXED_NOW - timedelta(seconds=1))
    session = AsyncMock(spec=AsyncSession)

    with (
        patch(
            "apps.API.services.auth_service.decode_refresh_token",
            return_value={"sub": "10", "sid": str(sesion.id), "type": "refresh"},
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.get_by_refresh_hash",
            new=AsyncMock(return_value=sesion),
        ),
        patch(
            "apps.API.repositories.sesion_usuario_repository.deactivate",
            new=AsyncMock(),
        ),
        patch(
            "apps.API.services.auth_service.tz_now",
            return_value=FIXED_NOW,
        ),
    ):
        with pytest.raises(RefreshTokenInvalidoError):
            await auth_service.refresh(
                session, refresh_token_value="expired.refresh"
            )
