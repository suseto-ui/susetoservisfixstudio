from typing import Dict, Any

class NANDHealthMonitor:
    """
    Simulates eMMC and UFS memory health extraction.
    Parses ExtCSD registers to assess remaining physical lifetime.
    """
    @staticmethod
    def query_ext_csd() -> Dict[str, Any]:
        """Returns dummy health metrics block."""
        return {
            "type": "eMMC 5.1",
            "slc_est_lifetime": "0x01 (0% - 10% used)",
            "mlc_est_lifetime": "0x02 (10% - 20% used)",
            "life_time_est_a": "100%",
            "life_time_est_b": "90%",
            "pre_eol_info": "0x01 (Normal)"
        }
