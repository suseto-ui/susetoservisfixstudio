import customtkinter as ctk
from ui.components.sidebar import Sidebar
from ui.components.device_banner import DeviceBanner

class MasterDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EUDCP Master Dashboard")
        self.geometry("1200x800")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.banner = DeviceBanner(self)
        self.banner.grid(row=0, column=0, columnspan=2, sticky="ew")
        
        self.sidebar = Sidebar(self, switch_callback=self.switch_frame)
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
    def switch_frame(self, name):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        # Placeholder for dynamic content
        ctk.CTkLabel(self.main_frame, text=f"Active View: {name}").pack()
