"""
Context-Aware Technician Diagnostic & Repair Wizard Widget for SusetoDroidFixStudio.
Interactive PySide6 HUD panel providing dynamic IF / WHAT / WHY guidance
with 1-Click execution triggers, safety badges, and real-time step progression.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ui._qt_compat import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QMessageBox,
    Signal,
    Slot,
    Qt,
)
from core.context_advisor import ContextAdvisorEngine, AdvisorStep, SafetyRating

logger = logging.getLogger("ui.context_guide")


class ContextGuideWidget(QWidget):
    """
    Interactive Side-Panel HUD displaying live IF / WHAT / WHY repair steps
    tailored to the currently connected device.
    """

    step_action_triggered = Signal(str, str)  # (action_id, action_title)
    guidance_completed = Signal(str)         # (diagnosis)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.advisor_engine = ContextAdvisorEngine()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # 1. Header Bar: Title & Status Badge
        header_row = QHBoxLayout()
        self.lbl_title = QLabel("🧭 Kontextový servisní průvodce (IF / WHAT / WHY)")
        self.lbl_title.setStyleSheet("font-weight: bold; color: #00f0ff; font-family: monospace; font-size: 12px;")
        header_row.addWidget(self.lbl_title)

        self.lbl_safety_badge = QLabel("STAV: PŘIPRAVEN")
        self.lbl_safety_badge.setStyleSheet("background-color: #1e293b; color: #94a3b8; font-weight: bold; padding: 3px 8px; border-radius: 4px; font-size: 10px;")
        header_row.addWidget(self.lbl_safety_badge, alignment=Qt.AlignRight)
        layout.addLayout(header_row)

        # 2. Stepper Progress Line
        self.lbl_step_counter = QLabel("Krok 0 z 0: Žádné zařízení")
        self.lbl_step_counter.setStyleSheet("color: #9ca3af; font-family: monospace; font-size: 11px;")
        layout.addWidget(self.lbl_step_counter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        # 3. HUD Cards Container
        self.card_container = QWidget()
        card_layout = QVBoxLayout(self.card_container)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(6)
        self.card_container.setStyleSheet("background-color: #0d111a; border: 1px solid #1f293d; border-radius: 6px;")

        # Card Title
        self.lbl_card_title = QLabel("Čekání na inicializaci zařízení...")
        self.lbl_card_title.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 13px;")
        card_layout.addWidget(self.lbl_card_title)

        # IF Card (Symptom / Condition)
        self.box_if = QWidget()
        box_if_layout = QVBoxLayout(self.box_if)
        box_if_layout.setContentsMargins(6, 6, 6, 6)
        self.box_if.setStyleSheet("background-color: #071927; border-left: 3px solid #00f0ff; border-radius: 4px;")
        lbl_if_tag = QLabel("POKUD (IF):")
        lbl_if_tag.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 10px; font-family: monospace;")
        box_if_layout.addWidget(lbl_if_tag)
        self.lbl_if_text = QLabel("Připojte zařízení přes USB/UART pro zahájení diagnostiky.")
        self.lbl_if_text.setStyleSheet("color: #e2e8f0; font-size: 11px;")
        self.lbl_if_text.setWordWrap(True)
        box_if_layout.addWidget(self.lbl_if_text)
        card_layout.addWidget(self.box_if)

        # WHAT Card (Actionable Step)
        self.box_what = QWidget()
        box_what_layout = QVBoxLayout(self.box_what)
        box_what_layout.setContentsMargins(6, 6, 6, 6)
        self.box_what.setStyleSheet("background-color: #062319; border-left: 3px solid #00ff9d; border-radius: 4px;")
        lbl_what_tag = QLabel("CO UDĚLAT (WHAT):")
        lbl_what_tag.setStyleSheet("color: #00ff9d; font-weight: bold; font-size: 10px; font-family: monospace;")
        box_what_layout.addWidget(lbl_what_tag)
        self.lbl_what_text = QLabel("Stiskněte tlačítko Skenovat porty.")
        self.lbl_what_text.setStyleSheet("color: #e2e8f0; font-size: 11px; font-weight: 500;")
        self.lbl_what_text.setWordWrap(True)
        box_what_layout.addWidget(self.lbl_what_text)
        card_layout.addWidget(self.box_what)

        # WHY Card (Deep Technical Rationale)
        self.box_why = QWidget()
        box_why_layout = QVBoxLayout(self.box_why)
        box_why_layout.setContentsMargins(6, 6, 6, 6)
        self.box_why.setStyleSheet("background-color: #261b05; border-left: 3px solid #ffaa00; border-radius: 4px;")
        lbl_why_tag = QLabel("PROČ (WHY - Technické zdůvodnění):")
        lbl_why_tag.setStyleSheet("color: #ffaa00; font-weight: bold; font-size: 10px; font-family: monospace;")
        box_why_layout.addWidget(lbl_why_tag)
        self.lbl_why_text = QLabel("Automatický negociátor detekuje čipset a navrhne optimální protokol.")
        self.lbl_why_text.setStyleSheet("color: #cbd5e1; font-size: 11px;")
        self.lbl_why_text.setWordWrap(True)
        box_why_layout.addWidget(self.lbl_why_text)
        card_layout.addWidget(self.box_why)

        layout.addWidget(self.card_container)

        # 4. Action Controls Rail
        actions_row = QHBoxLayout()
        actions_row.setSpacing(6)

        self.btn_prev = QPushButton("◀ Předchozí")
        self.btn_prev.setEnabled(False)
        self.btn_prev.clicked.connect(self._on_prev_clicked)
        actions_row.addWidget(self.btn_prev)

        self.btn_skip = QPushButton("Přeskočit")
        self.btn_skip.setEnabled(False)
        self.btn_skip.clicked.connect(self._on_skip_clicked)
        actions_row.addWidget(self.btn_skip)

        self.btn_execute = QPushButton("⚡ Spustit tento krok")
        self.btn_execute.setObjectName("btn_primary")
        self.btn_execute.setEnabled(False)
        self.btn_execute.clicked.connect(self._on_execute_clicked)
        actions_row.addWidget(self.btn_execute, stretch=1)

        layout.addLayout(actions_row)
        self.setStyleSheet("background-color: #111622; border: 1px solid #1f293d; border-radius: 8px;")

    def load_device_context(
        self,
        vid: str,
        pid: str,
        port: str = "",
        mode: str = "",
        gpt_present: bool = True,
        frp_locked: bool = True,
    ) -> None:
        """Profile device and load custom IF / WHAT / WHY workflow."""
        steps = self.advisor_engine.analyze_and_plan(vid, pid, port, mode, gpt_present, frp_locked)
        self._refresh_step_view()
        logger.info("Context Guide loaded %d steps for port: %s (%s)", len(steps), port, mode)

    def _refresh_step_view(self) -> None:
        step = self.advisor_engine.get_current_step()
        if not step:
            # Workflow completed
            self.lbl_step_counter.setText("Diagnostický postup dokončen! ✔")
            self.progress_bar.setValue(100)
            self.lbl_card_title.setText("Servisní sekvence úspěšně dokončena")
            self.lbl_if_text.setText("Všechny doporučené kroky byly vykonány.")
            self.lbl_what_text.setText("Zařízení lze restartovat do operačního systému.")
            self.lbl_why_text.setText("Všechny kontrolní body a zámky byly úspěšně zpracovány.")
            self.lbl_safety_badge.setText("HOTOVO")
            self.lbl_safety_badge.setStyleSheet("background-color: #062319; color: #00ff9d; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
            self.btn_execute.setEnabled(False)
            self.btn_skip.setEnabled(False)
            self.btn_prev.setEnabled(True)
            self.guidance_completed.emit(self.advisor_engine.active_diagnosis or "COMPLETE")
            return

        # Active Step Rendering
        self.lbl_step_counter.setText(f"Krok {step.step_number} z {step.total_steps}: {step.title}")
        pct = int(((step.step_number - 1) / step.total_steps) * 100)
        self.progress_bar.setValue(pct)

        self.lbl_card_title.setText(step.title)
        self.lbl_if_text.setText(step.condition_if)
        self.lbl_what_text.setText(step.action_what)
        self.lbl_why_text.setText(step.rationale_why)

        # Safety Badge
        if step.safety_rating == SafetyRating.SAFE:
            self.lbl_safety_badge.setText("BEZPEČNÁ OPERACE")
            self.lbl_safety_badge.setStyleSheet("background-color: #062319; color: #00ff9d; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
        elif step.safety_rating == SafetyRating.CAUTION:
            self.lbl_safety_badge.setText("ZVÝŠENÁ OPATRNOST")
            self.lbl_safety_badge.setStyleSheet("background-color: #261b05; color: #ffaa00; font-weight: bold; padding: 3px 8px; border-radius: 4px;")
        else:
            self.lbl_safety_badge.setText("KRITICKÁ POJISTKA")
            self.lbl_safety_badge.setStyleSheet("background-color: #27070e; color: #ff3366; font-weight: bold; padding: 3px 8px; border-radius: 4px;")

        self.btn_execute.setEnabled(True)
        self.btn_skip.setEnabled(True)
        self.btn_prev.setEnabled(self.advisor_engine.current_step_index > 0)

    def _on_execute_clicked(self) -> None:
        step = self.advisor_engine.get_current_step()
        if step:
            logger.info("Executing step: %s (%s)", step.title, step.action_id)
            self.step_action_triggered.emit(step.action_id, step.title)
            self.advisor_engine.advance_step()
            self._refresh_step_view()

    def _on_skip_clicked(self) -> None:
        logger.info("Operator skipped current step.")
        self.advisor_engine.advance_step()
        self._refresh_step_view()

    def _on_prev_clicked(self) -> None:
        self.advisor_engine.previous_step()
        self._refresh_step_view()
