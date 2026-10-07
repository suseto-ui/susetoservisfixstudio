@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - Automaticke Stazeni a Instalace Ovladacu

cd /d "%~dp0"

echo ==============================================================================
echo    SUSETO DROID FIX STUDIO - AUTOMATICKE STAZENI A INSTALACE OVLADACU
echo ==============================================================================
echo Tento skript automaticky stahne a nainstaluje vsechny potrebne ovladace:
echo  1. Qualcomm Snapdragon QDLoader 9008 Driver (v2.1.3.8 x64)
echo  2. MediaTek SP VCOM & BootROM Driver (v5.2136 x64)
echo  3. FTDI D2XX Direct Driver pro SmartCard dongly
echo  4. Google Android WinUSB Driver pro Fastboot a ADB
echo ==============================================================================
echo.

:: 1. Kontrola administrátorských práv
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Vyžadují se administrátorská oprávnění pro instalaci ovladačů.
    echo [*] Vyvolávám UAC potvrzení...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b 0
)

:: 2. Aktivace virtuálního prostředí
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

:: 3. Spuštění Python stahovače ovladačů
python core/driver_downloader.py

echo.
echo [*] Spouštím finální registraci ovladačů do Windows DriverStore...
if exist "drivers\winusb_setup.cmd" (
    call "drivers\winusb_setup.cmd"
)

echo.
echo ==============================================================================
echo [DOKONČENO] Všechny ovladače byly úspěšně staženy a integrovány!
echo ==============================================================================
pause
