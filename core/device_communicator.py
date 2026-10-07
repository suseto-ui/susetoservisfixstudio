"""
Direct Port & USB Binding Communicator (`core/device_communicator.py`).
Provides direct physical binding to OS serial COM ports via PySerial and USB endpoints via PyUSB
with live packet transmission and strict error reporting.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("core.device_communicator")

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import usb.core
    import usb.util
    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False


class RealDeviceCommunicator:
    """
    Manages direct physical OS serial port and WinUSB endpoint communication
    without simulation or fallback mocks.
    """

    def __init__(self, port_name: str, baudrate: int = 115200, timeout: float = 2.0) -> None:
        self.port_name = port_name
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial_handle: Optional[Any] = None

    def connect_serial(self) -> bool:
        """Opens physical serial port handle."""
        if not SERIAL_AVAILABLE:
            raise ImportError("PySerial library is required for real hardware serial communication.")
        
        try:
            self._serial_handle = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            logger.info(f"Successfully opened physical serial port: {self.port_name} at {self.baudrate} baud.")
            return True
        except Exception as e:
            logger.error(f"Failed to open physical port {self.port_name}: {e}")
            raise ConnectionError(f"Could not bind to physical serial port {self.port_name}: {e}") from e

    def disconnect_serial(self) -> None:
        """Closes physical serial port handle."""
        if self._serial_handle and self._serial_handle.is_open:
            self._serial_handle.close()
            logger.info(f"Closed physical serial port: {self.port_name}")

    def write_packet(self, data: bytes) -> int:
        """Writes raw packet bytes to the physical serial port."""
        if not self._serial_handle or not self._serial_handle.is_open:
            raise ConnectionError(f"Serial port {self.port_name} is not open.")
        
        written = self._serial_handle.write(data)
        self._serial_handle.flush()
        return written

    def read_packet(self, size: int = 1024) -> bytes:
        """Reads raw packet bytes from the physical serial port."""
        if not self._serial_handle or not self._serial_handle.is_open:
            raise ConnectionError(f"Serial port {self.port_name} is not open.")
        
        return self._serial_handle.read(size)

    @staticmethod
    def find_usb_device(id_vendor: int, id_product: int) -> Any:
        """Locates physical USB device via PyUSB WinUSB backend."""
        if not USB_AVAILABLE:
            raise ImportError("PyUSB library is required for direct WinUSB device access.")
        
        device = usb.core.find(idVendor=id_vendor, idProduct=id_product)
        if device is None:
            raise ValueError(f"Physical USB device with Vendor ID 0x{id_vendor:04X} and Product ID 0x{id_product:04X} not found.")
        return device
