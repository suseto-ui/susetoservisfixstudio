"""
Unit & Integration Test Suite for production_build.py:
Verifies staging of native FTDI/CP210x/SetupAPI DLLs, SQLite schema, PyInstaller spec generation,
and self-contained distribution verification.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from production_build import UnifiedProductionPackager


class TestProductionBuildPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.packager = UnifiedProductionPackager(root_dir=Path(self.tmp_dir.name))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_stage_native_dependencies(self):
        """Verify native DLLs (FTDI, CP210x, WinUSB) and SQLite schema are staged in tmp dir."""
        self.packager.stage_native_dependencies()

        drivers_dir = Path(self.tmp_dir.name) / "drivers"
        self.assertTrue(drivers_dir.exists())
        self.assertTrue((drivers_dir / "ftd2xx64.dll").exists())
        self.assertTrue((drivers_dir / "silabser64.dll").exists())
        self.assertTrue((drivers_dir / "setupapi_x64.dll").exists())
        self.assertTrue((drivers_dir / "winusb_setup.cmd").exists())

        db_dir = Path(self.tmp_dir.name) / "db"
        self.assertTrue(db_dir.exists())
        self.assertTrue((db_dir / "schema.sql").exists())

    def test_generate_spec_file(self):
        """Verify PyInstaller spec file is generated with correct data bindings."""
        self.packager.stage_native_dependencies()
        (Path(self.tmp_dir.name) / "main.py").write_text("print('Mock main')", encoding="utf-8")

        spec_path = self.packager.generate_spec_file()
        self.assertTrue(spec_path.exists())

        spec_text = spec_path.read_text(encoding="utf-8")
        self.assertIn("SusetoDroidFixStudio", spec_text)
        self.assertIn("core.one_click_automation", spec_text)
        self.assertIn("ui.kiosk_view", spec_text)
        self.assertIn("ui.admin_view", spec_text)
        self.assertIn("ui.app_router", spec_text)

    def test_build_and_verify_distribution(self):
        """Verify end-to-end distribution packaging and artifact verification."""
        self.packager.stage_native_dependencies()
        (Path(self.tmp_dir.name) / "main.py").write_text("print('Mock main')", encoding="utf-8")
        self.packager.generate_spec_file()

        is_valid = self.packager.build_distribution()
        self.assertTrue(is_valid)

        dist_dir = Path(self.tmp_dir.name) / "dist" / "SusetoDroidFixStudio"
        self.assertTrue(dist_dir.exists())
        self.assertTrue((dist_dir / "db" / "schema.sql").exists() or (dist_dir / "_internal" / "db" / "schema.sql").exists())
        self.assertTrue((dist_dir / "SusetoDroidFixStudio.exe").exists())


if __name__ == "__main__":
    unittest.main()
