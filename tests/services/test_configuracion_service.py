from dataclasses import dataclass
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.services import configuracion_service
from shared.exceptions.configuration import SetupIncompletoError

ACTIVO_ID = 1
FIXED_NOW = datetime(2026, 7, 28, 8, 0, 0, tzinfo=timezone.utc)


@dataclass
class _FakeUsuario:
    id: int = 1
    debe_cambiar_pw: bool = False


def _base_patches(
    *,
    setup_completado: str | None = None,
    usuario: _FakeUsuario | None = None,
    sedes: int = 1,
    dispositivos: int = 1,
    empleados: int = 1,
):
    if usuario is None:
        usuario = _FakeUsuario()

    return {
        "get_estado_id": patch(
            "apps.API.repositories.cat_estado_repository.get_estado_id",
            new=AsyncMock(return_value=ACTIVO_ID),
        ),
        "get_valor_or_none": patch(
            "apps.API.repositories.config_general_repository.get_valor_or_none",
            new=AsyncMock(return_value=setup_completado),
        ),
        "get_by_id": patch(
            "apps.API.repositories.usuario_repository.get_by_id",
            new=AsyncMock(return_value=usuario),
        ),
        "count_sedes": patch(
            "apps.API.repositories.sede_repository.count_by_estado",
            new=AsyncMock(return_value=sedes),
        ),
        "count_dispositivos": patch(
            "apps.API.repositories.dispositivo_repository.count_by_estado",
            new=AsyncMock(return_value=dispositivos),
        ),
        "count_empleados": patch(
            "apps.API.repositories.empleado_repository.count_by_estado",
            new=AsyncMock(return_value=empleados),
        ),
        "upsert": patch(
            "apps.API.repositories.config_general_repository.upsert",
            new=AsyncMock(),
        ),
        "auditoria": patch(
            "apps.API.repositories.auditoria_repository.create",
            new=AsyncMock(),
        ),
        "now": patch(
            "apps.API.services.configuracion_service.tz_now",
            return_value=FIXED_NOW,
        ),
    }


async def test_get_setup_status_already_completed():
    p = _base_patches(setup_completado="true")
    session = AsyncMock(spec=AsyncSession)

    with p["get_estado_id"], p["get_valor_or_none"]:
        result = await configuracion_service.get_setup_status(session, user_id=1)

    assert result["setup_completado"] is True
    assert result["pasos"] == []


async def test_get_setup_status_all_steps_done():
    p = _base_patches(sedes=2, dispositivos=1, empleados=3)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_estado_id"],
        p["get_valor_or_none"],
        p["get_by_id"],
        p["count_sedes"],
        p["count_dispositivos"],
        p["count_empleados"],
    ):
        result = await configuracion_service.get_setup_status(session, user_id=1)

    assert result["setup_completado"] is True
    assert all(paso["completado"] for paso in result["pasos"])


async def test_get_setup_status_password_pending():
    usuario = _FakeUsuario(debe_cambiar_pw=True)
    p = _base_patches(usuario=usuario)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_estado_id"],
        p["get_valor_or_none"],
        p["get_by_id"],
        p["count_sedes"],
        p["count_dispositivos"],
        p["count_empleados"],
    ):
        result = await configuracion_service.get_setup_status(session, user_id=1)

    assert result["setup_completado"] is False
    pw_paso = next(p for p in result["pasos"] if p["clave"] == "CAMBIO_CONTRASENA")
    assert pw_paso["completado"] is False


async def test_get_setup_status_no_sedes():
    p = _base_patches(sedes=0)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_estado_id"],
        p["get_valor_or_none"],
        p["get_by_id"],
        p["count_sedes"],
        p["count_dispositivos"],
        p["count_empleados"],
    ):
        result = await configuracion_service.get_setup_status(session, user_id=1)

    assert result["setup_completado"] is False
    sede_paso = next(p for p in result["pasos"] if p["clave"] == "SEDE_REGISTRADA")
    assert sede_paso["completado"] is False


async def test_completar_setup_success():
    p = _base_patches()
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_estado_id"],
        p["get_valor_or_none"],
        p["get_by_id"],
        p["count_sedes"],
        p["count_dispositivos"],
        p["count_empleados"],
        p["upsert"] as mock_upsert,
        p["auditoria"],
        p["now"],
    ):
        await configuracion_service.completar_setup(session, user_id=1)

    mock_upsert.assert_awaited_once()


async def test_completar_setup_raises_when_incomplete():
    p = _base_patches(sedes=0, dispositivos=0)
    session = AsyncMock(spec=AsyncSession)

    with (
        p["get_estado_id"],
        p["get_valor_or_none"],
        p["get_by_id"],
        p["count_sedes"],
        p["count_dispositivos"],
        p["count_empleados"],
    ):
        with pytest.raises(SetupIncompletoError):
            await configuracion_service.completar_setup(session, user_id=1)
