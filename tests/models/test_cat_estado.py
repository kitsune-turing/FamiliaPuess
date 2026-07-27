from apps.API.models.cat_estado import CatEstado


def test_cat_estado_maps_to_expected_table():
    assert CatEstado.__tablename__ == "cat_estado"


def test_cat_estado_columns_match_database_sql_schema():
    columns = {column.name for column in CatEstado.__table__.columns}

    assert columns == {
        "id",
        "codigo",
        "nombre",
        "descripcion",
        "created_at",
        "updated_at",
    }


def test_cat_estado_codigo_is_unique():
    codigo_column = CatEstado.__table__.columns["codigo"]

    assert codigo_column.unique is True
    assert codigo_column.nullable is False
