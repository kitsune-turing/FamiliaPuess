from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.permiso_rol import PermisoRol


async def get_permisos_by_rol(session: AsyncSession, id_rol: int) -> list[PermisoRol]:
    stmt = select(PermisoRol).where(PermisoRol.id_rol == id_rol)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(session: AsyncSession, permiso_id: int) -> PermisoRol | None:
    stmt = select(PermisoRol).where(PermisoRol.id == permiso_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_rol_and_modulo(
    session: AsyncSession, id_rol: int, id_modulo: int
) -> PermisoRol | None:
    stmt = select(PermisoRol).where(
        PermisoRol.id_rol == id_rol,
        PermisoRol.id_modulo == id_modulo,
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def create(
    session: AsyncSession,
    *,
    id_rol: int,
    id_modulo: int,
    puede_leer: bool = False,
    puede_escribir: bool = False,
    puede_eliminar: bool = False,
    puede_administrar: bool = False,
) -> PermisoRol:
    permiso = PermisoRol(
        id_rol=id_rol,
        id_modulo=id_modulo,
        puede_leer=puede_leer,
        puede_escribir=puede_escribir,
        puede_eliminar=puede_eliminar,
        puede_administrar=puede_administrar,
    )
    session.add(permiso)
    await session.flush()
    return permiso


async def update_permiso(
    session: AsyncSession,
    permiso_id: int,
    **values: bool,
) -> None:
    if not values:
        return
    stmt = update(PermisoRol).where(PermisoRol.id == permiso_id).values(**values)
    await session.execute(stmt)


async def remove(session: AsyncSession, permiso_id: int) -> None:
    stmt = delete(PermisoRol).where(PermisoRol.id == permiso_id)
    await session.execute(stmt)
