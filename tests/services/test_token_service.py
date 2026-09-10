from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import token_service
from shared.exceptions.device import DispositivoNoAutorizadoError, DispositivoNoEncontradoError

ACTIVO_ID = 1
INACTIVO_ID = 2
ESTADO_TOKEN_ACTIVO_ID = 10
FIXED_NOW = datetime(2026, 1, 1, 8, 0, 0, tzinfo=timezone.utc)

CONFIG_VALUES = {
    "QR_EXPIRACION_SEG": "30",
    "CODIGO_LONGITUD": "6",
    "CODIGO_FORMATO": "ALFANUMERICO",
}


@dataclass
class _FakeSede:
    id_estado: int


@dataclass
class _FakeDispositivo:
    id: int
    id_sede: int
    id_estado: int
    sede: _FakeSede


def _dispositivo_activo() -> _FakeDispositivo:
    return _FakeDispositivo(id=7, id_sede=3, id_estado=ACTIVO_ID, sede=_FakeSede(id_estado=ACTIVO_ID))


async def _config_side_effect(session, clave: str) -> str:
    return CONFIG_VALUES[clave]


def _patched_repositories(dispositivo):
    return (
        patch(
            "apps.API.repositories.dispositivo_repository.get_by_identificador",
            new=AsyncMock(return_value=dispositivo),
        ),
        patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        patch(
            "apps.API.repositories.cat_estado_token_repository.get_estado_token_id",
            new=AsyncMock(return_value=ESTADO_TOKEN_ACTIVO_ID),
        ),
        patch(
            "apps.API.repositories.config_general_repository.get_valor",
            new=AsyncMock(side_effect=_config_side_effect),
        ),
        patch("apps.API.repositories.token_qr_repository.create", new=AsyncMock()),
        patch("apps.API.core.timezone.now", return_value=FIXED_NOW),
    )


async def test_generate_token_happy_path():
    dispositivo = _dispositivo_activo()
    session = AsyncMock(spec=AsyncSession)

    patches = _patched_repositories(dispositivo)
    with patches[0], patches[1], patches[2], patches[3] as mock_get_valor, patches[
        4
    ] as mock_create, patches[5]:
        resultado = await token_service.generate_token(session, "KIOSK-001")

    assert resultado.generado_en == FIXED_NOW
    assert resultado.expira_en == FIXED_NOW + timedelta(seconds=30)
    assert len(resultado.codigo_alfa) == 6
    assert len(resultado.token) > 0
    mock_get_valor.assert_awaited()
    mock_create.assert_awaited_once_with(
        session,
        id_sede=dispositivo.id_sede,
        id_dispositivo=dispositivo.id,
        id_estado_token=ESTADO_TOKEN_ACTIVO_ID,
        token=resultado.token,
        codigo_alfa=resultado.codigo_alfa,
        generado_en=FIXED_NOW,
        expira_en=FIXED_NOW + timedelta(seconds=30),
    )


async def test_generate_token_raises_when_dispositivo_not_found():
    session = AsyncMock(spec=AsyncSession)
    patches = _patched_repositories(None)

    with patches[0], patches[1], patches[2], patches[3], patches[4] as mock_create, patches[5]:
        with pytest.raises(DispositivoNoEncontradoError):
            await token_service.generate_token(session, "NO-EXISTE")

    mock_create.assert_not_awaited()


async def test_generate_token_raises_when_dispositivo_inactivo():
    dispositivo = _FakeDispositivo(
        id=7, id_sede=3, id_estado=INACTIVO_ID, sede=_FakeSede(id_estado=ACTIVO_ID)
    )
    session = AsyncMock(spec=AsyncSession)
    patches = _patched_repositories(dispositivo)

    with patches[0], patches[1], patches[2], patches[3], patches[4] as mock_create, patches[5]:
        with pytest.raises(DispositivoNoAutorizadoError):
            await token_service.generate_token(session, "KIOSK-001")

    mock_create.assert_not_awaited()


async def test_generate_token_raises_when_sede_inactiva():
    dispositivo = _FakeDispositivo(
        id=7, id_sede=3, id_estado=ACTIVO_ID, sede=_FakeSede(id_estado=INACTIVO_ID)
    )
    session = AsyncMock(spec=AsyncSession)
    patches = _patched_repositories(dispositivo)

    with patches[0], patches[1], patches[2], patches[3], patches[4] as mock_create, patches[5]:
        with pytest.raises(DispositivoNoAutorizadoError):
            await token_service.generate_token(session, "KIOSK-001")

    mock_create.assert_not_awaited()


async def test_generate_token_never_repeats_the_previous_token():
    dispositivo = _dispositivo_activo()
    session = AsyncMock(spec=AsyncSession)
    patches = _patched_repositories(dispositivo)

    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5]:
        primero = await token_service.generate_token(session, "KIOSK-001")
        segundo = await token_service.generate_token(session, "KIOSK-001")

    assert primero.token != segundo.token
    assert primero.codigo_alfa != segundo.codigo_alfa
