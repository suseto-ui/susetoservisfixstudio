import customtkinter as ctk
from typing import Any, Dict
from PIL import Image, ImageTk
import io

class TestpointVisualizer(ctk.CTkFrame):
    """
    Visualizer component for testpoint locations.
    Supports photos, schematics, and text instructions.
    """
    def __init__(self, master: Any, **kwargs):
        super().__init__(master, **kwargs)
        
        # Display Area
        self.lbl_image = ctk.CTkLabel(self, text="Waiting for device detection...")
        self.lbl_image.pack(pady=10)
        
        self.txt_instructions = ctk.CTkTextbox(self, height=100)
        self.txt_instructions.pack(pady=10, fill="x")

    def display_testpoint(self, info: Dict[str, Any]) -> None:
        """
        Updates the UI with testpoint info (image, layout, instructions).
        """
        self.txt_instructions.delete("1.0", "end")
        self.txt_instructions.insert("1.0", info.get("instructions", "No instructions available."))
        
        # Logic for loading photo or schematic image
        # Assuming path to local image assets is provided in info
        image_path = info.get("image_path")
        if image_path:
            img = Image.open(image_path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(300, 200))
            self.lbl_image.configure(image=ctk_img, text="")
