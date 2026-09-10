from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.asistencia import Asistencia
from apps.API.models.cat_estado import CatEstado
from apps.API.models.empleado import Empleado
from apps.API.models.novedad import Novedad


async def contar_empleados_activos(session: AsyncSession) -> int:
    stmt = (
        select(func.count())
        .select_from(Empleado)
        .join(CatEstado, Empleado.id_estado == CatEstado.id)
        .where(CatEstado.codigo == "ACTIVO")
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def contar_asistencias_fecha(session: AsyncSession, fecha: date) -> int:
    stmt = (
        select(func.count())
        .select_from(Asistencia)
        .where(Asistencia.fecha_registro == fecha)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def contar_novedades_fecha(session: AsyncSession, fecha: date) -> int:
    stmt = (
        select(func.count())
        .select_from(Novedad)
        .where(Novedad.fecha == fecha)
    )
    result = await session.execute(stmt)
    return result.scalar_one()


async def contar_tardanzas_fecha(
    session: AsyncSession, fecha: date, codigo_tardanza: str = "TARDANZA"
) -> int:
    from apps.API.models.cat_novedad import CatNovedad

    stmt = (
        select(func.count())
        .select_from(Novedad)
        .join(CatNovedad, Novedad.id_tipo_novedad == CatNovedad.id)
        .where(Novedad.fecha == fecha, CatNovedad.codigo == codigo_tardanza)
    )
    result = await session.execute(stmt)
    return result.scalar_one()
