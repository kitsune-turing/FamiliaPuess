# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Familia Puess Desktop kiosk app (directory mode for installer)."""

import os
from pathlib import Path

import certifi

HERE = Path(SPECPATH).resolve()
PROJECT_ROOT = HERE.parents[1]  # FamiliaPuess/

block_cipher = None

_certifi_pem = certifi.where()

a = Analysis(
    [str(HERE / "main.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=[
        (str(HERE / "assets" / "app.ico"), os.path.join("apps", "Desktop", "assets")),
        (str(HERE / "assets" / "icons"), os.path.join("apps", "Desktop", "assets", "icons")),
        (str(HERE / "assets" / "images"), os.path.join("apps", "Desktop", "assets", "images")),
        (str(HERE / "assets" / "fonts"), os.path.join("apps", "Desktop", "assets", "fonts")),
        (_certifi_pem, "certifi"),
    ],
    hiddenimports=[
        "PySide6.QtSvgWidgets",
        "PySide6.QtSvg",
        "certifi",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib",
        "numpy",
        "scipy",
        "pandas",
        "tkinter",
        "unittest",
        "pytest",
        "sqlalchemy",
        "asyncpg",
        "fastapi",
        "uvicorn",
    ],
    noarchive=False,
    optimize=0,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="FamiliaPuess",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(HERE / "assets" / "app.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FamiliaPuess",
)
