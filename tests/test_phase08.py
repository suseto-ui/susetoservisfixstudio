import pytest
from unittest.mock import AsyncMock, patch
from core.fastboot_engine import FastbootEngine
from core.unbrick_engine import UnbrickOrchestrator

@pytest.mark.asyncio
async def test_fastboot_slot_switching():
    engine = FastbootEngine()
    with patch.object(engine, '_run_command', new_callable=AsyncMock) as mock_run:
        await engine.switch_slot("a")
        mock_run.assert_called_with("--set-active=a")

@pytest.mark.asyncio
async def test_unbrick_mandatory_backup():
    val = AsyncMock()
    orchestrator = UnbrickOrchestrator(val)
    
    # Mock backup to return False
    with patch.object(orchestrator, '_perform_backup', return_value=False):
        result = await orchestrator.wipe_frp(None)
        assert result is False
