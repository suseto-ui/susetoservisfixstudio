"""
Ergonomic Theme & Styling Manager for SusetoDroidFixStudio.
Provides high-contrast Dark Mode QSS stylesheets (Cyber/Technician, Dark Slate, High-Contrast Forensic)
engineered for long-duration laboratory inspection without visual fatigue.
"""

from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger("theme_manager")


CYBER_TECHNICIAN_QSS = """
/* SusetoDroidFixStudio - Cyber/Technician High-Contrast Theme */
QWidget {
    background-color: #0a0d14;
    color: #d4d4d4;
    font-family: 'Segoe UI', 'SF Pro Display', 'DejaVu Sans', sans-serif;
    font-size: 12px;
    selection-background-color: #00f0ff;
    selection-color: #000000;
}

QMainWindow, QDialog {
    background-color: #0a0d14;
}

/* Header and Dock Panes */
QHeaderView::section {
    background-color: #111622;
    color: #00f0ff;
    padding: 6px;
    border: 1px solid #1f293d;
    font-weight: bold;
    font-family: 'Consolas', monospace;
}

/* Splitters */
QSplitter::handle {
    background-color: #1f293d;
}
QSplitter::handle:hover {
    background-color: #00f0ff;
}

/* Push Buttons */
QPushButton {
    background-color: #111622;
    color: #e5e7eb;
    border: 1px solid #1f293d;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: bold;
    font-size: 11px;
}
QPushButton:hover {
    background-color: #1f293d;
    border-color: #00f0ff;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #0e639c;
    border-color: #00f0ff;
}
QPushButton:disabled {
    background-color: #0b0e17;
    color: #4b5563;
    border-color: #161f30;
}

/* Special Action Buttons */
QPushButton#btn_primary {
    background-color: #00f0ff;
    color: #000000;
    font-weight: 900;
    border: none;
}
QPushButton#btn_primary:hover {
    background-color: #33f3ff;
}
QPushButton#btn_danger {
    background-color: #ff3366;
    color: #ffffff;
    font-weight: 800;
    border: none;
}
QPushButton#btn_success {
    background-color: #107c41;
    color: #ffffff;
    font-weight: 800;
    border: none;
}

/* Line Edits & Text Areas */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #07090e;
    color: #00f0ff;
    border: 1px solid #1f293d;
    border-radius: 4px;
    padding: 6px;
    font-family: 'Consolas', 'Courier New', monospace;
}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #00f0ff;
}

/* Lists and Tree Views */
QTreeWidget, QListWidget, QTableWidget {
    background-color: #0d111a;
    border: 1px solid #1f293d;
    border-radius: 6px;
    color: #e2e8f0;
    font-family: 'Consolas', monospace;
}
QTreeWidget::item:selected, QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #162a45;
    color: #00f0ff;
    border-left: 3px solid #00f0ff;
}

/* Progress Bars */
QProgressBar {
    background-color: #111622;
    border: 1px solid #1f293d;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
    font-family: 'Consolas', monospace;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #00ff9d);
    border-radius: 3px;
}

/* Status Bar */
QStatusBar {
    background-color: #07090e;
    border-top: 1px solid #1f293d;
    color: #9ca3af;
    font-family: 'Consolas', monospace;
    font-size: 11px;
}

/* Tooltips */
QToolTip {
    background-color: #111622;
    color: #00f0ff;
    border: 1px solid #00f0ff;
    padding: 6px;
    border-radius: 4px;
    font-size: 11px;
}
"""

DARK_SLATE_QSS = """
QWidget {
    background-color: #1e293b;
    color: #f1f5f9;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}
QStatusBar {
    background-color: #0f172a;
    border-top: 1px solid #334155;
    color: #94a3b8;
}
QPushButton {
    background-color: #334155;
    color: #ffffff;
    border: 1px solid #475569;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #475569;
}
"""


class ThemeManager:
    """
    Controls runtime theme application and style configurations.
    """

    THEMES = {
        "cyber_technician": CYBER_TECHNICIAN_QSS,
        "dark_slate": DARK_SLATE_QSS,
    }

    def __init__(self, default_theme: str = "cyber_technician") -> None:
        self.active_theme_name = default_theme

    def get_stylesheet(self, theme_name: Optional[str] = None) -> str:
        """Retrieve QSS stylesheet string for specified or active theme."""
        name = theme_name or self.active_theme_name
        return self.THEMES.get(name, CYBER_TECHNICIAN_QSS)

    def apply_theme(self, widget: Any, theme_name: Optional[str] = None) -> None:
        """Apply stylesheet directly to a QWidget or QApplication instance."""
        qss = self.get_stylesheet(theme_name)
        if hasattr(widget, "setStyleSheet"):
            widget.setStyleSheet(qss)
            logger.info("Applied theme '%s' to %s", theme_name or self.active_theme_name, type(widget).__name__)
