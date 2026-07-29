class DispositivoNoEncontradoError(Exception):
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        super().__init__(f"Dispositivo '{identificador}' no esta registrado")


class DispositivoNoEncontradoPorIdError(Exception):
    def __init__(self, dispositivo_id: int) -> None:
        self.dispositivo_id = dispositivo_id
        super().__init__(f"El dispositivo con id {dispositivo_id} no existe")


class DispositivoNoAutorizadoError(Exception):
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        super().__init__(
            f"Dispositivo '{identificador}' o su sede no se encuentran activos"
        )


class IdentificadorDuplicadoError(Exception):
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        super().__init__(
            f"Ya existe un dispositivo con el identificador '{identificador}'"
        )


class IdentificadorFormatoInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "El identificador del dispositivo tiene un formato invalido. "
            "Debe contener entre 5 y 255 caracteres alfanumericos, "
            "guiones o puntos"
        )


class SedeYaTieneDispositivoError(Exception):
    def __init__(self, sede_id: int) -> None:
        self.sede_id = sede_id
        super().__init__(
            f"La sede con id {sede_id} ya tiene un dispositivo autorizado activo. "
            "Debe actualizar el dispositivo existente en lugar de crear uno nuevo"
        )
