"""
Electric Violet (#7c3aed / #8b5cf6) accent palette.
"""

BRUTALIST_DARK_QSS = """

* {
    font-family: 'Helvetica Neue', 'Helvetica', 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
    color: #f3f4f6;
}

/* Main Window Background - Ultra Dark Slate */
QMainWindow, QDialog {
    background-color: #0b0c10;
}

/* Central Widget */
QWidget#centralWidget, QWidget#mainContainer {
    background-color: #0b0c10;
}

/* 1px Thin Bordered Panel Containers */
QFrame.glassPanel, QWidget.glassPanel, QFrame.brutalistPanel {
    background-color: #14161d;
    border: 1px solid #2a2d3d;
    border-radius: 2px;
}

/* GroupBox - Sleek 1px Container */
QGroupBox {
    font-weight: 800;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #f3f4f6;
    background-color: #12141c;
    border: 1px solid #262938;
    border-radius: 2px;
    margin-top: 14px;
    padding-top: 16px;
    padding-bottom: 10px;
    padding-left: 10px;
    padding-right: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 2px 8px;
    color: #ffffff;
    background-color: #7c3aed; /* Electric Violet Accent */
    border: 1px solid #8b5cf6;
    border-radius: 2px;
    font-weight: 800;
}

/* Typography */
QLabel {
    color: #f3f4f6;
}

QLabel.titleLabel {
    font-size: 21px;
    font-weight: 900;
    letter-spacing: -0.5px;
    text-transform: uppercase;
    color: #ffffff;
}

QLabel.subLabel {
    font-size: 11px;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Standard Buttons - 1px Border */
QPushButton {
    color: #ffffff;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 7px 16px;
    border-radius: 2px;
    border: 1px solid #374151;
    background-color: #1f2937;
}

QPushButton:hover {
    background-color: #7c3aed; /* Electric Violet */
    color: #ffffff;
    border: 1px solid #8b5cf6;
}

QPushButton:pressed {
    background-color: #6d28d9;
    color: #ffffff;
}

QPushButton:disabled {
    color: #6b7280;
    border: 1px solid #1f2937;
    background-color: #111827;
}

/* Primary Action Button - Electric Violet Accent */
QPushButton.btnGreen {
    color: #ffffff;
    font-weight: 900;
    font-size: 14px;
    letter-spacing: 1px;
    text-transform: uppercase;
    border: 1px solid #a855f7;
    background-color: #7c3aed; /* Electric Violet */
}

QPushButton.btnGreen:hover {
    background-color: #8b5cf6; /* Vibrant Violet */
    border: 1px solid #c084fc;
}

QPushButton.btnGreen:pressed {
    background-color: #6d28d9;
    border: 1px solid #7c3aed;
}

/* Secondary Button - Dark Slate */
QPushButton.btnSecondary {
    color: #e5e7eb;
    font-weight: 800;
    border: 1px solid #374151;
    background-color: #1e2430;
}

QPushButton.btnSecondary:hover {
    background-color: #374151;
    color: #ffffff;
    border: 1px solid #4b5563;
}

/* Tab Widget - Sleek 1px Border Tabs */
QTabWidget::pane {
    border: 1px solid #2a2d3d;
    background-color: #12141c;
    border-radius: 2px;
}

QTabBar::tab {
    color: #9ca3af;
    font-weight: 800;
    font-size: 12px;
    text-transform: uppercase;
    padding: 8px 14px;
    margin-right: 3px;
    border: 1px solid #2a2d3d;
    border-bottom: none;
    border-radius: 2px 2px 0px 0px;
    background-color: #1a1d27;
}

QTabBar::tab:hover {
    background-color: #2a2d3d;
    color: #ffffff;
    border: 1px solid #374151;
}

QTabBar::tab:selected {
    color: #ffffff;
    background-color: #7c3aed;
    border: 1px solid #8b5cf6;
    border-bottom: 1px solid #7c3aed;
    font-weight: 900;
}

/* LineEdit & SpinBox - Sleek 1px Inputs */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #181b24;
    color: #ffffff;
    font-weight: 700;
    border: 1px solid #374151;
    border-radius: 2px;
    padding: 6px 8px;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    background-color: #1f2330;
    border: 1px solid #8b5cf6;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #374151;
    background-color: #7c3aed;
}

QComboBox QAbstractItemView {
    background-color: #14161d;
    color: #ffffff;
    font-weight: 700;
    selection-background-color: #7c3aed;
    selection-color: #ffffff;
    border: 1px solid #374151;
}

/* Sliders - Sleek 1px Track */
QSlider::groove:horizontal {
    height: 8px;
    background-color: #181b24;
    border: 1px solid #374151;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background-color: #7c3aed;
    border: 1px solid #8b5cf6;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background-color: #ffffff;
    border: 1px solid #a855f7;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 2px;
}

QSlider::handle:horizontal:hover {
    background-color: #c084fc;
    border: 1px solid #ffffff;
}

/* Progress Bar - Violet Accent Chunk */
QProgressBar {
    border: 1px solid #374151;
    background-color: #181b24;
    border-radius: 2px;
    text-align: center;
    color: #ffffff;
    font-weight: 900;
}

QProgressBar::chunk {
    background-color: #7c3aed;
    border-right: 1px solid #8b5cf6;
}

/* CheckBox & RadioButton */
QCheckBox, QRadioButton {
    color: #f3f4f6;
    font-weight: 700;
    spacing: 8px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    background-color: #181b24;
    border: 1px solid #374151;
    border-radius: 2px;
}

QCheckBox::indicator:checked {
    background-color: #7c3aed;
    border: 1px solid #8b5cf6;
}

/* TextEdit / Log Output */
QTextEdit {
    background-color: #0e1017;
    color: #c084fc;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid #2a2d3d;
    border-radius: 2px;
    padding: 6px;
}

/* ScrollBars - 1px Border Scrollbar */
QScrollBar:vertical {
    background-color: #12141c;
    width: 14px;
    margin: 0px;
    border: 1px solid #2a2d3d;
}

QScrollBar::handle:vertical {
    background-color: #374151;
    min-height: 20px;
    border-radius: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #7c3aed;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ToolTips */
QToolTip {
    background-color: #1f2937;
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #7c3aed;
    padding: 4px 8px;
    border-radius: 2px;
}
"""
