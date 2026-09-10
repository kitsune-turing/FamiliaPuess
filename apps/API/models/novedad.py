from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base
from apps.API.models.cat_novedad import CatNovedad
from apps.API.models.empleado import Empleado


class Novedad(Base):
    __tablename__ = "novedad"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.id"), nullable=False)
    id_tipo_novedad: Mapped[int] = mapped_column(
        ForeignKey("cat_novedad.id"), nullable=False
    )
    id_asistencia: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("asistencia.id")
    )
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    observacion: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    empleado: Mapped[Empleado] = relationship(lazy="joined")
    tipo_novedad: Mapped[CatNovedad] = relationship(lazy="joined")

    __table_args__ = (
        Index("idx_novedad_empleado", "id_empleado", fecha.desc()),
        Index("idx_novedad_fecha", fecha.desc()),
        Index("idx_novedad_tipo", "id_tipo_novedad", fecha.desc()),
        Index("idx_novedad_dashboard", "fecha", "id_tipo_novedad"),
    )
