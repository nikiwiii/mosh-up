from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton
from lucide_icons import get_lucide_icon
from ..utils import apply_card_shadow


class NavigationRail(QFrame):
    """
    Vertical navigation rail displayed on the left of the application window.
    Contains buttons for each wizard step and an info button at the bottom.
    """
    step_selected = Signal(int)
    reset_requested = Signal()
    info_requested = Signal()

    STEPS = [
        ("file-video", "1. Wczytaj wideo"),
        ("sliders", "2. Efekty i parametry"),
        ("rocket", "3. Renderowanie"),
        ("film", "4. Podgląd wideo")
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

        for i, (icon_name, tooltip) in enumerate(self.STEPS):
            btn = QPushButton(self)
            btn.setProperty("class", "navRailBtnActive" if i == 0 else "navRailBtn")
            btn.setFixedSize(44, 44)
            btn.setIcon(get_lucide_icon(icon_name, color="#ffffff" if i == 0 else "#64748b", size=18))
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked=False, idx=i: self.step_selected.emit(idx))
            sidebar_layout.addWidget(btn)
            self.rail_buttons.append((btn, icon_name))

        sidebar_layout.addStretch()

        # Reset Parameters Button
        self.btn_nav_reset = QPushButton(self)
        self.btn_nav_reset.setProperty("class", "navRailBtn")
        self.btn_nav_reset.setFixedSize(44, 44)
        self.btn_nav_reset.setIcon(get_lucide_icon("rotate-ccw", color="#64748b", size=18))
        self.btn_nav_reset.setToolTip("Resetuj parametry do stanu początkowego")
        self.btn_nav_reset.clicked.connect(self.reset_requested.emit)
        sidebar_layout.addWidget(self.btn_nav_reset)

        # Bottom Info Button
        self.btn_nav_info = QPushButton(self)
        self.btn_nav_info.setProperty("class", "navRailBtn")
        self.btn_nav_info.setFixedSize(44, 44)
        self.btn_nav_info.setIcon(get_lucide_icon("info", color="#64748b", size=18))
        self.btn_nav_info.setToolTip("Informacje o MoshUp")
        self.btn_nav_info.clicked.connect(self.info_requested.emit)
        sidebar_layout.addWidget(self.btn_nav_info)

        apply_card_shadow(self, blur=14, offset_y=2, alpha=25)

    def set_current_step(self, step_idx):
        for i, (btn, icon_name) in enumerate(self.rail_buttons):
            if i == step_idx:
                btn.setProperty("class", "navRailBtnActive")
                btn.setIcon(get_lucide_icon(icon_name, color="#ffffff", size=18))
            else:
                btn.setProperty("class", "navRailBtn")
                btn.setIcon(get_lucide_icon(icon_name, color="#64748b", size=18))

            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
