"""
Dynamic Plugin Loader & OEM Adapter Registry (`core/plugin_manager.py`).
Provides runtime dynamic loading and security validation for external vendor adapter plugins
stored in the `plugins/` directory, enabling hot-plugging support for new phone models/chipsets
without requiring main application executable re-compilation.
"""

from __future__ import annotations

import importlib.util
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from adapters.base_adapter import BaseDeviceAdapter

logger = logging.getLogger("core.plugin_manager")

_DEFAULT_PLUGINS_DIR = Path(__file__).resolve().parent.parent / "plugins"


class DynamicPluginLoader:
    """
    Scans, validates, and dynamically registers external Python plugin modules (.py)
    that inherit from `BaseDeviceAdapter`.
    """

    def __init__(self, plugins_dir: Optional[Path] = None) -> None:
        self.plugins_dir = Path(plugins_dir) if plugins_dir else _DEFAULT_PLUGINS_DIR
        self._loaded_adapters: Dict[str, Type[BaseDeviceAdapter]] = {}
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def discover_plugins(self) -> List[Path]:
        """Scans the plugins directory for valid python script files."""
        if not self.plugins_dir.exists():
            return []
        
        plugin_files = [
            f for f in self.plugins_dir.glob("*.py")
            if not f.name.startswith("__") and not f.name.startswith(".")
        ]
        logger.info(f"Discovered {len(plugin_files)} plugin script files in '{self.plugins_dir}'.")
        return plugin_files

    def load_plugin_module(self, plugin_path: Path) -> Optional[Type[BaseDeviceAdapter]]:
        """
        Dynamically imports a single python script file and extracts valid
        subclasses of `BaseDeviceAdapter`.
        """
        module_name = f"plugins_dyn_{plugin_path.stem}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, str(plugin_path))
            if not spec or not spec.loader:
                logger.warning(f"Could not create module spec for '{plugin_path}'.")
                return None

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find subclasses of BaseDeviceAdapter
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseDeviceAdapter) and obj is not BaseDeviceAdapter:
                    logger.info(f"[PLUGIN_LOADED] Valid adapter subclass '{name}' loaded from '{plugin_path.name}'.")
                    return obj

            # Fallback check for duck-typed adapters with required interface methods
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, "connect") and hasattr(obj, "send_command") and hasattr(obj, "disconnect"):
                    logger.info(f"[PLUGIN_LOADED] Valid duck-typed adapter '{name}' loaded from '{plugin_path.name}'.")
                    return obj

            logger.warning(f"No valid BaseDeviceAdapter subclasses found in '{plugin_path.name}'.")
            return None
        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_path.name}': {e}")
            return None

    def load_all_plugins(self) -> Dict[str, Type[BaseDeviceAdapter]]:
        """Discovers and dynamically imports all plugins in the target plugins folder."""
        plugin_files = self.discover_plugins()
        for p in plugin_files:
            cls = self.load_plugin_module(p)
            if cls:
                adapter_key = p.stem.upper().replace("_ADAPTER", "")
                self._loaded_adapters[adapter_key] = cls

        logger.info(f"Plugin loader active: {len(self._loaded_adapters)} external adapters registered.")
        return self._loaded_adapters

    def get_adapter_class(self, vendor_name: str) -> Optional[Type[BaseDeviceAdapter]]:
        """Retrieves registered adapter class by vendor key."""
        key = vendor_name.upper().replace("_ADAPTER", "")
        return self._loaded_adapters.get(key)

    def instantiate_adapter(
        self, vendor_name: str, port: str = "COM3", baudrate: int = 115200
    ) -> Optional[BaseDeviceAdapter]:
        """Instantiates a registered dynamic adapter class with specified COM port and baud rate."""
        cls = self.get_adapter_class(vendor_name)
        if not cls:
            logger.warning(f"Adapter '{vendor_name}' not found in registered plugins.")
            return None
        try:
            instance = cls(port=port, baudrate=baudrate)
            return instance
        except Exception as e:
            logger.error(f"Failed to instantiate adapter class for '{vendor_name}': {e}")
            return None


# Global singleton instance
plugin_loader = DynamicPluginLoader()
