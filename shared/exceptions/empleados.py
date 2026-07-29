class EmpleadoNoEncontradoError(Exception):
    def __init__(self, empleado_id: int) -> None:
        self.empleado_id = empleado_id
        super().__init__(f"El empleado con id {empleado_id} no existe")


class DocumentoDuplicadoError(Exception):
    def __init__(self, documento: str) -> None:
        self.documento = documento
        super().__init__(
            f"Ya existe un empleado con el documento '{documento}'"
        )


class DocumentoFormatoInvalidoError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "El documento de identidad tiene un formato invalido. "
            "Debe contener entre 6 y 20 caracteres numericos"
        )


class NombreInvalidoError(Exception):
    def __init__(self, campo: str) -> None:
        self.campo = campo
        super().__init__(
            f"El campo '{campo}' contiene caracteres no permitidos. "
            "Solo se permiten letras, espacios, tildes y guiones"
        )


class SedeNoEncontradaError(Exception):
    def __init__(self, sede_id: int) -> None:
        self.sede_id = sede_id
        super().__init__(f"La sede con id {sede_id} no existe")


class SedeInactivaError(Exception):
    def __init__(self, sede_id: int) -> None:
        self.sede_id = sede_id
        super().__init__(f"La sede con id {sede_id} se encuentra inactiva")
