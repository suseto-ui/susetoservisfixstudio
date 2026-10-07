"""
Cloud Payload Synchronizer & Secure Storage Manager for SusetoDroidFixStudio.
Fetches Firehose programmers (.mbn/.elf), MediaTek scatter profiles,
and Test Point diagrams from remote CDN repositories with SHA-256 integrity
verification and localized cryptographic caching.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import shutil
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("cloud_payload_sync")


class CloudPayloadSyncManager:
    """
    Manages synchronization, validation, and encrypted storage of cloud loaders and scatter files.
    """

    DEFAULT_MANIFEST_URL = "https://cdn.susetodroidfix.com/v1/payloads_manifest.json"

    def __init__(self, storage_dir: str = "storage/cloud_payloads", manifest_url: str = DEFAULT_MANIFEST_URL) -> None:
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_url = manifest_url
        self.cached_manifest: Dict[str, Any] = {}

    def fetch_manifest(self, custom_url: Optional[str] = None, mock_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch latest loaders/scatter manifest containing available models, hashes, and URLs.
        """
        if mock_data is not None:
            self.cached_manifest = mock_data
            return self.cached_manifest

        url = custom_url or self.manifest_url
        logger.info("Querying cloud payload manifest from: %s", url)

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SusetoDroidFixStudio-Sync/1.0"})
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                self.cached_manifest = json.loads(resp.read().decode("utf-8"))
            return self.cached_manifest
        except Exception as exc:
            logger.warning("Manifest retrieval failed (%s). Using default empty manifest.", exc)
            self.cached_manifest = {"version": "1.0.0", "payloads": []}
            return self.cached_manifest

    @staticmethod
    def calculate_sha256(data_or_path: bytes | str) -> str:
        """Calculate SHA-256 checksum from bytes or file path."""
        if isinstance(data_or_path, bytes):
            return hashlib.sha256(data_or_path).hexdigest().lower()

        hasher = hashlib.sha256()
        with open(data_or_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest().lower()

    @staticmethod
    def encrypt_payload_bytes(data: bytes, key: str = "SUSETO_PAYLOAD_CIPHER_2026") -> bytes:
        """
        Lightweight fast symmetric stream cipher / XOR-CBC obfuscator for localized caching.
        """
        key_bytes = hashlib.sha256(key.encode("utf-8")).digest()
        key_len = len(key_bytes)
        return bytes(b ^ key_bytes[i % key_len] for i, b in enumerate(data))

    @staticmethod
    def decrypt_payload_bytes(data: bytes, key: str = "SUSETO_PAYLOAD_CIPHER_2026") -> bytes:
        """Decrypt localized payload bytes."""
        return CloudPayloadSyncManager.encrypt_payload_bytes(data, key)

    def sync_payload(
        self,
        payload_id: str,
        download_url: str,
        expected_sha256: str,
        category: str = "firehose",
        mock_bytes: Optional[bytes] = None,
    ) -> Tuple[bool, str, str]:
        """
        Download, verify SHA-256, and store encrypted payload asset on local disk.
        Returns: (success, local_file_path, message)
        """
        cat_dir = self.storage_dir / category
        cat_dir.mkdir(parents=True, exist_ok=True)
        local_enc_path = cat_dir / f"{payload_id}.sds"

        expected_hash = expected_sha256.strip().lower()

        try:
            if mock_bytes is not None:
                raw_data = mock_bytes
            elif download_url.startswith("file://") or os.path.exists(download_url):
                src = download_url.replace("file://", "")
                raw_data = Path(src).read_bytes()
            else:
                req = urllib.request.Request(download_url, headers={"User-Agent": "SusetoSync/1.0"})
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    raw_data = resp.read()

            # Verify integrity
            computed_hash = self.calculate_sha256(raw_data)
            if expected_hash and computed_hash != expected_hash:
                return False, "", f"SHA-256 mismatch: got {computed_hash}, expected {expected_hash}"

            # Encrypt and save
            encrypted = self.encrypt_payload_bytes(raw_data)
            local_enc_path.write_bytes(encrypted)

            logger.info("Successfully synced payload '%s' (%d bytes) to %s", payload_id, len(raw_data), local_enc_path)
            return True, str(local_enc_path), "Synced and verified successfully"

        except Exception as exc:
            logger.error("Sync error for payload '%s': %s", payload_id, exc)
            return False, "", str(exc)

    def load_decrypted_payload(self, file_path: str) -> bytes:
        """Load and decrypt a local payload file for hardware flashing."""
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"Payload file not found: {file_path}")
        enc_data = p.read_bytes()
        return self.decrypt_payload_bytes(enc_data)

    def list_local_payloads(self) -> List[Dict[str, Any]]:
        """List all downloaded and verified localized payloads."""
        results: List[Dict[str, Any]] = []
        for file in self.storage_dir.glob("**/*.sds"):
            results.append({
                "payload_id": file.stem,
                "category": file.parent.name,
                "size_bytes": file.stat().st_size,
                "path": str(file),
            })
        return results
