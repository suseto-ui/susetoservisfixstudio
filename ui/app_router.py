"""
Application Router & Main Window (`ui/app_router.py`).
Master application window with dynamic view switching between KioskView (locked down)
and AdminView (expert diagnostic), guarded by global hotkey (Ctrl+Shift+A) and cryptographic
password authentication.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("ui.app_router")

try:
    import customtkinter as ctk  # type: ignore[import-untyped]
except ImportError:
    from ui._ctk_compat import ctk  # type: ignore[no-redef]

from core.one_click_automation import OneClickAutomation
from storage.wal_ledger import SQLiteWALLedger
from ui.admin_view import AdminAuthManager, AdminView
from ui.kiosk_view import KioskView


class PasswordPromptDialog(ctk.CTkToplevel):
    """
    Modal security prompt dialog verifying admin authentication before granting cockpit access.
    """

    def __init__(
        self,
        master: Any,
        auth_manager: AdminAuthManager,
        on_success: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)
        self.auth_manager = auth_manager
        self.on_success = on_success

        self.title("Ověření administrátora - Přístup L3")
        self.geometry("420x260")
        self.transient(master)

        # Container
        frame = ctk.CTkFrame(self, fg_color="#1e222a", corner_radius=12)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.grid_columnconfigure(0, weight=1)

        lbl_icon = ctk.CTkLabel(
            frame,
            text="🔐",
            font=("Arial", 32),
        )
        lbl_icon.pack(pady=(15, 5))

        lbl_title = ctk.CTkLabel(
            frame,
            text="Zadejte heslo administrátora",
            font=("Arial", 16, "bold"),
            text_color="#ffffff",
        )
        lbl_title.pack(pady=2)

        lbl_desc = ctk.CTkLabel(
            frame,
            text="Pro přístup k expertním funkcím zadejte servisní klíč.",
            font=("Arial", 11),
            text_color="#7f8c8d",
        )
        lbl_desc.pack(pady=(0, 10))

        # Password Entry
        self.ent_pw = ctk.CTkEntry(
            frame,
            placeholder_text="Heslo...",
            show="*",
            width=260,
            height=36,
        )
        self.ent_pw.pack(pady=5)
        self.ent_pw.focus_set()
        self.ent_pw.bind("<Return>", lambda e: self._verify_and_submit())

        # Error notification label
        self.lbl_error = ctk.CTkLabel(
            frame,
            text="",
            font=("Arial", 11, "bold"),
            text_color="#e74c3c",
        )
        self.lbl_error.pack(pady=2)

        # Buttons
        btn_box = ctk.CTkFrame(frame, fg_color="transparent")
        btn_box.pack(pady=(5, 10))

        btn_cancel = ctk.CTkButton(
            btn_box,
            text="Zrušit",
            width=100,
            fg_color="#7f8c8d",
            hover_color="#636e72",
            command=self.destroy,
        )
        btn_cancel.pack(side="left", padx=10)

        btn_ok = ctk.CTkButton(
            btn_box,
            text="Odemknout",
            width=120,
            fg_color="#2980b9",
            hover_color="#1f618d",
            command=self._verify_and_submit,
        )
        btn_ok.pack(side="left", padx=10)

        # Bind Escape
        self.bind("<Escape>", lambda e: self.destroy())

    def _verify_and_submit(self) -> None:
        entered_pw = self.ent_pw.get()
        if self.auth_manager.verify_password(entered_pw):
            self.destroy()
            if callable(self.on_success):
                self.on_success()
        else:
            self.lbl_error.configure(text="Neplatné heslo! Přístup odepřen.")
            self.ent_pw.delete(0, "end")


class AppRouter(ctk.CTk):
    """
    Main application window and stateful view router.
    Defaults to locked-down KioskView and switches to AdminView upon hotkey authentication.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.title("SusetoDroidFixStudio - Universal Kiosk & Diagnostic Engine")
        self.geometry("1100x780")

        # Configure dark appearance if supported
        if hasattr(ctk, "set_appearance_mode"):
            ctk.set_appearance_mode("Dark")
        if hasattr(ctk, "set_default_color_theme"):
            ctk.set_default_color_theme("blue")

        # Global shared instances
        self.ledger = SQLiteWALLedger(db_path="system_wal_ledger.db")
        self.automation = OneClickAutomation(ledger=self.ledger)
        self.auth_manager = AdminAuthManager()

        # View state
        self._current_view_name = "kiosk"
        self._active_view_widget: Optional[ctk.CTkFrame] = None

        # Container Frame
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Mount initial default view: KIOSK
        self.switch_to_view("kiosk")

        # Register global hotkey for Admin access: Ctrl+Shift+A
        self._bind_admin_hotkeys()

    def _bind_admin_hotkeys(self) -> None:
        """Bind multiple variations of Ctrl+Shift+A across platforms."""
        hotkey_seqs = [
            "<Control-Shift-A>",
            "<Control-Shift-a>",
            "<Control-Shift-Key-A>",
            "<Control-Shift-Key-a>",
            "<Control-Key-A>",
        ]
        for seq in hotkey_seqs:
            try:
                self.bind(seq, self._on_admin_hotkey_pressed)
            except Exception as exc:
                logger.debug("Binding %s skipped: %s", seq, exc)

    def _on_admin_hotkey_pressed(self, event: Optional[Any] = None) -> None:
        """Invoked when technician presses the hotkey combination."""
        if self._current_view_name == "admin":
            # Already in admin mode
            return
        self.open_password_dialog()

    def open_password_dialog(self) -> None:
        """Display password prompt dialog."""
        PasswordPromptDialog(
            master=self,
            auth_manager=self.auth_manager,
            on_success=lambda: self.switch_to_view("admin"),
        )

    def switch_to_view(self, view_name: str) -> None:
        """Switch active UI frame cleanly without thread locks."""
        # Unmount current view
        if self._active_view_widget is not None:
            self._active_view_widget.grid_forget()
            self._active_view_widget.destroy()
            self._active_view_widget = None

        self._current_view_name = view_name

        if view_name == "admin":
            self._active_view_widget = AdminView(
                master=self.container,
                ledger=self.ledger,
                on_lock_kiosk=lambda: self.switch_to_view("kiosk"),
            )
        else:  # Default to kiosk
            self._active_view_widget = KioskView(
                master=self.container,
                automation_engine=self.automation,
                on_request_admin=self.open_password_dialog,
            )

        self._active_view_widget.grid(row=0, column=0, sticky="nsew")


def run_app() -> None:
    """Entry point for standalone execution."""
    app = AppRouter()
    app.mainloop()


if __name__ == "__main__":
    run_app()
