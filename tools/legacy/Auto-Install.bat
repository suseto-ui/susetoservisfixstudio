@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - 1-Click Automaticky Instalator (C:\SusetoFix)

:: Ensure we are running in the script's root directory
cd /d "%~dp0"

echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - AUTOMATICKA INSTALACE DO C:\SusetoFix
echo ==============================================================================
echo.

:: 1. Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py -3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [CHYBA] Python nebyl v systemu nalezen!
        echo.
        echo Prosim stahnete a nainstalujte Python 3.10+ z:
        echo https://www.python.org/downloads/
        echo (Nezapomente zaskrtnout 'Add python.exe to PATH'!)
        echo ==============================================================================
        pause
        exit /b 1
    ) else (
        set "PY_CMD=py -3"
    )
) else (
    set "PY_CMD=python"
)

echo [*] Nalezen Python interpreter:
%PY_CMD% --version
echo.

:: 2. Activate or create virtual environment
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    echo [+] Virtualni prostredi .venv aktivovano.
) else (
    echo [*] Inicializuji virtualni prostredi .venv...
    %PY_CMD% -m venv .venv
    if exist ".venv\Scripts\activate.bat" (
        call ".venv\Scripts\activate.bat"
    )
)

:: 3. Ensure required packages exist
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Instalace PyInstaller a zavislosti...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt --quiet
    python -m pip install pyinstaller --quiet
)

:: 4. Run Master Installer Build Pipeline
echo.
echo [*] Sestavuji produkcni balicek a standalone .exe...
python build_master_installer.py

if %errorlevel% neq 0 (
    echo.
    echo [CHYBA] Sestaveni selhalo!
    pause
    exit /b 1
)

:: 5. Install to short path C:\SusetoFix (eliminating Windows MAX_PATH errors)
set "DEST_DIR=C:\SusetoFix"
echo.
echo [*] Instaluji program do kratke cesty: %DEST_DIR%
if not exist "%DEST_DIR%" (
    mkdir "%DEST_DIR%" 2>nul
    if not exist "%DEST_DIR%" (
        echo [!] Pristup k C:\ byl odepren, instaluji do %LOCALAPPDATA%\SusetoFix...
        set "DEST_DIR=%LOCALAPPDATA%\SusetoFix"
        if not exist "!DEST_DIR!" mkdir "!DEST_DIR!"
    )
)

if exist "Output\SusetoFix" (
    xcopy "Output\SusetoFix\*" "%DEST_DIR%\" /E /Y /Q >nul 2>&1
) else if exist "dist\SusetoDroidFixStudio" (
    xcopy "dist\SusetoDroidFixStudio\*" "%DEST_DIR%\" /E /Y /Q >nul 2>&1
)

:: 6. Register Drivers
echo [*] Registrace hardware ovladacu (FTDI, CP210x, WinUSB)...
if exist "%DEST_DIR%\drivers\winusb_setup.cmd" (
    call "%DEST_DIR%\drivers\winusb_setup.cmd" >nul 2>&1
)

:: 7. Create Desktop Shortcut (supporting OneDrive / Czech 'Plocha' / English Desktop)
echo [*] Vytvarim zastupce na plose...
set "TARGET_EXE=%DEST_DIR%\SusetoDroidFixStudio.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ws = New-Object -ComObject WScript.Shell; $desk = [Environment]::GetFolderPath('Desktop'); $s = $ws.CreateShortcut(\"$desk\SusetoDroidFixStudio.lnk\"); $s.TargetPath = '%TARGET_EXE%'; $s.WorkingDirectory = '%DEST_DIR%'; $s.Description = 'SusetoDroidFixStudio Service Cockpit'; $s.Save()"

echo.
echo ==============================================================================
echo [USPECH] INSTALACE BYLA USPESNE DOKONCENA!
echo  - Program nainstalovan do: %DEST_DIR%
echo  - Zastupce vytvoren na plose: SusetoDroidFixStudio.lnk
echo  - Spustitelny soubor: %TARGET_EXE%
echo ==============================================================================
echo.
echo [*] Okamzite spoustim aplikaci...
if exist "%TARGET_EXE%" (
    start "" /D "%DEST_DIR%" "%TARGET_EXE%"
) else (
    echo Spoustim aplikaci pres Python...
    python main.py
)

timeout /t 3 >nul
exit /b 0
