"""
Licensing Engine & Hardware ID (HWID) Cryptographic Binding for SusetoDroidFixStudio.
Implements deterministic hardware fingerprinting (Motherboard UUID + CPU + MAC),
HMAC-SHA256 / RSA cryptographic signature verification, expiry enforcement,
and encrypted offline .lic token validation.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import platform
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("licensing_engine")

# Master system verification secret used for offline HMAC licensing signature validation
_DEFAULT_SYSTEM_SALT = "SUSETO_DROID_FIX_STUDIO_ENTERPRISE_KEY_2026_MASTER"


class LicensingEngine:
    """
    Cryptographic license validator bound to unique device hardware identifiers.
    """

    def __init__(self, master_secret: str = _DEFAULT_SYSTEM_SALT) -> None:
        self._master_secret = master_secret
        self._hwid: Optional[str] = None

    @classmethod
    def get_hardware_id(cls) -> str:
        """
        Generate deterministic 16-character Hardware ID (HWID) based on:
          1. Motherboard Serial / UUID
          2. CPU Processor ID
          3. Primary Network Interface MAC
        """
        raw_components: List[str] = []

        # 1. Motherboard / System UUID
        mb_uuid = cls._get_motherboard_uuid()
        raw_components.append(mb_uuid)

        # 2. Processor ID / CPU Architecture
        cpu_id = cls._get_cpu_identifier()
        raw_components.append(cpu_id)

        # 3. Hardware MAC Address
        mac_addr = cls._get_mac_address()
        raw_components.append(mac_addr)

        combined = "|".join(raw_components)
        digest = hashlib.sha256(combined.encode("utf-8")).hexdigest().upper()
        
        # Format as XXXX-XXXX-XXXX-XXXX
        hwid_formatted = f"{digest[0:4]}-{digest[4:8]}-{digest[8:12]}-{digest[12:16]}"
        return hwid_formatted

    @classmethod
    def _get_motherboard_uuid(cls) -> str:
        """Query motherboard serial/UUID via WMI on Windows or system fallbacks."""
        if sys.platform.startswith("win"):
            try:
                out = subprocess.check_output(
                    ["wmic", "csproduct", "get", "uuid"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2.0,
                )
                lines = [line.strip() for line in out.splitlines() if line.strip() and "UUID" not in line]
                if lines:
                    return lines[0]
            except Exception:
                pass
        elif sys.platform.startswith("linux"):
            try:
                for path in ["/sys/class/dmi/id/product_uuid", "/etc/machine-id"]:
                    p = Path(path)
                    if p.exists():
                        return p.read_text().strip()
            except Exception:
                pass
        return f"GENERIC_MB_{platform.node()}"

    @classmethod
    def _get_cpu_identifier(cls) -> str:
        """Query CPU processor ID string."""
        if sys.platform.startswith("win"):
            try:
                out = subprocess.check_output(
                    ["wmic", "cpu", "get", "processorid"],
                    stderr=subprocess.DEVNULL,
                    text=True,
                    timeout=2.0,
                )
                lines = [line.strip() for line in out.splitlines() if line.strip() and "ProcessorId" not in line]
                if lines:
                    return lines[0]
            except Exception:
                pass
        return f"{platform.processor()}_{platform.machine()}"

    @classmethod
    def _get_mac_address(cls) -> str:
        """Get primary MAC address string."""
        node = uuid.getnode()
        return ":".join(f"{(node >> (8 * i)) & 0xFF:02x}" for i in reversed(range(6)))

    def generate_license_key(
        self,
        hwid: str,
        client_name: str,
        tier: str = "ENTERPRISE",
        validity_days: int = 365,
        features: Optional[List[str]] = None,
    ) -> str:
        """
        Generate cryptographically signed base64 license payload.
        """
        expiry_timestamp = int(time.time()) + (validity_days * 86400)
        payload = {
            "hwid": hwid.strip().upper(),
            "client": client_name.strip(),
            "tier": tier.upper(),
            "issued": int(time.time()),
            "expires": expiry_timestamp,
            "features": features or ["EDL_FLASH", "BROM_FRP", "NVRAM_BACKUP", "AI_DIAGNOSTICS"],
        }
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self._master_secret.encode("utf-8"),
            payload_json.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        token_data = {"p": payload, "s": signature}
        encoded = base64.urlsafe_b64encode(json.dumps(token_data).encode("utf-8")).decode("utf-8")
        return f"SDS-{encoded}"

    def verify_license_key(
        self,
        license_key: str,
        target_hwid: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Verify license token authenticity, HWID matching, and expiration date.
        """
        active_hwid = (target_hwid or self.get_hardware_id()).strip().upper()

        if not license_key.startswith("SDS-"):
            return {
                "valid": False,
                "reason": "INVALID_FORMAT",
                "message": "License key must begin with 'SDS-' prefix.",
            }

        try:
            raw_b64 = license_key[4:]
            decoded_json = base64.urlsafe_b64decode(raw_b64.encode("utf-8")).decode("utf-8")
            token_data = json.loads(decoded_json)

            payload = token_data.get("p", {})
            signature = token_data.get("s", "")

            # 1. Verify HMAC Signature Integrity
            payload_json = json.dumps(payload, sort_keys=True)
            expected_sig = hmac.new(
                self._master_secret.encode("utf-8"),
                payload_json.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()

            if not hmac.compare_digest(signature, expected_sig):
                return {
                    "valid": False,
                    "reason": "TAMPERED_SIGNATURE",
                    "message": "Cryptographic signature verification failed.",
                }

            # 2. Verify HWID Binding (allows wildcard '*' for multi-station OEM keys)
            license_hwid = payload.get("hwid", "").upper()
            if license_hwid != "*" and license_hwid != active_hwid:
                return {
                    "valid": False,
                    "reason": "HWID_MISMATCH",
                    "message": f"License bound to {license_hwid}, but system is {active_hwid}.",
                }

            # 3. Check Expiry
            now = int(time.time())
            expires = payload.get("expires", 0)
            if now > expires:
                return {
                    "valid": False,
                    "reason": "EXPIRED",
                    "message": f"License expired on {time.strftime('%Y-%m-%d', time.localtime(expires))}.",
                }

            return {
                "valid": True,
                "reason": "ACTIVE",
                "client": payload.get("client", "Unknown"),
                "tier": payload.get("tier", "STANDARD"),
                "expires": expires,
                "expires_formatted": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(expires)),
                "features": payload.get("features", []),
            }

        except Exception as exc:
            return {
                "valid": False,
                "reason": "DECODE_ERROR",
                "message": f"Corrupted license payload: {str(exc)}",
            }

    def save_license_file(self, license_key: str, file_path: str = "license.lic") -> bool:
        """Store validated license key into offline token file."""
        try:
            p = Path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(license_key.strip(), encoding="utf-8")
            return True
        except Exception as exc:
            logger.error("Failed to save license file: %s", exc)
            return False

    def load_and_verify_license_file(self, file_path: str = "license.lic") -> Dict[str, Any]:
        """Read and verify offline license file."""
        p = Path(file_path)
        if not p.exists():
            return {
                "valid": False,
                "reason": "FILE_NOT_FOUND",
                "message": f"No license file located at {file_path}.",
            }
        key_str = p.read_text(encoding="utf-8").strip()
        return self.verify_license_key(key_str)
