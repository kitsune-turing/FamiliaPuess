from apps.Desktop.utils.assets import font_paths, icon_path, image_path


def test_icon_path_resolves_to_existing_files():
    for name in ("point.svg", "time.svg", "wifi.svg"):
        assert icon_path(name).is_file()


def test_image_path_resolves_to_existing_files():
    for name in ("marca.png", "logos.png", "mazorca1.png"):
        assert image_path(name).is_file()


def test_font_paths_finds_all_poppins_weights():
    names = {path.name for path in font_paths()}

    assert names == {
        "Poppins-Regular.ttf",
        "Poppins-Medium.ttf",
        "Poppins-SemiBold.ttf",
        "Poppins-Bold.ttf",
    }
