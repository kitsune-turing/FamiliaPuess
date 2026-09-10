class SedeNoEncontradaError(Exception):
    def __init__(self, sede_id: int) -> None:
        self.sede_id = sede_id
        super().__init__(f"La sede con id {sede_id} no existe")


class SedeNombreDuplicadoError(Exception):
    def __init__(self, nombre: str) -> None:
        self.nombre = nombre
        super().__init__(
            f"Ya existe una sede con el nombre '{nombre}'"
        )


class SedeInactivaError(Exception):
    def __init__(self, sede_id: int) -> None:
        self.sede_id = sede_id
        super().__init__(f"La sede con id {sede_id} se encuentra inactiva")


class SedeDireccionInvalidaError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "La direccion contiene caracteres no permitidos. "
            "Solo se permiten letras, numeros, espacios, puntos, comas, "
            "numerales, guiones y barras"
        )


class SedeNombreInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "El nombre de la sede contiene caracteres no permitidos. "
            "Solo se permiten letras, numeros, espacios, tildes y guiones"
        )
