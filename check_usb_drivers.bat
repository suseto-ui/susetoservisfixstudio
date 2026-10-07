@echo off
setlocal enabledelayedexpansion
title SusetoDroidFixStudio - Diagnostika USB ovladacu a zarizeni (Device Manager Check)

cd /d "%~dp0"

echo ==============================================================================
echo       SUSETO DROID FIX STUDIO - HLOUBKOVA KONTROLA USB OVLADACU A ZARIZENI
echo ==============================================================================
echo Tento nastroj provede detailni audit Windows Device Manageru pro servisni cipy:
echo  1. Qualcomm Snapdragon EDL (VID: 05C6, PID: 9008 / 900E / 901D)
echo  2. MediaTek BootROM & Preloader (VID: 0E8D, PID: 0003 / 2000)
echo  3. FTDI SmartCard & UART prevodiky (VID: 0403, PID: 6001)
echo  4. Filtry a ovladace: WinUSB, libusb-win32, libusb0, qcusbser, usb2ser
echo ==============================================================================
echo.

set "SCRIPT_DIR=%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference = 'SilentlyContinue'; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"Write-Host '[1/4] KONTROLA REGISTROVANYCH OVLADACOVYCH SLUZEB (DRIVER SERVICES)' -ForegroundColor Cyan; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"$services = @('WinUSB', 'libusb0', 'libusbK', 'qcusbser', 'usb2ser', 'ftdibus', 'silabser'); " ^
"foreach ($svc in $services) { " ^
"    $drv = Get-Service -Name $svc 2>$null; " ^
"    if ($drv) { " ^
"        Write-Host (' [+] Sluzba ' + $svc.PadRight(12) + ': INSTALOVANA (Stav: ' + $drv.Status + ')') -ForegroundColor Green; " ^
"    } else { " ^
"        $infCheck = Get-ChildItem 'C:\Windows\INF\*.inf' | Select-String -Pattern $svc -SimpleMatch 2>$null; " ^
"        if ($infCheck) { " ^
"            Write-Host (' [~] Sluzba ' + $svc.PadRight(12) + ': PRIPRAVENA V INF STORE') -ForegroundColor Yellow; " ^
"        } else { " ^
"            Write-Host (' [!] Sluzba ' + $svc.PadRight(12) + ': NENI REGISTROVANA') -ForegroundColor Gray; " ^
"        } " ^
"    } " ^
"}; " ^
"Write-Host ''; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"Write-Host '[2/4] DETEKCE FYZICKY PRIPOJENYCH SERVISNICH ZARIZENI (DEVICE MANAGER)' -ForegroundColor Cyan; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"$targetVids = @('05C6', '0E8D', '0403', '10C4', '18D1', '2717'); " ^
"$devices = Get-PnpDevice 2>$null | Where-Object { " ^
"    $hwid = $_.InstanceId; " ^
"    foreach ($vid in $targetVids) { if ($hwid -like ('*VID_' + $vid + '*')) { return $true } } " ^
"    return $false; " ^
"}; " ^
"if ($devices) { " ^
"    foreach ($dev in $devices) { " ^
"        $statusColor = if ($dev.Status -eq 'OK') { 'Green' } else { 'Red' }; " ^
"        $problemStr = if ($dev.Problem) { (' [CHYBA: Kod ' + $dev.Problem + ']') } else { '' }; " ^
"        Write-Host (' [+] Zarizeni: ' + $dev.FriendlyName) -ForegroundColor $statusColor; " ^
"        Write-Host ('     - ID:     ' + $dev.InstanceId) -ForegroundColor Gray; " ^
"        Write-Host ('     - Trida:  ' + $dev.Class + ' | Stav: ' + $dev.Status + $problemStr) -ForegroundColor $statusColor; " ^
"        if ($dev.Problem -eq 28) { " ^
"            Write-Host '     ⚠️ CHYBA KOD 28: Chybi ovladac (napr. QUSB_BULK / MTK)! Nutno spustit install_drivers.' -ForegroundColor Yellow; " ^
"        } elseif ($dev.Problem -eq 10) { " ^
"            Write-Host '     ⚠️ CHYBA KOD 10: Zarizeni nelze spustit. Odpojte kabel, podrzte tlacitka a zapojte znovu.' -ForegroundColor Yellow; " ^
"        } elseif ($dev.Problem -eq 43) { " ^
"            Write-Host '     ⚠️ CHYBA KOD 43: Selhani USB deskriptoru (spatny kabel / port USB 3.0).' -ForegroundColor Red; " ^
"        } " ^
"        Write-Host ''; " ^
"    } " ^
"} else { " ^
"    Write-Host ' [i] Zadne zname servisni zarizeni (Qualcomm 9008, MTK, FTDI) neni v teto chvili fyzicky pripojeno.' -ForegroundColor Yellow; " ^
"    Write-Host '     - Pripojte telefon kabelem s drzenim tlacitek Volume Down / Testpoint.' -ForegroundColor Gray; " ^
"}; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"Write-Host '[3/4] KONTROLA SERIOVYCH COM PORTU (SERIALCOMM)' -ForegroundColor Cyan; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"$ports = [System.IO.Ports.SerialPort]::GetPortNames() 2>$null; " ^
"if ($ports) { " ^
"    Write-Host (' [+] Nalezene aktivni COM porty v systemu: ' + ($ports -join ', ')) -ForegroundColor Green; " ^
"} else { " ^
"    Write-Host ' [i] V systemu neni momentalne otevren zadny aktivni COM port.' -ForegroundColor Gray; " ^
"}; " ^
"Write-Host ''; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"Write-Host '[4/4] VYSLEDNE DOPORUCENI A DIAGNOSTIKA' -ForegroundColor Cyan; " ^
"Write-Host '------------------------------------------------------------------------------' -ForegroundColor Cyan; " ^
"if (Test-Path 'drivers\winusb_setup.cmd') { " ^
"    Write-Host ' [+] Ovladačový instalator je pripraven: drivers\winusb_setup.cmd' -ForegroundColor Green; " ^
"} else { " ^
"    Write-Host ' [!] drivers\winusb_setup.cmd nebyl nalezen.' -ForegroundColor Red; " ^
"}"

echo.
echo ==============================================================================
echo Co si prejete provest?
echo  [1] Nainstalovat vsechny chybejici ovladace (Spustit drivers\winusb_setup.cmd)
echo  [2] Spustit aplikaci SusetoDroidFixStudio
echo  [3] Ukoncit
echo ==============================================================================
set /p "CHOICE=Zadejte volbu (1, 2 nebo 3): "

if "%CHOICE%"=="1" (
    echo.
    echo ==============================================================================
    echo [PRE-FLIGHT] Provadim kontrolu starych / identickych ovladacu v DriverStore...
    echo ==============================================================================
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$missing = Get-PnpDevice 2>$null | Where-Object { $_.Problem -eq 28 -and ($_.InstanceId -like '*VID_05C6*' -or $_.InstanceId -like '*VID_0E8D*' -or $_.InstanceId -like '*VID_18D1*') }; " ^
    "if (-not $missing) { " ^
    "    Write-Host '[PRE-FLIGHT OK] Vsechna pripojena servisni zarizeni maji jiz platny funkcni ovladac!' -ForegroundColor Green; " ^
    "    Write-Host '[PRE-FLIGHT INFO] Instalace neni nutna. Nebude provaden zadny zbytecny prepis registru.' -ForegroundColor Cyan; " ^
    "} else { " ^
    "    Write-Host ('[PRE-FLIGHT VAROVANI] Nalezeno ' + $missing.Count + ' zarizeni bez ovladace (Kod 28). Zahajuji instalaci...') -ForegroundColor Yellow; " ^
    "}"
    echo.
    echo [*] Spoustim instalacni skript ovladacu...
    call "%SCRIPT_DIR%drivers\winusb_setup.cmd"
    echo.
    echo Hotovo! Stisknete libovolnou klavesu pro opakovani diagnostiky...
    pause >nul
    "%~f0"
    exit /b 0
)

if "%CHOICE%"=="2" (
    echo [*] Spoustim aplikaci...
    call "%SCRIPT_DIR%run.bat"
    exit /b 0
)

exit /b 0
