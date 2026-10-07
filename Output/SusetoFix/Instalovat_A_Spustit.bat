@echo off
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
