from apps.API.models.cat_novedad import CatNovedad


def test_cat_novedad_maps_to_expected_table():
    assert CatNovedad.__tablename__ == "cat_novedad"


def test_cat_novedad_columns_match_schema():
    columns = {column.name for column in CatNovedad.__table__.columns}
    assert columns == {
        "id",
        "codigo",
        "nombre",
        "id_estado",
        "color",
        "icono",
        "descripcion",
        "created_at",
        "updated_at",
    }
