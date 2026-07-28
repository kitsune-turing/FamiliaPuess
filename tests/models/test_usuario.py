from apps.API.models.usuario import Usuario


def test_usuario_maps_to_expected_table():
    assert Usuario.__tablename__ == "usuario"


def test_usuario_columns_match_database_sql_schema():
    columns = {column.name for column in Usuario.__table__.columns}

    assert columns == {
        "id",
        "id_rol",
        "id_estado",
        "nombre",
        "correo",
        "username",
        "password_hash",
        "debe_cambiar_pw",
        "ultimo_login",
        "created_at",
        "updated_at",
    }


def test_usuario_username_is_unique():
    username_col = Usuario.__table__.columns["username"]

    assert username_col.unique is True
    assert username_col.nullable is False


def test_usuario_correo_is_unique():
    correo_col = Usuario.__table__.columns["correo"]

    assert correo_col.unique is True
    assert correo_col.nullable is False


def test_usuario_has_rol_and_estado_foreign_keys():
    fk_columns = {fk.parent.name for fk in Usuario.__table__.foreign_keys}

    assert "id_rol" in fk_columns
    assert "id_estado" in fk_columns
