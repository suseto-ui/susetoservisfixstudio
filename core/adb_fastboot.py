"""
ADB and Fastboot Hardware Bridge (`core/adb_fastboot.py`).
Executes native ADB / Fastboot commands using system PATH or bundled binaries in `bin/`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

_ROOT = Path(__file__).resolve().parent.parent


class ADBFastbootBridge:
    """
    Executes native CLI command utilities safely without shell=True to avoid injection risks.
    Handles device listing, reboots, and status polling.
    """

    @classmethod
    def resolve_binary(cls, tool_name: str) -> str:
        """Find executable in PATH or project bin/ directory."""
        exe_ext = ".exe" if sys.platform.startswith("win") else ""
        tool_with_ext = f"{tool_name}{exe_ext}"

        # 1. Check project bin folder
        local_bin = _ROOT / "bin" / tool_with_ext
        if local_bin.exists():
            return str(local_bin)

        local_bin_noext = _ROOT / "bin" / tool_name
        if local_bin_noext.exists():
            return str(local_bin_noext)

        # 2. Check installed C:\SusetoFix\bin
        suseto_bin = Path(r"C:\SusetoFix\bin") / tool_with_ext
        if suseto_bin.exists():
            return str(suseto_bin)

        # 3. Check system PATH
        system_bin = shutil.which(tool_name) or shutil.which(tool_with_ext)
        if system_bin:
            return system_bin

        return tool_name

    @classmethod
    def execute_command(cls, command: List[str]) -> Tuple[bool, str]:
        """Safely execute command with resolved binary path."""
        try:
            if not command:
                return False, "Prázdný příkaz"

            cmd = list(command)
            binary_name = cmd[0]
            if binary_name in ("adb", "fastboot"):
                cmd[0] = cls.resolve_binary(binary_name)

            if cmd[0] == "echo" and sys.platform.startswith("win"):
                cmd = [sys.executable, "-c", "import sys; print(' '.join(sys.argv[1:]))"] + cmd[1:]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout if result.stdout else result.stderr
            return result.returncode == 0, output
        except Exception as e:
            return False, f"Chyba při provádění příkazu: {str(e)}"

    def get_adb_devices(self) -> str:
        """Run adb devices query."""
        _, out = self.execute_command(["adb", "devices"])
        return out

    def get_fastboot_devices(self) -> str:
        """Run fastboot devices query."""
        _, out = self.execute_command(["fastboot", "devices"])
        return out

    def reboot_bootloader(self) -> str:
        """Reboot connected ADB device into fastboot bootloader mode."""
        _, out = self.execute_command(["adb", "reboot", "bootloader"])
        return out
