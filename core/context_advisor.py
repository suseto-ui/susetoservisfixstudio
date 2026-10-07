"""
Context-Aware Technician Diagnostic & Repair Advisor Engine for SusetoDroidFixStudio.
Analyzes connected device state, SoC descriptors, and hardware symptoms to generate
actionable step-by-step guidance formatted with IF (Pokud) / WHAT (Co udělat) / WHY (Proč).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger("context_advisor")


class SafetyRating(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    CRITICAL_INTERLOCK = "CRITICAL_INTERLOCK"


@dataclass
class AdvisorStep:
    """Represents a single actionable step in the diagnostic/repair workflow."""
    step_number: int
    total_steps: int
    title: str
    condition_if: str
    action_what: str
    rationale_why: str
    action_id: str
    safety_rating: SafetyRating
    estimated_duration_sec: int = 5
    is_completed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "total_steps": self.total_steps,
            "title": self.title,
            "condition_if": self.condition_if,
            "action_what": self.action_what,
            "rationale_why": self.rationale_why,
            "action_id": self.action_id,
            "safety_rating": self.safety_rating.value,
            "estimated_duration_sec": self.estimated_duration_sec,
            "is_completed": self.is_completed,
        }


class DeviceStateProfiler:
    """
    Evaluates raw device descriptors, VID/PID, port parameters, and memory signatures
    to categorize the hardware fault or diagnostic context.
    """

    @staticmethod
    def profile_device(
        vid: str,
        pid: str,
        port: str = "",
        mode: str = "",
        gpt_present: bool = True,
        frp_locked: bool = True,
    ) -> str:
        """Categorize device into a diagnostic state key."""
        vid_upper = vid.upper().replace("0X", "")
        pid_upper = pid.upper().replace("0X", "")

        if vid_upper == "05C6" or pid_upper == "9008" or "EDL" in mode.upper():
            return "QUALCOMM_EDL_BRICKED"

        if vid_upper == "0E8D" or pid_upper == "0003" or "BROM" in mode.upper():
            return "MTK_BROM_LOCKED"

        if vid_upper == "04E8" or "SAMSUNG" in mode.upper():
            return "SAMSUNG_MTP_FRP"

        if vid_upper == "1782" or "SPRD" in mode.upper() or "UNISOC" in mode.upper():
            return "UNISOC_BOOTLOADER_CORRUPT"

        if "FASTBOOT" in mode.upper():
            return "FASTBOOT_BOOTLOOP"

        return "GENERIC_UART_DIAG"


class ContextAdvisorEngine:
    """
    Generates tailored, step-by-step diagnostic workflows based on device profiling.
    """

    def __init__(self) -> None:
        self.active_diagnosis: Optional[str] = None
        self.steps: List[AdvisorStep] = []
        self.current_step_index: int = 0

    def analyze_and_plan(
        self,
        vid: str,
        pid: str,
        port: str = "",
        mode: str = "",
        gpt_present: bool = True,
        frp_locked: bool = True,
    ) -> List[AdvisorStep]:
        """Profile device and construct an IF / WHAT / WHY workflow."""
        diagnosis = DeviceStateProfiler.profile_device(vid, pid, port, mode, gpt_present, frp_locked)
        self.active_diagnosis = diagnosis
        self.steps = self._build_steps_for_diagnosis(diagnosis)
        self.current_step_index = 0
        logger.info("Generated %d advisor steps for diagnosis: %s", len(self.steps), diagnosis)
        return self.steps

    def _build_steps_for_diagnosis(self, diagnosis: str) -> List[AdvisorStep]:
        if diagnosis == "QUALCOMM_EDL_BRICKED":
            return [
                AdvisorStep(
                    step_number=1,
                    total_steps=3,
                    title="Sahara Handshake & Firehose Loader Sync",
                    condition_if="Zařízení je v nouzovém režimu Emergency Download (EDL 9008) a nekomunikuje se systémem.",
                    action_what="Ověřit odezvu protokolu Sahara a odeslat podepsaný Firehose programátor (.mbn/.elf).",
                    rationale_why="Primární bootloader (XBL) selhal nebo je poškozen. Procesor Qualcomm vyžaduje nahrání RAM loaderu pro odemčení přístupu k UFS/eMMC paměti.",
                    action_id="EXEC_SAHARA_FIREHOSE",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=3,
                ),
                AdvisorStep(
                    step_number=2,
                    total_steps=3,
                    title="Záloha GPT oddílů & Bezpečnostní audit",
                    condition_if="Firehose loader je aktivní v paměti RAM a paměťové médium odpovídá na sektorové dotazy.",
                    action_what="Vyčíst a uložit kontrolní zálohu primární GPT tabulky (LBA 0..33) do složky backups/gpt_backup.bin.",
                    rationale_why="Před jakýmkoliv zásahem do oddílů je nezbytné mít přesný otisk LBA sektorů pro okamžitou rekonstrukci při neočekávaném přerušení.",
                    action_id="EXEC_BACKUP_GPT",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=2,
                ),
                AdvisorStep(
                    step_number=3,
                    total_steps=3,
                    title="1-Click FRP Unlock & Flash Oprava",
                    condition_if="Zařízení je chráněno FRP zámkem nebo má poškozený boot oddíl.",
                    action_what="Provést cílený výmaz FRP persistentního sektoru (LBA 148480..150527) s aktivovanou pojistkou Bootloader Interlock.",
                    rationale_why="Fyzické přepsání nulovým vzorem (0x00) v persistentním bloku odstraní autentizační token Google účtu bez rizika poškození uživatelských dat.",
                    action_id="EXEC_FRP_UNLOCK",
                    safety_rating=SafetyRating.CAUTION,
                    estimated_duration_sec=5,
                ),
            ]

        elif diagnosis == "MTK_BROM_LOCKED":
            return [
                AdvisorStep(
                    step_number=1,
                    total_steps=3,
                    title="BROM DAA & SLA Bypass Handshake",
                    condition_if="Zařízení MediaTek je připojeno v režimu BootROM a vyžaduje autorizační klíč.",
                    action_what="Odeslat synchronizační sekvenci 0xA0 0x0A 0x50 0x05 a obejít hardwarovou ochranu DAA/SLA.",
                    rationale_why="Moderní procesory Dimensity/Helio blokují čtení/zápis paměti bez autorizovaného DA loaderu nebo exploitového bypassu.",
                    action_id="EXEC_MTK_BYPASS",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=4,
                ),
                AdvisorStep(
                    step_number=2,
                    total_steps=3,
                    title="Povinná záloha NVRAM / NVDATA kalibrace",
                    condition_if="BootROM bypass je úspěšný a sběrnice má plný přístup k eMMC/UFS.",
                    action_what="Stáhnout a verifikovat oddíly 'nvram' a 'nvdata' s výpočtem SHA-256 hashe.",
                    rationale_why="Oddíl NVRAM obsahuje unikátní tovární kalibrace rádiové části (RF) a IMEI. Ztráta těchto dat vede k trvalému znefunkčnění GSM modemu.",
                    action_id="EXEC_BACKUP_NVRAM",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=6,
                ),
                AdvisorStep(
                    step_number=3,
                    total_steps=3,
                    title="Servisní výmaz FRP zámku",
                    condition_if="Záloha NVRAM je ověřena a uložena v lokálním ledgeru.",
                    action_what="Vynulovat adresní rozsah 0x02D88000 (Délka: 1 MB) na oddílu 'frp'.",
                    rationale_why="MediaTek architektura ukládá stav zámku do dedikovaného oddílu. Po jeho vyčištění naběhne systém do stavu prvního spuštění.",
                    action_id="EXEC_FRP_UNLOCK",
                    safety_rating=SafetyRating.CAUTION,
                    estimated_duration_sec=4,
                ),
            ]

        elif diagnosis == "SAMSUNG_MTP_FRP":
            return [
                AdvisorStep(
                    step_number=1,
                    total_steps=2,
                    title="Aktivace servisního režimu Modem AT (*#0*#)",
                    condition_if="Telefon Samsung je v běžném MTP režimu na uvítací obrazovce.",
                    action_what="Vytočit na číselníku tísňového volání kód *#0*# a odeslat AT příkaz pro inicializaci testovacího módu.",
                    rationale_why="Testovací režim zpřístupní USB ladění (ADB Bridge) bez nutnosti odemykat bootloader nebo rozebírat zařízení.",
                    action_id="EXEC_SAMSUNG_AT_ENABLE",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=3,
                ),
                AdvisorStep(
                    step_number=2,
                    total_steps=2,
                    title="ADB FRP Bypass & Odeslání aktivačního tokenu",
                    condition_if="USB ladění je na zařízení povoleno a klíč RSA byl schválen.",
                    action_what="Odeslat příkaz pro odstranění Setup Wizard lock aktivity a restartovat zařízení.",
                    rationale_why="Umožní okamžité přeskočení úvodního průvodce bez narušení bezpečnostního stavu Knox (0x0).",
                    action_id="EXEC_SAMSUNG_ADB_BYPASS",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=2,
                ),
            ]

        else:
            return [
                AdvisorStep(
                    step_number=1,
                    total_steps=2,
                    title="Auto-Negotiate Baudrate & RTT Test",
                    condition_if="Zařízení je připojeno na neznámém sériovém nebo USB portu.",
                    action_what="Spustit automatické vyjednání přenosové rychlosti (9600 až 3 MBaud) a otestovat latenci linky.",
                    rationale_why="Správně nastavená parita a baudrate zabraňuje chybám rámců (Framing Errors) a ztrátám paketů.",
                    action_id="EXEC_AUTO_NEGOTIATE",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=2,
                ),
                AdvisorStep(
                    step_number=2,
                    total_steps=2,
                    title="Čtení systémových deskriptorů & GPT",
                    condition_if="Sériová linka je synchronizována a odezva je stabilní.",
                    action_what="Vyčíst identifikátory procesoru, velikost paměti a strukturu tabulky oddílů.",
                    rationale_why="Poskytne kompletní přehled o stavu hardwaru pro volbu dalšího servisního postupu.",
                    action_id="EXEC_READ_INFO",
                    safety_rating=SafetyRating.SAFE,
                    estimated_duration_sec=3,
                ),
            ]

    def get_current_step(self) -> Optional[AdvisorStep]:
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None

    def advance_step(self) -> Optional[AdvisorStep]:
        if self.current_step_index < len(self.steps):
            self.steps[self.current_step_index].is_completed = True
            self.current_step_index += 1
        return self.get_current_step()

    def previous_step(self) -> Optional[AdvisorStep]:
        if self.current_step_index > 0:
            self.current_step_index -= 1
        return self.get_current_step()
