import os
import time
import cv2
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
)
from lucide_icons import get_lucide_icon
from datamosh_engine import format_seconds_to_timestamp


class VideoPreviewWidget(QWidget):
    """
    High-performance, real-time synchronized video player widget based on OpenCV VideoCapture.
    Supports scrubbing slider, play/pause, smooth scrubbing, sequential read pipeline,
    and wall-clock synchronization to prevent slow-motion playback.
    """
    position_changed = Signal(float)

    def __init__(self, parent=None, min_height=220):
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
        self._was_playing_before_scrub = False

        # Precise timer for real-time frame deadlines (~100Hz ticks)
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self._on_playback_tick)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Frame View Label
        self.display_label = QLabel(self)
        self.display_label.setObjectName("previewDisplay")
        self.display_label.setMinimumSize(320, min_height)
        self.display_label.setStyleSheet("""
            QLabel#previewDisplay {
                background-color: #0b0f19;
                border: 1px solid #cbd5e1;
                border-radius: 16px;
                color: #94a3b8;
                font-weight: 600;
            }
        """)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setText("Brak załadowanego wideo")
        layout.addWidget(self.display_label, 1)

        # Controls Row
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.btn_play = QPushButton("  Odtwórz", self)
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=15))
        self.btn_play.setFixedWidth(105)
        self.btn_play.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.sliderPressed.connect(self._on_slider_pressed)
        self.slider.sliderReleased.connect(self._on_slider_released)
        self.slider.sliderMoved.connect(self.seek_frame)

        self.time_label = QLabel("00:00 / 00:00", self)
        self.time_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 700;
            color: #334155;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 8px;
            padding: 4px 10px;
        """)

        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.slider, 1)
        ctrl_layout.addWidget(self.time_label)

        layout.addLayout(ctrl_layout)

    def play(self):
        if not self.cap or not self.cap.isOpened():
            return

        # If at or past the end, restart from beginning
        if self.total_frames > 0 and self.current_frame >= self.total_frames - 1:
            self.current_frame = 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.cap_pos = 0

        self.is_playing = True
        self.play_start_time = time.perf_counter()
        self.play_start_frame = self.current_frame

        # 10ms tick ensures we evaluate frame presentation within <=10ms of deadline
        self.timer.start(10)
        self.btn_play.setText("  Wstrzymaj")
        self.btn_play.setIcon(get_lucide_icon("pause", color="#1e293b", size=15))

    def pause(self):
        self.is_playing = False
        if self.timer.isActive():
            self.timer.stop()
        self.btn_play.setText("  Odtwórz")
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=15))

    def toggle_play(self):
        if not self.cap or not self.cap.isOpened():
            return

        if self.is_playing:
            self.pause()
        else:
            self.play()

    def get_current_seconds(self):
        if not self.fps or self.fps <= 0:
            return 0.0
        return self.current_frame / self.fps

    def load_video(self, video_path):
        if not video_path or not os.path.exists(video_path):
            self.display_label.setText("Nie można odnaleźć pliku")
            return

        self.pause()
        if self.cap:
            self.cap.release()
            self.cap = None

        self.current_file_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.display_label.setText("Błąd odczytu wideo")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        raw_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = raw_fps if (raw_fps and 1.0 <= raw_fps <= 240.0) else 30.0
        self.video_duration = self.total_frames / self.fps
        self.slider.setRange(0, max(0, self.total_frames - 1))
        self.current_frame = 0
        self.cap_pos = 0
        self._last_rendered_frame = None
        self.seek_frame(0)
        self.btn_play.setText("  Odtwórz")
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=15))

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
        """Backward-compatible alias for seek_frame."""
        self.seek_frame(frame_no)

    def _on_playback_tick(self):
        if not self.cap or not self.cap.isOpened() or not self.is_playing:
            return

        elapsed = time.perf_counter() - self.play_start_time
        target_frame = self.play_start_frame + int(elapsed * self.fps)

        # Loop smoothly when reaching total frames
        if self.total_frames > 0 and target_frame >= self.total_frames:
            self.play_start_time = time.perf_counter()
            self.play_start_frame = 0
            target_frame = 0

        # Don't re-render if we haven't crossed to the next frame yet
        if target_frame == self.current_frame:
            return

        self._advance_to_frame(target_frame)

    def _advance_to_frame(self, target_frame):
        if not self.cap or not self.cap.isOpened():
            return

        target_frame = max(0, min(target_frame, max(0, self.total_frames - 1)))

        # Direct sequential read (fastest, standard playback path)
        if target_frame == self.cap_pos:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                self.cap_pos = target_frame + 1
                self.current_frame = target_frame
                self._render_frame(frame)
                self._update_ui_state()
                return

        # Slight frame lag (1-8 frames behind real-time): fast grab to catch up without seek
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

        # Large jump or loop backward: explicit seek required
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
            lbl_w, lbl_h = 480, 270

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

        # Downscale directly in OpenCV SIMD before RGB conversion to avoid Qt CPU scaling
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
        curr_sec = self.get_current_seconds()
        tot_sec = self.video_duration
        self.time_label.setText(f"{format_seconds_to_timestamp(curr_sec)} / {format_seconds_to_timestamp(tot_sec)}")

        if not self.slider.isSliderDown():
            self.slider.blockSignals(True)
            self.slider.setValue(self.current_frame)
            self.slider.blockSignals(False)

        self.position_changed.emit(curr_sec)

    def _on_slider_pressed(self):
        self._was_playing_before_scrub = self.is_playing
        if self.is_playing:
            self.pause()

    def _on_slider_released(self):
        self.seek_frame(self.slider.value())
        if getattr(self, '_was_playing_before_scrub', False):
            self.play()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.is_playing and self._last_rendered_frame is not None:
            self._render_frame(self._last_rendered_frame)

    def closeEvent(self, event):
        self.pause()
        if self.cap:
            self.cap.release()
            self.cap = None
        super().closeEvent(event)
