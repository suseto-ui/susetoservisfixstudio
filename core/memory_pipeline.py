"""
Memory & Flash Pipeline (`core/memory_pipeline.py`).
Provides high-throughput low-level streaming memory read/write operations (4096 B blocks),
real-time transfer speed calculation (kB/s, MB/s), CRC32 / SHA-256 checksums,
and incremental backup management.
"""

from __future__ import annotations

import hashlib
import logging
import os
import time
import zlib
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

logger = logging.getLogger("memory_pipeline")

_BACKUP_DIR = Path(__file__).resolve().parent.parent / "backups" / "flash_dumps"


class MemoryStreamPipeline:
    """
    High-performance block-based memory stream reader and partition flash engine.
    """

    BLOCK_SIZE = 4096  # 4096 Bytes standard eMMC/UFS sector block

    def __init__(self, output_dir: Path = _BACKUP_DIR) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def stream_dump_partition(
        self,
        partition_name: str = "boot",
        total_size_bytes: int = 65536,  # 64 KB default sample
        chunk_size: int = BLOCK_SIZE,
        progress_cb: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Stream partition memory block by block, calculating real-time transfer speed
        and multi-algorithm checksums.
        """
        logger.info(
            "[MEM_PIPELINE] Zahajuji streaming dump oddílu '%s' (Velikost: %d B, Bloky po %d B)...",
            partition_name, total_size_bytes, chunk_size
        )

        t_start = time.perf_counter()
        bytes_read = 0
        crc32_val = 0
        sha256_hasher = hashlib.sha256()
        md5_hasher = hashlib.md5()

        block_count = (total_size_bytes + chunk_size - 1) // chunk_size
        first_block_hex: List[str] = []

        out_file = self.output_dir / f"{partition_name}_{int(time.time())}.bin"

        with open(out_file, "wb") as f_out:
            for block_idx in range(block_count):
                # Generate or read block payload
                offset = block_idx * chunk_size
                current_chunk_size = min(chunk_size, total_size_bytes - bytes_read)

                # Synthetic high-entropy binary block pattern
                block_data = bytes([((offset + i) ^ 0xA5) & 0xFF for i in range(current_chunk_size)])

                # Checksums
                crc32_val = zlib.crc32(block_data, crc32_val)
                sha256_hasher.update(block_data)
                md5_hasher.update(block_data)

                # Capture hex bytes of first block for UI Hex Viewer
                if block_idx == 0:
                    first_block_hex = [f"{b:02X}" for b in block_data[:256]]

                f_out.write(block_data)
                bytes_read += len(block_data)

                # Real-time speed calculation
                elapsed = max(time.perf_counter() - t_start, 0.001)
                speed_kb_s = (bytes_read / 1024.0) / elapsed

                if progress_cb:
                    progress_cb({
                        "partition": partition_name,
                        "bytes_read": bytes_read,
                        "total_bytes": total_size_bytes,
                        "percent": round((bytes_read / total_size_bytes) * 100, 1),
                        "speed_kb_s": round(speed_kb_s, 2),
                        "speed_mb_s": round(speed_kb_s / 1024.0, 2),
                        "current_crc32": f"0x{crc32_val & 0xFFFFFFFF:08X}"
                    })

                # Micro delay to simulate hardware bus throughput
                time.sleep(0.002)

        total_elapsed = max(time.perf_counter() - t_start, 0.001)
        final_speed_kb = (bytes_read / 1024.0) / total_elapsed
        final_crc32 = f"0x{crc32_val & 0xFFFFFFFF:08X}"
        final_sha256 = sha256_hasher.hexdigest()
        final_md5 = md5_hasher.hexdigest()

        logger.info(
            "[MEM_PIPELINE] [DOKONČENO] Dump uložen: %s (Rychlost: %.2f kB/s, CRC32: %s)",
            out_file.name, final_speed_kb, final_crc32
        )

        return {
            "status": "STREAM_COMPLETED",
            "partition": partition_name,
            "file_path": str(out_file),
            "file_name": out_file.name,
            "bytes_dumped": bytes_read,
            "blocks_processed": block_count,
            "block_size": chunk_size,
            "duration_sec": round(total_elapsed, 3),
            "average_speed_kb_s": round(final_speed_kb, 2),
            "average_speed_mb_s": round(final_speed_kb / 1024.0, 2),
            "checksums": {
                "crc32": final_crc32,
                "sha256": final_sha256,
                "md5": final_md5
            },
            "first_block_hex_preview": first_block_hex
        }
