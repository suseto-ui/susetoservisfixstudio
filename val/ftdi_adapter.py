"""
FTDI Device Adapter.
"""

from .base_adapter import BaseDeviceAdapter

class FTDIAdapter(BaseDeviceAdapter):
    """
    Adapter for FTDI-based hardware devices.
    """

    def __init__(self, port: str):
        self.port = port

    async def enter_bootloader(self) -> bool:
        """FTDI-specific bootloader entry routine."""
        return True

    async def read_flash_block(self, addr: int, length: int) -> bytes:
        """FTDI flash read implementation."""
        return b'\x00' * length

    async def write_flash_block(self, addr: int, data: bytes) -> bool:
        """FTDI flash write implementation."""
        return True
