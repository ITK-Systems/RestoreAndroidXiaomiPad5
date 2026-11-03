# RestoreAndroidXiaomiPad5
Khôi phục máy tính bản cài song song windows và android về măc đinh android
# 📱 Xiaomi Pad 5 (nabu) - Android Restore Tool Pro

Ứng dụng giao diện đồ họa (GUI) chuyên dụng trên máy tính Windows, giúp tự động hóa 100% quy trình **gỡ bỏ hoàn toàn Windows 11 & phân vùng khởi động ESP**, khôi phục bảng phân vùng chuẩn gốc (Qualcomm LUN0 GPT) và mở rộng phân vùng `userdata` về **100% dung lượng Android nguyên bản** (128GB hoặc 256GB).

Được xây dựng dựa trên hướng dẫn chính thức từ dự án **[erdilS/Port-Windows-11-Xiaomi-Pad-5](https://github.com/erdilS/Port-Windows-11-Xiaomi-Pad-5)**.

👉 **[Xem Cẩm Nang Hướng Dẫn Sử Dụng & Tối Ưu Chi Tiết Tại Đây (USER_GUIDE.md)](USER_GUIDE.md)**

---

## 🌟 Tính Năng Nổi Bật

- **Giao diện Modern Dark Mode (PyQt6)**: Trực quan, chuyên nghiệp, hỗ trợ tiếng Việt đầy đủ.
- **Tự động nhận diện thiết bị thời gian thực (Real-time Live Monitor)**:
  - Tự động quét và phát hiện trạng thái kết nối cáp USB (ADB Online, Fastboot, Chưa cấp quyền).
  - Nút chuyển nhanh từ **Android sang FASTBOOT** chỉ với 1 click (không cần gõ lệnh dòng lệnh).
- **Khôi phục 1-Click an toàn tuyệt đối**:
  - Tự động nạp bảng phân vùng gốc chuẩn chính hãng `gpt_both0.bin` (Qualcomm LUN0 GPT).
  - Tự động xóa sạch phân vùng `win` và `esp`.
  - Format mở rộng lại `userdata` (`fastboot -w`) để Android nhận lại trọn vẹn dung lượng bộ nhớ ban đầu.
  - Tự động khởi động lại thiết bị về Android.
- **Tích hợp sẵn mọi công cụ (Self-Contained Portable)**:
  - Đã tích hợp sẵn Google Platform-Tools (`adb.exe`, `fastboot.exe`, DLLs).
  - Đã tích hợp sẵn file phân vùng gốc chính hãng `gpt_both0.bin` (45,056 bytes, đã kiểm tra mã SHA256).
- **Hộp nhật ký thao tác trực tiếp (Real-time Terminal Console)**:
  - Hiển thị từng dòng lệnh, kết quả thực thi theo màu sắc rõ ràng (Thành công, Cảnh báo, Lỗi).
  - Hỗ trợ nút sao chép log nhanh chóng.
- **Bộ công cụ nâng cao (Advanced Tools)**:
  - Quản lý phân vùng khởi động A/B: Kiểm tra và chuyển đổi Slot A (Android) / Slot B (Windows/UEFI).
  - Tùy chọn khởi động lại: Vào System, vào Recovery, vào Fastboot, vào chế độ EDL (9008).
  - Kiểm tra toàn bộ thông số phần cứng thiết bị (`fastboot getvar all`).
  - Phím tắt mở nhanh Device Manager (`devmgmt.msc`) để hỗ trợ cập nhật Driver Fastboot.
  - Công cụ nạp Boot Image (`boot.img`) tùy chọn nếu cần khôi phục kernel gốc.
- **Kho Tiện Ích Chọn Lọc Cho Xiaomi Pad 5 (Utilities App Store)**:
  - Tuyển tập các ứng dụng mã nguồn mở, siêu nhẹ, không quảng cáo tối ưu cho màn hình 2.5K 120Hz và chip Snapdragon 860:
    - **CPU Info (2.8 MB)**: Giám sát phần cứng, nhiệt độ CPU Snapdragon 860, RAM, pin thời gian thực.
    - **Shizuku (2.5 MB)**: Cấp quyền quản trị ADB độc lập ngay trên máy tính bảng mà không cần cắm lại PC.
    - **NewPipe (11.5 MB)**: Xem YouTube chặn 100% quảng cáo, nghe nhạc tắt màn hình, tải video Full HD.
    - **Aurora Store (8.5 MB)**: Tải app Google Play Store không cần đăng nhập tài khoản.
    - **F-Droid (12.5 MB)**: Kho ứng dụng mã nguồn mở miễn phí lớn nhất thế giới Android.
    - **VLC Media Player (35 MB)**: Trình xem phim đa định dạng 4K HDR, phụ đề tiếng Việt.
    - **KOReader (29 MB)**: Trình đọc sách EPUB, PDF chuyên sâu, tối ưu phông chữ sắc nét.
    - **Mihon (27.7 MB)**: Đọc truyện tranh manga hàng đầu thế giới (kế thừa Tachiyomi).
    - **LibreTorrent (23 MB)**: Tải file và phim torrent tốc độ cao, sạch 100%.
  - Tự động nhận diện trạng thái `Đã Cài Đặt` / `Chưa Cài Đặt` theo thời gian thực.
  - Hỗ trợ **1-Click Tải & Cài Đặt** và **1-Click Gỡ Bỏ** cực kỳ nhanh gọn.
- **Quản lý & Cài đặt Ứng Dụng (App Manager & ADB Debloater)**:
  - **Dọn dẹp Bloatware 1-Click**: Tự động nhận diện và gỡ bỏ an toàn các ứng dụng rác, quảng cáo, theo dõi ngầm của Xiaomi/MIUI/HyperOS (Analytics, MSA, GetApps, Joyose, Mi Browser, Facebook Services...).
  - **Quản lý Package linh hoạt**: Lọc ứng dụng hệ thống, ứng dụng người dùng, tìm kiếm theo tên gói, gỡ bỏ (Uninstall user 0), vô hiệu hóa (Disable) và bật lại (Enable).
  - **Cài đặt hàng loạt APK qua ADB**: Chọn nhiều file APK cùng lúc, tùy chọn tự động cấp quyền (`-g`), cài đè (`-r`), hạ cấp (`-d`) và theo dõi tiến trình trực quan.
- **Tinh chỉnh Màn hình & Tần số quét 120Hz (Display & DPI Tweaker)**:
  - **Chuyển đổi Mật độ DPI**: Tùy chỉnh nhanh chế độ Laptop / Desktop (240 DPI), Đa nhiệm ghi chú (280 DPI), Mặc định gốc (320 DPI), Chữ to (360 DPI) hoặc nhập DPI tùy ý.
  - **Khóa Tần số quét 120Hz**: Ép máy chạy 120Hz mọi lúc, chống tình trạng hệ điều hành tự tụt xuống 60Hz khi xem YouTube/Web. Tùy chọn 90Hz, 60Hz và Dynamic thích ứng.
  - **Tối ưu tốc độ hiệu ứng (Animation Scale)**: Đặt 0.5x hoặc 0x để tối đa hóa độ mượt mà và tốc độ phản hồi trên màn hình 120Hz.

---

## 📋 Điều Kiện Chuẩn Bị

1. **Mức pin máy tính bảng**: Đảm bảo pin trên **30%** trước khi thao tác.
2. **Cáp kết nối**: Sử dụng cáp USB Type-C tốt kết nối trực tiếp với cổng USB trên máy tính (hạn chế dùng qua cổng chuyển đổi HUB nếu chập chờn).
3. **Sao lưu dữ liệu**: Quá trình khôi phục phân vùng sẽ **xóa sạch toàn bộ dữ liệu** của cả Windows 11 và Android để định dạng lại hệ thống tập tin toàn bộ bộ nhớ. Hãy sao lưu các file cần thiết trước khi bắt đầu.
4. **Hệ điều hành máy tính**: Windows 10 hoặc Windows 11 đã cài sẵn Python (máy tính hiện tại đã có sẵn Python 3.10 và PyQt6).

---

## 🚀 Hướng Dẫn Sử Dụng

### Bước 1: Khởi Chạy Ứng Dụng
- Nhấp đúp chuột vào file **`run.bat`** trong thư mục `RestoreMiPad5`.
- Hoặc mở PowerShell / CMD tại thư mục và chạy:
  ```powershell
  python app.py
  ```

### Bước 2: Kết Nối Thiết Bị
- Cắm cáp kết nối Xiaomi Pad 5 với máy tính.
- **Nếu máy đang mở trong Android**:
  - Phần mềm sẽ hiển thị trạng thái `ĐÃ KẾT NỐI ANDROID (ADB Online)`.
  - Bấm nút **⚡ Chuyển sang FASTBOOT** trên giao diện. Máy tính bảng sẽ tự khởi động lại vào màn hình Fastboot (chữ FASTBOOT màu cam).
- **Nếu máy đang tắt nguồn**:
  - Giữ đồng thời nút **Giảm Âm Lượng + Nguồn** khoảng 5 giây cho đến khi hiện màn hình FASTBOOT, sau đó cắm cáp USB vào máy tính.

### Bước 3: Bắt Đầu Khôi Phục
- Khi giao diện hiện trạng thái màu xanh lá: **`ĐÃ KẾT NỐI CHẾ ĐỘ FASTBOOT (nabu)`**.
- Tích chọn vào ô: *"Tôi hiểu rằng thao tác này sẽ xóa sạch dữ liệu..."*
- Nhấn nút lớn: **🚀 BẮT ĐẦU KHÔI PHỤC VỀ ANDROID GỐC (1-CLICK RESTORE)**.
- Xác nhận hộp thoại cảnh báo hiện ra.
- Phần mềm sẽ tự động thực thi các bước nạp bảng phân vùng, format bộ nhớ và khởi động lại máy.

---

## 📱 Lưu Ý Sau Khi Khởi Động Lại

1. **Thời gian khởi động lần đầu**: Thường kéo dài từ **2 đến 5 phút** do hệ điều hành Android cần khởi tạo lại cấu trúc bộ nhớ mới.
2. **Nếu máy khởi động vào màn hình Mi-Recovery (Recovery mặc định của Xiaomi)**:
   Đây là điều bình thường khi phân vùng vừa được mở rộng lại. Hãy thao tác bằng phím cứng:
   - Dùng phím **Giảm âm lượng** di chuyển xuống chọn: **`Wipe Data`** -> bấm phím **Nguồn** để chọn.
   - Chọn tiếp: **`Wipe All Data`** -> bấm **`Confirm`**.
   - Sau khi hoàn tất, chọn **`Back to Main Menu`** -> chọn **`Reboot`** -> chọn **`Reboot to System`**.
3. **Kết quả**: Thiết bị sẽ khởi động vào màn hình thiết lập ban đầu (MIUI / HyperOS Setup Wizard) với **100% dung lượng gốc** (128GB hoặc 256GB), phân vùng Windows 11 và ESP đã bị loại bỏ hoàn toàn sạch sẽ!

---

## 🔧 Khắc Phục Lỗi Driver Fastboot Trên Windows

Nếu bạn đã đưa máy về màn hình FASTBOOT nhưng ứng dụng vẫn báo *`Chưa phát hiện thiết bị`*:
1. Chuyển sang tab **"⚙️ Tiện Ích Nâng Cao"** trên ứng dụng -> bấm nút **"Mở Device Manager"**.
2. Tìm trong danh sách thiết bị mục có tên `Android` (thường có dấu chấm than màu vàng).
3. Chuột phải vào đó -> chọn **Update driver** -> **Browse my computer for drivers** -> **Let me pick from a list of available drivers on my computer**.
4. Chọn danh mục **Android Device** (hoặc Android Phone) -> ở danh sách bên phải chọn model **Android Bootloader Interface** -> bấm **Next** để hoàn tất.
5. Quay lại ứng dụng và bấm nút **🔄 Làm mới**, thiết bị sẽ được nhận diện ngay lập tức.
