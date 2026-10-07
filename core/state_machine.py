"""
State Machine Engine (`core/state_machine.py`)
Provides deterministic State Machine (FSM) for Universal Hardware Diagnostic Engine.
States: DISCONNECTED, DETECTING, PORT_TUNING, OEM_HANDSHAKE, STREAMING_IO, RECOVERY_VERIFY, IDLE_READY, FAULT_INTERCEPT
"""

from __future__ import annotations

import enum
import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("state_machine")


class EngineState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    DETECTING = "DETECTING"
    PORT_TUNING = "PORT_TUNING"
    OEM_HANDSHAKE = "OEM_HANDSHAKE"
    STREAMING_IO = "STREAMING_IO"
    RECOVERY_VERIFY = "RECOVERY_VERIFY"
    IDLE_READY = "IDLE_READY"
    FAULT_INTERCEPT = "FAULT_INTERCEPT"
    ERROR = "ERROR"


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class DiagnosticStateMachine:
    """
    Deterministic FSM governing the hardware diagnostic lifecycle.
    Enforces valid transitions and triggers registered entry/exit callbacks.
    """

    ALLOWED_TRANSITIONS: Dict[EngineState, List[EngineState]] = {
        EngineState.DISCONNECTED: [EngineState.DETECTING, EngineState.ERROR],
        EngineState.DETECTING: [EngineState.PORT_TUNING, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.PORT_TUNING: [EngineState.OEM_HANDSHAKE, EngineState.FAULT_INTERCEPT, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.OEM_HANDSHAKE: [EngineState.STREAMING_IO, EngineState.RECOVERY_VERIFY, EngineState.IDLE_READY, EngineState.FAULT_INTERCEPT, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.STREAMING_IO: [EngineState.RECOVERY_VERIFY, EngineState.IDLE_READY, EngineState.FAULT_INTERCEPT, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.RECOVERY_VERIFY: [EngineState.IDLE_READY, EngineState.FAULT_INTERCEPT, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.IDLE_READY: [EngineState.DETECTING, EngineState.PORT_TUNING, EngineState.OEM_HANDSHAKE, EngineState.STREAMING_IO, EngineState.RECOVERY_VERIFY, EngineState.FAULT_INTERCEPT, EngineState.DISCONNECTED],
        EngineState.FAULT_INTERCEPT: [EngineState.PORT_TUNING, EngineState.OEM_HANDSHAKE, EngineState.IDLE_READY, EngineState.DISCONNECTED, EngineState.ERROR],
        EngineState.ERROR: [EngineState.DISCONNECTED, EngineState.DETECTING, EngineState.IDLE_READY],
    }

    def __init__(self, initial_state: EngineState = EngineState.DISCONNECTED) -> None:
        self._current_state = initial_state
        self._history: List[Dict[str, Any]] = [
            {"state": initial_state.value, "timestamp": time.time(), "reason": "INIT"}
        ]
        self._listeners: List[Callable[[EngineState, EngineState, str], None]] = []

    @property
    def current_state(self) -> EngineState:
        return self._current_state

    def add_listener(self, callback: Callable[[EngineState, EngineState, str], None]) -> None:
        self._listeners.append(callback)

    def transition_to(self, new_state: EngineState, reason: str = "") -> EngineState:
        """Attempt transition to new state with validation."""
        valid_targets = self.ALLOWED_TRANSITIONS.get(self._current_state, [])
        if new_state not in valid_targets and new_state != EngineState.ERROR:
            err = f"Neplatný přechod stavu: {self._current_state.value} -> {new_state.value}"
            logger.error(err)
            raise StateTransitionError(err)

        prev_state = self._current_state
        self._current_state = new_state
        self._history.append({
            "from": prev_state.value,
            "to": new_state.value,
            "timestamp": time.time(),
            "reason": reason
        })
        logger.info("[FSM] Přechod stavu: %s -> %s (Důvod: %s)", prev_state.value, new_state.value, reason or "N/A")

        for listener in self._listeners:
            try:
                listener(prev_state, new_state, reason)
            except Exception as ex:
                logger.warning("[FSM] Chyba v listeneru: %s", ex)

        return self._current_state

    def get_history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def reset(self) -> None:
        self.transition_to(EngineState.DISCONNECTED, reason="RESET")
