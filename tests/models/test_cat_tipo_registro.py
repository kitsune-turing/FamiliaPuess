from apps.API.models.cat_tipo_registro import CatTipoRegistro


def test_cat_tipo_registro_maps_to_expected_table():
    assert CatTipoRegistro.__tablename__ == "cat_tipo_registro"


def test_cat_tipo_registro_columns_match_database_sql_schema():
    columns = {column.name for column in CatTipoRegistro.__table__.columns}

    assert columns == {
        "id",
        "codigo",
        "nombre",
        "descripcion",
    }


def test_cat_tipo_registro_codigo_is_unique():
    col = CatTipoRegistro.__table__.columns["codigo"]

    assert col.unique is True
    assert col.nullable is False


def test_cat_tipo_registro_descripcion_is_optional():
    assert CatTipoRegistro.__table__.columns["descripcion"].nullable is True
