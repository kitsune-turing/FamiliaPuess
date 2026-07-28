from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.empleado import Empleado


async def get_by_documento(session: AsyncSession, documento: str) -> Empleado | None:
    stmt = select(Empleado).where(Empleado.documento == documento)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
