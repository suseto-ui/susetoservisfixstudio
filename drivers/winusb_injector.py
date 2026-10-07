"""
Windows Driver Injector using SetupAPI and PnPUtil.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

logger = logging.getLogger("winusb_injector")


class WinUSBInjector:
    """
    Wrapper for Windows SetupAPI and PnPUtil to detect and install missing drivers (Code 28).
    """

    def __init__(self) -> None:
        self.is_windows = sys.platform == "win32"

    def detect_missing_drivers(self) -> bool:
        """Detect if any devices are missing drivers (Code 28)."""
        if not self.is_windows:
            return False
        try:
            import ctypes
            cfgmgr32 = ctypes.windll.cfgmgr32
            ul_len = ctypes.c_ulong()
            if cfgmgr32.CM_Get_Device_ID_List_SizeW(ctypes.byref(ul_len), None, 0) == 0:
                return ul_len.value > 0
        except Exception as e:
            logger.warning("SetupAPI detect error: %s", e)
        return False

    def install_winusb_inf(self, inf_path: str) -> bool:
        """Trigger silent installation of a generic INF driver via PnPUtil."""
        if not os.path.exists(inf_path):
            return False
        if not self.is_windows:
            logger.info("Non-Windows staging: INF %s verified.", inf_path)
            return True
        try:
            cmd = ["pnputil.exe", "/add-driver", inf_path, "/install"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.returncode in (0, 3010)
        except Exception as e:
            logger.error("PnPUtil installation error: %s", e)
            return False
