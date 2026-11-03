import os
from typing import List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QCheckBox, QProgressBar,
    QAbstractItemView, QSplitter
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread

from core.adb_fastboot import (
    adb_list_packages,
    adb_uninstall_package,
    adb_disable_package,
    adb_enable_package,
    adb_install_apk,
    XIAOMI_BLOATWARE_PRESET,
    run_command,
    ADB_EXE
)


class PackageWorker(QThread):
    """Worker thread for package operations (listing, uninstalling, disabling, enabling)."""
    finished_list = pyqtSignal(list)
    action_progress = pyqtSignal(int, int, str)
    action_completed = pyqtSignal(str)
    log_signal = pyqtSignal(str, str)

    def __init__(self, mode: str, data=None):
        super().__init__()
        self.mode = mode  # 'list', 'uninstall', 'disable', 'enable'
        self.data = data

    def run(self):
        if self.mode == "list":
            filter_type = self.data or "all"
            self.log_signal.emit("INFO", f"Đang quét danh sách ứng dụng từ thiết bị (Bộ lọc: {filter_type})...")
            packages = adb_list_packages(filter_type)
            self.finished_list.emit(packages)
            self.log_signal.emit("SUCCESS", f"Đã tìm thấy {len(packages)} ứng dụng trên thiết bị.")

        elif self.mode in ("uninstall", "disable", "enable"):
            packages = self.data or []
            total = len(packages)
            success_count = 0

            for idx, pkg in enumerate(packages, 1):
                self.action_progress.emit(idx, total, f"Đang xử lý [{idx}/{total}]: {pkg}")
                
                if self.mode == "uninstall":
                    ok, msg = adb_uninstall_package(pkg)
                elif self.mode == "disable":
                    ok, msg = adb_disable_package(pkg)
                else:
                    ok, msg = adb_enable_package(pkg)

                if ok:
                    success_count += 1
                    self.log_signal.emit("SUCCESS", msg)
                else:
                    self.log_signal.emit("WARNING", msg)

            summary = f"Hoàn tất thao tác: Thành công {success_count}/{total} ứng dụng."
            self.action_completed.emit(summary)
            self.log_signal.emit("SUCCESS", summary)


class ApkInstallWorker(QThread):
    """Worker thread for batch APK installation."""
    apk_progress = pyqtSignal(int, int, str, str)  # idx, total, filename, status
    all_done = pyqtSignal(int, int)  # success_count, total
    log_signal = pyqtSignal(str, str)

    def __init__(self, apk_list: List[str], reinstall=True, downgrade=False, grant_perms=True):
        super().__init__()
        self.apk_list = apk_list
        self.reinstall = reinstall
        self.downgrade = downgrade
        self.grant_perms = grant_perms

    def run(self):
        total = len(self.apk_list)
        success_count = 0
        self.log_signal.emit("INFO", f"Bắt đầu cài đặt hàng loạt {total} file APK qua ADB...")

        for idx, apk_path in enumerate(self.apk_list, 1):
            fname = os.path.basename(apk_path)
            self.apk_progress.emit(idx, total, fname, "Đang cài đặt...")
            self.log_signal.emit("CMD", f"> adb install {fname}")

            ok, msg = adb_install_apk(
                apk_path,
                reinstall=self.reinstall,
                downgrade=self.downgrade,
                grant_permissions=self.grant_perms
            )

            if ok:
                success_count += 1
                self.apk_progress.emit(idx, total, fname, "Thành công ✅")
                self.log_signal.emit("SUCCESS", f"[{idx}/{total}] Cài đặt thành công: {fname}")
            else:
                self.apk_progress.emit(idx, total, fname, "Thất bại ❌")
                self.log_signal.emit("ERROR", f"[{idx}/{total}] Cài đặt lỗi {fname}: {msg}")

        self.all_done.emit(success_count, total)
        self.log_signal.emit("SUCCESS", f"Đã hoàn thành cài đặt {success_count}/{total} file APK.")


class AppManagerTab(QWidget):
    """Tab for Debloating Apps and Batch Installing APKs via ADB."""

    log_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_loaded_packages = []
        self.worker = None
        self.install_worker = None
        self.apk_queue = []

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setHandleWidth(8)

        # -------------------------------------------------------------
        # SECTION 1: DEBLOAT & PACKAGE MANAGER
        # -------------------------------------------------------------
        debloat_widget = QWidget()
        debloat_layout = QVBoxLayout(debloat_widget)
        debloat_layout.setContentsMargins(0, 0, 0, 0)
        debloat_layout.setSpacing(10)

        card_debloat = QFrame()
        card_debloat.setObjectName("CardFrame")
        card_debloat_layout = QVBoxLayout(card_debloat)
        card_debloat_layout.setSpacing(10)

        # Header Title
        title_row = QHBoxLayout()
        lbl_debloat_title = QLabel("🧹 DỌN DẸP ỨNG DỤNG RÁC & BLOATWARE (ADB DEBLOATER)")
        lbl_debloat_title.setObjectName("SectionTitle")
        title_row.addWidget(lbl_debloat_title)

        lbl_guide = QLabel("(Thiết bị cần ở Android và đã bật USB Debugging)")
        lbl_guide.setStyleSheet("color: #38bdf8; font-size: 12px;")
        title_row.addWidget(lbl_guide)
        title_row.addStretch(1)

        card_debloat_layout.addLayout(title_row)

        # Controls Row (Filter, Search, Refresh, Select All)
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(8)

        self.cmb_filter = QComboBox()
        self.cmb_filter.addItems([
            "⭐ Đề xuất dọn rác Xiaomi (Safe Xiaomi Debloat)",
            "📦 Tất cả ứng dụng (All Packages)",
            "👤 Ứng dụng người dùng cài (3rd Party -3)",
            "⚙️ Ứng dụng hệ thống (System -s)",
            "🚫 Ứng dụng đã vô hiệu hóa (Disabled -d)"
        ])
        self.cmb_filter.currentIndexChanged.connect(self._on_filter_changed)
        ctrl_row.addWidget(self.cmb_filter)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm theo tên gói (vd: miui, analytics, facebook, google)...")
        self.txt_search.textChanged.connect(self._filter_table_items)
        ctrl_row.addWidget(self.txt_search, stretch=1)

        self.btn_refresh = QPushButton("🔄 Tải Danh Sách")
        self.btn_refresh.clicked.connect(self._load_packages)
        ctrl_row.addWidget(self.btn_refresh)

        self.btn_select_all = QPushButton("☑️ Chọn Tất Cả")
        self.btn_select_all.clicked.connect(self._select_all_items)
        ctrl_row.addWidget(self.btn_select_all)

        self.btn_deselect_all = QPushButton("⬜ Bỏ Chọn")
        self.btn_deselect_all.clicked.connect(self._deselect_all_items)
        ctrl_row.addWidget(self.btn_deselect_all)

        card_debloat_layout.addLayout(ctrl_row)

        # Table of Packages
        self.table_packages = QTableWidget()
        self.table_packages.setColumnCount(4)
        self.table_packages.setHorizontalHeaderLabels(["Chọn", "Tên Gói Ứng Dụng (Package Name)", "Mô Tả / Khuyến Nghị", "Loại"])
        self.table_packages.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packages.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_packages.setColumnWidth(1, 320)
        self.table_packages.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_packages.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_packages.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        card_debloat_layout.addWidget(self.table_packages, stretch=1)

        # Debloat Action Buttons Row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_quick_xiaomi = QPushButton("⚡ 1-Click Dọn Rác Xiaomi (Khuyên Dùng)")
        self.btn_quick_xiaomi.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0ea5e9);
            color: white; font-weight: bold; padding: 8px 14px;
        """)
        self.btn_quick_xiaomi.setToolTip("Tự động gỡ bỏ các ứng dụng rác, quảng cáo, theo dõi ngầm mặc định của MIUI/HyperOS an toàn.")
        self.btn_quick_xiaomi.clicked.connect(self._quick_xiaomi_debloat)
        action_row.addWidget(self.btn_quick_xiaomi)

        self.btn_uninstall = QPushButton("🗑️ Gỡ Bỏ Đã Chọn (Uninstall User 0)")
        self.btn_uninstall.setObjectName("DangerButton")
        self.btn_uninstall.clicked.connect(lambda: self._execute_package_action("uninstall"))
        action_row.addWidget(self.btn_uninstall)

        self.btn_disable = QPushButton("🚫 Vô Hiệu Hóa (Disable)")
        self.btn_disable.clicked.connect(lambda: self._execute_package_action("disable"))
        action_row.addWidget(self.btn_disable)

        self.btn_enable = QPushButton("✅ Bật Lại (Enable)")
        self.btn_enable.clicked.connect(lambda: self._execute_package_action("enable"))
        action_row.addWidget(self.btn_enable)

        action_row.addStretch(1)

        self.lbl_package_count = QLabel("Tổng số: 0 ứng dụng")
        self.lbl_package_count.setStyleSheet("color: #94a3b8; font-weight: 600;")
        action_row.addWidget(self.lbl_package_count)

        card_debloat_layout.addLayout(action_row)
        debloat_layout.addWidget(card_debloat)
        splitter.addWidget(debloat_widget)

        # -------------------------------------------------------------
        # SECTION 2: BATCH APK INSTALLER
        # -------------------------------------------------------------
        apk_widget = QWidget()
        apk_layout = QVBoxLayout(apk_widget)
        apk_layout.setContentsMargins(0, 0, 0, 0)
        apk_layout.setSpacing(10)

        card_apk = QFrame()
        card_apk.setObjectName("CardFrame")
        card_apk_layout = QVBoxLayout(card_apk)
        card_apk_layout.setSpacing(10)

        lbl_apk_title = QLabel("📥 CÀI ĐẶT ỨNG DỤNG APK QUA ADB (BATCH APK INSTALLER)")
        lbl_apk_title.setObjectName("SectionTitle")
        card_apk_layout.addWidget(lbl_apk_title)

        # Options & Add Files Row
        opts_row = QHBoxLayout()
        opts_row.setSpacing(14)

        self.chk_reinstall = QCheckBox("Ghi đè ứng dụng cũ (-r)")
        self.chk_reinstall.setChecked(True)
        opts_row.addWidget(self.chk_reinstall)

        self.chk_grant_perms = QCheckBox("Tự động cấp tất cả quyền (-g)")
        self.chk_grant_perms.setChecked(True)
        opts_row.addWidget(self.chk_grant_perms)

        self.chk_downgrade = QCheckBox("Cho phép hạ cấp phiên bản (-d)")
        self.chk_downgrade.setChecked(False)
        opts_row.addWidget(self.chk_downgrade)

        opts_row.addStretch(1)

        btn_add_apk = QPushButton("📂 Chọn File APK...")
        btn_add_apk.setStyleSheet("background-color: #0284c7; color: white; font-weight: bold;")
        btn_add_apk.clicked.connect(self._choose_apks)
        opts_row.addWidget(btn_add_apk)

        btn_clear_apk = QPushButton("❌ Xóa Danh Sách")
        btn_clear_apk.clicked.connect(self._clear_apks)
        opts_row.addWidget(btn_clear_apk)

        card_apk_layout.addLayout(opts_row)

        # Table of APKs
        self.table_apks = QTableWidget()
        self.table_apks.setColumnCount(4)
        self.table_apks.setHorizontalHeaderLabels(["Tên File", "Dung Lượng (MB)", "Trạng Thái", "Đường Dẫn Đầy Đủ"])
        self.table_apks.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_apks.setColumnWidth(0, 240)
        self.table_apks.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_apks.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_apks.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        card_apk_layout.addWidget(self.table_apks)

        # Install Action Bar
        install_action_row = QHBoxLayout()
        install_action_row.setSpacing(12)

        self.apk_progress = QProgressBar()
        self.apk_progress.setRange(0, 100)
        self.apk_progress.setValue(0)
        self.apk_progress.setTextVisible(True)
        self.apk_progress.setFormat("Sẵn sàng")
        install_action_row.addWidget(self.apk_progress, stretch=1)

        self.btn_start_install = QPushButton("🚀 BẮT ĐẦU CÀI ĐẶT TẤT CẢ APK")
        self.btn_start_install.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
            color: white; font-weight: bold; padding: 10px 20px; font-size: 14px;
        """)
        self.btn_start_install.setEnabled(False)
        self.btn_start_install.clicked.connect(self._start_install_apks)
        install_action_row.addWidget(self.btn_start_install)

        card_apk_layout.addLayout(install_action_row)
        apk_layout.addWidget(card_apk)
        splitter.addWidget(apk_widget)

        # Set initial splitter proportion
        splitter.setSizes([380, 220])
        main_layout.addWidget(splitter)

    # -------------------------------------------------------------
    # DEBLOAT / PACKAGE LOGIC
    # -------------------------------------------------------------
    def _on_filter_changed(self, index: int):
        self._load_packages()

    def _load_packages(self):
        filter_idx = self.cmb_filter.currentIndex()
        filter_mode = "all"
        if filter_idx == 1:
            filter_mode = "all"
        elif filter_idx == 2:
            filter_mode = "user"
        elif filter_idx == 3:
            filter_mode = "system"
        elif filter_idx == 4:
            filter_mode = "disabled"

        self.btn_refresh.setEnabled(False)
        self.table_packages.setRowCount(0)
        self.lbl_package_count.setText("Đang đọc dữ liệu...")

        self.worker = PackageWorker(mode="list", data=filter_mode)
        self.worker.log_signal.connect(self.log_requested.emit)
        self.worker.finished_list.connect(self._on_packages_loaded)
        self.worker.start()

    def _on_packages_loaded(self, packages: list):
        self.btn_refresh.setEnabled(True)
        self.all_loaded_packages = packages
        self._populate_package_table(packages)

    def _populate_package_table(self, packages: list):
        filter_idx = self.cmb_filter.currentIndex()
        only_xiaomi_preset = (filter_idx == 0)

        # Filter if Preset is selected
        display_list = []
        if only_xiaomi_preset:
            for pkg in packages:
                if pkg in XIAOMI_BLOATWARE_PRESET:
                    display_list.append((pkg, XIAOMI_BLOATWARE_PRESET[pkg], "Bloatware Rác"))
            # If no packages were returned (e.g. tablet not connected yet or custom ROM), show preset list as reference
            if not display_list and not packages:
                for pkg, desc in XIAOMI_BLOATWARE_PRESET.items():
                    display_list.append((pkg, desc, "Đề xuất gỡ"))
        else:
            for pkg in packages:
                desc = XIAOMI_BLOATWARE_PRESET.get(pkg, "Ứng dụng Android")
                tag = "Rác Xiaomi" if pkg in XIAOMI_BLOATWARE_PRESET else "Hệ thống / Người dùng"
                display_list.append((pkg, desc, tag))

        self.table_packages.setRowCount(len(display_list))

        for row, (pkg, desc, tag) in enumerate(display_list):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.table_packages.setItem(row, 0, chk_item)

            pkg_item = QTableWidgetItem(pkg)
            pkg_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_packages.setItem(row, 1, pkg_item)

            desc_item = QTableWidgetItem(desc)
            desc_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if pkg in XIAOMI_BLOATWARE_PRESET:
                desc_item.setForeground(Qt.GlobalColor.cyan)
            self.table_packages.setItem(row, 2, desc_item)

            tag_item = QTableWidgetItem(tag)
            tag_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table_packages.setItem(row, 3, tag_item)

        self.lbl_package_count.setText(f"Hiển thị: {len(display_list)} ứng dụng")

    def _filter_table_items(self, text: str):
        query = text.strip().lower()
        visible_count = 0
        for row in range(self.table_packages.rowCount()):
            pkg_name = self.table_packages.item(row, 1).text().lower()
            desc = self.table_packages.item(row, 2).text().lower()
            match = query in pkg_name or query in desc
            self.table_packages.setRowHidden(row, not match)
            if match:
                visible_count += 1
        self.lbl_package_count.setText(f"Hiển thị: {visible_count} ứng dụng")

    def _select_all_items(self):
        for row in range(self.table_packages.rowCount()):
            if not self.table_packages.isRowHidden(row):
                item = self.table_packages.item(row, 0)
                if item:
                    item.setCheckState(Qt.CheckState.Checked)

    def _deselect_all_items(self):
        for row in range(self.table_packages.rowCount()):
            item = self.table_packages.item(row, 0)
            if item:
                item.setCheckState(Qt.CheckState.Unchecked)

    def _get_checked_packages(self) -> List[str]:
        checked = []
        for row in range(self.table_packages.rowCount()):
            if not self.table_packages.isRowHidden(row):
                chk = self.table_packages.item(row, 0)
                if chk and chk.checkState() == Qt.CheckState.Checked:
                    pkg_item = self.table_packages.item(row, 1)
                    if pkg_item:
                        checked.append(pkg_item.text().strip())
        return checked

    def _execute_package_action(self, action: str):
        selected = self._get_checked_packages()
        if not selected:
            QMessageBox.warning(self, "Chưa chọn ứng dụng", "Vui lòng tích chọn ít nhất 1 ứng dụng trong danh sách để thao tác.")
            return

        action_names = {
            "uninstall": "gỡ bỏ (an toàn cho user 0)",
            "disable": "vô hiệu hóa",
            "enable": "bật lại"
        }
        name = action_names.get(action, action)

        reply = QMessageBox.question(
            self,
            f"Xác nhận {name.upper()}",
            f"Bạn có chắc chắn muốn {name} {len(selected)} ứng dụng đã chọn?\n\n"
            f"Danh sách đầu tiên: {', '.join(selected[:4])}{'...' if len(selected) > 4 else ''}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        self._set_debloat_buttons_enabled(False)

        self.worker = PackageWorker(mode=action, data=selected)
        self.worker.log_signal.connect(self.log_requested.emit)
        self.worker.action_completed.connect(self._on_package_action_finished)
        self.worker.start()

    def _on_package_action_finished(self, summary: str):
        self._set_debloat_buttons_enabled(True)
        QMessageBox.information(self, "Thông Báo", summary)
        self._load_packages()

    def _set_debloat_buttons_enabled(self, enabled: bool):
        self.btn_refresh.setEnabled(enabled)
        self.btn_quick_xiaomi.setEnabled(enabled)
        self.btn_uninstall.setEnabled(enabled)
        self.btn_disable.setEnabled(enabled)
        self.btn_enable.setEnabled(enabled)

    def _quick_xiaomi_debloat(self):
        """Pre-check all known Xiaomi bloatware and prompt user to clean with 1-click."""
        self.cmb_filter.setCurrentIndex(0)
        self._select_all_items()
        selected = self._get_checked_packages()
        if not selected:
            QMessageBox.information(self, "Thông Báo", "Không tìm thấy ứng dụng bloatware rác nào của Xiaomi trên máy (hoặc máy bạn đang dùng Custom ROM sạch).")
            return

        self._execute_package_action("uninstall")

    # -------------------------------------------------------------
    # BATCH APK INSTALLER LOGIC
    # -------------------------------------------------------------
    def _choose_apks(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Chọn file APK cần cài đặt",
            "",
            "Android Packages (*.apk);;All Files (*.*)"
        )
        if not files:
            return

        for fpath in files:
            if fpath not in [item["path"] for item in self.apk_queue]:
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                self.apk_queue.append({
                    "name": os.path.basename(fpath),
                    "size": f"{size_mb:.2f}",
                    "status": "Chờ cài đặt",
                    "path": fpath
                })

        self._refresh_apk_table()

    def _clear_apks(self):
        self.apk_queue.clear()
        self._refresh_apk_table()
        self.apk_progress.setValue(0)
        self.apk_progress.setFormat("Sẵn sàng")

    def _refresh_apk_table(self):
        self.table_apks.setRowCount(len(self.apk_queue))
        for row, item in enumerate(self.apk_queue):
            name_item = QTableWidgetItem(item["name"])
            size_item = QTableWidgetItem(item["size"])
            status_item = QTableWidgetItem(item["status"])
            path_item = QTableWidgetItem(item["path"])

            for it in (name_item, size_item, status_item, path_item):
                it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            self.table_apks.setItem(row, 0, name_item)
            self.table_apks.setItem(row, 1, size_item)
            self.table_apks.setItem(row, 2, status_item)
            self.table_apks.setItem(row, 3, path_item)

        self.btn_start_install.setEnabled(len(self.apk_queue) > 0)

    def _start_install_apks(self):
        if not self.apk_queue:
            return

        apk_paths = [it["path"] for it in self.apk_queue]

        self.btn_start_install.setEnabled(False)
        self.apk_progress.setValue(0)
        self.apk_progress.setFormat(f"0/{len(apk_paths)} đang cài đặt...")

        self.install_worker = ApkInstallWorker(
            apk_paths,
            reinstall=self.chk_reinstall.isChecked(),
            downgrade=self.chk_downgrade.isChecked(),
            grant_perms=self.chk_grant_perms.isChecked()
        )
        self.install_worker.log_signal.connect(self.log_requested.emit)
        self.install_worker.apk_progress.connect(self._on_apk_progress)
        self.install_worker.all_done.connect(self._on_all_apks_installed)
        self.install_worker.start()

    def _on_apk_progress(self, idx: int, total: int, filename: str, status: str):
        pct = int((idx / total) * 100)
        self.apk_progress.setValue(pct)
        self.apk_progress.setFormat(f"[{idx}/{total}] {status}: {filename}")

        for row in range(self.table_apks.rowCount()):
            if self.table_apks.item(row, 0).text() == filename:
                self.table_apks.item(row, 2).setText(status)
                break

    def _on_all_apks_installed(self, success_count: int, total: int):
        self.btn_start_install.setEnabled(True)
        self.apk_progress.setValue(100)
        self.apk_progress.setFormat(f"Đã hoàn thành ({success_count}/{total})")

        QMessageBox.information(
            self,
            "Cài Đặt APK Hoàn Tất",
            f"Quá trình cài đặt hoàn thành!\n- Thành công: {success_count}/{total} file APK."
        )
