"""
Telemetry Dashboard UI Component Helper for Port Tuner and SQLite WAL Ledger.
"""

from __future__ import annotations

from typing import Dict, Any, List


class TelemetryDashboardComponent:
    """
    Aggregates metrics for RTT latency, fault injection frame drops, and active baud rates.
    """

    def __init__(self):
        self.rtt_history: List[float] = []
        self.frame_drops = 0
        self.active_baudrate = 115200
        self.negotiation_logs: List[str] = []

    def record_rtt(self, rtt_ms: float) -> None:
        """Record RTT measurement for sparkline rendering."""
        self.rtt_history.append(rtt_ms)
        if len(self.rtt_history) > 20:
            self.rtt_history.pop(0)

    def record_frame_drop(self) -> None:
        """Increment frame drop counter."""
        self.frame_drops += 1

    def set_baudrate(self, rate: int, log_msg: str) -> None:
        """Update active baud rate and append log."""
        self.active_baudrate = rate
        self.negotiation_logs.append(log_msg)

    def render_dashboard_metrics(self) -> Dict[str, Any]:
        """Return formatted metrics payload for UI rendering."""
        avg_rtt = sum(self.rtt_history) / len(self.rtt_history) if self.rtt_history else 0.0
        sparkline = "".join([" " if r < 10 else "▂" if r < 25 else "▆" if r < 50 else "█" for r in self.rtt_history])
        
        return {
            "active_baudrate": self.active_baudrate,
            "avg_rtt_ms": round(avg_rtt, 2),
            "sparkline": sparkline,
            "frame_drops": self.frame_drops,
            "recent_logs": self.negotiation_logs[-5:],
        }
