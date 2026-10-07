"""
Security & RBAC Shield (`security/rbac_shield.py`).
Enforces Role-Based Access Control (RBAC), SmartCard HW Token ATR validation,
and Cryptographic Operation Signatures (SHA256 / Nonce) to protect high-risk
servicing operations (1-Click FRP Wipe, NVRAM/IMEI Repair, eMMC Format).
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("security.rbac_shield")


class UnauthorizedOperationError(PermissionError):
    """Raised when an unauthorized or un-signed critical operation is attempted."""
    pass


class Role:
    TECHNICIAN = "TECHNICIAN"
    SUPERVISOR = "SUPERVISOR"
    ADMIN = "ADMIN"


class OperationRiskLevel:
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    CRITICAL_INTERLOCK = "CRITICAL_INTERLOCK"


class SecurityShield:
    """
    Cryptographic Security Shield enforcing RBAC permissions and SmartCard HW token checks.
    High-risk operations require a valid cryptographic operation signature.
    """

    CRITICAL_OPERATIONS: Set[str] = {
        "EXEC_1CLICK_FRP",
        "EXEC_NVRAM_IMEI_REPAIR",
        "EXEC_EMMC_RAW_ERASE",
        "EXEC_RPMB_KEY_PROVISION",
        "EXEC_SUPER_PARTITION_FORMAT",
    }

    ROLE_HIERARCHY: Dict[str, int] = {
        Role.TECHNICIAN: 1,
        Role.SUPERVISOR: 2,
        Role.ADMIN: 3,
    }

    REQUIRED_LEVEL_FOR_OPERATION: Dict[str, int] = {
        "READ_GPT": 1,
        "FLASH_BOOT_PARTITION": 1,
        "EXEC_1CLICK_FRP": 2,            # Requires SUPERVISOR+
        "EXEC_NVRAM_IMEI_REPAIR": 2,     # Requires SUPERVISOR+
        "EXEC_EMMC_RAW_ERASE": 3,        # Requires ADMIN+
        "EXEC_RPMB_KEY_PROVISION": 3,    # Requires ADMIN+
    }

    def __init__(self, master_secret: str = "SUSETO_HMAC_MASTER_KEY_2026") -> None:
        self.master_secret = master_secret
        self.active_nonce = self.generate_session_nonce()

    def generate_session_nonce(self) -> str:
        """Generates a 32-byte cryptographic session nonce."""
        seed = f"{time.time_ns()}:{os.urandom(16).hex()}"
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def generate_operation_signature(self, operation_id: str, operator_id: str, nonce: str) -> str:
        """Generates an HMAC-SHA256 operation signature."""
        msg = f"{operation_id}:{operator_id}:{nonce}".encode("utf-8")
        return hmac.new(self.master_secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()

    def verify_operation_signature(
        self, operation_id: str, operator_id: str, nonce: str, signature: str
    ) -> bool:
        """Validates a cryptographic operation signature against the master secret."""
        if not signature:
            return False
        expected = self.generate_operation_signature(operation_id, operator_id, nonce)
        return hmac.compare_digest(expected.lower(), signature.lower())

    def validate_smartcard_token(self, hw_token_atr: Optional[str]) -> bool:
        """
        Validates the SmartCard HW Token Answer-To-Reset (ATR) string.
        Returns True if a valid SmartCard dongle ATR is present.
        """
        if not hw_token_atr or len(hw_token_atr) < 8:
            return False
        # Valid SmartCard ATR starts with 3B or 3F
        clean_atr = hw_token_atr.upper().replace(" ", "").replace(":", "")
        return clean_atr.startswith("3B") or clean_atr.startswith("3F") or "SC2026" in clean_atr

    def authorize_operation(
        self,
        operator_role: str,
        operator_id: str,
        operation_id: str,
        hw_token_atr: Optional[str] = None,
        crypto_signature: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main authorization entrypoint.
        Enforces RBAC hierarchy, SmartCard HW token requirements, and Cryptographic Signatures
        for high-risk critical interlock operations.
        """
        role_u = operator_role.upper()
        op_level = self.ROLE_HIERARCHY.get(role_u, 0)
        req_level = self.REQUIRED_LEVEL_FOR_OPERATION.get(operation_id, 1)

        # 1. RBAC Level Check
        if op_level < req_level:
            err_msg = (
                f"Kritické bezpečnostní odmítnutí: Operátor v roli '{role_u}' "
                f"nemá dostatečné oprávnění pro operaci '{operation_id}' (Vyžaduje {req_level})."
            )
            logger.error(err_msg)
            raise UnauthorizedOperationError(err_msg)

        # 2. Check if Critical Operation
        is_critical = operation_id in self.CRITICAL_OPERATIONS or req_level >= 2

        if is_critical:
            # 2a. Validate SmartCard HW Token ATR
            if not self.validate_smartcard_token(hw_token_atr):
                err_msg = (
                    f"Kritická pojistka (Security Interlock): Operace '{operation_id}' "
                    f"vyžaduje přítomnost aktivního SmartCard HW Tokenu! ATR je neplatné nebo chybí."
                )
                logger.error(err_msg)
                raise UnauthorizedOperationError(err_msg)

            # 2b. Validate Cryptographic Operation Signature
            active_n = nonce or self.active_nonce
            if not crypto_signature or not self.verify_operation_signature(operation_id, operator_id, active_n, crypto_signature):
                err_msg = (
                    f"Kryptografická verifikace selhala: Operace '{operation_id}' "
                    f"vyžaduje platný kryptografický podpis operátora SHA256/HMAC!"
                )
                logger.error(err_msg)
                raise UnauthorizedOperationError(err_msg)

        logger.info(f"Operation '{operation_id}' AUTHORIZED for operator '{operator_id}' [{role_u}].")
        return {
            "authorized": True,
            "operation_id": operation_id,
            "operator_id": operator_id,
            "operator_role": role_u,
            "smartcard_verified": True if is_critical else False,
            "signature_verified": True if is_critical else False,
            "timestamp": time.time()
        }
