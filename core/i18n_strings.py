"""
Centralized Internationalization, Error Translation & UX Copywriting Engine for SusetoDroidFixStudio.
Translates low-level hardware error codes (Sahara NAK, BROM Timeout, WinUSB Code 28)
into actionable technician remediation steps in Czech and English.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("i18n_strings")


STRINGS: Dict[str, Dict[str, str]] = {
    # General App Titles & Navigation
    "app_title": {
        "cs": "SusetoDroidFixStudio v1.0-PROD | Servisní a diagnostický cockpit",
        "en": "SusetoDroidFixStudio v1.0-PROD | Hardware Servicing Cockpit",
    },
    "tab_overview": {
        "cs": "PŘEHLED A COCKPIT",
        "en": "OVERVIEW & COCKPIT",
    },
    "tab_frp": {
        "cs": "1-CLICK FRP & UNBRICK",
        "en": "1-CLICK FRP & UNBRICK",
    },
    "tab_partitions": {
        "cs": "SPRÁVCE ODDÍLŮ & HEX",
        "en": "PARTITION MANAGER & HEX",
    },
    "tab_cloud": {
        "cs": "CLOUDOVÉ LOADERY & TUNEL",
        "en": "CLOUD LOADERS & TUNNEL",
    },
    "tab_dongle": {
        "cs": "SMARTCARD & BEZPEČNOST",
        "en": "SMARTCARD & SHIELD",
    },
    "tab_fleet": {
        "cs": "PODNIKOVÁ SPRÁVA PRACOVIŠŤ",
        "en": "ENTERPRISE FLEET & RBAC",
    },
    "tab_wal": {
        "cs": "SQLITE WAL TRANSANCE",
        "en": "SQLITE WAL LEDGER",
    },

    # Actions & Buttons
    "btn_scan_devices": {
        "cs": "Skenovat USB/COM porty",
        "en": "Scan USB/COM Ports",
    },
    "btn_execute_frp": {
        "cs": "⚡ Spustit 1-Click FRP výmaz",
        "en": "⚡ Execute 1-Click FRP Wipe",
    },
    "btn_backup_gpt": {
        "cs": "Zálohovat GPT hlavičku",
        "en": "Backup GPT Header",
    },
    "btn_export_dump": {
        "cs": "Exportovat .bin dump",
        "en": "Export .bin Dump",
    },
    "btn_auth_dongle": {
        "cs": "⚡ Autentizovat SmartCard",
        "en": "⚡ Authenticate SmartCard",
    },
    "btn_ship_audit": {
        "cs": "⚡ Odeslat auditní logy (mTLS)",
        "en": "⚡ Ship Audit Logs (mTLS)",
    },
    "btn_cancel": {
        "cs": "Zrušit operaci",
        "en": "Cancel Operation",
    },

    # Tooltips
    "tip_baudrate_autotune": {
        "cs": "Automaticky otestuje a nastaví nejvyšší stabilní rychlost sériového rozhraní (až 3 MBaud) a změří latenci linky (RTT).",
        "en": "Automatically benchmarks and sets the highest stable serial baud rate (up to 3 MBaud) and measures round-trip latency.",
    },
    "tip_checksum_verify": {
        "cs": "Vypočítá a ověří SHA-256 kontrolní součet zapisovaného bloku pro zamezení poškození paměti.",
        "en": "Computes and validates the SHA-256 hash of written memory blocks to prevent data corruption.",
    },
    "tip_security_interlock": {
        "cs": "Hardwarová pojistka zabraňující neúmyslnému přepsání klíčových oddílů bootloaderu (preloader, xbl, tz).",
        "en": "Hardware safety interlock preventing unintended writes to critical bootloader partitions (preloader, xbl, tz).",
    },
    "tip_frp_zero_wipe": {
        "cs": "Bezpečně přepíše persistentní konfigurační bloky nulovými bajty (0x00) bez zásahu do uživatelských dat.",
        "en": "Safely zeroes persistent lock sectors with 0x00 bytes without modifying user data partitions.",
    },
    "tip_smartcard_dongle": {
        "cs": "Fyzický hardwarový klíč ISO 7816 / FTDI. Odemkne šifrované nízkoúrovňové algoritmy v operační paměti.",
        "en": "Physical ISO 7816 / FTDI hardware key. Unlocks encrypted low-level service algorithms in RAM.",
    },
}

# Structured low-level hardware error resolution table
ERROR_RESOLUTIONS: Dict[str, Dict[str, Any]] = {
    "ERR_SAHARA_NAK": {
        "code": "0x5A01",
        "title_cs": "Chyba protokolu Qualcomm Sahara (NAK Packet)",
        "title_en": "Qualcomm Sahara Protocol Error (NAK Packet)",
        "cause_cs": "Procesor Qualcomm odmítl odeslaný Firehose loader (.mbn). Kontrolní součet nebo certifikát loaderu neodpovídá hardwarovému klíči CPU.",
        "cause_en": "Qualcomm SoC rejected the Firehose loader (.mbn). Loader hash or OEM PKI certificate mismatch.",
        "steps_cs": [
            "Ověřte přesné označení procesoru (např. Snapdragon 888 vs 870).",
            "Otevřete Cloud Loaders a synchronizujte správnou verzi .mbn/.elf loaderu.",
            "Zkontrolujte, zda zařízení nevyžaduje autorizovaný OEM EDL podpis.",
        ],
        "steps_en": [
            "Verify the exact SoC part number (e.g., Snapdragon 888 vs 870).",
            "Open Cloud Loaders and download the matching .mbn/.elf programmer.",
            "Verify if device requires OEM authorization tokens.",
        ],
    },
    "ERR_BROM_TIMEOUT_A0": {
        "code": "0x5A02",
        "title_cs": "Vypršel časový limit MediaTek BROM (0xA0 Handshake Timeout)",
        "title_en": "MediaTek BROM Handshake Timeout (0xA0 Not Received)",
        "cause_cs": "Zařízení nebylo včas připojeno v režimu BootROM nebo nebyla držena servisní kombinace tlačítek hlasitosti.",
        "cause_en": "Device was not connected in BootROM mode or Volume buttons were released too early.",
        "steps_cs": [
            "Odpojte USB kabel a vyčkejte 5 sekund.",
            "Stiskněte a držte současně tlačítka Volume Up a Volume Down.",
            "Zasuňte USB kabel a držte tlačítka, dokud aplikace neohlásí navázání BROM spojení.",
        ],
        "steps_en": [
            "Disconnect USB cable and wait 5 seconds.",
            "Press and hold both Volume Up and Volume Down buttons.",
            "Insert USB cable and keep holding until BROM handshake is acknowledged.",
        ],
    },
    "ERR_WINUSB_CODE_28": {
        "code": "0x5A03",
        "title_cs": "Chybějící nebo neplatný ovladač USB zařízení (Kód 28)",
        "title_en": "Missing or Invalid USB Driver (Device Manager Code 28)",
        "cause_cs": "Systém Windows nerozpoznal zařízení v servisním režimu (Qualcomm 9008 nebo MTK VCP) kvůli chybějícímu .inf ovladači.",
        "cause_en": "Windows failed to bind drivers for service mode (Qualcomm 9008 or MTK VCP).",
        "steps_cs": [
            "V menu aplikace vyberte Nástroje -> Přeinstalovat WinUSB ovladače.",
            "Zkontrolujte správné přiřazení COM portu ve Správci zařízení.",
            "V případě potřeby dočasně zakažte vynucení digitálního podpisu ovladačů.",
        ],
        "steps_en": [
            "Select Tools -> Reinstall WinUSB Drivers in the application menu.",
            "Verify COM port assignment in Windows Device Manager.",
            "Ensure driver signature enforcement does not block the installation.",
        ],
    },
    "ERR_SECURITY_INTERLOCK": {
        "code": "0x5A04",
        "title_cs": "Zásah bezpečnostní pojistky (Chráněný bootloader)",
        "title_en": "Security Interlock Triggered (Protected Bootloader Partition)",
        "cause_cs": "Pokus o zápis do kritického oddílu (preloader, xbl, tz), jehož poškození by způsobilo trvalé znefunkčnění (hard-brick).",
        "cause_en": "Attempted write to critical bootloader partition that could cause an unrecoverable hard-brick.",
        "steps_cs": [
            "Zkontrolujte, zda byl vybrán správný cílový oddíl (např. boot_a místo xbl_a).",
            "Před jakoukoliv změnou vytvořte zálohu stávající GPT tabulky.",
            "K přepsání bootloaderu je nutné explicitní povolení v režimu Administrátor s parametrem Force.",
        ],
        "steps_en": [
            "Verify selected target partition (e.g., boot_a instead of xbl_a).",
            "Perform a full GPT backup prior to any modification.",
            "Overriding bootloader protection requires Administrator role and explicit Force approval.",
        ],
    },
    "ERR_PORT_ACCESS_DENIED": {
        "code": "0x5A05",
        "title_cs": "Přístup k sériovému portu odepřen (Port obsazen)",
        "title_en": "Serial Port Access Denied (Port In Use)",
        "cause_cs": "Požadovaný COM/USB port je blokován jiným běžícím programem nebo terminálem.",
        "cause_en": "Target COM/USB port is held open by another background process or terminal.",
        "steps_cs": [
            "Ukončete aplikace jako ModemManager, PuTTY, Cura nebo jiné servisní nástroje.",
            "Spusťte Anti-Debug / Process Scanner a prověřte konfliktní procesy.",
            "Znovu spusťte skenování portů.",
        ],
        "steps_en": [
            "Close conflicting apps such as ModemManager, PuTTY, 3D printing software, or other flasher tools.",
            "Run Anti-Debug / Process Scanner to audit active process handles.",
            "Rescan hardware ports.",
        ],
    },
}


class I18NManager:
    """
    Manages localization, translations, tooltips, and human-readable hardware error diagnostics.
    """

    def __init__(self, default_lang: str = "cs") -> None:
        self.current_lang = default_lang

    def set_language(self, lang: str) -> None:
        if lang in ("cs", "en"):
            self.current_lang = lang

    def get_text(self, key: str, fallback: Optional[str] = None) -> str:
        """Retrieve localized UI string by key."""
        entry = STRINGS.get(key)
        if entry:
            return entry.get(self.current_lang, entry.get("en", key))
        return fallback or key

    def get_tooltip(self, key: str) -> str:
        """Retrieve localized tooltip string."""
        return self.get_text(f"tip_{key}", fallback="")

    def resolve_error(self, error_key: str) -> Dict[str, Any]:
        """
        Translate low-level error code into structured, human-readable technician guidance.
        """
        err = ERROR_RESOLUTIONS.get(error_key)
        if not err:
            return {
                "code": "0x5A99",
                "title": f"Neznámá chyba hardware ({error_key})" if self.current_lang == "cs" else f"Unknown Hardware Error ({error_key})",
                "cause": "Došlo k neočekávané chybě komunikace." if self.current_lang == "cs" else "An unexpected communication error occurred.",
                "steps": ["Zkontrolujte připojení kabelu a opakujte operaci."] if self.current_lang == "cs" else ["Check cable connection and retry."],
            }

        lang = self.current_lang
        return {
            "code": err["code"],
            "title": err[f"title_{lang}"],
            "cause": err[f"cause_{lang}"],
            "steps": list(err[f"steps_{lang}"]),
        }
