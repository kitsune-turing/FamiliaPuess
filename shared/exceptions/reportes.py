class ReporteNoEncontradoError(Exception):
    def __init__(self, reporte_id: int) -> None:
        self.reporte_id = reporte_id
        super().__init__(f"El reporte con id {reporte_id} no existe")


class RangoFechasInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "El rango de fechas es invalido: la fecha inicial no puede ser posterior a la final"
        )


class ReporteDuplicadoError(Exception):
    def __init__(self, fecha_inicio: str, fecha_fin: str) -> None:
        super().__init__(
            f"Ya existe un reporte semanal para el periodo {fecha_inicio} - {fecha_fin}"
        )


class ReporteGeneracionError(Exception):
    def __init__(self, detalle: str = "") -> None:
        msg = "Error durante la generacion del reporte semanal"
        if detalle:
            msg = f"{msg}: {detalle}"
        super().__init__(msg)


class ReporteSinDatosError(Exception):
    def __init__(self) -> None:
        super().__init__("No existen registros que cumplan los filtros aplicados")
