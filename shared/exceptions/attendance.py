from datetime import datetime


class AsistenciaDuplicadaError(Exception):
    def __init__(self, hora_anterior: datetime, sede_anterior: str) -> None:
        self.hora_anterior = hora_anterior
        self.sede_anterior = sede_anterior
        super().__init__(
            f"Ya registro su entrada el dia de hoy a las "
            f"{hora_anterior.strftime('%I:%M %p')} en {sede_anterior}"
        )
