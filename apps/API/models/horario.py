from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base
from apps.API.models.sede import Sede


class Horario(Base):
    __tablename__ = "horario"

    id: Mapped[int] = mapped_column(primary_key=True)
    id_sede: Mapped[int] = mapped_column(ForeignKey("sede.id"), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(100))
    hora_entrada: Mapped[time] = mapped_column(Time, nullable=False)
    hora_salida: Mapped[time | None] = mapped_column(Time)
    tolerancia_min: Mapped[int] = mapped_column(nullable=False, default=15)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigente_hasta: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    sede: Mapped[Sede] = relationship(lazy="joined")

    __table_args__ = (
        CheckConstraint(
            "tolerancia_min >= 0 AND tolerancia_min <= 120",
            name="ck_horario_tolerancia",
        ),
        CheckConstraint(
            "vigente_hasta IS NULL OR vigente_hasta >= vigente_desde",
            name="ck_horario_vigencia",
        ),
        Index("idx_horario_sede_vigente", "id_sede", "vigente_desde", "vigente_hasta"),
    )
