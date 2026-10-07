import asyncio
import logging
from typing import Dict, Any

class FastbootEngine:
    """
    Handles advanced bootloader control using asynchronous subprocess calls.
    """
    def __init__(self):
        self.logger = logging.getLogger("FastbootEngine")

    async def _run_command(self, cmd: str) -> str:
        process = await asyncio.create_subprocess_exec(
            "fastboot", *cmd.split(),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            self.logger.error(f"Fastboot error: {stderr.decode()}")
            raise Exception(f"Fastboot failed: {stderr.decode()}")
        return stdout.decode()

    async def switch_slot(self, slot: str) -> None:
        await self._run_command(f"--set-active={slot}")

    async def get_bootloader_vars(self) -> Dict[str, str]:
        output = await self._run_command("getvar all")
        # Parse output for variables
        return {line.split(":")[0]: line.split(":")[1] for line in output.splitlines() if ":" in line}

    async def safe_reboot(self) -> None:
        await self._run_command("reboot")
