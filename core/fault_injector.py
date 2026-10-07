"""
Hardware Fault Injector for robust resilience testing and error recovery validation.
Simulates line noise, bit flips, frame drops, and sudden hardware disconnects.
"""

from __future__ import annotations

import random
from typing import Optional
from val.base_adapter import BaseDeviceAdapter


class HardwareFaultInjector:
    """
    Simulation utility for injecting communication faults into serial streams.
    """

    @staticmethod
    def inject_noise(buffer: bytes, error_rate: float = 0.05) -> bytes:
        """
        Inject random bit flips / corruption into buffer bytes based on error_rate (0.0 to 1.0).
        """
        if error_rate <= 0.0:
            return buffer

        mutable_buf = bytearray(buffer)
        for i in range(len(mutable_buf)):
            if random.random() < error_rate:
                # Flip random bits or corrupt byte
                mutable_buf[i] ^= random.randint(1, 255)
        return bytes(mutable_buf)

    @staticmethod
    async def simulate_disconnect(adapter: BaseDeviceAdapter) -> None:
        """
        Simulate sudden device detachment during active session.
        """
        if hasattr(adapter, "ser") and adapter.ser and hasattr(adapter.ser, "close"):
            try:
                adapter.ser.close()
            except Exception:
                pass
        if hasattr(adapter, "port"):
            adapter.port = "DISCONNECTED"
