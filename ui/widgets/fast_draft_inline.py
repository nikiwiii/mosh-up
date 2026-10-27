import os
import cv2
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QStackedWidget, QFrame, QSizePolicy
)
from lucide_icons import get_lucide_icon
from datamosh_engine import format_seconds_to_timestamp


class FastDraftInlineWidget(QWidget):
    """
    Compact 3-state widget for Fast Draft preview on the effect description level:
    - State 0: Action button ("Podgląd 3s")
    - State 1: Compact statusbar / progress bar with percentage
    - State 2: Small looping video player with micro-controls (play/pause, refresh, close)
    """
    draft_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30.0
        self.video_duration = 0.0
        self.current_file_path = ""

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedSize(118, 30)

        self.stack = QStackedWidget(self)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(self.stack)

        # --- State 0: Action Button ---
        page_btn = QWidget()
        pb_layout = QHBoxLayout(page_btn)
        pb_layout.setContentsMargins(0, 0, 0, 0)
        pb_layout.setSpacing(0)
        pb_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.btn_draft = QPushButton("  Podgląd 3s", page_btn)
        self.btn_draft.setIcon(get_lucide_icon("zap", color="#ffffff", size=13))
        self.btn_draft.setFixedHeight(30)
        self.btn_draft.setFixedWidth(118)
        self.btn_draft.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_draft.setToolTip("Generuj 3-sekundowy podgląd z bieżącymi parametrami")
        self.btn_draft.setStyleSheet("""
            QPushButton {
                background-color: #151829;
                color: #ffffff;
                font-size: 11.5px;
                font-weight: 700;
                border: 1px solid #151829;
                border-radius: 8px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #242a42;
                border-color: #242a42;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0d101c;
                border-color: #0d101c;
                color: #ffffff;
            }
        """)
        self.btn_draft.clicked.connect(self.draft_requested.emit)
        pb_layout.addWidget(self.btn_draft)

        self.stack.addWidget(page_btn)  # Index 0

        # --- State 1: Progress Statusbar ---
        page_loading = QWidget()
        pl_layout = QHBoxLayout(page_loading)
        pl_layout.setContentsMargins(0, 0, 0, 0)
        pl_layout.setSpacing(0)
        pl_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.progress_bar = QProgressBar(page_loading)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(28)
        self.progress_bar.setFixedWidth(130)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #f1f5fa;
                border: 1px solid #cbd5e1;
                border-radius: 7px;
                text-align: center;
                color: #1e293b;
                font-size: 11px;
                font-weight: 700;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #3b82f6);
                border-radius: 6px;
            }
        """)
        pl_layout.addWidget(self.progress_bar)

        self.stack.addWidget(page_loading)  # Index 1

        # --- State 2: Small Preview Player ---
        page_preview = QWidget()
        pp_layout = QVBoxLayout(page_preview)
        pp_layout.setContentsMargins(0, 0, 0, 0)
        pp_layout.setSpacing(4)
        pp_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        self.preview_card = QFrame(page_preview)
        self.preview_card.setFixedSize(206, 142)
        self.preview_card.setStyleSheet("""
            QFrame {
                background-color: #0b0f19;
                border: 1px solid #334155;
                border-radius: 10px;
            }
        """)
        pc_layout = QVBoxLayout(self.preview_card)
        pc_layout.setContentsMargins(4, 4, 4, 4)
        pc_layout.setSpacing(3)

        # Video Display Label
        self.display_label = QLabel(self.preview_card)
        self.display_label.setFixedSize(198, 110)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("background-color: #000000; border-radius: 6px; border: none;")
        pc_layout.addWidget(self.display_label)

        # Micro-controls row
        ctrl_row = QHBoxLayout()
        ctrl_row.setContentsMargins(2, 0, 2, 0)
        ctrl_row.setSpacing(4)

        self.btn_play = QPushButton(self.preview_card)
        self.btn_play.setIcon(get_lucide_icon("pause", color="#ffffff", size=13))
        self.btn_play.setFixedSize(22, 22)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 4px; } QPushButton:hover { background: #1e293b; }")
        self.btn_play.clicked.connect(self.toggle_play)
        ctrl_row.addWidget(self.btn_play)

        self.time_label = QLabel("00:00 / 00:03", self.preview_card)
        self.time_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: 600; border: none; background: transparent;")
        ctrl_row.addWidget(self.time_label)

        ctrl_row.addStretch()

        self.btn_refresh = QPushButton(self.preview_card)
        self.btn_refresh.setIcon(get_lucide_icon("rotate-ccw", color="#94a3b8", size=12))
        self.btn_refresh.setFixedSize(22, 22)
        self.btn_refresh.setToolTip("Odśwież podgląd")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 4px; } QPushButton:hover { background: #1e293b; }")
        self.btn_refresh.clicked.connect(self.draft_requested.emit)
        ctrl_row.addWidget(self.btn_refresh)

        self.btn_close = QPushButton(self.preview_card)
        self.btn_close.setIcon(get_lucide_icon("x", color="#94a3b8", size=12))
        self.btn_close.setFixedSize(22, 22)
        self.btn_close.setToolTip("Zamknij podgląd")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet("QPushButton { background: transparent; border: none; border-radius: 4px; } QPushButton:hover { background: #1e293b; }")
        self.btn_close.clicked.connect(self.close_preview)
        ctrl_row.addWidget(self.btn_close)

        pc_layout.addLayout(ctrl_row)
        pp_layout.addWidget(self.preview_card)

        self.stack.addWidget(page_preview)  # Index 2

        self.show_button()

    def sizeHint(self):
        curr = self.stack.currentWidget()
        if curr:
            return curr.sizeHint()
        return QSize(118, 30)

    def minimumSizeHint(self):
        return self.sizeHint()

    def show_button(self):
        self.pause()
        self.setFixedSize(118, 30)
        self.stack.setCurrentIndex(0)
        self.updateGeometry()

    def show_loading(self):
        self.pause()
        self.setFixedSize(130, 28)
        self.progress_bar.setValue(0)
        self.stack.setCurrentIndex(1)
        self.updateGeometry()

    def set_progress(self, pct):
        self.progress_bar.setValue(int(pct))

    def show_preview(self, video_path):
        self.load_video(video_path)
        self.setFixedSize(206, 142)
        self.stack.setCurrentIndex(2)
        self.updateGeometry()
        self.play()

    def close_preview(self):
        self.show_button()
        if self.cap:
            self.cap.release()
            self.cap = None

    def reset(self):
        self.show_button()
        if self.cap:
            self.cap.release()
            self.cap = None

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setIcon(get_lucide_icon("play", color="#ffffff", size=13))

    def play(self):
        if not self.cap or not self.cap.isOpened():
            return
        interval = max(10, int(1000.0 / self.fps))
        self.timer.start(interval)
        self.btn_play.setIcon(get_lucide_icon("pause", color="#ffffff", size=13))

    def toggle_play(self):
        if self.timer.isActive():
            self.pause()
        else:
            self.play()

    def load_video(self, video_path):
        if not video_path or not os.path.exists(video_path):
            return

        if self.cap:
            self.cap.release()
            self.timer.stop()

        self.current_file_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.video_duration = self.total_frames / self.fps
        self.current_frame = 0
        self.show_frame(0)

    def _next_frame(self):
        if not self.cap:
            return
        self.current_frame += 1
        if self.current_frame >= self.total_frames:
            self.current_frame = 0
        self.show_frame(self.current_frame)

    def show_frame(self, frame_no):
        if not self.cap or not self.cap.isOpened():
            return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = self.cap.read()
        if ret and frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_img).scaled(
                self.display_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.display_label.setPixmap(pixmap)

            curr_sec = frame_no / self.fps if self.fps > 0 else 0.0
            tot_sec = self.video_duration
            self.time_label.setText(f"{format_seconds_to_timestamp(curr_sec)} / {format_seconds_to_timestamp(tot_sec)}")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        super().closeEvent(event)
