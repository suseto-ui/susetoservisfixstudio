"""
Flash & Memory I/O Progress Component for SusetoDroidFixStudio.
Provides granular visualization of transfer throughput (Mbit/s, KB/s),
elapsed/estimated remaining time (ETA), round-trip latency, and async cancellation token integration.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    Signal,
    Slot,
    Qt,
)

logger = logging.getLogger("ui.flash_progress")


class FlashProgressComponentState:
    """
    State accumulator and metrics calculator for flash progress telemetry.
    """

    def __init__(self) -> None:
        self.status = "IDLE"
        self.percent = 0.0
        self.bytes_written = 0
        self.total_size = 0
        self.speed_bytes_per_sec = 0.0
        self.elapsed_sec = 0.0
        self.recent_logs = []

    def update(self, metrics: dict) -> None:
        self.status = metrics.get("status", self.status)
        self.percent = float(metrics.get("percent", self.percent))
        self.bytes_written = int(metrics.get("bytes_written", self.bytes_written))
        self.total_size = int(metrics.get("total_size", self.total_size))
        self.speed_bytes_per_sec = float(metrics.get("speed_bytes_per_sec", self.speed_bytes_per_sec))
        self.elapsed_sec = float(metrics.get("elapsed_sec", self.elapsed_sec))
        if "log" in metrics:
            self.recent_logs.append(metrics["log"])
        else:
            self.recent_logs.append(f"Progress: {self.percent:.1f}% ({self.status})")

    def get_summary(self) -> dict:
        kb_sec = self.speed_bytes_per_sec / 1024.0
        return {
            "status": self.status,
            "percent": self.percent,
            "percent_str": f"{self.percent:.1f}%",
            "throughput_str": f"{kb_sec:.2f} KB/s",
            "bytes_written": self.bytes_written,
            "total_size": self.total_size,
            "elapsed_sec": self.elapsed_sec,
            "recent_logs": list(self.recent_logs),
        }


class FlashProgressComponent(QWidget):
    """
    High-precision progress tracker with real-time throughput metrics and cancel controls.
    """

    cancellation_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._start_time: Optional[float] = None
        self._total_bytes: int = 0
        self._transferred_bytes: int = 0
        self._current_sector: int = 0
        self._total_sectors: int = 0

        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Top Info Line: Operation Title & Latency
        top_row = QHBoxLayout()
        self.lbl_operation = QLabel("Operation: Idle")
        self.lbl_operation.setStyleSheet("font-weight: bold; color: #00f0ff; font-family: monospace;")
        top_row.addWidget(self.lbl_operation)

        self.lbl_latency = QLabel("Latency: -- ms")
        self.lbl_latency.setStyleSheet("color: #00ff9d; font-family: monospace; font-size: 11px;")
        top_row.addWidget(self.lbl_latency, alignment=Qt.AlignRight)
        layout.addLayout(top_row)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        # Metrics Line: Speed, Transferred, ETA
        metrics_row = QHBoxLayout()
        self.lbl_speed = QLabel("Speed: 0.00 KB/s (0.00 Mbit/s)")
        self.lbl_speed.setStyleSheet("color: #d4d4d4; font-family: monospace; font-size: 11px;")
        metrics_row.addWidget(self.lbl_speed)

        self.lbl_sectors = QLabel("Sectors: 0 / 0")
        self.lbl_sectors.setStyleSheet("color: #9ca3af; font-family: monospace; font-size: 11px;")
        metrics_row.addWidget(self.lbl_sectors)

        self.lbl_eta = QLabel("ETA: --:--")
        self.lbl_eta.setStyleSheet("color: #ffaa00; font-family: monospace; font-size: 11px;")
        metrics_row.addWidget(self.lbl_eta, alignment=Qt.AlignRight)
        layout.addLayout(metrics_row)

        # Action Buttons Line
        btn_row = QHBoxLayout()
        self.btn_cancel = QPushButton("✖ Cancel Operation")
        self.btn_cancel.setObjectName("btn_danger")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_cancel)
        layout.addLayout(btn_row)

        self.setStyleSheet("background-color: #0d111a; border-radius: 6px; border: 1px solid #1f293d;")

    def start_operation(self, op_name: str, total_bytes: int, total_sectors: int = 0) -> None:
        """Initialize and arm progress tracking."""
        self._start_time = time.time()
        self._total_bytes = total_bytes
        self._transferred_bytes = 0
        self._total_sectors = total_sectors
        self._current_sector = 0

        self.lbl_operation.setText(f"Operation: {op_name}")
        self.progress_bar.setValue(0)
        self.btn_cancel.setEnabled(True)
        self._update_display(0)
        logger.info("Flash progress started: %s (Total bytes: %d)", op_name, total_bytes)

    def update_progress(self, current_bytes: int, current_sector: int = 0, latency_ms: Optional[float] = None) -> None:
        """Update transfer counter and recompute speed/ETA."""
        self._transferred_bytes = current_bytes
        self._current_sector = current_sector

        if latency_ms is not None:
            self.lbl_latency.setText(f"Latency: {latency_ms:.1f} ms")

        if self._total_bytes > 0:
            pct = int((current_bytes / self._total_bytes) * 100)
            self.progress_bar.setValue(min(pct, 100))

        self._update_display(current_bytes)

    def _update_display(self, current_bytes: int) -> None:
        if not self._start_time:
            return

        elapsed = max(time.time() - self._start_time, 0.001)
        speed_bytes_sec = current_bytes / elapsed
        speed_kb_sec = speed_bytes_sec / 1024.0
        speed_mbit_sec = (speed_bytes_sec * 8) / (1024.0 * 1024.0)

        self.lbl_speed.setText(f"Speed: {speed_kb_sec:.1f} KB/s ({speed_mbit_sec:.2f} Mbit/s)")

        if self._total_sectors > 0:
            self.lbl_sectors.setText(f"Sectors: {self._current_sector} / {self._total_sectors}")

        if self._total_bytes > 0 and speed_bytes_sec > 0:
            remaining_bytes = max(self._total_bytes - current_bytes, 0)
            eta_seconds = int(remaining_bytes / speed_bytes_sec)
            mins, secs = divmod(eta_seconds, 60)
            self.lbl_eta.setText(f"ETA: {mins:02d}:{secs:02d}")
        else:
            self.lbl_eta.setText("ETA: --:--")

    def complete_operation(self, success: bool = True, message: str = "") -> None:
        """Mark operation complete and disable cancel trigger."""
        self.btn_cancel.setEnabled(False)
        if success:
            self.progress_bar.setValue(100)
            self.lbl_operation.setText(f"Operation: Complete - {message}")
            self.lbl_eta.setText("ETA: 00:00")
        else:
            self.lbl_operation.setText(f"Operation: Failed - {message}")
        self._start_time = None

    def _on_cancel_clicked(self) -> None:
        self.btn_cancel.setEnabled(False)
        self.lbl_operation.setText("Operation: Aborting...")
        logger.warning("User requested operation cancellation.")
        self.cancellation_requested.emit()
