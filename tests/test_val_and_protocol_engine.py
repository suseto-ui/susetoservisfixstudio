"""
Unit Test Suite for Vendor Abstraction Layer (VAL) and Protocol Engine.
Tests SLIP/HDLC framing, XOR/CRC16/MD5 checksums, BaseDeviceAdapter,
MTKBromAdapter handshake & FRP erase, and QualcommEDLAdapter Firehose XML.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.protocol_engine import ProtocolEngine, SLIPProtocolEngine
from adapters.base_adapter import BaseDeviceAdapter
from adapters.mtk_brom_adapter import MTKBromAdapter
from adapters.qualcomm_edl_adapter import QualcommEDLAdapter


class TestProtocolEngine(unittest.TestCase):
    def test_checksum_xor(self):
        data = b"\x01\x02\x03\x04"
        # 1 ^ 2 ^ 3 ^ 4 = 4
        self.assertEqual(ProtocolEngine.calculate_xor(data), 4)

    def test_checksum_crc16(self):
        data = b"123456789"
        crc = ProtocolEngine.calculate_crc16(data)
        self.assertIsInstance(crc, int)
        self.assertGreater(crc, 0)

    def test_checksum_md5(self):
        data = b"SusetoDroidFixStudio"
        md5_hex = ProtocolEngine.calculate_md5(data)
        self.assertEqual(len(md5_hex), 32)
        md5_bytes = ProtocolEngine.calculate_md5_bytes(data)
        self.assertEqual(len(md5_bytes), 16)

    def test_slip_framing_roundtrip(self):
        payload = b"TEST\xC0SLIP\xDBDATA"
        encoded = ProtocolEngine.encode_slip(payload)
        self.assertTrue(encoded.startswith(b"\xC0"))
        self.assertTrue(encoded.endswith(b"\xC0"))
        decoded = ProtocolEngine.decode_slip(encoded)
        self.assertEqual(decoded, payload)

    def test_hdlc_framing_roundtrip(self):
        payload = b"TEST\x7EHDLC\x7DDATA"
        encoded = ProtocolEngine.encode_hdlc(payload)
        self.assertTrue(encoded.startswith(b"\x7E"))
        self.assertTrue(encoded.endswith(b"\x7E"))
        decoded = ProtocolEngine.decode_hdlc(encoded)
        self.assertEqual(decoded, payload)

    def test_encode_and_decode_frame_slip_crc16(self):
        cmd = 0x1234
        payload = b"PAYLOAD_FIRMWARE_BLOCK"
        framed = ProtocolEngine.encode_frame(cmd, payload, framing="SLIP", checksum_type="CRC16")
        
        decoded_cmd, decoded_payload = ProtocolEngine.decode_frame(framed, checksum_type="CRC16")
        self.assertEqual(decoded_cmd, cmd)
        self.assertEqual(decoded_payload, payload)

    def test_encode_and_decode_frame_hdlc_xor(self):
        cmd = 0x00A5
        payload = b"HDLC_FAST_PACKET"
        framed = ProtocolEngine.encode_frame(cmd, payload, framing="HDLC", checksum_type="XOR")
        
        decoded_cmd, decoded_payload = ProtocolEngine.decode_frame(framed, checksum_type="XOR")
        self.assertEqual(decoded_cmd, cmd)
        self.assertEqual(decoded_payload, payload)

    def test_decode_corrupted_frame_fails(self):
        cmd = 0x0001
        payload = b"ORIGINAL_DATA"
        framed = bytearray(ProtocolEngine.encode_frame(cmd, payload, checksum_type="CRC16"))
        # Corrupt one payload byte inside frame
        framed[4] ^= 0xFF
        with self.assertRaises(ValueError):
            ProtocolEngine.decode_frame(bytes(framed), checksum_type="CRC16")


class TestMTKBromAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = MTKBromAdapter()

    def test_connect_and_handshake(self):
        connected = self.adapter.connect("COM5", baudrate=115200)
        self.assertTrue(connected)
        self.assertTrue(self.adapter.is_connected)

    def test_send_command_and_flash_rw(self):
        self.adapter.connect("COM5")
        resp = self.adapter.send_command(0xD1, b"\x00\x01")
        self.assertGreater(len(resp), 0)

        write_ok = self.adapter.write_flash_block(0x00100000, b"\xAA\xBB\xCC\xDD")
        self.assertTrue(write_ok)

        data = self.adapter.read_flash_block(0x00100000, 4)
        self.assertEqual(len(data), 4)

    def test_erase_frp_by_address(self):
        self.adapter.connect("COM5")
        # Test erasing FRP partition defined by scatter address
        result = self.adapter.erase_frp_by_address("0x2d88000", "0x100000")
        self.assertTrue(result)

    def test_erase_frp_invalid_address(self):
        result = self.adapter.erase_frp_by_address("INVALID_HEX", "0x1000")
        self.assertFalse(result)


class TestQualcommEDLAdapter(unittest.TestCase):
    def setUp(self):
        self.adapter = QualcommEDLAdapter()

    def test_connect(self):
        res = self.adapter.connect("COM3")
        self.assertTrue(res)
        self.assertTrue(self.adapter.is_connected)

    def test_firehose_configure_and_xml(self):
        self.adapter.connect("COM3")
        cfg_resp = self.adapter.configure_firehose(max_payload_size=1048576, target_name="eMMC")
        self.assertIn("ACK", cfg_resp)

    def test_load_programmer(self):
        self.adapter.connect("COM3")
        with tempfile.NamedTemporaryFile(suffix=".mbn", delete=False) as f:
            f.write(b"MOCK_FIREHOSE_PROGRAMMER_BINARY_PAYLOAD")
            prog_path = f.name

        try:
            loaded = self.adapter.load_programmer(prog_path)
            self.assertTrue(loaded)
        finally:
            if os.path.exists(prog_path):
                os.remove(prog_path)

    def test_flash_rawprogram_xml(self):
        self.adapter.connect("COM3")
        rawprog_xml = (
            '<?xml version="1.0" ?>\n'
            '<data>\n'
            '  <program SECTOR_SIZE_IN_BYTES="512" file_sector_offset="0" filename="boot.img" '
            'label="boot" num_partition_sectors="65536" physical_partition_number="0" start_sector="1048576"/>\n'
            '</data>'
        )
        with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as f:
            f.write(rawprog_xml)
            rawprog_path = f.name

        try:
            res = self.adapter.flash_rawprogram(rawprog_path)
            self.assertTrue(res)
        finally:
            if os.path.exists(rawprog_path):
                os.remove(rawprog_path)

    def test_apply_patch_xml(self):
        self.adapter.connect("COM3")
        patch_xml = (
            '<?xml version="1.0" ?>\n'
            '<data>\n'
            '  <patch SECTOR_SIZE_IN_BYTES="512" byte_offset="48" filename="DISK" '
            'physical_partition_number="0" size_in_bytes="4" start_sector="0" value="0"/>\n'
            '</data>'
        )
        with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False) as f:
            f.write(patch_xml)
            patch_path = f.name

        try:
            res = self.adapter.apply_patch(patch_path)
            self.assertTrue(res)
        finally:
            if os.path.exists(patch_path):
                os.remove(patch_path)


if __name__ == "__main__":
    unittest.main()
