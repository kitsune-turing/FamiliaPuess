from apps.API.models.cat_estado_token import CatEstadoToken


def test_cat_estado_token_maps_to_expected_table():
    assert CatEstadoToken.__tablename__ == "cat_estado_token"


def test_cat_estado_token_columns_match_database_sql_schema():
    columns = {column.name for column in CatEstadoToken.__table__.columns}

    assert columns == {"id", "codigo", "nombre", "descripcion"}
