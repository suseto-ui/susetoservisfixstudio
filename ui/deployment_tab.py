from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from ui._qt_compat import (
    Qt,
    QTimer,
    QColor,
    QFont,
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DeploymentTabWidget(QWidget):
    """
    Deployment Readiness Tab for PySide6 Cyber Cockpit.
    Audits build readiness: PyInstaller, Inno Setup compiler, native hardware drivers,
    SQLite WAL schema, and CLI binaries. Also hosts the interactive Windows Build & Run Guide.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.root_dir = Path(__file__).resolve().parent.parent
        self.setup_ui()
        self.run_audit()

    def setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Title / Header
        header_layout = QHBoxLayout()
        title_label = QLabel("Deployment & Production Readiness Center")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00FFCC;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("Spustit audit (Run Audit)")
        self.refresh_btn.setStyleSheet(
            "background-color: #00FFCC; color: #111111; font-weight: bold; padding: 8px 16px; border-radius: 4px;"
        )
        self.refresh_btn.clicked.connect(self.run_audit)
        header_layout.addWidget(self.refresh_btn)

        self.build_btn = QPushButton("Sestavit do .EXE (Build)")
        self.build_btn.setStyleSheet(
            "background-color: #333333; color: #00FFCC; font-weight: bold; padding: 8px 16px; border: 1px solid #00FFCC; border-radius: 4px;"
        )
        self.build_btn.clicked.connect(self.trigger_build)
        header_layout.addWidget(self.build_btn)

        self.installer_btn = QPushButton("Vytvořit instalátor (Setup.exe / ZIP)")
        self.installer_btn.setStyleSheet(
            "background-color: #00FFCC; color: #111111; font-weight: bold; padding: 8px 16px; border: 1px solid #00FFCC; border-radius: 4px;"
        )
        self.installer_btn.clicked.connect(self.trigger_installer)
        header_layout.addWidget(self.installer_btn)

        self.usb_doctor_btn = QPushButton("USB & Driver Doctor")
        self.usb_doctor_btn.setStyleSheet(
            "background-color: #225555; color: #00FFCC; font-weight: bold; padding: 8px 16px; border: 1px solid #00FFCC; border-radius: 4px;"
        )
        self.usb_doctor_btn.clicked.connect(self.trigger_usb_doctor)
        header_layout.addWidget(self.usb_doctor_btn)

        self.pipeline_btn = QPushButton("Master Pipeline (Vše v 1)")
        self.pipeline_btn.setStyleSheet(
            "background-color: #1a3a3a; color: #00FFCC; font-weight: bold; padding: 8px 16px; border: 1px solid #00FFCC; border-radius: 4px;"
        )
        self.pipeline_btn.clicked.connect(self.trigger_pipeline)
        header_layout.addWidget(self.pipeline_btn)

        main_layout.addLayout(header_layout)

        # Status Cards Group
        audit_group = QGroupBox("Stav připravenosti nástrojů a ovladačů (Toolchain & Drivers)")
        audit_group.setStyleSheet(
            "QGroupBox { color: #FFFFFF; font-weight: bold; font-size: 13px; border: 1px solid #333333; border-radius: 8px; margin-top: 6px; padding-top: 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; }"
        )
        audit_layout = QVBoxLayout(audit_group)
        self.indicators_layout = QVBoxLayout()
        self.indicators_layout.setSpacing(6)
        audit_layout.addLayout(self.indicators_layout)
        main_layout.addWidget(audit_group)

        # Windows Build & Run Guide Group
        guide_group = QGroupBox("Průvodce sestavením a spuštěním pro Windows (1-Click Guide)")
        guide_group.setStyleSheet(
            "QGroupBox { color: #00FFCC; font-weight: bold; font-size: 13px; border: 1px solid #00FFCC; border-radius: 8px; margin-top: 6px; padding-top: 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; }"
        )
        guide_layout = QVBoxLayout(guide_group)

        self.guide_text = QTextEdit()
        self.guide_text.setReadOnly(True)
        self.guide_text.setStyleSheet(
            "background-color: #121818; color: #E0E0E0; font-family: monospace; font-size: 12px; border: 1px solid #224444; border-radius: 4px; padding: 6px;"
        )
        self._populate_guide_text()
        guide_layout.addWidget(self.guide_text)

        main_layout.addWidget(guide_group)

        # Audit Log / Report Area
        log_group = QGroupBox("Protokol o sestavení a diagnostika (Build & Execution Log)")
        log_group.setStyleSheet(
            "QGroupBox { color: #FFFFFF; font-weight: bold; font-size: 13px; border: 1px solid #333333; border-radius: 8px; margin-top: 6px; padding-top: 12px; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 15px; padding: 0 5px; }"
        )
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(
            "background-color: #0D0D0D; color: #00FFCC; font-family: monospace; font-size: 12px; border: 1px solid #222222; border-radius: 4px; padding: 6px;"
        )
        log_layout.addWidget(self.log_text)

        main_layout.addWidget(log_group)

    def _populate_guide_text(self) -> None:
        guide_content = (
            "========================================================================================\n"
            "   JEDNOKLIKOVÁ INSTALACE A SPUŠTĚNÍ NA WINDOWS (2 HLAVNÍ SKRIPTY)                     \n"
            "========================================================================================\n\n"
            "1. ⭐ AUTOMATICKÁ INSTALACE DO C:\\SusetoFix (DOPORUČENO):\n"
            "   -> Dvakrát klikněte na soubor: Auto-Install.bat\n"
            "   * Sestaví samostatný .exe a nainstaluje jej do krátké cesty C:\\SusetoFix.\n"
            "   * Zcela eliminuje chyby Windows s limitem 260 znaků (MAX_PATH).\n"
            "   * Zaregistruje ovladače (FTDI, CP210x, WinUSB), vytvoří ikonu na ploše a spustí app.\n\n"
            "2. ⚡ RYCHLÉ SPUŠTĚNÍ PRO VÝVOJ ZE ZDROJOVÝCH KÓDŮ:\n"
            "   -> Dvakrát klikněte na soubor: Run.bat\n"
            "   * Vytvoří / aktivuje virtuální prostředí .venv a spustí přímo main.py.\n\n"
            "3. 🔧 INSTALACE OVLADAČŮ PRO HARDWARE SERVIS:\n"
            "   * Qualcomm Snapdragon EDL 9008 (VID 05C6, PID 9008) -> ovladač QDLoader 9008\n"
            "   * MediaTek MTK BROM (VID 0E8D, PID 0003)            -> ovladač MTK USB Port\n"
            "   * Registrace WinUSB ovladačů -> drivers\\winusb_setup.cmd\n\n"
            "Kompletní manuál a řešení potíží: WINDOWS_SETUP_GUIDE.md nebo README.md\n"
            "========================================================================================"
        )
        self.guide_text.setPlainText(guide_content)

    def run_audit(self) -> None:
        # Clear existing indicator widgets
        while self.indicators_layout.count():
            item = self.indicators_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        checks = [
            self.check_pyinstaller(),
            self.check_inno_setup(),
            self.check_native_drivers(),
            self.check_sqlite_schema(),
            self.check_cli_binaries(),
        ]

        log_lines = []
        log_lines.append("=== SUSETO DROID FIX STUDIO DEPLOYMENT AUDIT ===")
        log_lines.append(f"Root Directory: {self.root_dir}")
        log_lines.append(f"Python Version: {sys.version.split()[0]}")
        log_lines.append("-" * 50)

        all_passed = True
        for name, passed, details in checks:
            status_text = "[OK] PRESENT / READY" if passed else "[!] MISSING / NOT FOUND"
            color = "#00FFCC" if passed else "#FF4444"
            symbol = "✔" if passed else "✘"

            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(5, 2, 5, 2)

            badge_lbl = QLabel(f" {symbol} ")
            badge_lbl.setStyleSheet(
                f"background-color: {color}; color: #000000; font-weight: bold; border-radius: 3px; padding: 2px 6px;"
            )
            row_layout.addWidget(badge_lbl)

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
            row_layout.addWidget(name_lbl)

            row_layout.addStretch()

            det_lbl = QLabel(details)
            det_lbl.setStyleSheet(f"color: {color}; font-size: 12px;")
            row_layout.addWidget(det_lbl)

            self.indicators_layout.addWidget(row_widget)

            log_lines.append(f"Component: {name} -> {status_text} ({details})")
            if not passed:
                all_passed = False

        log_lines.append("-" * 50)
        if all_passed:
            log_lines.append("[SUCCESS] All core deployment prerequisites are satisfied!")
        else:
            log_lines.append("[INFO] Follow WINDOWS_SETUP_GUIDE.md or click 1-Click scripts to configure.")

        self.log_text.setPlainText("\n".join(log_lines))

    def check_pyinstaller(self) -> tuple[str, bool, str]:
        pyi = shutil.which("pyinstaller")
        if pyi:
            return ("PyInstaller Build Engine", True, f"Found at {pyi}")
        try:
            import PyInstaller  # type: ignore
            return ("PyInstaller Build Engine", True, f"Python module installed ({PyInstaller.__version__})")
        except ImportError:
            return ("PyInstaller Build Engine", False, "Module not found (pip install pyinstaller)")

    def check_inno_setup(self) -> tuple[str, bool, str]:
        iscc = shutil.which("ISCC") or shutil.which("iscc")
        if not iscc and sys.platform.startswith("win"):
            possible = [
                Path("C:/Program Files (x86)/Inno Setup 6/ISCC.exe"),
                Path("C:/Program Files/Inno Setup 6/ISCC.exe"),
            ]
            for p in possible:
                if p.exists():
                    iscc = str(p)
                    break
        if iscc:
            return ("Inno Setup Compiler (ISCC.exe)", True, f"Found at {iscc}")
        return ("Inno Setup Compiler (ISCC.exe)", False, "ISCC.exe not found (instalujte Inno Setup 6)")

    def check_native_drivers(self) -> tuple[str, bool, str]:
        drivers_dir = self.root_dir / "drivers"
        required = ["ftd2xx64.dll", "silabser64.dll", "winusb_setup.cmd"]
        missing = [f for f in required if not (drivers_dir / f).exists()]
        if not missing:
            return ("Nativní ovladače (FTDI / CP210x / WinUSB)", True, "Všechny DLL a skripty přítomny v drivers/")
        return ("Nativní ovladače (FTDI / CP210x / WinUSB)", False, f"Chybí: {', '.join(missing)}")

    def check_sqlite_schema(self) -> tuple[str, bool, str]:
        schema = self.root_dir / "db" / "schema.sql"
        if schema.exists():
            return ("SQLite WAL Schéma (db/schema.sql)", True, f"Nalezeno v {schema.relative_to(self.root_dir)}")
        return ("SQLite WAL Schéma (db/schema.sql)", False, "schema.sql chybí")

    def check_cli_binaries(self) -> tuple[str, bool, str]:
        adb = self.root_dir / "bin" / ("adb.exe" if sys.platform.startswith("win") else "adb")
        fastboot = self.root_dir / "bin" / ("fastboot.exe" if sys.platform.startswith("win") else "fastboot")
        if adb.exists() and fastboot.exists():
            return ("ADB & Fastboot CLI Nástroje", True, "Připraveno v bin/")
        return ("ADB & Fastboot CLI Nástroje", False, "Binárky chybí v bin/")

    def trigger_build(self) -> None:
        self.log_text.append("\n[INFO] Spouštím produkční build skript (production_build.py)...")
        try:
            script = self.root_dir / "production_build.py"
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
            self.log_text.append(result.stdout)
            if result.stderr:
                self.log_text.append(result.stderr)
            if result.returncode == 0:
                self.log_text.append("[SUCCESS] Produkční build dokončen! Výstup: dist/SusetoDroidFixStudio/")
            else:
                self.log_text.append(f"[ERROR] Build selhal s kódem {result.returncode}")
        except Exception as err:
            self.log_text.append(f"[ERROR] Selhání spuštění buildu: {err}")

    def trigger_pipeline(self) -> None:
        self.log_text.append("\n[INFO] Spouštím kompletní Master Automation Pipeline (run_master_pipeline.py)...")
        try:
            script = self.root_dir / "run_master_pipeline.py"
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
            self.log_text.append(result.stdout)
            if result.stderr:
                self.log_text.append(result.stderr)
            if result.returncode == 0:
                self.log_text.append("[SUCCESS] Master pipeline úspěšně proběhl (100% testů prošlo, dist i verify OK)!")
            else:
                self.log_text.append(f"[ERROR] Pipeline selhal s kódem {result.returncode}")
        except Exception as err:
            self.log_text.append(f"[ERROR] Selhání spuštění pipeline: {err}")

    def trigger_installer(self) -> None:
        self.log_text.append("\n[INFO] Spouštím generátor finálního instalátoru (build_master_installer.py)...")
        try:
            script = self.root_dir / "build_master_installer.py"
            result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
            self.log_text.append(result.stdout)
            if result.stderr:
                self.log_text.append(result.stderr)
            if result.returncode == 0:
                self.log_text.append("[SUCCESS] Finální instalační balíček vytvořen ve složce Output/!")
            else:
                self.log_text.append(f"[ERROR] Tvorba instalátoru selhala s kódem {result.returncode}")
        except Exception as err:
            self.log_text.append(f"[ERROR] Selhání spuštění master instalátoru: {err}")

    def trigger_usb_doctor(self) -> None:
        self.log_text.append("\n[INFO] Spouštím hloubkovou diagnostiku USB portů a ovladačů (usb_doctor.py)...")
        try:
            from usb_doctor import USBDoctor
            doctor = USBDoctor()
            report = doctor.run_full_diagnosis()

            self.log_text.append(f"[*] Operační systém: {report['platform']}")
            self.log_text.append(f"[*] Nalezeno COM/USB portů: {report['total_ports_detected']}")
            for p in report["ports"]:
                acc = "DOSTUPNÝ" if p["is_accessible"] else f"BLOKOVÁN ({p['lock_reason']})"
                chipset = f"-> {p['chipset']}" if p["chipset"] else ""
                self.log_text.append(f"    - {p['device']}: {p['description']} [{p['vid']}:{p['pid']}] [{acc}] {chipset}")

            self.log_text.append("\n--- ROOT-CAUSE ANALÝZA NEFUNKČNOSTI A DOPORUČENÁ ŘEŠENÍ ---")
            for f in report["findings"]:
                self.log_text.append(f"[{f['severity']}] {f['title']}")
                self.log_text.append(f"  Popis:  {f['description']}")
                self.log_text.append(f"  Řešení: 👉 {f['fix']}\n")

            self.log_text.append("[SUCCESS] USB & Driver Doctor diagnostika úspěšně dokončena!")
        except Exception as err:
            self.log_text.append(f"[ERROR] Diagnostika USB selhala: {err}")


