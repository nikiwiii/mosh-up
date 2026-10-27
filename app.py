import os
import sys
import time
import subprocess
import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFileDialog, QMessageBox, QStackedWidget
)

from style import SOFT_PORCELAIN_QSS, DARK_QSS
from datamosh_engine import (
    DatamoshEngine,
    get_ffmpeg_exe,
    parse_timestamp,
    format_seconds_to_timestamp,
)
from lucide_icons import get_lucide_icon
from ui import (
    apply_card_shadow,
    generate_random_filename,
    DatamoshWorker,
    FastDraftWorker,
    DropAreaWidget,
    VideoPreviewWidget,
    NavigationRail,
    FastDraftInlineWidget,
    UploadPage,
    EffectsPage,
    RenderPage,
    PreviewPage,
)


class MoshUpApp(QMainWindow):
    """
    Main Application Window for MoshUp Studio.
    Orchestrates wizard navigation across 4 steps, background worker execution,
    and video state management.
    """

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

        # 1. Left Navigation Rail
        self.sidebar_rail = NavigationRail(self)
        self.sidebar_rail.step_selected.connect(self.go_to_step)
        self.sidebar_rail.reset_requested.connect(self.confirm_and_reset_app)
        self.sidebar_rail.info_requested.connect(self.show_about_dialog)
        root_layout.addWidget(self.sidebar_rail)

        # Backward compatibility for self.rail_buttons
        self.rail_buttons = self.sidebar_rail.rail_buttons

        # 2. Main Workspace Area
        main_workspace = QWidget(self)
        main_layout = QVBoxLayout(main_workspace)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        self.stack = QStackedWidget(self)

        # Initialize the 4 Pages
        self.page_upload = UploadPage(self)
        self.page_effects = EffectsPage(self)
        self.page_render = RenderPage(self)
        self.page_preview = PreviewPage(self)

        # Wire Step 1 (Upload) controls
        self.upload_content_stack = self.page_upload.upload_content_stack
        self.drop_area = self.page_upload.drop_area
        self.drop_area.file_dropped.connect(self.set_input_file_a)
        self.btn_browse_empty = self.page_upload.btn_browse_empty
        self.btn_browse_empty.clicked.connect(self.browse_input_a)
        self.source_player = self.page_upload.source_player
        self.lbl_source_status_badge = self.page_upload.lbl_source_status_badge
        self.lbl_file_name_val = self.page_upload.lbl_file_name_val
        self.lbl_file_dur_val = self.page_upload.lbl_file_dur_val
        self.lbl_file_res_val = self.page_upload.lbl_file_res_val
        self.lbl_file_fps_val = self.page_upload.lbl_file_fps_val
        self.lbl_file_size_val = self.page_upload.lbl_file_size_val
        self.btn_replace_video = self.page_upload.btn_replace_video
        self.btn_replace_video.clicked.connect(self.browse_input_a)
        self.lbl_step1_hint = self.page_upload.lbl_step1_hint
        self.btn_step1_next = self.page_upload.btn_step1_next
        self.btn_step1_next.clicked.connect(lambda: self.go_to_step(1))

        # Wire Step 2 (Effects) controls
        self.tabs = self.page_effects.tabs
        self.txt_ts_start = self.page_effects.txt_ts_start
        self.txt_ts_start.textChanged.connect(self.validate_timestamps)
        self.txt_ts_end = self.page_effects.txt_ts_end
        self.txt_ts_end.textChanged.connect(self.validate_timestamps)
        self.btn_set_curr_start = self.page_effects.btn_set_curr_start
        self.btn_set_curr_start.clicked.connect(self.set_ts_start_from_cursor)
        self.btn_set_curr_end = self.page_effects.btn_set_curr_end
        self.btn_set_curr_end.clicked.connect(self.set_ts_end_from_cursor)
        self.lbl_ts_validation = self.page_effects.lbl_ts_validation

        self.spin_s_repeat = self.page_effects.spin_s_repeat
        self.spin_s_freq = self.page_effects.spin_s_freq

        self.btn_select_b = self.page_effects.btn_select_b
        self.btn_select_b.clicked.connect(self.browse_input_b)
        self.lbl_file_b_path = self.page_effects.lbl_file_b_path

        self.slider_c_rate = self.page_effects.slider_c_rate
        self.slider_c_intensity = self.page_effects.slider_c_intensity

        self.spin_fl_scale = self.page_effects.spin_fl_scale
        self.spin_fl_decay = self.page_effects.spin_fl_decay

        self.spin_rgb_delay = self.page_effects.spin_rgb_delay
        self.spin_rgb_shift = self.page_effects.spin_rgb_shift
        self.combo_rgb_direction = self.page_effects.combo_rgb_direction
        self.slider_rgb_jitter = self.page_effects.slider_rgb_jitter

        self.chk_keep_audio = self.page_effects.chk_keep_audio
        self.btn_select_out = self.page_effects.btn_select_out
        self.btn_select_out.clicked.connect(self.browse_output)
        self.lbl_out_path = self.page_effects.lbl_out_path

        self.fast_draft_widget = self.page_effects.fast_draft_widget
        self.btn_fast_draft = self.page_effects.btn_fast_draft
        self.fast_draft_player = self.page_effects.fast_draft_player
        self.fast_draft_widget.draft_requested.connect(self.start_fast_draft)

        self.btn_step2_back = self.page_effects.btn_step2_back
        self.btn_step2_back.clicked.connect(lambda: self.go_to_step(0))
        self.btn_step2_next = self.page_effects.btn_step2_next
        self.btn_step2_next.clicked.connect(lambda: self.go_to_step(2))

        # Wire Step 3 (Render) controls
        self.summary_card = self.page_render.summary_card
        self.lbl_sum_src_name = self.page_render.lbl_sum_src_name
        self.lbl_sum_src_meta1 = self.page_render.lbl_sum_src_meta1
        self.lbl_sum_src_meta2 = self.page_render.lbl_sum_src_meta2
        self.lbl_sum_mode_name = self.page_render.lbl_sum_mode_name
        self.lbl_sum_param1 = self.page_render.lbl_sum_param1
        self.lbl_sum_param2 = self.page_render.lbl_sum_param2
        self.lbl_sum_audio_status = self.page_render.lbl_sum_audio_status
        self.lbl_sum_output_file = self.page_render.lbl_sum_output_file
        self.lbl_sum_output_dir = self.page_render.lbl_sum_output_dir

        self.btn_start = self.page_render.btn_start
        self.btn_start.clicked.connect(self.start_datamosh)
        self.lbl_status = self.page_render.lbl_status
        self.progress_bar = self.page_render.progress_bar
        self.log_console = self.page_render.log_console

        self.btn_step3_back = self.page_render.btn_step3_back
        self.btn_step3_back.clicked.connect(lambda: self.go_to_step(1))
        self.btn_step3_next = self.page_render.btn_step3_next
        self.btn_step3_next.clicked.connect(lambda: self.go_to_step(3))

        # Wire Step 4 (Preview) controls
        self.btn_view_result = self.page_preview.btn_view_result
        self.btn_view_result.clicked.connect(self.show_preview_result)
        self.btn_view_source = self.page_preview.btn_view_source
        self.btn_view_source.clicked.connect(self.show_preview_source)
        self.preview_player = self.page_preview.preview_player
        self.lbl_result_path = self.page_preview.lbl_result_path

        self.btn_open_video = self.page_preview.btn_open_video
        self.btn_open_video.clicked.connect(self.open_output_video)
        self.btn_open_folder = self.page_preview.btn_open_folder
        self.btn_open_folder.clicked.connect(self.open_output_folder)
        self.btn_tweak_params = self.page_preview.btn_tweak_params
        self.btn_tweak_params.clicked.connect(lambda: self.go_to_step(1))
        self.btn_new_project = self.page_preview.btn_new_project
        self.btn_new_project.clicked.connect(self.reset_new_project)

        self.btn_step4_back = self.page_preview.btn_step4_back
        self.btn_step4_back.clicked.connect(lambda: self.go_to_step(2))
        self.btn_step4_restart = self.page_preview.btn_step4_restart
        self.btn_step4_restart.clicked.connect(self.reset_new_project)

        # Add pages to stack
        self.stack.addWidget(self.page_upload)    # Index 0
        self.stack.addWidget(self.page_effects)   # Index 1
        self.stack.addWidget(self.page_render)    # Index 2
        self.stack.addWidget(self.page_preview)   # Index 3

        main_layout.addWidget(self.stack, 1)
        root_layout.addWidget(main_workspace, 1)

        self.update_stepper_and_rail()

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
        if hasattr(self, 'fast_draft_widget'):
            self.fast_draft_widget.pause()
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
        self.sidebar_rail.set_current_step(self.current_step)

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
        elif tab_idx == 4:
            self.lbl_sum_mode_name.setText("Flow Drift (Przepływ optyczny Farneback)")
            self.lbl_sum_param1.setText(f"Skala przepływu: {self.spin_fl_scale.value():.1f} • Wygaszanie śladu: {self.spin_fl_decay.value():.2f}")
            self.lbl_sum_param2.setText("Dynamiczna deformacja pola wektorów na ekranie")
        else:
            self.lbl_sum_mode_name.setText("RGB Channel Split (Aberracja chromatyczna)")
            dir_text = self.combo_rgb_direction.currentText()
            self.lbl_sum_param1.setText(f"Lag: {self.spin_rgb_delay.value()} kl. • Shift: {self.spin_rgb_shift.value()} px ({dir_text})")
            self.lbl_sum_param2.setText(f"Zakłócenia linii VHS: {self.slider_rgb_jitter.value()}% szansy na klatkę")

        # 3. Audio Tile
        if self.chk_keep_audio.isChecked():
            self.lbl_sum_audio_status.setText("Ścieżka audio: Zachowana (Oryginał)")
        else:
            self.lbl_sum_audio_status.setText("Ścieżka audio: Wyciszona (Brak audio)")

        # 4. Output File Tile
        mode_keys = ['volcano_melt', 'motion_smear', 'stitch_mosh', 'cyber_glitch', 'flow_drift', 'rgb_split']
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
            "<li><b>RGB Channel Split</b>: Rozszczepianie kanałów barwnych (Red, Green, Blue) z opóźnieniem czasowym i przesunięciem przestrzennym</li>"
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
            self, "Zapisz wyjściowy film Datamosh", self.output_file or f"moshup_output_export.mp4", "MP4 Video (*.mp4);;AVI Video (*.avi)"
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
            4: 'flow_drift',
            5: 'rgb_split'
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
            'decay': self.spin_fl_decay.value(),
            'rgb_delay': self.spin_rgb_delay.value(),
            'rgb_shift': self.spin_rgb_shift.value(),
            'rgb_direction': self.combo_rgb_direction.currentData() or 'horizontal',
            'rgb_jitter': self.slider_rgb_jitter.value()
        }

        self.btn_start.setEnabled(False)
        self.btn_step3_back.setEnabled(False)
        self.btn_step3_next.setEnabled(False)
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

    # FAST DRAFT (3-second instant preview)
    def start_fast_draft(self):
        if not self.input_file_a or not os.path.exists(self.input_file_a):
            QMessageBox.warning(self, "Brak pliku wideo", "Wybierz najpierw plik wideo w kroku 1!")
            self.go_to_step(0)
            return

        mode_map = {
            0: 'volcano_melt',
            1: 'motion_smear',
            2: 'stitch_mosh',
            3: 'cyber_glitch',
            4: 'flow_drift',
            5: 'rgb_split'
        }
        tab_idx = self.tabs.currentIndex()
        mode = mode_map.get(tab_idx, 'volcano_melt')

        if mode == 'volcano_melt':
            if not self.validate_timestamps():
                QMessageBox.warning(self, "Błąd zakresu czasu", "Popraw przedział czasu w zakładce Volcano Melt przed podglądem!")
                return

        if mode == 'stitch_mosh':
            if not self.input_file_b or not os.path.exists(self.input_file_b):
                QMessageBox.warning(self, "Brak drugiego wideo", "Wybierz plik Wideo B dla trybu Stitch Mosh przed wygenerowaniem podglądu!")
                return

        if mode == 'volcano_melt':
            start_sec = parse_timestamp(self.txt_ts_start.text()) or 0.0
            t_start = max(0.0, min(max(0.0, self.video_duration - 3.0), start_sec))
        else:
            cursor_sec = self.source_player.get_current_seconds() if hasattr(self, 'source_player') and self.source_player.cap else 0.0
            t_start = max(0.0, min(max(0.0, self.video_duration - 3.0), cursor_sec))

        options = {
            'keep_audio': self.chk_keep_audio.isChecked(),
            'input_b': self.input_file_b,
            'start_sec': 0.0,
            'end_sec': 3.0,
            'video_duration': 3.0,
            'repeat_count': self.spin_s_repeat.value(),
            'frequency': self.spin_s_freq.value(),
            'corrupt_rate': self.slider_c_rate.value() / 100.0,
            'intensity': self.slider_c_intensity.value() / 100.0,
            'flow_scale': self.spin_fl_scale.value(),
            'decay': self.spin_fl_decay.value(),
            'rgb_delay': self.spin_rgb_delay.value(),
            'rgb_shift': self.spin_rgb_shift.value(),
            'rgb_direction': self.combo_rgb_direction.currentData() or 'horizontal',
            'rgb_jitter': self.slider_rgb_jitter.value()
        }

        temp_dir = os.path.dirname(self.input_file_a) or "."
        draft_output = os.path.join(temp_dir, f"_temp_fast_draft_{mode}.mp4")

        if hasattr(self, 'fast_draft_widget'):
            self.fast_draft_widget.show_loading()
            self.fast_draft_widget.set_progress(0)

        self.draft_worker = FastDraftWorker(
            mode=mode,
            input_path_a=self.input_file_a,
            input_path_b=self.input_file_b,
            output_draft_path=draft_output,
            options=options,
            t_start=t_start
        )
        self.draft_worker.progress_signal.connect(self.on_draft_progress)
        self.draft_worker.finished_signal.connect(self.on_draft_finished)
        self.draft_worker.error_signal.connect(self.on_draft_error)
        self.draft_worker.start()

    def on_draft_progress(self, pct, msg):
        if hasattr(self, 'fast_draft_widget'):
            self.fast_draft_widget.set_progress(pct)

    def on_draft_finished(self, draft_path):
        if hasattr(self, 'fast_draft_widget') and os.path.exists(draft_path):
            self.fast_draft_widget.show_preview(draft_path)

    def on_draft_error(self, err_msg):
        if hasattr(self, 'fast_draft_widget'):
            self.fast_draft_widget.show_button()
        QMessageBox.critical(self, "Błąd szybkiego podglądu", f"Nie udało się wygenerować wycinka:\n\n{err_msg}")

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

    def confirm_and_reset_app(self):
        """Displays a confirmation dialog before resetting all application parameters and state."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Resetowanie parametrów")
        msg_box.setText("<h3>Czy chcesz zresetować parametry do stanu początkowego?</h3>")
        msg_box.setInformativeText(
            "Wszystkie wczytane pliki wideo, zmodyfikowane parametry efektów, "
            "wygenerowane podglądy oraz stan renderowania zostaną przywrócone do stanu zerowego (uruchomienia)."
        )
        msg_box.setIcon(QMessageBox.Icon.Question)
        btn_reset = msg_box.addButton("  Zresetuj wszystko", QMessageBox.ButtonRole.AcceptRole)
        btn_reset.setProperty("class", "btnPrimary")
        btn_cancel = msg_box.addButton("  Anuluj", QMessageBox.ButtonRole.RejectRole)
        btn_cancel.setProperty("class", "btnSecondary")
        msg_box.setDefaultButton(btn_cancel)
        btn_reset.setIcon(get_lucide_icon("rotate-ccw", color="#64748b", size=14))
        btn_cancel.setIcon(get_lucide_icon("x", color="#64748b", size=14))

        msg_box.exec()
        if msg_box.clickedButton() == btn_reset:
            self.reset_to_defaults()

    def reset_to_defaults(self):
        """Resets all app variables, players, controls, and wizard pages to pristine startup state."""
        # 1. Stop background workers if running
        if hasattr(self, 'worker') and self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker = None
        if hasattr(self, 'draft_worker') and self.draft_worker and self.draft_worker.isRunning():
            self.draft_worker.terminate()
            self.draft_worker = None

        # 2. Stop and release video players
        if hasattr(self, 'source_player'):
            self.source_player.pause()
            if self.source_player.cap:
                self.source_player.cap.release()
                self.source_player.cap = None
            self.source_player.display_label.setText("Brak załadowanego wideo")
            self.source_player.display_label.setPixmap(QPixmap())
            self.source_player.time_label.setText("00:00 / 00:00")
            self.source_player.slider.setValue(0)
            self.source_player.slider.setRange(0, 0)
            self.source_player.current_file_path = ""

        if hasattr(self, 'fast_draft_widget'):
            self.fast_draft_widget.reset()

        if hasattr(self, 'preview_player'):
            self.preview_player.pause()
            if self.preview_player.cap:
                self.preview_player.cap.release()
                self.preview_player.cap = None
            self.preview_player.display_label.setText("Brak załadowanego wideo")
            self.preview_player.display_label.setPixmap(QPixmap())
            self.preview_player.time_label.setText("00:00 / 00:00")
            self.preview_player.slider.setValue(0)
            self.preview_player.slider.setRange(0, 0)
            self.preview_player.current_file_path = ""

        # 3. Reset application state variables
        self.input_file_a = ""
        self.input_file_b = ""
        self.output_file = ""
        self.video_duration = 0.0
        self.video_fps = 30.0
        self.video_width = 0
        self.video_height = 0
        self.video_frames = 0
        self.video_size_mb = 0.0
        self.max_reached_step = 0

        # 4. Step 1 (Upload Page) reset
        self.upload_content_stack.setCurrentIndex(0)
        self.btn_step1_next.setEnabled(False)
        self.lbl_step1_hint.setText("Wybierz plik wideo, aby przejść do konfiguracji efektów.")
        self.lbl_file_name_val.setText("-")
        self.lbl_file_dur_val.setText("-")
        self.lbl_file_res_val.setText("-")
        self.lbl_file_fps_val.setText("-")
        self.lbl_file_size_val.setText("-")

        # 5. Step 2 (Effects Page) reset
        self.page_effects.reset_parameters()

        # 6. Step 3 (Render Page) reset
        self.btn_start.setEnabled(True)
        self.btn_step3_back.setEnabled(True)
        self.btn_step3_next.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Status: Oczekiwanie na rozpoczęcie")
        self.log_console.clear()
        self.log_console.append("MoshUp Studio gotowe.")
        self.lbl_sum_src_name.setText("-")
        self.lbl_sum_src_meta1.setText("-")
        self.lbl_sum_src_meta2.setText("-")
        self.lbl_sum_mode_name.setText("-")
        self.lbl_sum_param1.setText("-")
        self.lbl_sum_param2.setText("-")
        self.lbl_sum_audio_status.setText("-")
        self.lbl_sum_output_file.setText("-")
        self.lbl_sum_output_dir.setText("-")

        # 7. Step 4 (Preview Page) reset
        self.lbl_result_path.setText("Brak wygenerowanego pliku")
        self.btn_open_video.setEnabled(False)
        self.btn_open_folder.setEnabled(False)

        # 8. Reset wizard navigation to Step 1
        self.go_to_step(0)
        self.update_stepper_and_rail()

        self.log("Zresetowano parametry aplikacji do stanu początkowego.")

    def reset_new_project(self):
        reply = QMessageBox.question(
            self, "Nowy projekt", "Czy chcesz zresetować bieżący projekt i wczytać nowe wideo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reset_to_defaults()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MoshUpApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
