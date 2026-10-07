import asyncio
import logging
from typing import Dict, Any, Callable, List

class EventRouter:
    """
    Asynchronous Pub/Sub bus to decouple low-level tasks from GUI.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger("EventRouter")

    def subscribe(self, event_type: str, callback: Callable[[Any], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    async def publish(self, event_type: str, data: Any):
        self.logger.info(f"Publishing {event_type}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
