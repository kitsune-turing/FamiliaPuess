from apps.API.models.cat_rol import CatRol


def test_cat_rol_maps_to_expected_table():
    assert CatRol.__tablename__ == "cat_rol"


def test_cat_rol_columns_match_database_sql_schema():
    columns = {column.name for column in CatRol.__table__.columns}

    assert columns == {
        "id",
        "codigo",
        "nombre",
        "id_estado",
        "descripcion",
        "created_at",
        "updated_at",
    }


def test_cat_rol_codigo_is_unique():
    codigo_column = CatRol.__table__.columns["codigo"]

    assert codigo_column.unique is True
    assert codigo_column.nullable is False


def test_cat_rol_has_estado_foreign_key():
    fk_columns = {
        fk.parent.name for fk in CatRol.__table__.foreign_keys
    }
    assert "id_estado" in fk_columns
