import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.API.models.sesion_usuario import SesionUsuario


async def create(
    session: AsyncSession,
    *,
    id_usuario: int,
    token_hash: str,
    refresh_token_hash: str,
    ip_address: str | None,
    user_agent: str | None,
    fecha_expira: datetime,
) -> SesionUsuario:
    sesion = SesionUsuario(
        id=uuid.uuid4(),
        id_usuario=id_usuario,
        token_hash=token_hash,
        refresh_token_hash=refresh_token_hash,
        ip_address=ip_address,
        user_agent=user_agent,
        fecha_expira=fecha_expira,
    )
    session.add(sesion)
    await session.flush()
    return sesion


async def get_active_by_user(session: AsyncSession, user_id: int) -> SesionUsuario | None:
    stmt = (
        select(SesionUsuario)
        .where(SesionUsuario.id_usuario == user_id, SesionUsuario.activa.is_(True))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_token_hash(session: AsyncSession, token_hash: str) -> SesionUsuario | None:
    stmt = (
        select(SesionUsuario)
        .where(SesionUsuario.token_hash == token_hash, SesionUsuario.activa.is_(True))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_refresh_hash(session: AsyncSession, refresh_hash: str) -> SesionUsuario | None:
    stmt = (
        select(SesionUsuario)
        .where(
            SesionUsuario.refresh_token_hash == refresh_hash,
            SesionUsuario.activa.is_(True),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def deactivate(session: AsyncSession, session_id: uuid.UUID, logout_time: datetime) -> None:
    stmt = (
        update(SesionUsuario)
        .where(SesionUsuario.id == session_id)
        .values(activa=False, fecha_logout=logout_time)
    )
    await session.execute(stmt)


async def deactivate_all_for_user(
    session: AsyncSession, user_id: int, logout_time: datetime
) -> None:
    stmt = (
        update(SesionUsuario)
        .where(SesionUsuario.id_usuario == user_id, SesionUsuario.activa.is_(True))
        .values(activa=False, fecha_logout=logout_time)
    )
    await session.execute(stmt)


async def update_tokens(
    session: AsyncSession,
    session_id: uuid.UUID,
    *,
    token_hash: str,
    refresh_token_hash: str,
    fecha_expira: datetime,
) -> None:
    stmt = (
        update(SesionUsuario)
        .where(SesionUsuario.id == session_id)
        .values(
            token_hash=token_hash,
            refresh_token_hash=refresh_token_hash,
            fecha_expira=fecha_expira,
        )
    )
    await session.execute(stmt)
