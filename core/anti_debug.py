"""
Anti-Debugging, Process Scanner & Runtime Integrity Shield for SusetoDroidFixStudio.
Detects active native debuggers (IsDebuggerPresent / RemoteDebugger),
blacklisted reverse-engineering / USB sniffing processes (Wireshark, x64dbg, IDA Pro),
and verifies code segment memory hash integrity.
"""

from __future__ import annotations

import ctypes
import hashlib
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("anti_debug")

BLACKLISTED_PROCESSES: Set[str] = {
    "x64dbg.exe",
    "x32dbg.exe",
    "ida64.exe",
    "ida.exe",
    "ghidra.exe",
    "wireshark.exe",
    "usbpcapcmd.exe",
    "charles.exe",
    "fiddler.exe",
    "processhacker.exe",
    "cheatengine.exe",
    "scylla.exe",
    "scylla_x64.exe",
    "ollydbg.exe",
}


class AntiDebugEngine:
    """
    Continuous runtime anti-reversing and tamper detection engine.
    """

    def __init__(self, expected_binary_sha256: Optional[str] = None) -> None:
        self.expected_binary_sha256 = expected_binary_sha256
        self._tamper_detected = False

    @staticmethod
    def is_debugger_present() -> bool:
        """
        Check for attached debugger using Windows Win32 API IsDebuggerPresent.
        """
        if sys.platform.startswith("win"):
            try:
                kernel32 = ctypes.windll.kernel32
                if kernel32.IsDebuggerPresent():
                    return True

                is_remote = ctypes.c_bool(False)
                handle = kernel32.GetCurrentProcess()
                kernel32.CheckRemoteDebuggerPresent(handle, ctypes.byref(is_remote))
                if is_remote.value:
                    return True
            except Exception:
                pass
        return False

    @classmethod
    def scan_blacklisted_processes(
        cls,
        mock_process_list: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Scan active operating system processes for known reverse-engineering and USB sniffer tools.
        """
        detected: List[str] = []

        if mock_process_list is not None:
            for p in mock_process_list:
                if p.lower().strip() in BLACKLISTED_PROCESSES:
                    detected.append(p)
            return detected

        if sys.platform.startswith("win"):
            try:
                import subprocess
                out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, timeout=2.0)
                for line in out.splitlines():
                    parts = line.split(",")
                    if parts:
                        proc_name = parts[0].replace('"', "").lower().strip()
                        if proc_name in BLACKLISTED_PROCESSES:
                            detected.append(proc_name)
            except Exception:
                pass

        return detected

    def verify_runtime_integrity(self, binary_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate and compare current application binary hash against production baseline.
        """
        target = binary_path or sys.executable
        p = Path(target)

        if not p.exists():
            return {"status": "SKIPPED", "is_valid": True, "message": "Non-compiled execution"}

        hasher = hashlib.sha256()
        try:
            with open(target, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            current_hash = hasher.hexdigest().lower()

            if self.expected_binary_sha256:
                is_match = (current_hash == self.expected_binary_sha256.lower())
                return {
                    "status": "VALID" if is_match else "TAMPERED",
                    "is_valid": is_match,
                    "sha256": current_hash,
                }
            return {
                "status": "RECORDED",
                "is_valid": True,
                "sha256": current_hash,
            }
        except Exception as exc:
            return {"status": "ERROR", "is_valid": False, "message": str(exc)}

    def perform_full_security_audit(
        self,
        mock_processes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute comprehensive security check: debugger presence, sniffer processes, integrity.
        """
        debugger_active = self.is_debugger_present()
        suspicious_procs = self.scan_blacklisted_processes(mock_process_list=mock_processes)
        integrity = self.verify_runtime_integrity()

        is_threat_detected = debugger_active or bool(suspicious_procs) or (not integrity["is_valid"])

        if is_threat_detected:
            self._tamper_detected = True
            logger.critical(
                "SECURITY ALERT: Threat detected! Debugger=%s, SuspiciousProcesses=%s",
                debugger_active,
                suspicious_procs,
            )

        return {
            "threat_detected": is_threat_detected,
            "debugger_present": debugger_active,
            "suspicious_processes": suspicious_procs,
            "integrity": integrity,
            "is_secure": not is_threat_detected,
        }
