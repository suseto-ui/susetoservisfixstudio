"""
Core Async Bus Manager & Dynamic Port Tuner for Hardware Diagnostic Engine.
Provides thread-safe event pub-sub via asyncio.Queue and high-speed auto-baudrate
tuning across standard diagnostic speeds: [115200, 921600, 460800, 57600, 9600, 3000000].
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    AsyncGenerator,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
)

logger = logging.getLogger("diagnostic_engine.bus")

T = TypeVar("T")

# Supported Diagnostic Baudrates in specified scanning precedence order
SUPPORTED_BAUDRATES: List[int] = [115200, 921600, 460800, 57600, 9600, 3000000]


class BusEventCategory(str, Enum):
    """Categorization of bus-level events."""
    HARDWARE = "HARDWARE"
    COMMUNICATION = "COMMUNICATION"
    DIAGNOSTIC = "DIAGNOSTIC"
    ERROR = "ERROR"


@dataclass
class BusEvent:
    """Base event contract for all hardware diagnostic bus operations."""
    category: BusEventCategory
    timestamp: float = field(default_factory=time.time)
    source: str = "BUS_CORE"
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceAttachedBusEvent(BusEvent):
    """Fired when a new physical hardware port/device is ready."""
    def __init__(self, port: str, vid: str, pid: str, metadata: Optional[Dict[str, Any]] = None):
        super().__init__(
            category=BusEventCategory.HARDWARE,
            source="BUS_ENUMERATOR",
            payload={"port": port, "vid": vid, "pid": pid, "metadata": metadata or {}},
        )


@dataclass
class DeviceDetachedBusEvent(BusEvent):
    """Fired when an existing hardware port/device is disconnected."""
    def __init__(self, port: str, device_id: str):
        super().__init__(
            category=BusEventCategory.HARDWARE,
            source="BUS_ENUMERATOR",
            payload={"port": port, "device_id": device_id},
        )


@dataclass
class PortTunedBusEvent(BusEvent):
    """Fired when baudrate tuning completes successfully."""
    def __init__(self, port: str, negotiated_baudrate: int, latency_ms: float):
        super().__init__(
            category=BusEventCategory.DIAGNOSTIC,
            source="DYNAMIC_PORT_TUNER",
            payload={"port": port, "baudrate": negotiated_baudrate, "latency_ms": latency_ms},
        )


@dataclass
class BusDataReceivedEvent(BusEvent):
    """Fired when raw bytes are received from the physical hardware bus."""
    def __init__(self, port: str, data: bytes):
        super().__init__(
            category=BusEventCategory.COMMUNICATION,
            source="BUS_TRANSPORT",
            payload={"port": port, "data_hex": data.hex(), "length": len(data)},
        )


@dataclass
class BusErrorEvent(BusEvent):
    """Fired when bus transmission, handshake, or hardware fault occurs."""
    def __init__(self, port: Optional[str], error_code: str, message: str):
        super().__init__(
            category=BusEventCategory.ERROR,
            source="BUS_CONTROLLER",
            payload={"port": port, "error_code": error_code, "message": message},
        )


@dataclass
class TuningResult:
    """Outcome of dynamic baudrate detection routine."""
    success: bool
    port: str
    detected_baudrate: Optional[int] = None
    latency_ms: float = 0.0
    attempts: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None


class DynamicPortTuner:
    """
    Dynamic auto-baudrate scanner for UART/USB serial communication.
    Systematically probes target hardware with standard synchronization bursts
    across [115200, 921600, 460800, 57600, 9600, 3000000].
    """

    def __init__(
        self,
        probe_payload: bytes = b"\r\nAT\r\n",
        read_timeout: float = 0.15,
        supported_rates: Optional[List[int]] = None,
    ):
        self.probe_payload = probe_payload
        self.read_timeout = read_timeout
        self.supported_rates = supported_rates or SUPPORTED_BAUDRATES

    async def scan_port(
        self,
        port_name: str,
        custom_probe: Optional[bytes] = None,
        expected_response: Optional[bytes] = None,
    ) -> TuningResult:
        """
        Scan a serial port through available baud rates and return first verified rate.

        Args:
            port_name: System port path (e.g. 'COM3' or '/dev/ttyUSB0')
            custom_probe: Optional probe bytes (default: b'\\r\\nAT\\r\\n')
            expected_response: Optional expected substring in response.
        """
        payload = custom_probe or self.probe_payload
        attempts: List[Dict[str, Any]] = []

        loop = asyncio.get_running_loop()

        for rate in self.supported_rates:
            t_start = time.perf_counter()
            success, raw_resp, err = await loop.run_in_executor(
                None, self._probe_baudrate_sync, port_name, rate, payload, expected_response
            )
            elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            attempts.append({
                "baudrate": rate,
                "success": success,
                "elapsed_ms": round(elapsed_ms, 2),
                "response_hex": raw_resp.hex() if raw_resp else None,
                "error": err,
            })

            if success:
                logger.info(
                    "DynamicPortTuner: Port %s locked at %d bps (RTT: %.2f ms)",
                    port_name,
                    rate,
                    elapsed_ms,
                )
                return TuningResult(
                    success=True,
                    port=port_name,
                    detected_baudrate=rate,
                    latency_ms=elapsed_ms,
                    attempts=attempts,
                )

        return TuningResult(
            success=False,
            port=port_name,
            detected_baudrate=None,
            latency_ms=0.0,
            attempts=attempts,
            error_message=f"Auto-baudrate scan failed on {port_name} across all rates.",
        )

    def _probe_baudrate_sync(
        self,
        port_name: str,
        baudrate: int,
        payload: bytes,
        expected_response: Optional[bytes],
    ) -> tuple[bool, Optional[bytes], Optional[str]]:
        """Synchronously probe target port at specified baudrate with proper cleanup."""
        import serial

        ser: Optional[serial.Serial] = None
        try:
            ser = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                timeout=self.read_timeout,
                write_timeout=self.read_timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            # Flush existing buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Transmit probe burst
            ser.write(payload)
            ser.flush()

            # Read response
            response = ser.read(128)
            if response:
                if expected_response is not None:
                    if expected_response in response:
                        return True, response, None
                    return False, response, "Unexpected response content"
                return True, response, None

            return False, None, "Timeout (no bytes received)"
        except Exception as exc:
            return False, None, str(exc)
        finally:
            if ser is not None and ser.is_open:
                try:
                    ser.close()
                except Exception:
                    pass


class AsyncBusManager:
    """
    Thread-safe asynchronous bus coordinator.
    Distributes hardware events, manages port subscribers, and executes
    background device handshakes without blocking IO loops.
    """

    def __init__(self, queue_maxsize: int = 1000):
        self._queue: asyncio.Queue[BusEvent] = asyncio.Queue(maxsize=queue_maxsize)
        self._subscribers: Dict[Optional[Type[BusEvent]], Set[Callable[[BusEvent], Any]]] = {}
        self._running = False
        self._dispatcher_task: Optional[asyncio.Task[None]] = None
        self.port_tuner = DynamicPortTuner()

    async def start(self) -> None:
        """Start internal bus event dispatcher."""
        if self._running:
            return
        self._running = True
        self._dispatcher_task = asyncio.create_task(self._event_dispatcher_loop())
        logger.info("AsyncBusManager started successfully.")

    async def stop(self) -> None:
        """Stop bus dispatcher and drain event queue."""
        self._running = False
        if self._dispatcher_task:
            self._dispatcher_task.cancel()
            try:
                await self._dispatcher_task
            except asyncio.CancelledError:
                pass
            self._dispatcher_task = None
        logger.info("AsyncBusManager stopped.")

    def publish_threadsafe(self, event: BusEvent, loop: asyncio.AbstractEventLoop) -> None:
        """Thread-safe submission of a bus event from non-async contexts."""
        loop.call_soon_threadsafe(self._queue.put_nowait, event)

    async def publish(self, event: BusEvent) -> None:
        """Publish an event onto the thread-safe async queue."""
        await self._queue.put(event)

    def subscribe(
        self,
        event_type: Optional[Type[BusEvent]],
        callback: Callable[[BusEvent], Any],
    ) -> Callable[[], None]:
        """
        Subscribe a callback function to a specific event type or all events (None).
        Returns an unsubscribe callable for deterministic teardown.
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = set()
        self._subscribers[event_type].add(callback)

        def unsubscribe():
            if event_type in self._subscribers:
                self._subscribers[event_type].discard(callback)

        return unsubscribe

    async def listen(self) -> AsyncGenerator[BusEvent, None]:
        """Yield events as an asynchronous stream."""
        sub_queue: asyncio.Queue[BusEvent] = asyncio.Queue()

        def _listener(evt: BusEvent):
            sub_queue.put_nowait(evt)

        unsub = self.subscribe(None, _listener)
        try:
            while self._running:
                event = await sub_queue.get()
                yield event
        finally:
            unsub()

    async def _event_dispatcher_loop(self) -> None:
        """Continuously dequeues events and invokes matching subscribers."""
        while self._running:
            try:
                event = await self._queue.get()
                self._queue.task_done()

                # Notify specific subscribers and wildcard subscribers
                targets = list(self._subscribers.get(type(event), set())) + list(
                    self._subscribers.get(None, set())
                )

                for cb in targets:
                    try:
                        res = cb(event)
                        if asyncio.iscoroutine(res):
                            asyncio.create_task(res)
                    except Exception as exc:
                        logger.error("Error in bus subscriber callback: %s", exc)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Bus dispatcher error: %s", exc)

    async def tune_and_register_port(self, port_name: str) -> TuningResult:
        """
        Run DynamicPortTuner and emit bus events based on detection outcome.
        """
        result = await self.port_tuner.scan_port(port_name)
        if result.success and result.detected_baudrate:
            await self.publish(
                PortTunedBusEvent(
                    port=port_name,
                    negotiated_baudrate=result.detected_baudrate,
                    latency_ms=result.latency_ms,
                )
            )
        else:
            await self.publish(
                BusErrorEvent(
                    port=port_name,
                    error_code="BAUD_TUNE_FAILURE",
                    message=result.error_message or "Auto-baudrate scan failed",
                )
            )
        return result
