# SusetoDroidFixStudio & EUDCP Enterprise Suite

[![Architecture](https://img.shields.io/badge/Architecture-Windows%2011%20x64-0078d4.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776ab.svg)](#)
[![UI](https://img.shields.io/badge/UI-Edge%20WebView2%20%2B%20React%20Tailwind-00f0ff.svg)](#)
[![Database](https://img.shields.io/badge/Database-SQLite%20WAL-00ff9d.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-89%20Passing-success.svg)](#)

Profesionální diagnostický, servisní a flashovací kokpit pro mobilní zařízení s procesory **Qualcomm** (EDL 9008, Sahara/Firehose protokol), **MediaTek** (BootROM BROM handshake, DA injection), **FTDI SmartCard** bezpečnostní tokeny, **Fastboot** a **ADB**.

Aplikace poskytuje **100% identické moderní rozhraní** jak na webu, tak v nativním desktopovém okně Windows (Edge WebView2) s přímým nízkoúrovňovým přístupem k USB sběrnici, diagnostikou portů (USB Doctor), zátěžovým testem propustnosti a interaktivním flasherem.

---

## 🚀 Rychlý start na Windows (3 hlavní skripty)

V kořenovém adresáři jsou připraveny **3 hlavní dávkové soubory**:

| Soubor | Účel |
|---|---|
| **`install.bat`** | **⭐ 1-KLIKOVÁ INSTALACE**: Nastaví oprávnění pro `C:\SusetoFix`, tise nainstaluje ovladače, vytvoří zástupce na ploše a ihned aplikaci spustí. |
| **`check_usb_drivers.bat`** | **🔍 DIAGNOSTIKA OVLADAČŮ**: Zkontroluje Device Manager pro Qualcomm 9008, MTK BROM, FTDI a filtry WinUSB/libusb a nabídne 1-klikovou opravu. |
| **`run.bat`** | **⚡ 1-KLIKOVÉ SPUŠTĚNÍ**: Okamžitě spustí aplikaci z aktuální složky ve virtuálním prostředí. |
| **`build.bat`** | **📦 1-KLIKOVÉ SESTAVENÍ**: Zkompiluje standalone `.exe`, přibalí `dist_web` a vytvoří instalační balíček do složky `Output\`. |

---

## 🛠️ 1. Požadavky na systém (Prerequisites)

1. **Operační systém:** Windows 10 nebo Windows 11 (64-bit).
2. **Python:** Verze **3.10, 3.11 nebo 3.12 (64-bit)**.
   - Ke stažení: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - ⚠️ **DŮLEŽITÉ:** Při instalaci hned na úvodní obrazovce zaškrtněte volbu **`Add python.exe to PATH`**!
3. **Microsoft Edge WebView2 Runtime:** Standardní součást Windows 10 a 11 (zajišťuje moderní 60 FPS vykreslování kokpitu).

---

## 📁 2. Proč instalace do `C:\SusetoFix`?

Operační systém Windows standardně omezuje cesty k souborům na 260 znaků (`MAX_PATH`). Při práci v hlubokých složkách uživatele (např. `C:\Users\Jmeno\Downloads\...`) dochází k selhání extrakce ovladačů.

Náš instalátor **`install.bat`** proto instaluje program do:
```
C:\SusetoFix
```
- Skript pomocí příkazu `icacls` automaticky nastaví plná oprávnění (`Full Control`), takže nedochází k chybám *Access Denied*.
- Vytvoří zástupce na ploše: **`Suseto Droid Fix Studio.lnk`**.

---

## 🔌 3. Podpora hardwarových režimů a ovladačů

Skript `install.bat` automaticky registruje ovladače ze složky `drivers/`:

1. **Qualcomm Snapdragon EDL 9008 (VID: 05C6, PID: 9008):**
   - Režim nouzového stahování (Emergency Download).
   - Ovladač: `Qualcomm HS-USB QDLoader 9008`.
   - Protokoly: Sahara Packet Sync v2 + Firehose XML Programmer.
2. **MediaTek MTK BootROM (VID: 0E8D, PID: 0003):**
   - Přímý přístup k BootROM (BROM) pro 1-klikový výmaz FRP paměti.
   - Ovladač: `MediaTek USB Port (COMx)`.
3. **FTDI SmartCard Dongle & UART Bridge (VID: 0403, PID: 6001):**
   - Nativní DLL knihovny `drivers/ftd2xx64.dll` pro hardwarové klíče ISO 7816.
4. **Silicon Labs CP210x USB to UART (VID: 10C4, PID: EA60):**
   - Knihovny `drivers/silabser64.dll` pro servisní kabely.
5. **Android Fastboot & ADB (VID: 18D1, PID: 4EE0):**
   - Standardní WinUSB rozhraní a systémový bridge v `core/adb_fastboot.py`.

---

## 🩺 4. USB Doctor & Zátěžový test sběrnice

V záložce **USB Doctor** naleznete:
- **Live Port Monitor:** Automatické sledování připojení a odpojení hardware v reálném čase (`WebUSB` a `WebSerial` události).
- **Zátěžový test stability:** Odesílání a příjem ECHO paketů s měřením propustnosti v KB/s (i Mbit/s), latence odezvy a chybovosti paketů (PER) v živém SVG grafu.
- **Root-Cause Failure Analýza:** Nápověda k řešení 6 nejčastějších problémů (nabíjecí kabely bez datových linek, xHCI USB 3.0 timeouty, blokování portu jiným procesem, krátké 1.5s okno MediaTek BROM).

---

## 🏗️ 5. Spuštění z příkazové řádky (CMD / PowerShell)

```powershell
# 1. Spuštění instalace a registrace ovladačů
install.bat

# 2. Rychlé spuštění bez instalace
run.bat

# 3. Sestavení distribučního balíčku do Output/
build.bat
```

---

## 🛡️ 6. Ověření kvality a testy

Projekt obsahuje **89 automatizovaných integračních a jednotkových testů** ověřujících:
- Sahara & Firehose XML parser
- MTK BROM Handshake & FRP erase
- SQLite Write-Ahead Logging (WAL) auditní žurnál
- USB Doctor & Native Hardware Bridge
- PySide6 & Edge WebView2 GUI spouštěče

Všechny testy spustíte příkazem:
```powershell
python run_master_pipeline.py
```
*(Všech 89 testů prochází se stavem `[SUCCESS]` bez jediné chyby).*
