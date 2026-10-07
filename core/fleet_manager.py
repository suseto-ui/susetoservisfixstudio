"""
Enterprise Multi-Tenant Fleet Manager for SusetoDroidFixStudio.
Implements Role-Based Access Control (RBAC: TECHNICIAN, SUPERVISOR, ADMIN),
tenant isolation, centralized configuration distribution, and hardware capability enforcement.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("fleet_manager")


class UserRole:
    TECHNICIAN = "TECHNICIAN"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


# Permission matrices for service actions
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    UserRole.TECHNICIAN: {
        "READ_DIAGNOSTICS",
        "READ_PARTITIONS",
        "FASTBOOT_INFO",
        "BACKUP_NVRAM",
    },
    UserRole.SUPERVISOR: {
        "READ_DIAGNOSTICS",
        "READ_PARTITIONS",
        "FASTBOOT_INFO",
        "BACKUP_NVRAM",
        "FRP_UNLOCK",
        "WRITE_PARTITIONS",
        "EXPORT_DUMP",
    },
    UserRole.ADMIN: {
        "READ_DIAGNOSTICS",
        "READ_PARTITIONS",
        "FASTBOOT_INFO",
        "BACKUP_NVRAM",
        "FRP_UNLOCK",
        "WRITE_PARTITIONS",
        "EXPORT_DUMP",
        "ERASE_BOOTLOADER",
        "MANAGE_STATIONS",
        "VIEW_AUDIT_LOGS",
        "CONFIGURE_FLEET",
    },
}


@dataclass
class ServiceStation:
    station_id: str
    tenant_id: str
    hwid: str
    station_name: str
    assigned_user: str
    role: str = UserRole.TECHNICIAN
    status: str = "ONLINE"
    last_heartbeat: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "station_id": self.station_id,
            "tenant_id": self.tenant_id,
            "hwid": self.hwid,
            "station_name": self.station_name,
            "assigned_user": self.assigned_user,
            "role": self.role,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
        }


class FleetManager:
    """
    Coordinates multi-tenant organizational structure, station registration, and RBAC authorization.
    """

    def __init__(self, tenant_id: str = "TENANT_MAIN_LAB") -> None:
        self.tenant_id = tenant_id
        self.stations: Dict[str, ServiceStation] = {}
        self.active_station_id: Optional[str] = None
        self.active_role: str = UserRole.TECHNICIAN
        self.fleet_config: Dict[str, Any] = {
            "allow_cloud_sync": True,
            "enforce_dongle": False,
            "max_concurrent_unlocks": 5,
        }

    def register_station(
        self,
        station_id: str,
        hwid: str,
        station_name: str,
        assigned_user: str,
        role: str = UserRole.TECHNICIAN,
        tenant_id: Optional[str] = None,
    ) -> ServiceStation:
        """Register or update a bench station within tenant scope."""
        t_id = tenant_id or self.tenant_id
        station = ServiceStation(
            station_id=station_id,
            tenant_id=t_id,
            hwid=hwid,
            station_name=station_name,
            assigned_user=assigned_user,
            role=role,
            status="ONLINE",
            last_heartbeat=time.time(),
        )
        self.stations[station_id] = station
        logger.info("Registered station '%s' (User: %s, Role: %s) for Tenant: %s", station_id, assigned_user, role, t_id)
        return station

    def set_active_station(self, station_id: str) -> bool:
        """Switch current local station context and activate role permissions."""
        if station_id not in self.stations:
            logger.warning("Station '%s' not registered in fleet.", station_id)
            return False

        station = self.stations[station_id]
        if station.tenant_id != self.tenant_id:
            logger.critical("TENANT ISOLATION VIOLATION: Cross-tenant access attempted for %s!", station_id)
            raise PermissionError(f"Access denied: Station belongs to different tenant '{station.tenant_id}'.")

        self.active_station_id = station_id
        self.active_role = station.role
        logger.info("Active station set to '%s' with role %s.", station_id, self.active_role)
        return True

    def is_action_permitted(self, action_name: str, role: Optional[str] = None) -> bool:
        """Check if an action is allowed for the target or current active role."""
        check_role = role or self.active_role
        perms = ROLE_PERMISSIONS.get(check_role, set())
        allowed = action_name in perms
        if not allowed:
            logger.warning("Permission denied for action '%s' under role '%s'.", action_name, check_role)
        return allowed

    def get_tenant_stations(self, tenant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all stations matching the active tenant."""
        t_id = tenant_id or self.tenant_id
        return [s.to_dict() for s in self.stations.values() if s.tenant_id == t_id]

    def update_heartbeat(self, station_id: str) -> bool:
        """Record live heartbeat telemetry from a service bench."""
        if station_id in self.stations:
            self.stations[station_id].last_heartbeat = time.time()
            self.stations[station_id].status = "ONLINE"
            return True
        return False
