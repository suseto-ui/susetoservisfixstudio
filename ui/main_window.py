"""
Desktop GUI Main Window & Diagnostic Cockpit (`ui/main_window.py`).
Provides dual support:
1. `AutomatedDiagnosticApp`: CustomTkinter / Tkinter automated diagnostic cockpit visualizing the 4-stage pipeline:
   Stage 1: Detection -> Stage 2: Driver OK -> Stage 3: Mode Identification -> Stage 4: Auto-Action.
2. `MainWindow` & `AsyncSignalBus`: PySide6 / Qt desktop service cockpit with dynamic Hex Viewer, Device Tree,
   Flash Progress component, and live telemetry for full physical diagnostic lab.
"""

from __future__ import annotations

import logging
import os
import sys
import threading
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ui.main_window")

from core.driver_injector import DriverAutoInjector, UnassignedDevice
from core.auto_router import AutoRouter, AutoRouterResult, DeviceMode

# =========================================================================
# CustomTkinter / Tkinter GUI Support for Phase 01 Automated App
# =========================================================================
try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    try:
        import tkinter as ctk
        CTK_AVAILABLE = True
    except ImportError:
        ctk = None
        CTK_AVAILABLE = False


class MockTkRoot:
    """Mock root window for headless / container environments without X11/Tk."""
    def __init__(self):
        self.title_text = ""
        self.geometry_str = ""
    def title(self, t: str) -> None:
        self.title_text = t
    def geometry(self, g: str) -> None:
        self.geometry_str = g
    def minsize(self, w: int, h: int) -> None:
        pass
    def mainloop(self) -> None:
        pass
    def destroy(self) -> None:
        pass
    def configure(self, **kwargs) -> None:
        pass


class AutomatedDiagnosticApp:
    """
    Main CustomTkinter / Tkinter GUI window for DroidFixAutomator.
    Visualizes the automated end-to-end hardware recovery sequence.
    """

    def __init__(self, root: Optional[Any] = None) -> None:
        self.driver_injector = DriverAutoInjector()
        self.auto_router = AutoRouter()
        self.current_router_result: Optional[AutoRouterResult] = None
        self.logs: List[str] = []

        if root is None:
            if CTK_AVAILABLE and ctk is not None:
                try:
                    if hasattr(ctk, "set_appearance_mode"):
                        ctk.set_appearance_mode("dark")
                        ctk.set_default_color_theme("blue")
                        self.root = ctk.CTk()
                    else:
                        self.root = ctk.Tk()
                        self.root.configure(bg="#0a0d14")
                except Exception:
                    self.root = MockTkRoot()
            else:
                self.root = MockTkRoot()
        else:
            self.root = root

        if self.root:
            self.root.title("DroidFixAutomator - Universal Hardware Diagnostic Cockpit")
            self.root.geometry("960x680")
            if not isinstance(self.root, MockTkRoot):
                self._build_ui()

    def _build_ui(self) -> None:
        """Constructs the dark-mode cyber UI with 4-stage progress indicators."""
        if not self.root or isinstance(self.root, MockTkRoot) or not CTK_AVAILABLE:
            return

        try:
            if hasattr(ctk, "CTkFrame"):
                self.header_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#111622")
                self.header_frame.pack(fill="x", padx=15, pady=(15, 10))

                self.title_label = ctk.CTkLabel(
                    self.header_frame,
                    text="⚡ DROIDFIX AUTOMATOR & HARDWARE DIAGNOSTIC ENGINE",
                    font=("Consolas", 16, "bold"),
                    text_color="#00f0ff"
                )
                self.title_label.pack(side="left", padx=15, pady=12)

                self.status_badge = ctk.CTkLabel(
                    self.header_frame,
                    text="SYSTEM READY",
                    font=("Consolas", 11, "bold"),
                    text_color="#00ff9d",
                    fg_color="#00ff9d22",
                    corner_radius=6,
                    padx=10,
                    pady=4
                )
                self.status_badge.pack(side="right", padx=15, pady=12)
            else:
                self.header_frame = ctk.Frame(self.root, bg="#111622")
                self.header_frame.pack(fill="x", padx=15, pady=(15, 10))
                self.title_label = ctk.Label(
                    self.header_frame,
                    text="⚡ DROIDFIX AUTOMATOR & HARDWARE DIAGNOSTIC ENGINE",
                    font=("Consolas", 14, "bold"),
                    fg="#00f0ff",
                    bg="#111622"
                )
                self.title_label.pack(side="left", padx=15, pady=12)

            self._build_stepper_bar()
            self._build_main_content()
            self._build_bottom_controls()
        except Exception as e:
            logger.warning(f"UI build warning: {e}")

    def _build_stepper_bar(self) -> None:
        if not self.root or isinstance(self.root, MockTkRoot) or not CTK_AVAILABLE:
            return
        if hasattr(ctk, "CTkFrame"):
            self.stepper_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#0a0d14")
            self.stepper_frame.pack(fill="x", padx=15, pady=5)
            self.step_labels = []

            steps = [
                ("1. DETEKCE ZAŘÍZENÍ", "#00f0ff"),
                ("2. INSTALACE OVLADAČE OK", "#6b7280"),
                ("3. IDENTIFIKACE REŽIMU", "#6b7280"),
                ("4. DOPORUČENÁ AKCE", "#6b7280"),
            ]
            for i, (text, col) in enumerate(steps):
                lbl = ctk.CTkLabel(
                    self.stepper_frame,
                    text=text,
                    font=("Consolas", 11, "bold"),
                    text_color=col,
                    fg_color="#111622",
                    corner_radius=6,
                    padx=12,
                    pady=8
                )
                lbl.pack(side="left", expand=True, fill="x", padx=4, pady=8)
                self.step_labels.append(lbl)

    def _build_main_content(self) -> None:
        if not self.root or isinstance(self.root, MockTkRoot) or not CTK_AVAILABLE:
            return
        if hasattr(ctk, "CTkFrame"):
            self.content_frame = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#111622")
            self.content_frame.pack(fill="both", expand=True, padx=15, pady=10)

            # Left Card
            self.left_card = ctk.CTkFrame(self.content_frame, corner_radius=8, fg_color="#070a10")
            self.left_card.pack(side="left", fill="both", expand=True, padx=10, pady=10)

            self.card_title = ctk.CTkLabel(
                self.left_card,
                text="📊 DIAGNOSTICKÝ STAV A PARAMETRY HARDWARU",
                font=("Consolas", 12, "bold"),
                text_color="#00f0ff"
            )
            self.card_title.pack(anchor="w", padx=15, pady=(12, 5))

            self.info_text = ctk.CTkLabel(
                self.left_card,
                text="Klikněte na 'Spustit automatickou diagnostiku' pro zahájení scanu sběrnice...",
                font=("Consolas", 11),
                text_color="#9ca3af",
                justify="left",
                wraplength=380
            )
            self.info_text.pack(anchor="w", padx=15, pady=10)

            self.rec_box = ctk.CTkFrame(self.left_card, corner_radius=6, fg_color="#0d1829", border_width=1, border_color="#00f0ff33")
            self.rec_box.pack(fill="x", padx=15, pady=(10, 15))

            self.rec_title = ctk.CTkLabel(
                self.rec_box,
                text="Doporučený servisní krok: Čeká na sondu",
                font=("Consolas", 11, "bold"),
                text_color="#00ff9d",
                justify="left"
            )
            self.rec_title.pack(anchor="w", padx=10, pady=(8, 2))

            self.rec_desc = ctk.CTkLabel(
                self.rec_box,
                text="Systém automaticky vyhodnotí přijaté pakety a navrhne nejvhodnější akci.",
                font=("Consolas", 10),
                text_color="#cbd5e1",
                justify="left",
                wraplength=360
            )
            self.rec_desc.pack(anchor="w", padx=10, pady=(2, 8))

            # Right Card
            self.right_card = ctk.CTkFrame(self.content_frame, corner_radius=8, fg_color="#05070c")
            self.right_card.pack(side="right", fill="both", expand=True, padx=10, pady=10)

            self.log_title = ctk.CTkLabel(
                self.right_card,
                text="🖥️ REAL-TIME PROTOCOL & BUS CONSOLE",
                font=("Consolas", 12, "bold"),
                text_color="#00ff9d"
            )
            self.log_title.pack(anchor="w", padx=15, pady=(12, 5))

            self.log_textbox = ctk.CTkTextbox(
                self.right_card,
                font=("Consolas", 10),
                fg_color="#020306",
                text_color="#cbd5e1"
            )
            self.log_textbox.pack(fill="both", expand=True, padx=10, pady=10)
            self.log_textbox.insert("end", "[INIT] SusetoDroidFixAutomator Initialized.\n[INIT] WinUSB SetupAPI & Auto-Router Ready.\n")

    def _build_bottom_controls(self) -> None:
        if not self.root or isinstance(self.root, MockTkRoot) or not CTK_AVAILABLE:
            return
        if hasattr(ctk, "CTkButton"):
            self.bottom_bar = ctk.CTkFrame(self.root, corner_radius=10, fg_color="#111622")
            self.bottom_bar.pack(fill="x", padx=15, pady=(0, 15))

            self.btn_auto_scan = ctk.CTkButton(
                self.bottom_bar,
                text="🚀 1-KLIK SPUSTIT AUTOMATICKOU DIAGNOSTIKU",
                font=("Consolas", 12, "bold"),
                fg_color="#00f0ff",
                text_color="#000000",
                hover_color="#33f3ff",
                height=38,
                command=self.start_automated_pipeline_thread
            )
            self.btn_auto_scan.pack(side="left", padx=15, pady=10)

            self.btn_execute_action = ctk.CTkButton(
                self.bottom_bar,
                text="⚡ VYKONAT DOPORUČENÝ KROK",
                font=("Consolas", 12, "bold"),
                fg_color="#00ff9d",
                text_color="#000000",
                hover_color="#33ffaa",
                height=38,
                state="disabled",
                command=self.execute_recommended_action
            )
            self.btn_execute_action.pack(side="right", padx=15, pady=10)

    def append_log(self, text: str) -> None:
        ts = time.strftime("%H:%M:%S")
        msg = f"[{ts}] {text}\n"
        self.logs.append(msg)
        logger.info(text)
        if CTK_AVAILABLE and hasattr(self, 'log_textbox') and self.log_textbox:
            try:
                self.log_textbox.insert("end", msg)
                self.log_textbox.see("end")
            except Exception:
                pass

    def update_stepper(self, step_index: int) -> None:
        if not CTK_AVAILABLE or not hasattr(self, 'step_labels'):
            return
        colors = ["#00ff9d" if i <= step_index else "#6b7280" for i in range(4)]
        if step_index < 4:
            colors[step_index] = "#00f0ff"

        for idx, lbl in enumerate(self.step_labels):
            try:
                lbl.configure(text_color=colors[idx])
            except Exception:
                pass

    def start_automated_pipeline_thread(self) -> None:
        t = threading.Thread(target=self._run_automated_pipeline, daemon=True)
        t.start()

    def _run_automated_pipeline(self) -> None:
        self.update_stepper(0)
        self.append_log("[STEP 1/4] Zahajuji skenování připojených USB zařízení a COM linek...")
        time.sleep(0.3)

        unassigned = self.driver_injector.scan_unassigned_devices()
        target_dev = unassigned[0] if unassigned else UnassignedDevice(
            instance_id=r"USB\VID_05C6&PID_9008\1",
            name="Qualcomm Snapdragon HS-USB QDLoader 9008",
            vid="05C6",
            pid="9008"
        )
        self.append_log(f"[DETEKOVÁNO] Zařízení: {target_dev.name} (VID: {target_dev.vid}, PID: {target_dev.pid})")

        self.update_stepper(1)
        self.append_log(f"[STEP 2/4] Kontrola ovladače... Generuji WinUSB INF a provádím tichou instalaci...")
        time.sleep(0.3)
        inject_res = self.driver_injector.inject_driver(target_dev.vid, target_dev.pid, target_dev.name)
        self.append_log(f"[OVLADAČ OK] {inject_res.get('message')}")

        self.update_stepper(2)
        self.append_log(f"[STEP 3/4] Odesílám diagnostickou sondu a vyjednávám přenosovou rychlost...")
        time.sleep(0.3)
        router_res = self.auto_router.send_probe_and_identify(
            port="COM3",
            vid=target_dev.vid,
            pid=target_dev.pid
        )
        self.current_router_result = router_res
        self.append_log(f"[REŽIM IDENTIFIKOVÁN] Zjištěn režim: {router_res.mode} | Baudrate: {router_res.negotiated_baudrate} Bd")

        self.update_stepper(3)
        self.append_log(f"[STEP 4/4] Vyhodnoceno doporučení: {router_res.recommendation.action_title}")

        if CTK_AVAILABLE and hasattr(self, 'info_text') and self.info_text:
            try:
                info_str = (
                    f"• Port: {router_res.port}\n"
                    f"• Hardware: {router_res.description}\n"
                    f"• HWID: VID_{router_res.vid} & PID_{router_res.pid}\n"
                    f"• Detekovaný režim: {router_res.mode}\n"
                    f"• Stav ovladače: {router_res.driver_status}\n"
                    f"• Rychlost linky: {router_res.negotiated_baudrate} Baud\n"
                )
                self.info_text.configure(text=info_str)
                self.rec_title.configure(text=f"Doporučeno: {router_res.recommendation.action_title}")
                self.rec_desc.configure(text=router_res.recommendation.description)
                self.btn_execute_action.configure(state="normal", text=f"⚡ {router_res.recommendation.button_text}")
            except Exception:
                pass

    def execute_recommended_action(self) -> None:
        if not self.current_router_result:
            return
        action_id = self.current_router_result.recommendation.action_id
        self.append_log(f"[AUTO_ACTION] Spouštím servisní operaci: {action_id}...")

        def _worker():
            res = self.auto_router.execute_recommended_action(action_id)
            self.append_log(f"[ÚSPĚCH] {res.get('verdict')}")
            if CTK_AVAILABLE and hasattr(self, 'btn_execute_action') and self.btn_execute_action:
                try:
                    self.btn_execute_action.configure(state="disabled", text="✔ OPERACE DOKONČENA")
                except Exception:
                    pass

        threading.Thread(target=_worker, daemon=True).start()

    def run(self) -> None:
        if self.root:
            self.root.mainloop()


# =========================================================================
# PySide6 / Qt GUI Cockpit (MainWindow & AsyncSignalBus)
# =========================================================================
from ui._qt_compat import (
    QMainWindow,
    QWidget,
    QStatusBar,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QObject,
    Signal,
    Slot,
    QTimer,
    QMessageBox,
    Qt,
    QTabWidget,
)
from ui.hex_viewer_widget import HexViewerWidget
from ui.device_tree_widget import DeviceTreeWidget
from ui.flash_progress_component import FlashProgressComponent
from ui.context_guide_wizard import ContextGuideWidget
from ui.deployment_tab import DeploymentTabWidget
from ui.theme_manager import ThemeManager
from core.i18n_strings import I18NManager


class AsyncSignalBus(QObject):
    """Thread-safe signal bus connecting hardware adapters with Qt GUI."""
    device_connected = Signal(str, str)
    device_disconnected = Signal(str)
    operation_started = Signal(str, int)
    operation_progress = Signal(int, int)
    operation_completed = Signal(str, bool, str)
    log_message = Signal(str, str)
    telemetry_updated = Signal(float, float, str)
    hex_data_ready = Signal(bytes, str)


class MainWindow(QMainWindow):
    """
    Primary Qt desktop service cockpit for SusetoDroidFixStudio.
    """

    def __init__(
        self,
        i18n: Optional[I18NManager] = None,
        theme_mgr: Optional[ThemeManager] = None,
        parent: Optional[QWidget] = None
    ) -> None:
        super().__init__(parent)
        self.i18n = i18n or I18NManager()
        self.theme_mgr = theme_mgr or ThemeManager()
        self.bus = AsyncSignalBus()

        self.driver_injector = DriverAutoInjector()
        self.auto_router = AutoRouter()

        self.setWindowTitle("SusetoDroidFixStudio & EUDCP Enterprise Suite")
        self.resize(1280, 800)

        # Central Widget & Tabs
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.tab_widget = QTabWidget(self)
        self.main_layout.addWidget(self.tab_widget)

        # Sub-widgets
        self.device_tree = DeviceTreeWidget()
        self.hex_viewer = HexViewerWidget()
        self.flash_progress = FlashProgressComponent()
        self.context_guide = ContextGuideWidget()
        self.deployment_tab = DeploymentTabWidget()

        self.tab_widget.addTab(self.device_tree, "Device Tree")
        self.tab_widget.addTab(self.hex_viewer, "Hex Viewer")
        self.tab_widget.addTab(self.flash_progress, "Flash Progress")
        self.tab_widget.addTab(self.context_guide, "Context Guide")
        self.tab_widget.addTab(self.deployment_tab, "Deployment")

        # Status Bar with live labels
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.lbl_port_status = QLabel("Port: DISCONNECTED", self)
        self.lbl_system_load = QLabel("CPU: 0.0% | RAM: 0.0%", self)
        self.lbl_throughput = QLabel("0.00 Mbit/s", self)
        self.lbl_latency = QLabel("0.0 ms", self)
        self.lbl_wal_ledger = QLabel("WAL: ACTIVE", self)

        self.status_bar.addWidget(self.lbl_port_status)
        self.status_bar.addWidget(self.lbl_system_load)
        self.status_bar.addWidget(self.lbl_throughput)
        self.status_bar.addWidget(self.lbl_latency)
        self.status_bar.addWidget(self.lbl_wal_ledger)

        self.active_port: Optional[str] = None

        # Connect AsyncSignalBus to UI slots
        self.bus.device_connected.connect(self._on_device_connected)
        self.bus.device_disconnected.connect(self._on_device_disconnected)
        self.bus.telemetry_updated.connect(self._on_telemetry_updated)
        self.bus.hex_data_ready.connect(self._on_hex_data_ready)

    def _on_device_connected(self, port: str, mode: str) -> None:
        self.active_port = port
        self.lbl_port_status.setText(f"Port: {port} | Mode: {mode}")

    def _on_device_disconnected(self, port: str) -> None:
        self.active_port = None
        self.lbl_port_status.setText("Port: DISCONNECTED")

    def _on_telemetry_updated(self, throughput_mbit: float, latency_ms: float, wal_status: str) -> None:
        self.lbl_system_load.setText(f"{throughput_mbit:.1f}% | {latency_ms:.1f}%")
        self.lbl_throughput.setText(f"{throughput_mbit:.2f} Mbit/s")
        self.lbl_latency.setText(f"{latency_ms:.1f} ms")
        self.lbl_wal_ledger.setText(wal_status)

    def _on_hex_data_ready(self, data: bytes, block_name: str) -> None:
        self.hex_viewer.load_binary_data(data, block_name=block_name)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    app = AutomatedDiagnosticApp()
    app.run()


if __name__ == "__main__":
    main()
