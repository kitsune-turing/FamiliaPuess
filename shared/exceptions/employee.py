class EmpleadoNoRegistradoError(Exception):
    def __init__(self) -> None:
        super().__init__("El empleado no se encuentra registrado")


class EmpleadoInactivoError(Exception):
    def __init__(self) -> None:
        super().__init__("El empleado no se encuentra habilitado para registrar asistencia")
