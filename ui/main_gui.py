"""
DroidFixAutomator Unified Desktop GUI (`ui/main_gui.py`).
Features a high-tech Cyber Technician cockpit with real-time 4-step visual tracker:
  1. 🔌 Detekováno zařízení (VID/PID, Port)
  2. 🛠️ Ovladač v systému (SetupAPI / WinUSB)
  3. 🔍 Identifikace režimu (EDL / BROM / Fastboot / ADB / AT Modem)
  4. ⚡ Doporučená akce (1-Klik Spuštění)
Provides CustomTkinter as primary toolkit with automatic fallback to PySide6 / Tkinter.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("main_gui")

from core.device_auto_router import AutoRouterState, DeviceAutoRouter
from drivers.auto_driver_installer import AutoDriverInstaller
from core.screen_mirror_engine import ScreenMirrorEngine


class DroidFixAutomatorApp:
    """
    Unified Desktop GUI for DroidFixAutomator.
    """

    def __init__(self) -> None:
        self.router = DeviceAutoRouter()
        self.installer = AutoDriverInstaller()
        self.screen_mirror = ScreenMirrorEngine()
        self._step_status = {
            1: "Čeká na připojení USB kabelu...",
            2: "Připraveno",
            3: "Čeká na detekci",
            4: "Žádná akce"
        }
        self._current_recommendation: Optional[Dict[str, Any]] = None
        self._init_gui()

    def _init_gui(self) -> None:
        # Check if customtkinter is available
        try:
            import customtkinter as ctk
            self._build_customtkinter_gui(ctk)
        except ImportError:
            try:
                self._build_pyside_gui()
            except Exception as e:
                logger.warning("GUI fallback initialization: %s", e)
                self._build_tkinter_gui()

    def _build_customtkinter_gui(self, ctk: Any) -> None:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("DroidFixAutomator v1.0-PROD | Zero-Conf Technician Cockpit")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)

        # Main Layout
        self.header_frame = ctk.CTkFrame(self.root, fg_color="#111622", height=60, corner_radius=0)
        self.header_frame.pack(fill="x", side="top")

        title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="⚡ DROIDFIX AUTOMATOR - ZERO-CONF COCKPIT",
            font=ctk.CTkFont(family="Consolas", size=16, weight="bold"),
            text_color="#00f0ff"
        )
        title_lbl.pack(side="left", padx=20, pady=15)

        # 4-Step Tracker Cards Frame
        self.tracker_frame = ctk.CTkFrame(self.root, fg_color="#0a0d14", corner_radius=12)
        self.tracker_frame.pack(fill="x", padx=20, pady=15)

        self.cards = {}
        step_titles = [
            (1, "🔌 1. Detekce zařízení", "Čeká na připojení..."),
            (2, "🛠️ 2. Ovladač WinUSB", "SetupAPI Ready"),
            (3, "🔍 3. Identifikace režimu", "Probe protokolu"),
            (4, "⚡ 4. Doporučená akce", "Připraveno ke spuštění")
        ]

        for i, title, subtitle in step_titles:
            card = ctk.CTkFrame(self.tracker_frame, fg_color="#111622", border_width=1, border_color="#1f293d", corner_radius=8)
            card.pack(side="left", fill="both", expand=True, padx=6, pady=10)

            t_lbl = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#00f0ff")
            t_lbl.pack(anchor="w", padx=10, pady=(8, 2))

            s_lbl = ctk.CTkLabel(card, text=subtitle, font=ctk.CTkFont(family="Consolas", size=10), text_color="#9ca3af", wraplength=180)
            s_lbl.pack(anchor="w", padx=10, pady=(0, 8))
            self.cards[i] = (card, t_lbl, s_lbl)

        # Middle Action Frame
        self.action_frame = ctk.CTkFrame(self.root, fg_color="#111622", corner_radius=12)
        self.action_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        self.action_title_lbl = ctk.CTkLabel(
            self.action_frame,
            text="Doporučený servisní krok: Klikněte na 'Spustit Auto-Detekci'",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.action_title_lbl.pack(padx=20, pady=(15, 5))

        self.action_desc_lbl = ctk.CTkLabel(
            self.action_frame,
            text="Systém automaticky prozkoumá USB sběrnici, otestuje odpovědi na handshake dotazy a navrhne nejvhodnější unbrick/flash postup.",
            font=ctk.CTkFont(size=12),
            text_color="#9ca3af",
            wraplength=800
        )
        self.action_desc_lbl.pack(padx=20, pady=(0, 15))

        self.run_btn = ctk.CTkButton(
            self.action_frame,
            text="🚀 SPUSTIT ZERO-CONF AUTO-DETEKCI",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            fg_color="#00f0ff",
            text_color="#000000",
            hover_color="#33f3ff",
            height=40,
            command=self._start_auto_detection_async
        )
        self.run_btn.pack(padx=20, pady=5)

        # Log Output Box
        self.log_box = ctk.CTkTextbox(
            self.action_frame,
            fg_color="#07090e",
            text_color="#00ff9d",
            font=ctk.CTkFont(family="Consolas", size=11),
            corner_radius=8
        )
        self.log_box.pack(fill="both", expand=True, padx=20, pady=15)
        self._log("[SYSTEM] DroidFixAutomator inicializován. Připojte telefon v libovolném režimu (EDL, BROM, Fastboot, ADB).")

    def _log(self, text: str) -> None:
        t = time.strftime("%H:%M:%S")
        if hasattr(self, "log_box"):
            self.log_box.insert("end", f"[{t}] {text}\n")
            self.log_box.see("end")
        else:
            print(f"[{t}] {text}")

    def _start_auto_detection_async(self) -> None:
        threading.Thread(target=self._run_auto_detection, daemon=True).start()

    def _run_auto_detection(self) -> None:
        self._log("[AUTO_ROUTER] Spouštím hloubkový Zero-Conf scan...")
        self.cards[1][2].configure(text="Skenuji USB porty...")
        time.sleep(0.3)

        device = self.router.run_zero_conf_pipeline()
        rec = device["recommendation"]
        self._current_recommendation = rec

        # Update visual cards
        self.cards[1][2].configure(text=f"{device['description']} ({device['port']})")
        self.cards[2][2].configure(text=f"WinUSB: {device['driver_status']}")
        self.cards[3][2].configure(text=f"Režim: {device['mode']}")
        self.cards[4][2].configure(text=f"{rec['action_title']}")

        self.action_title_lbl.configure(text=f"Doporučená operace: {rec['action_title']}")
        self.action_desc_lbl.configure(text=rec["description"])

        self.run_btn.configure(
            text=rec["button_text"],
            fg_color="#00ff9d",
            command=self._execute_action_async
        )
        self._log(f"[AUTO_ROUTER] [DOPORUČENO] {rec['action_title']} (Riziko: {rec['risk_level']})")

    def _execute_action_async(self) -> None:
        threading.Thread(target=self._execute_action, daemon=True).start()

    def _execute_action(self) -> None:
        self._log("[EXECUTOR] Provádím doporučenou servisní operaci...")
        res = self.router.execute_recommended_action()
        self._log(f"[EXECUTOR] [ÚSPĚCH] {res['verdict']}")
        self.action_title_lbl.configure(text=f"Operace dokončena: {res['title']}")
        self.run_btn.configure(
            text="🚀 SPUSTIT NOVOU DETEKCI",
            fg_color="#00f0ff",
            command=self._start_auto_detection_async
        )

    def _build_pyside_gui(self) -> None:
        from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QTextEdit, QVBoxLayout, QWidget

        self.qt_app = QApplication(sys.argv)
        self.qt_window = QMainWindow()
        self.qt_window.setWindowTitle("DroidFixAutomator v1.0-PROD (PySide6)")
        self.qt_window.resize(1000, 650)
        central = QWidget()
        layout = QVBoxLayout(central)
        lbl = QLabel("⚡ DROIDFIX AUTOMATOR ZERO-CONF COCKPIT")
        layout.addWidget(lbl)
        self.qt_window.setCentralWidget(central)

    def _build_tkinter_gui(self) -> None:
        import tkinter as tk
        self.root = tk.Tk()
        self.root.title("DroidFixAutomator (Tkinter Fallback)")
        self.root.geometry("900x600")

    def run(self) -> None:
        if hasattr(self, "root"):
            self.root.mainloop()
        elif hasattr(self, "qt_app"):
            self.qt_window.show()
            sys.exit(self.qt_app.exec())


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
    app = DroidFixAutomatorApp()
    app.run()


if __name__ == "__main__":
    main()
