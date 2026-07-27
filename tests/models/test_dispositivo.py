from apps.API.models.dispositivo import Dispositivo


def test_dispositivo_maps_to_expected_table():
    assert Dispositivo.__tablename__ == "dispositivo"


def test_dispositivo_columns_match_database_sql_schema():
    columns = {column.name for column in Dispositivo.__table__.columns}

    assert columns == {
        "id",
        "id_sede",
        "identificador",
        "id_estado",
        "descripcion",
        "ultimo_ping",
        "created_at",
        "updated_at",
    }


def test_dispositivo_identificador_is_unique():
    identificador_column = Dispositivo.__table__.columns["identificador"]

    assert identificador_column.unique is True
    assert identificador_column.nullable is False
