# 🛠️ Návod k sestavení a spuštění na Windows (Windows Setup & Build Guide)

> **SusetoDroidFixStudio & EUDCP Enterprise Suite**  
> Diagnostický, servisní a flashovací kokpit pro mobilní zařízení (Qualcomm EDL 9008, MediaTek MTK BROM, Fastboot, ADB).

---

## ⚡ Rychlý přehled (1-klikové skripty pro Windows)

Pro Windows jsou k dispozici jednoklikové skripty:

| Soubor | Účel |
|---|---|
| **`build_complete_installer.bat`** | **⭐ 1-KLIK PRO VYTVOŘENÍ INSTALÁTORU**: Jedním kliknutím zkompiluje standalone `.exe`, přibalí ovladače a vygeneruje kompletní instalační balíček (`SusetoFix_Setup.exe` nebo přenosný instalátor) do složky `Output\` a rovnou ji otevře. |
| **`run_windows.bat`** | **⚡ 1-KLIK PRO SPUŠTĚNÍ**: Automaticky připraví virtuální prostředí, nainstaluje knihovny z `requirements.txt` a rovnou spustí aplikaci. |
| **`compile_installer.bat`** | **📦 KOMPILACE INNO SETUP**: Zkompiluje instalační průvodce Inno Setup 6. |
| **`build_windows_exe.bat`** | **🔨 KOMPILACE PYINSTALLER**: Samostatná kompilace do `dist/SusetoDroidFixStudio`. |

---

## 1. Požadavky na systém (Prerequisites)

Před prvním spuštěním ověřte, že máte nainstalováno:

1. **Python 3.10, 3.11 nebo 3.12 (64-bit)**
   - Stáhněte z oficiálního webu: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - ⚠️ **KRITICKY DŮLEŽITÉ:** Při instalaci hned na první obrazovce **zaškrtněte volbu `Add python.exe to PATH`**!
2. **Microsoft Visual C++ Redistributable (x64)**
   - Většina systémů Windows 10/11 jej již má. Pokud ne, stáhněte z [Microsoft C++ Runtime](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

## 2. Proč instalace do `C:\SusetoFix`? (Ochrana před chybou MAX_PATH)

Operační systém Windows standardně omezuje délku cest k souborům na **260 znaků** (`MAX_PATH`).
Při rozbalování hlubokých archivů (např. ve složkách uživatele `C:\Users\Jmeno\Downloads\DlouhaSlozka\...`) dochází k selhání extrakce souborů.

Proto náš instalátor **`Auto-Install.bat`** instaluje program přímo do krátké cesty:
```
C:\SusetoFix
```
- Celková délka cesty k programu je pouhých **37 znaků** (`C:\SusetoFix\SusetoDroidFixStudio.exe`).
- Zabraňuje 100 % chyb při rozbalování a zajišťuje bleskové načítání souborů.

---

## 3. Instalace ovladačů pro servisní režimy (Drivers Guide)

Pro komunikaci s hardwarovými čipy je potřeba mít nainstalované příslušné ovladače:

1. **WinUSB a generické USB řadiče**:
   - Skript `Auto-Install.bat` provádí registraci automaticky.
   - Manuálně můžete spustit jako Správce: `drivers\winusb_setup.cmd` (nebo `C:\SusetoFix\drivers\winusb_setup.cmd`).
2. **Qualcomm Snapdragon EDL režim (Emergency Download Mode - VID: 05C6, PID: 9008)**:
   - Po připojení telefonu s testpointem nebo EDL kabelem se ve Správci zařízení musí objevit:  
     `Qualcomm HS-USB QDLoader 9008 (COMx)`.
   - V aplikaci stačí kliknout na tlačítko **Scan Devices**.
3. **MediaTek MTK BROM režim (VID: 0E8D, PID: 0003)**:
   - Po připojení se zařízením ve stavu BROM se přihlásí `MediaTek USB Port (COMx)`.
4. **FTDI / CP210x převodníky**:
   - DLL knihovny `ftd2xx64.dll` a `silabser64.dll` jsou přibaleny přímo u aplikace v podsložce `drivers/`.

---

## 4. USB Doctor – Diagnostika portů a všech příčin nefunkčnosti

Pokud aplikace nedetekuje zařízení nebo komunikace selhává, spusťte diagnostický nástroj:
```powershell
python usb_doctor.py
```
*(nebo klikněte na tlačítko **USB & Driver Doctor** v záložce Deployment v aplikaci).*

### 🛑 6 nejčastějších příčin nefunkčnosti USB a jejich řešení:

1. **Pouze nabíjecí kabel (Charge-Only):**
   - *Příčina:* Kabel má zapojené pouze napájení (VBUS, GND), ale chybí datové vodiče (D+, D-). Telefon se nabíjí, ale v PC se neobjeví žádný port.
   - *Řešení:* Použijte originální kvalitní datový kabel do délky 1 m.
2. **Inkompatibilita USB 3.0 / 3.2 (xHCI modré porty):**
   - *Příčina:* Čipsety Qualcomm EDL (9008) a MediaTek BROM mají starší USB PHY řadič, který na moderních modrých USB 3.0 portech ztrácí synchronizaci (Sahara timeout / Firehose drop).
   - *Řešení:* Zapojte telefon výhradně do černého portu USB 2.0 (ideálně vzadu na základní desce). U notebooků pouze s USB 3.0 použijte pasivní USB 2.0 rozbočovač (HUB).
3. **Port je blokován (Access Denied):**
   - *Příčina:* K COM portu přistupuje jiný program (PuTTY, Cura, PrusaSlicer, Arduino IDE nebo visící proces ve Windows).
   - *Řešení:* Ukončete daný program nebo zkontrolujte procesy ve Správci úloh.
4. **Časové okno MediaTek BROM (Handshake Timeout):**
   - *Příčina:* MediaTek telefony zůstávají v režimu BootROM (BROM) pouze 1–2 sekundy po připojení.
   - *Řešení:* V aplikaci nejprve spusťte operaci a teprve poté připojte telefon s držením Volume Down.
5. **Chybějící ovladač (Žlutý vykřičník / Kód 28):**
   - *Příčina:* Windows nemají ovladač pro `QUSB_BULK` nebo `MTK USB Port`.
   - *Řešení:* Spusťte `drivers\winusb_setup.cmd` jako Správce nebo nainstalujte ovladač Qualcomm HS-USB QDLoader 9008.
6. **Vybitá baterie nebo špatný testpoint:**
   - *Příčina:* Pokud má baterie pod 3.3 V, zařízení se při pokusu o EDL handshake okamžitě vypne.
   - *Řešení:* Nabijte telefon externě nebo odpojte baterii a napájejte pouze přes USB s testpointem.

---

## 5. Řešení častých potíží (Troubleshooting)

| Příznak | Příčina | Řešení |
|---|---|---|
| `'python' is not recognized...` | Python není v systémové proměnné PATH | Přeinstalujte Python a **zaškrtněte 'Add python.exe to PATH'** na úvodní obrazovce instalátoru. |
| SmartScreen / Antivirus hlásí neznámý soubor | Vlastnoručně zkompilovaný .exe bez drahého certifikátu | Klikněte na **"Více informací"** (More info) a zvolte **"Přesto spustit"** (Run anyway). |
| Port COM hlásí `Access Denied` | Port je obsazen jiným programem | Ukončete aplikace jako PuTTY, Cura, Arduino IDE nebo starší běžící instanci ve Správci úloh. |
| Chyba při extrakci ZIP archivu | Příliš dlouhá cesta ve Windows | Použijte `Auto-Install.bat`, který extrahuje do krátké cesty `C:\SusetoFix`. |

---

## 6. Ověření funkčnosti (Test Suite)

Celý projekt obsahuje **89 automatizovaných testů** pokrývajících šifrování, protokoly Sahara/Firehose, MTK BROM, GPT tabulky, SQLite WAL žurnál, USB Doctor diagnostiku a GUI signály.

Testy spustíte příkazem:
```powershell
python run_master_pipeline.py
```
Všech 89 testů prochází se stavem `[SUCCESS]`.

