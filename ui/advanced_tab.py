import os
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QMessageBox, QDialog, QTextEdit
)
from PyQt6.QtCore import pyqtSignal, Qt
from core.adb_fastboot import (
    adb_reboot_system,
    adb_reboot_recovery,
    adb_reboot_bootloader,
    fastboot_reboot,
    fastboot_reboot_recovery,
    fastboot_reboot_bootloader,
    fastboot_reboot_edl,
    fastboot_get_current_slot,
    fastboot_set_slot,
    get_all_fastboot_vars,
    run_command,
    FASTBOOT_EXE
)


class AdvancedTab(QWidget):
    """Tab containing advanced tools: reboot actions, hardware specs, driver helper, boot flasher."""

    log_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 1. Card: Reboot Controls
        card_reboot = QFrame()
        card_reboot.setObjectName("CardFrame")
        layout_reboot = QVBoxLayout(card_reboot)
        layout_reboot.setSpacing(12)

        lbl_reboot_title = QLabel("🔄 TÙY CHỌN KHỞI ĐỘNG LẠI (REBOOT CONTROLS)")
        lbl_reboot_title.setObjectName("SectionTitle")
        layout_reboot.addWidget(lbl_reboot_title)

        lbl_reboot_desc = QLabel("Tự động gửi lệnh khởi động lại phù hợp theo trạng thái hiện tại của thiết bị (ADB hoặc Fastboot):")
        lbl_reboot_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout_reboot.addWidget(lbl_reboot_desc)

        btn_grid = QHBoxLayout()
        btn_grid.setSpacing(10)

        btn_reboot_sys = QPushButton("📱 Vào Hệ Điều Hành (System)")
        btn_reboot_sys.clicked.connect(self._reboot_system)
        btn_grid.addWidget(btn_reboot_sys)

        btn_reboot_rec = QPushButton("🛠️ Vào Recovery")
        btn_reboot_rec.clicked.connect(self._reboot_recovery)
        btn_grid.addWidget(btn_reboot_rec)

        btn_reboot_fb = QPushButton("⚡ Vào FASTBOOT")
        btn_reboot_fb.clicked.connect(self._reboot_bootloader)
        btn_grid.addWidget(btn_reboot_fb)

        btn_reboot_edl = QPushButton("⚠️ Vào Chế độ EDL (9008)")
        btn_reboot_edl.setObjectName("DangerButton")
        btn_reboot_edl.setToolTip("Chế độ Emergency Download Mode Qualcomm dành cho cứu máy")
        btn_reboot_edl.clicked.connect(self._reboot_edl)
        btn_grid.addWidget(btn_reboot_edl)

        layout_reboot.addLayout(btn_grid)
        layout.addWidget(card_reboot)

        # 2. Card: A/B Slot Switcher
        card_slot = QFrame()
        card_slot.setObjectName("CardFrame")
        layout_slot = QVBoxLayout(card_slot)
        layout_slot.setSpacing(10)

        lbl_slot_title = QLabel("🔀 CHUYỂN ĐỔI PHÂN VÙNG KHỞI ĐỘNG (A/B SLOT SWITCHER)")
        lbl_slot_title.setObjectName("SectionTitle")
        layout_slot.addWidget(lbl_slot_title)

        lbl_slot_desc = QLabel(
            "Khi cài Windows 11 song song, bộ nạp UEFI thường nằm ở Slot B còn Android ở Slot A. "
            "Nếu máy bị lặp Fastboot sau khi xóa Windows, hãy chuyển về Slot A."
        )
        lbl_slot_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout_slot.addWidget(lbl_slot_desc)

        slot_btn_layout = QHBoxLayout()
        slot_btn_layout.setSpacing(10)

        self.lbl_current_slot = QLabel("Slot hiện tại: (Nhấn kiểm tra)")
        self.lbl_current_slot.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 13px;")
        slot_btn_layout.addWidget(self.lbl_current_slot, stretch=1)

        btn_check_slot = QPushButton("🔄 Đọc Slot Hiện Tại")
        btn_check_slot.clicked.connect(self._check_current_slot)
        slot_btn_layout.addWidget(btn_check_slot)

        btn_slot_a = QPushButton("🅰️ Chuyển sang Slot A (Android gốc)")
        btn_slot_a.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold;")
        btn_slot_a.clicked.connect(lambda: self._switch_slot("a"))
        slot_btn_layout.addWidget(btn_slot_a)

        btn_slot_b = QPushButton("🅱️ Chuyển sang Slot B")
        btn_slot_b.clicked.connect(lambda: self._switch_slot("b"))
        slot_btn_layout.addWidget(btn_slot_b)

        layout_slot.addLayout(slot_btn_layout)
        layout.addWidget(card_slot)

        # 3. Card: Fastboot Device Specs & Driver Helper
        card_specs = QFrame()
        card_specs.setObjectName("CardFrame")
        layout_specs = QVBoxLayout(card_specs)
        layout_specs.setSpacing(12)

        lbl_specs_title = QLabel("🔍 KIỂM TRA THÔNG TIN & TRỢ LÝ DRIVER")
        lbl_specs_title.setObjectName("SectionTitle")
        layout_specs.addWidget(lbl_specs_title)

        specs_row = QHBoxLayout()
        specs_row.setSpacing(12)

        btn_getvar = QPushButton("📋 Đọc Thông Số Phần Cứng (getvar all)")
        btn_getvar.clicked.connect(self._show_specs_dialog)
        specs_row.addWidget(btn_getvar)

        btn_dev_manager = QPushButton("🖥️ Mở Device Manager (Kiểm tra Driver Fastboot)")
        btn_dev_manager.clicked.connect(self._open_device_manager)
        specs_row.addWidget(btn_dev_manager)

        layout_specs.addLayout(specs_row)
        layout.addWidget(card_specs)

        # 3. Card: Flash Boot Image
        card_boot = QFrame()
        card_boot.setObjectName("CardFrame")
        layout_boot = QVBoxLayout(card_boot)
        layout_boot.setSpacing(12)

        lbl_boot_title = QLabel("⚡ NẠP FILE BOOT IMAGE (NẾU CẦN KHÔI PHỤC KERNEL GỐC)")
        lbl_boot_title.setObjectName("SectionTitle")
        layout_boot.addWidget(lbl_boot_title)

        lbl_boot_desc = QLabel(
            "Nếu bạn cần nạp lại phân vùng boot (ví dụ: gỡ bỏ Magisk hoặc nạp lại boot.img chuẩn từ ROM gốc):"
        )
        lbl_boot_desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout_boot.addWidget(lbl_boot_desc)

        boot_row = QHBoxLayout()
        boot_row.setSpacing(10)

        self.lbl_boot_file = QLabel("Chưa chọn file boot.img")
        self.lbl_boot_file.setStyleSheet("color: #64748b; font-style: italic;")
        boot_row.addWidget(self.lbl_boot_file, stretch=1)

        btn_choose_boot = QPushButton("📂 Chọn file boot.img...")
        btn_choose_boot.clicked.connect(self._choose_boot_file)
        boot_row.addWidget(btn_choose_boot)

        self.btn_flash_boot = QPushButton("⚡ Flash Boot Image")
        self.btn_flash_boot.setEnabled(False)
        self.btn_flash_boot.clicked.connect(self._flash_boot_image)
        boot_row.addWidget(self.btn_flash_boot)

        layout_boot.addLayout(boot_row)
        layout.addWidget(card_boot)

        layout.addStretch(1)

        self.selected_boot_file = None

    def _reboot_system(self):
        self.log_requested.emit("INFO", "Thực hiện lệnh khởi động lại vào Hệ điều hành (System)...")
        # Try fastboot first, then adb
        ok, msg = fastboot_reboot()
        if not ok:
            ok, msg = adb_reboot_system()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", f"Kết quả: {msg}")

    def _reboot_recovery(self):
        self.log_requested.emit("INFO", "Thực hiện lệnh khởi động lại vào Recovery...")
        ok, msg = fastboot_reboot_recovery()
        if not ok:
            ok, msg = adb_reboot_recovery()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", f"Kết quả: {msg}")

    def _reboot_bootloader(self):
        self.log_requested.emit("INFO", "Thực hiện lệnh khởi động lại vào FASTBOOT...")
        ok, msg = adb_reboot_bootloader()
        if not ok:
            ok, msg = fastboot_reboot_bootloader()
        self.log_requested.emit("SUCCESS" if ok else "ERROR", f"Kết quả: {msg}")

    def _reboot_edl(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận vào EDL (9008)",
            "Chế độ EDL (Qualcomm 9008) chỉ nên dùng khi bạn cần cứu máy bằng Mi Flash chuyên sâu.\nBạn có chắc chắn muốn vào chế độ EDL?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_requested.emit("WARNING", "Đang gửi lệnh vào chế độ EDL 9008...")
            ok, msg = fastboot_reboot_edl()
            self.log_requested.emit("SUCCESS" if ok else "ERROR", f"Kết quả: {msg}")

    def _show_specs_dialog(self):
        self.log_requested.emit("INFO", "Đang đọc thông số từ fastboot getvar all...")
        output = get_all_fastboot_vars()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Thông Số Kỹ Thuật Thiết Bị (fastboot getvar all)")
        dialog.resize(600, 450)
        
        d_layout = QVBoxLayout(dialog)
        d_layout.addWidget(QLabel("Dưới đây là toàn bộ thông số phần cứng thiết bị đọc từ Bootloader:"))
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(output)
        txt.setStyleSheet("background-color: #050811; color: #38bdf8; font-family: 'Consolas', monospace;")
        d_layout.addWidget(txt)
        
        btn_close = QPushButton("Đóng")
        btn_close.clicked.connect(dialog.accept)
        d_layout.addWidget(btn_close)
        
        dialog.exec()

    def _open_device_manager(self):
        try:
            subprocess.Popen(["devmgmt.msc"], shell=True)
            self.log_requested.emit("INFO", "Đã mở Windows Device Manager. Nếu thấy thiết bị 'Android' có dấu chấm than vàng, vui lòng cài driver Android Bootloader Interface.")
        except Exception as e:
            self.log_requested.emit("ERROR", f"Không thể mở Device Manager: {e}")

    def _choose_boot_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file Boot Image",
            "",
            "Image Files (*.img);;All Files (*.*)"
        )
        if file_path:
            self.selected_boot_file = file_path
            self.lbl_boot_file.setText(os.path.basename(file_path))
            self.lbl_boot_file.setStyleSheet("color: #38bdf8; font-weight: 600;")
            self.btn_flash_boot.setEnabled(True)
            self.log_requested.emit("INFO", f"Đã chọn file boot image: {file_path}")

    def _flash_boot_image(self):
        if not self.selected_boot_file or not os.path.isfile(self.selected_boot_file):
            return
        
        reply = QMessageBox.question(
            self,
            "Xác nhận Flash Boot",
            f"Bạn có chắc chắn muốn nạp file boot này vào thiết bị?\nFile: {os.path.basename(self.selected_boot_file)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_requested.emit("CMD", f"> fastboot flash boot {self.selected_boot_file}")
            code, stdout, stderr = run_command([FASTBOOT_EXE, "flash", "boot", self.selected_boot_file])
            if code == 0:
                self.log_requested.emit("SUCCESS", f"Flash boot image thành công!\n{stdout or stderr}")
            else:
                self.log_requested.emit("ERROR", f"Flash boot image thất bại: {stderr or stdout}")

    def _check_current_slot(self):
        slot = fastboot_get_current_slot()
        if slot:
            self.lbl_current_slot.setText(f"Slot hiện tại: [{slot.upper()}]")
            self.log_requested.emit("INFO", f"Phân vùng khởi động hiện tại là Slot {slot.upper()}")
        else:
            self.lbl_current_slot.setText("Slot hiện tại: Không xác định (Cần kết nối Fastboot)")
            self.log_requested.emit("WARNING", "Không thể đọc thông tin slot. Hãy đảm bảo máy đang ở Fastboot.")

    def _switch_slot(self, slot: str):
        self.log_requested.emit("INFO", f"Đang yêu cầu chuyển sang Slot {slot.upper()}...")
        ok, msg = fastboot_set_slot(slot)
        self.log_requested.emit("SUCCESS" if ok else "ERROR", msg)
        if ok:
            self.lbl_current_slot.setText(f"Slot hiện tại: [{slot.upper()}]")
            QMessageBox.information(
                self,
                "Chuyển Slot thành công",
                f"Đã chuyển phân vùng khởi động sang Slot {slot.upper()}!\n\n"
                f"Bạn có thể bấm nút 'Vào Hệ Điều Hành (System)' hoặc giữ nút Nguồn để khởi động lại máy."
            )
