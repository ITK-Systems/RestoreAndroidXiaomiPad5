import time
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QPlainTextEdit, QApplication
)
from PyQt6.QtCore import Qt


class ConsoleLogWidget(QFrame):
    """Real-time styled terminal log output window with color coding."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header bar
        header = QHBoxLayout()
        lbl_title = QLabel("💻 NHẬT KÝ THAO TÁC (TERMINAL LOG)")
        lbl_title.setStyleSheet("font-size: 13px; font-weight: 700; color: #94a3b8;")
        header.addWidget(lbl_title, stretch=1)

        btn_copy = QPushButton("📋 Sao chép")
        btn_copy.setToolTip("Sao chép toàn bộ nhật ký vào Clipboard")
        btn_copy.clicked.connect(self.copy_log)
        header.addWidget(btn_copy)

        btn_clear = QPushButton("🗑️ Xóa")
        btn_clear.setToolTip("Xóa trắng màn hình nhật ký")
        btn_clear.clicked.connect(self.clear_log)
        header.addWidget(btn_clear)

        layout.addLayout(header)

        # Console text area
        self.text_edit = QPlainTextEdit()
        self.text_edit.setObjectName("ConsoleOutput")
        self.text_edit.setReadOnly(True)
        self.text_edit.setMaximumBlockCount(2000)
        layout.addWidget(self.text_edit)

        # Initial welcome message
        self.append_log("INFO", "Sẵn sàng làm việc. Hệ thống đang theo dõi kết nối thiết bị Xiaomi Pad 5...")

    def append_log(self, level: str, text: str):
        timestamp = time.strftime("%H:%M:%S")
        prefix = f"[{timestamp}] "
        
        # Color mapping
        color = "#e2e8f0"  # default
        tag = ""
        if level == "SUCCESS":
            color = "#34d399"
            tag = "[OK] "
        elif level == "WARNING":
            color = "#fbbf24"
            tag = "[CẢNH BÁO] "
        elif level == "ERROR":
            color = "#f87171"
            tag = "[LỖI] "
        elif level == "CMD":
            color = "#38bdf8"
            tag = ""
        elif level == "INFO":
            color = "#94a3b8"
            tag = ""

        # Format line
        formatted_line = f"{prefix}{tag}{text}"
        self.text_edit.appendPlainText(formatted_line)
        self.text_edit.verticalScrollBar().setValue(self.text_edit.verticalScrollBar().maximum())

    def clear_log(self):
        self.text_edit.clear()
        self.append_log("INFO", "Đã xóa màn hình nhật ký.")

    def copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        self.append_log("SUCCESS", "Đã sao chép toàn bộ nhật ký vào bộ nhớ tạm (Clipboard)!")
