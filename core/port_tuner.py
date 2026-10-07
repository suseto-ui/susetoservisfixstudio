"""
Dynamic Port Tuner & Auto-Negotiation Engine.
Measures RTT latency and automatically finds optimal baud rate (9600 to 921600 bps).
"""

from __future__ import annotations

import asyncio
import time
import logging
from typing import List, Optional

logger = logging.getLogger("diagnostic_engine.tuner")

STANDARD_BAUDRATES = [9600, 57600, 115200, 460800, 921600]


class DynamicPortTuner:
    """
    Auto-negotiation engine for serial communication lines.
    """

    def __init__(self, probe_payload: bytes = b"\r\nAT\r\n", timeout: float = 0.1):
        self.probe_payload = probe_payload
        self.timeout = timeout

    async def auto_tune_baud(self, port: str) -> int:
        """
        Scan baud rates from 9600 to 921600 bps and return the highest reliable rate.
        """
        best_rate = 9600
        for rate in STANDARD_BAUDRATES:
            rtt = await self.measure_rtt(port, baudrate=rate)
            if rtt >= 0:
                best_rate = rate
                logger.info("Port %s negotiated stable baudrate at %d bps (RTT: %.2f ms)", port, rate, rtt)
            else:
                logger.debug("Port %s failed probe at %d bps", port, rate)
        return best_rate

    async def measure_rtt(self, port: str, baudrate: int = 115200) -> float:
        """
        Measure round-trip time (RTT) in milliseconds for the specified port and baudrate.
        Returns negative float if probe fails or times out.
        """
        loop = asyncio.get_running_loop()
        
        def _sync_probe() -> float:
            import serial
            try:
                ser = serial.Serial(port=port, baudrate=baudrate, timeout=self.timeout)
                t0 = time.perf_counter()
                ser.write(self.probe_payload)
                ser.flush()
                resp = ser.read(len(self.probe_payload))
                elapsed = (time.perf_counter() - t0) * 1000.0
                ser.close()
                if resp:
                    return elapsed
                return -1.0
            except Exception:
                return -1.0

        return await loop.run_in_executor(None, _sync_probe)
