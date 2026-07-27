from apps.API.models.sede import Sede


def test_sede_maps_to_expected_table():
    assert Sede.__tablename__ == "sede"


def test_sede_columns_match_database_sql_schema():
    columns = {column.name for column in Sede.__table__.columns}

    assert columns == {"id", "nombre", "direccion", "id_estado", "created_at", "updated_at"}
