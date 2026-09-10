from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.API.models.base import Base
from apps.API.models.cat_rol import CatRol


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_rol: Mapped[int] = mapped_column(ForeignKey("cat_rol.id"), nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("cat_estado.id"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    debe_cambiar_pw: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    ultimo_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    rol: Mapped[CatRol] = relationship(lazy="joined")
