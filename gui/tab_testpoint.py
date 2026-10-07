import customtkinter as ctk

class TestPointTab(ctk.CTkFrame):
    """
    Renders reference diagrams, images, and schematic pin locations for forcing EDL/BROM.
    """
    def __init__(self, master: any, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="Hardware TestPoints Pinout Database", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_load_xiaomi = ctk.CTkButton(self.btn_frame, text="Load Xiaomi EDL Pinouts", command=lambda: self.load_pinout("Xiaomi"))
        self.btn_load_xiaomi.pack(side="left", padx=10, pady=10)

        self.btn_load_samsung = ctk.CTkButton(self.btn_frame, text="Load Samsung Testpoint Maps", command=lambda: self.load_pinout("Samsung"))
        self.btn_load_samsung.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- Testpoint Schematic Locator ---\n")

    def load_pinout(self, vendor: str) -> None:
        self.terminal_out.delete("1.0", "end")
        self.terminal_out.insert("1.0", f"--- {vendor} Emergency Hardware TestPoint Map ---\n")
        if vendor == "Xiaomi":
            self.terminal_out.insert("end", "1. Locate EDL points near the battery interface connector block.\n2. Short both pins using conductive metal tweezers.\n3. Plug in the USB cable to establish Qualcomm HS-USB QDLoader 9008 mode connection.\n")
        else:
            self.terminal_out.insert("end", "1. Locate the dynamic clock pins (CLK) on the logic board board assembly.\n2. Short pin CLK to GND chassis shielding.\n3. Power on to initiate MediaTek Preloader BROM override sequence.\n")
