"""
Soft Porcelain / Neumorphic Claymorphic Design Theme for MoshUp
Inspired by ultra-clean, tactile, rounded, frosted slate & porcelain aesthetics.
"""

SOFT_PORCELAIN_QSS = """
* {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #1e293b;
    outline: none;
}

/* Main Window & Central Container */
QMainWindow, QDialog {
    background-color: #ebf0f7;
}

QWidget#centralWidget, QWidget#mainContainer {
    background-color: #ebf0f7;
}

/* Sidebar & Navigation Rail */
QFrame#sidebarRail {
    background-color: #f5f8fc;
    border-right: 1px solid #dbe4ef;
    border-radius: 18px;
}

QPushButton.navRailBtn {
    background-color: transparent;
    border: none;
    border-radius: 12px;
    padding: 8px;
    margin: 2px 0px;
}

QPushButton.navRailBtn:hover {
    background-color: #e2ebf5;
}

QPushButton.navRailBtnActive {
    background-color: #151829;
    border: none;
    border-radius: 12px;
    padding: 8px;
    margin: 2px 0px;
}

QPushButton.navRailBtnActive:hover {
    background-color: #242940;
}

/* Soft Cards & Elevated Panels */
QFrame.clayCard, QWidget.clayCard, QFrame.softCard, QWidget.softCard {
    background-color: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 18px;
}

/* Subtle Inset Card */
QFrame.insetCard {
    background-color: #f1f5fa;
    border: 1px solid #dce4ef;
    border-radius: 12px;
}

/* GroupBox with Soft Porcelain Styling */
QGroupBox {
    font-weight: 700;
    font-size: 12px;
    color: #1e293b;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-top: 8px;
    padding-top: 12px;
    padding-bottom: 8px;
    padding-left: 10px;
    padding-right: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 1px 7px;
    color: #475569;
    background-color: #edf2f8;
    border: 1px solid #d6e0ec;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}

/* Labels */
QLabel {
    color: #334155;
}

QLabel.titleLabel {
    font-size: 18px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: #0f172a;
}

QLabel.sectionTitle {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: -0.2px;
    color: #0f172a;
}

QLabel.subLabel {
    font-size: 12px;
    font-weight: 500;
    color: #64748b;
}

QLabel.pillBadge {
    background-color: #ebf1f7;
    color: #334155;
    font-size: 11px;
    font-weight: 700;
    border-radius: 8px;
    padding: 2px 8px;
    border: 1px solid #d8e2ec;
}

/* Buttons */
QPushButton {
    color: #1e293b;
    font-weight: 600;
    font-size: 12.5px;
    padding: 7px 14px;
    border-radius: 11px;
    border: 1px solid #d3dde8;
    background-color: #ffffff;
}

QPushButton:hover {
    background-color: #f1f5fa;
    border: 1px solid #c8d4e2;
    color: #0f172a;
}

QPushButton:pressed {
    background-color: #e2ebf5;
    border: 1px solid #b8c8d8;
}

QPushButton:disabled {
    color: #94a3b8;
    border: 1px solid #e2e8f0;
    background-color: #f8fafc;
}

/* Obsidian Primary Action Button */
QPushButton.btnGreen, QPushButton.btnPrimary, QPushButton#btnStart {
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.2px;
    border-radius: 11px;
    border: 1px solid #151829;
    background-color: #151829;
    padding: 8px 18px;
}

QPushButton.btnGreen:hover, QPushButton.btnPrimary:hover, QPushButton#btnStart:hover {
    background-color: #242a42;
    border: 1px solid #242a42;
    color: #ffffff;
}

QPushButton.btnGreen:pressed, QPushButton.btnPrimary:pressed, QPushButton#btnStart:pressed {
    background-color: #0d101c;
    border: 1px solid #0d101c;
}

QPushButton.btnGreen:disabled, QPushButton.btnPrimary:disabled, QPushButton#btnStart:disabled {
    background-color: #94a3b8;
    border: 1px solid #94a3b8;
    color: #f1f5f9;
}

/* Secondary Action Button */
QPushButton.btnSecondary {
    color: #334155;
    font-weight: 600;
    font-size: 12.5px;
    border: 1px solid #cbd5e1;
    background-color: #f8fafc;
    border-radius: 11px;
    padding: 7px 15px;
}

QPushButton.btnSecondary:hover {
    background-color: #f1f5f9;
    border: 1px solid #94a3b8;
    color: #0f172a;
}

QPushButton.btnSecondary:pressed {
    background-color: #e2e8f0;
    border: 1px solid #64748b;
}

/* Segmented Pill Tabs */
QTabWidget::pane {
    border: 1px solid #dbe3ed;
    background-color: #ffffff;
    border-radius: 14px;
    margin-top: 4px;
}

QTabBar {
    background-color: #e3ebf4;
    border-radius: 12px;
    padding: 3px;
}

QTabBar::tab {
    color: #64748b;
    font-weight: 600;
    font-size: 11.5px;
    padding: 5px 9px;
    margin: 1px 1px;
    border: none;
    border-radius: 9px;
    background-color: transparent;
}

QTabBar::tab:hover:!selected {
    color: #1e293b;
    background-color: rgba(255, 255, 255, 0.6);
}

QTabBar::tab:selected {
    color: #0f172a;
    background-color: #ffffff;
    border: 1px solid rgba(210, 222, 235, 0.8);
    font-weight: 700;
}

/* Text Inputs, Spinboxes, Comboboxes */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    min-height: 22px;
    background-color: #f6f9fc;
    color: #1e293b;
    font-weight: 600;
    border: 1px solid #d8e2ed;
    border-radius: 10px;
    padding: 5px 9px;
    selection-background-color: #151829;
    selection-color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: #ffffff;
    border: 1.5px solid #151829;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 26px;
    border-left: 1px solid #d8e2ed;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    background-color: #f1f5fa;
}

QComboBox::down-arrow {
    image: url(assets/chevron_down.png);
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #1e293b;
    font-weight: 600;
    selection-background-color: #151829;
    selection-color: #ffffff;
    border: 1px solid #d8e2ed;
    border-radius: 10px;
    padding: 4px;
}

/* Tactile Slider */
QSlider::groove:horizontal {
    height: 7px;
    background-color: #dce5ef;
    border: none;
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background-color: #151829;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background-color: #ffffff;
    border: 2px solid #151829;
    width: 18px;
    height: 18px;
    margin-top: -6px;
    margin-bottom: -6px;
    border-radius: 9px;
}

QSlider::handle:horizontal:hover {
    background-color: #f8fafc;
    border: 2.5px solid #242940;
}

/* Rounded Pill Progress Bar */
QProgressBar {
    border: 1px solid #dce4ef;
    background-color: #e5edf5;
    border-radius: 9px;
    text-align: center;
    color: #1e293b;
    font-size: 11px;
    font-weight: 800;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #151829;
    border-radius: 8px;
}

/* Checkbox & Radio Button */
QCheckBox, QRadioButton {
    color: #334155;
    font-weight: 600;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 17px;
    height: 17px;
    background-color: #f6f9fc;
    border: 1.5px solid #cad6e4;
    border-radius: 5px;
}

QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border: 1.5px solid #151829;
}

QCheckBox::indicator:checked {
    background-color: #151829;
    border: 1.5px solid #151829;
    image: url(assets/check.png);
}

/* Execution Log Console */
QTextEdit {
    background-color: #f6f9fc;
    color: #334155;
    font-family: 'SF Mono', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.5;
    border: 1px solid #dbe3ed;
    border-radius: 12px;
    padding: 8px;
}

/* Clean Scrollbars */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    margin: 4px 2px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #cbd5e1;
    min-height: 24px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background-color: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    margin: 2px 4px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #cbd5e1;
    min-width: 24px;
    border-radius: 4px;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* Tooltips */
QToolTip {
    background-color: #151829;
    color: #ffffff;
    font-size: 11px;
    font-weight: 600;
    border: none;
    padding: 5px 9px;
    border-radius: 7px;
}

/* Splitter */
QSplitter::handle {
    background-color: transparent;
    width: 6px;
    height: 6px;
}

/* Stepper Navigation Bar */
QFrame#stepperBar {
    background-color: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 16px;
}

QPushButton.stepperItem {
    background-color: transparent;
    border: none;
    border-radius: 11px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-align: center;
}

QPushButton.stepperItem:hover {
    background-color: #f1f5fa;
    color: #1e293b;
}

QPushButton.stepperItemActive {
    background-color: #151829;
    border: none;
    border-radius: 11px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
    color: #ffffff;
}

QPushButton.stepperItemActive:hover {
    background-color: #242940;
}

QPushButton.stepperItemDone {
    background-color: #f1f6fb;
    border: 1px solid #d5e2f0;
    border-radius: 11px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 700;
    color: #0f172a;
}

QPushButton.stepperItemDone:hover {
    background-color: #e4edf7;
}

/* Page Headers */
QLabel.pageHeaderTitle {
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -0.4px;
    color: #0f172a;
}

QLabel.pageHeaderSubtitle {
    font-size: 12.5px;
    font-weight: 500;
    color: #64748b;
}

/* Success Card Banner */
QFrame.successBanner {
    background-color: #ecfdf5;
    border: 1.5px solid #a7f3d0;
    border-radius: 14px;
}

/* Wizard Bottom Nav Bar */
QFrame#wizardNavBar {
    background-color: #ffffff;
    border: 1px solid #dbe3ed;
    border-radius: 16px;
}
"""

# Alias for backwards compatibility
DARK_QSS = SOFT_PORCELAIN_QSS
