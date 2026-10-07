@echo off
setlocal
title SusetoDroidFixStudio - Vytvoreni zastupce na plose
echo [*] Vytvarim zastupce na Vasi plose a registruji ovladace...

set "TARGET_EXE=%~dp0SusetoDroidFixStudio.exe"
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
set "SHORTCUT_PATH=%DESKTOP_DIR%\SusetoDroidFixStudio.lnk"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_EXE%'; $s.WorkingDirectory = '%~dp0'; $s.Description = 'SusetoDroidFixStudio Cockpit'; $s.Save()"

echo [+] Zastupce na plose byl uspesne vytvoren: %SHORTCUT_PATH%
echo.
if exist "%~dp0drivers\winusb_setup.cmd" (
    echo [*] Registrace hardware ovladacu...
    call "%~dp0drivers\winusb_setup.cmd"
)
echo [HOTOVO] Aplikace je pripravena. Nyni ji muzete spoustet primo z plochy!
pause
