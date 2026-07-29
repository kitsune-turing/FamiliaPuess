from apps.API.models.reporte_semanal import ReporteSemanal


def test_reporte_semanal_maps_to_expected_table():
    assert ReporteSemanal.__tablename__ == "reporte_semanal"


def test_reporte_semanal_columns_match_schema():
    columns = {column.name for column in ReporteSemanal.__table__.columns}
    assert columns == {
        "id",
        "fecha_inicio",
        "fecha_fin",
        "total_registros",
        "total_novedades",
        "created_at",
    }
