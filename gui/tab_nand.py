import customtkinter as ctk
from core.nand_health import NANDHealthMonitor

class NANDTab(ctk.CTkFrame):
    """
    GUI Panel summarizing physical lifetime assessments for built-in UFS and eMMC memory cards.
    """
    def __init__(self, master: any, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="eMMC / UFS NAND Flash Health Diagnostics", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_read = ctk.CTkButton(self.btn_frame, text="Read ExtCSD / Device Lifespan", command=self.read_lifetime)
        self.btn_read.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- NAND Health Reports ---\n")

    def read_lifetime(self) -> None:
        res = NANDHealthMonitor.query_ext_csd()
        self.terminal_out.delete("1.0", "end")
        self.terminal_out.insert("1.0", "--- ExtCSD Parse Health Report ---\n")
        for k, v in res.items():
            self.terminal_out.insert("end", f"{k.upper():<20}: {v}\n")
