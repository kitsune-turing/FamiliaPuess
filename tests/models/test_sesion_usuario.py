from apps.API.models.sesion_usuario import SesionUsuario


def test_sesion_usuario_maps_to_expected_table():
    assert SesionUsuario.__tablename__ == "sesion_usuario"


def test_sesion_usuario_columns_match_database_sql_schema():
    columns = {column.name for column in SesionUsuario.__table__.columns}

    assert columns == {
        "id",
        "id_usuario",
        "token_hash",
        "refresh_token_hash",
        "ip_address",
        "user_agent",
        "activa",
        "fecha_login",
        "fecha_expira",
        "fecha_logout",
    }


def test_sesion_usuario_has_usuario_foreign_key():
    fk_columns = {fk.parent.name for fk in SesionUsuario.__table__.foreign_keys}

    assert "id_usuario" in fk_columns
