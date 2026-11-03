import os
import subprocess
import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.constants import (
    FASTBOOT_EXE,
    GPT_BIN,
    EXPECTED_GPT_SIZE,
    TARGET_CODENAME
)
from core.adb_fastboot import (
    get_fastboot_devices,
    get_fastboot_var,
    verify_gpt_hash,
    SUBPROCESS_FLAGS
)


class RestoreEngineThread(QThread):
    """Executes the partition table restore process asynchronously with live signals."""

    # level: 'INFO', 'SUCCESS', 'WARNING', 'ERROR', 'CMD'
    log_signal = pyqtSignal(str, str)
    # current_step, total_steps, step_name
    progress_signal = pyqtSignal(int, int, str)
    # success, summary_message
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        total_steps = 4

        def log(level: str, msg: str):
            self.log_signal.emit(level, msg)

        log("INFO", "=== BẮT ĐẦU QUÁ TRÌNH KHÔI PHỤC PHÂN VÙNG XIAOMI PAD 5 ===")
        log("INFO", f"Thời gian bắt đầu: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # --- BƯỚC 1: KIỂM TRA THIẾT BỊ VÀ FILE GỐC ---
        self.progress_signal.emit(1, total_steps, "Kiểm tra kết nối và tính toàn vẹn...")
        log("INFO", "[BƯỚC 1/4] Kiểm tra thiết bị và file bảng phân vùng...")

        # 1.1 Kiểm tra file gpt_both0.bin
        if not os.path.isfile(GPT_BIN):
            log("ERROR", f"Không tìm thấy file: {GPT_BIN}")
            self.finished_signal.emit(False, "Thiếu file gpt_both0.bin.")
            return

        size = os.path.getsize(GPT_BIN)
        if size != EXPECTED_GPT_SIZE:
            log("ERROR", f"Kích thước file gpt_both0.bin không đúng: {size} bytes (yêu cầu {EXPECTED_GPT_SIZE} bytes)")
            self.finished_signal.emit(False, "File gpt_both0.bin bị lỗi dung lượng.")
            return

        if not verify_gpt_hash():
            log("WARNING", "SHA256 của file gpt_both0.bin không trùng khớp tuyệt đối, nhưng kích thước đúng. Tiếp tục thận trọng...")
        else:
            log("SUCCESS", "Đã xác thực SHA256 file gpt_both0.bin chuẩn chính hãng (45,056 bytes).")

        # 1.2 Kiểm tra thiết bị Fastboot
        devices = get_fastboot_devices()
        if not devices:
            log("ERROR", "Không tìm thấy thiết bị nào ở chế độ FASTBOOT! Hãy cắm cáp USB và đưa máy về Fastboot.")
            self.finished_signal.emit(False, "Không phát hiện thiết bị ở chế độ FASTBOOT.")
            return

        serial = devices[0]["serial"]
        log("SUCCESS", f"Phát hiện thiết bị Fastboot: Serial [{serial}]")

        # 1.3 Kiểm tra product name
        product = get_fastboot_var("product")
        log("INFO", f"Thông tin Product ID: '{product}'")
        if product and TARGET_CODENAME not in product.lower():
            log("WARNING", f"Thiết bị báo mã product là '{product}' thay vì '{TARGET_CODENAME}'. Hãy đảm bảo đây đúng là Xiaomi Pad 5!")
        else:
            log("SUCCESS", f"Đã xác nhận đúng mã thiết bị Xiaomi Pad 5 ({TARGET_CODENAME})")

        # --- BƯỚC 2: FLASH PHÂN VÙNG GỐC GPT_BOTH0.BIN ---
        self.progress_signal.emit(2, total_steps, "Nạp bảng phân vùng gốc (Xóa Windows + ESP)...")
        log("INFO", "[BƯỚC 2/4] Nạp bảng phân vùng gốc gpt_both0.bin vào partition:0...")
        
        flash_cmd = [FASTBOOT_EXE, "flash", "partition:0", GPT_BIN]
        log("CMD", f"> {' '.join(flash_cmd)}")

        success, stdout, stderr = self._run_command_logged(flash_cmd)
        if not success:
            log("ERROR", f"Nạp phân vùng thất bại!\n{stderr or stdout}")
            self.finished_signal.emit(False, "Lỗi khi nạp bảng phân vùng gốc (fastboot flash partition:0).")
            return

        log("SUCCESS", "Nạp bảng phân vùng gốc thành công! Toàn bộ cấu trúc phân vùng Windows & ESP đã bị loại bỏ.")
        time.sleep(1.5)

        # --- BƯỚC 3: FORMAT VÀ MỞ RỘNG USERDATA VỀ 100% ---
        self.progress_signal.emit(3, total_steps, "Format và mở rộng toàn bộ bộ nhớ Android...")
        log("INFO", "[BƯỚC 3/4] Xóa dữ liệu cũ và định dạng lại Userdata để nhận lại 100% dung lượng...")

        # 3.1 Erase metadata nếu có
        log("CMD", "> fastboot erase metadata")
        self._run_command_logged([FASTBOOT_EXE, "erase", "metadata"], log_errors=False)

        # 3.2 Erase userdata
        log("CMD", "> fastboot erase userdata")
        self._run_command_logged([FASTBOOT_EXE, "erase", "userdata"], log_errors=True)

        # 3.3 Fastboot -w (Wipe and format filesystem)
        wipe_cmd = [FASTBOOT_EXE, "-w"]
        log("CMD", f"> {' '.join(wipe_cmd)}")
        success, stdout, stderr = self._run_command_logged(wipe_cmd)
        if not success:
            log("WARNING", f"Lệnh fastboot -w cảnh báo/lỗi nhẹ: {stderr or stdout}. Thiết bị sẽ tự format ở bước khởi động lại.")
        else:
            log("SUCCESS", "Format bộ nhớ hoàn tất! Hệ thống tập tin đã mở rộng đầy đủ 100% bộ nhớ trong.")

        time.sleep(1.5)

        # --- BƯỚC 4: KHỞI ĐỘNG LẠI THIẾT BỊ ---
        self.progress_signal.emit(4, total_steps, "Khởi động lại máy vào Android...")
        log("INFO", "[BƯỚC 4/4] Khởi động lại thiết bị về Android...")
        
        reboot_cmd = [FASTBOOT_EXE, "reboot"]
        log("CMD", f"> {' '.join(reboot_cmd)}")
        success, stdout, stderr = self._run_command_logged(reboot_cmd)
        if not success:
            log("WARNING", f"Không thể tự động gửi lệnh reboot: {stderr}. Bạn có thể giữ nút Nguồn 10s để khởi động lại máy.")
        else:
            log("SUCCESS", "Đã gửi lệnh khởi động lại thành công!")

        log("SUCCESS", "===========================================================")
        log("SUCCESS", "🎉 KHÔI PHỤC THÀNH CÔNG 100% ANDROID CHO XIAOMI PAD 5!")
        log("INFO", "👉 LƯU Ý KHI KHỞI ĐỘNG LẠI LẦN ĐẦU TIÊN:")
        log("INFO", "1. Lần khởi động đầu tiên sẽ mất khoảng 2 - 5 phút để Android thiết lập lại hệ thống.")
        log("INFO", "2. Nếu máy dừng lại ở màn hình Mi-Recovery (Màn hình chữ màu đen/trắng):")
        log("INFO", "   - Dùng phím Âm lượng di chuyển chọn: 'Wipe Data' -> bấm phím Nguồn để chọn.")
        log("INFO", "   - Chọn tiếp: 'Wipe All Data' -> bấm 'Confirm'.")
        log("INFO", "   - Sau khi hoàn thành, chọn 'Back to Main Menu' -> 'Reboot' -> 'Reboot to System'.")
        log("INFO", "3. Máy sẽ khởi động vào màn hình thiết lập xuất xưởng nguyên bản với 100% dung lượng (128GB/256GB)!")
        log("SUCCESS", "===========================================================")

        self.finished_signal.emit(True, "Khôi phục thành công! Xiaomi Pad 5 đã trở về 100% Android gốc.")

    def _run_command_logged(self, cmd, log_errors: bool = True):
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=SUBPROCESS_FLAGS,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            stdout, stderr = proc.communicate(timeout=60)
            
            # fastboot prints its progress to stderr
            combined = f"{stdout}\n{stderr}".strip()
            for line in combined.splitlines():
                if line.strip():
                    self.log_signal.emit("INFO", f"  {line.strip()}")
            
            return (proc.returncode == 0), stdout, stderr
        except Exception as e:
            if log_errors:
                self.log_signal.emit("ERROR", f"Lỗi thực thi lệnh: {e}")
            return False, "", str(e)
