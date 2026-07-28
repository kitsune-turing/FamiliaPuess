from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.permiso_rol import PermisoRol


async def get_permisos_by_rol(session: AsyncSession, id_rol: int) -> list[PermisoRol]:
    stmt = select(PermisoRol).where(PermisoRol.id_rol == id_rol)
    result = await session.execute(stmt)
    return list(result.scalars().all())
