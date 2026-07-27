from apps.API.models.config_general import ConfigGeneral


def test_config_general_maps_to_expected_table():
    assert ConfigGeneral.__tablename__ == "config_general"


def test_config_general_columns_match_database_sql_schema():
    columns = {column.name for column in ConfigGeneral.__table__.columns}

    assert columns == {
        "id",
        "categoria",
        "clave",
        "valor",
        "tipo_dato",
        "descripcion",
        "updated_at",
        "updated_by",
    }


def test_config_general_clave_is_unique():
    clave_column = ConfigGeneral.__table__.columns["clave"]

    assert clave_column.unique is True
