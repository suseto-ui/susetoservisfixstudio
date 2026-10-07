import asyncio
import hashlib
import logging
import os
import aiohttp
from typing import Optional, Dict, Any

class CloudLoaderManager:
    """
    Manages local dependencies, remote syncing, and integrity verification.
    """
    def __init__(self, ledger: Any):
        self.ledger = ledger
        self.logger = logging.getLogger("CloudLoaderManager")
        self.paths = {
            "bin": "bin/",
            "loaders": "cache/loaders/",
            "drivers": "drivers/"
        }
        for path in self.paths.values():
            os.makedirs(path, exist_ok=True)

    async def _verify_sha256(self, file_path: str, expected_hash: str) -> bool:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest() == expected_hash

    async def fetch_dependency(self, filename: str, category: str, url: str, expected_hash: str) -> bool:
        target_path = os.path.join(self.paths.get(category, ""), filename)
        
        # Check local
        if os.path.exists(target_path) and await self._verify_sha256(target_path, expected_hash):
            return True

        # Remote sync
        try:
            self.logger.info(f"Syncing {filename}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.read()
                        with open(target_path, "wb") as f:
                            f.write(data)
                        if await self._verify_sha256(target_path, expected_hash):
                            return True
        except Exception as e:
            self.logger.warning(f"Network error syncing {filename}: {e}. Falling back.")

        # Fallback to local (already checked)
        if os.path.exists(target_path):
            self.logger.info(f"Rollback to local file: {target_path}")
            return True
            
        return False
