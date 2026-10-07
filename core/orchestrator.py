"""
Universal Core Orchestrator (`core/orchestrator.py`).
Master orchestrator unifying the State Machine (FSM), Hardware Event Bus,
Port & Tuning Engine, VAL Chipset Abstraction, Memory Stream Pipeline,
Memory Recovery Agent, Fault Injection Studio, and System Health Watchdog.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, List, Optional

from core.e2e_diagnostic_suite import E2EDiagnosticSuite
from core.event_bus import HardwareEventBus
from core.fault_injection_engine import FaultInjectionEngine
from core.memory_pipeline import MemoryStreamPipeline
from core.memory_recovery_agent import MemoryRecoveryAgent
from core.port_tuning_engine import PortTuningEngine
from core.state_machine import DiagnosticStateMachine, EngineState
from core.system_watchdog import SystemHealthWatchdog
from core.telemetry_rtt import TelemetryRttMonitor
from val.chipset_val import UnifiedVendorAbstractionLayer

logger = logging.getLogger("orchestrator")


class UniversalCoreOrchestrator:
    """
    Central Coordinator for the entire Universal Hardware Diagnostic Engine.
    """

    _instance: Optional[UniversalCoreOrchestrator] = None

    @classmethod
    def get_instance(cls) -> UniversalCoreOrchestrator:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self.fsm = DiagnosticStateMachine()
        self.bus = HardwareEventBus.get_instance()
        self.tuning = PortTuningEngine()
        self.val = UnifiedVendorAbstractionLayer()
        self.memory = MemoryStreamPipeline()
        self.recovery = MemoryRecoveryAgent()
        self.faults = FaultInjectionEngine()
        self.telemetry = TelemetryRttMonitor()
        self.watchdog = SystemHealthWatchdog()
        self.e2e = E2EDiagnosticSuite()

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Aggregate high-level health and status from all subsystems."""
        return {
            "engine_state": self.fsm.current_state.value,
            "watchdog": self.watchdog.get_system_health(),
            "telemetry": self.telemetry.get_metrics_snapshot(),
            "active_profiles": len(self.val.list_profiles()),
            "fsm_history_count": len(self.fsm.get_history())
        }
