import importlib.util
import os
import logging
import sys
from typing import Any, Dict

class PluginLoader:
    """
    Dynamically loads external protocol adapters and flashing modules.
    """
    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = plugins_dir
        self.logger = logging.getLogger("PluginLoader")

    def load_plugin(self, plugin_name: str) -> Any:
        try:
            plugin_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            self.logger.info(f"Loaded plugin: {plugin_name}")
            return module
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            raise
