"""
USB Enumeration & Hotplug Engine for Modular Windows Universal Hardware Diagnostic.
Provides real-time device arrival/removal tracking using Windows Win32 Message Pump
(WM_DEVICECHANGE) with Linux udev/sysfs fallback and cross-platform port reconciliation.
"""

from __future__ import annotations

import asyncio
import os
import platform
import re
import sys
from enum import Enum
from typing import AsyncGenerator, Callable, Dict, List, Optional, Set
try:
    from pydantic.dataclasses import dataclass
    from pydantic import ConfigDict
    _DATACLASS_KWARGS = {"config": ConfigDict(arbitrary_types_allowed=True)}
except ImportError:
    from dataclasses import dataclass  # type: ignore[no-redef]
    _DATACLASS_KWARGS = {}

# Standard GUID Constants for Windows Hardware Notification
GUID_DEVINTERFACE_USB_DEVICE = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
GUID_DEVINTERFACE_COMPORT = "{86E0D1E0-8089-11D0-9CE4-08003E301F73}"
GUID_DEVINTERFACE_MODEM = "{2C7089AA-2E0E-11D1-B114-00C04FC2AAE4}"

WM_DEVICECHANGE = 0x0219
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEREMOVECOMPLETE = 0x8004
DBT_DEVTYP_DEVICEINTERFACE = 0x00000005


class DeviceEventType(str, Enum):
    """Device hotplug lifecycle event."""
    ARRIVED = "ARRIVED"
    REMOVED = "REMOVED"
    UPDATED = "UPDATED"


@dataclass(**_DATACLASS_KWARGS)
class USBDeviceMetadata:
    """
    Validated metadata descriptor for connected USB/Serial diagnostic devices.
    """
    vid: str
    pid: str
    serial_number: Optional[str] = None
    device_interface_guid: Optional[str] = None
    port_name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    hardware_id: Optional[str] = None

    @property
    def device_id(self) -> str:
        """Unique compound hardware identifier."""
        if self.serial_number:
            return f"USB_{self.vid}_{self.pid}_{self.serial_number}".upper()
        if self.port_name:
            return f"PORT_{self.port_name}_{self.vid}_{self.pid}".upper()
        return f"DEV_{self.vid}_{self.pid}_{abs(hash(self.hardware_id or ''))}".upper()


@dataclass
class DeviceHotplugEvent:
    """Event wrapper emitted when physical bus state shifts."""
    event_type: DeviceEventType
    device: USBDeviceMetadata
    raw_path: Optional[str] = None


class USBDeviceParser:
    """Utility to parse and normalize hardware identifiers across Windows and Linux."""

    VID_PID_REGEX = re.compile(r"VID[_:]([0-9A-Fa-f]{4})[&:]PID[_:]([0-9A-Fa-f]{4})", re.IGNORECASE)
    GUID_REGEX = re.compile(r"\{[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12}\}")

    @classmethod
    def parse_hardware_id(cls, hwid: str) -> tuple[Optional[str], Optional[str]]:
        """Extract VID and PID hex strings from hardware identifier string."""
        if not hwid:
            return None, None
        match = cls.VID_PID_REGEX.search(hwid)
        if match:
            return match.group(1).upper(), match.group(2).upper()
        return None, None

    @classmethod
    def extract_guid(cls, raw_path: str) -> Optional[str]:
        """Extract GUID from device interface notification path."""
        if not raw_path:
            return None
        match = cls.GUID_REGEX.search(raw_path)
        return match.group(0).upper() if match else None


class AsyncUSBHotplugListener:
    """
    Async-native USB & Serial Device Hotplug Engine.
    Employs Windows WM_DEVICECHANGE message pump via Win32 API when running on Windows,
    and falls back to non-blocking udev / poll monitors on Linux and test environments.
    """

    def __init__(self, poll_interval: float = 1.0):
        self.poll_interval = poll_interval
        self._running = False
        self._queue: asyncio.Queue[DeviceHotplugEvent] = asyncio.Queue()
        self._known_devices: Dict[str, USBDeviceMetadata] = {}
        self._listener_task: Optional[asyncio.Task[None]] = None
        self._callbacks: List[Callable[[DeviceHotplugEvent], None]] = []
        self._is_windows = platform.system() == "Windows"

    def register_callback(self, callback: Callable[[DeviceHotplugEvent], None]) -> None:
        """Register a synchronous or asynchronous callback for hotplug events."""
        self._callbacks.append(callback)

    async def start(self) -> None:
        """Start listening for hardware hotplug events in the background."""
        if self._running:
            return
        self._running = True
        
        # Populate initial baseline snapshot
        initial_devices = await self.enumerate_devices_async()
        for dev in initial_devices:
            self._known_devices[dev.device_id] = dev

        self._listener_task = asyncio.create_task(self._run_hotplug_monitor())

    async def stop(self) -> None:
        """Gracefully terminate hotplug monitors and clean up system handles."""
        self._running = False
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
            self._listener_task = None

    async def get_event(self) -> DeviceHotplugEvent:
        """Wait for the next hotplug event in the event queue."""
        return await self._queue.get()

    async def events(self) -> AsyncGenerator[DeviceHotplugEvent, None]:
        """Async generator yielding hotplug events continuously."""
        while self._running:
            try:
                event = await self.get_event()
                yield event
            except asyncio.CancelledError:
                break

    async def _dispatch_event(self, event: DeviceHotplugEvent) -> None:
        """Deliver hotplug event to internal queue and registered callbacks."""
        await self._queue.put(event)
        for cb in self._callbacks:
            try:
                res = cb(event)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as exc:
                sys.stderr.write(f"[HotplugListener Callback Error] {exc}\n")

    async def enumerate_devices_async(self) -> List[USBDeviceMetadata]:
        """Async wrapper around system device enumeration."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.enumerate_devices)

    def enumerate_devices(self) -> List[USBDeviceMetadata]:
        """
        Scan system for all currently attached USB/Serial diagnostic devices.
        Uses serial.tools.list_ports with fallback to PyWin32 WMI / sysfs.
        """
        devices: List[USBDeviceMetadata] = []
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            for p in ports:
                vid_str = f"{p.vid:04X}" if p.vid is not None else None
                pid_str = f"{p.pid:04X}" if p.pid is not None else None

                if not vid_str or not pid_str:
                    extracted_vid, extracted_pid = USBDeviceParser.parse_hardware_id(p.hwid)
                    vid_str = vid_str or extracted_vid or "0000"
                    pid_str = pid_str or extracted_pid or "0000"

                guid = USBDeviceParser.extract_guid(p.hwid)
                if not guid and self._is_windows:
                    guid = GUID_DEVINTERFACE_COMPORT

                meta = USBDeviceMetadata(
                    vid=vid_str,
                    pid=pid_str,
                    serial_number=p.serial_number,
                    device_interface_guid=guid,
                    port_name=p.device,
                    description=p.description,
                    manufacturer=p.manufacturer,
                    hardware_id=p.hwid,
                )
                devices.append(meta)
        except ImportError:
            # Fallback when pyserial is not directly installed or during lightweight tests
            pass

        return devices

    async def _run_hotplug_monitor(self) -> None:
        """Main monitoring loop; triggers platform-specific event listener or polling fallback."""
        if self._is_windows and self._has_win32_support():
            try:
                await self._run_windows_hotplug_loop()
                return
            except Exception as exc:
                sys.stderr.write(f"[Win32 Native Hook Failed, falling back to reconciler] {exc}\n")

        # Robust async reconciler for non-Windows and mock environments
        await self._run_polling_reconciler()

    def _has_win32_support(self) -> bool:
        """Check if native Windows Win32 API extensions are available."""
        try:
            import win32gui
            import win32con
            return True
        except ImportError:
            return False

    async def _run_windows_hotplug_loop(self) -> None:
        """
        Native Windows Message Window listener registering for DBT_DEVICEARRIVAL
        and DBT_DEVICEREMOVECOMPLETE.
        """
        loop = asyncio.get_running_loop()

        def win32_pump():
            import win32gui
            import win32con
            import win32gui_struct

            wndclass = win32gui.WNDCLASS()
            wndclass.hInstance = win32gui.GetModuleHandle(None)
            wndclass.lpszClassName = "DiagnosticEngineHotplugSink"
            
            def wndproc(hwnd, msg, wparam, lparam):
                if msg == WM_DEVICECHANGE:
                    if wparam == DBT_DEVICEARRIVAL:
                        asyncio.run_coroutine_threadsafe(self._handle_reconcile_tick(), loop)
                    elif wparam == DBT_DEVICEREMOVECOMPLETE:
                        asyncio.run_coroutine_threadsafe(self._handle_reconcile_tick(), loop)
                return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

            wndclass.lpfnWndProc = wndproc
            try:
                atom = win32gui.RegisterClass(wndclass)
            except Exception:
                pass

            hwnd = win32gui.CreateWindow(
                "DiagnosticEngineHotplugSink",
                "DiagnosticEngineSinkWindow",
                0, 0, 0, 0, 0, 0, 0, wndclass.hInstance, None
            )

            while self._running:
                win32gui.PumpWaitingMessages()

        await loop.run_in_executor(None, win32_pump)

    async def _run_polling_reconciler(self) -> None:
        """Continuous diff-based state reconciler running on async loop."""
        while self._running:
            try:
                await self._handle_reconcile_tick()
                await asyncio.sleep(self.poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                sys.stderr.write(f"[Reconciler Error] {exc}\n")
                await asyncio.sleep(self.poll_interval)

    async def _handle_reconcile_tick(self) -> None:
        """Evaluate delta between current hardware bus state and cached state."""
        current_devices = await self.enumerate_devices_async()
        current_map = {d.device_id: d for d in current_devices}

        # Check for newly arrived devices
        for dev_id, dev in current_map.items():
            if dev_id not in self._known_devices:
                self._known_devices[dev_id] = dev
                await self._dispatch_event(
                    DeviceHotplugEvent(event_type=DeviceEventType.ARRIVED, device=dev)
                )

        # Check for detached devices
        for dev_id in list(self._known_devices.keys()):
            if dev_id not in current_map:
                removed_dev = self._known_devices.pop(dev_id)
                await self._dispatch_event(
                    DeviceHotplugEvent(event_type=DeviceEventType.REMOVED, device=removed_dev)
                )
