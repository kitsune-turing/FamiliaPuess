from apps.API.models.modulo import Modulo


def test_modulo_maps_to_expected_table():
    assert Modulo.__tablename__ == "modulo"


def test_modulo_columns_match_database_sql_schema():
    columns = {column.name for column in Modulo.__table__.columns}

    assert columns == {"id", "codigo", "nombre", "descripcion"}


def test_modulo_codigo_is_unique():
    codigo_col = Modulo.__table__.columns["codigo"]

    assert codigo_col.unique is True
    assert codigo_col.nullable is False
