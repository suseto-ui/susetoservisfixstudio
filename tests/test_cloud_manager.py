import pytest
import os
import hashlib
from unittest.mock import AsyncMock
from core.cloud_loader_manager import CloudLoaderManager

@pytest.mark.asyncio
async def test_cloud_manager_fetch(tmp_path):
    # Setup
    ledger = AsyncMock()
    manager = CloudLoaderManager(ledger=ledger)
    manager.paths["loaders"] = str(tmp_path) # Override for test
    
    filename = "test.bin"
    content = b"data"
    expected_hash = hashlib.sha256(content).hexdigest()
    
    # 1. Success case: already exists
    file_path = tmp_path / filename
    with open(file_path, "wb") as f:
        f.write(content)
        
    assert await manager.fetch_dependency(filename, "loaders", "url", expected_hash) is True
    
    # 2. Integrity failure (invalid hash)
    os.remove(file_path)
    with open(file_path, "wb") as f:
        f.write(b"wrong")
        
    # Will try remote, fail, and fallback to local file if it exists,
    # but here hash is wrong, so it should fail
    # (assuming no network mock)
    assert await manager.fetch_dependency(filename, "loaders", "url", expected_hash) is False
