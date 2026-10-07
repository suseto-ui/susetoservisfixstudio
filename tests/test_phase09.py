import pytest
import asyncio
from core.event_router import EventRouter
from ui.master_cockpit_window import MasterCockpitWindow

@pytest.mark.asyncio
async def test_event_router():
    router = EventRouter()
    received_data = []

    def callback(data):
        received_data.append(data)

    router.subscribe("test_event", callback)
    await router.publish("test_event", "hello")
    
    assert received_data == ["hello"]

def test_master_cockpit_init():
    # Run in headless mode for testing
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()
    
    window = MasterCockpitWindow()
    assert window.title() == "EUDCP Master Cockpit"
    window.destroy()
    root.destroy()
