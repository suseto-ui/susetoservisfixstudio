"""
Vendor Abstraction Layer (VAL) - Base Device Adapter Interface.
Defines standard low-level hardware abstraction methods for flashing,
memory reading, block writing, and partition management.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class BaseDeviceAdapter(ABC):
    """
    Abstract Base Class defining the unified hardware protocol interface
    for vendor-specific adapters (Qualcomm EDL, MediaTek BROM, Unisoc, etc.).
    """

    def __init__(self, port: Optional[str] = None, baudrate: int = 115200) -> None:
        self.port: Optional[str] = port
        self.baudrate: int = baudrate
        self.is_connected: bool = False

    @abstractmethod
    def connect(self, port: str, baudrate: int) -> bool:
        """
        Establish connection to physical serial/USB device port at specified baud rate.
        Returns True if connection and initial handshakes succeeded.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close physical COM/USB connection and free system handles."""
        pass

    @abstractmethod
    def send_command(self, cmd: int, data: bytes) -> bytes:
        """
        Dispatch vendor-specific command packet and return response payload.
        """
        pass

    @abstractmethod
    def read_flash_block(self, address: int, length: int) -> bytes:
        """
        Read raw binary block of length bytes starting from physical flash address.
        """
        pass

    @abstractmethod
    def write_flash_block(self, address: int, data: bytes) -> bool:
        """
        Program/write data buffer into physical flash memory block at target address.
        """
        pass

    @abstractmethod
    def erase_partition(self, partition_name: str) -> bool:
        """
        Erase complete partition volume identified by partition name or label.
        """
        pass

    def __enter__(self) -> BaseDeviceAdapter:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.disconnect()
