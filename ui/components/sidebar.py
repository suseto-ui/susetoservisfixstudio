import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, switch_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.switch_callback = switch_callback
        
        self.label = ctk.CTkLabel(self, text="EUDCP Tools", font=("Arial", 16, "bold"))
        self.label.pack(pady=20)
        
        btns = ["Dashboard", "Service Ops", "Memory", "Settings"]
        for b in btns:
            btn = ctk.CTkButton(self, text=b, command=lambda x=b: self.switch_callback(x))
            btn.pack(pady=5, padx=10, fill="x")
