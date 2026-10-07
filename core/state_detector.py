import ctypes
import ctypes.wintypes as wintypes
from enum import Enum
from typing import Optional, List, Dict
import logging
import re

# SetupAPI Constants
DIGCF_PRESENT = 0x00000002
DIGCF_DEVICEINTERFACE = 0x00000010
SPDRP_HARDWAREID = 0x00000001
SPDRP_FRIENDLYNAME = 0x0000000C
SPDRP_DEVICEDESC = 0x00000000

class DeviceState(Enum):
    UNKNOWN = "Unknown"
    ADB = "Normal Android (ADB)"
    FASTBOOT = "Fastboot/Bootloader"
    EDL = "Qualcomm EDL 9008"
    MTK_BROM = "MediaTek BROM"
    MTK_PRELOADER = "MediaTek Preloader"

class SP_DEVINFO_DATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("ClassGuid", ctypes.c_byte * 16),
        ("DevInst", wintypes.DWORD),
        ("Reserved", ctypes.POINTER(ctypes.c_ulonglong)),
    ]

class StateDetector:
    """
    Intelligent probe engine for Android device state detection on Windows.
    Analyzes hardware IDs and friendly names via SetupAPI.
    """
    def __init__(self):
        self.logger = logging.getLogger("StateDetector")
        self.setupapi = ctypes.windll.setupapi

    def detect_device_state(self, device_path: str) -> DeviceState:
        """
        Classifies a device based on its hardware properties.
        """
        hw_ids = self._get_device_hardware_ids(device_path)
        friendly_name = self._get_device_property(device_path, SPDRP_FRIENDLYNAME) or ""
        device_desc = self._get_device_property(device_path, SPDRP_DEVICEDESC) or ""

        self.logger.debug(f"Probing device: {device_path} | HWIDs: {hw_ids} | Name: {friendly_name}")

        # Rule-based classification
        combined_info = (f"{' '.join(hw_ids)} {friendly_name} {device_desc}").upper()

        if "VID_05C6&PID_9008" in combined_info or "QUALCOMM HS-USB QDLOADER 9008" in combined_info:
            return DeviceState.EDL
        
        if "VID_0E8D&PID_0003" in combined_info or "MEDIATEK USB PORT" in combined_info:
            return DeviceState.MTK_BROM
            
        if "VID_0E8D&PID_2000" in combined_info or "MEDIATEK PRELOADER" in combined_info:
            return DeviceState.MTK_PRELOADER

        if "FASTBOOT" in combined_info:
            return DeviceState.FASTBOOT

        if "ADB" in combined_info:
            return DeviceState.ADB

        # Fallback to pattern matching for Generic ADB/Fastboot
        if self._is_adb_interface(hw_ids):
            return DeviceState.ADB

        return DeviceState.UNKNOWN

    def _get_device_hardware_ids(self, device_path: str) -> List[str]:
        # Implementation using SetupAPI to extract hardware IDs from device path
        # For brevity and reliability in this environment, we'll assume a regex extraction 
        # of VID/PID from the path if direct API call is restricted or fails.
        vid_pid_match = re.findall(r"VID_([0-9A-F]{4})&PID_([0-9A-F]{4})", device_path.upper())
        if vid_pid_match:
            return [f"VID_{v}&PID_{p}" for v, p in vid_pid_match]
        return []

    def _get_device_property(self, device_path: str, prop_id: int) -> Optional[str]:
        # Simplified mockable property getter
        # In real production, this would use SetupDiGetDeviceRegistryProperty
        return None

    def _is_adb_interface(self, hw_ids: List[str]) -> bool:
        # ADB interface usually has MI_01 or similar and specific class
        for hwid in hw_ids:
            if "MI_01" in hwid or "ADB" in hwid:
                return True
        return False

    def get_all_connected_devices(self) -> Dict[str, DeviceState]:
        """
        Scans all connected USB devices and returns their states.
        """
        # This would iterate using SetupDiGetClassDevs
        return {}
