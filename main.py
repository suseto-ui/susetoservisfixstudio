"""
SusetoDroidFixStudio & EUDCP Enterprise Suite
Primary Executable Entry Point for Windows Standalone Application (.exe)

Modes supported:
  --kiosk     : Launch the locked-down 1-Click Kiosk & Admin Router (Default for shop kiosks)
  --webview   : Launch pixel-perfect modern Cyber Cockpit via Edge WebView2 (app_webview.py)
  --qt        : Launch PySide6 / CustomTkinter native window
"""

from __future__ import annotations

import logging
import os
import sys

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("main")


def main() -> None:
    """
    Primary entry point for SusetoDroidFixStudio standalone executable.
    Prioritizes Kiosk mode if specified or default desktop execution.
    """
    # 1. Explicit Kiosk Mode
    if "--kiosk" in sys.argv or os.environ.get("SUSETO_MODE") == "kiosk":
        _launch_kiosk_gui()
        return

    # 2. Legacy Qt mode requested
    if "--qt" in sys.argv or os.environ.get("SUSETO_FORCE_QT") == "1":
        _launch_qt_gui()
        return

    # 3. WebView Cockpit with automatic fallback to Kiosk / CTk Router
    try:
        from app_webview import main as launch_webview
        launch_webview()
    except Exception as exc:
        logger.warning("WebView2 cockpit failed (%s). Falling back to Kiosk / Admin AppRouter...", exc)
        _launch_kiosk_gui()


def _launch_kiosk_gui() -> None:
    """Launch the locked-down Kiosk & Admin Router window."""
    try:
        from ui.app_router import AppRouter
        app = AppRouter()
        app.mainloop()
    except Exception as exc:
        logger.error("Failed to launch Kiosk AppRouter: %s. Attempting Qt fallback...", exc)
        _launch_qt_gui()


def _launch_qt_gui() -> None:
    """Fallback launcher for PySide6 / CustomTkinter native window."""
    try:
        from ui._qt_compat import QApplication
        from ui.main_window import MainWindow as PySideMainWindow
        from ui.theme_manager import ThemeManager

        app = QApplication(sys.argv)
        theme_mgr = ThemeManager()
        window = PySideMainWindow(theme_mgr=theme_mgr)
        window.show()
        sys.exit(app.exec())
    except Exception as err:
        logger.warning("Launching CustomTkinter fallback GUI interface: %s", err)
        try:
            from ui.app_router import AppRouter
            app = AppRouter()
            app.mainloop()
        except Exception as inner_err:
            logger.error("All GUI interfaces failed: %s", inner_err)


if __name__ == "__main__":
    main()
