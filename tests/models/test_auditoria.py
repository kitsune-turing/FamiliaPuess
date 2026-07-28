from apps.API.models.auditoria import Auditoria


def test_auditoria_maps_to_expected_table():
    assert Auditoria.__tablename__ == "auditoria"


def test_auditoria_columns_match_database_sql_schema():
    columns = {column.name for column in Auditoria.__table__.columns}

    assert columns == {
        "id",
        "id_usuario",
        "recurso",
        "id_recurso",
        "operacion",
        "valor_anterior",
        "valor_nuevo",
        "ip_address",
        "detalle",
        "timestamp_accion",
    }


def test_auditoria_id_usuario_is_nullable():
    col = Auditoria.__table__.columns["id_usuario"]
    assert col.nullable is True


def test_auditoria_has_usuario_foreign_key():
    fk_columns = {fk.parent.name for fk in Auditoria.__table__.foreign_keys}

    assert "id_usuario" in fk_columns
