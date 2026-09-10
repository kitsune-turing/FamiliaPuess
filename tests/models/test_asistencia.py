from apps.API.models.asistencia import Asistencia


def test_asistencia_maps_to_expected_table():
    assert Asistencia.__tablename__ == "asistencia"


def test_asistencia_columns_match_database_sql_schema():
    columns = {column.name for column in Asistencia.__table__.columns}

    assert columns == {
        "id",
        "id_empleado",
        "id_token_qr",
        "id_tipo_registro",
        "id_sede",
        "fecha_registro",
        "registrado_en",
    }


def test_asistencia_required_fields():
    assert Asistencia.__table__.columns["id_empleado"].nullable is False
    assert Asistencia.__table__.columns["id_token_qr"].nullable is False
    assert Asistencia.__table__.columns["id_tipo_registro"].nullable is False
    assert Asistencia.__table__.columns["id_sede"].nullable is False
    assert Asistencia.__table__.columns["fecha_registro"].nullable is False


def test_asistencia_has_unique_constraint_for_duplicate_prevention():
    constraint_names = [
        c.name
        for c in Asistencia.__table__.constraints
        if hasattr(c, "columns") and len(c.columns) > 1
    ]

    assert "uq_asistencia_empleado_fecha_tipo" in constraint_names
