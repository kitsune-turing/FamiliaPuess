from apps.API.models.empleado import Empleado


def test_empleado_maps_to_expected_table():
    assert Empleado.__tablename__ == "empleado"


def test_empleado_columns_match_database_sql_schema():
    columns = {column.name for column in Empleado.__table__.columns}

    assert columns == {
        "id",
        "documento",
        "nombre",
        "apellido",
        "cargo",
        "id_estado",
        "id_sede",
        "created_at",
        "updated_at",
    }


def test_empleado_documento_is_unique():
    col = Empleado.__table__.columns["documento"]

    assert col.unique is True
    assert col.nullable is False


def test_empleado_required_fields():
    assert Empleado.__table__.columns["nombre"].nullable is False
    assert Empleado.__table__.columns["apellido"].nullable is False
    assert Empleado.__table__.columns["cargo"].nullable is False
    assert Empleado.__table__.columns["id_estado"].nullable is False
    assert Empleado.__table__.columns["id_sede"].nullable is False
