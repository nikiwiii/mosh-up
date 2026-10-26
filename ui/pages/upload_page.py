from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QGroupBox
)
from lucide_icons import get_lucide_icon
from ..widgets import DropAreaWidget, VideoPreviewWidget
from ..utils import apply_card_shadow


class UploadPage(QWidget):
    """
    Step 1: Upload Video Page.
    Allows drag-and-drop or browsing for video, and displays technical metadata
    along with the source video player once loaded.
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
        self.upload_content_stack = QStackedWidget(self)

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
        dc_layout.addWidget(self.drop_area, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_browse_empty = QPushButton("  Wybierz plik wideo z dysku...", drop_card)
        self.btn_browse_empty.setProperty("class", "btnPrimary")
        self.btn_browse_empty.setIcon(get_lucide_icon("folder-open", color="#ffffff", size=17))
        self.btn_browse_empty.setFixedHeight(44)
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
        mc_layout.addWidget(self.btn_replace_video)

        apply_card_shadow(meta_card)
        vl_layout.addWidget(meta_card, 2)

        self.upload_content_stack.addWidget(view_loaded)
        layout.addWidget(self.upload_content_stack, 1)

        # Bottom Navigation Bar
        nav_card = QFrame(self)
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
        nc_layout.addWidget(self.btn_step1_next)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)
