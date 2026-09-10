"""Formato de fechas en español para la pantalla de asistencia."""

from __future__ import annotations

from datetime import datetime

# No se usa `locale` a propósito: el kiosco puede correr en equipos sin los
# locales de español instalados, y la fecha del pie es parte del diseño.
_DIAS = (
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
)

_MESES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def format_datetime_es(momento: datetime) -> str:
    """Devuelve, por ejemplo, ``Lunes, 27 de Julio del 2026 10:46 AM``."""
    dia = _DIAS[momento.weekday()]
    mes = _MESES[momento.month - 1]
    hora12 = momento.hour % 12 or 12
    meridiano = "AM" if momento.hour < 12 else "PM"
    return (
        f"{dia}, {momento.day} de {mes} del {momento.year} "
        f"{hora12:02d}:{momento.minute:02d} {meridiano}"
    )
