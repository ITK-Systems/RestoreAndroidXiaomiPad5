"""
Modern Dark Theme QSS Stylesheet for Xiaomi Pad 5 Restore Tool.
Inspired by slate/navy dark mode with vibrant accent colors.
"""

DARK_THEME_QSS = """
/* Global Window Styling */
QMainWindow, QDialog {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0f172a;
    border-radius: 12px;
    top: -1px;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 10px 24px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid transparent;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border: 1px solid #334155;
    border-bottom: 2px solid #38bdf8;
}

QTabBar::tab:hover:!selected {
    background-color: #162032;
    color: #cbd5e1;
}

/* Card Containers */
QFrame#CardFrame {
    background-color: #141e33;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 16px;
}

QFrame#HeaderFrame {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f172a, stop:1 #1e293b);
    border-bottom: 1px solid #334155;
}

/* Labels */
QLabel#HeaderTitle {
    color: #f8fafc;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QLabel#HeaderSubtitle {
    color: #38bdf8;
    font-size: 12px;
    font-weight: 500;
}

QLabel#SectionTitle {
    color: #f1f5f9;
    font-size: 15px;
    font-weight: 600;
}

QLabel#StatusBadge {
    font-size: 14px;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 16px;
}

/* Primary Action Buttons */
QPushButton {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #273549;
    border-color: #475569;
}

QPushButton:pressed {
    background-color: #0f172a;
}

QPushButton:disabled {
    background-color: #0f172a;
    color: #64748b;
    border-color: #1e293b;
}

/* Restore Big Glow Button */
QPushButton#RestoreButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0ea5e9);
    color: #ffffff;
    border: 1px solid #38bdf8;
    border-radius: 10px;
    padding: 14px 24px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#RestoreButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #0284c7);
    border-color: #7dd3fc;
}

QPushButton#RestoreButton:pressed {
    background: #0284c7;
}

QPushButton#RestoreButton:disabled {
    background: #1e293b;
    color: #64748b;
    border-color: #334155;
}

/* Danger Button */
QPushButton#DangerButton {
    background: #991b1b;
    color: #ffffff;
    border: 1px solid #ef4444;
}

QPushButton#DangerButton:hover {
    background: #b91c1c;
}

/* Secondary Button */
QPushButton#ActionRebootBtn {
    background: #1e293b;
    color: #38bdf8;
    border: 1px solid #0284c7;
    font-weight: 600;
}

QPushButton#ActionRebootBtn:hover {
    background: #0284c7;
    color: #ffffff;
}

/* Console Log Box */
QPlainTextEdit#ConsoleOutput {
    background-color: #050811;
    color: #f1f5f9;
    border: 1px solid #1e293b;
    border-radius: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 8px;
    selection-background-color: #0284c7;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0b0f19;
    width: 8px;
    margin: 0px 0px 0px 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #334155;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Progress Bar */
QProgressBar {
    background-color: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 6px;
    text-align: center;
    color: #f8fafc;
    font-weight: bold;
    height: 20px;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #10b981);
    border-radius: 5px;
}

/* Checkbox */
QCheckBox {
    spacing: 10px;
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 500;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #0f172a;
}

QCheckBox::indicator:hover {
    border-color: #38bdf8;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
    image: none;
}

/* Line Edit & Inputs */
QLineEdit {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 13px;
}

QLineEdit:focus {
    border-color: #38bdf8;
    background-color: #162032;
}

/* Combo Box */
QComboBox {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    font-weight: 500;
}

QComboBox:hover {
    border-color: #475569;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid #334155;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

/* Tables */
QTableWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #1e293b;
    border-radius: 8px;
    gridline-color: #1e293b;
    selection-background-color: #1e3a5f;
    selection-color: #38bdf8;
    outline: none;
}

QTableWidget::item {
    padding: 6px 8px;
    border-bottom: 1px solid #141e33;
}

QTableWidget::item:selected {
    background-color: #1e3a5f;
    color: #38bdf8;
}

QHeaderView::section {
    background-color: #141e33;
    color: #94a3b8;
    padding: 8px 10px;
    font-weight: 600;
    font-size: 12px;
    border: none;
    border-bottom: 2px solid #1e293b;
}

/* List Widgets */
QListWidget {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid #1e293b;
    border-radius: 8px;
}

QListWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #141e33;
}

QListWidget::item:selected {
    background-color: #1e3a5f;
    color: #38bdf8;
}
"""
