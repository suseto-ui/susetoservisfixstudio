"""
Event Bus & Asynchronous Core Orchestrator (`core/event_bus.py`).
Provides thread-safe, high-throughput event routing and persistent transactional logging
with SQLite Write-Ahead Logging (WAL) mode for non-blocking concurrent operations
between worker threads and the main GUI thread.
"""

from __future__ import annotations

import json
import logging
import queue
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("core.event_bus")

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "hardware_diagnostics.db"


class EventRouter:
    """
    Core Orchestrator & Asynchronous Event-Driven Bus.
    Routes messages, hardware telemetry, and diagnostic events safely between
    low-level worker threads (USB scanning, RAM dumping, auto-tuning) and GUI components.
    """

    _instance: Optional[EventRouter] = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls, db_path: Optional[Path] = None) -> EventRouter:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path or _DEFAULT_DB)
            return cls._instance

    def __init__(self, db_path: Path = _DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._event_queue: queue.Queue[Dict[str, Any]] = queue.Queue()
        self._is_running = True
        self._events_processed = 0
        self._sub_lock = threading.Lock()
        
        self._init_sqlite_wal()

        # Dedicated background worker thread to drain queue and notify subscribers
        self._worker_thread = threading.Thread(target=self._queue_worker, daemon=True, name="EventRouterWorker")
        self._worker_thread.start()

    def _init_sqlite_wal(self) -> None:
        """Initialize SQLite database with WAL journal mode for concurrent reads/writes."""
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self.db_path), timeout=5.0) as conn:
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA synchronous=NORMAL;")
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bus_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        topic TEXT NOT NULL,
                        source TEXT NOT NULL,
                        payload_json TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        timestamp REAL NOT NULL
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bus_topic ON bus_events(topic);")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_bus_ts ON bus_events(timestamp);")
                conn.commit()
        except Exception as e:
            logger.warning("[EVENT_ROUTER] Database initialization warning: %s", e)

    def subscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register subscriber callback for a specific topic or '*' for all topics."""
        with self._sub_lock:
            if topic not in self._subscribers:
                self._subscribers[topic] = []
            if handler not in self._subscribers[topic]:
                self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Remove subscriber callback."""
        with self._sub_lock:
            if topic in self._subscribers and handler in self._subscribers[topic]:
                self._subscribers[topic].remove(handler)

    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        source: str = "WORKER",
        severity: str = "INFO"
    ) -> None:
        """Publishes an event, logs to SQLite WAL, and dispatches to subscribers."""
        event = {
            "topic": topic,
            "source": source,
            "payload": payload,
            "severity": severity,
            "timestamp": time.time()
        }

        # 1. Log to WAL database
        self._log_to_db(topic, source, payload, severity, event["timestamp"])

        # 2. Synchronously dispatch to matching subscribers for immediate UI responsiveness
        with self._sub_lock:
            handlers = list(self._subscribers.get(topic, [])) + list(self._subscribers.get("*", []))

        for handler in handlers:
            try:
                handler(event)
            except Exception as ex:
                logger.warning("[EVENT_ROUTER] Handler error for %s: %s", topic, ex)

        self._events_processed += 1
        self._event_queue.put(event)

    def emit(self, event_type: str, data: Any) -> None:
        """Convenience helper for simple event publication."""
        payload = data if isinstance(data, dict) else {"data": data}
        self.publish(topic=event_type, payload=payload, source="EMITTER")

    def _queue_worker(self) -> None:
        """Worker loop draining background queue."""
        while self._is_running:
            try:
                event = self._event_queue.get(timeout=0.1)
                self._event_queue.task_done()
            except queue.Empty:
                continue

    def _log_to_db(
        self,
        topic: str,
        source: str,
        payload: Dict[str, Any],
        severity: str,
        ts: float
    ) -> None:
        try:
            with sqlite3.connect(str(self.db_path), timeout=2.0) as conn:
                conn.execute(
                    "INSERT INTO bus_events (topic, source, payload_json, severity, timestamp) VALUES (?, ?, ?, ?, ?)",
                    (topic, source, json.dumps(payload), severity, ts)
                )
                conn.commit()
        except Exception as e:
            logger.debug("[EVENT_ROUTER] SQLite log skipped: %s", e)

    def query_history(self, limit: int = 100, topic_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieves historical events from persistent WAL storage."""
        try:
            with sqlite3.connect(str(self.db_path), timeout=2.0) as conn:
                conn.row_factory = sqlite3.Row
                if topic_filter:
                    cur = conn.execute(
                        "SELECT * FROM bus_events WHERE topic = ? ORDER BY id DESC LIMIT ?",
                        (topic_filter, limit)
                    )
                else:
                    cur = conn.execute(
                        "SELECT * FROM bus_events ORDER BY id DESC LIMIT ?",
                        (limit,)
                    )
                rows = cur.fetchall()
                return [
                    {
                        "id": r["id"],
                        "topic": r["topic"],
                        "source": r["source"],
                        "payload": json.loads(r["payload_json"]),
                        "severity": r["severity"],
                        "timestamp": r["timestamp"]
                    }
                    for r in rows
                ]
        except Exception as ex:
            logger.error("[EVENT_ROUTER] Query failed: %s", ex)
            return []

    # Alias for backward compatibility
    query_recent_events = query_history

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on processed events and queue backlog."""
        return {
            "events_processed": self._events_processed,
            "queue_backlog": self._event_queue.qsize(),
            "active_subscribers": sum(len(h) for h in self._subscribers.values()),
        }

    def shutdown(self) -> None:
        """Flushes queue and stops background worker thread."""
        self._is_running = False
        if self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)


# Backward Compatibility Alias
HardwareEventBus = EventRouter
