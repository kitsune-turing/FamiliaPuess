from datetime import datetime

_DIAS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
_MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]


def format_datetime_es(moment: datetime) -> str:
    dia = _DIAS[moment.weekday()].capitalize()
    mes = _MESES[moment.month - 1].capitalize()
    return f"{dia}, {moment.day} de {mes} del {moment.year}\n{moment.strftime('%I:%M %p')}"
