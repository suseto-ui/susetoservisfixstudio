-- ==============================================================================
-- Modular Windows Universal Hardware Diagnostic & Communication Engine
-- Architecture Database Schema (SQLite with Write-Ahead Logging)
-- Target: Windows Hardware Bus Diagnostics & Operations Persistence
-- ==============================================================================

PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- ------------------------------------------------------------------------------
-- Table: devices
-- Stores unique enumerated USB/Serial hardware devices discovered by the bus.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS devices (
    id TEXT PRIMARY KEY,
    vid TEXT NOT NULL,
    pid TEXT NOT NULL,
    serial_number TEXT,
    device_interface_guid TEXT,
    port_name TEXT,
    description TEXT,
    manufacturer TEXT,
    hardware_id TEXT,
    status TEXT NOT NULL DEFAULT 'CONNECTED', -- 'CONNECTED', 'DISCONNECTED', 'FAULT'
    first_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_devices_vid_pid ON devices (vid, pid);
CREATE INDEX IF NOT EXISTS idx_devices_port_name ON devices (port_name);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices (status);

-- ------------------------------------------------------------------------------
-- Table: operations_log
-- Audit log of hardware operations, diagnostic probes, and bus state transitions.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS operations_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,             -- 'ENUMERATION', 'BAUD_SCAN', 'DIAGNOSTIC_PROBE', 'BACKUP_DUMP', 'REFLASH'
    status TEXT NOT NULL,                     -- 'SUCCESS', 'FAILED', 'IN_PROGRESS', 'TIMEOUT'
    details_json TEXT NOT NULL DEFAULT '{}',
    error_message TEXT,
    duration_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_operations_device_created ON operations_log (device_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_operations_type ON operations_log (operation_type);

-- ------------------------------------------------------------------------------
-- Table: backups
-- Stores records of firmware, NVRAM, EEPROM, and configuration dumps.
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    backup_path TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_backups_device ON backups (device_id);
CREATE INDEX IF NOT EXISTS idx_backups_checksum ON backups (checksum_sha256);
