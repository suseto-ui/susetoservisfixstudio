import customtkinter as ctk

class ADBTab(ctk.CTkFrame):
    """
    GUI Frame layout for managing device connections, command outputs,
    and triggering automated Gemini log diagnostic assistance.
    """
    def __init__(self, master: any, bridge: any, ai_engine: any, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.bridge = bridge
        self.ai = ai_engine

        # Configure Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.lbl_title = ctk.CTkLabel(self, text="Android Debug Bridge (ADB) Operations", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Command Panel
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_get_devices = ctk.CTkButton(self.btn_frame, text="Scan ADB Devices", command=self.scan_devices)
        self.btn_get_devices.pack(side="left", padx=10, pady=10)

        self.btn_reboot_bl = ctk.CTkButton(self.btn_frame, text="Reboot Bootloader", command=self.reboot_bl, fg_color="amber" if hasattr(ctk, "amber") else None)
        self.btn_reboot_bl.pack(side="left", padx=10, pady=10)

        self.btn_ai_analyze = ctk.CTkButton(self.btn_frame, text="AI Log Analysis", command=self.analyze_current_log, fg_color="purple" if hasattr(ctk, "purple") else None)
        self.btn_ai_analyze.pack(side="left", padx=10, pady=10)

        # Output Terminal Screen
        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- ADB Output Console ---\nReady for operation...\n")

    def scan_devices(self) -> None:
        out = self.bridge.get_adb_devices()
        self.terminal_out.delete("1.0", "end")
        self.terminal_out.insert("1.0", out)

    def reboot_bl(self) -> None:
        out = self.bridge.reboot_bootloader()
        self.terminal_out.insert("end", f"\nRebooting command: {out}\n")

    def analyze_current_log(self) -> None:
        log_content = self.terminal_out.get("1.0", "end")
        analysis = self.ai.analyze_log(log_content)
        self.terminal_out.insert("end", f"\n\n--- AI ASSISTED DIAGNOSIS ---\n{analysis}\n")
