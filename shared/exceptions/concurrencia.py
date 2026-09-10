class ConflictoConcurrenciaError(Exception):
    def __init__(self, recurso: str, recurso_id: int) -> None:
        self.recurso = recurso
        self.recurso_id = recurso_id
        super().__init__(
            f"El registro de {recurso} con id {recurso_id} fue modificado por otro usuario. "
            "Recargue la informacion e intente nuevamente"
        )
