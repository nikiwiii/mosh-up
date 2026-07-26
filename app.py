"""
MoshUp - Video Datamoshing Studio
Dark Swiss & Neo-Brutalist Interface with Sleek 1px Borders & Electric Violet Accent.
All user messages and interface texts translated to English.
"""

import os
import sys
import time
import random
import subprocess
import cv2
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl, QSize
from PySide6.QtGui import QIcon, QPixmap, QImage, QDragEnterEvent, QDropEvent, QColor, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QTabWidget, QSlider, QSpinBox,
    QDoubleSpinBox, QCheckBox, QComboBox, QProgressBar, QTextEdit,
    QGroupBox, QFrame, QMessageBox, QSplitter, QLineEdit
)

from brutalist_style import BRUTALIST_DARK_QSS
from datamosh_engine import DatamoshEngine, get_ffmpeg_exe, parse_timestamp, format_seconds_to_timestamp
from lucide_icons import get_lucide_icon, get_lucide_pixmap


def generate_random_filename(input_path, mode=""):
    """Generates an output filename with random 4-digit ID to prevent overwriting."""
    if not input_path:
        rand_id = random.randint(1000, 9999)
        return f"moshup_output_{rand_id}.mp4"
    
    dir_name = os.path.dirname(input_path) or "."
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    rand_id = random.randint(1000, 9999)
    
    mode_str = f"_{mode}" if mode else ""
    return os.path.join(dir_name, f"{base_name}_moshup{mode_str}_{rand_id}.mp4")


class DatamoshWorker(QThread):
    """Background worker thread to run datamoshing without freezing the GUI."""
    progress_signal = Signal(int, str)
    finished_signal = Signal(str)
    error_signal = Signal(str)

    def __init__(self, mode, input_path, output_path, options):
        super().__init__()
        self.mode = mode
        self.input_path = input_path
        self.output_path = output_path
        self.options = options
        self.engine = DatamoshEngine()

    def run(self):
        try:
            def cb(pct, msg):
                self.progress_signal.emit(pct, msg)

            self.engine.process(self.mode, self.input_path, self.output_path, self.options, progress_callback=cb)
            self.finished_signal.emit(self.output_path)
        except Exception as e:
            self.error_signal.emit(str(e))


class DropAreaWidget(QFrame):
    """Custom Drag & Drop video file drop area with sleek 1px styling."""
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 1px dashed #4b5563;
                border-radius: 2px;
                background-color: #12141c;
            }
            QFrame#dropArea:hover {
                background-color: #1a1726;
                border: 1px dashed #a855f7;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(get_lucide_pixmap("file-video", color="#c084fc", size=40))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("DROP VIDEO FILE HERE\nOR CLICK 'SELECT VIDEO A'", self)
        self.text_label.setStyleSheet("font-size: 12px; font-weight: 800; color: #f3f4f6; background: transparent;")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv')):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "UNSUPPORTED FORMAT", "Please select a valid video file (MP4, AVI, MOV, MKV)")


class VideoPreviewWidget(QWidget):
    """Custom Video Player Widget using OpenCV for lightweight playback."""
    position_changed = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._next_frame)
        self.current_frame = 0
        self.total_frames = 0
        self.fps = 30.0
        self.video_duration = 0.0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Frame View Label
        self.display_label = QLabel(self)
        self.display_label.setMinimumSize(320, 200)
        self.display_label.setStyleSheet("""
            background-color: #08090d;
            border: 1px solid #2a2d3d;
            border-radius: 2px;
            color: #9ca3af;
            font-weight: 800;
        """)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setText("[ VIDEO PREVIEW MONITOR ]")
        layout.addWidget(self.display_label, 1)

        # Controls Row
        ctrl_layout = QHBoxLayout()
        self.btn_play = QPushButton(" PLAY", self)
        self.btn_play.setIcon(get_lucide_icon("play", color="#ffffff", size=16))
        self.btn_play.setFixedWidth(110)
        self.btn_play.clicked.connect(self.toggle_play)

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.sliderMoved.connect(self.seek_frame)

        self.time_label = QLabel("00:00 / 00:00", self)
        self.time_label.setStyleSheet("font-size: 11px; font-weight: 800; color: #f3f4f6;")

        ctrl_layout.addWidget(self.btn_play)
        ctrl_layout.addWidget(self.slider, 1)
        ctrl_layout.addWidget(self.time_label)

        layout.addLayout(ctrl_layout)

    def get_current_seconds(self):
        if not self.fps or self.fps <= 0:
            return 0.0
        return self.current_frame / self.fps

    def load_video(self, video_path):
        if self.cap:
            self.cap.release()
            self.timer.stop()

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            self.display_label.setText("[ CANNOT LOAD VIDEO ]")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.video_duration = self.total_frames / self.fps
        self.slider.setRange(0, self.total_frames - 1)
        self.current_frame = 0
        self.show_frame(0)
        self.btn_play.setText(" PLAY")
        self.btn_play.setIcon(get_lucide_icon("play", color="#ffffff", size=16))

    def toggle_play(self):
        if not self.cap or not self.cap.isOpened():
            return

        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText(" PLAY")
            self.btn_play.setIcon(get_lucide_icon("play", color="#ffffff", size=16))
        else:
            interval = max(10, int(1000.0 / self.fps))
            self.timer.start(interval)
            self.btn_play.setText(" PAUSE")
            self.btn_play.setIcon(get_lucide_icon("pause", color="#ffffff", size=16))

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


class MoshUpApp(QMainWindow):
    """Main Application Window for MoshUp in Sleek Dark Swiss Style with Electric Violet Accent."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MOSHUP // VIDEO DATAMOSHING STUDIO")
        self.setWindowIcon(get_lucide_icon("film", color="#ffffff", size=32))
        self.resize(1060, 750)
        self.setMinimumSize(900, 640)

        self.input_file_a = ""
        self.input_file_b = ""
        self.output_file = ""
        self.video_duration = 0.0
        self.worker = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(BRUTALIST_DARK_QSS)

        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 12, 16, 12)
        main_layout.setSpacing(12)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # LEFT PANEL: Input & Preview
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        # File Drop & Input Group
        input_group = QGroupBox("INPUT VIDEO FILE", self)
        input_g_layout = QVBoxLayout(input_group)

        self.drop_area = DropAreaWidget(self)
        self.drop_area.file_dropped.connect(self.set_input_file_a)
        input_g_layout.addWidget(self.drop_area)

        file_btn_layout = QHBoxLayout()
        self.btn_select_a = QPushButton(" SELECT VIDEO A...", self)
        self.btn_select_a.setIcon(get_lucide_icon("folder-open", color="#ffffff", size=18))
        self.btn_select_a.clicked.connect(self.browse_input_a)

        self.lbl_file_a_path = QLabel("NO FILE SELECTED", self)
        self.lbl_file_a_path.setStyleSheet("font-size: 11px; font-weight: 700; color: #9ca3af;")
        self.lbl_file_a_path.setWordWrap(True)

        file_btn_layout.addWidget(self.btn_select_a)
        file_btn_layout.addWidget(self.lbl_file_a_path, 1)
        input_g_layout.addLayout(file_btn_layout)

        left_layout.addWidget(input_group)

        # Video Preview Player
        preview_group = QGroupBox("PREVIEW MONITOR", self)
        prev_layout = QVBoxLayout(preview_group)
        self.preview_player = VideoPreviewWidget(self)
        prev_layout.addWidget(self.preview_player)
        left_layout.addWidget(preview_group, 1)

        splitter.addWidget(left_widget)

        # RIGHT PANEL: Options & Datamosh Tabs
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # Preset Selector
        preset_group = QGroupBox("STYLE PRESETS", self)
        preset_layout = QHBoxLayout(preset_group)
        preset_label = QLabel("SELECT PRESET:", self)
        preset_label.setStyleSheet("font-weight: 800; color: #f3f4f6;")
        
        self.combo_presets = QComboBox(self)
        self.combo_presets.addItems([
            "DEFAULT CONFIGURATION",
            "VOLCANO MELT (KEYFRAME REMOVAL)",
            "ENDLESS MOTION SMEAR (P-FRAME REPEAT)",
            "CYBERPUNK BIT GLITCH (DATA CORRUPTION)",
            "FLOW DRIFT (OPTICAL FLOW DRIFT)"
        ])
        self.combo_presets.currentIndexChanged.connect(self.apply_preset)

        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.combo_presets, 1)
        right_layout.addWidget(preset_group)

        # Datamosh Mode Tabs with Lucide Icons
        self.tabs = QTabWidget(self)
        self.tabs.setIconSize(QSize(18, 18))

        # Tab 1: Volcano Melt (I-Frame Removal by Timestamps)
        tab_volcano = QWidget()
        tab_v_layout = QVBoxLayout(tab_volcano)

        lbl_v_desc = QLabel("Removes keyframes (I-Frames) in the specified time window, causing motion vectors to deform previous video frames.", tab_volcano)
        lbl_v_desc.setWordWrap(True)
        lbl_v_desc.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: 700; margin-bottom: 6px;")
        tab_v_layout.addWidget(lbl_v_desc)

        # Timestamp Input Controls
        ts_box = QGroupBox("TIMESTAMPS RANGE", tab_volcano)
        ts_box_layout = QVBoxLayout(ts_box)

        # Start Timestamp row
        ts_start_layout = QHBoxLayout()
        ts_start_layout.addWidget(QLabel("START TIME:", tab_volcano))
        self.txt_ts_start = QLineEdit(tab_volcano)
        self.txt_ts_start.setPlaceholderText("00:00")
        self.txt_ts_start.setText("00:00")
        self.txt_ts_start.textChanged.connect(self.validate_timestamps)
        
        self.btn_set_curr_start = QPushButton(" SET FROM CURSOR", tab_volcano)
        self.btn_set_curr_start.setIcon(get_lucide_icon("clock", color="#ffffff", size=14))
        self.btn_set_curr_start.clicked.connect(self.set_ts_start_from_cursor)

        ts_start_layout.addWidget(self.txt_ts_start, 1)
        ts_start_layout.addWidget(self.btn_set_curr_start)
        ts_box_layout.addLayout(ts_start_layout)

        # End Timestamp row
        ts_end_layout = QHBoxLayout()
        ts_end_layout.addWidget(QLabel("END TIME:", tab_volcano))
        self.txt_ts_end = QLineEdit(tab_volcano)
        self.txt_ts_end.setPlaceholderText("00:30")
        self.txt_ts_end.setText("00:30")
        self.txt_ts_end.textChanged.connect(self.validate_timestamps)

        self.btn_set_curr_end = QPushButton(" SET FROM CURSOR", tab_volcano)
        self.btn_set_curr_end.setIcon(get_lucide_icon("clock", color="#ffffff", size=14))
        self.btn_set_curr_end.clicked.connect(self.set_ts_end_from_cursor)

        ts_end_layout.addWidget(self.txt_ts_end, 1)
        ts_end_layout.addWidget(self.btn_set_curr_end)
        ts_box_layout.addLayout(ts_end_layout)

        # Validation Feedback Status Label
        self.lbl_ts_validation = QLabel("INFO: FORMAT MM:SS (e.g. 00:05 or 01:20)", tab_volcano)
        self.lbl_ts_validation.setStyleSheet("font-size: 11px; font-weight: 800; color: #f3f4f6; margin-top: 4px;")
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(ts_box)
        tab_v_layout.addStretch()
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#ffffff"), "VOLCANO MELT")

        # Tab 2: Motion Smear (P-Frame Duplication)
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)

        lbl_s_desc = QLabel("Duplicates delta frames (P-Frames) to repeat motion vectors indefinitely, smearing pixels across the frame.", tab_smear)
        lbl_s_desc.setWordWrap(True)
        lbl_s_desc.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: 700; margin-bottom: 8px;")
        tab_s_layout.addWidget(lbl_s_desc)

        tab_s_layout.addWidget(QLabel("REPEAT COUNT:", tab_smear))
        self.spin_s_repeat = QSpinBox(tab_smear)
        self.spin_s_repeat.setRange(2, 60)
        self.spin_s_repeat.setValue(15)
        tab_s_layout.addWidget(self.spin_s_repeat)

        tab_s_layout.addWidget(QLabel("FREQUENCY (EVERY N-TH P-FRAME):", tab_smear))
        self.spin_s_freq = QSpinBox(tab_smear)
        self.spin_s_freq.setRange(1, 30)
        self.spin_s_freq.setValue(5)
        tab_s_layout.addWidget(self.spin_s_freq)

        tab_s_layout.addStretch()
        self.tabs.addTab(tab_smear, get_lucide_icon("wind", color="#ffffff"), "MOTION SMEAR")

        # Tab 3: Stitch Mosh (Cross-Video Blend)
        tab_stitch = QWidget()
        tab_st_layout = QVBoxLayout(tab_stitch)

        lbl_st_desc = QLabel("Stitches Video A and B together. Video B's initial keyframe is removed, so Video B animates Video A's static frame.", tab_stitch)
        lbl_st_desc.setWordWrap(True)
        lbl_st_desc.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: 700; margin-bottom: 8px;")
        tab_st_layout.addWidget(lbl_st_desc)

        tab_st_layout.addWidget(QLabel("SECOND VIDEO B (TRANSITION):", tab_stitch))
        file_b_layout = QHBoxLayout()
        self.btn_select_b = QPushButton(" SELECT VIDEO B...", tab_stitch)
        self.btn_select_b.setIcon(get_lucide_icon("folder-open", color="#ffffff", size=18))
        self.btn_select_b.clicked.connect(self.browse_input_b)
        self.lbl_file_b_path = QLabel("NO SECOND FILE", tab_stitch)
        self.lbl_file_b_path.setStyleSheet("font-size: 11px; font-weight: 700; color: #9ca3af;")
        file_b_layout.addWidget(self.btn_select_b)
        file_b_layout.addWidget(self.lbl_file_b_path, 1)
        tab_st_layout.addLayout(file_b_layout)

        tab_st_layout.addStretch()
        self.tabs.addTab(tab_stitch, get_lucide_icon("shuffle", color="#ffffff"), "STITCH MOSH")

        # Tab 4: Cyber Glitch (Bit Corruption)
        tab_cyber = QWidget()
        tab_c_layout = QVBoxLayout(tab_cyber)

        lbl_c_desc = QLabel("Injects random byte corruptions directly into P-frame vector payloads for cyberpunk digital artifacting.", tab_cyber)
        lbl_c_desc.setWordWrap(True)
        lbl_c_desc.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: 700; margin-bottom: 8px;")
        tab_c_layout.addWidget(lbl_c_desc)

        tab_c_layout.addWidget(QLabel("CORRUPTION RATE (% OF P-FRAMES):", tab_cyber))
        self.slider_c_rate = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_rate.setRange(1, 30)
        self.slider_c_rate.setValue(8)
        tab_c_layout.addWidget(self.slider_c_rate)

        tab_c_layout.addWidget(QLabel("BYTE SWAP FACTOR:", tab_cyber))
        self.slider_c_intensity = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_intensity.setRange(1, 20)
        self.slider_c_intensity.setValue(3)
        tab_c_layout.addWidget(self.slider_c_intensity)

        tab_c_layout.addStretch()
        self.tabs.addTab(tab_cyber, get_lucide_icon("cpu", color="#ffffff"), "CYBER GLITCH")

        # Tab 5: Flow Drift (Optical Flow)
        tab_flow = QWidget()
        tab_fl_layout = QVBoxLayout(tab_flow)

        lbl_fl_desc = QLabel("Calculates optical flow vector fields between frames and warps accumulated pixel feedback directly on screen.", tab_flow)
        lbl_fl_desc.setWordWrap(True)
        lbl_fl_desc.setStyleSheet("color: #d1d5db; font-size: 11px; font-weight: 700; margin-bottom: 8px;")
        tab_fl_layout.addWidget(lbl_fl_desc)

        tab_fl_layout.addWidget(QLabel("FLOW MAGNITUDE SCALE:", tab_flow))
        self.spin_fl_scale = QDoubleSpinBox(tab_flow)
        self.spin_fl_scale.setRange(0.5, 10.0)
        self.spin_fl_scale.setSingleStep(0.5)
        self.spin_fl_scale.setValue(2.5)
        tab_fl_layout.addWidget(self.spin_fl_scale)

        tab_fl_layout.addWidget(QLabel("TRAIL DECAY FACTOR:", tab_flow))
        self.spin_fl_decay = QDoubleSpinBox(tab_flow)
        self.spin_fl_decay.setRange(0.50, 0.98)
        self.spin_fl_decay.setSingleStep(0.05)
        self.spin_fl_decay.setValue(0.85)
        tab_fl_layout.addWidget(self.spin_fl_decay)

        tab_fl_layout.addStretch()
        self.tabs.addTab(tab_flow, get_lucide_icon("waves", color="#ffffff"), "FLOW DRIFT")

        right_layout.addWidget(self.tabs)

        # Global Options Group
        opts_group = QGroupBox("OUTPUT CONFIGURATION", self)
        opts_layout = QVBoxLayout(opts_group)

        self.chk_keep_audio = QCheckBox(" PRESERVE ORIGINAL AUDIO TRACK", self)
        self.chk_keep_audio.setChecked(True)
        opts_layout.addWidget(self.chk_keep_audio)

        out_file_layout = QHBoxLayout()
        self.btn_select_out = QPushButton(" SAVE AS...", self)
        self.btn_select_out.setIcon(get_lucide_icon("save", color="#ffffff", size=18))
        self.btn_select_out.clicked.connect(self.browse_output)
        self.lbl_out_path = QLabel("AUTOMATIC UNIQUE FILENAME", self)
        self.lbl_out_path.setStyleSheet("font-size: 11px; font-weight: 700; color: #9ca3af;")
        out_file_layout.addWidget(self.btn_select_out)
        out_file_layout.addWidget(self.lbl_out_path, 1)
        opts_layout.addLayout(out_file_layout)

        right_layout.addWidget(opts_group)

        # START BUTTON
        self.btn_start = QPushButton(" MOSH UP", self)
        self.btn_start.setIcon(get_lucide_icon("rocket", color="#ffffff", size=22))
        self.btn_start.setIconSize(QSize(22, 22))
        self.btn_start.setProperty("class", "btnGreen")
        self.btn_start.setFixedHeight(48)
        self.btn_start.setStyleSheet("font-size: 15px; font-weight: 900;")
        self.btn_start.clicked.connect(self.start_datamosh)
        right_layout.addWidget(self.btn_start)

        splitter.addWidget(right_widget)
        splitter.setSizes([450, 550])

        main_layout.addWidget(splitter, 1)

        # Bottom Progress & Log Box
        bottom_frame = QFrame(self)
        bottom_frame.setProperty("class", "brutalistPanel")
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(10, 8, 10, 8)

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(24)

        self.lbl_status = QLabel("STATUS: IDLE", self)
        self.lbl_status.setStyleSheet("font-weight: 900; color: #ffffff; text-transform: uppercase;")
        progress_row.addWidget(self.lbl_status)
        progress_row.addWidget(self.progress_bar, 1)

        bottom_layout.addLayout(progress_row)

        self.log_console = QTextEdit(self)
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(85)
        self.log_console.setPlaceholderText("Execution log stream...")
        bottom_layout.addWidget(self.log_console)

        # Action bar buttons
        action_bar = QHBoxLayout()
        self.btn_open_folder = QPushButton(" OPEN OUTPUT DIRECTORY", self)
        self.btn_open_folder.setIcon(get_lucide_icon("folder-open", color="#ffffff", size=18))
        self.btn_open_folder.setProperty("class", "btnSecondary")
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        self.btn_open_folder.setEnabled(False)

        self.btn_open_video = QPushButton(" OPEN MOSHED VIDEO", self)
        self.btn_open_video.setIcon(get_lucide_icon("film", color="#ffffff", size=18))
        self.btn_open_video.setProperty("class", "btnSecondary")
        self.btn_open_video.clicked.connect(self.open_output_video)
        self.btn_open_video.setEnabled(False)

        action_bar.addWidget(self.btn_open_folder)
        action_bar.addWidget(self.btn_open_video)
        action_bar.addStretch()

        bottom_layout.addLayout(action_bar)
        main_layout.addWidget(bottom_frame)

        self.log("SYSTEM READY. SELECT AN INPUT VIDEO FILE TO BEGIN.")

    def log(self, text):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_console.append(timestamp + text)

    def update_random_output_filename(self, mode=""):
        if self.input_file_a:
            self.output_file = generate_random_filename(self.input_file_a, mode)
            self.lbl_out_path.setText(os.path.basename(self.output_file))

    def browse_input_a(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT VIDEO FILE A", "", "Video (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*.*)"
        )
        if file_path:
            self.set_input_file_a(file_path)

    def set_input_file_a(self, file_path):
        self.input_file_a = file_path
        self.lbl_file_a_path.setText(os.path.basename(file_path))
        self.preview_player.load_video(file_path)
        self.video_duration = self.preview_player.video_duration
        
        self.txt_ts_start.setText("00:00")
        self.txt_ts_end.setText(format_seconds_to_timestamp(self.video_duration))
        self.validate_timestamps()

        self.update_random_output_filename()
        self.log(f"LOADED VIDEO A: {file_path} (DURATION: {format_seconds_to_timestamp(self.video_duration)})")

    def set_ts_start_from_cursor(self):
        curr_sec = self.preview_player.get_current_seconds()
        self.txt_ts_start.setText(format_seconds_to_timestamp(curr_sec))
        self.validate_timestamps()

    def set_ts_end_from_cursor(self):
        curr_sec = self.preview_player.get_current_seconds()
        self.txt_ts_end.setText(format_seconds_to_timestamp(curr_sec))
        self.validate_timestamps()

    def validate_timestamps(self):
        """Validates timestamp inputs and updates visual feedback label."""
        if not hasattr(self, 'lbl_ts_validation'):
            return False

        start_str = self.txt_ts_start.text()
        end_str = self.txt_ts_end.text()

        start_sec = parse_timestamp(start_str)
        end_sec = parse_timestamp(end_str)

        if start_sec is None:
            self.lbl_ts_validation.setStyleSheet("color: #ef4444; font-weight: 800;")
            self.lbl_ts_validation.setText("⚠️ INVALID START TIMESTAMP (Use MM:SS or MM:SS.s)")
            return False

        if end_sec is None:
            self.lbl_ts_validation.setStyleSheet("color: #ef4444; font-weight: 800;")
            self.lbl_ts_validation.setText("⚠️ INVALID END TIMESTAMP (Use MM:SS or MM:SS.s)")
            return False

        if start_sec >= end_sec:
            self.lbl_ts_validation.setStyleSheet("color: #ef4444; font-weight: 800;")
            self.lbl_ts_validation.setText(f"⚠️ END TIME ({format_seconds_to_timestamp(end_sec)}) MUST BE GREATER THAN START TIME ({format_seconds_to_timestamp(start_sec)})")
            return False

        if self.video_duration > 0 and end_sec > self.video_duration:
            self.lbl_ts_validation.setStyleSheet("color: #f59e0b; font-weight: 800;")
            self.lbl_ts_validation.setText(f"⚠️ END TIME ({format_seconds_to_timestamp(end_sec)}) EXCEEDS VIDEO DURATION ({format_seconds_to_timestamp(self.video_duration)})")
            return False

        duration = end_sec - start_sec
        self.lbl_ts_validation.setStyleSheet("color: #ffffff; font-weight: 800; background-color: #7c3aed; padding: 3px 6px; border-radius: 2px;")
        self.lbl_ts_validation.setText(f"✓ VALID TIMESTAMPS: {format_seconds_to_timestamp(start_sec)} -> {format_seconds_to_timestamp(end_sec)} [DURATION: {duration:.1f}s]")
        return True

    def browse_input_b(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "SELECT VIDEO FILE B", "", "Video (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*.*)"
        )
        if file_path:
            self.input_file_b = file_path
            self.lbl_file_b_path.setText(os.path.basename(file_path))
            self.log(f"LOADED VIDEO B: {file_path}")

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "SAVE DATAMOSH VIDEO OUTPUT", self.output_file or f"moshup_output_{random.randint(1000, 9999)}.mp4", "MP4 Video (*.mp4);;AVI Video (*.avi)"
        )
        if file_path:
            self.output_file = file_path
            self.lbl_out_path.setText(os.path.basename(file_path))

    def apply_preset(self, index):
        if index == 1:
            self.tabs.setCurrentIndex(0)
            self.txt_ts_start.setText("00:00")
            if self.video_duration > 0:
                self.txt_ts_end.setText(format_seconds_to_timestamp(self.video_duration))
            else:
                self.txt_ts_end.setText("00:30")
        elif index == 2:
            self.tabs.setCurrentIndex(1)
            self.spin_s_repeat.setValue(20)
            self.spin_s_freq.setValue(4)
        elif index == 3:
            self.tabs.setCurrentIndex(3)
            self.slider_c_rate.setValue(15)
            self.slider_c_intensity.setValue(6)
        elif index == 4:
            self.tabs.setCurrentIndex(4)
            self.spin_fl_scale.setValue(4.0)
            self.spin_fl_decay.setValue(0.90)

    def start_datamosh(self):
        if not self.input_file_a or not os.path.exists(self.input_file_a):
            QMessageBox.warning(self, "MISSING INPUT VIDEO", "Please select a valid input video file (Video A) first!")
            return

        mode_map = {
            0: 'volcano_melt',
            1: 'motion_smear',
            2: 'stitch_mosh',
            3: 'cyber_glitch',
            4: 'flow_drift'
        }
        tab_idx = self.tabs.currentIndex()
        mode = mode_map.get(tab_idx, 'volcano_melt')

        if mode == 'volcano_melt':
            if not self.validate_timestamps():
                QMessageBox.warning(self, "INVALID TIMESTAMPS", "Please fix timestamp errors in Volcano Melt tab before proceeding!")
                return

        self.output_file = generate_random_filename(self.input_file_a, mode)
        self.lbl_out_path.setText(os.path.basename(self.output_file))

        start_sec = parse_timestamp(self.txt_ts_start.text()) or 0.0
        end_sec = parse_timestamp(self.txt_ts_end.text()) or self.video_duration or 100.0

        options = {
            'keep_audio': self.chk_keep_audio.isChecked(),
            'input_b': self.input_file_b,
            'start_sec': start_sec,
            'end_sec': end_sec,
            'video_duration': self.video_duration or end_sec,
            'repeat_count': self.spin_s_repeat.value(),
            'frequency': self.spin_s_freq.value(),
            'corrupt_rate': self.slider_c_rate.value() / 100.0,
            'intensity': self.slider_c_intensity.value() / 100.0,
            'flow_scale': self.spin_fl_scale.value(),
            'decay': self.spin_fl_decay.value()
        }

        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("STATUS: PROCESSING...")
        self.log(f"STARTING MOSHUP: MODE '{mode}' -> {self.output_file}")

        self.worker = DatamoshWorker(mode, self.input_file_a, self.output_file, options)
        self.worker.progress_signal.connect(self.on_worker_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"STATUS: {pct}%")
        self.log(f"[{pct}%] {msg}")

    def on_worker_finished(self, out_path):
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_status.setText("STATUS: COMPLETED")
        self.log(f"SUCCESS: MOSHED VIDEO SAVED TO {out_path}")

        self.btn_open_folder.setEnabled(True)
        self.btn_open_video.setEnabled(True)

        self.preview_player.load_video(out_path)

        QMessageBox.information(
            self, "MOSHUP COMPLETE",
            f"Datamoshing process finished successfully!\n\nUnique file saved at:\n{out_path}"
        )

    def on_worker_error(self, err_msg):
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("STATUS: ERROR")
        self.log(f"ERROR: {err_msg}")
        QMessageBox.critical(self, "PROCESSING ERROR", f"An error occurred during datamoshing:\n\n{err_msg}")

    def open_output_folder(self):
        if self.output_file and os.path.exists(os.path.dirname(self.output_file)):
            folder = os.path.dirname(self.output_file)
            if sys.platform == 'win32':
                os.startfile(folder)
            else:
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', folder])

    def open_output_video(self):
        if self.output_file and os.path.exists(self.output_file):
            if sys.platform == 'win32':
                os.startfile(self.output_file)
            else:
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', self.output_file])


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MoshUpApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
