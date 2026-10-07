"""
Streaming Memory Dump and CRC/SHA256 Integrity Engine.
Writes high-speed diagnostic streams directly to disk using memory-mapped I/O (mmap).
"""

from __future__ import annotations

import os
import mmap
import zlib
import hashlib
from typing import Dict, Any, Callable, Optional


class StreamingDumpEngine:
    """
    Manages physical-layer hardware memory readout pipelines, writes blocks using mmap,
    and updates validation hashes continuously during streaming.
    """

    def __init__(self, output_filepath: str, total_bytes: int, block_size: int = 65536):
        self.filepath = output_filepath
        self.total_bytes = total_bytes
        self.block_size = block_size
        self.bytes_written = 0
        self.crc_accumulator = 0
        self.sha256_hasher = hashlib.sha256()

    def start_dump(self, data_source: Callable[[int, int], bytes]) -> Dict[str, Any]:
        """
        Stream binary blocks from source callable directly to memory-mapped disk storage.
        """
        # Create file with desired capacity
        with open(self.filepath, "wb") as f:
            f.write(b"\x00" * self.total_bytes)

        # Open and map the file into RAM space
        with open(self.filepath, "r+b") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
                while self.bytes_written < self.total_bytes:
                    remaining = self.total_bytes - self.bytes_written
                    chunk_len = min(self.block_size, remaining)

                    # Query raw data block from adapter read stream
                    block = data_source(self.bytes_written, chunk_len)
                    
                    # Update hashes
                    self.crc_accumulator = zlib.crc32(block, self.crc_accumulator)
                    self.sha256_hasher.update(block)

                    # Write block directly to memory-mapped block
                    mm[self.bytes_written : self.bytes_written + chunk_len] = block
                    self.bytes_written += chunk_len
                    mm.flush()

        return {
            "status": "COMPLETED",
            "total_bytes": self.bytes_written,
            "crc32": f"0x{self.crc_accumulator & 0xFFFFFFFF:08X}",
            "sha256": self.sha256_hasher.hexdigest(),
        }
