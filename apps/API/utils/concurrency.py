from datetime import datetime

from shared.exceptions.concurrencia import ConflictoConcurrenciaError


def check_concurrency(
    entity_updated_at: datetime,
    expected_updated_at: datetime,
    resource_name: str,
    entity_id: int,
) -> None:
    if entity_updated_at != expected_updated_at:
        raise ConflictoConcurrenciaError(resource_name, entity_id)
