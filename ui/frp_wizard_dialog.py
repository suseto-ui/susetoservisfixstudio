"""
Automated FRP Removal Wizard Dialog for SusetoDroidFixStudio.
PySide6 multi-step servicing wizard for guided OEM unlocking,
port negotiation, and 1-click Factory Reset Protection (FRP) partition erasure.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.frp_engine import FRPEngine

logger = logging.getLogger("ui.frp_wizard")


class FRPWizardDialog(QWidget):
    """
    Step-by-step guided wizard for automated multi-chipset FRP removal.
    """

    frp_completed = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None, frp_engine: Optional[FRPEngine] = None) -> None:
        super().__init__(parent)
        self.engine = frp_engine or FRPEngine()
        self.current_step = 1
        self.selected_brand = "SAMSUNG"
        self.selected_chipset = "SAMSUNG"
        self.selected_port = "COM3"

        self._init_ui()

    def _init_ui(self) -> None:
        self.setWindowTitle("SusetoDroidFixStudio | 1-Click FRP Removal Wizard")
        self.resize(640, 480)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Header Title & Step Indicator
        self.lbl_title = QLabel("Automated Factory Reset Protection (FRP) Unlock")
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ffff;")
        main_layout.addWidget(self.lbl_title)

        self.lbl_step = QLabel("Step 1 of 3: Select Device Manufacturer & Chipset")
        self.lbl_step.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffaa00;")
        main_layout.addWidget(self.lbl_step)

        # Brand Selector Buttons
        self.box_brands = QHBoxLayout()
        self.btn_samsung = QPushButton("Samsung (MTP/AT)")
        self.btn_samsung.clicked.connect(lambda: self._select_brand("SAMSUNG", "SAMSUNG"))
        self.box_brands.addWidget(self.btn_samsung)

        self.btn_xiaomi = QPushButton("Xiaomi / Redmi (EDL/Fastboot)")
        self.btn_xiaomi.clicked.connect(lambda: self._select_brand("XIAOMI", "QUALCOMM"))
        self.box_brands.addWidget(self.btn_xiaomi)

        self.btn_mtk = QPushButton("MediaTek (BROM / Preloader)")
        self.btn_mtk.clicked.connect(lambda: self._select_brand("MTK_GENERIC", "MTK"))
        self.box_brands.addWidget(self.btn_mtk)

        self.btn_qc = QPushButton("Qualcomm 9008 (Firehose)")
        self.btn_qc.clicked.connect(lambda: self._select_brand("QUALCOMM", "QUALCOMM"))
        self.box_brands.addWidget(self.btn_qc)

        main_layout.addLayout(self.box_brands)

        # Port & Parameter Settings
        lbl_port_desc = QLabel("Target Service Port / Interface:")
        main_layout.addWidget(lbl_port_desc)

        self.input_port = QLineEdit("COM3 (Qualcomm HS-USB QDLoader 9008)")
        self.input_port.setStyleSheet("background-color: #252526; color: #4ec9b0; font-family: monospace;")
        main_layout.addWidget(self.input_port)

        # Execution Log View
        self.lbl_log = QLabel("Ready. Select target manufacturer above and click 'Execute 1-Click FRP Wipe'.")
        self.lbl_log.setStyleSheet(
            "padding: 12px; background-color: #181818; color: #d4d4d4; "
            "border: 1px solid #3c3c3c; border-radius: 4px; font-family: monospace;"
        )
        main_layout.addWidget(self.lbl_log, stretch=1)

        # Action Button Row
        actions_layout = QHBoxLayout()
        self.btn_execute = QPushButton("⚡ Execute 1-Click FRP Wipe")
        self.btn_execute.setStyleSheet(
            "padding: 10px 20px; background-color: #d83b01; color: white; "
            "font-weight: bold; font-size: 14px; border-radius: 4px;"
        )
        self.btn_execute.clicked.connect(self._on_execute_frp)
        actions_layout.addWidget(self.btn_execute)

        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self._on_close_clicked)
        actions_layout.addWidget(self.btn_close)

        main_layout.addLayout(actions_layout)
        self.setStyleSheet("background-color: #1e1e1e; color: #cccccc;")

    def _select_brand(self, brand: str, chipset: str) -> None:
        self.selected_brand = brand
        self.selected_chipset = chipset
        self.lbl_step.setText(f"Target Selected: {brand} [Architecture: {chipset}]")
        self.lbl_log.setText(f"Configured for {brand}.\nProtocol pipeline: {self.engine.CHIPSETS.get(chipset, chipset)}")

    def _on_execute_frp(self) -> None:
        port = self.input_port.text().split()[0]
        self.lbl_log.setText(f"[*] Dispatched FRP Wipe payload to {port} ({self.selected_chipset})...\n")

        result = self.engine.execute_frp_wipe(
            chipset=self.selected_chipset,
            port=port,
            partition_info={"name": "frp", "start_sector": 1048576, "sectors": 2048},
        )

        if result.get("success"):
            self.lbl_log.setText(
                f"[SUCCESS] FRP Wipe Complete!\n"
                f"Method: {result.get('method')}\n"
                f"Status: {result.get('status')}\n"
                f"Payload dispatched to hardware controller."
            )
            self.frp_completed.emit(result)
            QMessageBox.information(
                self,
                "FRP Unlock Completed",
                f"FRP partition successfully erased for {self.selected_brand}!\nDevice may now be rebooted.",
            )
        else:
            self.lbl_log.setText(f"[FAILED] {result.get('status')}")
            QMessageBox.critical(self, "FRP Error", f"Operation failed:\n{result.get('status')}")

    def _on_close_clicked(self) -> None:
        pass
