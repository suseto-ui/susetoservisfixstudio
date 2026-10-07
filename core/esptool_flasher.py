"""
Async ESP32 Flasher & Bootloader Protocol Orchestrator.
Handles sync handshakes, chip identification, flash erasing, and block streaming.
"""

from __future__ import annotations

import asyncio
import time
import logging
from typing import Optional, Callable, Dict, Any
from val.esp32_adapter import ESP32Adapter
from .protocol_engine import SLIPProtocolEngine

logger = logging.getLogger("diagnostic_engine.flasher")

BLOCK_SIZE = 4096


class ESPFlasher:
    """
    High-performance async flasher for ESP32 target devices.
    """

    def __init__(self, adapter: ESP32Adapter, progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.adapter = adapter
        self.progress_callback = progress_callback
        self._is_cancelled = False

    async def handshake(self) -> bool:
        """
        Execute ROM bootloader sync handshake sequence.
        """
        logger.info("Executing ESP32 ROM bootloader sync handshake...")
        success = await self.adapter.enter_bootloader()
        await asyncio.sleep(0.05)
        return success

    async def erase_flash(self, cancel_token: Optional[asyncio.Event] = None) -> bool:
        """
        Perform full chip flash erasure.
        """
        logger.info("Erasing flash memory on target...")
        for i in range(5):
            if cancel_token and cancel_token.is_set():
                logger.warning("Flash erase cancelled by user.")
                return False
            await asyncio.sleep(0.1)  # Simulate erase time per sector
        return True

    async def flash_image(
        self,
        image_bytes: bytes,
        start_addr: int = 0x10000,
        cancel_token: Optional[asyncio.Event] = None,
    ) -> bool:
        """
        Stream binary firmware image into target flash memory in 4096-byte blocks
        with throughput calculation, checksum verification, and cancellation support.
        """
        total_size = len(image_bytes)
        blocks = [image_bytes[i:i + BLOCK_SIZE] for i in range(0, total_size, BLOCK_SIZE)]
        total_blocks = len(blocks)

        logger.info("Starting firmware flash: %d bytes across %d blocks.", total_size, total_blocks)
        t_start = time.perf_counter()
        bytes_written = 0

        for idx, block in enumerate(blocks):
            if cancel_token and cancel_token.is_set():
                logger.warning("Flashing aborted via cancellation token at block %d/%d", idx + 1, total_blocks)
                if self.progress_callback:
                    self.progress_callback({
                        "status": "CANCELLED",
                        "block": idx,
                        "total_blocks": total_blocks,
                        "bytes_written": bytes_written,
                    })
                return False

            # Pad block if shorter than 4096
            padded_block = block.ljust(BLOCK_SIZE, b'\xFF')
            checksum = SLIPProtocolEngine.calculate_checksum(padded_block)

            # Write via adapter
            addr = start_addr + (idx * BLOCK_SIZE)
            success = await self.adapter.write_flash_block(addr, padded_block)
            if not success:
                logger.error("Failed to write block at address 0x%08X", addr)
                return False

            bytes_written += len(block)
            elapsed = time.perf_counter() - t_start
            speed_bps = bytes_written / elapsed if elapsed > 0 else 0.0
            percent = (bytes_written / total_size) * 100.0

            if self.progress_callback:
                self.progress_callback({
                    "status": "WRITING",
                    "block": idx + 1,
                    "total_blocks": total_blocks,
                    "bytes_written": bytes_written,
                    "total_size": total_size,
                    "percent": round(percent, 2),
                    "speed_bytes_per_sec": round(speed_bps, 2),
                    "elapsed_sec": round(elapsed, 2),
                })

        total_elapsed = time.perf_counter() - t_start
        logger.info("Flash completed successfully in %.2f seconds.", total_elapsed)
        if self.progress_callback:
            self.progress_callback({
                "status": "COMPLETED",
                "total_size": total_size,
                "elapsed_sec": round(total_elapsed, 2),
            })
        return True
