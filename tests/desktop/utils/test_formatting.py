from datetime import datetime

from apps.Desktop.utils.formatting import format_datetime_es


def test_format_datetime_es_uses_spanish_weekday_and_month():
    moment = datetime(2026, 7, 27, 10, 46)  # a Monday in July

    formatted = format_datetime_es(moment)

    assert "Lunes" in formatted
    assert "Julio" in formatted
    assert "2026" in formatted
    assert "10:46 AM" in formatted
