from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.cat_rol import CatRol


async def get_by_codigo(session: AsyncSession, codigo: str) -> CatRol | None:
    stmt = select(CatRol).where(CatRol.codigo == codigo)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
