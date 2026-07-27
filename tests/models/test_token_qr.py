from apps.API.models.token_qr import TokenQR


def test_token_qr_maps_to_expected_table():
    assert TokenQR.__tablename__ == "token_qr"


def test_token_qr_columns_match_database_sql_schema():
    columns = {column.name for column in TokenQR.__table__.columns}

    assert columns == {
        "id",
        "id_sede",
        "id_dispositivo",
        "id_estado_token",
        "token",
        "codigo_alfa",
        "generado_en",
        "expira_en",
        "consumido_en",
        "ip_generacion",
    }


def test_token_qr_token_is_unique():
    token_column = TokenQR.__table__.columns["token"]

    assert token_column.unique is True


def test_token_qr_dispositivo_and_estado_are_required():
    assert TokenQR.__table__.columns["id_dispositivo"].nullable is False
    assert TokenQR.__table__.columns["id_estado_token"].nullable is False
    assert TokenQR.__table__.columns["expira_en"].nullable is False
