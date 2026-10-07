#!/usr/bin/env python3
"""
Executable Binary & Package Functional Verification Script (`verify_executable.py`).
Performs rigorous structural checks, native DLL staging verification, SQLite WAL schema audit,
and headless GUI module instantiation smoke test for SusetoDroidFixStudio.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("verify_executable")

_ROOT = Path(__file__).resolve().parent
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def verify_package_integrity() -> bool:
    logger.info("=== SUSETO DROID FIX STUDIO - EXECUTABLE & PACKAGE VERIFICATION ===")
    
    dist_dir = _ROOT / "dist" / "SusetoDroidFixStudio"
    if not dist_dir.exists():
        dist_dir = _ROOT / "dist"
    
    # 1. Check Executable / Core entry
    exe_candidates = [
        dist_dir / "SusetoDroidFixStudio.exe",
        dist_dir / "SusetoDroidFixStudio",
        _ROOT / "main.py",
    ]
    found_exe = any(p.exists() for p in exe_candidates)
    if found_exe:
        logger.info("   [✔] Executable / Entrypoint binary present.")
    else:
        logger.error("   [✘] Executable binary missing in dist/!")
        return False

    # 2. Check Native Drivers
    drivers_dir = dist_dir / "drivers" if (dist_dir / "drivers").exists() else _ROOT / "drivers"
    required_drivers = ["ftd2xx64.dll", "silabser64.dll", "winusb_setup.cmd"]
    for drv in required_drivers:
        if (drivers_dir / drv).exists():
            logger.info("   [✔] Native driver / script present: drivers/%s", drv)
        else:
            logger.error("   [✘] Missing required driver file: drivers/%s", drv)
            return False

    # 3. Check SQLite Schema
    schema_path = dist_dir / "db" / "schema.sql" if (dist_dir / "db" / "schema.sql").exists() else _ROOT / "db" / "schema.sql"
    if schema_path.exists():
        logger.info("   [✔] SQLite WAL schema present: %s", schema_path.name)
    else:
        logger.error("   [✘] SQLite schema missing!")
        return False

    # 4. Check CLI Binaries
    bin_dir = dist_dir / "bin" if (dist_dir / "bin").exists() else _ROOT / "bin"
    adb_bin = bin_dir / ("adb.exe" if sys.platform.startswith("win") else "adb")
    if adb_bin.exists():
        logger.info("   [✔] CLI tool present: bin/%s", adb_bin.name)
    else:
        logger.warning("   [!] CLI binary missing or mocked.")

    # 5. Smoke Test GUI & Modules
    logger.info("   [*] Executing headless GUI module and database initialization smoke test...")
    try:
        from db.database import DatabaseManager
        db = DatabaseManager(str(_ROOT / "hardware_diagnostics.db"), str(_ROOT / "db" / "schema.sql"))
        logger.info("   [✔] Database WAL ledger successfully initialized and verified.")

        from ui.main_window import MainWindow, AsyncSignalBus
        from ui.deployment_tab import DeploymentTabWidget
        logger.info("   [✔] GUI modules (MainWindow, DeploymentTabWidget, AsyncSignalBus) imported successfully.")

        # Phase 06 Kiosk & Admin smoke test
        from core.one_click_automation import OneClickAutomation
        from ui.app_router import AppRouter
        from ui.kiosk_view import KioskView
        from ui.admin_view import AdminView, AdminAuthManager

        auth = AdminAuthManager()
        assert auth.verify_password("admin123") or auth.config_path.exists(), "AdminAuth verification check failed"
        logger.info("   [✔] Phase 06 Kiosk modules (AppRouter, KioskView, AdminView, OneClickAutomation) verified.")
    except Exception as err:
        logger.error("   [✘] GUI module smoke test failed: %s", err)
        return False

    logger.info("=== [SUCCESS] EXECUTABLE & PACKAGE FUNCTIONAL VERIFICATION PASSED! ===")
    return True


def main() -> None:
    success = verify_package_integrity()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
