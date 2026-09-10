from datetime import date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.asistencia import Asistencia


async def create(
    session: AsyncSession,
    *,
    id_empleado: int,
    id_token_qr: int,
    id_tipo_registro: int,
    id_sede: int,
    fecha_registro: date,
    registrado_en: datetime,
) -> Asistencia:
    asistencia = Asistencia(
        id_empleado=id_empleado,
        id_token_qr=id_token_qr,
        id_tipo_registro=id_tipo_registro,
        id_sede=id_sede,
        fecha_registro=fecha_registro,
        registrado_en=registrado_en,
    )
    session.add(asistencia)
    await session.flush()
    return asistencia


async def get_duplicado(
    session: AsyncSession,
    *,
    id_empleado: int,
    fecha: date,
    id_tipo_registro: int,
) -> Asistencia | None:
    stmt = (
        select(Asistencia)
        .where(
            Asistencia.id_empleado == id_empleado,
            Asistencia.fecha_registro == fecha,
            Asistencia.id_tipo_registro == id_tipo_registro,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
