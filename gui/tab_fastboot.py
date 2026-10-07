import customtkinter as ctk

class FastbootTab(ctk.CTkFrame):
    """
    GUI panel layout for flashing raw fastboot variables,
    unlocking secure structures, and loading flashing packages.
    """
    def __init__(self, master: any, bridge: any, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.bridge = bridge

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="Fastboot Protocol Operations", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.ctrl_frame = ctk.CTkFrame(self)
        self.ctrl_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_scan = ctk.CTkButton(self.ctrl_frame, text="Scan Fastboot Devices", command=self.scan_fastboot)
        self.btn_scan.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- Fastboot Operation Console ---\n")

    def scan_fastboot(self) -> None:
        out = self.bridge.get_fastboot_devices()
        self.terminal_out.delete("1.0", "end")
        self.terminal_out.insert("1.0", out)
