"""
SQLite Write-Ahead Logging (WAL) Transaction Ledger for Hardware Communication Logs.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteWALLedger:
    """
    Transaction ledger with Write-Ahead Logging (WAL) mode enabled.
    Executes non-blocking asynchronous disk writes using asyncio executors.
    """

    def __init__(self, db_path: str = "system_wal_ledger.db"):
        self.db_path = db_path
        self._lock = asyncio.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
            cursor.execute("PRAGMA foreign_keys = ON;")
        finally:
            cursor.close()
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transaction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    port TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()

    async def log_event(self, port: str, event_type: str, data: Dict[str, Any]) -> int:
        """Asynchronously log a communication or diagnostic event to WAL database."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_log_event, port, event_type, data)

    def _sync_log_event(self, port: str, event_type: str, data: Dict[str, Any]) -> int:
        data_json = json.dumps(data, ensure_ascii=False)
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO transaction_logs (port, event_type, data_json)
                VALUES (?, ?, ?);
                """,
                (port, event_type, data_json),
            )
            conn.commit()
            return cursor.lastrowid or 0

    async def query_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Query recent transaction logs asynchronously."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_query_logs, limit)

    def _sync_query_logs(self, limit: int) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, port, event_type, data_json, created_at
                FROM transaction_logs
                ORDER BY id DESC
                LIMIT ?;
                """,
                (limit,),
            ).fetchall()
            return [
                {
                    "id": r["id"],
                    "port": r["port"],
                    "event_type": r["event_type"],
                    "data": json.loads(r["data_json"]),
                    "created_at": r["created_at"],
                }
                for r in rows
            ]

    async def create_backup_snapshot(self) -> str:
        """Create a backup snapshot of the WAL database."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._sync_backup)

    def _sync_backup(self) -> str:
        backup_path = f"backup_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(self.db_path, backup_path)
        return backup_path
