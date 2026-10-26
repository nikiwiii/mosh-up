import os
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
    Lightweight video player widget based on OpenCV VideoCapture.
    Supports scrubbing slider, play/pause, and real-time position reporting.
    """
    position_changed = Signal(float)

    def __init__(self, parent=None, min_height=220):
        super().__init__(parent)
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30.0
        self.video_duration = 0.0
        self.current_file_path = ""

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

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("  Odtwórz")
            self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=15))

    def get_current_seconds(self):
        if not self.fps or self.fps <= 0:
            return 0.0
        return self.current_frame / self.fps

    def load_video(self, video_path):
        if not video_path or not os.path.exists(video_path):
            self.display_label.setText("Nie można odnaleźć pliku")
            return

        if self.cap:
            self.cap.release()
            self.timer.stop()

        self.current_file_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.display_label.setText("Błąd odczytu wideo")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.video_duration = self.total_frames / self.fps
        self.slider.setRange(0, max(0, self.total_frames - 1))
        self.current_frame = 0
        self.show_frame(0)
        self.btn_play.setText("  Odtwórz")
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=15))

    def toggle_play(self):
        if not self.cap or not self.cap.isOpened():
            return

        if self.timer.isActive():
            self.pause()
        else:
            interval = max(10, int(1000.0 / self.fps))
            self.timer.start(interval)
            self.btn_play.setText("  Wstrzymaj")
            self.btn_play.setIcon(get_lucide_icon("pause", color="#1e293b", size=15))

    def seek_frame(self, frame_no):
        if not self.cap:
            return
        self.current_frame = frame_no
        self.show_frame(frame_no)

    def _next_frame(self):
        if not self.cap:
            return
        self.current_frame += 1
        if self.current_frame >= self.total_frames:
            self.current_frame = 0
        self.slider.setValue(self.current_frame)
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

            curr_sec = self.get_current_seconds()
            tot_sec = self.video_duration
            self.time_label.setText(f"{format_seconds_to_timestamp(curr_sec)} / {format_seconds_to_timestamp(tot_sec)}")
            self.position_changed.emit(curr_sec)

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        super().closeEvent(event)
