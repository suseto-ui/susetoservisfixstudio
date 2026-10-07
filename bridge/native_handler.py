import asyncio
import json
import logging
from typing import Dict, Any

from core.hotplug_listener import HotplugListener, DeviceEvent
from core.state_detector import StateDetector, DetectionResult

class NativeHandler:
    """
    Entry point for C++ / Native Bridge integration.
    Provides JSON-serialized data for the frontend/host application.
    """
    def __init__(self):
        self.detector = StateDetector()
        self.listener = HotplugListener(self._handle_event)
        self.logger = logging.getLogger("NativeHandler")
        self._on_event_callback = None # Set by C++ side or pybind11

    def set_callback(self, callback):
        """Sets the function to be called when a device event occurs."""
        self._on_event_callback = callback

    def start(self):
        """Initializes the backend components."""
        self.listener.start()
        self.logger.info("Native Handler initialized.")

    def _handle_event(self, event: DeviceEvent):
        """Processes internal events and serializes them for the bridge."""
        if event.action == 'attach':
            detection = self.detector.classify(event)
            payload = {
                "event": "device_attached",
                "vid": event.vid,
                "pid": event.pid,
                "boot_state": detection.state.value,
                "vendor": detection.vendor,
                "product": detection.product_name,
                "hardware_id": event.hardware_id
            }
        else:
            payload = {
                "event": "device_detached",
                "path": event.path
            }

        # Send to host bridge
        if self._on_event_callback:
            self._on_event_callback(json.dumps(payload))
        else:
            # Fallback for debugging if no bridge is attached
            print(f"DEBUG_BRIDGE_EVENT: {json.dumps(payload)}")

# Bridge Interface for pybind11 or direct C API
def get_handler_instance():
    return NativeHandler()
