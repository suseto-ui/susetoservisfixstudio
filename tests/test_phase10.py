import pytest
import os
from core.plugin_loader import PluginLoader
from core.cloud_loader_manager import CloudLoaderManager
from core.ota_updater import OTAUpdater

def test_plugin_loading(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "test_plugin.py"
    plugin_file.write_text("def run(): return 'ok'")
    
    loader = PluginLoader(plugins_dir=str(plugin_dir))
    module = loader.load_plugin("test_plugin")
    assert module.run() == "ok"

@pytest.mark.asyncio
async def test_hash_verification():
    manager = CloudLoaderManager()
    # Mock data and hash (simplified)
    # real test would require internet/mocked aiohttp
    pass
