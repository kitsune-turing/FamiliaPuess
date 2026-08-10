from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.API.models.usuario import Usuario
from shared.utils.sql import escape_like


async def get_by_username(session: AsyncSession, username: str) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_correo(session: AsyncSession, correo: str) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.correo == correo)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all(
    session: AsyncSession,
    *,
    nombre: str | None = None,
    username: str | None = None,
    id_rol: int | None = None,
    id_estado: int | None = None,
) -> Sequence[Usuario]:
    stmt = select(Usuario).options(joinedload(Usuario.rol)).order_by(Usuario.nombre)
    if nombre is not None:
        safe = escape_like(nombre)
        stmt = stmt.where(Usuario.nombre.ilike(f"%{safe}%", escape="\\"))
    if username is not None:
        safe = escape_like(username)
        stmt = stmt.where(Usuario.username.ilike(f"%{safe}%", escape="\\"))
    if id_rol is not None:
        stmt = stmt.where(Usuario.id_rol == id_rol)
    if id_estado is not None:
        stmt = stmt.where(Usuario.id_estado == id_estado)
    result = await session.execute(stmt)
    return result.scalars().unique().all()


async def create(
    session: AsyncSession,
    *,
    nombre: str,
    correo: str,
    username: str,
    password_hash: str,
    id_rol: int,
    id_estado: int,
    now: datetime | None = None,
) -> Usuario:
    usuario = Usuario(
        nombre=nombre,
        correo=correo,
        username=username,
        password_hash=password_hash,
        id_rol=id_rol,
        id_estado=id_estado,
        debe_cambiar_pw=True,
    )
    if now is not None:
        usuario.created_at = now
        usuario.updated_at = now
    session.add(usuario)
    await session.flush()
    await session.refresh(usuario, attribute_names=["rol"])
    return usuario


async def update_usuario(
    session: AsyncSession,
    user_id: int,
    *,
    nombre: str | None = None,
    correo: str | None = None,
    username: str | None = None,
    id_rol: int | None = None,
    id_estado: int | None = None,
    now: datetime | None = None,
) -> None:
    values: dict = {}
    if nombre is not None:
        values["nombre"] = nombre
    if correo is not None:
        values["correo"] = correo
    if username is not None:
        values["username"] = username
    if id_rol is not None:
        values["id_rol"] = id_rol
    if id_estado is not None:
        values["id_estado"] = id_estado
    if now is not None:
        values["updated_at"] = now
    if not values:
        return
    stmt = update(Usuario).where(Usuario.id == user_id).values(**values)
    await session.execute(stmt)


async def update_ultimo_login(
    session: AsyncSession, user_id: int, timestamp: datetime
) -> None:
    stmt = (
        update(Usuario)
        .where(Usuario.id == user_id)
        .values(ultimo_login=timestamp)
    )
    await session.execute(stmt)


async def update_password(
    session: AsyncSession, user_id: int, new_hash: str, timestamp: datetime
) -> None:
    stmt = (
        update(Usuario)
        .where(Usuario.id == user_id)
        .values(password_hash=new_hash, debe_cambiar_pw=False, updated_at=timestamp)
    )
    await session.execute(stmt)


async def count_super_admins_activos(
    session: AsyncSession, id_estado_activo: int, id_rol_super_admin: int
) -> int:
    stmt = (
        select(func.count())
        .select_from(Usuario)
        .where(
            Usuario.id_estado == id_estado_activo,
            Usuario.id_rol == id_rol_super_admin,
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one()
