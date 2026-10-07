import customtkinter as ctk

class DeviceBanner(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.label = ctk.CTkLabel(self, text="Status: DISCONNECTED", font=("Arial", 14))
        self.label.pack(pady=5, padx=10)
        self.set_status("OFFLINE")
        
    def set_status(self, status: str):
        colors = {
            "NORMAL": "#2ecc71", # Green
            "FASTBOOT": "#f1c40f", # Yellow
            "EDL": "#e74c3c", # Red
            "OFFLINE": "#95a5a6" # Gray
        }
        color = colors.get(status, "#95a5a6")
        self.label.configure(text=f"Status: {status}", fg_color=color)
