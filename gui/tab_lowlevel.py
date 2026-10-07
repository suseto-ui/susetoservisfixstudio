import customtkinter as ctk

class LowLevelTab(ctk.CTkFrame):
    """
    Low level emergency diagnostic options.
    Exposes switches for EDL mode (9008) and BROM bootloader bypass options.
    """
    def __init__(self, master: any, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="Low-Level Emergency Diagnostic (EDL 9008 / BROM)", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_edl = ctk.CTkButton(self.btn_frame, text="Trigger EDL 9008 Mode", command=self.trigger_edl)
        self.btn_edl.pack(side="left", padx=10, pady=10)

        self.btn_brom = ctk.CTkButton(self.btn_frame, text="Bypass MTK BROM Security", command=self.bypass_brom)
        self.btn_brom.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- EDL / BROM Diagnostics Console ---\n")

    def trigger_edl(self) -> None:
        self.terminal_out.insert("end", "\n[EDL] Sending Sahara sync protocol packet...\n")

    def bypass_brom(self) -> None:
        self.terminal_out.insert("end", "\n[BROM] Injecting MTK custom DA payload bypass...\n")
