"""
Vendor Abstraction Layer (VAL) - Async Protocol Engine & Checksum Verification.
Supports SLIP/HDLC framing, XOR, CRC16, and MD5 integrity verification
for universal servicing in SusetoDroidFixStudio.
"""

from __future__ import annotations

import hashlib
import struct
from typing import List, Tuple, Optional, Union

# SLIP Special Character Constants
SLIP_END = 0xC0
SLIP_ESC = 0xDB
SLIP_ESC_END = 0xDC
SLIP_ESC_ESC = 0xDD

# HDLC Special Character Constants
HDLC_FLAG = 0x7E
HDLC_ESC = 0x7D
HDLC_XOR = 0x20


class ProtocolEngine:
    """
    High-performance framing and checksum engine supporting SLIP and HDLC protocols
    with XOR, CRC-16-CCITT, and MD5 data integrity checks.
    """

    @staticmethod
    def calculate_xor(data: bytes, initial: int = 0) -> int:
        """Calculate bitwise XOR checksum of data bytes."""
        checksum = initial
        for b in data:
            checksum ^= b
        return checksum & 0xFF

    @staticmethod
    def calculate_crc16(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
        """
        Calculate CRC-16-CCITT checksum (Polynomial 0x1021, default initial 0xFFFF).
        """
        crc = init
        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = ((crc << 1) ^ poly) & 0xFFFF
                else:
                    crc = (crc << 1) & 0xFFFF
        return crc & 0xFFFF

    @staticmethod
    def calculate_md5(data: bytes) -> str:
        """Calculate hex-encoded MD5 digest for large firmware payload blocks."""
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def calculate_md5_bytes(data: bytes) -> bytes:
        """Calculate binary 16-byte MD5 digest for data blocks."""
        return hashlib.md5(data).digest()

    @classmethod
    def encode_slip(cls, payload: bytes) -> bytes:
        """Encode raw bytes using SLIP framing (RFC 1055)."""
        escaped = bytearray()
        for b in payload:
            if b == SLIP_END:
                escaped.extend([SLIP_ESC, SLIP_ESC_END])
            elif b == SLIP_ESC:
                escaped.extend([SLIP_ESC, SLIP_ESC_ESC])
            else:
                escaped.append(b)
        return bytes([SLIP_END]) + bytes(escaped) + bytes([SLIP_END])

    @classmethod
    def decode_slip(cls, raw_stream: bytes) -> bytes:
        """Decode SLIP-framed byte stream back to unescaped bytes."""
        # Strip external SLIP_END delimiters
        stream = raw_stream.strip(bytes([SLIP_END]))
        unescaped = bytearray()
        escaping = False

        for b in stream:
            if escaping:
                if b == SLIP_ESC_END:
                    unescaped.append(SLIP_END)
                elif b == SLIP_ESC_ESC:
                    unescaped.append(SLIP_ESC)
                else:
                    unescaped.append(b)
                escaping = False
            elif b == SLIP_ESC:
                escaping = True
            else:
                unescaped.append(b)

        return bytes(unescaped)

    @classmethod
    def encode_hdlc(cls, payload: bytes) -> bytes:
        """Encode raw bytes using HDLC framing (Flag 0x7E, Escape 0x7D)."""
        escaped = bytearray()
        for b in payload:
            if b in (HDLC_FLAG, HDLC_ESC):
                escaped.extend([HDLC_ESC, b ^ HDLC_XOR])
            else:
                escaped.append(b)
        return bytes([HDLC_FLAG]) + bytes(escaped) + bytes([HDLC_FLAG])

    @classmethod
    def decode_hdlc(cls, raw_stream: bytes) -> bytes:
        """Decode HDLC-framed byte stream back to unescaped bytes."""
        stream = raw_stream.strip(bytes([HDLC_FLAG]))
        unescaped = bytearray()
        escaping = False

        for b in stream:
            if escaping:
                unescaped.append(b ^ HDLC_XOR)
                escaping = False
            elif b == HDLC_ESC:
                escaping = True
            else:
                unescaped.append(b)

        return bytes(unescaped)

    @classmethod
    def encode_frame(
        cls,
        cmd: int,
        payload: bytes,
        framing: str = "SLIP",
        checksum_type: str = "CRC16"
    ) -> bytes:
        """
        Encode command and payload into framed packet with integrity checksum.
        Frame body structure:
          - CMD: 2 bytes (Big-Endian unsigned short)
          - PAYLOAD: N bytes
          - CHECKSUM: 2 bytes (CRC16) or 1 byte (XOR)
        """
        header = struct.pack(">H", cmd & 0xFFFF)
        body_to_checksum = header + payload

        if checksum_type.upper() == "XOR":
            cs = cls.calculate_xor(body_to_checksum)
            checksum_bytes = struct.pack("B", cs)
        elif checksum_type.upper() == "MD5":
            checksum_bytes = cls.calculate_md5_bytes(body_to_checksum)
        else:  # Default CRC16
            cs = cls.calculate_crc16(body_to_checksum)
            checksum_bytes = struct.pack(">H", cs)

        packet = body_to_checksum + checksum_bytes

        if framing.upper() == "HDLC":
            return cls.encode_hdlc(packet)
        return cls.encode_slip(packet)

    @classmethod
    def decode_frame(
        cls,
        raw_bytes: bytes,
        checksum_type: str = "CRC16"
    ) -> Tuple[int, bytes]:
        """
        Decode framed packet, verify integrity checksum, and extract (cmd, payload).
        Automatically detects whether stream is HDLC (0x7E) or SLIP (0xC0).
        """
        if not raw_bytes:
            raise ValueError("Cannot decode empty frame stream.")

        if raw_bytes[0] == HDLC_FLAG or raw_bytes[-1] == HDLC_FLAG:
            body = cls.decode_hdlc(raw_bytes)
        else:
            body = cls.decode_slip(raw_bytes)

        if checksum_type.upper() == "XOR":
            if len(body) < 3:
                raise ValueError("Frame length too short for XOR checksum.")
            packet_data = body[:-1]
            expected_cs = body[-1]
            actual_cs = cls.calculate_xor(packet_data)
            if actual_cs != expected_cs:
                raise ValueError(f"XOR checksum mismatch: expected {expected_cs:#04x}, got {actual_cs:#04x}")
            cmd = struct.unpack(">H", packet_data[:2])[0]
            payload = packet_data[2:]
            return cmd, payload

        elif checksum_type.upper() == "MD5":
            if len(body) < 18:
                raise ValueError("Frame length too short for MD5 checksum.")
            packet_data = body[:-16]
            expected_md5 = body[-16:]
            actual_md5 = cls.calculate_md5_bytes(packet_data)
            if actual_md5 != expected_md5:
                raise ValueError("MD5 checksum verification failed.")
            cmd = struct.unpack(">H", packet_data[:2])[0]
            payload = packet_data[2:]
            return cmd, payload

        else:  # Default CRC16
            if len(body) < 4:
                raise ValueError("Frame length too short for CRC16 checksum.")
            packet_data = body[:-2]
            expected_crc = struct.unpack(">H", body[-2:])[0]
            actual_crc = cls.calculate_crc16(packet_data)
            if actual_crc != expected_crc:
                raise ValueError(f"CRC16 checksum mismatch: expected {expected_crc:#06x}, got {actual_crc:#06x}")
            cmd = struct.unpack(">H", packet_data[:2])[0]
            payload = packet_data[2:]
            return cmd, payload


# Backward compatibility for existing ESP32 Phase 03/04 test suites
class SLIPProtocolEngine:
    """
    Legacy wrapper for ESP32 ROM bootloader SLIP communication.
    """

    @staticmethod
    def encode_frame(payload: bytes) -> bytes:
        return ProtocolEngine.encode_slip(payload)

    @staticmethod
    def decode_frame(raw_stream: bytes) -> List[bytes]:
        frames: List[bytes] = []
        current_frame = bytearray()
        escaping = False

        for b in raw_stream:
            if b == SLIP_END:
                if len(current_frame) > 0:
                    frames.append(bytes(current_frame))
                    current_frame = bytearray()
                escaping = False
            elif escaping:
                if b == SLIP_ESC_END:
                    current_frame.append(SLIP_END)
                elif b == SLIP_ESC_ESC:
                    current_frame.append(SLIP_ESC)
                else:
                    current_frame.append(b)
                escaping = False
            elif b == SLIP_ESC:
                escaping = True
            else:
                current_frame.append(b)

        return frames

    @staticmethod
    def calculate_checksum(data: bytes, initial: int = 0xEF) -> int:
        checksum = initial
        for b in data:
            checksum ^= b
        return checksum

    @staticmethod
    def verify_checksum(data: bytes, expected: int) -> bool:
        return SLIPProtocolEngine.calculate_checksum(data) == expected
