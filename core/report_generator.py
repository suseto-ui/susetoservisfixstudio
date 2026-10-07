import os
import json
from datetime import datetime

class ReportGenerator:
    """
    Generates professional service diagnostic reports and certificates 
    in JSON or simulated PDF format for customers and internal audit.
    """
    @staticmethod
    def generate_json_report(device_info: dict, repair_actions: list, ai_diagnosis: str) -> str:
        report_dir = "storage/reports"
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        serial = device_info.get("serial", "UNKNOWN_DEVICE")
        filename = os.path.join(report_dir, f"report_{serial}_{timestamp}.json")

        report_data = {
            "application": "SusetoDroidFixStudio v1.0-PROD",
            "timestamp": datetime.now().isoformat(),
            "device_info": device_info,
            "repair_actions": repair_actions,
            "ai_diagnosis": ai_diagnosis,
            "status": "SUCCESS"
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=4, ensure_ascii=False)

        return filename
