from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QGroupBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QSlider, QCheckBox, QComboBox, QScrollArea
)
from lucide_icons import get_lucide_icon, get_lucide_pixmap
from ..widgets import VideoPreviewWidget, FastDraftInlineWidget
from ..utils import apply_card_shadow


class EffectsPage(QWidget):
    """
    Step 2: Effects & Parameters Configuration Page.
    Contains tabbed settings for all 6 datamoshing effects, as well as an inline
    Fast Draft preview player and export/audio options.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(self)
        header_card.setProperty("class", "softCard")
        h_layout = QVBoxLayout(header_card)
        h_layout.setContentsMargins(16, 8, 16, 8)
        h_layout.setSpacing(2)

        lbl_h_title = QLabel("Krok 2: Wybór efektu i parametrów", header_card)
        lbl_h_title.setProperty("class", "pageHeaderTitle")
        lbl_h_sub = QLabel("Wybierz tryb zniekształceń klatek i dostosuj parametry algorytmu datamosh.", header_card)
        lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(lbl_h_title)
        h_layout.addWidget(lbl_h_sub)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Content Scroll Area for Step 2
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        sc_layout = QVBoxLayout(scroll_content)
        sc_layout.setContentsMargins(0, 0, 0, 0)
        sc_layout.setSpacing(8)

        # Datamosh Modes Tabs Card
        tabs_card = QFrame(scroll_content)
        tabs_card.setProperty("class", "softCard")
        tabs_card_layout = QVBoxLayout(tabs_card)
        tabs_card_layout.setContentsMargins(14, 8, 14, 8)
        tabs_card_layout.setSpacing(6)

        self.tabs = QTabWidget(tabs_card)
        self.tabs.setIconSize(QSize(16, 16))
        self.tabs.setUsesScrollButtons(False)

        # --- Tab 1: Volcano Melt ---
        tab_volcano = QWidget()
        tab_v_layout = QVBoxLayout(tab_volcano)
        tab_v_layout.setContentsMargins(10, 8, 10, 6)
        tab_v_layout.setSpacing(6)

        desc_v_row = QHBoxLayout()
        desc_v_row.setContentsMargins(0, 0, 0, 2)
        desc_v_row.setSpacing(10)
        desc_v_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_v_desc = QLabel(
            "Usuwa klatki kluczowe (I-Frames) w zadanym oknie czasowym. Wektory ruchu deformatują poprzedni "
            "statyczny obraz, tworząc płynne topnienie obiektów.", tab_volcano
        )
        lbl_v_desc.setWordWrap(True)
        lbl_v_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_v_row.addWidget(lbl_v_desc, 1)
        tab_v_layout.addLayout(desc_v_row)

        ts_box = QGroupBox("Przedział czasowy efektu", tab_volcano)
        ts_box_layout = QVBoxLayout(ts_box)
        ts_box_layout.setContentsMargins(12, 8, 12, 6)
        ts_box_layout.setSpacing(6)

        ts_start_layout = QHBoxLayout()
        lbl_start = QLabel("Czas początkowy (Start):", tab_volcano)
        lbl_start.setStyleSheet("font-weight: 600; color: #475569;")
        lbl_start.setFixedWidth(160)
        self.txt_ts_start = QLineEdit(tab_volcano)
        self.txt_ts_start.setPlaceholderText("00:00")
        self.txt_ts_start.setText("00:00")

        self.btn_set_curr_start = QPushButton("  Z pozycji odtwarzacza", tab_volcano)
        self.btn_set_curr_start.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))

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

        self.btn_set_curr_end = QPushButton("  Z pozycji odtwarzacza", tab_volcano)
        self.btn_set_curr_end.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))

        ts_end_layout.addWidget(lbl_end)
        ts_end_layout.addWidget(self.txt_ts_end, 1)
        ts_end_layout.addWidget(self.btn_set_curr_end)
        ts_box_layout.addLayout(ts_end_layout)

        self.lbl_ts_validation = QLabel("Format: MM:SS (np. 00:05 lub 01:20)", tab_volcano)
        self.lbl_ts_validation.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5fa; "
            "border: 1px solid #dce4ef; border-radius: 7px; padding: 3px 8px; margin-top: 1px;"
        )
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(ts_box)
        tab_v_layout.addStretch(1)
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#475569"), "Volcano Melt")

        # --- Tab 2: Motion Smear ---
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)
        tab_s_layout.setContentsMargins(10, 8, 10, 6)
        tab_s_layout.setSpacing(6)

        desc_s_row = QHBoxLayout()
        desc_s_row.setContentsMargins(0, 0, 0, 2)
        desc_s_row.setSpacing(10)
        desc_s_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_s_desc = QLabel(
            "Duplikuje klatki delta (P-Frames), powodując wielokrotne powtarzanie wektorów ruchu i "
            "charakterystyczne smugi pikseli.", tab_smear
        )
        lbl_s_desc.setWordWrap(True)
        lbl_s_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_s_row.addWidget(lbl_s_desc, 1)
        tab_s_layout.addLayout(desc_s_row)

        s_box = QGroupBox("Parametry rozmycia wektorów", tab_smear)
        s_box_layout = QVBoxLayout(s_box)
        s_box_layout.setContentsMargins(12, 8, 12, 6)
        s_box_layout.setSpacing(6)

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
        tab_s_layout.addStretch(1)
        self.tabs.addTab(tab_smear, get_lucide_icon("wind", color="#475569"), "Motion Smear")

        # --- Tab 3: Stitch Mosh ---
        tab_stitch = QWidget()
        tab_st_layout = QVBoxLayout(tab_stitch)
        tab_st_layout.setContentsMargins(10, 8, 10, 6)
        tab_st_layout.setSpacing(6)

        desc_st_row = QHBoxLayout()
        desc_st_row.setContentsMargins(0, 0, 0, 2)
        desc_st_row.setSpacing(10)
        desc_st_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_st_desc = QLabel(
            "Łączy dwa pliki wideo. Początkowa klatka kluczowa wideo B zostaje wycięta, przez co ruch z "
            "drugiego klipu ożywia ostatnią klatkę pierwszego wideo.", tab_stitch
        )
        lbl_st_desc.setWordWrap(True)
        lbl_st_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_st_row.addWidget(lbl_st_desc, 1)
        tab_st_layout.addLayout(desc_st_row)

        st_box = QGroupBox("Drugi plik wideo (Wideo B)", tab_stitch)
        st_box_layout = QVBoxLayout(st_box)
        st_box_layout.setContentsMargins(12, 8, 12, 6)
        st_box_layout.setSpacing(6)

        file_b_layout = QHBoxLayout()
        self.btn_select_b = QPushButton("  Wybierz wideo B...", tab_stitch)
        self.btn_select_b.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=15))

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
        tab_st_layout.addStretch(1)
        self.tabs.addTab(tab_stitch, get_lucide_icon("shuffle", color="#475569"), "Stitch Mosh")

        # --- Tab 4: Cyber Glitch ---
        tab_cyber = QWidget()
        tab_c_layout = QVBoxLayout(tab_cyber)
        tab_c_layout.setContentsMargins(10, 8, 10, 6)
        tab_c_layout.setSpacing(6)

        desc_c_row = QHBoxLayout()
        desc_c_row.setContentsMargins(0, 0, 0, 2)
        desc_c_row.setSpacing(10)
        desc_c_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_c_desc = QLabel(
            "Wstrzykuje losowe uszkodzenia bajtów bezpośrednio do wektorów klatek różnicowych (P-Frames), "
            "generując cyfrowe zakłócenia w stylu glitch-art.", tab_cyber
        )
        lbl_c_desc.setWordWrap(True)
        lbl_c_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_c_row.addWidget(lbl_c_desc, 1)
        tab_c_layout.addLayout(desc_c_row)

        c_box = QGroupBox("Ustawienia uszkodzeń bitowych", tab_cyber)
        c_box_layout = QVBoxLayout(c_box)
        c_box_layout.setContentsMargins(12, 8, 12, 6)
        c_box_layout.setSpacing(6)

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
        tab_c_layout.addStretch(1)
        self.tabs.addTab(tab_cyber, get_lucide_icon("cpu", color="#475569"), "Cyber Glitch")

        # --- Tab 5: Flow Drift ---
        tab_flow = QWidget()
        tab_fl_layout = QVBoxLayout(tab_flow)
        tab_fl_layout.setContentsMargins(10, 8, 10, 6)
        tab_fl_layout.setSpacing(6)

        desc_fl_row = QHBoxLayout()
        desc_fl_row.setContentsMargins(0, 0, 0, 2)
        desc_fl_row.setSpacing(10)
        desc_fl_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_fl_desc = QLabel(
            "Oblicza wektory przepływu optycznego pomiędzy klatkami i deformuje zakumulowane piksele "
            "na ekranie w organiczny, płynny sposób.", tab_flow
        )
        lbl_fl_desc.setWordWrap(True)
        lbl_fl_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_fl_row.addWidget(lbl_fl_desc, 1)
        tab_fl_layout.addLayout(desc_fl_row)

        fl_box = QGroupBox("Parametry przepływu optycznego (Farneback)", tab_flow)
        fl_box_layout = QVBoxLayout(fl_box)
        fl_box_layout.setContentsMargins(12, 8, 12, 6)
        fl_box_layout.setSpacing(6)

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
        tab_fl_layout.addStretch(1)
        self.tabs.addTab(tab_flow, get_lucide_icon("waves", color="#475569"), "Flow Drift")

        # --- Tab 6: RGB Split ---
        tab_rgb = QWidget()
        tab_rgb_layout = QVBoxLayout(tab_rgb)
        tab_rgb_layout.setContentsMargins(10, 8, 10, 6)
        tab_rgb_layout.setSpacing(6)

        desc_rgb_row = QHBoxLayout()
        desc_rgb_row.setContentsMargins(0, 0, 0, 2)
        desc_rgb_row.setSpacing(10)
        desc_rgb_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_rgb_desc = QLabel(
            "Rozszczepia składowe barwne (czerwony, zielony, niebieski) z opóźnieniem czasowym i przesunięciem "
            "przestrzennym, tworząc hipnotyzujące tęczowe smugi ruchu oraz analogowy efekt aberracji chromatycznej VHS.", tab_rgb
        )
        lbl_rgb_desc.setWordWrap(True)
        lbl_rgb_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_rgb_row.addWidget(lbl_rgb_desc, 1)
        tab_rgb_layout.addLayout(desc_rgb_row)

        rgb_box = QGroupBox("Parametry rozszczepienia kanałów RGB", tab_rgb)
        rgb_box_layout = QVBoxLayout(rgb_box)
        rgb_box_layout.setContentsMargins(12, 8, 12, 6)
        rgb_box_layout.setSpacing(5)

        rgb_delay_row = QHBoxLayout()
        rgb_delay_lbl = QLabel("Opóźnienie klatek (Lag czasowy):", tab_rgb)
        rgb_delay_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        rgb_delay_lbl.setFixedWidth(220)
        self.spin_rgb_delay = QSpinBox(tab_rgb)
        self.spin_rgb_delay.setRange(0, 20)
        self.spin_rgb_delay.setValue(4)
        rgb_delay_row.addWidget(rgb_delay_lbl)
        rgb_delay_row.addWidget(self.spin_rgb_delay, 1)
        rgb_box_layout.addLayout(rgb_delay_row)

        rgb_shift_row = QHBoxLayout()
        rgb_shift_lbl = QLabel("Przesunięcie optyczne (px):", tab_rgb)
        rgb_shift_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        rgb_shift_lbl.setFixedWidth(220)
        self.spin_rgb_shift = QSpinBox(tab_rgb)
        self.spin_rgb_shift.setRange(0, 40)
        self.spin_rgb_shift.setValue(8)
        rgb_shift_row.addWidget(rgb_shift_lbl)
        rgb_shift_row.addWidget(self.spin_rgb_shift, 1)
        rgb_box_layout.addLayout(rgb_shift_row)

        rgb_dir_row = QHBoxLayout()
        rgb_dir_lbl = QLabel("Kierunek przesunięcia:", tab_rgb)
        rgb_dir_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        rgb_dir_lbl.setFixedWidth(220)
        self.combo_rgb_direction = QComboBox(tab_rgb)
        self.combo_rgb_direction.addItem("Poziomy (Horizontal)", "horizontal")
        self.combo_rgb_direction.addItem("Ukośny (Diagonal)", "diagonal")
        self.combo_rgb_direction.addItem("Pionowy (Vertical)", "vertical")
        rgb_dir_row.addWidget(rgb_dir_lbl)
        rgb_dir_row.addWidget(self.combo_rgb_direction, 1)
        rgb_box_layout.addLayout(rgb_dir_row)

        rgb_jitter_lbl = QLabel("Zakłócenia linii VHS (Jitter %):", tab_rgb)
        rgb_jitter_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        rgb_box_layout.addWidget(rgb_jitter_lbl)
        self.slider_rgb_jitter = QSlider(Qt.Orientation.Horizontal, tab_rgb)
        self.slider_rgb_jitter.setRange(0, 50)
        self.slider_rgb_jitter.setValue(10)
        rgb_box_layout.addWidget(self.slider_rgb_jitter)

        tab_rgb_layout.addWidget(rgb_box)
        tab_rgb_layout.addStretch(1)
        self.tabs.addTab(tab_rgb, get_lucide_icon("split", color="#475569"), "RGB Split")

        tabs_card_layout.addWidget(self.tabs, 1)
        apply_card_shadow(tabs_card)
        sc_layout.addWidget(tabs_card)

        # Inline Fast Draft on Effect Description Level
        self.desc_rows = [desc_v_row, desc_s_row, desc_st_row, desc_c_row, desc_fl_row, desc_rgb_row]
        self.fast_draft_widget = FastDraftInlineWidget(self)
        self.desc_rows[0].addWidget(self.fast_draft_widget)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.btn_fast_draft = self.fast_draft_widget.btn_draft
        self.fast_draft_player = self.fast_draft_widget

        # Export & Audio Configuration Card
        opts_card = QFrame(scroll_content)
        opts_card.setProperty("class", "softCard")
        opts_card_layout = QVBoxLayout(opts_card)
        opts_card_layout.setContentsMargins(16, 8, 16, 8)
        opts_card_layout.setSpacing(6)

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
        sc_layout.addWidget(opts_card)
        sc_layout.addStretch(1)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area, 1)

        # Bottom Navigation Bar
        nav_card = QFrame(self)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 6, 14, 6)

        self.btn_step2_back = QPushButton("  Wróć do wyboru wideo", nav_card)
        self.btn_step2_back.setProperty("class", "btnSecondary")
        self.btn_step2_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step2_back.setFixedHeight(36)
        nc_layout.addWidget(self.btn_step2_back)

        nc_layout.addStretch()

        self.btn_step2_next = QPushButton("  Dalej: Eksport i Renderowanie", nav_card)
        self.btn_step2_next.setProperty("class", "btnPrimary")
        self.btn_step2_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step2_next.setFixedHeight(36)
        nc_layout.addWidget(self.btn_step2_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

    def _on_tab_changed(self, idx):
        if 0 <= idx < len(self.desc_rows):
            self.fast_draft_widget.pause()
            self.fast_draft_widget.show_button()
            self.desc_rows[idx].addWidget(self.fast_draft_widget)

