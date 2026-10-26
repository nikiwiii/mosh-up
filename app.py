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
    QGraphicsDropShadowEffect, QSizePolicy, QStackedWidget
)

from style import SOFT_PORCELAIN_QSS, DARK_QSS
from datamosh_engine import DatamoshEngine, get_ffmpeg_exe, parse_timestamp, format_seconds_to_timestamp
from lucide_icons import get_lucide_icon, get_lucide_pixmap


def apply_card_shadow(widget, blur=18, offset_y=4, alpha=35):
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
                border-radius: 20px;
                background-color: #f8fafc;
            }
            QFrame#dropArea:hover {
                background-color: #ffffff;
                border: 2px dashed #151829;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 40, 32, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(get_lucide_pixmap("upload", color="#475569", size=54))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_title = QLabel("Przeciągnij i upuść plik wideo tutaj", self)
        self.text_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #1e293b; background: transparent;")
        self.text_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text_subtitle = QLabel("lub wybierz plik z dysku komputera\nObsługiwane formaty: MP4, MOV, MKV, AVI, WEBM", self)
        self.text_subtitle.setStyleSheet("font-size: 12px; font-weight: 500; color: #64748b; background: transparent; line-height: 1.4;")
        self.text_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_title)
        layout.addWidget(self.text_subtitle)

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
                QMessageBox.warning(self, "Nieobsługiwany format", "Wybierz prawidłowy plik wideo (MP4, AVI, MOV, MKV, WEBM)")


class VideoPreviewWidget(QWidget):
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


class MoshUpApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MoshUp Studio")
        self.setWindowIcon(get_lucide_icon("film", color="#151829", size=32))
        self.resize(1180, 820)
        self.setMinimumSize(1000, 720)

        # State
        self.input_file_a = ""
        self.input_file_b = ""
        self.output_file = ""
        self.video_duration = 0.0
        self.video_fps = 30.0
        self.video_width = 0
        self.video_height = 0
        self.video_frames = 0
        self.video_size_mb = 0.0
        self.worker = None

        self.current_step = 0
        self.max_reached_step = 0

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
        # 1. Left Navigation Rail (BOCZNA NAWIGACJA - BEZ GÓRNEGO LOGO)
        # -------------------------------------------------------------
        sidebar_rail = QFrame(self)
        sidebar_rail.setObjectName("sidebarRail")
        sidebar_rail.setFixedWidth(64)
        sidebar_layout = QVBoxLayout(sidebar_rail)
        sidebar_layout.setContentsMargins(8, 14, 8, 14)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Rail Step Buttons (Start bezpośrednio od kroków)
        self.rail_buttons = []
        rail_steps = [
            ("file-video", "1. Wczytaj wideo"),
            ("sliders", "2. Efekty i parametry"),
            ("rocket", "3. Renderowanie"),
            ("film", "4. Podgląd wideo")
        ]

        for i, (icon_name, tooltip) in enumerate(rail_steps):
            btn = QPushButton(self)
            btn.setProperty("class", "navRailBtnActive" if i == 0 else "navRailBtn")
            btn.setFixedSize(44, 44)
            btn.setIcon(get_lucide_icon(icon_name, color="#ffffff" if i == 0 else "#64748b", size=18))
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked=False, idx=i: self.go_to_step(idx))
            sidebar_layout.addWidget(btn)
            self.rail_buttons.append((btn, icon_name))

        sidebar_layout.addStretch()

        # Bottom Info Button
        self.btn_nav_info = QPushButton(self)
        self.btn_nav_info.setProperty("class", "navRailBtn")
        self.btn_nav_info.setFixedSize(44, 44)
        self.btn_nav_info.setIcon(get_lucide_icon("info", color="#64748b", size=18))
        self.btn_nav_info.setToolTip("Informacje o MoshUp")
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

        # Stacked Widget for Screens
        self.stack = QStackedWidget(self)

        # Create Pages
        self.page_upload = self.create_page_upload()
        self.page_effects = self.create_page_effects()
        self.page_render = self.create_page_render()
        self.page_preview = self.create_page_preview()

        self.stack.addWidget(self.page_upload)    # Index 0
        self.stack.addWidget(self.page_effects)   # Index 1
        self.stack.addWidget(self.page_render)    # Index 2
        self.stack.addWidget(self.page_preview)   # Index 3

        main_layout.addWidget(self.stack, 1)
        root_layout.addWidget(main_workspace, 1)

        self.update_stepper_and_rail()

    # SCREEN 1: WRZUCANIE WIDEO (Upload Video)
    def create_page_upload(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(page)
        header_card.setProperty("class", "softCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(18, 14, 18, 14)
        h_layout.setSpacing(4)

        lbl_h_title = QLabel("Krok 1: Wczytaj plik wideo", header_card)
        lbl_h_title.setProperty("class", "pageHeaderTitle")
        lbl_h_sub = QLabel("Przeciągnij i upuść plik wideo, który posłuży jako baza dla zniekształceń i efektów datamoshingu.", header_card)
        lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(lbl_h_title)
        h_layout.addWidget(lbl_h_sub)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Content Split: Empty Upload Area OR Loaded Video View
        self.upload_content_stack = QStackedWidget(page)

        # View A: Empty Drop Zone
        view_empty = QWidget()
        ve_layout = QVBoxLayout(view_empty)
        ve_layout.setContentsMargins(0, 0, 0, 0)
        ve_layout.setSpacing(14)

        drop_card = QFrame(view_empty)
        drop_card.setProperty("class", "softCard")
        dc_layout = QVBoxLayout(drop_card)
        dc_layout.setContentsMargins(20, 20, 20, 20)
        dc_layout.setSpacing(16)

        self.drop_area = DropAreaWidget(drop_card)
        self.drop_area.file_dropped.connect(self.set_input_file_a)
        dc_layout.addWidget(self.drop_area, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_browse_empty = QPushButton("  Wybierz plik wideo z dysku...", drop_card)
        self.btn_browse_empty.setProperty("class", "btnPrimary")
        self.btn_browse_empty.setIcon(get_lucide_icon("folder-open", color="#ffffff", size=17))
        self.btn_browse_empty.setFixedHeight(44)
        self.btn_browse_empty.clicked.connect(self.browse_input_a)
        btn_row.addWidget(self.btn_browse_empty)
        btn_row.addStretch()
        dc_layout.addLayout(btn_row)

        apply_card_shadow(drop_card)
        ve_layout.addWidget(drop_card, 1)
        self.upload_content_stack.addWidget(view_empty)

        # View B: Loaded State (Player + Detailed Metadata)
        view_loaded = QWidget()
        vl_layout = QHBoxLayout(view_loaded)
        vl_layout.setContentsMargins(0, 0, 0, 0)
        vl_layout.setSpacing(12)

        # Left: Source Video Player Card
        source_player_card = QFrame(view_loaded)
        source_player_card.setProperty("class", "softCard")
        spc_layout = QVBoxLayout(source_player_card)
        spc_layout.setContentsMargins(16, 16, 16, 16)
        spc_layout.setSpacing(10)

        spc_hdr = QHBoxLayout()
        lbl_spc_title = QLabel("Podgląd wideo źródłowego", source_player_card)
        lbl_spc_title.setProperty("class", "sectionTitle")
        spc_hdr.addWidget(lbl_spc_title)
        spc_hdr.addStretch()
        spc_layout.addLayout(spc_hdr)

        self.source_player = VideoPreviewWidget(source_player_card, min_height=260)
        spc_layout.addWidget(self.source_player, 1)

        apply_card_shadow(source_player_card)
        vl_layout.addWidget(source_player_card, 3)

        # Right: Video Metadata & Quick Actions
        meta_card = QFrame(view_loaded)
        meta_card.setProperty("class", "softCard")
        mc_layout = QVBoxLayout(meta_card)
        mc_layout.setContentsMargins(18, 16, 18, 16)
        mc_layout.setSpacing(12)

        lbl_mc_title = QLabel("Informacje o pliku", meta_card)
        lbl_mc_title.setProperty("class", "sectionTitle")
        mc_layout.addWidget(lbl_mc_title)

        self.lbl_source_status_badge = QLabel("✓ Plik załadowany pomyślnie", meta_card)
        self.lbl_source_status_badge.setStyleSheet("""
            background-color: #d1fae5;
            color: #065f46;
            font-size: 11.5px;
            font-weight: 700;
            padding: 5px 12px;
            border-radius: 9px;
            border: 1px solid #a7f3d0;
        """)
        mc_layout.addWidget(self.lbl_source_status_badge)

        self.lbl_file_name_val = QLabel("-", meta_card)
        self.lbl_file_name_val.setStyleSheet("font-size: 13px; font-weight: 700; color: #0f172a;")
        self.lbl_file_name_val.setWordWrap(True)

        self.lbl_file_dur_val = QLabel("-", meta_card)
        self.lbl_file_dur_val.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")

        self.lbl_file_res_val = QLabel("-", meta_card)
        self.lbl_file_res_val.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")

        self.lbl_file_fps_val = QLabel("-", meta_card)
        self.lbl_file_fps_val.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")

        self.lbl_file_size_val = QLabel("-", meta_card)
        self.lbl_file_size_val.setStyleSheet("font-size: 12px; font-weight: 600; color: #334155;")

        details_box = QGroupBox("Parametry techniczne", meta_card)
        db_layout = QVBoxLayout(details_box)
        db_layout.setContentsMargins(12, 14, 12, 12)
        db_layout.setSpacing(8)

        def make_meta_row(label, val_widget):
            row = QHBoxLayout()
            lbl = QLabel(label, details_box)
            lbl.setStyleSheet("font-weight: 600; color: #64748b; font-size: 12px;")
            lbl.setFixedWidth(110)
            row.addWidget(lbl)
            row.addWidget(val_widget, 1)
            return row

        db_layout.addLayout(make_meta_row("Nazwa pliku:", self.lbl_file_name_val))
        db_layout.addLayout(make_meta_row("Czas trwania:", self.lbl_file_dur_val))
        db_layout.addLayout(make_meta_row("Rozdzielczość:", self.lbl_file_res_val))
        db_layout.addLayout(make_meta_row("Klatkaż (FPS):", self.lbl_file_fps_val))
        db_layout.addLayout(make_meta_row("Rozmiar:", self.lbl_file_size_val))
        mc_layout.addWidget(details_box)

        mc_layout.addStretch()

        self.btn_replace_video = QPushButton("  Zmień plik wideo...", meta_card)
        self.btn_replace_video.setProperty("class", "btnSecondary")
        self.btn_replace_video.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=15))
        self.btn_replace_video.setFixedHeight(38)
        self.btn_replace_video.clicked.connect(self.browse_input_a)
        mc_layout.addWidget(self.btn_replace_video)

        apply_card_shadow(meta_card)
        vl_layout.addWidget(meta_card, 2)

        self.upload_content_stack.addWidget(view_loaded)
        layout.addWidget(self.upload_content_stack, 1)

        # Bottom Navigation Bar
        nav_card = QFrame(page)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.lbl_step1_hint = QLabel("Wybierz plik wideo, aby przejść do konfiguracji efektów.", nav_card)
        self.lbl_step1_hint.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        nc_layout.addWidget(self.lbl_step1_hint)
        nc_layout.addStretch()

        self.btn_step1_next = QPushButton("  Dalej: Wybierz efekty", nav_card)
        self.btn_step1_next.setProperty("class", "btnPrimary")
        self.btn_step1_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step1_next.setFixedHeight(38)
        self.btn_step1_next.setEnabled(False)
        self.btn_step1_next.clicked.connect(lambda: self.go_to_step(1))
        nc_layout.addWidget(self.btn_step1_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

        return page

    # SCREEN 2: WYBÓR I KONFIGURACJA EFEKTÓW (Effects & Parameters - BEZ SZYBKICH STYLI)
    def create_page_effects(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(page)
        header_card.setProperty("class", "softCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(18, 12, 18, 12)
        h_layout.setSpacing(4)

        lbl_h_title = QLabel("Krok 2: Wybór efektu i parametrów", header_card)
        lbl_h_title.setProperty("class", "pageHeaderTitle")
        lbl_h_sub = QLabel("Wybierz tryb zniekształceń klatek i dostosuj parametry algorytmu datamosh.", header_card)
        lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(lbl_h_title)
        h_layout.addWidget(lbl_h_sub)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Datamosh Modes Tabs Card (Pełna wysokość bez wyboru szybkich styli)
        tabs_card = QFrame(page)
        tabs_card.setProperty("class", "softCard")
        tabs_card_layout = QVBoxLayout(tabs_card)
        tabs_card_layout.setContentsMargins(16, 12, 16, 12)
        tabs_card_layout.setSpacing(8)

        self.tabs = QTabWidget(tabs_card)
        self.tabs.setIconSize(QSize(16, 16))
        self.tabs.setUsesScrollButtons(False)

        # --- Tab 1: Volcano Melt ---
        tab_volcano = QWidget()
        tab_v_layout = QVBoxLayout(tab_volcano)
        tab_v_layout.setContentsMargins(12, 12, 12, 10)
        tab_v_layout.setSpacing(8)

        lbl_v_desc = QLabel("Usuwa klatki kluczowe (I-Frames) w zadanym oknie czasowym. Wektory ruchu deformatują poprzedni statyczny obraz, tworząc płynne topnienie obiektów.", tab_volcano)
        lbl_v_desc.setWordWrap(True)
        lbl_v_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500; margin-bottom: 4px;")
        tab_v_layout.addWidget(lbl_v_desc)

        ts_box = QGroupBox("Przedział czasowy efektu", tab_volcano)
        ts_box_layout = QVBoxLayout(ts_box)
        ts_box_layout.setContentsMargins(14, 14, 14, 12)
        ts_box_layout.setSpacing(8)

        ts_start_layout = QHBoxLayout()
        lbl_start = QLabel("Czas początkowy (Start):", tab_volcano)
        lbl_start.setStyleSheet("font-weight: 600; color: #475569;")
        lbl_start.setFixedWidth(160)
        self.txt_ts_start = QLineEdit(tab_volcano)
        self.txt_ts_start.setPlaceholderText("00:00")
        self.txt_ts_start.setText("00:00")
        self.txt_ts_start.textChanged.connect(self.validate_timestamps)
        
        self.btn_set_curr_start = QPushButton("  Z pozycji odtwarzacza", tab_volcano)
        self.btn_set_curr_start.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))
        self.btn_set_curr_start.clicked.connect(self.set_ts_start_from_cursor)

        ts_start_layout.addWidget(lbl_start)
        ts_start_layout.addWidget(self.txt_ts_start, 1)
        ts_start_layout.addWidget(self.btn_set_curr_start)
        ts_box_layout.addLayout(ts_start_layout)

        ts_end_layout = QHBoxLayout()
        lbl_end = QLabel("Czas końcowy (Koniec):", tab_volcano)
        lbl_end.setStyleSheet("font-weight: 600; color: #475569;")
        lbl_end.setFixedWidth(160)
        self.txt_ts_end = QLineEdit(tab_volcano)
        self.txt_ts_end.setPlaceholderText("00:30")
        self.txt_ts_end.setText("00:30")
        self.txt_ts_end.textChanged.connect(self.validate_timestamps)

        self.btn_set_curr_end = QPushButton("  Z pozycji odtwarzacza", tab_volcano)
        self.btn_set_curr_end.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))
        self.btn_set_curr_end.clicked.connect(self.set_ts_end_from_cursor)

        ts_end_layout.addWidget(lbl_end)
        ts_end_layout.addWidget(self.txt_ts_end, 1)
        ts_end_layout.addWidget(self.btn_set_curr_end)
        ts_box_layout.addLayout(ts_end_layout)

        self.lbl_ts_validation = QLabel("Format: MM:SS (np. 00:05 lub 01:20)", tab_volcano)
        self.lbl_ts_validation.setStyleSheet("font-size: 11.5px; font-weight: 600; color: #64748b; background-color: #f1f5fa; border: 1px solid #dce4ef; border-radius: 8px; padding: 5px 10px; margin-top: 2px;")
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(ts_box)
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#475569"), "Volcano Melt")

        # --- Tab 2: Motion Smear ---
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)
        tab_s_layout.setContentsMargins(12, 12, 12, 10)
        tab_s_layout.setSpacing(8)

        lbl_s_desc = QLabel("Duplikuje klatki delta (P-Frames), powodując wielokrotne powtarzanie wektorów ruchu i charakterystyczne smugi pikseli.", tab_smear)
        lbl_s_desc.setWordWrap(True)
        lbl_s_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500; margin-bottom: 4px;")
        tab_s_layout.addWidget(lbl_s_desc)

        s_box = QGroupBox("Parametry rozmycia wektorów", tab_smear)
        s_box_layout = QVBoxLayout(s_box)
        s_box_layout.setContentsMargins(14, 14, 14, 12)
        s_box_layout.setSpacing(8)

        s_repeat_row = QHBoxLayout()
        s_repeat_lbl = QLabel("Liczba powtórzeń (Repeat Count):", tab_smear)
        s_repeat_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        s_repeat_lbl.setFixedWidth(210)
        self.spin_s_repeat = QSpinBox(tab_smear)
        self.spin_s_repeat.setRange(2, 60)
        self.spin_s_repeat.setValue(15)
        s_repeat_row.addWidget(s_repeat_lbl)
        s_repeat_row.addWidget(self.spin_s_repeat, 1)
        s_box_layout.addLayout(s_repeat_row)

        s_freq_row = QHBoxLayout()
        s_freq_lbl = QLabel("Częstotliwość (co N-tą klatkę):", tab_smear)
        s_freq_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        s_freq_lbl.setFixedWidth(210)
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
        tab_st_layout.setContentsMargins(12, 12, 12, 10)
        tab_st_layout.setSpacing(8)

        lbl_st_desc = QLabel("Łączy dwa pliki wideo. Początkowa klatka kluczowa wideo B zostaje wycięta, przez co ruch z drugiego klipu ożywia ostatnią klatkę pierwszego wideo.", tab_stitch)
        lbl_st_desc.setWordWrap(True)
        lbl_st_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500; margin-bottom: 4px;")
        tab_st_layout.addWidget(lbl_st_desc)

        st_box = QGroupBox("Drugi plik wideo (Wideo B)", tab_stitch)
        st_box_layout = QVBoxLayout(st_box)
        st_box_layout.setContentsMargins(14, 14, 14, 12)
        st_box_layout.setSpacing(8)

        file_b_layout = QHBoxLayout()
        self.btn_select_b = QPushButton("  Wybierz wideo B...", tab_stitch)
        self.btn_select_b.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=15))
        self.btn_select_b.clicked.connect(self.browse_input_b)

        self.lbl_file_b_path = QLabel("Nie wybrano drugiego pliku wideo", tab_stitch)
        self.lbl_file_b_path.setStyleSheet("""
            font-size: 11.5px;
            font-weight: 600;
            color: #64748b;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 9px;
            padding: 6px 12px;
        """)
        file_b_layout.addWidget(self.btn_select_b)
        file_b_layout.addWidget(self.lbl_file_b_path, 1)
        st_box_layout.addLayout(file_b_layout)

        tab_st_layout.addWidget(st_box)
        self.tabs.addTab(tab_stitch, get_lucide_icon("shuffle", color="#475569"), "Stitch Mosh")

        # --- Tab 4: Cyber Glitch ---
        tab_cyber = QWidget()
        tab_c_layout = QVBoxLayout(tab_cyber)
        tab_c_layout.setContentsMargins(12, 12, 12, 10)
        tab_c_layout.setSpacing(8)

        lbl_c_desc = QLabel("Wstrzykuje losowe uszkodzenia bajtów bezpośrednio do wektorów klatek różnicowych (P-Frames), generując cyfrowe zakłócenia w stylu glitch-art.", tab_cyber)
        lbl_c_desc.setWordWrap(True)
        lbl_c_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500; margin-bottom: 4px;")
        tab_c_layout.addWidget(lbl_c_desc)

        c_box = QGroupBox("Ustawienia uszkodzeń bitowych", tab_cyber)
        c_box_layout = QVBoxLayout(c_box)
        c_box_layout.setContentsMargins(14, 14, 14, 12)
        c_box_layout.setSpacing(8)

        c_rate_lbl = QLabel("Wskaźnik korupcji (% klatek P):", tab_cyber)
        c_rate_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        c_box_layout.addWidget(c_rate_lbl)
        self.slider_c_rate = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_rate.setRange(1, 30)
        self.slider_c_rate.setValue(8)
        c_box_layout.addWidget(self.slider_c_rate)

        c_int_lbl = QLabel("Intensywność zamiany bajtów:", tab_cyber)
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
        tab_fl_layout.setContentsMargins(12, 12, 12, 10)
        tab_fl_layout.setSpacing(8)

        lbl_fl_desc = QLabel("Oblicza wektory przepływu optycznego pomiędzy klatkami i deformuje zakumulowane piksele na ekranie w organiczny, płynny sposób.", tab_flow)
        lbl_fl_desc.setWordWrap(True)
        lbl_fl_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500; margin-bottom: 4px;")
        tab_fl_layout.addWidget(lbl_fl_desc)

        fl_box = QGroupBox("Parametry przepływu optycznego (Farneback)", tab_flow)
        fl_box_layout = QVBoxLayout(fl_box)
        fl_box_layout.setContentsMargins(14, 14, 14, 12)
        fl_box_layout.setSpacing(8)

        fl_scale_row = QHBoxLayout()
        fl_scale_lbl = QLabel("Skala przepływu (Flow Scale):", tab_flow)
        fl_scale_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        fl_scale_lbl.setFixedWidth(210)
        self.spin_fl_scale = QDoubleSpinBox(tab_flow)
        self.spin_fl_scale.setRange(0.5, 10.0)
        self.spin_fl_scale.setSingleStep(0.5)
        self.spin_fl_scale.setValue(2.5)
        fl_scale_row.addWidget(fl_scale_lbl)
        fl_scale_row.addWidget(self.spin_fl_scale, 1)
        fl_box_layout.addLayout(fl_scale_row)

        fl_decay_row = QHBoxLayout()
        fl_decay_lbl = QLabel("Zanikanie śladu (Trail Decay):", tab_flow)
        fl_decay_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        fl_decay_lbl.setFixedWidth(210)
        self.spin_fl_decay = QDoubleSpinBox(tab_flow)
        self.spin_fl_decay.setRange(0.50, 0.98)
        self.spin_fl_decay.setSingleStep(0.05)
        self.spin_fl_decay.setValue(0.85)
        fl_decay_row.addWidget(fl_decay_lbl)
        fl_decay_row.addWidget(self.spin_fl_decay, 1)
        fl_box_layout.addLayout(fl_decay_row)

        tab_fl_layout.addWidget(fl_box)
        self.tabs.addTab(tab_flow, get_lucide_icon("waves", color="#475569"), "Flow Drift")

        tabs_card_layout.addWidget(self.tabs, 1)
        apply_card_shadow(tabs_card)
        layout.addWidget(tabs_card, 1)

        # Export & Audio Configuration Card
        opts_card = QFrame(page)
        opts_card.setProperty("class", "softCard")
        opts_card_layout = QVBoxLayout(opts_card)
        opts_card_layout.setContentsMargins(18, 12, 18, 12)
        opts_card_layout.setSpacing(8)

        opts_hdr = QHBoxLayout()
        lbl_opts_title = QLabel("Ustawienia eksportu", opts_card)
        lbl_opts_title.setProperty("class", "sectionTitle")
        opts_hdr.addWidget(lbl_opts_title)
        opts_hdr.addStretch()
        opts_card_layout.addLayout(opts_hdr)

        self.chk_keep_audio = QCheckBox("Zachowaj oryginalną ścieżkę dźwiękową wideo", opts_card)
        self.chk_keep_audio.setChecked(True)
        opts_card_layout.addWidget(self.chk_keep_audio)

        out_file_layout = QHBoxLayout()
        out_file_layout.setSpacing(8)
        self.btn_select_out = QPushButton("  Zmień nazwę/folder zapisu...", opts_card)
        self.btn_select_out.setIcon(get_lucide_icon("save", color="#1e293b", size=15))
        self.btn_select_out.clicked.connect(self.browse_output)

        self.lbl_out_path = QLabel("Automatyczna nazwa pliku wyjściowego", opts_card)
        self.lbl_out_path.setStyleSheet("""
            font-size: 11.5px;
            font-weight: 600;
            color: #64748b;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 9px;
            padding: 6px 12px;
        """)
        out_file_layout.addWidget(self.btn_select_out)
        out_file_layout.addWidget(self.lbl_out_path, 1)
        opts_card_layout.addLayout(out_file_layout)

        apply_card_shadow(opts_card)
        layout.addWidget(opts_card)

        # Bottom Navigation Bar
        nav_card = QFrame(page)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step2_back = QPushButton("  Wróć do wyboru wideo", nav_card)
        self.btn_step2_back.setProperty("class", "btnSecondary")
        self.btn_step2_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step2_back.setFixedHeight(38)
        self.btn_step2_back.clicked.connect(lambda: self.go_to_step(0))
        nc_layout.addWidget(self.btn_step2_back)

        nc_layout.addStretch()

        self.btn_step2_next = QPushButton("  Dalej: Eksport i Renderowanie", nav_card)
        self.btn_step2_next.setProperty("class", "btnPrimary")
        self.btn_step2_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step2_next.setFixedHeight(38)
        self.btn_step2_next.clicked.connect(lambda: self.go_to_step(2))
        nc_layout.addWidget(self.btn_step2_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

        return page

    # SCREEN 3: EKSPORT I RENDEROWANIE (Processing & Render)
    def create_page_render(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(page)
        header_card.setProperty("class", "softCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(18, 12, 18, 12)
        h_layout.setSpacing(4)

        lbl_h_title = QLabel("Krok 3: Eksport i Renderowanie", header_card)
        lbl_h_title.setProperty("class", "pageHeaderTitle")
        lbl_h_sub = QLabel("Szczegółowe zestawienie parametrów renderowania oraz uruchomienie silnika Datamosh.", header_card)
        lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(lbl_h_title)
        h_layout.addWidget(lbl_h_sub)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # PRIORITY SUMMARY CARD (Podsumowanie jako priorytet tego kroku)
        self.summary_card = QFrame(page)
        self.summary_card.setProperty("class", "softCard")
        sum_layout = QVBoxLayout(self.summary_card)
        sum_layout.setContentsMargins(20, 16, 20, 16)
        sum_layout.setSpacing(12)

        # Summary Header (bez małego kafelka nazwy wybranego trybu)
        sum_hdr = QHBoxLayout()
        lbl_sum_hdr = QLabel("Podsumowanie zadania renderingu", self.summary_card)
        lbl_sum_hdr.setProperty("class", "sectionTitle")
        sum_hdr.addWidget(lbl_sum_hdr)
        sum_hdr.addStretch()
        sum_layout.addLayout(sum_hdr)

        # 4 Detailed Grid Tiles (2x2 layout)
        grid_layout = QVBoxLayout()
        grid_layout.setSpacing(10)

        row1 = QHBoxLayout()
        row1.setSpacing(12)

        # Tile 1: Source Video
        tile_src = QFrame(self.summary_card)
        tile_src.setProperty("class", "insetCard")
        ts_layout = QVBoxLayout(tile_src)
        ts_layout.setContentsMargins(14, 12, 14, 12)
        ts_layout.setSpacing(4)

        th_src = QHBoxLayout()
        icon_src = QLabel(tile_src)
        icon_src.setPixmap(get_lucide_pixmap("file-video", color="#475569", size=18))
        lbl_src_title = QLabel("1. WIDEO ŹRÓDŁOWE", tile_src)
        lbl_src_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_src.addWidget(icon_src)
        th_src.addWidget(lbl_src_title)
        th_src.addStretch()
        ts_layout.addLayout(th_src)

        self.lbl_sum_src_name = QLabel("Nie wybrano pliku", tile_src)
        self.lbl_sum_src_name.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_src_name.setWordWrap(True)
        self.lbl_sum_src_meta1 = QLabel("Rozdzielczość: - • Klatkaż: -", tile_src)
        self.lbl_sum_src_meta1.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_src_meta2 = QLabel("Czas trwania: - • Rozmiar: -", tile_src)
        self.lbl_sum_src_meta2.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")

        ts_layout.addWidget(self.lbl_sum_src_name)
        ts_layout.addWidget(self.lbl_sum_src_meta1)
        ts_layout.addWidget(self.lbl_sum_src_meta2)
        row1.addWidget(tile_src, 1)

        # Tile 2: Effect Mode & Parameters
        tile_mode = QFrame(self.summary_card)
        tile_mode.setProperty("class", "insetCard")
        tm_layout = QVBoxLayout(tile_mode)
        tm_layout.setContentsMargins(14, 12, 14, 12)
        tm_layout.setSpacing(4)

        th_mode = QHBoxLayout()
        icon_mode = QLabel(tile_mode)
        icon_mode.setPixmap(get_lucide_pixmap("sliders", color="#475569", size=18))
        lbl_mode_title = QLabel("2. PARAMETRY EFEKTU", tile_mode)
        lbl_mode_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_mode.addWidget(icon_mode)
        th_mode.addWidget(lbl_mode_title)
        th_mode.addStretch()
        tm_layout.addLayout(th_mode)

        self.lbl_sum_mode_name = QLabel("Volcano Melt", tile_mode)
        self.lbl_sum_mode_name.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_param1 = QLabel("Zakres: 00:00 - 00:30", tile_mode)
        self.lbl_sum_param1.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_param2 = QLabel("Usuwa klatki I-Frame z zachowaniem wektorów ruchu", tile_mode)
        self.lbl_sum_param2.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")

        tm_layout.addWidget(self.lbl_sum_mode_name)
        tm_layout.addWidget(self.lbl_sum_param1)
        tm_layout.addWidget(self.lbl_sum_param2)
        row1.addWidget(tile_mode, 1)

        grid_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        # Tile 3: Audio (Bez nadmiernych opisów)
        tile_audio = QFrame(self.summary_card)
        tile_audio.setProperty("class", "insetCard")
        ta_layout = QVBoxLayout(tile_audio)
        ta_layout.setContentsMargins(14, 12, 14, 12)
        ta_layout.setSpacing(6)

        th_audio = QHBoxLayout()
        icon_audio = QLabel(tile_audio)
        icon_audio.setPixmap(get_lucide_pixmap("music", color="#475569", size=18))
        lbl_audio_title = QLabel("3. ŚCIEŻKA AUDIO", tile_audio)
        lbl_audio_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_audio.addWidget(icon_audio)
        th_audio.addWidget(lbl_audio_title)
        th_audio.addStretch()
        ta_layout.addLayout(th_audio)

        self.lbl_sum_audio_status = QLabel("Ścieżka audio: Zachowana (Oryginał)", tile_audio)
        self.lbl_sum_audio_status.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")

        ta_layout.addWidget(self.lbl_sum_audio_status)
        ta_layout.addStretch()
        row2.addWidget(tile_audio, 1)

        # Tile 4: Output File & Directory
        tile_out = QFrame(self.summary_card)
        tile_out.setProperty("class", "insetCard")
        to_layout = QVBoxLayout(tile_out)
        to_layout.setContentsMargins(14, 12, 14, 12)
        to_layout.setSpacing(4)

        th_out = QHBoxLayout()
        icon_out = QLabel(tile_out)
        icon_out.setPixmap(get_lucide_pixmap("save", color="#475569", size=18))
        lbl_out_title = QLabel("4. PLIK WYJŚCIOWY", tile_out)
        lbl_out_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_out.addWidget(icon_out)
        th_out.addWidget(lbl_out_title)
        th_out.addStretch()
        to_layout.addLayout(th_out)

        self.lbl_sum_output_file = QLabel("moshup_output.mp4", tile_out)
        self.lbl_sum_output_file.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_output_file.setWordWrap(True)
        self.lbl_sum_output_dir = QLabel("Katalog: -", tile_out)
        self.lbl_sum_output_dir.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_output_dir.setWordWrap(True)

        to_layout.addWidget(self.lbl_sum_output_file)
        to_layout.addWidget(self.lbl_sum_output_dir)
        to_layout.addStretch()
        row2.addWidget(tile_out, 1)

        grid_layout.addLayout(row2)
        sum_layout.addLayout(grid_layout)

        apply_card_shadow(self.summary_card)
        layout.addWidget(self.summary_card, 1)  # Stretch=1: Podsumowanie jest priorytetem!

        # Action & Progress Card
        action_card = QFrame(page)
        action_card.setProperty("class", "softCard")
        ac_layout = QVBoxLayout(action_card)
        ac_layout.setContentsMargins(18, 14, 18, 14)
        ac_layout.setSpacing(10)

        # BIG START BUTTON
        self.btn_start = QPushButton("  ROZPOCZNIJ MOSHING", action_card)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setProperty("class", "btnPrimary")
        self.btn_start.setIcon(get_lucide_icon("rocket", color="#ffffff", size=20))
        self.btn_start.setIconSize(QSize(20, 20))
        self.btn_start.setFixedHeight(46)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_start.clicked.connect(self.start_datamosh)
        ac_layout.addWidget(self.btn_start)

        # Progress Row
        progress_row = QHBoxLayout()
        progress_row.setSpacing(12)

        self.lbl_status = QLabel("Status: Gotowy do uruchomienia", action_card)
        self.lbl_status.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 12.5px;")

        self.progress_bar = QProgressBar(action_card)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)

        progress_row.addWidget(self.lbl_status)
        progress_row.addWidget(self.progress_bar, 1)
        ac_layout.addLayout(progress_row)

        apply_card_shadow(action_card)
        layout.addWidget(action_card, 0)

        # Compact Console Card (Zmieniono nazwę na "Konsola")
        log_card = QFrame(page)
        log_card.setProperty("class", "softCard")
        lc_layout = QVBoxLayout(log_card)
        lc_layout.setContentsMargins(16, 8, 16, 10)
        lc_layout.setSpacing(6)

        log_hdr = QHBoxLayout()
        icon_log = QLabel(log_card)
        icon_log.setPixmap(get_lucide_pixmap("terminal", color="#64748b", size=15))
        lbl_log_title = QLabel("Konsola", log_card)
        lbl_log_title.setStyleSheet("font-size: 11.5px; font-weight: 700; color: #64748b;")
        log_hdr.addWidget(icon_log)
        log_hdr.addWidget(lbl_log_title)
        log_hdr.addStretch()
        lc_layout.addLayout(log_hdr)

        self.log_console = QTextEdit(log_card)
        self.log_console.setReadOnly(True)
        self.log_console.setFixedHeight(75)
        self.log_console.setPlaceholderText("Strumień logów z silnika FFmpeg...")
        lc_layout.addWidget(self.log_console)

        apply_card_shadow(log_card)
        layout.addWidget(log_card, 0)

        # Bottom Navigation Bar
        nav_card = QFrame(page)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step3_back = QPushButton("  Wróć do parametrów", nav_card)
        self.btn_step3_back.setProperty("class", "btnSecondary")
        self.btn_step3_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step3_back.setFixedHeight(38)
        self.btn_step3_back.clicked.connect(lambda: self.go_to_step(1))
        nc_layout.addWidget(self.btn_step3_back)

        nc_layout.addStretch()

        self.btn_step3_next = QPushButton("  Dalej: Podgląd gotowego wideo", nav_card)
        self.btn_step3_next.setProperty("class", "btnPrimary")
        self.btn_step3_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step3_next.setFixedHeight(38)
        self.btn_step3_next.setEnabled(False)
        self.btn_step3_next.clicked.connect(lambda: self.go_to_step(3))
        nc_layout.addWidget(self.btn_step3_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

        return page

    # SCREEN 4: PODGLĄD WIDEO (Preview & Final Result)
    def create_page_preview(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(page)
        header_card.setProperty("class", "softCard")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(18, 12, 18, 12)
        h_layout.setSpacing(12)

        titles_vbox = QVBoxLayout()
        titles_vbox.setSpacing(4)
        lbl_h_title = QLabel("Krok 4: Podgląd gotowego wideo", header_card)
        lbl_h_title.setProperty("class", "pageHeaderTitle")
        lbl_h_sub = QLabel("Odtwórz wyrenderowane wideo, porównaj je z oryginałem lub otwórz plik na dysku.", header_card)
        lbl_h_sub.setProperty("class", "pageHeaderSubtitle")
        titles_vbox.addWidget(lbl_h_title)
        titles_vbox.addWidget(lbl_h_sub)
        h_layout.addLayout(titles_vbox, 1)

        # Comparison Toggle Buttons
        comp_group = QHBoxLayout()
        comp_group.setSpacing(6)

        self.btn_view_result = QPushButton("  Efekt", header_card)
        self.btn_view_result.setProperty("class", "btnPrimary")
        self.btn_view_result.setIcon(get_lucide_icon("sparkles", color="#ffffff", size=15))
        self.btn_view_result.setFixedHeight(36)
        self.btn_view_result.clicked.connect(self.show_preview_result)

        self.btn_view_source = QPushButton("  Oryginał", header_card)
        self.btn_view_source.setProperty("class", "btnSecondary")
        self.btn_view_source.setIcon(get_lucide_icon("film", color="#1e293b", size=15))
        self.btn_view_source.setFixedHeight(36)
        self.btn_view_source.clicked.connect(self.show_preview_source)

        comp_group.addWidget(self.btn_view_result)
        comp_group.addWidget(self.btn_view_source)
        h_layout.addLayout(comp_group)

        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Large Video Player Card
        player_card = QFrame(page)
        player_card.setProperty("class", "softCard")
        pc_layout = QVBoxLayout(player_card)
        pc_layout.setContentsMargins(18, 16, 18, 16)
        pc_layout.setSpacing(10)

        self.preview_player = VideoPreviewWidget(player_card, min_height=320)
        pc_layout.addWidget(self.preview_player, 1)

        apply_card_shadow(player_card)
        layout.addWidget(player_card, 1)

        # Actions Card
        actions_card = QFrame(page)
        actions_card.setProperty("class", "softCard")
        ac_layout = QVBoxLayout(actions_card)
        ac_layout.setContentsMargins(18, 12, 18, 12)
        ac_layout.setSpacing(10)

        # File path label
        file_row = QHBoxLayout()
        lbl_file_tag = QLabel("Lokalizacja pliku:", actions_card)
        lbl_file_tag.setStyleSheet("font-weight: 700; color: #475569; font-size: 12px;")
        lbl_file_tag.setFixedWidth(120)

        self.lbl_result_path = QLabel("Brak wygenerowanego pliku", actions_card)
        self.lbl_result_path.setStyleSheet("""
            font-size: 11.5px;
            font-weight: 600;
            color: #0f172a;
            background-color: #f1f5fa;
            border: 1px solid #dce4ef;
            border-radius: 8px;
            padding: 6px 12px;
        """)
        self.lbl_result_path.setWordWrap(True)

        file_row.addWidget(lbl_file_tag)
        file_row.addWidget(self.lbl_result_path, 1)
        ac_layout.addLayout(file_row)

        # Action Buttons Row
        action_btn_row = QHBoxLayout()
        action_btn_row.setSpacing(10)

        self.btn_open_video = QPushButton("  Odtwórz w odtwarzaczu systemowym", actions_card)
        self.btn_open_video.setProperty("class", "btnPrimary")
        self.btn_open_video.setIcon(get_lucide_icon("play", color="#ffffff", size=15))
        self.btn_open_video.setFixedHeight(38)
        self.btn_open_video.clicked.connect(self.open_output_video)

        self.btn_open_folder = QPushButton("  Otwórz folder z plikiem", actions_card)
        self.btn_open_folder.setProperty("class", "btnSecondary")
        self.btn_open_folder.setIcon(get_lucide_icon("folder-open", color="#334155", size=15))
        self.btn_open_folder.setFixedHeight(38)
        self.btn_open_folder.clicked.connect(self.open_output_folder)

        self.btn_tweak_params = QPushButton("  Zmień parametry", actions_card)
        self.btn_tweak_params.setProperty("class", "btnSecondary")
        self.btn_tweak_params.setIcon(get_lucide_icon("sliders", color="#334155", size=15))
        self.btn_tweak_params.setFixedHeight(38)
        self.btn_tweak_params.clicked.connect(lambda: self.go_to_step(1))

        self.btn_new_project = QPushButton("  Wczytaj nowe wideo", actions_card)
        self.btn_new_project.setProperty("class", "btnSecondary")
        self.btn_new_project.setIcon(get_lucide_icon("rotate-ccw", color="#334155", size=15))
        self.btn_new_project.setFixedHeight(38)
        self.btn_new_project.clicked.connect(self.reset_new_project)

        action_btn_row.addWidget(self.btn_open_video)
        action_btn_row.addWidget(self.btn_open_folder)
        action_btn_row.addWidget(self.btn_tweak_params)
        action_btn_row.addWidget(self.btn_new_project)
        ac_layout.addLayout(action_btn_row)

        apply_card_shadow(actions_card)
        layout.addWidget(actions_card)

        # Bottom Navigation Bar
        nav_card = QFrame(page)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step4_back = QPushButton("  Wróć do renderowania", nav_card)
        self.btn_step4_back.setProperty("class", "btnSecondary")
        self.btn_step4_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step4_back.setFixedHeight(38)
        self.btn_step4_back.clicked.connect(lambda: self.go_to_step(2))
        nc_layout.addWidget(self.btn_step4_back)

        nc_layout.addStretch()

        self.btn_step4_restart = QPushButton("  Nowy projekt", nav_card)
        self.btn_step4_restart.setProperty("class", "btnSecondary")
        self.btn_step4_restart.setIcon(get_lucide_icon("rotate-ccw", color="#334155", size=15))
        self.btn_step4_restart.setFixedHeight(38)
        self.btn_step4_restart.clicked.connect(self.reset_new_project)
        nc_layout.addWidget(self.btn_step4_restart)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

        return page

    # STEPPER & WORKFLOW NAVIGATION
    def go_to_step(self, step_idx):
        if step_idx == self.current_step:
            return

        # Validation checks
        if step_idx in [1, 2] and not self.input_file_a:
            QMessageBox.warning(self, "Brak wideo", "Wczytaj najpierw plik wideo w kroku 1!")
            return

        if step_idx == 3 and (not self.output_file or not os.path.exists(self.output_file)):
            QMessageBox.warning(self, "Brak wygenerowanego pliku", "Najpierw wyrenderuj wideo w kroku 3, aby zobaczyć podgląd!")
            return

        # Pause any playing videos before switching
        if hasattr(self, 'source_player'):
            self.source_player.pause()
        if hasattr(self, 'preview_player'):
            self.preview_player.pause()

        # Update step-specific data
        if step_idx == 2:
            self.update_summary_card()
        elif step_idx == 3:
            self.show_preview_result()

        self.current_step = step_idx
        self.max_reached_step = max(self.max_reached_step, step_idx)
        self.stack.setCurrentIndex(step_idx)
        self.update_stepper_and_rail()

    def update_stepper_and_rail(self):
        # Update Left Rail buttons
        for i, (btn, icon_name) in enumerate(self.rail_buttons):
            if i == self.current_step:
                btn.setProperty("class", "navRailBtnActive")
                btn.setIcon(get_lucide_icon(icon_name, color="#ffffff", size=18))
            else:
                btn.setProperty("class", "navRailBtn")
                btn.setIcon(get_lucide_icon(icon_name, color="#64748b", size=18))

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def update_summary_card(self):
        # 1. Source Video Tile
        if self.input_file_a:
            base = os.path.basename(self.input_file_a)
            dur_str = format_seconds_to_timestamp(self.video_duration)
            self.lbl_sum_src_name.setText(base)
            self.lbl_sum_src_meta1.setText(f"Rozdzielczość: {self.video_width} × {self.video_height} px • Klatkaż: {self.video_fps:.2f} fps")
            self.lbl_sum_src_meta2.setText(f"Czas trwania: {dur_str} ({self.video_duration:.1f} s) • Rozmiar: {self.video_size_mb:.2f} MB")
        else:
            self.lbl_sum_src_name.setText("Brak wybranego pliku")
            self.lbl_sum_src_meta1.setText("Rozdzielczość: - • Klatkaż: -")
            self.lbl_sum_src_meta2.setText("Czas trwania: - • Rozmiar: -")

        # 2. Chosen Mode Tile
        tab_idx = self.tabs.currentIndex()
        if tab_idx == 0:
            self.lbl_sum_mode_name.setText("Volcano Melt (Usuwanie klatek kluczowych)")
            self.lbl_sum_param1.setText(f"Przedział czasowy: {self.txt_ts_start.text()} - {self.txt_ts_end.text()}")
            self.lbl_sum_param2.setText("Usuwa klatki I-Frame w wybranym oknie czasowym")
        elif tab_idx == 1:
            self.lbl_sum_mode_name.setText("Motion Smear (Rozmazywanie wektorów)")
            self.lbl_sum_param1.setText(f"Powtórzenia: {self.spin_s_repeat.value()}x • Częstotliwość: co {self.spin_s_freq.value()} klatki")
            self.lbl_sum_param2.setText("Wielokrotna replikacja klatek delta (P-Frames)")
        elif tab_idx == 2:
            self.lbl_sum_mode_name.setText("Stitch Mosh (Łączenie dwóch wideo)")
            name_b = os.path.basename(self.input_file_b) if self.input_file_b else "Brak wybranego pliku B"
            self.lbl_sum_param1.setText(f"Drugi plik: {name_b}")
            self.lbl_sum_param2.setText("Ruch z pliku B ożywia statyczną klatkę z pliku A")
        elif tab_idx == 3:
            self.lbl_sum_mode_name.setText("Cyber Glitch (Cyfrowa korupcja bitów)")
            self.lbl_sum_param1.setText(f"Wskaźnik uszkodzeń: {self.slider_c_rate.value()}% klatek P")
            self.lbl_sum_param2.setText(f"Intensywność zamiany bajtów: poziom {self.slider_c_intensity.value()}")
        else:
            self.lbl_sum_mode_name.setText("Flow Drift (Przepływ optyczny Farneback)")
            self.lbl_sum_param1.setText(f"Skala przepływu: {self.spin_fl_scale.value():.1f} • Wygaszanie śladu: {self.spin_fl_decay.value():.2f}")
            self.lbl_sum_param2.setText("Dynamiczna deformacja pola wektorów na ekranie")

        # 3. Audio Tile (Bez nadmiernych opisów)
        if self.chk_keep_audio.isChecked():
            self.lbl_sum_audio_status.setText("Ścieżka audio: Zachowana (Oryginał)")
        else:
            self.lbl_sum_audio_status.setText("Ścieżka audio: Wyciszona (Brak audio)")

        # 4. Output File Tile
        mode_keys = ['volcano_melt', 'motion_smear', 'stitch_mosh', 'cyber_glitch', 'flow_drift']
        if not self.output_file:
            self.output_file = generate_random_filename(self.input_file_a, mode_keys[tab_idx])

        self.lbl_sum_output_file.setText(os.path.basename(self.output_file))
        dir_name = os.path.dirname(self.output_file) or "."
        self.lbl_sum_output_dir.setText(f"Folder: {dir_name}")

    # LOGIC, EVENTS & WORKERS
    def log(self, text):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_console.append(timestamp + text)

    def show_about_dialog(self):
        QMessageBox.about(
            self,
            "O programie MoshUp Studio",
            "<h3>MoshUp Studio</h3>"
            "<p>Nowoczesne studio do zaawansowanego zniekształcania wideo (Datamoshing) oparte na PySide6 i FFmpeg.</p>"
            "<p><b>Tryby zniekształceń:</b></p>"
            "<ul>"
            "<li><b>Volcano Melt</b>: Usuwanie klatek kluczowych (I-Frames) w zadanym oknie czasowym</li>"
            "<li><b>Endless Motion Smear</b>: Powielanie klatek delta (P-Frames)</li>"
            "<li><b>Stitch Mosh</b>: Przenoszenie ruchu z drugiego klipu (Video B) na klatkę z Video A</li>"
            "<li><b>Cyber Glitch</b>: Bezpośrednie uszkadzanie bitów wektorów ruchu</li>"
            "<li><b>Flow Drift</b>: Organiczny dryf pikseli obliczany metodą przepływu optycznego</li>"
            "</ul>"
        )

    def browse_input_a(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik wideo A", "", "Pliki wideo (*.mp4 *.avi *.mov *.mkv *.webm);;Wszystkie pliki (*.*)"
        )
        if file_path:
            self.set_input_file_a(file_path)

    def set_input_file_a(self, file_path):
        if not file_path or not os.path.exists(file_path):
            return

        self.input_file_a = file_path

        # Gather video properties via OpenCV
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            self.video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_duration = self.video_frames / self.video_fps if self.video_fps > 0 else 0.0
            cap.release()

        try:
            size_b = os.path.getsize(file_path)
            self.video_size_mb = size_b / (1024 * 1024)
        except Exception:
            self.video_size_mb = 0.0

        # Update Step 1 View
        self.lbl_file_name_val.setText(os.path.basename(file_path))
        self.lbl_file_dur_val.setText(f"{format_seconds_to_timestamp(self.video_duration)} ({self.video_duration:.1f} s)")
        self.lbl_file_res_val.setText(f"{self.video_width} × {self.video_height} px")
        self.lbl_file_fps_val.setText(f"{self.video_fps:.2f} fps ({self.video_frames} klatek)")
        self.lbl_file_size_val.setText(f"{self.video_size_mb:.2f} MB")

        # Load into source preview player
        self.source_player.load_video(file_path)

        # Switch to loaded view in Screen 1
        self.upload_content_stack.setCurrentIndex(1)
        self.btn_step1_next.setEnabled(True)
        self.lbl_step1_hint.setText(f"Załadowano: {os.path.basename(file_path)}. Możesz przejść dalej.")

        # Default start and end for Volcano Melt
        self.txt_ts_start.setText("00:00")
        self.txt_ts_end.setText(format_seconds_to_timestamp(self.video_duration))
        self.validate_timestamps()

        # Generate output filename
        self.update_random_output_filename()

        self.log(f"Wczytano wideo: {file_path} (Czas: {format_seconds_to_timestamp(self.video_duration)}, {self.video_width}x{self.video_height})")

    def set_ts_start_from_cursor(self):
        curr_sec = self.source_player.get_current_seconds() if hasattr(self, 'source_player') and self.source_player.cap else 0.0
        self.txt_ts_start.setText(format_seconds_to_timestamp(curr_sec))
        self.validate_timestamps()

    def set_ts_end_from_cursor(self):
        curr_sec = self.source_player.get_current_seconds() if hasattr(self, 'source_player') and self.source_player.cap else 0.0
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
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 5px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText("Nieprawidłowy format czasu początkowego (użyj MM:SS lub MM:SS.s)")
            return False

        if end_sec is None:
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 5px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText("Nieprawidłowy format czasu końcowego (użyj MM:SS lub MM:SS.s)")
            return False

        if start_sec >= end_sec:
            self.lbl_ts_validation.setStyleSheet("color: #b91c1c; font-weight: 700; background-color: #fee2e2; padding: 5px 10px; border-radius: 8px; border: 1px solid #fecaca;")
            self.lbl_ts_validation.setText(f"Czas końcowy ({format_seconds_to_timestamp(end_sec)}) musi być większy niż czas początkowy ({format_seconds_to_timestamp(start_sec)})")
            return False

        if self.video_duration > 0 and end_sec > self.video_duration:
            self.lbl_ts_validation.setStyleSheet("color: #b45309; font-weight: 700; background-color: #fef3c7; padding: 5px 10px; border-radius: 8px; border: 1px solid #fde68a;")
            self.lbl_ts_validation.setText(f"Czas końcowy ({format_seconds_to_timestamp(end_sec)}) przekracza długość filmu ({format_seconds_to_timestamp(self.video_duration)})")
            return False

        duration = end_sec - start_sec
        self.lbl_ts_validation.setStyleSheet("color: #0f172a; font-weight: 700; background-color: #e2ebf5; padding: 5px 10px; border-radius: 8px; border: 1px solid #c8d8ea;")
        self.lbl_ts_validation.setText(f"Prawidłowy przedział: {format_seconds_to_timestamp(start_sec)} do {format_seconds_to_timestamp(end_sec)} [Długość okna: {duration:.1f} s]")
        return True

    def browse_input_b(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik wideo B", "", "Pliki wideo (*.mp4 *.avi *.mov *.mkv *.webm);;Wszystkie pliki (*.*)"
        )
        if file_path:
            self.input_file_b = file_path
            self.lbl_file_b_path.setText(os.path.basename(file_path))
            self.log(f"Wczytano wideo B: {file_path}")

    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz wyjściowy film Datamosh", self.output_file or f"moshup_output_{random.randint(1000, 9999)}.mp4", "MP4 Video (*.mp4);;AVI Video (*.avi)"
        )
        if file_path:
            self.output_file = file_path
            self.lbl_out_path.setText(os.path.basename(file_path))

    def update_random_output_filename(self, mode=""):
        if self.input_file_a:
            self.output_file = generate_random_filename(self.input_file_a, mode)
            self.lbl_out_path.setText(os.path.basename(self.output_file))

    def start_datamosh(self):
        if not self.input_file_a or not os.path.exists(self.input_file_a):
            QMessageBox.warning(self, "Brak pliku wideo", "Wybierz najpierw plik wideo w kroku 1!")
            self.go_to_step(0)
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
                QMessageBox.warning(self, "Błąd zakresu czasu", "Popraw przedział czasu w zakładce Volcano Melt przed startem!")
                self.go_to_step(1)
                return

        if mode == 'stitch_mosh':
            if not self.input_file_b or not os.path.exists(self.input_file_b):
                QMessageBox.warning(self, "Brak drugiego wideo", "Wybierz plik Wideo B dla trybu Stitch Mosh!")
                self.go_to_step(1)
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
        self.btn_step3_back.setEnabled(False)
        self.btn_step3_next.setEnabled(False)
        self.card_completed.setVisible(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Status: Przetwarzanie w toku...")

        self.log(f"Rozpoczynanie zadania: tryb '{mode}' -> {self.output_file}")

        self.worker = DatamoshWorker(mode, self.input_file_a, self.output_file, options)
        self.worker.progress_signal.connect(self.on_worker_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.error_signal.connect(self.on_worker_error)
        self.worker.start()

    def on_worker_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"Status: Przetwarzanie ({pct}%)")
        self.log(f"[{pct}%] {msg}")

    def on_worker_finished(self, out_path):
        self.btn_start.setEnabled(True)
        self.btn_step3_back.setEnabled(True)
        self.btn_step3_next.setEnabled(True)
        self.progress_bar.setValue(100)
        self.lbl_status.setText("Status: Zakończono sukcesem!")
        self.card_completed.setVisible(True)

        self.max_reached_step = max(self.max_reached_step, 3)
        self.update_stepper_and_rail()

        self.log(f"Sukces: Gotowy film zapisano w {out_path}")
        self.lbl_result_path.setText(out_path)

        # Preload into preview player
        self.preview_player.load_video(out_path)

        # Automatically transition to Step 4 (Preview) after brief moment
        QTimer.singleShot(700, lambda: self.go_to_step(3))

    def on_worker_error(self, err_msg):
        self.btn_start.setEnabled(True)
        self.btn_step3_back.setEnabled(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Status: Wystąpił błąd")
        self.log(f"Błąd: {err_msg}")
        QMessageBox.critical(self, "Błąd przetwarzania", f"Wystąpił błąd podczas procesu datamosh:\n\n{err_msg}")

    # PREVIEW SCREEN ACTIONS (Compare Source vs Result)
    def show_preview_result(self):
        self.btn_view_result.setProperty("class", "btnPrimary")
        self.btn_view_source.setProperty("class", "btnSecondary")
        self.btn_view_result.style().unpolish(self.btn_view_result)
        self.btn_view_result.style().polish(self.btn_view_result)
        self.btn_view_source.style().unpolish(self.btn_view_source)
        self.btn_view_source.style().polish(self.btn_view_source)

        if hasattr(self, 'lbl_player_mode_tag'):
            self.lbl_player_mode_tag.setText("Oglądasz: Wygenerowany plik Datamosh")
        if self.output_file and os.path.exists(self.output_file):
            self.lbl_result_path.setText(self.output_file)
            self.preview_player.load_video(self.output_file)

    def show_preview_source(self):
        self.btn_view_result.setProperty("class", "btnSecondary")
        self.btn_view_source.setProperty("class", "btnPrimary")
        self.btn_view_result.style().unpolish(self.btn_view_result)
        self.btn_view_result.style().polish(self.btn_view_result)
        self.btn_view_source.style().unpolish(self.btn_view_source)
        self.btn_view_source.style().polish(self.btn_view_source)

        if hasattr(self, 'lbl_player_mode_tag'):
            self.lbl_player_mode_tag.setText("Oglądasz: Oryginalny plik wideo (Przed efektem)")
        if self.input_file_a and os.path.exists(self.input_file_a):
            self.lbl_result_path.setText(self.input_file_a)
            self.preview_player.load_video(self.input_file_a)

    def open_output_folder(self):
        target = self.output_file if (self.output_file and os.path.exists(self.output_file)) else self.input_file_a
        if target and os.path.exists(os.path.dirname(target)):
            folder = os.path.dirname(target)
            if sys.platform == 'win32':
                os.startfile(folder)
            else:
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', folder])

    def open_output_video(self):
        target = self.output_file if (self.output_file and os.path.exists(self.output_file)) else self.input_file_a
        if target and os.path.exists(target):
            if sys.platform == 'win32':
                os.startfile(target)
            else:
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', target])

    def reset_new_project(self):
        reply = QMessageBox.question(
            self, "Nowy projekt", "Czy chcesz zresetować bieżący projekt i wczytać nowe wideo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'source_player'):
                self.source_player.pause()
            if hasattr(self, 'preview_player'):
                self.preview_player.pause()

            self.input_file_a = ""
            self.input_file_b = ""
            self.output_file = ""
            self.max_reached_step = 0
            self.card_completed.setVisible(False)
            self.btn_step1_next.setEnabled(False)
            self.btn_step3_next.setEnabled(False)
            self.lbl_step1_hint.setText("Wybierz plik wideo, aby przejść do konfiguracji efektów.")
            self.upload_content_stack.setCurrentIndex(0)
            self.go_to_step(0)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MoshUpApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
