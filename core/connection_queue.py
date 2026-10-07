import asyncio
import logging
from typing import List, Dict, Any, Callable, Optional, Awaitable

class ConnectionQueue:
    """
    Asynchronous connection queue with strict 5-second fallback timeout.
    """
    def __init__(self, profiles: List[Dict[str, Any]]):
        self.profiles = profiles
        self.logger = logging.getLogger("ConnectionQueue")
        self.timeout = 5.0
        self._pause_event = asyncio.Event()
        self._pause_event.set() # Running by default
        self._skip_event = asyncio.Event()

    async def run(self, handshake_callback: Callable[[Dict[str, Any]], Awaitable[bool]]) -> Optional[Dict[str, Any]]:
        """
        Sequentially tests profiles until handshake succeeds or all profiles exhausted.
        """
        for profile in self.profiles:
            await self._pause_event.wait()
            self.logger.info(f"Testing profile: {profile.get('name', 'Unknown')}")
            
            try:
                # 5-second fallback timer
                handshake_task = asyncio.create_task(handshake_callback(profile))
                
                # Wait for task or timeout
                done, pending = await asyncio.wait(
                    [handshake_task], 
                    timeout=self.timeout
                )
                
                if handshake_task in done:
                    success = await handshake_task
                    if success:
                        self.logger.info("Handshake successful")
                        return profile
                else:
                    self.logger.warning(f"Timeout for profile {profile.get('name', 'Unknown')}")
                    handshake_task.cancel()
                    
            except Exception as e:
                self.logger.error(f"Error testing profile: {e}")
        
        return None

    def pause(self) -> None:
        self._pause_event.clear()

    def resume(self) -> None:
        self._pause_event.set()

    def skip(self) -> None:
        self._skip_event.set()
