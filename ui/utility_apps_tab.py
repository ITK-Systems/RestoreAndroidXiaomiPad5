import os
import subprocess
import urllib.request
from typing import List, Dict, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QLineEdit, QComboBox, QProgressBar,
    QScrollArea, QGridLayout, QApplication
)
from PyQt6.QtCore import pyqtSignal, Qt, QThread

from core.constants import APKS_DIR, ADB_EXE
from core.adb_fastboot import (
    adb_list_packages,
    adb_uninstall_package,
    adb_install_apk
)


# =========================================================================
# CURATED APPS CATALOG FOR XIAOMI PAD 5
# =========================================================================
UTILITY_APPS_CATALOG: List[Dict] = [
    {
        "id": "cpu_info",
        "name": "CPU Info (Hardware & System Monitor)",
        "package": "com.kgurgul.cpuinfo",
        "category": "Giám Sát Phần Cứng",
        "size_str": "2.8 MB",
        "icon": "⚡",
        "badge": "Mã Nguồn Mở • Siêu Nhẹ 2.8MB",
        "desc": "Ứng dụng giám sát phần cứng chuyên sâu cho Xiaomi Pad 5: Theo dõi nhiệt độ thời gian thực của chip Snapdragon 860, xung nhịp 8 nhân, mức RAM, tình trạng pin và màn hình 120Hz.",
        "filename": "CPU_Info_v6.7.0.apk",
        "download_url": "https://github.com/kamgurgul/cpu-info/releases/download/android-6.7.0/androidApp-release.apk"
    },
    {
        "id": "shizuku",
        "name": "Shizuku (Quyền Quản Trị Hệ Thống ADB)",
        "package": "moe.shizuku.privileged.api",
        "category": "Công Cụ Hệ Thống",
        "size_str": "2.5 MB",
        "icon": "🛠️",
        "badge": "Tiện Ích Số 1 • Chạy Lệnh ADB Trực Tiếp",
        "desc": "Cho phép các ứng dụng nâng cao chạy lệnh ADB trực tiếp trên máy tính bảng mà không cần cắm lại máy tính. Cực kỳ tiện lợi để tinh chỉnh hệ thống và tối ưu trải nghiệm.",
        "filename": "Shizuku_v13.6.0.apk",
        "download_url": "https://github.com/RikkaApps/Shizuku/releases/download/v13.6.0/shizuku-v13.6.0.r1086.2650830c-release.apk"
    },
    {
        "id": "newpipe",
        "name": "NewPipe (YouTube Chặn Quảng Cáo & Nghe Nhạc Ẩn)",
        "package": "org.schabi.newpipe",
        "category": "Giải Trí & Xem Phim",
        "size_str": "11.5 MB",
        "icon": "🎬",
        "badge": "Chặn 100% Quảng Cáo • Nghe Nhạc Tắt Màn Hình",
        "desc": "Xem YouTube mượt mà, chặn toàn bộ quảng cáo, hỗ trợ phát âm thanh khi tắt màn hình, tải video Full HD/2K và nhạc MP3. Tối ưu nhẹ hơn 5 lần ứng dụng YouTube mặc định.",
        "filename": "NewPipe_v0.29.1.apk",
        "download_url": "https://github.com/TeamNewPipe/NewPipe/releases/download/v0.29.1/NewPipe_v0.29.1.apk"
    },
    {
        "id": "aurora_store",
        "name": "Aurora Store (Google Play Store Sạch)",
        "package": "com.aurora.store",
        "category": "Cửa Hàng Ứng Dụng",
        "size_str": "8.5 MB",
        "icon": "🛒",
        "badge": "Tải App Không Cần Đăng Nhập",
        "desc": "Tải và cập nhật mọi ứng dụng từ Google Play Store mà không bắt buộc đăng nhập tài khoản Google cá nhân. Giao diện Material You hiện đại, hỗ trợ cài đặt tự động.",
        "filename": "AuroraStore_v4.8.4.apk",
        "download_url": "https://auroraoss.com/download/AuroraStore/Release/AuroraStore_4.8.4.apk"
    },
    {
        "id": "fdroid",
        "name": "F-Droid (Kho Ứng Dụng Mã Nguồn Mở 100% Miễn Phí)",
        "package": "org.fdroid.fdroid",
        "category": "Cửa Hàng Ứng Dụng",
        "size_str": "12.5 MB",
        "icon": "📦",
        "badge": "100% Free • Không Theo Dõi",
        "desc": "Kho ứng dụng mã nguồn mở lớn nhất thế giới Android. Toàn bộ app đều miễn phí 100%, không quảng cáo, không theo dõi và tôn trọng quyền riêng tư người dùng.",
        "filename": "F-Droid.apk",
        "download_url": "https://f-droid.org/F-Droid.apk"
    },
    {
        "id": "vlc",
        "name": "VLC Media Player (Xem Phim Đa Định Dạng 2.5K)",
        "package": "org.videolan.vlc",
        "category": "Giải Trí & Xem Phim",
        "size_str": "35 MB",
        "icon": "🎥",
        "badge": "Hỗ Trợ 4K HDR • Phụ Đề Rời",
        "desc": "Trình phát đa phương tiện số 1 thế giới. Chơi mượt mà mọi định dạng MKV, MP4, ISO, hỗ trợ phụ đề tiếng Việt và âm thanh vòm trên màn hình 2.5K sắc nét của Pad 5.",
        "filename": "VLC_Android_3.5.4.apk",
        "download_url": "https://get.videolan.org/vlc-android/3.5.4/VLC-Android-3.5.4-arm64-v8a.apk"
    },
    {
        "id": "koreader",
        "name": "KOReader (Đọc Sách EPUB & PDF Chuyên Nghiệp)",
        "package": "org.koreader.launcher",
        "category": "Đọc Sách & Học Tập",
        "size_str": "29 MB",
        "icon": "📖",
        "badge": "Tối Ưu PDF & EPUB • Phông Chữ Sắc Nét",
        "desc": "Ứng dụng đọc sách EPUB, PDF chuyên sâu tốt nhất cho máy tính bảng. Tối ưu hiển thị phông chữ sắc nét, căn lề thông minh, ghi chú và chế độ đọc ban đêm chống mỏi mắt.",
        "filename": "KOReader_v2026.07.1.apk",
        "download_url": "https://github.com/koreader/koreader/releases/download/v2026.07.1/koreader-android-arm-v2026.07.1.apk"
    },
    {
        "id": "mihon",
        "name": "Mihon (Đọc Truyện Tranh / Manga Màn Hình 2.5K)",
        "package": "mihon.app",
        "category": "Đọc Sách & Học Tập",
        "size_str": "27.7 MB",
        "icon": "📚",
        "badge": "Kế Thừa Tachiyomi • Tối Ưu Màn 11 Inch",
        "desc": "Ứng dụng đọc truyện tranh/manga hàng đầu thế giới kế thừa từ Tachiyomi. Tận dụng trọn vẹn màn hình 11 inch 2.5K sắc nét, hỗ trợ hàng trăm nguồn đọc tiếng Việt phong phú.",
        "filename": "Mihon_v0.21.3.apk",
        "download_url": "https://github.com/mihonapp/mihon/releases/download/v0.21.3/mihon-arm64-v8a-v0.21.3.apk"
    },
    {
        "id": "libretorrent",
        "name": "LibreTorrent (Trình Tải File & Phim Torrent Sạch)",
        "package": "org.proninyaroslav.libretorrent",
        "category": "Tải File & Công Cụ",
        "size_str": "23 MB",
        "icon": "⚡",
        "badge": "Mã Nguồn Mở • Tốc Độ Cao",
        "desc": "Trình tải torrent mã nguồn mở hoàn toàn sạch, không quảng cáo, tối ưu tốc độ tải phim 4K, tài liệu trực tiếp vào bộ nhớ trong máy tính bảng.",
        "filename": "LibreTorrent_v4.1.1.apk",
        "download_url": "https://github.com/proninyaroslav/libretorrent/releases/download/4.1.1/LibreTorrent-4.1.1-arm64-v8a.apk"
    }
]


# =========================================================================
# WORKER THREAD: DOWNLOAD & INSTALL APK
# =========================================================================
class AppInstallWorker(QThread):
    progress_signal = pyqtSignal(str, int, str)  # app_id, percent, status_text
    log_signal = pyqtSignal(str, str)            # level, message
    finished_signal = pyqtSignal(str, bool, str) # app_id, success, message

    def __init__(self, app_info: Dict):
        super().__init__()
        self.app = app_info

    def run(self):
        app_id = self.app["id"]
        app_name = self.app["name"]
        filename = self.app["filename"]
        url = self.app["download_url"]
        local_path = os.path.join(APKS_DIR, filename)

        # 1. Download if not already in local cache
        if not os.path.isfile(local_path) or os.path.getsize(local_path) < 10000:
            self.log_signal.emit("INFO", f"Bắt đầu tải xuống {app_name}...")
            self.progress_signal.emit(app_id, 10, "Đang kết nối tải xuống...")

            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    total_size = int(resp.headers.get("content-length", 0))
                    downloaded = 0
                    chunk_size = 65536

                    with open(local_path, "wb") as f:
                        while chunk := resp.read(chunk_size):
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                pct = min(90, int((downloaded / total_size) * 80) + 10)
                                mb_done = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                self.progress_signal.emit(app_id, pct, f"Đang tải: {mb_done:.1f} / {mb_total:.1f} MB ({pct}%)")

                self.log_signal.emit("SUCCESS", f"Tải xuống hoàn tất: {filename}")
            except Exception as e:
                self.log_signal.emit("ERROR", f"Tải thất bại {app_name}: {e}")
                self.progress_signal.emit(app_id, 0, "Lỗi tải xuống")
                self.finished_signal.emit(app_id, False, f"Không thể tải file: {e}")
                return
        else:
            self.log_signal.emit("INFO", f"Sử dụng file APK sẵn có trong bộ đệm: {filename}")

        # 2. Install via ADB
        self.progress_signal.emit(app_id, 92, "Đang nạp và cài đặt qua ADB...")
        self.log_signal.emit("CMD", f"> adb install -r -g {filename}")

        ok, msg = adb_install_apk(local_path, reinstall=True, grant_permissions=True)
        if ok:
            self.progress_signal.emit(app_id, 100, "Đã cài đặt thành công ✅")
            self.log_signal.emit("SUCCESS", f"Đã cài đặt thành công {app_name} vào Xiaomi Pad 5!")
            self.finished_signal.emit(app_id, True, f"Cài đặt thành công: {app_name}")
        else:
            self.progress_signal.emit(app_id, 0, "Cài đặt thất bại ❌")
            self.log_signal.emit("ERROR", f"Cài đặt thất bại {app_name}: {msg}")
            self.finished_signal.emit(app_id, False, msg)


# =========================================================================
# WORKER THREAD: UNINSTALL APP
# =========================================================================
class AppUninstallWorker(QThread):
    log_signal = pyqtSignal(str, str)
    finished_signal = pyqtSignal(str, bool, str)

    def __init__(self, app_info: Dict):
        super().__init__()
        self.app = app_info

    def run(self):
        app_id = self.app["id"]
        app_name = self.app["name"]
        pkg = self.app["package"]

        self.log_signal.emit("INFO", f"Đang gỡ bỏ ứng dụng: {app_name} ({pkg})...")
        ok, msg = adb_uninstall_package(pkg)
        if ok:
            self.log_signal.emit("SUCCESS", f"Đã gỡ cài đặt thành công: {app_name}")
            self.finished_signal.emit(app_id, True, f"Đã gỡ cài đặt {app_name}")
        else:
            self.log_signal.emit("WARNING", f"Gỡ cài đặt {app_name}: {msg}")
            self.finished_signal.emit(app_id, False, msg)


# =========================================================================
# APP ITEM CARD WIDGET
# =========================================================================
class UtilityAppCard(QFrame):
    install_requested = pyqtSignal(dict)
    uninstall_requested = pyqtSignal(dict)

    def __init__(self, app_info: Dict, parent=None):
        super().__init__(parent)
        self.app = app_info
        self.setObjectName("CardFrame")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        # Top Header: Icon + Name + Badges + Status
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Icon box
        lbl_icon = QLabel(self.app["icon"])
        lbl_icon.setStyleSheet("""
            font-size: 24px;
            background-color: #1e293b;
            border-radius: 10px;
            padding: 8px 10px;
            border: 1px solid #334155;
        """)
        top_row.addWidget(lbl_icon)

        # Info Box
        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        lbl_name = QLabel(self.app["name"])
        lbl_name.setStyleSheet("font-size: 15px; font-weight: 700; color: #f8fafc;")
        title_row.addWidget(lbl_name)

        lbl_size = QLabel(f"📦 {self.app['size_str']}")
        lbl_size.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
        title_row.addWidget(lbl_size)

        lbl_badge = QLabel(self.app["badge"])
        lbl_badge.setStyleSheet("""
            background-color: #0369a1;
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
        """)
        title_row.addWidget(lbl_badge)
        title_row.addStretch(1)

        info_layout.addLayout(title_row)

        lbl_pkg = QLabel(f"Package: {self.app['package']} • Danh mục: {self.app['category']}")
        lbl_pkg.setStyleSheet("color: #64748b; font-size: 11px;")
        info_layout.addWidget(lbl_pkg)

        top_row.addLayout(info_layout, stretch=1)

        # Status Badge
        self.lbl_status = QLabel("⚪ Đang kiểm tra...")
        self.lbl_status.setStyleSheet("font-weight: 700; font-size: 12px; color: #94a3b8; padding: 4px 10px;")
        top_row.addWidget(self.lbl_status)

        layout.addLayout(top_row)

        # Description
        lbl_desc = QLabel(self.app["desc"])
        lbl_desc.setStyleSheet("color: #cbd5e1; font-size: 12px; line-height: 1.4;")
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        # Progress bar (Hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 4px;
                height: 16px;
                text-align: center;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #10b981);
            }
        """)
        layout.addWidget(self.progress_bar)

        # Action Buttons Row
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        self.btn_install = QPushButton("⚡ 1-Click Tải & Cài Đặt")
        self.btn_install.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #0ea5e9);
            color: #ffffff;
            font-weight: 700;
            padding: 8px 18px;
            border-radius: 8px;
            border: 1px solid #38bdf8;
            font-size: 13px;
        """)
        self.btn_install.clicked.connect(lambda: self.install_requested.emit(self.app))
        action_row.addWidget(self.btn_install)

        self.btn_reinstall = QPushButton("🔄 Cập Nhật / Cài Lại")
        self.btn_reinstall.setStyleSheet("padding: 8px 14px; font-weight: 600;")
        self.btn_reinstall.setVisible(False)
        self.btn_reinstall.clicked.connect(lambda: self.install_requested.emit(self.app))
        action_row.addWidget(self.btn_reinstall)

        self.btn_uninstall = QPushButton("🗑️ Gỡ Cài Đặt")
        self.btn_uninstall.setObjectName("DangerButton")
        self.btn_uninstall.setVisible(False)
        self.btn_uninstall.clicked.connect(lambda: self.uninstall_requested.emit(self.app))
        action_row.addWidget(self.btn_uninstall)

        action_row.addStretch(1)
        layout.addLayout(action_row)

    def set_installed_state(self, is_installed: bool):
        if is_installed:
            self.lbl_status.setText("✅ ĐÃ CÀI ĐẶT")
            self.lbl_status.setStyleSheet("""
                background-color: #064e3b;
                color: #34d399;
                font-weight: 700;
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 6px;
                border: 1px solid #059669;
            """)
            self.btn_install.setVisible(False)
            self.btn_reinstall.setVisible(True)
            self.btn_uninstall.setVisible(True)
            self.btn_reinstall.setEnabled(True)
            self.btn_uninstall.setEnabled(True)
        else:
            self.lbl_status.setText("⚪ CHƯA CÀI ĐẶT")
            self.lbl_status.setStyleSheet("""
                background-color: #1e293b;
                color: #94a3b8;
                font-weight: 600;
                font-size: 12px;
                padding: 4px 12px;
                border-radius: 6px;
                border: 1px solid #334155;
            """)
            self.btn_install.setVisible(True)
            self.btn_reinstall.setVisible(False)
            self.btn_uninstall.setVisible(False)
            self.btn_install.setEnabled(True)

    def show_progress(self, pct: int, status_text: str):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(status_text)
        self.btn_install.setEnabled(False)
        self.btn_reinstall.setEnabled(False)
        self.btn_uninstall.setEnabled(False)

    def hide_progress(self):
        self.progress_bar.setVisible(False)
        self.btn_install.setEnabled(True)
        self.btn_reinstall.setEnabled(True)
        self.btn_uninstall.setEnabled(True)


# =========================================================================
# MAIN UTILITY APPS TAB
# =========================================================================
class UtilityAppsTab(QWidget):
    """Curated App Store / Utilities Hub for Xiaomi Pad 5."""

    log_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_cards: Dict[str, UtilityAppCard] = {}
        self.installed_packages_cache = set()
        self.active_workers: Dict[str, QThread] = {}

        self._init_ui()

    def _init_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Wrap in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Top Header Card
        header_card = QFrame()
        header_card.setObjectName("CardFrame")
        h_layout = QVBoxLayout(header_card)
        h_layout.setSpacing(10)

        top_info_row = QHBoxLayout()
        lbl_title = QLabel("⭐ KHO ỨNG DỤNG TIỆN ÍCH CHỌN LỌC (XIAOMI PAD 5 UTILITIES)")
        lbl_title.setObjectName("SectionTitle")
        top_info_row.addWidget(lbl_title)

        lbl_guide = QLabel("(Yêu cầu máy ở Android và đã bật USB Debugging)")
        lbl_guide.setStyleSheet("color: #38bdf8; font-size: 12px;")
        top_info_row.addWidget(lbl_guide)
        top_info_row.addStretch(1)

        # Quick Actions in Header
        btn_open_folder = QPushButton("📂 Thư Mục APKs")
        btn_open_folder.setToolTip("Mở thư mục lưu trữ file APK đã tải về trên máy tính")
        btn_open_folder.clicked.connect(self._open_apks_folder)
        top_info_row.addWidget(btn_open_folder)

        btn_refresh_status = QPushButton("🔄 Quét Trạng Thái")
        btn_refresh_status.setToolTip("Quét lại danh sách ứng dụng đã cài trên máy tính bảng")
        btn_refresh_status.clicked.connect(self.refresh_installed_status)
        top_info_row.addWidget(btn_refresh_status)

        h_layout.addLayout(top_info_row)

        desc_lbl = QLabel(
            "Tuyển tập các ứng dụng mã nguồn mở, siêu nhẹ, không quảng cáo được tối ưu hoàn hảo cho màn hình 2.5K 120Hz "
            "và chip Snapdragon 860 của Xiaomi Pad 5. Bạn có thể cài đặt hoặc gỡ bỏ dễ dàng chỉ với 1 click!"
        )
        desc_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        h_layout.addWidget(desc_lbl)

        # Filter & Search Row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        self.cmb_category = QComboBox()
        self.cmb_category.addItems([
            "⭐ Tất cả danh mục",
            "⚡ Giám Sát Phần Cứng",
            "🛠️ Công Cụ Hệ Thống",
            "🎬 Giải Trí & Xem Phim",
            "🛒 Cửa Hàng Ứng Dụng",
            "📖 Đọc Sách & Học Tập",
            "⚡ Tải File & Công Cụ"
        ])
        self.cmb_category.currentIndexChanged.connect(self._apply_filter)
        filter_row.addWidget(self.cmb_category)

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 Tìm theo tên ứng dụng hoặc tính năng (vd: nhiệt độ, youtube, vlc, pdf)...")
        self.txt_search.textChanged.connect(self._apply_filter)
        filter_row.addWidget(self.txt_search, stretch=1)

        h_layout.addLayout(filter_row)
        main_layout.addWidget(header_card)

        # 2. App Cards Container
        self.cards_layout = QVBoxLayout()
        self.cards_layout.setSpacing(12)

        for app_info in UTILITY_APPS_CATALOG:
            card = UtilityAppCard(app_info)
            card.install_requested.connect(self._on_install_requested)
            card.uninstall_requested.connect(self._on_uninstall_requested)
            self.app_cards[app_info["id"]] = card
            self.cards_layout.addWidget(card)

        main_layout.addLayout(self.cards_layout)
        main_layout.addStretch(1)

        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

    # -------------------------------------------------------------
    # LOGIC: STATUS CHECKING
    # -------------------------------------------------------------
    def refresh_installed_status(self):
        """Query installed packages from device via ADB and update cards."""
        self.log_requested.emit("INFO", "Đang quét danh sách ứng dụng đã cài đặt trên Xiaomi Pad 5...")
        packages = adb_list_packages("all")
        self.installed_packages_cache = set(packages)

        installed_count = 0
        for app_info in UTILITY_APPS_CATALOG:
            app_id = app_info["id"]
            pkg = app_info["package"]
            card = self.app_cards.get(app_id)
            if card:
                is_inst = (pkg in self.installed_packages_cache)
                card.set_installed_state(is_inst)
                if is_inst:
                    installed_count += 1

        self.log_requested.emit("SUCCESS", f"Đã quét xong: Đã cài đặt {installed_count}/{len(UTILITY_APPS_CATALOG)} ứng dụng tiện ích.")

    def _apply_filter(self):
        cat = self.cmb_category.currentText()
        query = self.txt_search.text().strip().lower()

        for app_info in UTILITY_APPS_CATALOG:
            app_id = app_info["id"]
            card = self.app_cards.get(app_id)
            if not card:
                continue

            match_cat = (cat == "⭐ Tất cả danh mục") or (cat == app_info["category"])
            match_query = (query in app_info["name"].lower()) or (query in app_info["desc"].lower()) or (query in app_info["package"].lower())

            card.setVisible(match_cat and match_query)

    def _open_apks_folder(self):
        os.makedirs(APKS_DIR, exist_ok=True)
        try:
            os.startfile(APKS_DIR)
            self.log_requested.emit("INFO", f"Đã mở thư mục APK: {APKS_DIR}")
        except Exception as e:
            self.log_requested.emit("ERROR", f"Không thể mở thư mục: {e}")

    # -------------------------------------------------------------
    # LOGIC: INSTALL / UNINSTALL ACTIONS
    # -------------------------------------------------------------
    def _on_install_requested(self, app_info: Dict):
        app_id = app_info["id"]
        card = self.app_cards.get(app_id)
        if card:
            card.show_progress(10, "Chuẩn bị tải...")

        worker = AppInstallWorker(app_info)
        worker.progress_signal.connect(self._on_worker_progress)
        worker.log_signal.connect(self.log_requested.emit)
        worker.finished_signal.connect(self._on_install_finished)
        self.active_workers[app_id] = worker
        worker.start()

    def _on_worker_progress(self, app_id: str, pct: int, status_text: str):
        card = self.app_cards.get(app_id)
        if card:
            card.show_progress(pct, status_text)

    def _on_install_finished(self, app_id: str, success: bool, message: str):
        card = self.app_cards.get(app_id)
        if card:
            card.hide_progress()

        if app_id in self.active_workers:
            del self.active_workers[app_id]

        if success:
            QMessageBox.information(self, "Cài Đặt Thành Công", f"{message}\n\nỨng dụng đã xuất hiện trên màn hình máy tính bảng!")
            self.refresh_installed_status()
        else:
            QMessageBox.critical(self, "Cài Đặt Thất Bại", f"Không thể cài đặt:\n{message}\n\nVui lòng kiểm tra cáp kết nối và bật USB Debugging.")

    def _on_uninstall_requested(self, app_info: Dict):
        app_name = app_info["name"]
        reply = QMessageBox.question(
            self,
            "Xác nhận gỡ cài đặt",
            f"Bạn có chắc chắn muốn gỡ bỏ ứng dụng {app_name} khỏi Xiaomi Pad 5?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        app_id = app_info["id"]
        worker = AppUninstallWorker(app_info)
        worker.log_signal.connect(self.log_requested.emit)
        worker.finished_signal.connect(self._on_uninstall_finished)
        self.active_workers[app_id] = worker
        worker.start()

    def _on_uninstall_finished(self, app_id: str, success: bool, message: str):
        if app_id in self.active_workers:
            del self.active_workers[app_id]

        if success:
            QMessageBox.information(self, "Gỡ Cài Đặt", f"{message} thành công!")
            self.refresh_installed_status()
        else:
            QMessageBox.critical(self, "Lỗi Gỡ Cài Đặt", f"Thất bại: {message}")
