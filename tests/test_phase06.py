import pytest
from core.testpoint_database import TestpointDatabaseManager
import json
import os

# Create dummy DB for testing
@pytest.fixture
def mock_db(tmp_path):
    db_file = tmp_path / "testpoints.json"
    data = {
        "devices": {
            "RedmiNote9": {
                "instructions": "Connect GND to TP1",
                "image_path": None
            }
        }
    }
    with open(db_file, 'w') as f:
        json.dump(data, f)
    return str(db_file)

def test_testpoint_retrieval(mock_db):
    manager = TestpointDatabaseManager(db_path=mock_db)
    info = manager.get_testpoint_info("RedmiNote9")
    
    assert info is not None
    assert info["instructions"] == "Connect GND to TP1"

def test_missing_device(mock_db):
    manager = TestpointDatabaseManager(db_path=mock_db)
    info = manager.get_testpoint_info("UnknownDevice")
    
    assert info is None
