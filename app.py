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
    QGroupBox, QFrame, QMessageBox, QSplitter, QLineEdit,
    QGraphicsDropShadowEffect, QSizePolicy
)

from style import SOFT_PORCELAIN_QSS, DARK_QSS
from datamosh_engine import DatamoshEngine, get_ffmpeg_exe, parse_timestamp, format_seconds_to_timestamp
from lucide_icons import get_lucide_icon, get_lucide_pixmap


def apply_card_shadow(widget, blur=18, offset_y=4, alpha=35):
    """Applies a soft, modern claymorphic drop shadow to a card widget."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(160, 175, 200, alpha))
    widget.setGraphicsEffect(shadow)


def generate_random_filename(input_path, mode=""):
    if not input_path:
        rand_id = random.randint(1000, 9999)
        return f"moshup_output_{rand_id}.mp4"
    
    dir_name = os.path.dirname(input_path) or "."
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    rand_id = random.randint(1000, 9999)
    
    mode_str = f"_{mode}" if mode else ""
    return os.path.join(dir_name, f"{base_name}_moshup{mode_str}_{rand_id}.mp4")


class DatamoshWorker(QThread):
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
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropArea")
        self.setStyleSheet("""
            QFrame#dropArea {
                border: 2px dashed #cad5e2;
                border-radius: 16px;
                background-color: #f8fafc;
            }
            QFrame#dropArea:hover {
                background-color: #ffffff;
                border: 2px dashed #151829;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(get_lucide_pixmap("file-video", color="#475569", size=42))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_label = QLabel("Drag & drop video file here\nor click 'Select Video A'", self)
        self.text_label.setStyleSheet("font-size: 12px; font-weight: 600; color: #475569; background: transparent; margin-top: 6px;")
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
                QMessageBox.warning(self, "Unsupported Format", "Please select a valid video file (MP4, AVI, MOV, MKV)")


class VideoPreviewWidget(QWidget):
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
        layout.setSpacing(10)

        # Frame View Label
        self.display_label = QLabel(self)
        self.display_label.setObjectName("previewDisplay")
        self.display_label.setMinimumSize(320, 210)
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
        self.display_label.setText("No Video Loaded")
        layout.addWidget(self.display_label, 1)

        # Controls Row
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)

        self.btn_play = QPushButton(" Play", self)
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=16))
        self.btn_play.setFixedWidth(95)
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
            self.display_label.setText("Cannot Load Video")
            return

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.video_duration = self.total_frames / self.fps
        self.slider.setRange(0, self.total_frames - 1)
        self.current_frame = 0
        self.show_frame(0)
        self.btn_play.setText(" Play")
        self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=16))

    def toggle_play(self):
        if not self.cap or not self.cap.isOpened():
            return

        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText(" Play")
            self.btn_play.setIcon(get_lucide_icon("play", color="#1e293b", size=16))
        else:
            interval = max(10, int(1000.0 / self.fps))
            self.timer.start(interval)
            self.btn_play.setText(" Pause")
            self.btn_play.setIcon(get_lucide_icon("pause", color="#1e293b", size=16))

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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoshUp")
        self.setWindowIcon(get_lucide_icon("film", color="#151829", size=32))
        self.resize(1140, 780)
        self.setMinimumSize(960, 680)

        self.input_file_a = ""
        self.input_file_b = ""
        self.output_file = ""
        self.video_duration = 0.0
        self.worker = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(SOFT_PORCELAIN_QSS)

        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # -------------------------------------------------------------
        # 1. Left Navigation Rail (Inspired directly by the reference)
        # -------------------------------------------------------------
        sidebar_rail = QFrame(self)
        sidebar_rail.setObjectName("sidebarRail")
        sidebar_rail.setFixedWidth(56)
        sidebar_layout = QVBoxLayout(sidebar_rail)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(8)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Active App Icon (Dark Obsidian Rounded Tile)
        self.btn_logo = QPushButton(self)
        self.btn_logo.setProperty("class", "navRailBtnActive")
        self.btn_logo.setFixedSize(40, 40)
        self.btn_logo.setIcon(get_lucide_icon("film", color="#ffffff", size=20))
        self.btn_logo.setToolTip("MoshUp Studio")
        sidebar_layout.addWidget(self.btn_logo)

        # Rail Navigation Buttons
        self.btn_nav_presets = QPushButton(self)
        self.btn_nav_presets.setProperty("class", "navRailBtn")
        self.btn_nav_presets.setFixedSize(40, 40)
        self.btn_nav_presets.setIcon(get_lucide_icon("sparkles", color="#64748b", size=18))
        self.btn_nav_presets.setToolTip("Style Presets")
        self.btn_nav_presets.clicked.connect(lambda: self.combo_presets.setFocus())
        sidebar_layout.addWidget(self.btn_nav_presets)

        self.btn_nav_effects = QPushButton(self)
        self.btn_nav_effects.setProperty("class", "navRailBtn")
        self.btn_nav_effects.setFixedSize(40, 40)
        self.btn_nav_effects.setIcon(get_lucide_icon("sliders", color="#64748b", size=18))
        self.btn_nav_effects.setToolTip("Effect Tabs")
        self.btn_nav_effects.clicked.connect(lambda: self.tabs.setFocus())
        sidebar_layout.addWidget(self.btn_nav_effects)

        self.btn_nav_video = QPushButton(self)
        self.btn_nav_video.setProperty("class", "navRailBtn")
        self.btn_nav_video.setFixedSize(40, 40)
        self.btn_nav_video.setIcon(get_lucide_icon("video", color="#64748b", size=18))
        self.btn_nav_video.setToolTip("Preview Monitor")
        self.btn_nav_video.clicked.connect(lambda: self.preview_player.toggle_play() if hasattr(self, 'preview_player') else None)
        sidebar_layout.addWidget(self.btn_nav_video)

        self.btn_nav_logs = QPushButton(self)
        self.btn_nav_logs.setProperty("class", "navRailBtn")
        self.btn_nav_logs.setFixedSize(40, 40)
        self.btn_nav_logs.setIcon(get_lucide_icon("terminal", color="#64748b", size=18))
        self.btn_nav_logs.setToolTip("Console Logs")
        self.btn_nav_logs.clicked.connect(lambda: self.log_console.setFocus())
        sidebar_layout.addWidget(self.btn_nav_logs)

        sidebar_layout.addStretch()

        # Bottom info button
        self.btn_nav_info = QPushButton(self)
        self.btn_nav_info.setProperty("class", "navRailBtn")
        self.btn_nav_info.setFixedSize(40, 40)
        self.btn_nav_info.setIcon(get_lucide_icon("info", color="#64748b", size=18))
        self.btn_nav_info.setToolTip("About MoshUp Studio")
        self.btn_nav_info.clicked.connect(self.show_about_dialog)
        sidebar_layout.addWidget(self.btn_nav_info)

        apply_card_shadow(sidebar_rail, blur=14, offset_y=2, alpha=25)
        root_layout.addWidget(sidebar_rail)

        # -------------------------------------------------------------
        # 2. Main Workspace Area
        # -------------------------------------------------------------
        main_workspace = QWidget(self)
        main_layout = QVBoxLayout(main_workspace)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Header Bar
        header_bar = QHBoxLayout()
        header_bar.setContentsMargins(6, 0, 6, 2)

        lbl_floor = QLabel("MoshUp Studio", self)
        lbl_floor.setStyleSheet("font-size: 15px; color: #1e293b;")

        header_bar.addWidget(lbl_floor)
        header_bar.addStretch()

        main_layout.addLayout(header_bar)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # -------------------------------------------------------------
        # LEFT COLUMN: Input Card & Preview Monitor Card
        # -------------------------------------------------------------
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # Card: Input Video File
        input_card = QFrame(self)
        input_card.setProperty("class", "softCard")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(16, 16, 16, 16)
        input_card_layout.setSpacing(12)

        # Input Card Header
        input_hdr = QHBoxLayout()
        lbl_input_title = QLabel("Input Video File", input_card)
        lbl_input_title.setProperty("class", "sectionTitle")
        input_hdr.addWidget(lbl_input_title)
        input_hdr.addStretch()
        input_card_layout.addLayout(input_hdr)

        # Drop Area
        self.drop_area = DropAreaWidget(self)
        self.drop_area.file_dropped.connect(self.set_input_file_a)
        input_card_layout.addWidget(self.drop_area)

        # Select File A row
        file_btn_layout = QHBoxLayout()
        file_btn_layout.setSpacing(8)
        self.btn_select_a = QPushButton(" Select Video A...", self)
        self.btn_select_a.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=16))
        self.btn_select_a.clicked.connect(self.browse_input_a)

        self.lbl_file_a_path = QLabel("No file selected", self)
        self.lbl_file_a_path.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 9px;
            padding: 6px 10px;
        """)
        self.lbl_file_a_path.setWordWrap(True)

        file_btn_layout.addWidget(self.btn_select_a)
        file_btn_layout.addWidget(self.lbl_file_a_path, 1)
        input_card_layout.addLayout(file_btn_layout)

        apply_card_shadow(input_card)
        left_layout.addWidget(input_card)

        # Card: Preview Monitor
        preview_card = QFrame(self)
        preview_card.setProperty("class", "softCard")
        prev_card_layout = QVBoxLayout(preview_card)
        prev_card_layout.setContentsMargins(16, 16, 16, 16)
        prev_card_layout.setSpacing(12)

        prev_hdr = QHBoxLayout()
        lbl_prev_title = QLabel("Preview Monitor", preview_card)
        lbl_prev_title.setProperty("class", "sectionTitle")
        prev_hdr.addWidget(lbl_prev_title)
        prev_hdr.addStretch()
        prev_card_layout.addLayout(prev_hdr)

        self.preview_player = VideoPreviewWidget(self)
        prev_card_layout.addWidget(self.preview_player, 1)

        apply_card_shadow(preview_card)
        left_layout.addWidget(preview_card, 1)

        splitter.addWidget(left_widget)

        # -------------------------------------------------------------
        # RIGHT COLUMN: Presets, Modes Tabs, Output Configuration
        # -------------------------------------------------------------
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Card: Style Presets
        preset_card = QFrame(self)
        preset_card.setProperty("class", "softCard")
        preset_card_layout = QVBoxLayout(preset_card)
        preset_card_layout.setContentsMargins(16, 10, 16, 10)
        preset_card_layout.setSpacing(6)

        preset_hdr = QHBoxLayout()
        lbl_pre_title = QLabel("Style Presets", preset_card)
        lbl_pre_title.setProperty("class", "sectionTitle")
        preset_hdr.addWidget(lbl_pre_title)
        preset_hdr.addStretch()
        preset_card_layout.addLayout(preset_hdr)

        preset_row = QHBoxLayout()
        preset_row.setSpacing(10)
        lbl_preset_sel = QLabel("Choose Preset:", preset_card)
        lbl_preset_sel.setStyleSheet("font-weight: 600; color: #475569;")

        self.combo_presets = QComboBox(preset_card)
        self.combo_presets.addItems([
            "Default Configuration",
            "Volcano Melt (Keyframe Removal)",
            "Endless Motion Smear (P-Frame Repeat)",
            "Cyberpunk Bit Glitch (Data Corruption)",
            "Flow Drift (Optical Flow Drift)"
        ])
        self.combo_presets.currentIndexChanged.connect(self.apply_preset)
        preset_row.addWidget(lbl_preset_sel)
        preset_row.addWidget(self.combo_presets, 1)
        preset_card_layout.addLayout(preset_row)

        preset_card.setFixedHeight(76)
        apply_card_shadow(preset_card)
        right_layout.addWidget(preset_card)

        # Card: Datamosh Modes Tabs
        tabs_card = QFrame(self)
        tabs_card.setProperty("class", "softCard")
        tabs_card_layout = QVBoxLayout(tabs_card)
        tabs_card_layout.setContentsMargins(16, 10, 16, 10)
        tabs_card_layout.setSpacing(6)

        tabs_hdr = QHBoxLayout()
        lbl_tabs_title = QLabel("Datamosh Engine Modes", tabs_card)
        lbl_tabs_title.setProperty("class", "sectionTitle")
        tabs_hdr.addWidget(lbl_tabs_title)
        tabs_hdr.addStretch()
        tabs_card_layout.addLayout(tabs_hdr)

        self.tabs = QTabWidget(self)
        self.tabs.setIconSize(QSize(15, 15))
        self.tabs.setUsesScrollButtons(False)

        # --- Tab 1: Volcano Melt ---
        tab_volcano = QWidget()
        tab_v_layout = QVBoxLayout(tab_volcano)
        tab_v_layout.setContentsMargins(10, 8, 10, 6)
        tab_v_layout.setSpacing(6)

        lbl_v_desc = QLabel("Removes keyframes (I-Frames) in the specified time window, causing motion vectors to deform previous video frames.", tab_volcano)
        lbl_v_desc.setWordWrap(True)
        lbl_v_desc.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; margin-bottom: 4px;")
        tab_v_layout.addWidget(lbl_v_desc)

        ts_box = QGroupBox("Timestamps Range", tab_volcano)
        ts_box.setMinimumHeight(140)
        ts_box_layout = QVBoxLayout(ts_box)
        ts_box_layout.setContentsMargins(12, 14, 12, 10)
        ts_box_layout.setSpacing(6)

        ts_start_layout = QHBoxLayout()
        lbl_start = QLabel("Start Time:", tab_volcano)
        lbl_start.setStyleSheet("font-weight: 600; color: #475569;")
        self.txt_ts_start = QLineEdit(tab_volcano)
        self.txt_ts_start.setPlaceholderText("00:00")
        self.txt_ts_start.setText("00:00")
        self.txt_ts_start.textChanged.connect(self.validate_timestamps)
        
        self.btn_set_curr_start = QPushButton(" From Cursor", tab_volcano)
        self.btn_set_curr_start.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))
        self.btn_set_curr_start.clicked.connect(self.set_ts_start_from_cursor)

        ts_start_layout.addWidget(lbl_start)
        ts_start_layout.addWidget(self.txt_ts_start, 1)
        ts_start_layout.addWidget(self.btn_set_curr_start)
        ts_box_layout.addLayout(ts_start_layout)

        ts_end_layout = QHBoxLayout()
        lbl_end = QLabel("End Time:", tab_volcano)
        lbl_end.setStyleSheet("font-weight: 600; color: #475569;")
        self.txt_ts_end = QLineEdit(tab_volcano)
        self.txt_ts_end.setPlaceholderText("00:30")
        self.txt_ts_end.setText("00:30")
        self.txt_ts_end.textChanged.connect(self.validate_timestamps)

        self.btn_set_curr_end = QPushButton(" From Cursor", tab_volcano)
        self.btn_set_curr_end.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))
        self.btn_set_curr_end.clicked.connect(self.set_ts_end_from_cursor)

        ts_end_layout.addWidget(lbl_end)
        ts_end_layout.addWidget(self.txt_ts_end, 1)
        ts_end_layout.addWidget(self.btn_set_curr_end)
        ts_box_layout.addLayout(ts_end_layout)

        self.lbl_ts_validation = QLabel("Format: MM:SS (e.g. 00:05 or 01:20)", tab_volcano)
        self.lbl_ts_validation.setStyleSheet("font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5fa; border: 1px solid #dce4ef; border-radius: 8px; padding: 4px 8px; margin-top: 2px;")
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(ts_box)
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#475569"), "Volcano Melt")

        # --- Tab 2: Motion Smear ---
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)
        tab_s_layout.setContentsMargins(12, 12, 12, 12)
        tab_s_layout.setSpacing(10)

        lbl_s_desc = QLabel("Duplicates delta frames (P-Frames) to repeat motion vectors indefinitely, smearing pixels across the frame.", tab_smear)
        lbl_s_desc.setWordWrap(True)
        lbl_s_desc.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; margin-bottom: 4px;")
        tab_s_layout.addWidget(lbl_s_desc)

        s_box = QGroupBox("Smear Parameters", tab_smear)
        s_box.setMinimumHeight(120)
        s_box_layout = QVBoxLayout(s_box)
        s_box_layout.setContentsMargins(12, 14, 12, 10)
        s_box_layout.setSpacing(6)

        s_repeat_row = QHBoxLayout()
        s_repeat_lbl = QLabel("Repeat Count:", tab_smear)
        s_repeat_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.spin_s_repeat = QSpinBox(tab_smear)
        self.spin_s_repeat.setRange(2, 60)
        self.spin_s_repeat.setValue(15)
        s_repeat_row.addWidget(s_repeat_lbl)
        s_repeat_row.addWidget(self.spin_s_repeat, 1)
        s_box_layout.addLayout(s_repeat_row)

        s_freq_row = QHBoxLayout()
        s_freq_lbl = QLabel("Frequency (every N-th frame):", tab_smear)
        s_freq_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.spin_s_freq = QSpinBox(tab_smear)
        self.spin_s_freq.setRange(1, 30)
        self.spin_s_freq.setValue(5)
        s_freq_row.addWidget(s_freq_lbl)
        s_freq_row.addWidget(self.spin_s_freq, 1)
        s_box_layout.addLayout(s_freq_row)

        tab_s_layout.addWidget(s_box)
        self.tabs.addTab(tab_smear, get_lucide_icon("wind", color="#475569"), "Motion Smear")

        # --- Tab 3: Stitch Mosh ---
        tab_stitch = QWidget()
        tab_st_layout = QVBoxLayout(tab_stitch)
        tab_st_layout.setContentsMargins(12, 12, 12, 12)
        tab_st_layout.setSpacing(10)

        lbl_st_desc = QLabel("Stitches Video A and B together. Video B's initial keyframe is removed, so Video B animates Video A's static frame.", tab_stitch)
        lbl_st_desc.setWordWrap(True)
        lbl_st_desc.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; margin-bottom: 4px;")
        tab_st_layout.addWidget(lbl_st_desc)

        st_box = QGroupBox("Second Video File", tab_stitch)
        st_box.setMinimumHeight(95)
        st_box_layout = QVBoxLayout(st_box)
        st_box_layout.setContentsMargins(12, 14, 12, 10)
        st_box_layout.setSpacing(6)

        file_b_layout = QHBoxLayout()
        self.btn_select_b = QPushButton(" Select Video B...", tab_stitch)
        self.btn_select_b.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=16))
        self.btn_select_b.clicked.connect(self.browse_input_b)

        self.lbl_file_b_path = QLabel("No second file selected", tab_stitch)
        self.lbl_file_b_path.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 9px;
            padding: 6px 10px;
        """)
        file_b_layout.addWidget(self.btn_select_b)
        file_b_layout.addWidget(self.lbl_file_b_path, 1)
        st_box_layout.addLayout(file_b_layout)

        tab_st_layout.addWidget(st_box)
        self.tabs.addTab(tab_stitch, get_lucide_icon("shuffle", color="#475569"), "Stitch Mosh")

        # --- Tab 4: Cyber Glitch ---
        tab_cyber = QWidget()
        tab_c_layout = QVBoxLayout(tab_cyber)
        tab_c_layout.setContentsMargins(12, 12, 12, 12)
        tab_c_layout.setSpacing(10)

        lbl_c_desc = QLabel("Injects random byte corruptions directly into P-frame vector payloads for cyberpunk digital artifacting.", tab_cyber)
        lbl_c_desc.setWordWrap(True)
        lbl_c_desc.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; margin-bottom: 4px;")
        tab_c_layout.addWidget(lbl_c_desc)

        c_box = QGroupBox("Corruption Settings", tab_cyber)
        c_box.setMinimumHeight(135)
        c_box_layout = QVBoxLayout(c_box)
        c_box_layout.setContentsMargins(12, 14, 12, 10)
        c_box_layout.setSpacing(6)

        c_rate_lbl = QLabel("Corruption Rate (% of P-Frames):", tab_cyber)
        c_rate_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        c_box_layout.addWidget(c_rate_lbl)
        self.slider_c_rate = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_rate.setRange(1, 30)
        self.slider_c_rate.setValue(8)
        c_box_layout.addWidget(self.slider_c_rate)

        c_int_lbl = QLabel("Byte Swap Intensity:", tab_cyber)
        c_int_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        c_box_layout.addWidget(c_int_lbl)
        self.slider_c_intensity = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_intensity.setRange(1, 20)
        self.slider_c_intensity.setValue(3)
        c_box_layout.addWidget(self.slider_c_intensity)

        tab_c_layout.addWidget(c_box)
        self.tabs.addTab(tab_cyber, get_lucide_icon("cpu", color="#475569"), "Cyber Glitch")

        # --- Tab 5: Flow Drift ---
        tab_flow = QWidget()
        tab_fl_layout = QVBoxLayout(tab_flow)
        tab_fl_layout.setContentsMargins(12, 12, 12, 12)
        tab_fl_layout.setSpacing(10)

        lbl_fl_desc = QLabel("Calculates optical flow vector fields between frames and warps accumulated pixel feedback directly on screen.", tab_flow)
        lbl_fl_desc.setWordWrap(True)
        lbl_fl_desc.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500; margin-bottom: 4px;")
        tab_fl_layout.addWidget(lbl_fl_desc)

        fl_box = QGroupBox("Optical Flow Settings", tab_flow)
        fl_box.setMinimumHeight(125)
        fl_box_layout = QVBoxLayout(fl_box)
        fl_box_layout.setContentsMargins(12, 14, 12, 10)
        fl_box_layout.setSpacing(6)

        fl_scale_row = QHBoxLayout()
        fl_scale_lbl = QLabel("Flow Scale:", tab_flow)
        fl_scale_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.spin_fl_scale = QDoubleSpinBox(tab_flow)
        self.spin_fl_scale.setRange(0.5, 10.0)
        self.spin_fl_scale.setSingleStep(0.5)
        self.spin_fl_scale.setValue(2.5)
        fl_scale_row.addWidget(fl_scale_lbl)
        fl_scale_row.addWidget(self.spin_fl_scale, 1)
        fl_box_layout.addLayout(fl_scale_row)

        fl_decay_row = QHBoxLayout()
        fl_decay_lbl = QLabel("Trail Decay:", tab_flow)
        fl_decay_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.spin_fl_decay = QDoubleSpinBox(tab_flow)
        self.spin_fl_decay.setRange(0.50, 0.98)
        self.spin_fl_decay.setSingleStep(0.05)
        self.spin_fl_decay.setValue(0.85)
        fl_decay_row.addWidget(fl_decay_lbl)
        fl_decay_row.addWidget(self.spin_fl_decay, 1)
        fl_box_layout.addLayout(fl_decay_row)

        tab_fl_layout.addWidget(fl_box)
        self.tabs.addTab(tab_flow, get_lucide_icon("waves", color="#475569"), "Flow Drift")

        tabs_card_layout.addWidget(self.tabs)
        apply_card_shadow(tabs_card)
        right_layout.addWidget(tabs_card, 1)

        # Card: Output & Action Button
        opts_card = QFrame(self)
        opts_card.setProperty("class", "softCard")
        opts_card_layout = QVBoxLayout(opts_card)
        opts_card_layout.setContentsMargins(16, 12, 16, 12)
        opts_card_layout.setSpacing(8)

        opts_hdr = QHBoxLayout()
        lbl_opts_title = QLabel("Export Configuration", opts_card)
        lbl_opts_title.setProperty("class", "sectionTitle")
        opts_hdr.addWidget(lbl_opts_title)
        opts_hdr.addStretch()
        opts_card_layout.addLayout(opts_hdr)

        self.chk_keep_audio = QCheckBox("Preserve original audio track", opts_card)
        self.chk_keep_audio.setChecked(True)
        opts_card_layout.addWidget(self.chk_keep_audio)

        out_file_layout = QHBoxLayout()
        out_file_layout.setSpacing(8)
        self.btn_select_out = QPushButton(" Save As...", opts_card)
        self.btn_select_out.setIcon(get_lucide_icon("save", color="#1e293b", size=16))
        self.btn_select_out.clicked.connect(self.browse_output)

        self.lbl_out_path = QLabel("Automatic filename", opts_card)
        self.lbl_out_path.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 9px;
            padding: 6px 10px;
        """)
        out_file_layout.addWidget(self.btn_select_out)
        out_file_layout.addWidget(self.lbl_out_path, 1)
        opts_card_layout.addLayout(out_file_layout)

        # START ACTION BUTTON (Obsidian Accent button inspired by image)
        self.btn_start = QPushButton("  MOSH UP", opts_card)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setProperty("class", "btnPrimary")
        self.btn_start.setIcon(get_lucide_icon("rocket", color="#ffffff", size=20))
        self.btn_start.setIconSize(QSize(20, 20))
        self.btn_start.setFixedHeight(48)
        self.btn_start.clicked.connect(self.start_datamosh)
        opts_card_layout.addWidget(self.btn_start)

        apply_card_shadow(opts_card)
        right_layout.addWidget(opts_card)

        splitter.addWidget(right_widget)
        splitter.setSizes([460, 560])
        main_layout.addWidget(splitter, 1)

        # -------------------------------------------------------------
        # 3. Bottom Activity & Console Panel
        # -------------------------------------------------------------
        bottom_frame = QFrame(self)
        bottom_frame.setProperty("class", "softCard")
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(14, 12, 14, 12)
        bottom_layout.setSpacing(8)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)

        self.lbl_status = QLabel("Status: Idle", self)
        self.lbl_status.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 12px;")

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)

        progress_row.addWidget(self.lbl_status)
        progress_row.addWidget(self.progress_bar, 1)
        bottom_layout.addLayout(progress_row)

        self.log_console = QTextEdit(self)
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(80)
        self.log_console.setPlaceholderText("Execution log stream...")
        bottom_layout.addWidget(self.log_console)

        # Action bar buttons
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.btn_open_folder = QPushButton(" Open Output Directory", self)
        self.btn_open_folder.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=16))
        self.btn_open_folder.setProperty("class", "btnSecondary")
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        self.btn_open_folder.setEnabled(False)

        self.btn_open_video = QPushButton(" Open Moshed Video", self)
        self.btn_open_video.setIcon(get_lucide_icon("film", color="#1e293b", size=16))
        self.btn_open_video.setProperty("class", "btnSecondary")
        self.btn_open_video.clicked.connect(self.open_output_video)
        self.btn_open_video.setEnabled(False)

        action_bar.addWidget(self.btn_open_folder)
        action_bar.addWidget(self.btn_open_video)
        action_bar.addStretch()

        bottom_layout.addLayout(action_bar)
        apply_card_shadow(bottom_frame)
        main_layout.addWidget(bottom_frame)

        root_layout.addWidget(main_workspace, 1)

        self.log("Studio ready. Select an input video file to begin.")

    def log(self, text):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_console.append(timestamp + text)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "About MoshUp Studio",
            "<h3>MoshUp Studio</h3>"
            "<p>A precision video datamoshing tool built with PySide6 & FFmpeg.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Volcano Melt (Keyframe Removal by Timestamps)</li>"
            "<li>Endless Motion Smear (P-Frame Repeat)</li>"
            "<li>Stitch Mosh (Cross-Video Motion Transfer)</li>"
            "<li>Cyber Glitch (Payload Bit Corruption)</li>"
            "<li>Flow Drift (Optical Flow Vector Warping)</li>"
            "</ul>"
        )

    def update_random_output_filename(self, mode=""):
        if self.input_file_a:
            self.output_file = generate_random_filename(self.input_file_a, mode)
            self.lbl_out_path.setText(os.path.basename(self.output_file))

    def browse_input_a(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File A", "", "Video (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*.*)"
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
        self.lbl_header_badge.setText("Video Loaded")
        self.lbl_header_badge.setStyleSheet("""
            background-color: #d1fae5;
            color: #065f46;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 8px;
            border: 1px solid #a7f3d0;
        """)
        self.log(f"Loaded Video A: {file_path} (Duration: {format_seconds_to_timestamp(self.video_duration)})")

    def set_ts_start_from_cursor(self):
        curr_sec = self.preview_player.get_current_seconds()
        self.txt_ts_start.setText(format_seconds_to_timestamp(curr_sec))
        self.validate_timestamps()

    def set_ts_end_from_cursor(self):
        curr_sec = self.preview_player.get_current_seconds()
        self.txt_ts_end.setText(format_seconds_to_timestamp(curr_sec))
        self.validate_timestamps()

    def validate_timestamps(self):
        if not hasattr(self, 'lbl_ts_validation'):
            return False

        start_str = self.txt_ts_start.text()
        end_str = self.txt_ts_end.text()

        start_sec = parse_timestamp(start_str)
        end_sec = parse_timestamp(end_str)

        if start_sec is None:
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 4px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText("⚠️ Invalid start timestamp (Use MM:SS or MM:SS.s)")
            return False

        if end_sec is None:
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 4px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText("⚠️ Invalid end timestamp (Use MM:SS or MM:SS.s)")
            return False

        if start_sec >= end_sec:
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 4px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText(f"⚠️ End time ({format_seconds_to_timestamp(end_sec)}) must be greater than start time ({format_seconds_to_timestamp(start_sec)})")
            return False

        if self.video_duration > 0 and end_sec > self.video_duration:
            self.lbl_ts_validation.setStyleSheet("color: #b45309; font-weight: 700; background-color: #fef3c7; padding: 4px 10px; border-radius: 8px; border: 1px solid #fde68a;")
            self.lbl_ts_validation.setText(f"⚠️ End time ({format_seconds_to_timestamp(end_sec)}) exceeds video duration ({format_seconds_to_timestamp(self.video_duration)})")
            return False

        duration = end_sec - start_sec
        self.lbl_ts_validation.setStyleSheet("color: #0f172a; font-weight: 700; background-color: #e2ebf5; padding: 4px 10px; border-radius: 8px; border: 1px solid #c8d8ea;")
        self.lbl_ts_validation.setText(f"✓ Valid Range: {format_seconds_to_timestamp(start_sec)} -> {format_seconds_to_timestamp(end_sec)} [Duration: {duration:.1f}s]")
        return True

    def browse_input_b(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File B", "", "Video (*.mp4 *.avi *.mov *.mkv *.webm);;All Files (*.*)"
        )
        if file_path:
            self.input_file_b = file_path
            self.lbl_file_b_path.setText(os.path.basename(file_path))
            self.log(f"Loaded Video B: {file_path}")

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Datamosh Video Output", self.output_file or f"moshup_output_{random.randint(1000, 9999)}.mp4", "MP4 Video (*.mp4);;AVI Video (*.avi)"
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
            QMessageBox.warning(self, "Missing Input Video", "Please select a valid input video file (Video A) first!")
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
                QMessageBox.warning(self, "Invalid Timestamps", "Please fix timestamp errors in Volcano Melt tab before proceeding!")
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
        self.lbl_status.setText("Status: Processing...")
        self.lbl_header_badge.setText("Processing...")
        self.lbl_header_badge.setStyleSheet("""
            background-color: #fef3c7;
            color: #92400e;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 8px;
            border: 1px solid #fde68a;
        """)
        self.log(f"Starting MoshUp: mode '{mode}' -> {self.output_file}")

        self.worker = DatamoshWorker(mode, self.input_file_a, self.output_file, options)
        self.worker.progress_signal.connect(self.on_worker_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"Status: {pct}%")
        self.log(f"[{pct}%] {msg}")

    def on_worker_finished(self, out_path):
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_status.setText("Status: Completed")
        self.lbl_header_badge.setText("Complete")
        self.lbl_header_badge.setStyleSheet("""
            background-color: #d1fae5;
            color: #065f46;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 8px;
            border: 1px solid #a7f3d0;
        """)
        self.log(f"Success: Moshed video saved to {out_path}")

        self.btn_open_folder.setEnabled(True)
        self.btn_open_video.setEnabled(True)

        self.preview_player.load_video(out_path)

        QMessageBox.information(
            self, "MoshUp Complete",
            f"Datamoshing process finished successfully!\n\nNew file saved at:\n{out_path}"
        )

    def on_worker_error(self, err_msg):
        self.btn_start.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Status: Error")
        self.lbl_header_badge.setText("Error")
        self.lbl_header_badge.setStyleSheet("""
            background-color: #fee2e2;
            color: #991b1b;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 10px;
            border-radius: 8px;
            border: 1px solid #fecaca;
        """)
        self.log(f"Error: {err_msg}")
        QMessageBox.critical(self, "Processing Error", f"An error occurred during datamoshing:\n\n{err_msg}")

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
