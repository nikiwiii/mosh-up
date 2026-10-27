from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QTextEdit
)
from lucide_icons import get_lucide_icon, get_lucide_pixmap
from ..utils import apply_card_shadow
from i18n import tr


class RenderPage(QWidget):
    """
    Step 3: Export & Render Page.
    Displays a comprehensive summary card of the chosen configuration,
    the large render launch button, real-time progress bar, and log console.
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

        self.lbl_h_title = QLabel(tr("step3_title"), header_card)
        self.lbl_h_title.setProperty("class", "pageHeaderTitle")
        self.lbl_h_sub = QLabel(tr("step3_subtitle"), header_card)
        self.lbl_h_sub.setProperty("class", "pageHeaderSubtitle")

        h_layout.addWidget(self.lbl_h_title)
        h_layout.addWidget(self.lbl_h_sub)
        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Priority Summary Card
        self.summary_card = QFrame(self)
        self.summary_card.setProperty("class", "softCard")
        sum_layout = QVBoxLayout(self.summary_card)
        sum_layout.setContentsMargins(20, 16, 20, 16)
        sum_layout.setSpacing(12)

        sum_hdr = QHBoxLayout()
        self.lbl_sum_hdr = QLabel(tr("summary_hdr"), self.summary_card)
        self.lbl_sum_hdr.setProperty("class", "sectionTitle")
        sum_hdr.addWidget(self.lbl_sum_hdr)
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
        self.lbl_src_title = QLabel(tr("tile1_title"), tile_src)
        self.lbl_src_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_src.addWidget(icon_src)
        th_src.addWidget(self.lbl_src_title)
        th_src.addStretch()
        ts_layout.addLayout(th_src)

        self.lbl_sum_src_name = QLabel("-", tile_src)
        self.lbl_sum_src_name.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_src_name.setWordWrap(True)
        self.lbl_sum_src_meta1 = QLabel("-", tile_src)
        self.lbl_sum_src_meta1.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_src_meta2 = QLabel("-", tile_src)
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
        self.lbl_mode_title = QLabel(tr("tile2_title"), tile_mode)
        self.lbl_mode_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_mode.addWidget(icon_mode)
        th_mode.addWidget(self.lbl_mode_title)
        th_mode.addStretch()
        tm_layout.addLayout(th_mode)

        self.lbl_sum_mode_name = QLabel("Volcano Melt", tile_mode)
        self.lbl_sum_mode_name.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_param1 = QLabel("-", tile_mode)
        self.lbl_sum_param1.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_param2 = QLabel("-", tile_mode)
        self.lbl_sum_param2.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")

        tm_layout.addWidget(self.lbl_sum_mode_name)
        tm_layout.addWidget(self.lbl_sum_param1)
        tm_layout.addWidget(self.lbl_sum_param2)
        row1.addWidget(tile_mode, 1)

        grid_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)

        # Tile 3: Audio
        tile_audio = QFrame(self.summary_card)
        tile_audio.setProperty("class", "insetCard")
        ta_layout = QVBoxLayout(tile_audio)
        ta_layout.setContentsMargins(14, 12, 14, 12)
        ta_layout.setSpacing(6)

        th_audio = QHBoxLayout()
        icon_audio = QLabel(tile_audio)
        icon_audio.setPixmap(get_lucide_pixmap("music", color="#475569", size=18))
        self.lbl_audio_title = QLabel(tr("tile3_title"), tile_audio)
        self.lbl_audio_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_audio.addWidget(icon_audio)
        th_audio.addWidget(self.lbl_audio_title)
        th_audio.addStretch()
        ta_layout.addLayout(th_audio)

        self.lbl_sum_audio_status = QLabel(tr("tile_audio_on"), tile_audio)
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
        self.lbl_out_title = QLabel(tr("tile4_title"), tile_out)
        self.lbl_out_title.setStyleSheet("font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.3px;")
        th_out.addWidget(icon_out)
        th_out.addWidget(self.lbl_out_title)
        th_out.addStretch()
        to_layout.addLayout(th_out)

        self.lbl_sum_output_file = QLabel("moshup_output.mp4", tile_out)
        self.lbl_sum_output_file.setStyleSheet("font-size: 13.5px; font-weight: 700; color: #0f172a;")
        self.lbl_sum_output_file.setWordWrap(True)
        self.lbl_sum_output_dir = QLabel(tr("tile_dir_label", folder="-"), tile_out)
        self.lbl_sum_output_dir.setStyleSheet("font-size: 11.5px; font-weight: 500; color: #475569;")
        self.lbl_sum_output_dir.setWordWrap(True)

        to_layout.addWidget(self.lbl_sum_output_file)
        to_layout.addWidget(self.lbl_sum_output_dir)
        to_layout.addStretch()
        row2.addWidget(tile_out, 1)

        grid_layout.addLayout(row2)
        sum_layout.addLayout(grid_layout)

        apply_card_shadow(self.summary_card)
        layout.addWidget(self.summary_card, 1)

        # Action & Progress Card
        action_card = QFrame(self)
        action_card.setProperty("class", "softCard")
        ac_layout = QVBoxLayout(action_card)
        ac_layout.setContentsMargins(18, 14, 18, 14)
        ac_layout.setSpacing(10)

        # Big Start Button
        self.btn_start = QPushButton(tr("btn_start_mosh"), action_card)
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setProperty("class", "btnPrimary")
        self.btn_start.setIcon(get_lucide_icon("rocket", color="#ffffff", size=20))
        self.btn_start.setIconSize(QSize(20, 20))
        self.btn_start.setFixedHeight(46)
        self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
        ac_layout.addWidget(self.btn_start)

        # Progress Row
        progress_row = QHBoxLayout()
        progress_row.setSpacing(12)

        self.lbl_status = QLabel(tr("status_ready"), action_card)
        self.lbl_status.setStyleSheet("font-weight: 700; color: #1e293b; font-size: 12.5px;")

        self.progress_bar = QProgressBar(action_card)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(18)

        progress_row.addWidget(self.lbl_status)
        progress_row.addWidget(self.progress_bar, 1)
        ac_layout.addLayout(progress_row)

        apply_card_shadow(action_card)
        layout.addWidget(action_card, 0)

        # Compact Console Card
        log_card = QFrame(self)
        log_card.setProperty("class", "softCard")
        lc_layout = QVBoxLayout(log_card)
        lc_layout.setContentsMargins(16, 8, 16, 10)
        lc_layout.setSpacing(6)

        log_hdr = QHBoxLayout()
        icon_log = QLabel(log_card)
        icon_log.setPixmap(get_lucide_pixmap("terminal", color="#64748b", size=15))
        self.lbl_log_title = QLabel(tr("console_title"), log_card)
        self.lbl_log_title.setStyleSheet("font-size: 11.5px; font-weight: 700; color: #64748b;")
        log_hdr.addWidget(icon_log)
        log_hdr.addWidget(self.lbl_log_title)
        log_hdr.addStretch()
        lc_layout.addLayout(log_hdr)

        self.log_console = QTextEdit(log_card)
        self.log_console.setReadOnly(True)
        self.log_console.setFixedHeight(75)
        self.log_console.setPlaceholderText(tr("console_placeholder"))
        lc_layout.addWidget(self.log_console)

        apply_card_shadow(log_card)
        layout.addWidget(log_card, 0)

        # Bottom Navigation Bar
        nav_card = QFrame(self)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step3_back = QPushButton(tr("btn_step3_back"), nav_card)
        self.btn_step3_back.setProperty("class", "btnSecondary")
        self.btn_step3_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step3_back.setFixedHeight(38)
        nc_layout.addWidget(self.btn_step3_back)

        nc_layout.addStretch()

        self.btn_step3_next = QPushButton(tr("btn_step3_next"), nav_card)
        self.btn_step3_next.setProperty("class", "btnPrimary")
        self.btn_step3_next.setIcon(get_lucide_icon("arrow-right", color="#ffffff", size=15))
        self.btn_step3_next.setFixedHeight(38)
        self.btn_step3_next.setEnabled(False)
        nc_layout.addWidget(self.btn_step3_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

    def retranslate_ui(self):
        """Retranslates all text on Step 3."""
        self.lbl_h_title.setText(tr("step3_title"))
        self.lbl_h_sub.setText(tr("step3_subtitle"))
        self.lbl_sum_hdr.setText(tr("summary_hdr"))
        self.lbl_src_title.setText(tr("tile1_title"))
        self.lbl_mode_title.setText(tr("tile2_title"))
        self.lbl_audio_title.setText(tr("tile3_title"))
        self.lbl_out_title.setText(tr("tile4_title"))
        self.btn_start.setText(tr("btn_start_mosh"))
        self.lbl_log_title.setText(tr("console_title"))
        self.log_console.setPlaceholderText(tr("console_placeholder"))
        self.btn_step3_back.setText(tr("btn_step3_back"))
        self.btn_step3_next.setText(tr("btn_step3_next"))
