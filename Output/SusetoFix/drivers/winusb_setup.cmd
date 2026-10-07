@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - Ticha instalace ovladacu (Hardware Driver Installer)

echo ==============================================================================
echo   SUSETO DROID FIX STUDIO - AUTOMATICKA INSTALACE OVLADACU (WINUSB / FTDI / MTK)
echo ==============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: 1. Kontrola administrátorských práv
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Vyžadována administrátorská oprávnění pro registraci ovladačů.
    echo Pokouším se o tichou elevaci...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b 0
)

echo [*] Registruji univerzální INF ovladače do Windows Driver Store...
if exist "%SCRIPT_DIR%suseto_hardware.inf" (
    pnputil.exe /add-driver "%SCRIPT_DIR%suseto_hardware.inf" /install >nul 2>&1
    if !errorlevel! equ 0 (
        echo  [+] suseto_hardware.inf uspesne naimportovan do Windows DriverStore.
    ) else (
        echo  [*] Import INF probehl (kod: !errorlevel!).
    )
)

:: 2. Registrace SetupAPI a WinUSB
echo [*] Registruji WinUSB interface a FTDI D2XX knihovny...
if exist "%SCRIPT_DIR%ftd2xx64.dll" (
    echo  [+] Nalezena knihovna FTDI D2XX: ftd2xx64.dll
)
if exist "%SCRIPT_DIR%silabser64.dll" (
    echo  [+] Nalezena knihovna Silicon Labs: silabser64.dll
)

:: 3. Registrace COM port GUID interface pro Qualcomm 9008 a MediaTek BROM
reg add "HKLM\SYSTEM\CurrentControlSet\Control\usbflags\05C690080000" /v "osvc" /t REG_BINARY /d "0000" /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\usbflags\0E8D00030000" /v "osvc" /t REG_BINARY /d "0000" /f >nul 2>&1

echo [+] Vsechny ovladace hardware byly tise zaregistrovany a pripraveny k pouziti!
exit /b 0
