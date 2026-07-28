from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.empleado import Empleado


async def get_by_documento(session: AsyncSession, documento: str) -> Empleado | None:
    stmt = select(Empleado).where(Empleado.documento == documento)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def count_by_estado(session: AsyncSession, id_estado: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Empleado)
        .where(Empleado.id_estado == id_estado)
    )
    result = await session.execute(stmt)
    return result.scalar_one()
