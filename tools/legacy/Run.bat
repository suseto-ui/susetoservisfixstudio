@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - 1-Click Launcher (Run)

:: Ensure we are running in the script's root directory
cd /d "%~dp0"

echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - 1-KLIK SPUSTENI APLIKACE (RUN)
echo ==============================================================================
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py -3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [CHYBA] Python 3.10+ neni nainstalovan!
        echo Stahnete z: https://www.python.org/downloads/
        echo Nezapomente zaskrtnout 'Add python.exe to PATH'!
        pause
        exit /b 1
    ) else (
        set "PY_CMD=py -3"
    )
) else (
    set "PY_CMD=python"
)

:: 2. Activate venv if present, otherwise create
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [*] Zakladam virtualni prostredi .venv...
    %PY_CMD% -m venv .venv
    call ".venv\Scripts\activate.bat"
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
)

:: 3. Ensure database schema and directories are initialized if missing
if not exist "hardware_diagnostics.db" (
    echo [*] Inicializuji SQLite WAL ledger a pracovni slozky...
    python setup_and_run.py >nul 2>&1
)

:: 4. Launch Main GUI Application
echo [*] Spoustim SusetoDroidFixStudio...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ==============================================================================
    echo [CHYBA] Aplikace skoncila s chybou. Proctete si WINDOWS_SETUP_GUIDE.md.
    echo ==============================================================================
    pause
)
