import json
import logging
from typing import Dict, Any, Optional, List

class TestpointDatabaseManager:
    """
    Manager for accessing testpoint data from a local JSON repository.
    """
    def __init__(self, db_path: str = "/data/testpoints.json"):
        self.db_path = db_path
        self.logger = logging.getLogger("TestpointDatabase")
        self.data: Dict[str, Any] = {}
        self._load_db()

    def _load_db(self) -> None:
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"Failed to load testpoints database: {e}")
            self.data = {"devices": {}}

    def get_testpoint_info(self, model: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves testpoint info for a specific device model.
        """
        return self.data.get("devices", {}).get(model)
