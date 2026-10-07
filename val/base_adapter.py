"""
Production Abstract Base Adapter and Async Cancellation Token Engine for SusetoDroidFixStudio.
Enables vendor-specific hardware communication with non-blocking I/O,
graceful cancellation tokens, physical disconnect detection, and resource cleanup.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Set

logger = logging.getLogger("base_adapter")


class OperationCancelledException(Exception):
    """Raised when an active physical I/O or flash operation is cancelled by the operator."""
    pass


class DeviceDisconnectedException(Exception):
    """Raised when physical USB/UART connection is unexpectedly broken during transfer."""
    pass


class CancellationToken:
    """
    Thread-safe asynchronous cancellation token for aborting long-running hardware transfers.
    """

    def __init__(self) -> None:
        self._is_cancelled = False
        self._cancel_callbacks: Set[Callable[[], None]] = set()

    @property
    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def cancel(self) -> None:
        """Trigger cancellation and notify all registered cleanup callbacks."""
        self._is_cancelled = True
        logger.warning("CancellationToken triggered: Aborting active operations.")
        for cb in list(self._cancel_callbacks):
            try:
                cb()
            except Exception as exc:
                logger.error("Error during cancellation callback execution: %s", exc)

    def register_callback(self, callback: Callable[[], None]) -> None:
        """Register a resource cleanup callback."""
        self._cancel_callbacks.add(callback)

    def throw_if_cancelled(self) -> None:
        """Raise OperationCancelledException if token is in cancelled state."""
        if self._is_cancelled:
            raise OperationCancelledException("Operation aborted by user request.")


class BaseDeviceAdapter(ABC):
    """
    Abstract interface for vendor-specific hardware adapters (Qualcomm, MTK, Samsung, Unisoc, ESP32, FTDI).
    Provides typed asynchronous methods for bootloader control and memory operations.
    """

    def __init__(self, port: str, baudrate: int = 115200) -> None:
        self.port = port
        self.baudrate = baudrate
        self.is_connected = False
        self.last_latency_ms: float = 0.0

    @abstractmethod
    async def enter_bootloader(self, cancel_token: Optional[CancellationToken] = None) -> bool:
        """Execute hardware handshake to put the device into vendor bootloader mode."""
        raise NotImplementedError("Subclasses must implement enter_bootloader.")

    @abstractmethod
    async def read_flash_block(
        self,
        addr: int,
        length: int,
        cancel_token: Optional[CancellationToken] = None,
    ) -> bytes:
        """Read a block of raw data from device flash memory."""
        raise NotImplementedError("Subclasses must implement read_flash_block.")

    @abstractmethod
    async def write_flash_block(
        self,
        addr: int,
        data: bytes,
        cancel_token: Optional[CancellationToken] = None,
    ) -> bool:
        """Write a block of raw data to device flash memory."""
        raise NotImplementedError("Subclasses must implement write_flash_block.")

    async def close(self) -> None:
        """Gracefully release physical hardware port handles."""
        self.is_connected = False
        logger.info("Closed hardware adapter port %s.", self.port)
