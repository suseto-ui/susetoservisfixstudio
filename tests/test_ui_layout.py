import pytest
import tkinter as tk
from ui.master_dashboard import MasterDashboard
from ui.components.device_banner import DeviceBanner

def test_ui_components():
    root = tk.Tk()
    root.withdraw()
    
    banner = DeviceBanner(root)
    banner.set_status("NORMAL")
    assert "NORMAL" in banner.label.cget("text")
    
    dashboard = MasterDashboard()
    assert dashboard.title() == "EUDCP Master Dashboard"
    
    dashboard.destroy()
    root.destroy()
