from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QGroupBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QSlider, QCheckBox, QComboBox, QScrollArea
)
from lucide_icons import get_lucide_icon, get_lucide_pixmap
from ..widgets import VideoPreviewWidget, FastDraftInlineWidget
from ..utils import apply_card_shadow
from i18n import tr


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

        self.lbl_h_title = QLabel(tr("step2_title"), header_card)
        self.lbl_h_title.setProperty("class", "pageHeaderTitle")
        self.lbl_h_sub = QLabel(tr("step2_subtitle"), header_card)
        self.lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(self.lbl_h_title)
        h_layout.addWidget(self.lbl_h_sub)
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

        self.lbl_v_desc = QLabel(tr("desc_volcano"), tab_volcano)
        self.lbl_v_desc.setWordWrap(True)
        self.lbl_v_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_v_row.addWidget(self.lbl_v_desc, 1)
        tab_v_layout.addLayout(desc_v_row)

        self.ts_box = QGroupBox(tr("group_time_window"), tab_volcano)
        ts_box_layout = QVBoxLayout(self.ts_box)
        ts_box_layout.setContentsMargins(12, 8, 12, 6)
        ts_box_layout.setSpacing(6)

        ts_start_layout = QHBoxLayout()
        self.lbl_start = QLabel(tr("lbl_time_start"), tab_volcano)
        self.lbl_start.setStyleSheet("font-weight: 600; color: #475569;")
        self.lbl_start.setFixedWidth(160)
        self.txt_ts_start = QLineEdit(tab_volcano)
        self.txt_ts_start.setPlaceholderText("00:00")
        self.txt_ts_start.setText("00:00")

        self.btn_set_curr_start = QPushButton(tr("btn_from_cursor"), tab_volcano)
        self.btn_set_curr_start.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))

        ts_start_layout.addWidget(self.lbl_start)
        ts_start_layout.addWidget(self.txt_ts_start, 1)
        ts_start_layout.addWidget(self.btn_set_curr_start)
        ts_box_layout.addLayout(ts_start_layout)

        ts_end_layout = QHBoxLayout()
        self.lbl_end = QLabel(tr("lbl_time_end"), tab_volcano)
        self.lbl_end.setStyleSheet("font-weight: 600; color: #475569;")
        self.lbl_end.setFixedWidth(160)
        self.txt_ts_end = QLineEdit(tab_volcano)
        self.txt_ts_end.setPlaceholderText("00:30")
        self.txt_ts_end.setText("00:30")

        self.btn_set_curr_end = QPushButton(tr("btn_from_cursor"), tab_volcano)
        self.btn_set_curr_end.setIcon(get_lucide_icon("clock", color="#1e293b", size=14))

        ts_end_layout.addWidget(self.lbl_end)
        ts_end_layout.addWidget(self.txt_ts_end, 1)
        ts_end_layout.addWidget(self.btn_set_curr_end)
        ts_box_layout.addLayout(ts_end_layout)

        self.lbl_ts_validation = QLabel(tr("ts_format_hint"), tab_volcano)
        self.lbl_ts_validation.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5fa; "
            "border: 1px solid #dce4ef; border-radius: 7px; padding: 3px 8px; margin-top: 1px;"
        )
        self.lbl_ts_validation.setWordWrap(True)
        ts_box_layout.addWidget(self.lbl_ts_validation)

        tab_v_layout.addWidget(self.ts_box)
        tab_v_layout.addStretch(1)
        self.tabs.addTab(tab_volcano, get_lucide_icon("flame", color="#475569"), tr("tab_volcano"))

        # --- Tab 2: Motion Smear ---
        tab_smear = QWidget()
        tab_s_layout = QVBoxLayout(tab_smear)
        tab_s_layout.setContentsMargins(10, 8, 10, 6)
        tab_s_layout.setSpacing(6)

        desc_s_row = QHBoxLayout()
        desc_s_row.setContentsMargins(0, 0, 0, 2)
        desc_s_row.setSpacing(10)
        desc_s_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_s_desc = QLabel(tr("desc_smear"), tab_smear)
        self.lbl_s_desc.setWordWrap(True)
        self.lbl_s_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_s_row.addWidget(self.lbl_s_desc, 1)
        tab_s_layout.addLayout(desc_s_row)

        self.s_box = QGroupBox(tr("group_smear_params"), tab_smear)
        s_box_layout = QVBoxLayout(self.s_box)
        s_box_layout.setContentsMargins(12, 8, 12, 6)
        s_box_layout.setSpacing(6)

        s_repeat_row = QHBoxLayout()
        self.s_repeat_lbl = QLabel(tr("lbl_repeat_count"), tab_smear)
        self.s_repeat_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.s_repeat_lbl.setFixedWidth(210)
        self.spin_s_repeat = QSpinBox(tab_smear)
        self.spin_s_repeat.setRange(2, 60)
        self.spin_s_repeat.setValue(15)
        s_repeat_row.addWidget(self.s_repeat_lbl)
        s_repeat_row.addWidget(self.spin_s_repeat, 1)
        s_box_layout.addLayout(s_repeat_row)

        s_freq_row = QHBoxLayout()
        self.s_freq_lbl = QLabel(tr("lbl_frequency"), tab_smear)
        self.s_freq_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.s_freq_lbl.setFixedWidth(210)
        self.spin_s_freq = QSpinBox(tab_smear)
        self.spin_s_freq.setRange(1, 30)
        self.spin_s_freq.setValue(5)
        s_freq_row.addWidget(self.s_freq_lbl)
        s_freq_row.addWidget(self.spin_s_freq, 1)
        s_box_layout.addLayout(s_freq_row)

        tab_s_layout.addWidget(self.s_box)
        tab_s_layout.addStretch(1)
        self.tabs.addTab(tab_smear, get_lucide_icon("wind", color="#475569"), tr("tab_smear"))

        # --- Tab 3: Stitch Mosh ---
        tab_stitch = QWidget()
        tab_st_layout = QVBoxLayout(tab_stitch)
        tab_st_layout.setContentsMargins(10, 8, 10, 6)
        tab_st_layout.setSpacing(6)

        desc_st_row = QHBoxLayout()
        desc_st_row.setContentsMargins(0, 0, 0, 2)
        desc_st_row.setSpacing(10)
        desc_st_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_st_desc = QLabel(tr("desc_stitch"), tab_stitch)
        self.lbl_st_desc.setWordWrap(True)
        self.lbl_st_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_st_row.addWidget(self.lbl_st_desc, 1)
        tab_st_layout.addLayout(desc_st_row)

        self.st_box = QGroupBox(tr("group_stitch_params"), tab_stitch)
        st_box_layout = QVBoxLayout(self.st_box)
        st_box_layout.setContentsMargins(12, 8, 12, 6)
        st_box_layout.setSpacing(6)

        file_b_layout = QHBoxLayout()
        self.btn_select_b = QPushButton(tr("btn_select_b"), tab_stitch)
        self.btn_select_b.setIcon(get_lucide_icon("folder-open", color="#1e293b", size=15))

        self.lbl_file_b_path = QLabel(tr("lbl_no_b_selected"), tab_stitch)
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

        tab_st_layout.addWidget(self.st_box)
        tab_st_layout.addStretch(1)
        self.tabs.addTab(tab_stitch, get_lucide_icon("shuffle", color="#475569"), tr("tab_stitch"))

        # --- Tab 4: Cyber Glitch ---
        tab_cyber = QWidget()
        tab_c_layout = QVBoxLayout(tab_cyber)
        tab_c_layout.setContentsMargins(10, 8, 10, 6)
        tab_c_layout.setSpacing(6)

        desc_c_row = QHBoxLayout()
        desc_c_row.setContentsMargins(0, 0, 0, 2)
        desc_c_row.setSpacing(10)
        desc_c_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_c_desc = QLabel(tr("desc_cyber"), tab_cyber)
        self.lbl_c_desc.setWordWrap(True)
        self.lbl_c_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_c_row.addWidget(self.lbl_c_desc, 1)
        tab_c_layout.addLayout(desc_c_row)

        self.c_box = QGroupBox(tr("group_cyber_params"), tab_cyber)
        c_box_layout = QVBoxLayout(self.c_box)
        c_box_layout.setContentsMargins(12, 8, 12, 6)
        c_box_layout.setSpacing(6)

        self.c_rate_lbl = QLabel(tr("lbl_corrupt_rate"), tab_cyber)
        self.c_rate_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        c_box_layout.addWidget(self.c_rate_lbl)
        self.slider_c_rate = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_rate.setRange(1, 30)
        self.slider_c_rate.setValue(8)
        c_box_layout.addWidget(self.slider_c_rate)

        self.c_int_lbl = QLabel(tr("lbl_corrupt_intensity"), tab_cyber)
        self.c_int_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        c_box_layout.addWidget(self.c_int_lbl)
        self.slider_c_intensity = QSlider(Qt.Orientation.Horizontal, tab_cyber)
        self.slider_c_intensity.setRange(1, 20)
        self.slider_c_intensity.setValue(3)
        c_box_layout.addWidget(self.slider_c_intensity)

        tab_c_layout.addWidget(self.c_box)
        tab_c_layout.addStretch(1)
        self.tabs.addTab(tab_cyber, get_lucide_icon("cpu", color="#475569"), tr("tab_cyber"))

        # --- Tab 5: Flow Drift ---
        tab_flow = QWidget()
        tab_fl_layout = QVBoxLayout(tab_flow)
        tab_fl_layout.setContentsMargins(10, 8, 10, 6)
        tab_fl_layout.setSpacing(6)

        desc_fl_row = QHBoxLayout()
        desc_fl_row.setContentsMargins(0, 0, 0, 2)
        desc_fl_row.setSpacing(10)
        desc_fl_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_fl_desc = QLabel(tr("desc_flow"), tab_flow)
        self.lbl_fl_desc.setWordWrap(True)
        self.lbl_fl_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_fl_row.addWidget(self.lbl_fl_desc, 1)
        tab_fl_layout.addLayout(desc_fl_row)

        self.fl_box = QGroupBox(tr("group_flow_params"), tab_flow)
        fl_box_layout = QVBoxLayout(self.fl_box)
        fl_box_layout.setContentsMargins(12, 8, 12, 6)
        fl_box_layout.setSpacing(6)

        fl_scale_row = QHBoxLayout()
        self.fl_scale_lbl = QLabel(tr("lbl_flow_scale"), tab_flow)
        self.fl_scale_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.fl_scale_lbl.setFixedWidth(210)
        self.spin_fl_scale = QDoubleSpinBox(tab_flow)
        self.spin_fl_scale.setRange(0.5, 10.0)
        self.spin_fl_scale.setSingleStep(0.5)
        self.spin_fl_scale.setValue(2.5)
        fl_scale_row.addWidget(self.fl_scale_lbl)
        fl_scale_row.addWidget(self.spin_fl_scale, 1)
        fl_box_layout.addLayout(fl_scale_row)

        fl_decay_row = QHBoxLayout()
        self.fl_decay_lbl = QLabel(tr("lbl_trail_decay"), tab_flow)
        self.fl_decay_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.fl_decay_lbl.setFixedWidth(210)
        self.spin_fl_decay = QDoubleSpinBox(tab_flow)
        self.spin_fl_decay.setRange(0.50, 0.98)
        self.spin_fl_decay.setSingleStep(0.05)
        self.spin_fl_decay.setValue(0.85)
        fl_decay_row.addWidget(self.fl_decay_lbl)
        fl_decay_row.addWidget(self.spin_fl_decay, 1)
        fl_box_layout.addLayout(fl_decay_row)

        tab_fl_layout.addWidget(self.fl_box)
        tab_fl_layout.addStretch(1)
        self.tabs.addTab(tab_flow, get_lucide_icon("waves", color="#475569"), tr("tab_flow"))

        # --- Tab 6: RGB Split ---
        tab_rgb = QWidget()
        tab_rgb_layout = QVBoxLayout(tab_rgb)
        tab_rgb_layout.setContentsMargins(10, 8, 10, 6)
        tab_rgb_layout.setSpacing(6)

        desc_rgb_row = QHBoxLayout()
        desc_rgb_row.setContentsMargins(0, 0, 0, 2)
        desc_rgb_row.setSpacing(10)
        desc_rgb_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.lbl_rgb_desc = QLabel(tr("desc_rgb"), tab_rgb)
        self.lbl_rgb_desc.setWordWrap(True)
        self.lbl_rgb_desc.setStyleSheet("color: #64748b; font-size: 12.5px; font-weight: 500;")
        desc_rgb_row.addWidget(self.lbl_rgb_desc, 1)
        tab_rgb_layout.addLayout(desc_rgb_row)

        self.rgb_box = QGroupBox(tr("group_rgb_params"), tab_rgb)
        rgb_box_layout = QVBoxLayout(self.rgb_box)
        rgb_box_layout.setContentsMargins(12, 8, 12, 6)
        rgb_box_layout.setSpacing(5)

        rgb_delay_row = QHBoxLayout()
        self.rgb_delay_lbl = QLabel(tr("lbl_rgb_delay"), tab_rgb)
        self.rgb_delay_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.rgb_delay_lbl.setFixedWidth(220)
        self.spin_rgb_delay = QSpinBox(tab_rgb)
        self.spin_rgb_delay.setRange(0, 20)
        self.spin_rgb_delay.setValue(4)
        rgb_delay_row.addWidget(self.rgb_delay_lbl)
        rgb_delay_row.addWidget(self.spin_rgb_delay, 1)
        rgb_box_layout.addLayout(rgb_delay_row)

        rgb_shift_row = QHBoxLayout()
        self.rgb_shift_lbl = QLabel(tr("lbl_rgb_shift"), tab_rgb)
        self.rgb_shift_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.rgb_shift_lbl.setFixedWidth(220)
        self.spin_rgb_shift = QSpinBox(tab_rgb)
        self.spin_rgb_shift.setRange(0, 40)
        self.spin_rgb_shift.setValue(8)
        rgb_shift_row.addWidget(self.rgb_shift_lbl)
        rgb_shift_row.addWidget(self.spin_rgb_shift, 1)
        rgb_box_layout.addLayout(rgb_shift_row)

        rgb_dir_row = QHBoxLayout()
        self.rgb_dir_lbl = QLabel(tr("lbl_rgb_direction"), tab_rgb)
        self.rgb_dir_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        self.rgb_dir_lbl.setFixedWidth(220)
        self.combo_rgb_direction = QComboBox(tab_rgb)
        self.combo_rgb_direction.addItem(tr("rgb_dir_horizontal"), "horizontal")
        self.combo_rgb_direction.addItem(tr("rgb_dir_diagonal"), "diagonal")
        self.combo_rgb_direction.addItem(tr("rgb_dir_vertical"), "vertical")
        rgb_dir_row.addWidget(self.rgb_dir_lbl)
        rgb_dir_row.addWidget(self.combo_rgb_direction, 1)
        rgb_box_layout.addLayout(rgb_dir_row)

        self.rgb_jitter_lbl = QLabel(tr("lbl_rgb_jitter"), tab_rgb)
        self.rgb_jitter_lbl.setStyleSheet("font-weight: 600; color: #475569;")
        rgb_box_layout.addWidget(self.rgb_jitter_lbl)
        self.slider_rgb_jitter = QSlider(Qt.Orientation.Horizontal, tab_rgb)
        self.slider_rgb_jitter.setRange(0, 50)
        self.slider_rgb_jitter.setValue(10)
        rgb_box_layout.addWidget(self.slider_rgb_jitter)

        tab_rgb_layout.addWidget(self.rgb_box)
        tab_rgb_layout.addStretch(1)
        self.tabs.addTab(tab_rgb, get_lucide_icon("split", color="#475569"), tr("tab_rgb"))

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
        self.lbl_opts_title = QLabel(tr("group_export_settings"), opts_card)
        self.lbl_opts_title.setProperty("class", "sectionTitle")
        opts_hdr.addWidget(self.lbl_opts_title)
        opts_hdr.addStretch()
        opts_card_layout.addLayout(opts_hdr)

        self.chk_keep_audio = QCheckBox(tr("chk_keep_audio"), opts_card)
        self.chk_keep_audio.setChecked(True)
        opts_card_layout.addWidget(self.chk_keep_audio)

        out_file_layout = QHBoxLayout()
        out_file_layout.setSpacing(8)
        self.btn_select_out = QPushButton(tr("btn_change_out"), opts_card)
        self.btn_select_out.setIcon(get_lucide_icon("save", color="#1e293b", size=15))

        self.lbl_out_path = QLabel(tr("lbl_auto_out"), opts_card)
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

        self.btn_step2_back = QPushButton(tr("btn_step2_back"), nav_card)
        self.btn_step2_back.setProperty("class", "btnSecondary")
        self.btn_step2_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step2_back.setFixedHeight(36)
        nc_layout.addWidget(self.btn_step2_back)

        nc_layout.addStretch()

        self.btn_step2_next = QPushButton(tr("btn_step2_next"), nav_card)
        self.btn_step2_next.setProperty("class", "btnPrimary")
        self.btn_step2_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step2_next.setFixedHeight(36)
        nc_layout.addWidget(self.btn_step2_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

    def retranslate_ui(self):
        """Retranslates all text on Step 2."""
        self.lbl_h_title.setText(tr("step2_title"))
        self.lbl_h_sub.setText(tr("step2_subtitle"))

        # Tabs
        self.tabs.setTabText(0, tr("tab_volcano"))
        self.tabs.setTabText(1, tr("tab_smear"))
        self.tabs.setTabText(2, tr("tab_stitch"))
        self.tabs.setTabText(3, tr("tab_cyber"))
        self.tabs.setTabText(4, tr("tab_flow"))
        self.tabs.setTabText(5, tr("tab_rgb"))

        # Tab 1
        self.lbl_v_desc.setText(tr("desc_volcano"))
        self.ts_box.setTitle(tr("group_time_window"))
        self.lbl_start.setText(tr("lbl_time_start"))
        self.lbl_end.setText(tr("lbl_time_end"))
        self.btn_set_curr_start.setText(tr("btn_from_cursor"))
        self.btn_set_curr_end.setText(tr("btn_from_cursor"))

        # Tab 2
        self.lbl_s_desc.setText(tr("desc_smear"))
        self.s_box.setTitle(tr("group_smear_params"))
        self.s_repeat_lbl.setText(tr("lbl_repeat_count"))
        self.s_freq_lbl.setText(tr("lbl_frequency"))

        # Tab 3
        self.lbl_st_desc.setText(tr("desc_stitch"))
        self.st_box.setTitle(tr("group_stitch_params"))
        self.btn_select_b.setText(tr("btn_select_b"))

        # Tab 4
        self.lbl_c_desc.setText(tr("desc_cyber"))
        self.c_box.setTitle(tr("group_cyber_params"))
        self.c_rate_lbl.setText(tr("lbl_corrupt_rate"))
        self.c_int_lbl.setText(tr("lbl_corrupt_intensity"))

        # Tab 5
        self.lbl_fl_desc.setText(tr("desc_flow"))
        self.fl_box.setTitle(tr("group_flow_params"))
        self.fl_scale_lbl.setText(tr("lbl_flow_scale"))
        self.fl_decay_lbl.setText(tr("lbl_trail_decay"))

        # Tab 6
        self.lbl_rgb_desc.setText(tr("desc_rgb"))
        self.rgb_box.setTitle(tr("group_rgb_params"))
        self.rgb_delay_lbl.setText(tr("lbl_rgb_delay"))
        self.rgb_shift_lbl.setText(tr("lbl_rgb_shift"))
        self.rgb_dir_lbl.setText(tr("lbl_rgb_direction"))
        cur_dir_idx = self.combo_rgb_direction.currentIndex()
        self.combo_rgb_direction.setItemText(0, tr("rgb_dir_horizontal"))
        self.combo_rgb_direction.setItemText(1, tr("rgb_dir_diagonal"))
        self.combo_rgb_direction.setItemText(2, tr("rgb_dir_vertical"))
        self.combo_rgb_direction.setCurrentIndex(cur_dir_idx)
        self.rgb_jitter_lbl.setText(tr("lbl_rgb_jitter"))

        # Fast draft
        self.fast_draft_widget.retranslate_ui()

        # Export & Audio
        self.lbl_opts_title.setText(tr("group_export_settings"))
        self.chk_keep_audio.setText(tr("chk_keep_audio"))
        self.btn_select_out.setText(tr("btn_change_out"))

        # Nav
        self.btn_step2_back.setText(tr("btn_step2_back"))
        self.btn_step2_next.setText(tr("btn_step2_next"))

    def _on_tab_changed(self, idx):
        if 0 <= idx < len(self.desc_rows):
            self.fast_draft_widget.pause()
            self.fast_draft_widget.show_button()
            self.desc_rows[idx].addWidget(self.fast_draft_widget)

    def reset_parameters(self):
        """Resets all effect parameters and export configurations to default initial values."""
        self.tabs.setCurrentIndex(0)
        self.txt_ts_start.setText("00:00")
        self.txt_ts_end.setText("00:30")
        self.lbl_ts_validation.setText(tr("ts_format_hint"))
        self.lbl_ts_validation.setStyleSheet(
            "font-size: 11px; font-weight: 600; color: #64748b; background-color: #f1f5fa; "
            "border: 1px solid #dce4ef; border-radius: 7px; padding: 3px 8px; margin-top: 1px;"
        )
        self.spin_s_repeat.setValue(15)
        self.spin_s_freq.setValue(5)
        self.lbl_file_b_path.setText(tr("lbl_no_b_selected"))
        self.slider_c_rate.setValue(8)
        self.slider_c_intensity.setValue(3)
        self.spin_fl_scale.setValue(2.5)
        self.spin_fl_decay.setValue(0.85)
        self.spin_rgb_delay.setValue(4)
        self.spin_rgb_shift.setValue(8)
        self.combo_rgb_direction.setCurrentIndex(0)
        self.slider_rgb_jitter.setValue(10)
        self.chk_keep_audio.setChecked(True)
        self.lbl_out_path.setText(tr("lbl_auto_out"))
        self.fast_draft_widget.reset()
