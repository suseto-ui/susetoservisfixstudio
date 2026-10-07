"""
Dynamic Model Profiler for platform and hardware partition definition profiles.
Reads/writes model characteristics including memory block boundaries, addresses, page sizes, and unlock codes.
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional


class DynamicModelProfiler:
    """
    Manages structured model configuration profiles.
    Allows targeting specific custom memory-mapped and platform-specific partitions.
    """

    DEFAULT_PROFILES = {
        "esp32_wroom_32e": {
            "vendor": "Espressif",
            "flash_size_bytes": 4194304,
            "page_size_bytes": 4096,
            "bootloader_addr": 0x1000,
            "user_partition_addr": 0x10000,
            "requires_unlock": False
        },
        "stm32f407_dfu": {
            "vendor": "STMicroelectronics",
            "flash_size_bytes": 1048576,
            "page_size_bytes": 16384,
            "bootloader_addr": 0x08000000,
            "user_partition_addr": 0x08008000,
            "requires_unlock": True,
            "unlock_payload": "0x41524F4D"
        },
        "qualcomm_sd888_edl": {
            "vendor": "Qualcomm",
            "flash_size_bytes": 137438953472, # 128 GB eMMC/UFS
            "page_size_bytes": 524288,       # 512 KB Block Size
            "bootloader_addr": 0x0,
            "user_partition_addr": 0x8000,
            "requires_unlock": True,
            "unlock_payload": "0x53414841"
        }
    }

    def __init__(self):
        self.active_profiles: Dict[str, Dict[str, Any]] = dict(self.DEFAULT_PROFILES)

    def get_profile(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get the platform partition layout for a registered model ID."""
        return self.active_profiles.get(model_id)

    def register_profile(self, model_id: str, configuration: Dict[str, Any]) -> None:
        """Dynamically add or override a hardware profile definition."""
        self.active_profiles[model_id] = configuration

    def serialize_profiles_json(self) -> str:
        """Output active configurations as standardized JSON layout payload."""
        return json.dumps(self.active_profiles, indent=2)
