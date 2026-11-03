from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser


class GuideTab(QWidget):
    """Tab displaying step-by-step instructions, safety tips, and recovery guides."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
                padding: 16px;
                color: #e2e8f0;
                font-size: 13px;
                line-height: 1.6;
            }
        """)

        html_content = """
        <h2 style="color: #38bdf8; margin-top:0;">📖 HƯỚNG DẪN KHÔI PHỤC XIAOMI PAD 5 (NABU) VỀ ANDROID GỐC</h2>
        
        <p>Ứng dụng này được thiết kế để tự động hóa 100% quy trình gỡ bỏ Windows 11 và khôi phục lại bảng phân vùng Android nguyên bản theo chuẩn khuyến nghị từ dự án <b>Port-Windows-11-Xiaomi-Pad-5 (erdilS)</b>.</p>
        
        <hr style="border: 0; height: 1px; background: #334155; margin: 16px 0;">

        <h3 style="color: #f59e0b;">⚠️ 1. CÁC ĐIỀU KIỆN CẦN CHUẨN BỊ</h3>
        <ul>
            <li><b>Mức Pin:</b> Đảm bảo pin máy tính bảng còn trên <b>30%</b> để tránh bị sập nguồn giữa chừng.</li>
            <li><b>Dữ Liệu:</b> Quá trình khôi phục bảng phân vùng sẽ <b>XÓA TOÀN BỘ DỮ LIỆU</b> của cả Windows 11 và Android (userdata sẽ được format lại hoàn toàn để mở rộng 100% bộ nhớ). Vui lòng sao lưu dữ liệu quan trọng trước khi bấm khôi phục.</li>
            <li><b>Trạng Thái Hiện Tại:</b> Đảm bảo bạn đang ở Android (hoặc có thể vào Fastboot bình thường).</li>
        </ul>

        <h3 style="color: #34d399;">🚀 2. QUY TRÌNH THỰC HIỆN 1-CLICK</h3>
        <ol>
            <li>Kết nối Xiaomi Pad 5 với máy tính qua cáp USB Type-C.</li>
            <li>Nếu máy đang bật trong Android, ứng dụng sẽ hiện trạng thái <b>ADB Online</b>. Bạn chỉ cần nhấn nút <b>"Chuyển sang FASTBOOT"</b>.</li>
            <li>Khi thiết bị đã ở màn hình FASTBOOT (chữ FASTBOOT màu cam):
                <ul>
                    <li>Tích chọn vào ô: <i>"Tôi hiểu rằng thao tác này sẽ xóa sạch dữ liệu..."</i></li>
                    <li>Bấm nút lớn: <b>"🚀 BẮT ĐẦU KHÔI PHỤC VỀ ANDROID GỐC"</b>.</li>
                </ul>
            </li>
            <li>Ứng dụng sẽ tự động:
                <ul>
                    <li>Nạp lại bảng phân vùng gốc <code>gpt_both0.bin</code> (xóa sạch phân vùng <code>win</code> và <code>esp</code>).</li>
                    <li>Format mở rộng phân vùng <code>userdata</code> về 100% dung lượng gốc (128GB hoặc 256GB).</li>
                    <li>Tự động khởi động lại thiết bị về Android.</li>
                </ul>
            </li>
        </ol>

        <h3 style="color: #a78bfa;">📱 3. LƯU Ý KHI KHỞI ĐỘNG LẠI LẦN ĐẦU TIÊN</h3>
        <ul>
            <li>Lần khởi động đầu tiên sẽ mất khoảng <b>2 đến 5 phút</b> để Android khởi tạo lại bộ nhớ.</li>
            <li><b>Nếu máy khởi động vào màn hình Mi-Recovery (Recovery gốc Xiaomi):</b>
                <br>Đây là phản ứng hoàn toàn bình thường khi phân vùng vừa được format lại. Hãy thao tác:
                <ol>
                    <li>Dùng phím <b>Giảm âm lượng</b> di chuyển xuống mục <b>Wipe Data</b> -> bấm phím <b>Nguồn</b>.</li>
                    <li>Chọn tiếp <b>Wipe All Data</b> -> bấm <b>Confirm</b>.</li>
                    <li>Đợi format xong, chọn <b>Back to Main Menu</b> -> chọn <b>Reboot</b> -> chọn <b>Reboot to System</b>.</li>
                </ol>
            </li>
            <li>Máy sẽ khởi động vào màn hình thiết lập xuất xưởng nguyên bản với trọn vẹn 100% dung lượng bộ nhớ trong!</li>
        </ul>

        <h3 style="color: #38bdf8;">🔧 4. KHẮC PHỤC LỖI DRIVER FASTBOOT TRÊN WINDOWS</h3>
        <p>Nếu bạn đã đưa máy về FASTBOOT nhưng phần mềm báo <i>"Chưa phát hiện thiết bị"</i>:</p>
        <ol>
            <li>Chuyển sang tab <b>"Công Cụ Nâng Cao"</b> -> bấm nút <b>"Mở Device Manager"</b>.</li>
            <li>Tìm mục có dấu chấm than vàng (thường có tên <i>Android</i> hoặc <i>Android Bootloader</i>).</li>
            <li>Chuột phải vào đó -> <b>Update driver</b> -> <b>Browse my computer for drivers</b> -> <b>Let me pick from a list of available drivers on my computer</b>.</li>
            <li>Chọn <b>Android Device</b> (hoặc Android Phone) -> chọn model <b>Android Bootloader Interface</b> -> bấm Next để cài đặt.</li>
            <li>Quay lại phần mềm và bấm nút <b>"Làm mới"</b>, thiết bị sẽ hiện ngay lập tức!</li>
        </ol>

        <hr style="border: 0; height: 1px; background: #334155; margin: 20px 0;">
        <p style="text-align: center; color: #94a3b8; font-size: 12px; margin: 0;">
            🚀 <b>Xiaomi Pad 5 Android Restore Tool Pro</b> • Phát triển bởi <b>ITK</b> (Created by <b>ITK</b>)
        </p>
        """

        browser.setHtml(html_content)
        layout.addWidget(browser)
