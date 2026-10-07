import customtkinter as ctk
from typing import Any

class AutomationCockpit(ctk.CTkFrame):
    """
    Operator control panel for automation sequence.
    """
    def __init__(self, master: Any, queue_controller: Any, **kwargs):
        super().__init__(master, **kwargs)
        self.queue = queue_controller
        self.paused = False
        
        # Pause/Resume Control
        self.btn_pause = ctk.CTkButton(self, text="Pause Automation", command=self._toggle_pause)
        self.btn_pause.pack(pady=5, padx=10, fill="x")
        
        # Manual Confirmation
        self.btn_confirm = ctk.CTkButton(self, text="Confirm Profile", command=self._confirm_profile)
        self.btn_confirm.pack(pady=5, padx=10, fill="x")
        
        # Skip Fallback
        self.btn_skip = ctk.CTkButton(self, text="Skip to Next", command=self._skip_profile)
        self.btn_skip.pack(pady=5, padx=10, fill="x")

    def _toggle_pause(self) -> None:
        if self.paused:
            self.queue.resume()
            self.btn_pause.configure(text="Pause Automation")
        else:
            self.queue.pause()
            self.btn_pause.configure(text="Resume Automation")
        self.paused = not self.paused

    def _confirm_profile(self) -> None:
        # Implementation for manual override
        pass

    def _skip_profile(self) -> None:
        self.queue.skip()
