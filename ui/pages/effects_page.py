from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QGroupBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QSlider, QCheckBox
)
from lucide_icons import get_lucide_icon
from ..utils import apply_card_shadow


class EffectsPage(QWidget):
    """
    Step 2: Effects & Parameters Configuration Page.
    Contains tabbed settings for all 5 datamoshing effects, as well as export
    and audio options.
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

        # Datamosh Modes Tabs Card
        tabs_card = QFrame(self)
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

        lbl_v_desc = QLabel(
            "Usuwa klatki kluczowe (I-Frames) w zadanym oknie czasowym. Wektory ruchu deformatują poprzedni "
            "statyczny obraz, tworząc płynne topnienie obiektów.", tab_volcano
        )
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
            "font-size: 11.5px; font-weight: 600; color: #64748b; background-color: #f1f5fa; "
            "border: 1px solid #dce4ef; border-radius: 8px; padding: 5px 10px; margin-top: 2px;"
        )
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(ts_box)
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#475569"), "Volcano Melt")

        # --- Tab 2: Motion Smear ---
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)
        tab_s_layout.setContentsMargins(12, 12, 12, 10)
        tab_s_layout.setSpacing(8)

        lbl_s_desc = QLabel(
            "Duplikuje klatki delta (P-Frames), powodując wielokrotne powtarzanie wektorów ruchu i "
            "charakterystyczne smugi pikseli.", tab_smear
        )
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

        lbl_st_desc = QLabel(
            "Łączy dwa pliki wideo. Początkowa klatka kluczowa wideo B zostaje wycięta, przez co ruch z "
            "drugiego klipu ożywia ostatnią klatkę pierwszego wideo.", tab_stitch
        )
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

        lbl_c_desc = QLabel(
            "Wstrzykuje losowe uszkodzenia bajtów bezpośrednio do wektorów klatek różnicowych (P-Frames), "
            "generując cyfrowe zakłócenia w stylu glitch-art.", tab_cyber
        )
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

        lbl_fl_desc = QLabel(
            "Oblicza wektory przepływu optycznego pomiędzy klatkami i deformuje zakumulowane piksele "
            "na ekranie w organiczny, płynny sposób.", tab_flow
        )
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
        opts_card = QFrame(self)
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
        nav_card = QFrame(self)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step2_back = QPushButton("  Wróć do wyboru wideo", nav_card)
        self.btn_step2_back.setProperty("class", "btnSecondary")
        self.btn_step2_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step2_back.setFixedHeight(38)
        nc_layout.addWidget(self.btn_step2_back)

        nc_layout.addStretch()

        self.btn_step2_next = QPushButton("  Dalej: Eksport i Renderowanie", nav_card)
        self.btn_step2_next.setProperty("class", "btnPrimary")
        self.btn_step2_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step2_next.setFixedHeight(38)
        nc_layout.addWidget(self.btn_step2_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)
