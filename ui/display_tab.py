import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QLineEdit, QSpinBox, QGridLayout, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread

from core.adb_fastboot import (
    adb_get_wm_density,
    adb_set_wm_density,
    adb_reset_wm_density,
    adb_get_refresh_rates,
    adb_set_refresh_rate,
    adb_get_animation_scale,
    adb_set_animation_scales,
    adb_restart_launcher,
    adb_open_workstation_mode
)


class DisplayTab(QWidget):
    """Tab for tweaking Display Resolution, DPI, 120Hz Refresh Rate, and Animation Scales."""

    log_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Wrap in ScrollArea so UI never gets vertically crushed on any resolution
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # -------------------------------------------------------------
        # 1. CARD: DPI & DISPLAY DENSITY TWEAKER
        # -------------------------------------------------------------
        card_dpi = QFrame()
        card_dpi.setObjectName("CardFrame")
        layout_dpi = QVBoxLayout(card_dpi)
        layout_dpi.setSpacing(14)

        # Title Row
        title_row = QHBoxLayout()
        lbl_dpi_title = QLabel("📐 TINH CHỈNH MẬT ĐỘ ĐIỂM ẢNH (DPI / DENSITY TWEAKER)")
        lbl_dpi_title.setObjectName("SectionTitle")
        title_row.addWidget(lbl_dpi_title)

        lbl_guide = QLabel("(Yêu cầu máy tính bảng đã bật USB Debugging)")
        lbl_guide.setStyleSheet("color: #38bdf8; font-size: 12px;")
        title_row.addWidget(lbl_guide)
        title_row.addStretch(1)

        btn_read_status = QPushButton("🔄 Đọc Thông Số Màn Hình")
        btn_read_status.setMinimumHeight(34)
        btn_read_status.clicked.connect(self._refresh_all_info)
        title_row.addWidget(btn_read_status)
        layout_dpi.addLayout(title_row)

        desc_dpi = QLabel(
            "Tùy chỉnh DPI giúp máy tính bảng Xiaomi Pad 5 (11 inch 2.5K) hiển thị nhiều không gian làm việc hơn, "
            "tương tự giao diện laptop hoặc đa nhiệm chia đôi màn hình cực rộng rãi."
        )
        desc_dpi.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc_dpi.setWordWrap(True)
        layout_dpi.addWidget(desc_dpi)

        # Status label
        self.lbl_dpi_status = QLabel("Trạng thái DPI: Nhấn 'Đọc Thông Số' để kiểm tra")
        self.lbl_dpi_status.setStyleSheet("color: #38bdf8; font-weight: 600; font-size: 13px;")
        layout_dpi.addWidget(self.lbl_dpi_status)

        # Presets Buttons Grid with explicit styling and minimum heights
        grid_presets = QGridLayout()
        grid_presets.setSpacing(12)
        grid_presets.setRowMinimumHeight(0, 46)
        grid_presets.setRowMinimumHeight(1, 46)

        preset_btn_qss = """
            QPushButton {
                background-color: #1a2333;
                color: #f1f5f9;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 600;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #273549;
                border-color: #38bdf8;
            }
        """

        preset_highlight_qss = """
            QPushButton {
                background-color: #0369a1;
                color: #ffffff;
                border: 1px solid #38bdf8;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                font-weight: 700;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0284c7;
                border-color: #7dd3fc;
            }
        """

        btn_240 = QPushButton("💻 240 DPI - Chế độ Laptop / Desktop (Cực rộng)")
        btn_240.setStyleSheet(preset_btn_qss)
        btn_240.setMinimumHeight(46)
        btn_240.setToolTip("Hiển thị thanh Taskbar to, nhiều nội dung cửa sổ làm việc nhất")
        btn_240.clicked.connect(lambda: self._apply_density(240))
        grid_presets.addWidget(btn_240, 0, 0)

        btn_280 = QPushButton("📐 280 DPI - Cân bằng Đa Nhiệm (Khuyên dùng)")
        btn_280.setStyleSheet(preset_highlight_qss)
        btn_280.setMinimumHeight(46)
        btn_280.setToolTip("Rất vừa vặn cho chia đôi màn hình và ghi chú bằng bút")
        btn_280.clicked.connect(lambda: self._apply_density(280))
        grid_presets.addWidget(btn_280, 0, 1)

        btn_320 = QPushButton("⚖️ 320 DPI - Mặc định Xiaomi Pad 5 (Chuẩn gốc)")
        btn_320.setStyleSheet(preset_btn_qss)
        btn_320.setMinimumHeight(46)
        btn_320.setToolTip("Mật độ điểm ảnh mặc định khi xuất xưởng")
        btn_320.clicked.connect(lambda: self._apply_density(320))
        grid_presets.addWidget(btn_320, 1, 0)

        btn_360 = QPushButton("📖 360 DPI - Chữ to, Dễ đọc (Phụ huynh / Đọc sách)")
        btn_360.setStyleSheet(preset_btn_qss)
        btn_360.setMinimumHeight(46)
        btn_360.setToolTip("Font chữ và biểu tượng phóng to, dễ nhìn")
        btn_360.clicked.connect(lambda: self._apply_density(360))
        grid_presets.addWidget(btn_360, 1, 1)

        layout_dpi.addLayout(grid_presets)

        # Custom DPI Input Row
        custom_row = QHBoxLayout()
        custom_row.setSpacing(10)

        lbl_custom = QLabel("Nhập DPI tùy chọn (200 - 450):")
        lbl_custom.setStyleSheet("font-weight: 500; font-size: 13px;")
        custom_row.addWidget(lbl_custom)

        self.spin_dpi = QSpinBox()
        self.spin_dpi.setRange(200, 450)
        self.spin_dpi.setValue(280)
        self.spin_dpi.setSingleStep(10)
        self.spin_dpi.setMinimumHeight(38)
        self.spin_dpi.setMinimumWidth(80)
        self.spin_dpi.setStyleSheet("background-color: #0f172a; color: white; padding: 6px; font-weight: bold;")
        custom_row.addWidget(self.spin_dpi)

        btn_apply_custom = QPushButton("⚡ Áp Dụng DPI Này")
        btn_apply_custom.setMinimumHeight(38)
        btn_apply_custom.clicked.connect(lambda: self._apply_density(self.spin_dpi.value()))
        custom_row.addWidget(btn_apply_custom)

        btn_reset_dpi = QPushButton("🔄 Khôi Phục Mặc Định (Reset DPI)")
        btn_reset_dpi.setMinimumHeight(38)
        btn_reset_dpi.clicked.connect(self._reset_density)
        custom_row.addWidget(btn_reset_dpi)

        custom_row.addStretch(1)
        layout_dpi.addLayout(custom_row)

        # Utility Buttons Row
        util_row = QHBoxLayout()
        util_row.setSpacing(12)

        btn_restart_launcher = QPushButton("📱 Tự Động Sắp Xếp Lại Icon (Sau Khi Đổi DPI)")
        btn_restart_launcher.setMinimumHeight(42)
        btn_restart_launcher.setStyleSheet("""
            background-color: #0369a1;
            color: #ffffff;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid #38bdf8;
        """)
        btn_restart_launcher.setToolTip("Khởi động lại màn hình chính để tự động căn chỉnh và sắp xếp lại các icon ngay ngắn theo DPI mới")
        btn_restart_launcher.clicked.connect(self._restart_launcher)
        util_row.addWidget(btn_restart_launcher)

        btn_workstation = QPushButton("💻 Bật / Mở Cài Đặt Chế Độ Máy Trạm (Workstation Mode - Giao Diện PC)")
        btn_workstation.setMinimumHeight(42)
        btn_workstation.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #a855f7);
            color: white; font-weight: bold; padding: 8px 18px; border-radius: 8px; font-size: 13px;
        """)
        btn_workstation.setToolTip("Mở trang cài đặt bí mật Chế độ máy trạm (Workstation Mode) trên Xiaomi Pad 5 với cửa sổ nổi tự do và Taskbar")
        btn_workstation.clicked.connect(self._open_workstation)
        util_row.addWidget(btn_workstation)

        util_row.addStretch(1)
        layout_dpi.addLayout(util_row)

        main_layout.addWidget(card_dpi)

        # -------------------------------------------------------------
        # 2. CARD: 120HZ REFRESH RATE TWEAKER
        # -------------------------------------------------------------
        card_hz = QFrame()
        card_hz.setObjectName("CardFrame")
        layout_hz = QVBoxLayout(card_hz)
        layout_hz.setSpacing(14)

        lbl_hz_title = QLabel("⚡ TẦN SỐ QUÉT MÀN HÌNH 120HZ (REFRESH RATE TWEAKER)")
        lbl_hz_title.setObjectName("SectionTitle")
        layout_hz.addWidget(lbl_hz_title)

        desc_hz = QLabel(
            "Màn hình Xiaomi Pad 5 hỗ trợ 120Hz mượt mà. Tuy nhiên, hệ điều hành MIUI/HyperOS thường tự động hạ xuống "
            "60Hz khi xem YouTube, lướt web hoặc dùng ứng dụng bên thứ 3. Tính năng này giúp ép màn hình chạy 120Hz mọi lúc."
        )
        desc_hz.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc_hz.setWordWrap(True)
        layout_hz.addWidget(desc_hz)

        # Status label
        self.lbl_hz_status = QLabel("Trạng thái tần số quét: Chưa đọc")
        self.lbl_hz_status.setStyleSheet("color: #10b981; font-weight: 600; font-size: 13px;")
        layout_hz.addWidget(self.lbl_hz_status)

        # Refresh Rate Action Grid
        hz_grid = QHBoxLayout()
        hz_grid.setSpacing(12)

        btn_force_120 = QPushButton("🚀 Ép Chạy 120Hz Mọi Lúc (Khóa 120Hz)")
        btn_force_120.setMinimumHeight(44)
        btn_force_120.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
            color: #04101e; font-weight: bold; padding: 10px 16px; font-size: 13px; border-radius: 8px;
        """)
        btn_force_120.setToolTip("Khóa cứng 120Hz không bị tự tụt fps khi xem video hay lướt app")
        btn_force_120.clicked.connect(lambda: self._set_refresh_rate("force_120"))
        hz_grid.addWidget(btn_force_120)

        btn_90 = QPushButton("⚡ 90Hz (Mượt & Tiết Kiệm Pin)")
        btn_90.setMinimumHeight(44)
        btn_90.setToolTip("Cân bằng hoàn hảo giữa độ mượt và thời lượng pin")
        btn_90.clicked.connect(lambda: self._set_refresh_rate("90"))
        hz_grid.addWidget(btn_90)

        btn_60 = QPushButton("🔋 60Hz (Tiết Kiệm Pin Tối Đa)")
        btn_60.setMinimumHeight(44)
        btn_60.setToolTip("Tiết kiệm pin tối đa khi đi xa hoặc sắp hết pin")
        btn_60.clicked.connect(lambda: self._set_refresh_rate("60"))
        hz_grid.addWidget(btn_60)

        btn_auto_hz = QPushButton("🔄 Tự Động Thích Ứng (Dynamic 60-120Hz)")
        btn_auto_hz.setMinimumHeight(44)
        btn_auto_hz.setToolTip("Trả lại chế độ tự thích ứng mặc định của Xiaomi")
        btn_auto_hz.clicked.connect(lambda: self._set_refresh_rate("auto"))
        hz_grid.addWidget(btn_auto_hz)

        layout_hz.addLayout(hz_grid)
        main_layout.addWidget(card_hz)

        # -------------------------------------------------------------
        # 3. CARD: ANIMATION SCALE TWEAKER
        # -------------------------------------------------------------
        card_anim = QFrame()
        card_anim.setObjectName("CardFrame")
        layout_anim = QVBoxLayout(card_anim)
        layout_anim.setSpacing(14)

        lbl_anim_title = QLabel("🏃 TỐC ĐỘ HIỆU ỨNG HỆ THỐNG (ANIMATION SCALING)")
        lbl_anim_title.setObjectName("SectionTitle")
        layout_anim.addWidget(lbl_anim_title)

        desc_anim = QLabel(
            "Tăng tốc độ chuyển cảnh và đóng mở ứng dụng kết hợp cùng màn hình 120Hz giúp mang lại cảm giác siêu tốc, "
            "phản hồi cảm ứng tức thì."
        )
        desc_anim.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc_anim.setWordWrap(True)
        layout_anim.addWidget(desc_anim)

        # Status label
        self.lbl_anim_status = QLabel("Tốc độ hiệu ứng: Chưa đọc")
        self.lbl_anim_status.setStyleSheet("color: #f59e0b; font-weight: 600; font-size: 13px;")
        layout_anim.addWidget(self.lbl_anim_status)

        anim_grid = QHBoxLayout()
        anim_grid.setSpacing(12)

        btn_anim_05 = QPushButton("⚡ 0.5x Siêu Nhanh (Khuyên Dùng cho 120Hz)")
        btn_anim_05.setMinimumHeight(40)
        btn_anim_05.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold; border-radius: 8px;")
        btn_anim_05.clicked.connect(lambda: self._set_animation(0.5))
        anim_grid.addWidget(btn_anim_05)

        btn_anim_0 = QPushButton("🚀 0.0x Tắt Hiệu Ứng (Tối Đa Tốc Độ)")
        btn_anim_0.setMinimumHeight(40)
        btn_anim_0.clicked.connect(lambda: self._set_animation(0.0))
        anim_grid.addWidget(btn_anim_0)

        btn_anim_1 = QPushButton("🔄 1.0x Mặc Định của Android")
        btn_anim_1.setMinimumHeight(40)
        btn_anim_1.clicked.connect(lambda: self._set_animation(1.0))
        anim_grid.addWidget(btn_anim_1)

        anim_grid.addStretch(1)
        layout_anim.addLayout(anim_grid)
        main_layout.addWidget(card_anim)

        main_layout.addStretch(1)

        # Set content widget into scroll area and add to root layout
        scroll_area.setWidget(content_widget)
        root_layout.addWidget(scroll_area)

    # -------------------------------------------------------------
    # LOGIC HANDLERS
    # -------------------------------------------------------------
    def _refresh_all_info(self):
        self.log_requested.emit("INFO", "Đang đọc thông số màn hình, DPI và tần số quét...")

        # 1. Read DPI
        physical, override = adb_get_wm_density()
        if override:
            self.lbl_dpi_status.setText(f"Trạng thái DPI: Đang áp dụng [{override} DPI] (Gốc phần cứng: {physical} DPI)")
        elif physical:
            self.lbl_dpi_status.setText(f"Trạng thái DPI: Đang dùng mặc định [{physical} DPI]")
        else:
            self.lbl_dpi_status.setText("Trạng thái DPI: Không đọc được (Hãy kiểm tra cáp và bật USB Debugging)")

        # 2. Read Refresh Rates
        rates = adb_get_refresh_rates()
        user_r = rates.get("user_refresh_rate", "Auto")
        min_r = rates.get("min_refresh_rate", "Auto")
        peak_r = rates.get("peak_refresh_rate", "Auto")
        self.lbl_hz_status.setText(f"Tần số quét hiện tại: [User: {user_r}Hz | Min: {min_r}Hz | Peak: {peak_r}Hz]")

        # 3. Read Animation
        anim = adb_get_animation_scale()
        self.lbl_anim_status.setText(f"Tốc độ hiệu ứng chuyển động: [{anim}]")

        self.log_requested.emit("SUCCESS", f"Đã đọc xong: DPI={override or physical}, UserHz={user_r}, Anim={anim}")

    def _apply_density(self, dpi: int):
        self.log_requested.emit("INFO", f"Đang thay đổi mật độ điểm ảnh sang {dpi} DPI...")
        ok, msg = adb_set_wm_density(dpi)
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            self._refresh_all_info()
            QMessageBox.information(self, "Đổi DPI Thành Công", f"Đã đổi mật độ hiển thị sang {dpi} DPI!\nMàn hình máy tính bảng đã áp dụng ngay lập tức.")
        else:
            QMessageBox.critical(self, "Lỗi Đổi DPI", f"Không thể đổi DPI: {msg}\n\nHãy đảm bảo máy đã cắm cáp và bật USB Debugging.")

    def _reset_density(self):
        self.log_requested.emit("INFO", "Khôi phục DPI về mặc định gốc...")
        ok, msg = adb_reset_wm_density()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            self._refresh_all_info()
            QMessageBox.information(self, "Reset DPI Thành Công", "Đã khôi phục DPI về chuẩn gốc xuất xưởng (320 DPI)!")
        else:
            QMessageBox.critical(self, "Lỗi Reset DPI", f"Không thể reset DPI: {msg}")

    def _set_refresh_rate(self, mode: str):
        self.log_requested.emit("INFO", f"Đang thay đổi thiết lập tần số quét ({mode})...")
        ok, msg = adb_set_refresh_rate(mode)
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            self._refresh_all_info()
            QMessageBox.information(self, "Cài Đặt Tần Số Quét", f"Thành công: {msg}")
        else:
            QMessageBox.critical(self, "Lỗi Tần Số Quét", f"Không thể đổi tần số quét: {msg}")

    def _set_animation(self, scale: float):
        self.log_requested.emit("INFO", f"Đang chỉnh tốc độ hiệu ứng sang {scale}x...")
        ok, msg = adb_set_animation_scales(scale)
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            self._refresh_all_info()
            QMessageBox.information(self, "Tốc Độ Hiệu Ứng", f"Thành công: {msg}")
        else:
            QMessageBox.critical(self, "Lỗi Hiệu Ứng", f"Không thể chỉnh hiệu ứng: {msg}")

    def _restart_launcher(self):
        self.log_requested.emit("INFO", "Đang gửi lệnh tải lại màn hình chính để tự động sắp xếp icon...")
        ok, msg = adb_restart_launcher()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            QMessageBox.information(
                self,
                "Sắp Xếp Icon Thành Công",
                "Đã khởi động lại màn hình chính!\n\n"
                "Các biểu tượng ứng dụng (icon) sẽ tự động tính toán lại tỷ lệ và căn chỉnh ngay ngắn vào lưới mới.\n\n"
                "👉 MẸO: Bạn cũng có thể chụm 2 ngón tay trên màn hình chính và lắc nhẹ máy để gom icon cực nhanh!"
            )

    def _open_workstation(self):
        self.log_requested.emit("INFO", "Đang mở trang cài đặt Chế độ máy trạm (Workstation Mode)...")
        ok, msg = adb_open_workstation_mode()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            QMessageBox.information(
                self,
                "Chế Độ Máy Trạm (Workstation Mode)",
                "Đã mở trang cài đặt bí mật trên màn hình máy tính bảng!\n\n"
                "👉 HƯỚNG DẪN TRÊN MÁY TÍNH BẢNG:\n"
                "1. Bạn hãy nhìn vào màn hình máy tính bảng.\n"
                "2. Gạt công tắc BẬT mục 'Chế độ máy trạm' (Workstation Mode / Desktop Mode).\n"
                "3. Máy tính bảng sẽ chuyển sang giao diện máy tính với thanh Taskbar và các cửa sổ nổi tự do!"
            )
        else:
            QMessageBox.critical(self, "Lỗi Mở Workstation", f"Không thể mở: {msg}")
