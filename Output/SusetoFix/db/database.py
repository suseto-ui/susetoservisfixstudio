"""
Database Manager for Windows Universal Hardware Diagnostic & Communication Engine.
Enforces SQLite Write-Ahead Logging (WAL) mode, connection pooling, and transactional integrity.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger("diagnostic_engine.db")


class DatabaseManager:
    """
    Thread-safe SQLite Database Manager operating in WAL (Write-Ahead Logging) mode.
    Handles device registration, operation auditing, and backup ledger records.
    """

    def __init__(self, db_path: str = "hardware_diagnostics.db", schema_file: Optional[str] = None):
        """
        Initialize database manager and enforce schema.

        Args:
            db_path: Path to SQLite database file. Use ':memory:' for isolated testing.
            schema_file: Optional explicit path to schema.sql file.
        """
        self.db_path = db_path
        self._schema_file = schema_file or str(Path(__file__).parent / "schema.sql")
        self._lock = asyncio.Lock()
        self._init_db()

    def _get_raw_connection(self) -> sqlite3.Connection:
        """Create and configure a low-level SQLite connection with WAL mode enabled."""
        conn = sqlite3.connect(
            self.db_path,
            timeout=10.0,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        
        # Enforce WAL mode and concurrency pragmas
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA busy_timeout = 5000;")
        finally:
            cursor.close()
        return conn

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager providing an auto-committing or rolling-back connection."""
        conn = self._get_raw_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Load schema.sql and create tables/indexes if they do not exist."""
        schema_path = Path(self._schema_file)
        if not schema_path.is_file():
            raise FileNotFoundError(f"Schema file not found at: {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()

        with self.connection() as conn:
            conn.executescript(schema_sql)
            logger.info("Database schema initialized with WAL mode at: %s", self.db_path)

    async def upsert_device_async(
        self,
        device_id: str,
        vid: str,
        pid: str,
        serial_number: Optional[str] = None,
        device_interface_guid: Optional[str] = None,
        port_name: Optional[str] = None,
        description: Optional[str] = None,
        manufacturer: Optional[str] = None,
        hardware_id: Optional[str] = None,
        status: str = "CONNECTED",
    ) -> None:
        """Asynchronously register or update a discovered device."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            self.upsert_device,
            device_id,
            vid,
            pid,
            serial_number,
            device_interface_guid,
            port_name,
            description,
            manufacturer,
            hardware_id,
            status,
        )

    def upsert_device(
        self,
        device_id: str,
        vid: str,
        pid: str,
        serial_number: Optional[str] = None,
        device_interface_guid: Optional[str] = None,
        port_name: Optional[str] = None,
        description: Optional[str] = None,
        manufacturer: Optional[str] = None,
        hardware_id: Optional[str] = None,
        status: str = "CONNECTED",
    ) -> None:
        """Insert or update device metadata."""
        query = """
        INSERT INTO devices (
            id, vid, pid, serial_number, device_interface_guid, port_name,
            description, manufacturer, hardware_id, status, last_seen_at
        ) VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
        )
        ON CONFLICT(id) DO UPDATE SET
            port_name = COALESCE(excluded.port_name, devices.port_name),
            description = COALESCE(excluded.description, devices.description),
            manufacturer = COALESCE(excluded.manufacturer, devices.manufacturer),
            device_interface_guid = COALESCE(excluded.device_interface_guid, devices.device_interface_guid),
            status = excluded.status,
            last_seen_at = CURRENT_TIMESTAMP;
        """
        with self.connection() as conn:
            conn.execute(
                query,
                (
                    device_id,
                    vid.upper(),
                    pid.upper(),
                    serial_number,
                    device_interface_guid,
                    port_name,
                    description,
                    manufacturer,
                    hardware_id,
                    status,
                ),
            )

    def mark_device_status(self, device_id: str, status: str) -> None:
        """Update hardware connection status ('CONNECTED', 'DISCONNECTED', 'FAULT')."""
        query = "UPDATE devices SET status = ?, last_seen_at = CURRENT_TIMESTAMP WHERE id = ?;"
        with self.connection() as conn:
            conn.execute(query, (status, device_id))

    def log_operation(
        self,
        device_id: str,
        operation_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: int = 0,
    ) -> int:
        """
        Record diagnostic or hardware operation audit trail.
        Returns the generated operation ID.
        """
        details_json = json.dumps(details or {}, ensure_ascii=False)
        query = """
        INSERT INTO operations_log (
            device_id, operation_type, status, details_json, error_message, duration_ms
        ) VALUES (?, ?, ?, ?, ?, ?);
        """
        with self.connection() as conn:
            cursor = conn.execute(
                query,
                (device_id, operation_type, status, details_json, error_message, duration_ms),
            )
            return cursor.lastrowid or 0

    def record_backup(
        self,
        device_id: str,
        backup_path: str,
        checksum_sha256: str,
        size_bytes: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Record created backup/firmware dump in the database."""
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False)
        query = """
        INSERT INTO backups (
            device_id, backup_path, checksum_sha256, size_bytes, metadata_json
        ) VALUES (?, ?, ?, ?, ?);
        """
        with self.connection() as conn:
            cursor = conn.execute(
                query,
                (device_id, backup_path, checksum_sha256, size_bytes, metadata_json),
            )
            return cursor.lastrowid or 0

    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve device record by primary identifier."""
        query = "SELECT * FROM devices WHERE id = ?;"
        with self.connection() as conn:
            row = conn.execute(query, (device_id,)).fetchone()
            return dict(row) if row else None

    def list_active_devices(self) -> List[Dict[str, Any]]:
        """List all devices currently marked CONNECTED."""
        query = "SELECT * FROM devices WHERE status = 'CONNECTED' ORDER BY last_seen_at DESC;"
        with self.connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(row) for row in rows]
