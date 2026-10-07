@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - Sestaveni instalatoru a balicku (Build)

cd /d "%~dp0"

echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - 1-KLIKOVE SESTAVENI INSTALATORU (BUILD)
echo ==============================================================================
echo.

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

python build_master_installer.py
if %errorlevel% neq 0 (
    echo.
    echo [CHYBA] Sestavení instalačního balíčku selhalo.
    pause
    exit /b %errorlevel%
)

echo.
echo ==============================================================================
echo [ÚSPĚCH] Instalační balíček byl vygenerován do složky Output\
echo ==============================================================================
if exist "Output" (
    start "" explorer "Output"
)

pause
