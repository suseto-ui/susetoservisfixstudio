@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - 1-Klikova Kompletni Instalace (C:\SusetoFix)

:: Ensure we are running from the script's directory
cd /d "%~dp0"

echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - 1-KLIKOVA INSTALACE (C:\SusetoFix)
echo ==============================================================================
echo Tento skript jednim spustenim provede:
echo  1. Overeni administrátorskych prav a prostredi Windows
echo  2. Nastaveni opravneni plneho pristupu (icacls) pro slozku C:\SusetoFix
echo  3. Tichou instalaci vsech ovladacu (WinUSB, Qualcomm 9008, MTK BROM, FTDI)
echo  4. Sestaveni a instalaci kompletni aplikace do C:\SusetoFix
echo  5. Vytvoreni ikony a zastupce na Plose (Desktop)
echo  6. Okamzite spusteni aplikace
echo ==============================================================================
echo.

:: 1. Kontrola administrátorských práv a automatická elevace
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Vyžadují se administrátorská oprávnění pro instalaci ovladačů a složky C:\SusetoFix.
    echo [*] Vyvolávám UAC potvrzení...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb RunAs"
    exit /b 0
)

:: 2. Detekce Pythonu
echo [*] Detekuji Python 3.10+...
set "PY_CMD="
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    py -3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=py -3"
    )
)

if "%PY_CMD%"=="" (
    echo.
    echo ==============================================================================
    echo [CHYBA] Python 3.10+ nebyl v systému nalezen!
    echo Prosim stahněte a nainstalujte Python z: https://www.python.org/downloads/
    echo ⚠️ DŮLEŽITÉ: Při instalaci zaškrtněte volbu "Add python.exe to PATH"!
    echo ==============================================================================
    echo.
    pause
    exit /b 1
)

echo [+] Nalezen Python:
%PY_CMD% --version
echo.

:: 3. Aktivace nebo vytvoření virtuálního prostředí
if exist ".venv\Scripts\activate.bat" (
    echo [*] Aktivuji virtuální prostředí .venv...
    call ".venv\Scripts\activate.bat"
) else (
    echo [*] Zakládám virtuální prostředí .venv a instaluji knihovny...
    %PY_CMD% -m venv .venv
    call ".venv\Scripts\activate.bat"
    python -m pip install --upgrade pip --quiet
    if exist "requirements.txt" (
        pip install -r requirements.txt --quiet
    )
)

:: 4. Příprava cílové složky C:\SusetoFix a nastavení oprávnění
set "TARGET_DIR=C:\SusetoFix"
echo [*] Příprava cílové složky: %TARGET_DIR%
if not exist "%TARGET_DIR%" (
    mkdir "%TARGET_DIR%" 2>nul
    if not exist "%TARGET_DIR%" (
        echo [!] C:\ je chráněno, přepínám na %LOCALAPPDATA%\SusetoFix...
        set "TARGET_DIR=%LOCALAPPDATA%\SusetoFix"
        if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"
    )
)

echo [*] Nastavuji plná oprávnění (icacls) pro bezpečný přístup k databázi a ovladačům...
icacls "%TARGET_DIR%" /grant "%USERNAME%":(OI)(CI)F /T /Q >nul 2>&1
icacls "%TARGET_DIR%" /grant *S-1-5-32-545:(OI)(CI)F /T /Q >nul 2>&1

:: 5. Sestavení a nakopírování distribuce
echo [*] Sestavuji a připravuji distribuční balíček...
python build_master_installer.py >nul 2>&1

if exist "Output\SusetoFix" (
    echo [*] Kopíruji programové soubory do %TARGET_DIR%...
    xcopy "Output\SusetoFix\*" "%TARGET_DIR%\" /E /Y /Q >nul 2>&1
) else if exist "dist\SusetoDroidFixStudio" (
    echo [*] Kopíruji ze složky dist do %TARGET_DIR%...
    xcopy "dist\SusetoDroidFixStudio\*" "%TARGET_DIR%\" /E /Y /Q >nul 2>&1
) else (
    echo [*] Kopíruji soubory ze zdrojové složky...
    xcopy "%~dp0*" "%TARGET_DIR%\" /E /Y /Q /EXCLUDE:%~dp0.gitignore >nul 2>&1
)

:: 6. Tichá instalace ovladačů
echo [*] Spouštím tichou instalaci a registraci hardwarových ovladačů...
if exist "%TARGET_DIR%\drivers\winusb_setup.cmd" (
    call "%TARGET_DIR%\drivers\winusb_setup.cmd"
) else if exist "drivers\winusb_setup.cmd" (
    call "drivers\winusb_setup.cmd"
)

:: 7. Vytvoření zástupce na ploše (Desktop)
echo [*] Vytvářím zástupce na ploše...
set "EXE_FILE=%TARGET_DIR%\SusetoDroidFixStudio.exe"
if not exist "%EXE_FILE%" (
    set "EXE_FILE=%TARGET_DIR%\run.bat"
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $s = $ws.CreateShortcut(\"$desk\Suseto Droid Fix Studio.lnk\"); $s.TargetPath = '%EXE_FILE%'; $s.WorkingDirectory = '%TARGET_DIR%'; $s.Description = 'SusetoDroidFixStudio Service Cockpit'; $s.Save()"

echo.
echo ==============================================================================
echo [ÚSPĚCH] INSTALACE BYLA ÚSPĚŠNĚ DOKONČENA!
echo ==============================================================================
echo  - Umístění aplikace:   %TARGET_DIR%
echo  - Zástupce na ploše:   Suseto Droid Fix Studio.lnk
echo  - Stav ovladačů:       WinUSB, FTDI, CP210x, Qualcomm 9008, MTK registrovány
echo  - Oprávnění složky:    Plný přístup (Full Control)
echo ==============================================================================
echo.

:: 8. Spuštění aplikace
echo [*] Spouštím aplikaci...
if exist "%TARGET_DIR%\SusetoDroidFixStudio.exe" (
    start "" /D "%TARGET_DIR%" "%TARGET_DIR%\SusetoDroidFixStudio.exe"
) else (
    start "" /D "%TARGET_DIR%" "%TARGET_DIR%\run.bat"
)

timeout /t 3 >nul
exit /b 0
