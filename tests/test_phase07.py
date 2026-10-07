import pytest
import struct
import io
from core.partition_manager import GPTManager
from core.memory_recovery_agent import StreamingDumpEngine

def test_gpt_header_parsing(tmp_path):
    # Create dummy binary with EFI PART header
    dummy_bin = tmp_path / "test.bin"
    with open(dummy_bin, "wb") as f:
        f.write(b"\x00" * 512)
        # Signature + LBA=1234, count=10, size=128
        header = b"EFI PART" + b"\x00" * 64 + struct.pack("<Q", 1234) + struct.pack("<I", 10) + struct.pack("<I", 128)
        f.write(header.ljust(512, b"\x00"))
        
    manager = GPTManager(str(dummy_bin))
    partitions = manager.get_partitions()
    assert len(partitions) > 0
    assert partitions[0]["lba"] == 1234

def test_stream_integrity(tmp_path):
    output = tmp_path / "out.bin"
    engine = StreamingDumpEngine(str(output))
    
    chunk = b"\xde\xad\xbe\xef"
    engine.process_chunk(chunk)
    
    assert os.path.exists(output)
    with open(output, "rb") as f:
        assert f.read() == chunk
