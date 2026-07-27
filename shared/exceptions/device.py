class DispositivoNoEncontradoError(Exception):
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        super().__init__(f"Dispositivo '{identificador}' no esta registrado")


class DispositivoNoAutorizadoError(Exception):
    def __init__(self, identificador: str) -> None:
        self.identificador = identificador
        super().__init__(
            f"Dispositivo '{identificador}' o su sede no se encuentran activos"
        )
