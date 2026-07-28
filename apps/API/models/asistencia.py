from datetime import date, datetime

from sqlalchemy import BigInteger, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime

from apps.API.models.base import Base
from apps.API.models.empleado import Empleado
from apps.API.models.sede import Sede


class Asistencia(Base):
    __tablename__ = "asistencia"
    __table_args__ = (
        UniqueConstraint(
            "id_empleado", "fecha_registro", "id_tipo_registro",
            name="uq_asistencia_empleado_fecha_tipo",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.id"), nullable=False)
    id_token_qr: Mapped[int] = mapped_column(ForeignKey("token_qr.id"), nullable=False)
    id_tipo_registro: Mapped[int] = mapped_column(
        ForeignKey("cat_tipo_registro.id"), nullable=False
    )
    id_sede: Mapped[int] = mapped_column(ForeignKey("sede.id"), nullable=False)
    fecha_registro: Mapped[date] = mapped_column(Date, nullable=False)
    registrado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    empleado: Mapped[Empleado] = relationship(lazy="joined")
    sede: Mapped[Sede] = relationship(lazy="joined")
