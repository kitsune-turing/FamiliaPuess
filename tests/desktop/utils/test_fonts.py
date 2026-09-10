from apps.Desktop.utils.fonts import register_application_fonts


def test_register_application_fonts_loads_every_weight_successfully(qapp):
    font_ids = register_application_fonts()

    assert len(font_ids) == 4
    assert all(font_id != -1 for font_id in font_ids)
