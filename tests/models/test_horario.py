from apps.API.models.horario import Horario


def test_horario_maps_to_expected_table():
    assert Horario.__tablename__ == "horario"


def test_horario_columns_match_database_sql_schema():
    columns = {column.name for column in Horario.__table__.columns}
    assert columns == {
        "id",
        "id_sede",
        "nombre",
        "hora_entrada",
        "hora_salida",
        "tolerancia_min",
        "vigente_desde",
        "vigente_hasta",
        "created_at",
    }
