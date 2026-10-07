import customtkinter as ctk
from core.firmware_engine import FirmwareEngine

class FirmwareTab(ctk.CTkFrame):
    """
    Firmware Engine Tab: Unpacks OTA payloads, analyzes boot.img, and patches vbmeta.
    """
    def __init__(self, master: any, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="Firmware Engine (OTA Unpacker & AVB Patcher)", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.ctrl_frame = ctk.CTkFrame(self)
        self.ctrl_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_analyze = ctk.CTkButton(self.ctrl_frame, text="Analyzovat boot.img", command=self.analyze_boot)
        self.btn_analyze.pack(side="left", padx=10, pady=10)

        self.btn_patch = ctk.CTkButton(self.ctrl_frame, text="Patch vbmeta (Disable AVB)", command=self.patch_avb, fg_color="green")
        self.btn_patch.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- Firmware Engine Console ---\nZde můžete provádět analýzu obrazů a úpravy AVB příznaků.\n")

    def analyze_boot(self) -> None:
        self.terminal_out.insert("end", "\n[Firmware] Kontroluji integritu boot.img hlavičky...\n")
        res = FirmwareEngine.analyze_boot_image("dummy_boot.img")
        for k, v in res.items():
            self.terminal_out.insert("end", f"  {k}: {v}\n")

    def patch_avb(self) -> None:
        self.terminal_out.insert("end", "\n[AVB] Aplikuji příznaky --disable-verity a --disable-verification...\n")
        success = FirmwareEngine.patch_vbmeta("dummy_vbmeta.img")
        if success:
            self.terminal_out.insert("end", "[AVB] Úspěšně patchnuto! Bootloop ochrana odstraněna.\n")
        else:
            self.terminal_out.insert("end", "[AVB] Chyba při zápisu patchovaných příznaků.\n")
