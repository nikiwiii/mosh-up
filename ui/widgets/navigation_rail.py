from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton
from lucide_icons import get_lucide_icon
from ..utils import apply_card_shadow
from i18n import tr, get_language


class NavigationRail(QFrame):
    """
    Vertical navigation rail displayed on the left of the application window.
    Contains buttons for each wizard step, language toggle, reset button, and info button.
    """
    step_selected = Signal(int)
    language_toggle_requested = Signal()
    reset_requested = Signal()
    info_requested = Signal()

    STEP_KEYS = [
        ("file-video", "nav_step_1"),
        ("sliders", "nav_step_2"),
        ("rocket", "nav_step_3"),
        ("film", "nav_step_4"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarRail")
        self.setFixedWidth(64)

        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(8, 14, 8, 14)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.rail_buttons = []

        for i, (icon_name, key) in enumerate(self.STEP_KEYS):
            btn = QPushButton(self)
            btn.setProperty("class", "navRailBtnActive" if i == 0 else "navRailBtn")
            btn.setFixedSize(44, 44)
            btn.setIcon(get_lucide_icon(icon_name, color="#ffffff" if i == 0 else "#64748b", size=18))
            btn.setToolTip(tr(key))
            btn.clicked.connect(lambda checked=False, idx=i: self.step_selected.emit(idx))
            sidebar_layout.addWidget(btn)
            self.rail_buttons.append((btn, icon_name, key))

        sidebar_layout.addStretch()

        # Language Toggle Button (above reset button)
        self.btn_nav_lang = QPushButton(self)
        self.btn_nav_lang.setProperty("class", "navRailBtn")
        self.btn_nav_lang.setFixedSize(44, 44)
        self.btn_nav_lang.setIcon(get_lucide_icon("languages", color="#64748b", size=18))
        self.btn_nav_lang.setToolTip(tr("nav_lang_tooltip"))
        self.btn_nav_lang.clicked.connect(self.language_toggle_requested.emit)
        sidebar_layout.addWidget(self.btn_nav_lang)

        # Reset Parameters Button
        self.btn_nav_reset = QPushButton(self)
        self.btn_nav_reset.setProperty("class", "navRailBtn")
        self.btn_nav_reset.setFixedSize(44, 44)
        self.btn_nav_reset.setIcon(get_lucide_icon("rotate-ccw", color="#64748b", size=18))
        self.btn_nav_reset.setToolTip(tr("nav_reset_tooltip"))
        self.btn_nav_reset.clicked.connect(self.reset_requested.emit)
        sidebar_layout.addWidget(self.btn_nav_reset)

        # Bottom Info Button
        self.btn_nav_info = QPushButton(self)
        self.btn_nav_info.setProperty("class", "navRailBtn")
        self.btn_nav_info.setFixedSize(44, 44)
        self.btn_nav_info.setIcon(get_lucide_icon("info", color="#64748b", size=18))
        self.btn_nav_info.setToolTip(tr("nav_info_tooltip"))
        self.btn_nav_info.clicked.connect(self.info_requested.emit)
        sidebar_layout.addWidget(self.btn_nav_info)

        apply_card_shadow(self, blur=14, offset_y=2, alpha=25)

    def set_current_step(self, step_idx):
        for i, (btn, icon_name, _) in enumerate(self.rail_buttons):
            if i == step_idx:
                btn.setProperty("class", "navRailBtnActive")
                btn.setIcon(get_lucide_icon(icon_name, color="#ffffff", size=18))
            else:
                btn.setProperty("class", "navRailBtn")
                btn.setIcon(get_lucide_icon(icon_name, color="#64748b", size=18))

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()

    def retranslate_ui(self):
        """Refreshes all tooltips and texts on the rail when language changes."""
        for btn, _, key in self.rail_buttons:
            btn.setToolTip(tr(key))
        self.btn_nav_lang.setToolTip(tr("nav_lang_tooltip"))
        self.btn_nav_reset.setToolTip(tr("nav_reset_tooltip"))
        self.btn_nav_info.setToolTip(tr("nav_info_tooltip"))
