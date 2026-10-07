import customtkinter as ctk
from typing import Any

class HexViewer(ctk.CTkFrame):
    """
    Component for visually inspecting memory streams and hex data.
    """
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        self.txt_hex = ctk.CTkTextbox(self, font=("Courier", 12))
        self.txt_hex.pack(fill="both", expand=True)
        
        self.btn_search = ctk.CTkButton(self, text="Search String", command=self._search_string)
        self.btn_search.pack(pady=5)
        
    def load_data(self, data: bytes) -> None:
        """
        Loads binary data into hex representation.
        """
        hex_data = " ".join([f"{b:02X}" for b in data])
        self.txt_hex.delete("1.0", "end")
        self.txt_hex.insert("1.0", hex_data)
        
    def _search_string(self) -> None:
        # Implementation for string search
        pass
