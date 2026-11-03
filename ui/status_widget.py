from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt
from core.adb_fastboot import adb_reboot_bootloader


class DeviceStatusWidget(QFrame):
    """Card widget displaying live device connection mode and action buttons."""

    # Signal when user clicks "Reboot to Fastboot"
    reboot_requested = pyqtSignal()
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CardFrame")
        self.current_mode = "NONE"
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Header Row: Indicator + Status Text + Buttons
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Status Circle Icon
        self.lbl_indicator = QLabel("●")
        self.lbl_indicator.setStyleSheet("color: #ef4444; font-size: 20px;")
        top_row.addWidget(self.lbl_indicator)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.lbl_title = QLabel("CHƯA PHÁT HIỆN THIẾT BỊ")
        self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        text_layout.addWidget(self.lbl_title)

        self.lbl_subtitle = QLabel("Vui lòng cắm cáp USB kết nối Xiaomi Pad 5 với máy tính.")
        self.lbl_subtitle.setStyleSheet("font-size: 12px; color: #94a3b8;")
        text_layout.addWidget(self.lbl_subtitle)

        top_row.addLayout(text_layout, stretch=1)

        # Action: Reboot to Fastboot (Visible only when in ADB)
        self.btn_reboot_fastboot = QPushButton("⚡ Chuyển sang FASTBOOT")
        self.btn_reboot_fastboot.setObjectName("ActionRebootBtn")
        self.btn_reboot_fastboot.setVisible(False)
        self.btn_reboot_fastboot.clicked.connect(self._on_reboot_clicked)
        top_row.addWidget(self.btn_reboot_fastboot)

        # Action: Manual Refresh
        self.btn_refresh = QPushButton("🔄 Làm mới")
        self.btn_refresh.clicked.connect(lambda: self.refresh_requested.emit())
        top_row.addWidget(self.btn_refresh)

        layout.addLayout(top_row)

        # Details Row: Serial, Product, Guide tips
        self.lbl_details = QLabel("")
        self.lbl_details.setStyleSheet("font-size: 12px; color: #64748b; padding-left: 32px;")
        layout.addWidget(self.lbl_details)

    def update_status(self, mode: str, serial: str, text: str, details: dict):
        self.current_mode = mode
        
        if mode == "FASTBOOT":
            self.lbl_indicator.setText("●")
            self.lbl_indicator.setStyleSheet("color: #10b981; font-size: 22px;")
            self.lbl_title.setText("ĐÃ KẾT NỐI CHẾ ĐỘ FASTBOOT (nabu)")
            self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #34d399;")
            self.lbl_subtitle.setText(f"Serial: {serial} | Thiết bị đã sẵn sàng để khôi phục phân vùng Android gốc.")
            self.lbl_details.setText("✔ Đã nhận diện bộ nạp khởi động Fastboot. Bạn có thể tiến hành khôi phục.")
            self.btn_reboot_fastboot.setVisible(False)

        elif mode == "ADB":
            self.lbl_indicator.setText("●")
            self.lbl_indicator.setStyleSheet("color: #38bdf8; font-size: 22px;")
            self.lbl_title.setText("ĐÃ KẾT NỐI ANDROID (ADB Online)")
            self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #38bdf8;")
            self.lbl_subtitle.setText(f"Serial: {serial} | Máy đang chạy trong hệ điều hành Android.")
            self.lbl_details.setText("👉 Bấm nút 'Chuyển sang FASTBOOT' bên phải để đưa máy về chế độ khôi phục.")
            self.btn_reboot_fastboot.setVisible(True)

        elif mode == "UNAUTHORIZED":
            self.lbl_indicator.setText("●")
            self.lbl_indicator.setStyleSheet("color: #f59e0b; font-size: 22px;")
            self.lbl_title.setText("CHƯA CHO PHÉP GỠ LỖI USB (ADB Unauthorized)")
            self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #fbbf24;")
            self.lbl_subtitle.setText("Vui lòng mở khóa màn hình Xiaomi Pad 5, chọn 'Luôn cho phép từ máy tính này' rồi bấm OK.")
            self.lbl_details.setText("💡 Hoặc bạn có thể tắt nguồn máy tính bảng, giữ nút Giảm âm lượng + Nguồn để vào thẳng FASTBOOT.")
            self.btn_reboot_fastboot.setVisible(False)

        else:  # NONE
            self.lbl_indicator.setText("●")
            self.lbl_indicator.setStyleSheet("color: #ef4444; font-size: 22px;")
            self.lbl_title.setText("CHƯA PHÁT HIỆN THIẾT BỊ")
            self.lbl_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #f87171;")
            self.lbl_subtitle.setText("Vui lòng cắm cáp USB kết nối Xiaomi Pad 5 với máy tính.")
            self.lbl_details.setText("💡 Nếu máy đang ở Android: Bật 'Gỡ lỗi USB' trong Cài đặt nhà phát triển. Hoặc giữ [Nguồn + Giảm âm lượng] để vào Fastboot.")
            self.btn_reboot_fastboot.setVisible(False)

    def _on_reboot_clicked(self):
        self.reboot_requested.emit()
