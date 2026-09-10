from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base
from apps.API.models.sede import Sede


class Dispositivo(Base):
    __tablename__ = "dispositivo"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sede: Mapped[int | None] = mapped_column(ForeignKey("sede.id"), nullable=True)
    identificador: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    id_estado: Mapped[int] = mapped_column(ForeignKey("cat_estado.id"), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    ultimo_ping: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sede: Mapped[Sede | None] = relationship(lazy="joined")
