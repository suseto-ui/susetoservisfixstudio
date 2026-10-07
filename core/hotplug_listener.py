import asyncio
import ctypes
import ctypes.wintypes as wintypes
from typing import Callable, Optional, Dict, Any
import logging
import threading

# Windows Constants
WM_DEVICECHANGE = 0x0219
DBT_DEVICEARRIVAL = 0x8000
DBT_DEVICEREMOVECOMPLETE = 0x8004
DBT_DEVTYP_DEVICEINTERFACE = 0x00000005

class DEV_BROADCAST_HDR(ctypes.Structure):
    _fields_ = [
        ("dbch_size", wintypes.DWORD),
        ("dbch_devicetype", wintypes.DWORD),
        ("dbch_reserved", wintypes.DWORD),
    ]

class DEV_BROADCAST_DEVICEINTERFACE(ctypes.Structure):
    _fields_ = [
        ("dbcc_size", wintypes.DWORD),
        ("dbcc_devicetype", wintypes.DWORD),
        ("dbcc_reserved", wintypes.DWORD),
        ("dbcc_classguid", ctypes.c_byte * 16),
        ("dbcc_name", wintypes.WCHAR * 256),
    ]

class HotplugListener:
    """
    Asynchronous USB Hotplug Listener for Windows.
    Uses a hidden window to capture WM_DEVICECHANGE events.
    """
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        self.logger = logging.getLogger("HotplugListener")
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._stop_event = threading.Event()
        self._hwnd: Optional[int] = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        threading.Thread(target=self._run_listener, daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._hwnd:
            ctypes.windll.user32.PostMessageW(self._hwnd, 0x0012, 0, 0)  # WM_QUIT

    def _run_listener(self) -> None:
        wc = ctypes.wintypes.WNDCLASSW()
        wc.lpfnWndProc = ctypes.WINFUNCTYPE(ctypes.c_longlong, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)(self._wnd_proc)
        wc.lpszClassName = "HotplugListenerWindow"
        wc.hInstance = ctypes.windll.kernel32.GetModuleHandleW(None)

        class_atom = ctypes.windll.user32.RegisterClassW(ctypes.byref(wc))
        if not class_atom:
            self.logger.error("Failed to register window class")
            return

        self._hwnd = ctypes.windll.user32.CreateWindowExW(
            0, wc.lpszClassName, "USB Listener", 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None
        )

        if not self._hwnd:
            self.logger.error("Failed to create hidden window")
            return

        # Register for device notifications (USB Guid)
        # GUID_DEVINTERFACE_USB_DEVICE: {A5DCBF10-6530-11D2-901F-00C04FB17C9E}
        GUID_USB = (ctypes.c_ubyte * 16)(
            0x10, 0xBF, 0xDC, 0xA5, 0x30, 0x65, 0xD2, 0x11, 0x90, 0x1F, 0x00, 0xC0, 0x4F, 0xB1, 0x7C, 0x9E
        )
        
        notification_filter = DEV_BROADCAST_DEVICEINTERFACE()
        notification_filter.dbcc_size = ctypes.sizeof(DEV_BROADCAST_DEVICEINTERFACE)
        notification_filter.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE
        ctypes.memmove(notification_filter.dbcc_classguid, GUID_USB, 16)

        h_dev_notify = ctypes.windll.user32.RegisterDeviceNotificationW(
            self._hwnd, ctypes.byref(notification_filter), 0
        )

        if not h_dev_notify:
            self.logger.error("Failed to register device notification")
            return

        msg = wintypes.MSG()
        while ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

    def _wnd_proc(self, hwnd: int, msg: int, wparam: int, lparam: int) -> int:
        if msg == WM_DEVICECHANGE:
            if wparam == DBT_DEVICEARRIVAL:
                self._handle_event("attach", lparam)
            elif wparam == DBT_DEVICEREMOVECOMPLETE:
                self._handle_event("detach", lparam)
        return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _handle_event(self, action: str, lparam: int) -> None:
        try:
            header = DEV_BROADCAST_HDR.from_address(lparam)
            if header.dbch_devicetype == DBT_DEVTYP_DEVICEINTERFACE:
                dev_interface = DEV_BROADCAST_DEVICEINTERFACE.from_address(lparam)
                device_path = dev_interface.dbcc_name
                if self._loop:
                    self._loop.call_soon_threadsafe(self.callback, action, device_path)
        except Exception as e:
            self.logger.error(f"Error handling hotplug event: {e}")
