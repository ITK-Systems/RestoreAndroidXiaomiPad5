import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QFrame, QCheckBox, QProgressBar,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QTimer

from core.constants import APP_NAME, APP_VERSION, TARGET_DEVICE_NAME, GPT_BIN
from core.adb_fastboot import check_tools_installed, adb_reboot_bootloader
from core.device_monitor import DeviceMonitorThread
from core.restore_engine import RestoreEngineThread

from ui.styles import DARK_THEME_QSS
from ui.status_widget import DeviceStatusWidget
from ui.console_widget import ConsoleLogWidget
from ui.advanced_tab import AdvancedTab
from ui.app_manager_tab import AppManagerTab
from ui.utility_apps_tab import UtilityAppsTab
from ui.display_tab import DisplayTab
from ui.guide_tab import GuideTab


class MainWindow(QMainWindow):
    """Main application window for Xiaomi Pad 5 Android Restore Tool."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(980, 750)
        self.setMinimumSize(850, 650)
        self.setStyleSheet(DARK_THEME_QSS)

        self.current_mode = "NONE"
        self.current_serial = ""
        self.current_details = {}

        self.monitor_thread = None
        self.restore_thread = None

        self._init_ui()
        self._init_background_services()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(12)

        # 1. Header Bar
        header_frame = QFrame()
        header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 8, 10, 8)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        lbl_app_title = QLabel(f"📱 {APP_NAME.upper()}")
        lbl_app_title.setObjectName("HeaderTitle")
        title_layout.addWidget(lbl_app_title)

        lbl_app_sub = QLabel("Khôi Phục 100% Phân Vùng Android Gốc • Gỡ Bỏ Windows 11 & ESP An Toàn Chuẩn Xác")
        lbl_app_sub.setObjectName("HeaderSubtitle")
        title_layout.addWidget(lbl_app_sub)

        header_layout.addLayout(title_layout, stretch=1)

        badge_ver = QLabel(f"v{APP_VERSION} Pro")
        badge_ver.setStyleSheet("""
            background-color: #1e293b;
            color: #38bdf8;
            font-size: 12px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #334155;
        """)
        header_layout.addWidget(badge_ver)

        main_layout.addWidget(header_frame)

        # 2. Live Device Status Card
        self.status_widget = DeviceStatusWidget()
        self.status_widget.reboot_requested.connect(self._on_reboot_fastboot_clicked)
        self.status_widget.refresh_requested.connect(self._on_manual_refresh)
        main_layout.addWidget(self.status_widget)

        # 3. Main Tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget, stretch=1)

        # Tab 1: Restore Partition (Main)
        self.tab_restore = self._create_restore_tab()
        self.tab_widget.addTab(self.tab_restore, "🚀 Khôi Phục Phân Vùng (Restore)")

        # Tab 2: Utility Apps Hub (Curated App Store)
        self.tab_utilities = UtilityAppsTab()
        self.tab_utilities.log_requested.connect(self.console.append_log)
        self.tab_widget.addTab(self.tab_utilities, "⭐ Kho Tiện Ích Pad 5 (Utilities)")

        # Tab 3: App Manager & Batch APK Installer (Debloater)
        self.tab_app_manager = AppManagerTab()
        self.tab_app_manager.log_requested.connect(self.console.append_log)
        self.tab_widget.addTab(self.tab_app_manager, "📦 Dọn Rác & Cài APK (Debloat)")

        # Tab 4: Display & 120Hz Tweaker
        self.tab_display = DisplayTab()
        self.tab_display.log_requested.connect(self.console.append_log)
        self.tab_widget.addTab(self.tab_display, "🖥️ Màn Hình & 120Hz (Display)")

        # Tab 5: Advanced Tools
        self.tab_advanced = AdvancedTab()
        self.tab_advanced.log_requested.connect(self.console.append_log)
        self.tab_widget.addTab(self.tab_advanced, "⚙️ Tiện Ích Nâng Cao (Advanced)")

        # Tab 6: Guide & Help
        self.tab_guide = GuideTab()
        self.tab_widget.addTab(self.tab_guide, "📖 Hướng Dẫn & Trợ Giúp (Guide)")

    def _create_restore_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Action & Confirmation Card
        action_card = QFrame()
        action_card.setObjectName("CardFrame")
        card_layout = QVBoxLayout(action_card)
        card_layout.setSpacing(12)

        lbl_info = QLabel("THAO TÁC SẼ THỰC HIỆN:")
        lbl_info.setObjectName("SectionTitle")
        card_layout.addWidget(lbl_info)

        desc_text = QLabel(
            "1. Nạp lại bảng phân vùng gốc chính hãng (Qualcomm LUN0 GPT) vào <b>partition:0</b>.<br>"
            "2. Gỡ bỏ hoàn toàn phân vùng Windows 11 (<code>win</code>) và phân vùng khởi động UEFI (<code>esp</code>).<br>"
            "3. Mở rộng và định dạng lại phân vùng dữ liệu <b>userdata</b> về 100% dung lượng xuất xưởng (128GB hoặc 256GB).<br>"
            "4. Khởi động lại thiết bị về Android nguyên bản."
        )
        desc_text.setStyleSheet("color: #cbd5e1; font-size: 13px; line-height: 1.5;")
        card_layout.addWidget(desc_text)

        # Checkbox Confirmation
        self.chk_confirm = QCheckBox(
            "Tôi hiểu rằng thao tác này sẽ xóa sạch dữ liệu trên máy tính bảng và đưa về Android gốc ban đầu."
        )
        self.chk_confirm.stateChanged.connect(self._update_button_states)
        card_layout.addWidget(self.chk_confirm)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Sẵn sàng")
        card_layout.addWidget(self.progress_bar)

        # Big Restore Button
        self.btn_restore = QPushButton("🚀 BẮT ĐẦU KHÔI PHỤC VỀ ANDROID GỐC (1-CLICK RESTORE)")
        self.btn_restore.setObjectName("RestoreButton")
        self.btn_restore.setEnabled(False)
        self.btn_restore.clicked.connect(self._on_start_restore_clicked)
        card_layout.addWidget(self.btn_restore)

        layout.addWidget(action_card)

        # Real-time Console Log Widget
        self.console = ConsoleLogWidget()
        layout.addWidget(self.console, stretch=1)

        return widget

    def _init_background_services(self):
        # Initial tools check
        ok, msg = check_tools_installed()
        if not ok:
            self.console.append_log("ERROR", f"Cảnh báo môi trường: {msg}")
        else:
            self.console.append_log("SUCCESS", f"Kiểm tra môi trường: {msg}")

        # Start Device Monitor Thread
        self.monitor_thread = DeviceMonitorThread(poll_interval=1.5, parent=self)
        self.monitor_thread.status_changed.connect(self._on_device_status_changed)
        self.monitor_thread.start()

    def _on_device_status_changed(self, mode: str, serial: str, text: str, details: dict):
        self.current_mode = mode
        self.current_serial = serial
        self.current_details = details

        self.status_widget.update_status(mode, serial, text, details)
        self._update_button_states()

        if mode == "ADB" and hasattr(self, "tab_utilities"):
            QTimer.singleShot(600, self.tab_utilities.refresh_installed_status)

    def _update_button_states(self):
        # Restore button is enabled only when device is in FASTBOOT and confirmation box is checked
        can_restore = (self.current_mode == "FASTBOOT") and self.chk_confirm.isChecked()
        
        # If restore thread is currently running, keep disabled
        if self.restore_thread and self.restore_thread.isRunning():
            self.btn_restore.setEnabled(False)
        else:
            self.btn_restore.setEnabled(can_restore)

    def _on_reboot_fastboot_clicked(self):
        self.console.append_log("INFO", "Đang gửi lệnh chuyển thiết bị từ Android sang FASTBOOT qua ADB...")
        ok, msg = adb_reboot_bootloader()
        if ok:
            self.console.append_log("SUCCESS", msg)
            self.console.append_log("INFO", "Thiết bị đang khởi động lại vào màn hình FASTBOOT. Vui lòng đợi trong giây lát...")
        else:
            self.console.append_log("ERROR", f"Chuyển sang Fastboot thất bại: {msg}")

    def _on_manual_refresh(self):
        self.console.append_log("INFO", "Đang làm mới danh sách thiết bị...")
        if self.monitor_thread:
            # Trigger immediate check
            self.monitor_thread._last_signature = None

    def _on_start_restore_clicked(self):
        if self.current_mode != "FASTBOOT":
            QMessageBox.warning(
                self,
                "Chưa ở chế độ FASTBOOT",
                "Thiết bị cần ở chế độ FASTBOOT để khôi phục bảng phân vùng.\n\n"
                "- Nếu máy đang ở Android: Nhấn nút 'Chuyển sang FASTBOOT'.\n"
                "- Hoặc tắt máy, giữ [Nguồn + Giảm âm lượng] để vào Fastboot."
            )
            return

        # Double confirmation dialog
        reply = QMessageBox.question(
            self,
            "⚠️ XÁC NHẬN KHÔI PHỤC ANDROID GỐC",
            "BẠN CÓ CHẮC CHẮN MUỐN TIẾN HÀNH KHÔI PHỤC?\n\n"
            "• Toàn bộ phân vùng Windows 11 và ESP sẽ bị XÓA HOÀN TOÀN.\n"
            "• Toàn bộ dữ liệu trong máy tính bảng sẽ bị xóa sạch.\n"
            "• Phân vùng userdata sẽ được mở rộng lại 100% dung lượng gốc.\n"
            "• Đảm bảo cáp USB được kết nối chắc chắn và không ngắt kết nối giữa chừng!\n\n"
            "Nhấn 'Yes' để bắt đầu khôi phục ngay lập tức.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            self.console.append_log("INFO", "Người dùng đã hủy thao tác khôi phục.")
            return

        # Disable controls during restore
        self.btn_restore.setEnabled(False)
        self.chk_confirm.setEnabled(False)
        self.progress_bar.setValue(10)
        self.progress_bar.setFormat("Đang bắt đầu khôi phục...")

        # Launch Restore Thread
        self.restore_thread = RestoreEngineThread(parent=self)
        self.restore_thread.log_signal.connect(self.console.append_log)
        self.restore_thread.progress_signal.connect(self._on_restore_progress)
        self.restore_thread.finished_signal.connect(self._on_restore_finished)
        self.restore_thread.start()

    def _on_restore_progress(self, step: int, total_steps: int, title: str):
        pct = int((step / total_steps) * 100)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"[{step}/{total_steps}] {title}")

    def _on_restore_finished(self, success: bool, message: str):
        self.chk_confirm.setEnabled(True)
        self._update_button_states()

        if success:
            self.progress_bar.setValue(100)
            self.progress_bar.setFormat("Khôi phục thành công 100%!")
            QMessageBox.information(
                self,
                "🎉 KHÔI PHỤC THÀNH CÔNG",
                "Quá trình khôi phục phân vùng Android gốc đã hoàn thành!\n\n"
                "👉 LƯU Ý KHI MÁY KHỞI ĐỘNG:\n"
                "1. Máy đang khởi động lại vào Android.\n"
                "2. Nếu máy dừng lại ở màn hình Mi-Recovery:\n"
                "   - Chọn 'Wipe Data' -> 'Wipe All Data' -> 'Confirm'.\n"
                "   - Chọn 'Back to Main Menu' -> 'Reboot' -> 'Reboot to System'.\n"
                "3. Máy sẽ vào Android với 100% dung lượng bộ nhớ ban đầu!"
            )
        else:
            self.progress_bar.setValue(0)
            self.progress_bar.setFormat("Thao tác thất bại")
            QMessageBox.critical(
                self,
                "❌ KHÔI PHỤC THẤT BẠI",
                f"Đã xảy ra sự cố trong quá trình khôi phục:\n\n{message}\n\n"
                "Vui lòng xem chi tiết lỗi trong khung 'Nhật ký thao tác' bên dưới."
            )

    def closeEvent(self, event):
        # Stop background thread on exit
        if self.monitor_thread:
            self.monitor_thread.stop()
        if self.restore_thread and self.restore_thread.isRunning():
            self.restore_thread.cancel()
        if hasattr(self, "tab_app_manager"):
            if self.tab_app_manager.worker and self.tab_app_manager.worker.isRunning():
                self.tab_app_manager.worker.terminate()
            if self.tab_app_manager.install_worker and self.tab_app_manager.install_worker.isRunning():
                self.tab_app_manager.install_worker.terminate()
        if hasattr(self, "tab_utilities") and self.tab_utilities.active_workers:
            for w in self.tab_utilities.active_workers.values():
                if w.isRunning():
                    w.terminate()
        event.accept()
