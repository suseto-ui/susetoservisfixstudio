import asyncio
import logging
from enum import Enum
from typing import Dict, Any, Optional
import time

class MachineState(Enum):
    IDLE = "IDLE"
    DETECTED = "DETECTED"
    PROFILING = "PROFILING"
    HANDSHAKE = "HANDSHAKE"
    ROUTING = "ROUTING"
    EXECUTING = "EXECUTING"
    FINALIZING = "FINALIZING"

class StateMachineOrchestrator:
    """
    Production-ready deterministic state machine for service routine execution.
    """
    def __init__(self, ledger_db: Any):
        self.state = MachineState.IDLE
        self.ledger = ledger_db
        self.logger = logging.getLogger("StateMachineOrchestrator")

    async def transition_to(self, new_state: MachineState, context: Dict[str, Any] = None) -> None:
        """
        Transitions to a new state and logs the event to the non-blocking ledger.
        """
        old_state = self.state
        self.state = new_state
        ctx = context or {}
        
        self.logger.info(f"Transition: {old_state.value} -> {new_state.value}")
        
        try:
            # Integration with SQLiteWALLedger
            await self.ledger.log_event(
                table="automation_logs",
                data={
                    "timestamp": time.time(),
                    "from_state": old_state.value,
                    "to_state": new_state.value,
                    "context": str(ctx)
                }
            )
        except Exception as e:
            self.logger.error(f"Failed to log state transition: {e}")
