"""
Unit Test Suite for build_exe.py:
Verifies PyInstaller standalone single-executable configuration, administrative manifest generation,
core/ engine module bundling, and standalone .exe artifact output.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from build_exe import AdminManifestGenerator, StandaloneExeBuilder


class TestBuildExe(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.root_path = Path(self.tmp_dir.name)
        self.builder = StandaloneExeBuilder(root_dir=self.root_path, app_name="SusetoDroidFixStudio")

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_admin_manifest_generation(self) -> None:
        """Verify generated XML manifest contains requireAdministrator privileges and OS compatibility."""
        manifest_xml = AdminManifestGenerator.generate_manifest_xml(
            app_name="SusetoDroidFixStudio",
            description="Testing Manifest",
        )
        self.assertIn("requireAdministrator", manifest_xml)
        self.assertIn("requestedExecutionLevel", manifest_xml)
        self.assertIn("uiAccess=\"false\"", manifest_xml)
        self.assertIn("supportedOS", manifest_xml)

        out_path = self.root_path / "test_manifest.xml"
        saved_path = AdminManifestGenerator.write_manifest(
            out_path,
            app_name="SusetoDroidFixStudio",
            description="Testing Manifest",
        )
        self.assertTrue(saved_path.exists())
        self.assertEqual(saved_path.read_text(encoding="utf-8"), manifest_xml)

    def test_collect_core_hidden_imports(self) -> None:
        """Verify dynamic scanning and hidden imports collection of core engine modules."""
        # Create mock core files
        core_dir = self.root_path / "core"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "one_click_automation.py").write_text("# mock", encoding="utf-8")
        (core_dir / "orchestrator.py").write_text("# mock", encoding="utf-8")

        imports = self.builder.collect_core_hidden_imports()
        self.assertIn("core.one_click_automation", imports)
        self.assertIn("core.orchestrator", imports)
        self.assertIn("storage.wal_ledger", imports)
        self.assertIn("val.base_adapter", imports)
        self.assertIn("ui.app_router", imports)

    def test_collect_data_specs(self) -> None:
        """Verify data paths for PyInstaller --add-data."""
        core_dir = self.root_path / "core"
        core_dir.mkdir(parents=True, exist_ok=True)
        db_dir = self.root_path / "db"
        db_dir.mkdir(parents=True, exist_ok=True)
        (db_dir / "schema.sql").write_text("CREATE TABLE test (id INT);", encoding="utf-8")

        specs = self.builder.collect_data_specs()
        spec_text = " ".join(specs)
        self.assertIn("core", spec_text)
        self.assertIn("db", spec_text)

    def test_standalone_exe_build_and_verification(self) -> None:
        """Verify complete standalone single-file executable compilation and validation."""
        (self.root_path / "main.py").write_text("print('Hello Standalone')", encoding="utf-8")
        core_dir = self.root_path / "core"
        core_dir.mkdir(parents=True, exist_ok=True)
        (core_dir / "engine.py").write_text("# engine code", encoding="utf-8")

        success = self.builder.build_standalone_executable()
        self.assertTrue(success)

        # Verify manifest generated
        self.assertTrue(self.builder.manifest_path.exists())
        manifest_content = self.builder.manifest_path.read_text(encoding="utf-8")
        self.assertIn("requireAdministrator", manifest_content)

        # Verify target executable in dist/
        exe_file = self.builder.dist_dir / "SusetoDroidFixStudio.exe"
        self.assertTrue(exe_file.exists())
        self.assertGreater(exe_file.stat().st_size, 1024)

        # Verify content contains PE signature and embedded manifest marker
        content = exe_file.read_bytes()
        self.assertTrue(content.startswith(b"MZ"))
        self.assertIn(b"requireAdministrator", content)


if __name__ == "__main__":
    unittest.main()
