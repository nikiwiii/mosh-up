"""
Windows Vista Aero Glass Theme & QSS Styling for PySide6 / Qt6
Reproduces the signature Windows Vista Aero aesthetic: deep glassy blue gradients,
specular highlights, glowing green/blue buttons, and Segoe UI typography.
"""

VISTA_AERO_QSS = """
/* ===================================================================
   WINDOWS VISTA AERO GLOBAL STYLESHEET
   =================================================================== */

* {
    font-family: 'Segoe UI', 'Tahoma', 'Arial', sans-serif;
    font-size: 13px;
    color: #e6f3ff;
}

/* Main Window Background - Deep Aero Glass Atmosphere */
QMainWindow, QDialog {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1b3d5c,
                                stop:0.25 #122b44,
                                stop:0.7 #0a1b2d,
                                stop:1 #050d18);
}

/* Central Widget & Base Panels */
QWidget#centralWidget, QWidget#mainContainer {
    background: transparent;
}

/* Frosted Glass Container Panels */
QFrame.glassPanel, QWidget.glassPanel {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 255, 255, 0.14),
                                stop:0.04 rgba(255, 255, 255, 0.08),
                                stop:0.5 rgba(12, 30, 50, 0.55),
                                stop:1 rgba(6, 17, 30, 0.75));
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-top: 1px solid rgba(255, 255, 255, 0.55);
    border-bottom: 1px solid rgba(0, 0, 0, 0.6);
    border-radius: 6px;
}

/* GroupBox - Vista Glass Style */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 255, 255, 0.12),
                                stop:0.05 rgba(255, 255, 255, 0.06),
                                stop:1 rgba(8, 22, 38, 0.55));
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-top: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 6px;
    margin-top: 12px;
    padding-top: 16px;
    padding-bottom: 8px;
    padding-left: 8px;
    padding-right: 8px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    padding: 0 6px;
    color: #d1edff;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2b5f8c,
                                stop:1 #143554);
    border: 1px solid rgba(255, 255, 255, 0.35);
    border-radius: 3px;
}

/* Labels & Text */
QLabel {
    color: #edf6ff;
}

QLabel.titleLabel {
    font-size: 17px;
    font-weight: bold;
    color: #ffffff;
}

QLabel.subLabel {
    font-size: 11px;
    color: #9ebfdc;
}

/* Buttons - Classic Windows Vista Aero Glossy Push Button */
QPushButton {
    color: #ffffff;
    font-weight: bold;
    padding: 6px 16px;
    border-radius: 4px;
    border: 1px solid #1c527e;
    border-top: 1px solid #5caee6;
    border-bottom: 1px solid #0d2f4a;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4fa7e8,
                                stop:0.48 #2982c7,
                                stop:0.50 #1866a4,
                                stop:1 #297fbf);
}

QPushButton:hover {
    border: 1px solid #3ca5f0;
    border-top: 1px solid #8ed4ff;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6ec3ff,
                                stop:0.48 #3d9de8,
                                stop:0.50 #247dc2,
                                stop:1 #3694d9);
}

QPushButton:pressed {
    border: 1px solid #0e3758;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #144f7c,
                                stop:0.5 #1b6094,
                                stop:1 #2777b2);
    padding-top: 7px;
    padding-left: 17px;
}

QPushButton:disabled {
    color: #8aa3ba;
    border: 1px solid #2b455c;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2c445a,
                                stop:1 #1c2e3e);
}

/* Primary Action Button - Windows Vista Green Glow Button */
QPushButton.btnGreen {
    color: #ffffff;
    font-weight: bold;
    border: 1px solid #2d8213;
    border-top: 1px solid #82e866;
    border-bottom: 1px solid #144f06;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6ed846,
                                stop:0.48 #3db319,
                                stop:0.50 #288c0b,
                                stop:1 #37a516);
}

QPushButton.btnGreen:hover {
    border: 1px solid #4be320;
    border-top: 1px solid #a8fc90;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #86f05d,
                                stop:0.48 #4dcc25,
                                stop:0.50 #34a813,
                                stop:1 #47bf24);
}

QPushButton.btnGreen:pressed {
    border: 1px solid #114205;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #1d6108,
                                stop:0.5 #2a820f,
                                stop:1 #359614);
}

/* Secondary Button - Vista Steel / Silver Gloss */
QPushButton.btnSecondary {
    color: #ffffff;
    border: 1px solid #3a5c78;
    border-top: 1px solid #8cb6da;
    border-bottom: 1px solid #1a3044;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #577f9f,
                                stop:0.48 #355d7f,
                                stop:0.50 #224463,
                                stop:1 #32597b);
}

QPushButton.btnSecondary:hover {
    border: 1px solid #5a8bb8;
    border-top: 1px solid #b6d9f7;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #6c97be,
                                stop:0.48 #467399,
                                stop:0.50 #2f567b,
                                stop:1 #416f99);
}

/* Tab Widget - Vista Aero Tab Styling */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-top: 1px solid rgba(255, 255, 255, 0.5);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(18, 44, 71, 0.8),
                                stop:1 rgba(8, 20, 35, 0.9));
    border-radius: 5px;
    border-top-left-radius: 0px;
}

QTabBar::tab {
    color: #d2e8fb;
    font-weight: bold;
    padding: 7px 16px;
    margin-right: 2px;
    border: 1px solid rgba(255, 255, 255, 0.25);
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 255, 255, 0.15),
                                stop:0.45 rgba(40, 85, 125, 0.6),
                                stop:1 rgba(15, 38, 62, 0.8));
}

QTabBar::tab:hover {
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 rgba(255, 255, 255, 0.3),
                                stop:0.45 rgba(60, 120, 175, 0.7),
                                stop:1 rgba(25, 60, 95, 0.9));
}

QTabBar::tab:selected {
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.45);
    border-top: 2px solid #5bb5f7;
    border-bottom: 1px solid rgba(18, 44, 71, 0.9);
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #3c82ba,
                                stop:0.48 #205c8d,
                                stop:0.50 #12436d,
                                stop:1 #1b5282);
}

/* LineEdit & SpinBox - Vista Inset Glass Input */
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #091726,
                                stop:1 #11273e);
    color: #ffffff;
    border: 1px solid #234f75;
    border-top: 1px solid #0d273e;
    border-radius: 3px;
    padding: 5px 8px;
    selection-background-color: #2982c7;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #4fa7e8;
    background: #0d233a;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #234f75;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #2b6fa4,
                                stop:1 #174267);
}

QComboBox QAbstractItemView {
    background-color: #0b1e31;
    color: #ffffff;
    selection-background-color: #2982c7;
    border: 1px solid #3c7fae;
}

/* Sliders - Vista Glossy Metallic Slider */
QSlider::groove:horizontal {
    height: 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #091522,
                                stop:1 #183552);
    border: 1px solid #2b5d88;
    border-radius: 4px;
}

QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #56b5f8,
                                stop:1 #2072b2);
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff,
                                stop:0.45 #d0e5f7,
                                stop:0.50 #9ec5e8,
                                stop:1 #c2e0f9);
    border: 1px solid #1c527e;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ffffff,
                                stop:0.5 #eef7ff,
                                stop:1 #badaf7);
    border: 1px solid #3ea4f2;
}

/* Progress Bar - Windows Vista Green Animated Shine */
QProgressBar {
    border: 1px solid #1f4a70;
    border-top: 1px solid #0c2338;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #091726,
                                stop:1 #122c47);
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    font-weight: bold;
}

QProgressBar::chunk {
    border-radius: 3px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #92f26d,
                                stop:0.48 #4dcc25,
                                stop:0.50 #2b9d0b,
                                stop:1 #3cbb1b);
}

/* CheckBox & RadioButton */
QCheckBox, QRadioButton {
    color: #edf6ff;
    spacing: 6px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 15px;
    height: 15px;
    background: #0c2034;
    border: 1px solid #285b88;
    border-radius: 3px;
}

QRadioButton::indicator {
    border-radius: 7px;
}

QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #4fa7e8,
                                stop:1 #1866a4);
    image: url(none);
}

QCheckBox::indicator:checked:after {
    content: "✓";
    color: white;
}

/* TextEdit / Log Output */
QTextEdit {
    background-color: #071320;
    color: #a8d5ff;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #1d466e;
    border-radius: 4px;
    padding: 6px;
}

/* ScrollBars - Vista Glossy Scrollbar */
QScrollBar:vertical {
    background: #091929;
    width: 14px;
    margin: 16px 0 16px 0;
    border: 1px solid #1a3c5a;
}

QScrollBar::handle:vertical {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #3c82ba,
                                stop:0.5 #205c8d,
                                stop:1 #12436d);
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: #143554;
    height: 15px;
    subcontrol-origin: margin;
}

/* ToolTips */
QToolTip {
    background-color: #122d48;
    color: #ffffff;
    border: 1px solid #4fa7e8;
    padding: 4px 8px;
    border-radius: 3px;
}
"""
