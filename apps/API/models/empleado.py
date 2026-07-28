from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base
from apps.API.models.sede import Sede


class Empleado(Base):
    __tablename__ = "empleado"

    id: Mapped[int] = mapped_column(primary_key=True)
    documento: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("cat_estado.id"), nullable=False)
    id_sede: Mapped[int] = mapped_column(ForeignKey("sede.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sede: Mapped[Sede] = relationship(lazy="joined")
