from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.usuario import Usuario


async def get_by_username(session: AsyncSession, username: str) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_id(session: AsyncSession, user_id: int) -> Usuario | None:
    stmt = select(Usuario).where(Usuario.id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


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
