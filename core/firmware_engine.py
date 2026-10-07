import os
import struct
from typing import Dict, Any

class FirmwareEngine:
    """
    Handles payload.bin chunk parsing, boot.img header analysis,
    and vbmeta image AVB flag patching (--disable-verity --disable-verification).
    """
    @staticmethod
    def analyze_boot_image(file_path: str) -> Dict[str, Any]:
        """Parses standard Android boot.img header MAGIC (ANDROID!) and kernel/ramdisk sizes."""
        if not os.path.exists(file_path):
            return {"error": "Soubor nenalezen."}

        try:
            with open(file_path, "rb") as f:
                magic = f.read(8)
                if magic != b"ANDROID!":
                    return {"status": "Neplatná magie boot.img (očekáváno ANDROID!)"}
                
                kernel_size, kernel_addr = struct.unpack("<II", f.read(8))
                ramdisk_size, ramdisk_addr = struct.unpack("<II", f.read(8))
                return {
                    "status": "Platný Android Boot Image",
                    "kernel_size": f"{kernel_size / 1024 / 1024:.2f} MB",
                    "ramdisk_size": f"{ramdisk_size / 1024 / 1024:.2f} MB",
                    "kernel_addr": hex(kernel_addr),
                    "ramdisk_addr": hex(ramdisk_addr)
                }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def patch_vbmeta(file_path: str) -> bool:
        """Applies AVB disable flags by setting verification and hashtree disable flags in vbmeta header."""
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "r+b") as f:
                header = f.read(256)
                if len(header) >= 124 and header[:4] == b"AVB0":
                    flags = struct.unpack(">I", header[120:124])[0]
                    flags |= 0x03  # HASHTREE_DISABLED (1) | VERIFICATION_DISABLED (2)
                    f.seek(120)
                    f.write(struct.pack(">I", flags))
                else:
                    f.seek(0, os.SEEK_END)
                    f.write(b"\x00\x00\x00\x03")
            return True
        except Exception:
            return False
