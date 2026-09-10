"""Build script for Familia Puess Desktop Windows installer.

Usage:
    python apps/Desktop/build_installer.py [--skip-inno]

Steps:
    1. Install PyInstaller if not present
    2. Run PyInstaller with the .spec file
    3. (Optional) Run Inno Setup to produce the .exe installer

Requirements:
    - Python 3.10+
    - pip (for installing PyInstaller)
    - Inno Setup 6 (optional, for producing the installer .exe)
      Download: https://jrsoftware.org/isdl.php
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SPEC_FILE = HERE / "familia_puess.spec"
ISS_FILE = HERE / "installer.iss"
DIST_DIR = PROJECT_ROOT / "dist"


def _ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print(">> Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])


def _run_pyinstaller() -> None:
    print(">> Running PyInstaller...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            str(SPEC_FILE),
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(PROJECT_ROOT / "build"),
            "--noconfirm",
        ],
        cwd=str(PROJECT_ROOT),
    )
    print(f">> PyInstaller output: {DIST_DIR / 'FamiliaPuess'}")


def _find_inno_setup() -> Path | None:
    iscc = shutil.which("ISCC")
    if iscc:
        return Path(iscc)
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _run_inno_setup() -> None:
    iscc = _find_inno_setup()
    if iscc is None:
        print(">> Inno Setup not found. Skipping installer generation.")
        print("   Download from: https://jrsoftware.org/isdl.php")
        print(f"   Then run: ISCC \"{ISS_FILE}\"")
        return
    print(f">> Running Inno Setup ({iscc})...")
    installer_out = DIST_DIR / "installer"
    installer_out.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(iscc), str(ISS_FILE)])
    print(f">> Installer output: {installer_out}")


def main() -> int:
    skip_inno = "--skip-inno" in sys.argv

    _ensure_pyinstaller()
    _run_pyinstaller()

    if not skip_inno:
        _run_inno_setup()

    print(">> Done!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
