from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import registro_service
from shared.exceptions.attendance import AsistenciaDuplicadaError
from shared.exceptions.employee import EmpleadoInactivoError, EmpleadoNoRegistradoError
from shared.exceptions.registration import (
    CodigoAlfaInvalidoError,
    DispositivoTokenNoAutorizadoError,
    SedeNoDisponibleError,
    TokenConsumidoError,
    TokenExpiradoError,
    TokenFormatoInvalidoError,
    TokenNoEncontradoError,
)

ACTIVO_ID = 1
INACTIVO_ID = 2
CONSUMIDO_ID = 10
ACTIVO_TOKEN_ID = 11
TIPO_ENTRADA_ID = 5
FIXED_NOW = datetime(2026, 7, 22, 8, 0, 0, tzinfo=timezone.utc)
VALID_TOKEN = "a" * 20


@dataclass
class _FakeSede:
    id: int = 3
    nombre: str = "Sede Central"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeDispositivo:
    id: int = 7
    id_sede: int = 3
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeTokenQR:
    id: int = 100
    token: str = VALID_TOKEN
    codigo_alfa: str = "A1B2C3"
    id_sede: int = 3
    id_estado_token: int = ACTIVO_TOKEN_ID
    expira_en: datetime = FIXED_NOW + timedelta(minutes=5)
    sede: _FakeSede = None
    dispositivo: _FakeDispositivo = None

    def __post_init__(self):
        if self.sede is None:
            self.sede = _FakeSede()
        if self.dispositivo is None:
            self.dispositivo = _FakeDispositivo()


@dataclass
class _FakeEmpleado:
    id: int = 25
    documento: str = "123456"
    nombre: str = "Juan"
    apellido: str = "Perez"
    id_estado: int = ACTIVO_ID


@dataclass
class _FakeAsistencia:
    registrado_en: datetime = FIXED_NOW
    sede: _FakeSede = None

    def __post_init__(self):
        if self.sede is None:
            self.sede = _FakeSede()


def _base_patches(
    token_qr=None,
    empleado=None,
    duplicado=None,
):
    if token_qr is None:
        token_qr = _FakeTokenQR()

    return {
        "get_by_token": patch(
            "apps.API.repositories.token_qr_repository.get_by_token",
            new=AsyncMock(return_value=token_qr),
        ),
        "get_estado_token_id": patch(
            "apps.API.repositories.cat_estado_token_repository.get_estado_token_id",
            new=AsyncMock(side_effect=[CONSUMIDO_ID, ACTIVO_TOKEN_ID]),
        ),
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "now": patch(
            "apps.API.core.timezone.now",
            return_value=FIXED_NOW,
        ),
        "get_by_documento": patch(
            "apps.API.repositories.empleado_repository.get_by_documento",
            new=AsyncMock(return_value=empleado),
        ),
        "get_tipo_registro_id": patch(
            "apps.API.repositories.cat_tipo_registro_repository.get_tipo_registro_id",
            new=AsyncMock(return_value=TIPO_ENTRADA_ID),
        ),
        "get_duplicado": patch(
            "apps.API.repositories.asistencia_repository.get_duplicado",
            new=AsyncMock(return_value=duplicado),
        ),
        "create_asistencia": patch(
            "apps.API.repositories.asistencia_repository.create",
            new=AsyncMock(),
        ),
        "try_consume_atomically": patch(
            "apps.API.repositories.token_qr_repository.try_consume_atomically",
            new=AsyncMock(return_value=True),
        ),
    }


# ── validar_token ──


async def test_validar_token_happy_path():
    patches = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"], patches[
        "get_estado_id"
    ]:
        result = await registro_service.validar_token(session, VALID_TOKEN)

    assert result.token == VALID_TOKEN
    assert result.sede_nombre == "Sede Central"


async def test_validar_token_raises_on_short_token():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(TokenFormatoInvalidoError):
        await registro_service.validar_token(session, "short")


async def test_validar_token_raises_on_empty_token():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(TokenFormatoInvalidoError):
        await registro_service.validar_token(session, "")


async def test_validar_token_raises_when_not_found():
    patches = _base_patches(token_qr=None)
    patches["get_by_token"] = patch(
        "apps.API.repositories.token_qr_repository.get_by_token",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"]:
        with pytest.raises(TokenNoEncontradoError):
            await registro_service.validar_token(session, VALID_TOKEN)


async def test_validar_token_raises_when_consumed():
    token_qr = _FakeTokenQR(id_estado_token=CONSUMIDO_ID)
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"]:
        with pytest.raises(TokenConsumidoError):
            await registro_service.validar_token(session, VALID_TOKEN)


async def test_validar_token_raises_when_expired():
    token_qr = _FakeTokenQR(expira_en=FIXED_NOW - timedelta(seconds=1))
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"], patches[
        "get_estado_id"
    ]:
        with pytest.raises(TokenExpiradoError):
            await registro_service.validar_token(session, VALID_TOKEN)


async def test_validar_token_raises_when_sede_inactive():
    token_qr = _FakeTokenQR(sede=_FakeSede(id_estado=INACTIVO_ID))
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"], patches[
        "get_estado_id"
    ]:
        with pytest.raises(SedeNoDisponibleError):
            await registro_service.validar_token(session, VALID_TOKEN)


# ── registrar_asistencia ──


async def test_registrar_asistencia_happy_path():
    empleado = _FakeEmpleado()
    patches = _base_patches(empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
        patches["get_tipo_registro_id"],
        patches["get_duplicado"],
        patches["create_asistencia"] as mock_create,
        patches["try_consume_atomically"] as mock_consume,
    ):
        result = await registro_service.registrar_asistencia(
            session,
            token_value=VALID_TOKEN,
            documento="123456",
            codigo_alfa="A1B2C3",
        )

    assert result.empleado_nombre == "Juan Perez"
    assert result.sede_nombre == "Sede Central"
    assert result.registrado_en == FIXED_NOW
    mock_create.assert_awaited_once()
    mock_consume.assert_awaited_once()


async def test_registrar_raises_on_short_token():
    session = AsyncMock(spec=AsyncSession)

    with pytest.raises(TokenFormatoInvalidoError):
        await registro_service.registrar_asistencia(
            session, token_value="short", documento="123", codigo_alfa="ABC"
        )


async def test_registrar_raises_when_token_not_found():
    patches = _base_patches()
    patches["get_by_token"] = patch(
        "apps.API.repositories.token_qr_repository.get_by_token",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"]:
        with pytest.raises(TokenNoEncontradoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123", codigo_alfa="ABC"
            )


async def test_registrar_raises_when_token_consumed():
    token_qr = _FakeTokenQR(id_estado_token=CONSUMIDO_ID)
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"]:
        with pytest.raises(TokenConsumidoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123", codigo_alfa="ABC"
            )


async def test_registrar_raises_when_token_expired():
    token_qr = _FakeTokenQR(expira_en=FIXED_NOW - timedelta(seconds=1))
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"], patches[
        "get_estado_id"
    ]:
        with pytest.raises(TokenExpiradoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123", codigo_alfa="ABC"
            )


async def test_registrar_raises_when_sede_inactive():
    token_qr = _FakeTokenQR(sede=_FakeSede(id_estado=INACTIVO_ID))
    patches = _base_patches(token_qr=token_qr)
    session = AsyncMock(spec=AsyncSession)

    with patches["get_by_token"], patches["get_estado_token_id"], patches["now"], patches[
        "get_estado_id"
    ]:
        with pytest.raises(SedeNoDisponibleError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123", codigo_alfa="ABC"
            )


async def test_registrar_raises_when_empleado_not_found():
    patches = _base_patches(empleado=None)
    patches["get_by_documento"] = patch(
        "apps.API.repositories.empleado_repository.get_by_documento",
        new=AsyncMock(return_value=None),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
    ):
        with pytest.raises(EmpleadoNoRegistradoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="000000", codigo_alfa="A1B2C3"
            )


async def test_registrar_raises_when_empleado_inactive():
    empleado = _FakeEmpleado(id_estado=INACTIVO_ID)
    patches = _base_patches(empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
    ):
        with pytest.raises(EmpleadoInactivoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
            )


async def test_registrar_raises_when_codigo_alfa_invalid():
    empleado = _FakeEmpleado()
    patches = _base_patches(empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
    ):
        with pytest.raises(CodigoAlfaInvalidoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="WRONG"
            )


async def test_registrar_raises_when_dispositivo_inactive():
    token_qr = _FakeTokenQR(dispositivo=_FakeDispositivo(id_estado=INACTIVO_ID))
    empleado = _FakeEmpleado()
    patches = _base_patches(token_qr=token_qr, empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
    ):
        with pytest.raises(DispositivoTokenNoAutorizadoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
            )


async def test_registrar_raises_when_dispositivo_sede_mismatch():
    token_qr = _FakeTokenQR(dispositivo=_FakeDispositivo(id_sede=999))
    empleado = _FakeEmpleado()
    patches = _base_patches(token_qr=token_qr, empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
    ):
        with pytest.raises(DispositivoTokenNoAutorizadoError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
            )


async def test_registrar_raises_when_duplicate_attendance_found():
    empleado = _FakeEmpleado()
    existing = _FakeAsistencia()
    patches = _base_patches(empleado=empleado, duplicado=existing)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
        patches["get_tipo_registro_id"],
        patches["get_duplicado"],
        patches["create_asistencia"] as mock_create,
        patches["try_consume_atomically"],
    ):
        with pytest.raises(AsistenciaDuplicadaError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
            )

    mock_create.assert_not_awaited()


async def test_registrar_raises_on_integrity_error_safety_net():
    empleado = _FakeEmpleado()
    patches = _base_patches(empleado=empleado)
    patches["create_asistencia"] = patch(
        "apps.API.repositories.asistencia_repository.create",
        new=AsyncMock(side_effect=IntegrityError("dup", {}, None)),
    )
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
        patches["get_tipo_registro_id"],
        patches["get_duplicado"],
        patches["create_asistencia"],
        patches["try_consume_atomically"],
    ):
        with pytest.raises(AsistenciaDuplicadaError):
            await registro_service.registrar_asistencia(
                session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
            )


async def test_registrar_consumes_token_atomically_before_insert():
    empleado = _FakeEmpleado()
    patches = _base_patches(empleado=empleado)
    session = AsyncMock(spec=AsyncSession)

    with (
        patches["get_by_token"],
        patches["get_estado_token_id"],
        patches["now"],
        patches["get_estado_id"],
        patches["get_by_documento"],
        patches["get_tipo_registro_id"],
        patches["get_duplicado"],
        patches["create_asistencia"],
        patches["try_consume_atomically"] as mock_consume,
    ):
        await registro_service.registrar_asistencia(
            session, token_value=VALID_TOKEN, documento="123456", codigo_alfa="A1B2C3"
        )

    mock_consume.assert_awaited_once()
    call_kwargs = mock_consume.call_args.kwargs
    assert call_kwargs["token_id"] == 100
    assert call_kwargs["id_estado_consumido"] == CONSUMIDO_ID
