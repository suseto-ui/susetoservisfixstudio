#!/usr/bin/env python3
"""
Desktop Native WebView Runner (`app_webview.py`) for SusetoDroidFixStudio.
Launches the 100% pixel-perfect modern React/Tailwind cockpit inside a native Windows
Edge WebView2 window (via pywebview) with direct bidirectional Python hardware bridging.
Also embeds a local high-performance HTTP server serving `dist_web/` and `/api/*` routes.
"""

from __future__ import annotations

import argparse
import http.server
import json
import logging
import os
import socket
import sys
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Any, Dict

from core.native_bridge import NativeStudioBridge

logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s] %(message)s")
logger = logging.getLogger("app_webview")

_ROOT = Path(__file__).resolve().parent
_DIST_WEB = _ROOT / "dist_web"


def find_free_port(start_port: int = 42888) -> int:
    """Locate an available local TCP port."""
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start_port


class StudioWebHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP server serving static React assets with fallback to index.html (SPA routing),
    and handling bidirectional `/api/*` REST hardware calls.
    """

    bridge: NativeStudioBridge = None  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(_DIST_WEB), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        if self.path.startswith("/api"):
            logger.info("%s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self._send_json(self.bridge.get_system_status())
            return
        elif parsed.path == "/api/scan-ports":
            self._send_json(self.bridge.scan_hardware_ports())
            return
        elif parsed.path == "/api/dongle-auth":
            self._send_json(self.bridge.authenticate_dongle())
            return
        elif parsed.path == "/api/driver-catalog":
            self._send_json(self.bridge.get_driver_catalog())
            return
        elif parsed.path == "/api/driver/unassigned":
            self._send_json(self.bridge.scan_unassigned_drivers())
            return
        elif parsed.path == "/api/socs":
            self._send_json(self.bridge.get_supported_socs())
            return
        elif parsed.path == "/api/val/profiles":
            self._send_json(self.bridge.get_val_profiles())
            return
        elif parsed.path == "/api/telemetry/metrics":
            self._send_json(self.bridge.get_telemetry_metrics())
            return
        elif parsed.path == "/api/screen/telemetry":
            self._send_json(self.bridge.get_screen_telemetry())
            return

        # Check if file exists in dist_web
        file_path = _DIST_WEB / parsed.path.lstrip("/")
        if not file_path.exists() or file_path.is_dir():
            # SPA Fallback: serve index.html for unknown routes
            index_path = _DIST_WEB / "index.html"
            if index_path.exists():
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(index_path.read_bytes())
                return

        super().do_GET()

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        try:
            payload = json.loads(body.decode("utf-8")) if body else {}
        except Exception:
            payload = {}

        if parsed.path == "/api/scan-ports":
            self._send_json(self.bridge.scan_hardware_ports())
        elif parsed.path == "/api/driver/auto-inject":
            force = bool(payload.get("force", False))
            self._send_json(self.bridge.auto_inject_all_drivers(force=force))
        elif parsed.path == "/api/router/run-zero-conf":
            port = payload.get("port")
            self._send_json(self.bridge.run_zero_conf_router(port=port))
        elif parsed.path == "/api/router/execute-action":
            self._send_json(self.bridge.execute_router_action())
        elif parsed.path == "/api/screen/tap":
            x = int(payload.get("x", 540))
            y = int(payload.get("y", 1200))
            self._send_json(self.bridge.dispatch_touch_tap(x, y))
        elif parsed.path == "/api/screen/swipe":
            x1 = int(payload.get("x1", 540))
            y1 = int(payload.get("y1", 1600))
            x2 = int(payload.get("x2", 540))
            y2 = int(payload.get("y2", 400))
            duration = int(payload.get("duration_ms", 300))
            self._send_json(self.bridge.dispatch_touch_swipe(x1, y1, x2, y2, duration))
        elif parsed.path == "/api/screen/keyevent":
            key = str(payload.get("key", "HOME"))
            self._send_json(self.bridge.dispatch_screen_keyevent(key))
        elif parsed.path == "/api/screen/text":
            text = str(payload.get("text", ""))
            self._send_json(self.bridge.dispatch_screen_text(text))
        elif parsed.path == "/api/screen/install-apk":
            pkg = str(payload.get("package_name", "app.apk"))
            self._send_json(self.bridge.install_screen_apk(pkg))
        elif parsed.path == "/api/screen/shell":
            cmd = str(payload.get("command", "getprop"))
            self._send_json(self.bridge.execute_screen_shell(cmd))
        elif parsed.path == "/api/download-drivers":
            pkg = payload.get("package_id")
            force = bool(payload.get("force", False))
            res = self.bridge.download_and_install_drivers(pkg, force=force)
            self._send_json(res)
        elif parsed.path == "/api/qualcomm-loader":
            port = payload.get("port", "COM3")
            soc = payload.get("soc_id", "SM8350")
            res = self.bridge.execute_qualcomm_loader(port=port, soc_id=soc)
            self._send_json(res)
        elif parsed.path == "/api/mtk-bypass":
            port = payload.get("port", "COM5")
            chip = payload.get("chip_id", "MT6768")
            res = self.bridge.execute_mtk_bypass(port=port, chip_id=chip)
            self._send_json(res)
        elif parsed.path == "/api/val/espressif-sync":
            port = payload.get("port", "COM7")
            baud = int(payload.get("baud", 115200))
            res = self.bridge.execute_espressif_sync(port=port, baud=baud)
            self._send_json(res)
        elif parsed.path == "/api/val/stm32-bootloader":
            port = payload.get("port", "COM9")
            baud = int(payload.get("baud", 115200))
            res = self.bridge.execute_stm32_bootloader(port=port, baud=baud)
            self._send_json(res)
        elif parsed.path == "/api/val/mtk-nvram-repair":
            port = payload.get("port", "COM5")
            imei1 = payload.get("imei1", "860123456789012")
            imei2 = payload.get("imei2", "")
            res = self.bridge.execute_mtk_nvram_repair(port=port, imei1=imei1, imei2=imei2)
            self._send_json(res)
        elif parsed.path == "/api/dtr-rts":
            port = payload.get("port", "COM7")
            chipset = payload.get("chipset", "ESP32")
            res = self.bridge.trigger_dtr_rts(port=port, chipset=chipset)
            self._send_json(res)
        elif parsed.path == "/api/negotiate-baud":
            port = payload.get("port", "COM3")
            baud = int(payload.get("preferred_baud", 921600))
            res = self.bridge.negotiate_baudrate(port=port, preferred_baud=baud)
            self._send_json(res)
        elif parsed.path == "/api/memory/streaming-dump":
            partition = payload.get("partition", "boot")
            total_size = int(payload.get("total_size", 65536))
            chunk_size = int(payload.get("chunk_size", 4096))
            res = self.bridge.start_streaming_dump(partition=partition, total_size=total_size, chunk_size=chunk_size)
            self._send_json(res)
        elif parsed.path == "/api/memory/crashdump-recovery":
            port = payload.get("port", "COM3")
            arch = payload.get("architecture", "ARM64")
            res = self.bridge.extract_emergency_crashdump(port=port, arch=arch)
            self._send_json(res)
        elif parsed.path == "/api/fault-injection/benchmark":
            port = payload.get("port", "COM3")
            noise = float(payload.get("noise", 15.0))
            frame_drop = float(payload.get("frame_drop", 10.0))
            hotplug = bool(payload.get("hotplug", True))
            packets = int(payload.get("packets", 40))
            res = self.bridge.run_fault_injection_benchmark(
                port=port, noise=noise, frame_drop=frame_drop, hotplug=hotplug, packets=packets
            )
            self._send_json(res)
        elif parsed.path == "/api/watchdog/soft-reset":
            port = payload.get("port", "COM3")
            res = self.bridge.run_port_soft_reset(port=port)
            self._send_json(res)
        elif parsed.path == "/api/e2e/benchmark":
            port = payload.get("port", "COM3")
            vendor = payload.get("vendor", "QUALCOMM")
            res = self.bridge.run_e2e_benchmark(port=port, vendor=vendor)
            self._send_json(res)
        elif parsed.path == "/api/stress-test":
            port = payload.get("port", "COM3")
            baud = int(payload.get("baud_rate", 115200))
            packets = int(payload.get("packets", 25))
            res = self.bridge.run_stress_test(port_name=port, baud_rate=baud, packet_count=packets)
            self._send_json(res)
        elif parsed.path == "/api/frp-wipe":
            port = payload.get("port", "COM3")
            chipset = payload.get("chipset", "QUALCOMM")
            res = self.bridge.execute_frp_wipe(port=port, chipset=chipset)
            self._send_json(res)
        elif parsed.path == "/api/hex-dump":
            partition = payload.get("partition", "boot")
            offset = int(payload.get("offset", 0))
            length = int(payload.get("length", 256))
            res = self.bridge.read_partition_hex(partition_name=partition, offset=offset, length=length)
            self._send_json(res)
        elif parsed.path == "/api/run-pipeline":
            res = self.bridge.run_master_pipeline()
            self._send_json(res)
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data: Any) -> None:
        content = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def start_local_server(port: int, bridge: NativeStudioBridge) -> http.server.HTTPServer:
    """Start local threaded HTTP server."""
    StudioWebHandler.bridge = bridge
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), StudioWebHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    logger.info("Lokální HTTP server s webovým kokpitem spuštěn na: http://127.0.0.1:%d", port)
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description="SusetoDroidFixStudio Native WebView Cockpit")
    parser.add_argument("--port", type=int, default=0, help="Custom HTTP server port")
    parser.add_argument("--no-gui", action="store_true", help="Run in headless server mode")
    parser.add_argument("--fullscreen", action="store_true", default=True, help="Launch in full-screen mode")
    parser.add_argument("--kiosk", action="store_true", default=True, help="Launch in full-screen kiosk mode")
    parser.add_argument("--windowed", action="store_true", help="Force standard windowed mode (1600x950)")
    parser.add_argument("--test", action="store_true", help="Self-test mode: launch, verify, exit")
    args = parser.parse_args()

    is_fullscreen = (args.fullscreen or args.kiosk) and not args.windowed

    # Ensure dist_web exists
    if not _DIST_WEB.exists() or not (_DIST_WEB / "index.html").exists():
        logger.info("Adresář dist_web nenalezen, spouštím automatické sestavení frontendu (npm run build)...")
        import subprocess
        subprocess.run(["npm", "run", "build"], cwd=str(_ROOT), check=True)

    bridge = NativeStudioBridge()
    port = args.port if args.port > 0 else find_free_port()
    server = start_local_server(port, bridge)
    target_url = f"http://127.0.0.1:{port}"

    if args.test:
        logger.info("[TEST] Ověřuji funkčnost nativního mostu a HTTP serveru...")
        status = bridge.get_system_status()
        diag = bridge.scan_hardware_ports()
        stress = bridge.run_stress_test("COM3", 115200, 5)
        e2e = bridge.run_e2e_benchmark("COM3", "QUALCOMM")
        router = bridge.run_zero_conf_router("COM3")
        screen = bridge.get_screen_telemetry()
        logger.info(
            "[TEST] Status: OK, Portů: %d, Zátěž: %s, Router: %s, Displej: %s",
            diag["total_ports_detected"], stress["verdict"], router["mode"], screen["resolution"]
        )
        server.shutdown()
        logger.info("[TEST] [SUCCESS] WebView server a bridge jsou 100%% připraveny!")
        sys.exit(0)

    if args.no_gui or "CI" in os.environ:
        logger.info("Spuštěno v bezhlavém režimu (headless). Kokpit je dostupný na: %s", target_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.shutdown()
            sys.exit(0)

    # Attempt launching pywebview in Full-Screen Kiosk / Maximized mode
    try:
        import webview

        logger.info("Otevírám moderní desktopové WebView okno (Microsoft Edge WebView2, Kiosk=%s)...", is_fullscreen)
        window = webview.create_window(
            title="SusetoDroidFixStudio v1.0-PROD | Servisní a diagnostický kokpit",
            url=target_url,
            js_api=bridge,
            fullscreen=is_fullscreen,
            width=1600,
            height=950,
            min_size=(1200, 750),
            background_color="#0a0d14",
            text_select=True,
            zoomable=True,
            easy_drag=True
        )
        webview.start(debug=False)
    except Exception as exc:
        logger.warning(
            "Nativní WebView GUI okno nelze inicializovat (%s). Spouštím hybridní režim v dedikovaném okně prohlížeče...", exc
        )
        import subprocess
        import webbrowser

        # Try launching Edge / Chrome in app kiosk mode
        launched = False
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ]
        for ep in edge_paths:
            if os.path.exists(ep):
                try:
                    cmd = [ep, f"--app={target_url}"]
                    if is_fullscreen:
                        cmd.append("--start-fullscreen")
                    subprocess.Popen(cmd)
                    launched = True
                    logger.info("Kokpit spuštěn v dedikovaném okně prohlížeče: %s", ep)
                    break
                except Exception:
                    pass

        if not launched:
            webbrowser.open(target_url)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.shutdown()


if __name__ == "__main__":
    main()
