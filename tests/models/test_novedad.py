from apps.API.models.novedad import Novedad


def test_novedad_maps_to_expected_table():
    assert Novedad.__tablename__ == "novedad"


def test_novedad_columns_match_schema():
    columns = {column.name for column in Novedad.__table__.columns}
    assert columns == {
        "id",
        "id_empleado",
        "id_tipo_novedad",
        "id_asistencia",
        "fecha",
        "observacion",
        "created_at",
    }
