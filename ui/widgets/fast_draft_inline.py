import os
import time
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
        self.is_playing = False
        self.play_start_time = 0.0
        self.play_start_frame = 0
        self.current_frame = 0
        self.cap_pos = 0
        self.total_frames = 0
        self.fps = 30.0
        self.video_duration = 0.0
        self.current_file_path = ""
        self._last_rendered_frame = None

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_playback_tick)

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
        self.is_playing = False
        if self.timer.isActive():
            self.timer.stop()
        self.btn_play.setIcon(get_lucide_icon("play", color="#ffffff", size=13))

    def play(self):
        if not self.cap or not self.cap.isOpened():
            return

        if self.total_frames > 0 and self.current_frame >= self.total_frames - 1:
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.cap_pos = 0

        self.is_playing = True
        self.play_start_time = time.perf_counter()
        self.play_start_frame = self.current_frame
        self.timer.start(10)
        self.btn_play.setIcon(get_lucide_icon("pause", color="#ffffff", size=13))

    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def load_video(self, video_path):
        if not video_path or not os.path.exists(video_path):
            return

        self.pause()
        if self.cap:
            self.cap.release()
            self.timer.stop()
            self.cap = None

        self.current_file_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        raw_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = raw_fps if (raw_fps and 1.0 <= raw_fps <= 240.0) else 30.0
        self.video_duration = self.total_frames / self.fps
        self.current_frame = 0
        self.cap_pos = 0
        self._last_rendered_frame = None
        self.seek_frame(0)

    def seek_frame(self, frame_no):
        if not self.cap or not self.cap.isOpened():
            return

        frame_no = max(0, min(frame_no, max(0, self.total_frames - 1)))
        self.play_start_time = time.perf_counter()
        self.play_start_frame = frame_no

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.cap_pos = frame_no + 1
            self.current_frame = frame_no
            self._render_frame(frame)
            self._update_ui_state()

    def show_frame(self, frame_no):
        self.seek_frame(frame_no)

    def _on_playback_tick(self):
        if not self.cap or not self.cap.isOpened() or not self.is_playing:
            return

        elapsed = time.perf_counter() - self.play_start_time
        target_frame = self.play_start_frame + int(elapsed * self.fps)

        if self.total_frames > 0 and target_frame >= self.total_frames:
            self.play_start_time = time.perf_counter()
            self.play_start_frame = 0
            target_frame = 0

        if target_frame == self.current_frame:
            return

        self._advance_to_frame(target_frame)

    def _advance_to_frame(self, target_frame):
        if not self.cap or not self.cap.isOpened():
            return

        target_frame = max(0, min(target_frame, max(0, self.total_frames - 1)))

        if target_frame == self.cap_pos:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.cap_pos = target_frame + 1
                self.current_frame = target_frame
                self._render_frame(frame)
                self._update_ui_state()
                return

        if self.cap_pos <= target_frame <= self.cap_pos + 8:
            for _ in range(target_frame - self.cap_pos):
                self.cap.grab()
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.cap_pos = target_frame + 1
                self.current_frame = target_frame
                self._render_frame(frame)
                self._update_ui_state()
                return

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = self.cap.read()
        if ret and frame is not None:
            self.cap_pos = target_frame + 1
            self.current_frame = target_frame
            self._render_frame(frame)
            self._update_ui_state()

    def _render_frame(self, frame):
        if frame is None:
            return
        self._last_rendered_frame = frame

        lbl_w = self.display_label.width()
        lbl_h = self.display_label.height()
        if lbl_w <= 10 or lbl_h <= 10:
            lbl_w, lbl_h = 198, 110

        orig_h, orig_w = frame.shape[:2]
        if orig_h == 0 or orig_w == 0:
            return

        aspect = orig_w / orig_h
        if lbl_w / lbl_h > aspect:
            target_h = lbl_h
            target_w = max(1, int(lbl_h * aspect))
        else:
            target_w = lbl_w
            target_h = max(1, int(lbl_w / aspect))

        if target_w < orig_w and target_h < orig_h:
            interp = cv2.INTER_AREA if (orig_w // target_w >= 2) else cv2.INTER_LINEAR
            scaled_frame = cv2.resize(frame, (target_w, target_h), interpolation=interp)
        else:
            scaled_frame = frame
            target_w, target_h = orig_w, orig_h

        frame_rgb = cv2.cvtColor(scaled_frame, cv2.COLOR_BGR2RGB)
        bytes_per_line = 3 * target_w
        qt_img = QImage(frame_rgb.data, target_w, target_h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img)
        self.display_label.setPixmap(pixmap)

    def _update_ui_state(self):
        curr_sec = self.current_frame / self.fps if self.fps > 0 else 0.0
        tot_sec = self.video_duration
        self.time_label.setText(f"{format_seconds_to_timestamp(curr_sec)} / {format_seconds_to_timestamp(tot_sec)}")

    def closeEvent(self, event):
        self.pause()
        if self.cap:
            self.cap.release()
            self.cap = None
        super().closeEvent(event)
