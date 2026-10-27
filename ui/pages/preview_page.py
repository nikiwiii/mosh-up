from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from lucide_icons import get_lucide_icon
from ..widgets import VideoPreviewWidget
from ..utils import apply_card_shadow
from i18n import tr


class PreviewPage(QWidget):
    """
    Step 4: Video Preview & Comparison Page.
    Enables playback of the final rendered video, toggle between original and moshed,
    and actions to open the file/folder or start a new project.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Page Header Card
        header_card = QFrame(self)
        header_card.setProperty("class", "softCard")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(18, 12, 18, 12)
        h_layout.setSpacing(12)

        titles_vbox = QVBoxLayout()
        titles_vbox.setSpacing(4)
        self.lbl_h_title = QLabel(tr("step4_title"), header_card)
        self.lbl_h_title.setProperty("class", "pageHeaderTitle")
        self.lbl_h_sub = QLabel(tr("step4_subtitle"), header_card)
        self.lbl_h_sub.setProperty("class", "pageHeaderSubtitle")
        titles_vbox.addWidget(self.lbl_h_title)
        titles_vbox.addWidget(self.lbl_h_sub)
        h_layout.addLayout(titles_vbox, 1)

        # Comparison Toggle Buttons
        comp_group = QHBoxLayout()
        comp_group.setSpacing(6)

        self.btn_view_result = QPushButton(tr("btn_toggle_effect"), header_card)
        self.btn_view_result.setProperty("class", "btnPrimary")
        self.btn_view_result.setIcon(get_lucide_icon("sparkles", color="#ffffff", size=15))
        self.btn_view_result.setFixedHeight(36)

        self.btn_view_source = QPushButton(tr("btn_toggle_source"), header_card)
        self.btn_view_source.setProperty("class", "btnSecondary")
        self.btn_view_source.setIcon(get_lucide_icon("film", color="#1e293b", size=15))
        self.btn_view_source.setFixedHeight(36)

        comp_group.addWidget(self.btn_view_result)
        comp_group.addWidget(self.btn_view_source)
        h_layout.addLayout(comp_group)

        apply_card_shadow(header_card)
        layout.addWidget(header_card)

        # Large Video Player Card
        player_card = QFrame(self)
        player_card.setProperty("class", "softCard")
        pc_layout = QVBoxLayout(player_card)
        pc_layout.setContentsMargins(18, 16, 18, 16)
        pc_layout.setSpacing(10)

        self.preview_player = VideoPreviewWidget(player_card, min_height=320)
        pc_layout.addWidget(self.preview_player, 1)

        apply_card_shadow(player_card)
        layout.addWidget(player_card, 1)

        # Actions Card
        actions_card = QFrame(self)
        actions_card.setProperty("class", "softCard")
        ac_layout = QVBoxLayout(actions_card)
        ac_layout.setContentsMargins(18, 12, 18, 12)
        ac_layout.setSpacing(10)

        # File path label
        file_row = QHBoxLayout()
        self.lbl_file_tag = QLabel(tr("lbl_location"), actions_card)
        self.lbl_file_tag.setStyleSheet("font-weight: 700; color: #475569; font-size: 12px;")
        self.lbl_file_tag.setFixedWidth(120)

        self.lbl_result_path = QLabel(tr("lbl_no_output_file"), actions_card)
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

        file_row.addWidget(self.lbl_file_tag)
        file_row.addWidget(self.lbl_result_path, 1)
        ac_layout.addLayout(file_row)

        # Action Buttons Row
        action_btn_row = QHBoxLayout()
        action_btn_row.setSpacing(10)

        self.btn_open_video = QPushButton(tr("btn_open_system_player"), actions_card)
        self.btn_open_video.setProperty("class", "btnPrimary")
        self.btn_open_video.setIcon(get_lucide_icon("play", color="#ffffff", size=15))
        self.btn_open_video.setFixedHeight(38)

        self.btn_open_folder = QPushButton(tr("btn_open_folder"), actions_card)
        self.btn_open_folder.setProperty("class", "btnSecondary")
        self.btn_open_folder.setIcon(get_lucide_icon("folder-open", color="#334155", size=15))
        self.btn_open_folder.setFixedHeight(38)

        self.btn_tweak_params = QPushButton(tr("btn_tweak_params"), actions_card)
        self.btn_tweak_params.setProperty("class", "btnSecondary")
        self.btn_tweak_params.setIcon(get_lucide_icon("sliders", color="#334155", size=15))
        self.btn_tweak_params.setFixedHeight(38)

        self.btn_new_project = QPushButton(tr("btn_new_project"), actions_card)
        self.btn_new_project.setProperty("class", "btnSecondary")
        self.btn_new_project.setIcon(get_lucide_icon("rotate-ccw", color="#334155", size=15))
        self.btn_new_project.setFixedHeight(38)

        action_btn_row.addWidget(self.btn_open_video)
        action_btn_row.addWidget(self.btn_open_folder)
        action_btn_row.addWidget(self.btn_tweak_params)
        action_btn_row.addWidget(self.btn_new_project)
        ac_layout.addLayout(action_btn_row)

        apply_card_shadow(actions_card)
        layout.addWidget(actions_card)

        # Bottom Navigation Bar
        nav_card = QFrame(self)
        nav_card.setObjectName("wizardNavBar")
        nc_layout = QHBoxLayout(nav_card)
        nc_layout.setContentsMargins(14, 8, 14, 8)

        self.btn_step4_back = QPushButton(tr("btn_step4_back"), nav_card)
        self.btn_step4_back.setProperty("class", "btnSecondary")
        self.btn_step4_back.setIcon(get_lucide_icon("arrow-left", color="#334155", size=15))
        self.btn_step4_back.setFixedHeight(38)
        nc_layout.addWidget(self.btn_step4_back)

        nc_layout.addStretch()

        self.btn_step4_restart = QPushButton(tr("btn_step4_restart"), nav_card)
        self.btn_step4_restart.setProperty("class", "btnSecondary")
        self.btn_step4_restart.setIcon(get_lucide_icon("rotate-ccw", color="#334155", size=15))
        self.btn_step4_restart.setFixedHeight(38)
        nc_layout.addWidget(self.btn_step4_restart)

        apply_card_shadow(nav_card, blur=10, offset_y=2, alpha=20)
        layout.addWidget(nav_card)

    def retranslate_ui(self):
        """Retranslates all text on Step 4."""
        self.lbl_h_title.setText(tr("step4_title"))
        self.lbl_h_sub.setText(tr("step4_subtitle"))
        self.btn_view_result.setText(tr("btn_toggle_effect"))
        self.btn_view_source.setText(tr("btn_toggle_source"))
        self.lbl_file_tag.setText(tr("lbl_location"))
        self.btn_open_video.setText(tr("btn_open_system_player"))
        self.btn_open_folder.setText(tr("btn_open_folder"))
        self.btn_tweak_params.setText(tr("btn_tweak_params"))
        self.btn_new_project.setText(tr("btn_new_project"))
        self.btn_step4_back.setText(tr("btn_step4_back"))
        self.btn_step4_restart.setText(tr("btn_step4_restart"))
        self.preview_player.retranslate_ui()
