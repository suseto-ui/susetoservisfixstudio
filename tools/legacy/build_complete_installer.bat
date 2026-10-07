@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - 1-Click Master Installer Builder

echo ==============================================================================
echo    SUSETO DROID FIX STUDIO - 1-KLIK GENERATOR KOMPLETNIHO INSTALATORU
echo ==============================================================================
echo Tento skript jednim kliknutim zkompiluje a zabali kompletni instalacni balicek:
echo  1. Zkontroluje Python a zavislosti
echo  2. Pripravi ovladace (WinUSB, FTDI, CP210x), ADB nastroje a SQLite WAL databazi
echo  3. Zkompiluje standalone .exe binarku (PyInstaller)
echo  4. Vytvori finalni instalator (Inno Setup Setup.exe nebo prenositelny instalacni ZIP)
echo  5. Otevre slozku Output\ s hotovym instalatorem
echo ==============================================================================
echo.

:: 1. Detekce Pythonu
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [CHYBA] Python nebyl v systemu nalezen!
    echo Prosim nainstalujte Python 3.10+ z https://www.python.org/downloads/
    echo Pri instalaci nezapomente zaskrtnout "Add python.exe to PATH".
    echo.
    pause
    exit /b 1
)

:: 2. Kontrola virtualniho prostredi
if exist "venv\Scripts\activate.bat" (
    echo [*] Aktivuji virtualni prostredi venv...
    call venv\Scripts\activate.bat
) else (
    echo [*] Virtualni prostredi venv nenalezeno, vytvarim nove...
    python -m venv venv
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
    )
)

:: 3. Kontrola zavislosti
echo [*] Overuji a aktualizuji potrebne knihovny (PyInstaller, PySide6, pyserial)...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: 4. Spusteni orchestratoru instalatoru
echo.
echo [*] Spoustim hlavni kompilacni proces (build_master_installer.py)...
echo.
python build_master_installer.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ==============================================================================
    echo [CHYBA] Kompilace instalatoru selhala! Prohlidnete si chybove hlaseni vyse.
    echo ==============================================================================
    pause
    exit /b %ERRORLEVEL%
)

:: 5. Otevreni vystupni slozky s hotovym instalatorem
echo.
echo ==============================================================================
echo [DOKONCENO] Hotovy instalacni balicek naleznete ve slozce: Output\
echo Oteviram slozku v Pruzkumnikovi Windows...
echo ==============================================================================
if exist "Output" (
    start "" explorer "Output"
)

echo.
echo Stisknete libovolnou klavesu pro ukonceni...
pause >nul
exit /b 0
