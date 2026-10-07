import customtkinter as ctk
from core.adb_fastboot import ADBFastbootBridge
from core.ai_engine import AIDiagnosticEngine

from gui.tab_adb import ADBTab
from gui.tab_fastboot import FastbootTab
from gui.tab_lowlevel import LowLevelTab
from gui.tab_firmware import FirmwareTab
from gui.tab_testpoint import TestPointTab
from gui.tab_ai_report import AIReporterTab

class MainWindow(ctk.CTk):
    """
    Main Navigation Window implementing the 6-tab navigation rail layout 
    for SusetoDroidFixStudio / AndroidServiceStudio.
    """
    def __init__(self) -> None:
        super().__init__()

        self.title("SusetoDroidFixStudio v1.0-PROD (AndroidServiceStudio)")
        self.geometry("1100x750")

        # Initialize core components
        self.bridge = ADBFastbootBridge()
        self.ai_engine = AIDiagnosticEngine()

        # Split screen into left side Navigation panel and right side Content Frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Left Nav Rail Panel
        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")

        self.lbl_brand = ctk.CTkLabel(self.nav_frame, text="DroidFix Studio", font=("Helvetica", 16, "bold"), text_color="cyan")
        self.lbl_brand.pack(padx=20, pady=20)

        # Tab Views Mapping Dictionary
        self.tabs: dict[str, ctk.CTkFrame] = {}
        
        # Instantiate right side dynamic tabs (all 6 tabs)
        self.tabs["adb"] = ADBTab(self, self.bridge, self.ai_engine)
        self.tabs["fastboot"] = FastbootTab(self, self.bridge)
        self.tabs["lowlevel"] = LowLevelTab(self)
        self.tabs["firmware"] = FirmwareTab(self)
        self.tabs["testpoint"] = TestPointTab(self)
        self.tabs["ai_report"] = AIReporterTab(self, self.ai_engine)

        # Add Nav Rail Selection Buttons
        ctk.CTkButton(self.nav_frame, text="1. ADB Commands", command=lambda: self.select_tab("adb")).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.nav_frame, text="2. Fastboot Protocol", command=lambda: self.select_tab("fastboot")).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.nav_frame, text="3. Low-Level (EDL/BROM)", command=lambda: self.select_tab("lowlevel")).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.nav_frame, text="4. Firmware Engine", command=lambda: self.select_tab("firmware")).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.nav_frame, text="5. TestPoint Viewer", command=lambda: self.select_tab("testpoint")).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.nav_frame, text="6. AI & Report", command=lambda: self.select_tab("ai_report")).pack(fill="x", padx=10, pady=5)

        # Default Active Tab selection
        self.select_tab("adb")

    def select_tab(self, tab_key: str) -> None:
        """
        Grids the selected tab onto row=0, column=1 on-the-fly and un-grids active peers.
        """
        for k, view in self.tabs.items():
            if k == tab_key:
                view.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
            else:
                view.grid_forget()
