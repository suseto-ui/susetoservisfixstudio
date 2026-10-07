@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - Spusteni aplikace (Run)

cd /d "%~dp0"

:: 1. Pokud existuje zkompilovaný .exe, spustíme jej přímo
if exist "SusetoDroidFixStudio.exe" (
    start "" "SusetoDroidFixStudio.exe" %*
    exit /b 0
)

:: 2. Jinak spustíme přes Python / .venv
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

python main.py %*
if %errorlevel% neq 0 (
    echo.
    echo [CHYBA] Spuštění selhalo. Podívejte se do souboru README.md.
    pause
)
