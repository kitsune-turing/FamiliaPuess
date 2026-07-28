from apps.API.models.permiso_rol import PermisoRol


def test_permiso_rol_maps_to_expected_table():
    assert PermisoRol.__tablename__ == "permiso_rol"


def test_permiso_rol_columns_match_database_sql_schema():
    columns = {column.name for column in PermisoRol.__table__.columns}

    assert columns == {
        "id",
        "id_rol",
        "id_modulo",
        "puede_leer",
        "puede_escribir",
        "puede_eliminar",
        "puede_administrar",
    }


def test_permiso_rol_has_cascade_foreign_keys():
    fk_columns = {fk.parent.name for fk in PermisoRol.__table__.foreign_keys}

    assert "id_rol" in fk_columns
    assert "id_modulo" in fk_columns
