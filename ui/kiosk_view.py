"""
Kiosk View UI Component (`ui/kiosk_view.py`).
Foolproof One-Button UI: Zero configuration required, massive color-coded status indicator,
and a single prominent START/DETECT button bound asynchronously to the OneClickAutomation pipeline.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger("ui.kiosk_view")

try:
    import customtkinter as ctk  # type: ignore[import-untyped]
except ImportError:
    from ui._ctk_compat import ctk  # type: ignore[no-redef]

from core.one_click_automation import (
    AutomationState,
    AutomationStatus,
    OneClickAutomation,
)


class KioskView(ctk.CTkFrame):
    """
    Locked-down, foolproof Kiosk Interface for frontline workshop technicians.
    One massive button, color-coded live status feedback, zero technical complexity.
    """

    def __init__(
        self,
        master: Any,
        automation_engine: Optional[OneClickAutomation] = None,
        on_request_admin: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self.automation = automation_engine or OneClickAutomation()
        self.on_request_admin = on_request_admin

        # Configure responsive grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Center Card
        self.grid_rowconfigure(2, weight=0)  # Footer

        self._build_header()
        self._build_center_status_card()
        self._build_footer()

        # Connect automation signals safely
        self.automation.add_status_listener(self._on_status_signal_threadsafe)

    def _build_header(self) -> None:
        """Top banner with branding and mode indicator."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            header_frame,
            text="SUSETO DROID FIX STUDIO",
            font=("Arial", 28, "bold"),
            text_color="#ffffff",
        )
        title_label.pack(anchor="center")

        sub_label = ctk.CTkLabel(
            header_frame,
            text="AUTOMATICKÝ SERVISNÍ KIOSK • JEDNOTLAČÍTKOVÁ OBNOVA ZAŘÍZENÍ",
            font=("Arial", 12),
            text_color="#95a5a6",
        )
        sub_label.pack(anchor="center", pady=(2, 0))

    def _build_center_status_card(self) -> None:
        """Center container with massive Status Indicator and START button."""
        self.card = ctk.CTkFrame(
            self,
            fg_color="#23272e",
            corner_radius=18,
            border_width=2,
            border_color="#34495e",
        )
        self.card.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure(0, weight=0)  # Badge
        self.card.grid_rowconfigure(1, weight=0)  # Title
        self.card.grid_rowconfigure(2, weight=0)  # Sub-message
        self.card.grid_rowconfigure(3, weight=0)  # Device badge
        self.card.grid_rowconfigure(4, weight=0)  # Progress Bar
        self.card.grid_rowconfigure(5, weight=1)  # Spacer
        self.card.grid_rowconfigure(6, weight=0)  # Massive Action Button

        # Status Pill / Color Badge
        self.status_pill = ctk.CTkLabel(
            self.card,
            text="● PŘIPRAVENO",
            font=("Arial", 14, "bold"),
            text_color="#7f8c8d",
            fg_color="#2c3e50",
            corner_radius=12,
            padx=16,
            pady=6,
        )
        self.status_pill.grid(row=0, column=0, pady=(35, 15))

        # Massive Primary Status Label
        self.lbl_status_main = ctk.CTkLabel(
            self.card,
            text="PŘIPRAVENO - Připojte zařízení",
            font=("Arial", 26, "bold"),
            text_color="#ecf0f1",
            wraplength=700,
        )
        self.lbl_status_main.grid(row=1, column=0, padx=20, pady=5)

        # Secondary Status Subtitle
        self.lbl_status_sub = ctk.CTkLabel(
            self.card,
            text="Připojte USB kabel se servisovaným zařízením a stiskněte tlačítko START.",
            font=("Arial", 15),
            text_color="#bdc3c7",
            wraplength=650,
        )
        self.lbl_status_sub.grid(row=2, column=0, padx=20, pady=(5, 15))

        # Device Info Strip
        self.lbl_device_strip = ctk.CTkLabel(
            self.card,
            text="Port: ŽÁDNÝ • Chipset: NEZNÁMÝ • Režim: ČEKÁNÍ",
            font=("Arial", 12),
            text_color="#7f8c8d",
            fg_color="#1a1c23",
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.lbl_device_strip.grid(row=3, column=0, pady=10)

        # Real-time Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.card,
            width=500,
            height=14,
            corner_radius=7,
            progress_color="#27ae60",
        )
        self.progress_bar.grid(row=4, column=0, pady=(20, 5))
        self.progress_bar.set(0.0)

        self.lbl_progress_percent = ctk.CTkLabel(
            self.card,
            text="0 %",
            font=("Arial", 12, "bold"),
            text_color="#7f8c8d",
        )
        self.lbl_progress_percent.grid(row=5, column=0, pady=(0, 20))

        # -----------------------------------------------------------
        # ONE SINGLE MASSIVE BUTTON: "START / DETECT"
        # -----------------------------------------------------------
        self.btn_start = ctk.CTkButton(
            self.card,
            text="▶  START / DETEKCE",
            font=("Arial", 22, "bold"),
            height=72,
            width=380,
            corner_radius=14,
            fg_color="#2980b9",
            hover_color="#1f618d",
            command=self._on_start_clicked,
        )
        self.btn_start.grid(row=6, column=0, pady=(0, 40))

    def _build_footer(self) -> None:
        """Bottom lock status bar with admin unlock shortcut note."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(5, 15))
        footer_frame.grid_columnconfigure(0, weight=1)

        self.lbl_admin_hint = ctk.CTkLabel(
            footer_frame,
            text="🔒 Kiosk režim uzamčen • Pro expertní diagnostiku stiskněte Ctrl+Shift+A",
            font=("Arial", 12),
            text_color="#7f8c8d",
        )
        self.lbl_admin_hint.pack(side="left", padx=10)

        # Subtle clickable link for touchscreens/assistive access
        btn_admin_touch = ctk.CTkButton(
            footer_frame,
            text="Admin přihlášení",
            font=("Arial", 11, "underline"),
            width=110,
            height=26,
            fg_color="transparent",
            text_color="#7f8c8d",
            hover_color="#2c3e50",
            command=self._trigger_admin_prompt,
        )
        btn_admin_touch.pack(side="right", padx=10)

    def _trigger_admin_prompt(self) -> None:
        if callable(self.on_request_admin):
            self.on_request_admin()

    def _on_start_clicked(self) -> None:
        """Handler for single massive button click."""
        if self.automation.is_running:
            return

        # Disable button during execution to prevent multi-trigger
        self.btn_start.configure(
            state="disabled",
            text="⏳ PROBÍHÁ ZPRACOVÁNÍ...",
            fg_color="#7f8c8d",
        )

        # Trigger background pipeline
        self.automation.run_in_background(
            simulated=False,
            on_complete=self._on_pipeline_completed,
        )

    def _on_pipeline_completed(self, success: bool) -> None:
        """Called when background pipeline finishes (from worker thread)."""
        # Dispatch to main GUI thread via after()
        self.after(0, self._restore_start_button, success)

    def _restore_start_button(self, success: bool) -> None:
        """Restore button state on main thread."""
        btn_color = "#27ae60" if success else "#2980b9"
        self.btn_start.configure(
            state="normal",
            text="▶  START / DETEKCE",
            fg_color=btn_color,
        )

    def _on_status_signal_threadsafe(self, status: AutomationStatus) -> None:
        """Receive status signal from background engine and dispatch to GUI loop."""
        self.after(0, self._apply_status_to_ui, status)

    def _apply_status_to_ui(self, status: AutomationStatus) -> None:
        """Render status update inside CustomTkinter components."""
        # Update Main Text & Subtitle
        self.lbl_status_main.configure(text=status.status_message)
        self.lbl_status_sub.configure(text=status.sub_message)

        # Update Color Badge
        pill_text = f"● {status.state.value}"
        self.status_pill.configure(
            text=pill_text,
            text_color=status.color,
            fg_color="#1a1c23",
        )

        # Update Card border to match active status color
        self.card.configure(border_color=status.color)

        # Update Progress Bar & Label
        progress_norm = status.progress_percent / 100.0
        self.progress_bar.set(progress_norm)
        self.progress_bar.configure(progress_color=status.color)
        self.lbl_progress_percent.configure(
            text=f"{int(status.progress_percent)} %",
            text_color=status.color,
        )

        # Update Device Strip
        if status.device_info:
            dev = status.device_info
            port = dev.get("port", "COM3")
            chipset = dev.get("chipset", "Neznámý")
            mode = dev.get("mode", "Online")
            self.lbl_device_strip.configure(
                text=f"Port: {port} • Chipset: {chipset} • Režim: {mode}",
                text_color="#ecf0f1",
            )
        else:
            self.lbl_device_strip.configure(
                text="Port: ŽÁDNÝ • Chipset: NEZNÁMÝ • Režim: ČEKÁNÍ",
                text_color="#7f8c8d",
            )
