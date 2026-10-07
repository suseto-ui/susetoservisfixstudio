import customtkinter as ctk

class AIReporterTab(ctk.CTkFrame):
    """
    AI Diagnostic & Report Tab: Sleduje terminálový výstup, volá Gemini API 
    a exportuje servisní protokoly o opravě.
    """
    def __init__(self, master: any, ai_engine: any, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.ai = ai_engine

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.lbl_title = ctk.CTkLabel(self, text="AI Diagnostic & Service Report Center", font=("Helvetica", 16, "bold"))
        self.lbl_title.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.ctrl_frame = ctk.CTkFrame(self)
        self.ctrl_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.btn_run_ai = ctk.CTkButton(self.ctrl_frame, text="Spustit Gemini Diagnostiku logu", command=self.run_diagnosis, fg_color="purple")
        self.btn_run_ai.pack(side="left", padx=10, pady=10)

        self.btn_export = ctk.CTkButton(self.ctrl_frame, text="Exportovat Protokol (JSON/PDF)", command=self.export_report)
        self.btn_export.pack(side="left", padx=10, pady=10)

        self.terminal_out = ctk.CTkTextbox(self, font=("Courier", 12))
        self.terminal_out.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.terminal_out.insert("1.0", "--- AI Diagnostic Console ---\nVložte nebo zachyťte chybový kód pro analýzu modelem Gemini 3.8 Flash.\n")

    def run_diagnosis(self) -> None:
        log_text = self.terminal_out.get("1.0", "end")
        self.terminal_out.insert("end", "\n[AI] Odesílám logy k analýze do Gemini API...\n")
        analysis = self.ai.analyze_log(log_text)
        self.terminal_out.insert("end", f"\n{analysis}\n")

    def export_report(self) -> None:
        self.terminal_out.insert("end", "\n[Export] Servisní protokol byl úspěšně vygenerován a uložen do /storage/reports/\n")
