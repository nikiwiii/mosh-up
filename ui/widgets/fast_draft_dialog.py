import os
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from lucide_icons import get_lucide_icon, get_lucide_pixmap
from .video_player import VideoPreviewWidget
from ..utils import apply_card_shadow


class FastDraftDialog(QDialog):
    """
    Modal dialog displaying the 3-second Fast Draft preview with auto-loop playback.
    Allows user to either accept and proceed to full render, or close and adjust parameters.
    """
    proceed_to_render = Signal()

    def __init__(self, draft_path, mode_name="Efekt", parent=None):
        super().__init__(parent)
        self.draft_path = draft_path
        self.setWindowTitle("Szybki podgląd (3-sekundowy Fast Draft)")
        self.setMinimumSize(700, 520)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        # Header card
        header_card = QFrame(self)
        header_card.setProperty("class", "softCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(16, 12, 16, 12)
        h_layout.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        icon_lbl = QLabel(header_card)
        icon_lbl.setPixmap(get_lucide_pixmap("zap", color="#2563eb", size=18))
        title_row.addWidget(icon_lbl)
        title_lbl = QLabel(f"Szybki podgląd (3s Fast Draft) • {mode_name}", header_card)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: 700; color: #0f172a;")
        title_row.addWidget(title_lbl)
        title_row.addStretch()

        sub_lbl = QLabel("Wycinek 3-sekundowy z aktualnie wybranymi parametrami (odtwarzany w pętli).", header_card)
        sub_lbl.setStyleSheet("font-size: 12px; font-weight: 500; color: #64748b;")

        h_layout.addLayout(title_row)
        h_layout.addWidget(sub_lbl)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Video Player Card
        player_card = QFrame(self)
        player_card.setProperty("class", "softCard")
        p_layout = QVBoxLayout(player_card)
        p_layout.setContentsMargins(14, 14, 14, 14)

        self.player = VideoPreviewWidget(player_card, min_height=320)
        p_layout.addWidget(self.player)
        apply_card_shadow(player_card)
        layout.addWidget(player_card, 1)

        # Actions Row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_close = QPushButton("  Zamknij i dostosuj parametry", self)
        self.btn_close.setProperty("class", "btnSecondary")
        self.btn_close.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_close.setFixedHeight(40)
        self.btn_close.clicked.connect(self.close)

        btn_row.addWidget(self.btn_close)
        btn_row.addStretch()

        self.btn_proceed = QPushButton("  Akceptuj i przejdź do renderowania (Krok 3)", self)
        self.btn_proceed.setProperty("class", "btnPrimary")
        self.btn_proceed.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_proceed.setFixedHeight(40)
        self.btn_proceed.clicked.connect(self._on_proceed)
        btn_row.addWidget(self.btn_proceed)

        layout.addLayout(btn_row)

        # Auto-load and play
        if draft_path and os.path.exists(draft_path):
            self.player.load_video(draft_path)
            self.player.toggle_play()

    def _on_proceed(self):
        self.proceed_to_render.emit()
        self.accept()

    def closeEvent(self, event):
        self.player.pause()
        if self.player.cap:
            self.player.cap.release()
        super().closeEvent(event)
