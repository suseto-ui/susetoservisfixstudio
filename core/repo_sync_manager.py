import asyncio
import aiohttp
import hashlib
import logging
import os
from typing import Optional

class RepoSyncManager:
    """
    Manages asynchronous repository synchronization with checksum validation.
    """
    def __init__(self, repo_slug: str, cache_dir: str = "cache/loaders"):
        self.repo_slug = repo_slug
        self.cache_dir = cache_dir
        self.logger = logging.getLogger("RepoSyncManager")
        os.makedirs(self.cache_dir, exist_ok=True)

    async def _verify_file(self, file_path: str, expected_hash: str) -> bool:
        if not os.path.exists(file_path):
            return False
        
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        
        return sha256.hexdigest() == expected_hash

    async def sync_asset(self, asset_name: str, download_url: str, expected_hash: str) -> bool:
        file_path = os.path.join(self.cache_dir, asset_name)
        
        # Check if already synced and valid
        if await self._verify_file(file_path, expected_hash):
            self.logger.info(f"Asset {asset_name} is already valid.")
            return True
            
        # If exists but invalid, delete
        if os.path.exists(file_path):
            self.logger.warning(f"Invalid hash for {asset_name}, deleting.")
            os.remove(file_path)
            
        # Download
        self.logger.info(f"Downloading {asset_name} from {download_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                if response.status != 200:
                    return False
                data = await response.read()
                
        with open(file_path, "wb") as f:
            f.write(data)
            
        # Final verify
        if await self._verify_file(file_path, expected_hash):
            return True
            
        self.logger.error(f"Download failed integrity check for {asset_name}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return False
