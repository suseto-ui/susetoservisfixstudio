# DroidFixAutomator - External Plugin & Vendor Adapter API Guide

Welcome to the **DroidFixAutomator** Plugin Development Guide. This document explains how third-party developers, hardware engineers, and technicians can extend DroidFixAutomator with custom OEM / Chipset Vendor Adapters without recompiling the main application executable.

---

## 🚀 Architecture Overview

DroidFixAutomator uses a **Dynamic Plugin Loader** (`core/plugin_manager.py`) that scans the `plugins/` folder at startup or on demand. Any `.py` file placed in the `plugins/` directory that inherits from `BaseDeviceAdapter` is automatically detected, validated, and registered into the active diagnostic cockpit.

```
plugins/
├── custom_spreadtrum_adapter.py
├── custom_realme_brom_adapter.py
└── custom_mediatek_v6_adapter.py
```

---

## 🛠️ Step-by-Step Developer Tutorial

### 1. Inherit from `BaseDeviceAdapter`

All plugins must subclass `adapters.base_adapter.BaseDeviceAdapter` and implement its abstract hardware interaction methods:

```python
from __future__ import annotations
import logging
import time
from typing import Optional
from adapters.base_adapter import BaseDeviceAdapter

logger = logging.getLogger("plugins.custom_spreadtrum")

class SpreadtrumUnisocAdapter(BaseDeviceAdapter):
    """
    Custom OEM Vendor Adapter plugin for Spreadtrum / Unisoc BootROM handshake.
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200) -> None:
        super().__init__(port=port, baudrate=baudrate)
        self.chip_id = "SC9863A"

    def connect(self, port: str, baudrate: int) -> bool:
        """Establish physical USB/COM connection and send Spreadtrum 0x7E sync frame."""
        self.port = port
        self.baudrate = baudrate
        logger.info(f"[SPREADTRUM] Sending 0x7E handshake frame to {port} at {baudrate} baud...")
        # Custom serial handshake code
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        """Cleanly close handles and reset lines."""
        if self.is_connected:
            logger.info(f"[SPREADTRUM] Disconnecting port {self.port}...")
            self.is_connected = False

    def send_command(self, cmd: int, data: bytes) -> bytes:
        """Send vendor HDLC/SLIP command packet and return response."""
        logger.info(f"[SPREADTRUM] CMD 0x{cmd:02X} sent ({len(data)} B payload).")
        return b"\x7E\x00\x00\x7E"

    def read_flash_block(self, address: int, length: int) -> bytes:
        """Read raw eMMC/UFS memory sector block."""
        logger.info(f"[SPREADTRUM] Reading {length} bytes from 0x{address:08X}...")
        return b"\x00" * length

    def write_flash_block(self, address: int, data: bytes) -> bool:
        """Program raw binary payload into target flash sector."""
        logger.info(f"[SPREADTRUM] Flashing {len(data)} bytes to 0x{address:08X}...")
        return True

    def erase_partition(self, partition_name: str) -> bool:
        """Erase specific partition (e.g. 'frp', 'userdata')."""
        logger.info(f"[SPREADTRUM] Erasing partition '{partition_name}'...")
        return True
```

---

## 📂 Installation & Dynamic Loading

1. Save your Python script in the `plugins/` folder (e.g. `plugins/spreadtrum_adapter.py`).
2. Launch or restart **DroidFixAutomator** (or trigger `plugin_loader.load_all_plugins()`).
3. Your new adapter will automatically appear in the **Hardware & Drivers** and **Auto-Routing** cockpits.

---

## ⚡ Key Benefits

- **Zero Recompilation**: Add new device support on the fly in production environments.
- **Strict Validation**: Invalid plugins that fail type or inheritance checks are safely isolated without crashing the host application.
- **Asynchronous Execution**: All hardware reads and writes run on background worker threads managed by `EventRouter`.
