import pytest
import os
import hashlib
from core.repo_sync_manager import RepoSyncManager

@pytest.mark.asyncio
async def test_repo_sync_integrity(tmp_path):
    cache_dir = tmp_path / "cache"
    manager = RepoSyncManager(repo_slug="test/repo", cache_dir=str(cache_dir))
    
    asset_name = "test.bin"
    file_path = cache_dir / asset_name
    content = b"hello world"
    expected_hash = hashlib.sha256(content).hexdigest()
    
    # Create valid file
    with open(file_path, "wb") as f:
        f.write(content)
        
    assert await manager._verify_file(str(file_path), expected_hash) is True

@pytest.mark.asyncio
async def test_repo_sync_fail_and_delete(tmp_path):
    cache_dir = tmp_path / "cache"
    manager = RepoSyncManager(repo_slug="test/repo", cache_dir=str(cache_dir))
    
    asset_name = "bad.bin"
    file_path = cache_dir / asset_name
    with open(file_path, "wb") as f:
        f.write(b"bad content")
        
    assert await manager._verify_file(str(file_path), "wrong_hash") is False
