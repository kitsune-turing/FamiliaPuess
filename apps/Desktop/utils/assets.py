from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent.parent / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
IMAGES_DIR = RESOURCES_DIR / "images"
FONTS_DIR = RESOURCES_DIR / "fonts"


def icon_path(name: str) -> Path:
    return ICONS_DIR / name


def image_path(name: str) -> Path:
    return IMAGES_DIR / name


def font_paths() -> list[Path]:
    return sorted(FONTS_DIR.glob("*.ttf"))
