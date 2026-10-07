import customtkinter as ctk
from ui.service_operations_component import ServiceOpsPanel

class MasterCockpitWindow(ctk.CTk):
    """
    Unified application interface (Master Cockpit) using Split View layout.
    """
    def __init__(self):
        super().__init__()
        self.title("EUDCP Master Cockpit")
        self.geometry("1024x768")
        
        # Split View layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Sidebar for navigation
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Content area
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=1, sticky="nsew")
        
        # Placeholder for service ops
        self.service_panel = ServiceOpsPanel(self.content)
        self.service_panel.pack(fill="both", expand=True)
