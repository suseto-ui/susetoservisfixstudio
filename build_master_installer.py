#!/usr/bin/env python3
"""
Master Installer Builder (`build_master_installer.py`).
Orchestrates end-to-end packaging into a complete, clean Windows installation package:
  1. Staging native drivers (FTDI, CP210x, WinUSB), SQLite WAL schema, and CLI tools.
  2. Compiling standalone executable via PyInstaller into dist/SusetoDroidFixStudio/.
  3. Generating Inno Setup Installer (SusetoFix_Setup.exe) if ISCC.exe is available,
     OR creating a compact portable installer package (SusetoFix_Portable_Installer.zip)
     with flat paths avoiding Windows MAX_PATH (260 characters) limits.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("master_installer")

_ROOT = Path(__file__).resolve().parent
_OUTPUT_DIR = _ROOT / "Output"


def find_inno_setup_compiler() -> str | None:
    """Locate Inno Setup 6 command line compiler (ISCC.exe)."""
    iscc = shutil.which("iscc.exe") or shutil.which("iscc") or shutil.which("ISCC.exe")
    if iscc:
        return iscc

    candidates = [
        os.path.expandvars(r"%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"),
        os.path.expandvars(r"%ProgramFiles%\Inno Setup 6\ISCC.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return candidate

    return None


def step1_compile_pyinstaller_distribution() -> bool:
    """Execute production_build.py to generate standalone distribution files."""
    logger.info("FÁZE 1/3: Staging ovladačů, SQLite schématu a sestavení .exe přes PyInstaller...")
    build_script = _ROOT / "production_build.py"
    if not build_script.exists():
        logger.error("[CHYBA] production_build.py nebyl nalezen v %s", _ROOT)
        return False

    res = subprocess.run([sys.executable, str(build_script)], capture_output=True, text=True)
    if res.returncode != 0:
        logger.error("[CHYBA] production_build.py selhal:\n%s\n%s", res.stdout, res.stderr)
        return False

    dist_dir = _ROOT / "dist" / "SusetoDroidFixStudio"
    if not dist_dir.exists():
        logger.error("[CHYBA] Výstupní složka dist/SusetoDroidFixStudio nebyla vytvořena.")
        return False

    logger.info("   [✔] Standalone distribuce úspěšně sestavena v: dist/SusetoDroidFixStudio")
    return True


def step2_create_installer() -> tuple[bool, str]:
    """Compile Inno Setup script OR create flat self-extracting portable package."""
    _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    iscc = find_inno_setup_compiler()

    if iscc:
        logger.info("FÁZE 2/3: Nalezen Inno Setup Compiler (%s). Kompiluji SusetoFix_Setup.exe...", iscc)
        iss_file = _ROOT / "SusetoDroidFixStudio.iss"
        if not iss_file.exists():
            logger.error("[CHYBA] Skript %s nebyl nalezen.", iss_file)
            return False, ""

        cmd = [iscc, str(iss_file)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            setup_exe = _OUTPUT_DIR / "SusetoFix_Setup.exe"
            logger.info("   [✔] Inno Setup kompilace úspěšná! Soubor: %s", setup_exe)
            return True, str(setup_exe)
        else:
            logger.warning("   [!] Inno Setup selhal (%s). Přepínám na vytvoření portable balíčku...", res.stderr)

    # Fallback: Flat portable release avoiding long paths
    logger.info("FÁZE 2/3: Vytvářím optimalizovaný přenositelný instalační balíček s krátkými cestami (C:\\SusetoFix)...")
    
    portable_dir = _OUTPUT_DIR / "SusetoFix"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    portable_dir.mkdir(parents=True, exist_ok=True)

    dist_dir = _ROOT / "dist" / "SusetoDroidFixStudio"
    for item in dist_dir.iterdir():
        dest = portable_dir / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(item, dest)

    # 1-Click Installer script for portable package (Installs directly to C:\SusetoFix)
    install_shortcut_bat = portable_dir / "Instalovat_A_Spustit.bat"
    shortcut_code = r"""@echo off
setlocal
title SusetoDroidFixStudio - Automaticka instalace do C:\SusetoFix
echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - AUTOMATICKA INSTALACE (C:\SusetoFix)
echo ==============================================================================
echo.

set "DEST_DIR=C:\SusetoFix"
echo [*] Instaluji aplikaci do kratke cesty: %DEST_DIR%
if not exist "%DEST_DIR%" mkdir "%DEST_DIR%"

echo [*] Kopiruji programove soubory...
xcopy "%~dp0*" "%DEST_DIR%\" /E /Y /Q >nul 2>&1

echo [*] Registrace hardware ovladacu...
if exist "%DEST_DIR%\drivers\winusb_setup.cmd" (
    call "%DEST_DIR%\drivers\winusb_setup.cmd"
)

echo [*] Vytvarim zastupce na plose...
set "TARGET_EXE=%DEST_DIR%\SusetoDroidFixStudio.exe"
set "SHORTCUT_PATH=%USERPROFILE%\Desktop\SusetoDroidFixStudio.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_EXE%'; $s.WorkingDirectory = '%DEST_DIR%'; $s.Description = 'SusetoDroidFixStudio Service Cockpit'; $s.Save()"

echo [+] Zastupce na plose vytvoren: %SHORTCUT_PATH%
echo [+] Instalace dokoncena!
echo.
echo [*] Spoustim aplikaci...
start "" "%TARGET_EXE%"
exit /b 0
"""
    with open(install_shortcut_bat, "w", encoding="cp852", errors="ignore") as f:
        f.write(shortcut_code)

    # Flat ZIP package (short paths inside zip: SusetoFix/...)
    zip_path = _OUTPUT_DIR / "SusetoFix_Portable_Installer.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(portable_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(_OUTPUT_DIR)
                zipf.write(file_path, arcname)

    logger.info("   [✔] Vytvořen přenositelný instalátor bez dlouhých cest: %s", zip_path.name)
    return True, str(zip_path)


def main() -> None:
    print("=" * 78)
    print("   SUSETO DROID FIX STUDIO - MASTER INSTALLER BUILD PIPELINE              ")
    print("=" * 78)

    ok = step1_compile_pyinstaller_distribution()
    if not ok:
        logger.error("[FATAL] Selhalo sestavení distribuce.")
        sys.exit(1)

    ok, result_path = step2_create_installer()
    if not ok:
        logger.error("[FATAL] Selhala tvorba instalačního balíčku.")
        sys.exit(1)

    logger.info("FÁZE 3/3: Finální kontrola a report...")
    res_file = Path(result_path)
    file_size_mb = res_file.stat().st_size / (1024 * 1024) if res_file.exists() else 0.0

    print("=" * 78)
    print(" [USPECH] FINÁLNÍ INSTALAČNÍ BALÍČEK BYL ÚSPĚŠNĚ VYTVOŘEN!              ")
    print("=" * 78)
    print(f"  Soubor:     {res_file.name}")
    print(f"  Cesta:      {res_file}")
    print(f"  Velikost:   {file_size_mb:.2f} MB")
    print(f"  Cílová cesta instalace: C:\\SusetoFix (bezpečné před limitem 260 znaků)")
    print("=" * 78)
    sys.exit(0)


if __name__ == "__main__":
    main()
