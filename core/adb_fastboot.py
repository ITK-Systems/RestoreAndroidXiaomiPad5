import os
import subprocess
import hashlib
from typing import Tuple, List, Dict, Optional
from core.constants import ADB_EXE, FASTBOOT_EXE, GPT_BIN, EXPECTED_GPT_SIZE, EXPECTED_GPT_SHA256

# Suppress console window on Windows
SUBPROCESS_FLAGS = 0
if os.name == "nt":
    SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW


def run_command(cmd: List[str], timeout: Optional[int] = 30) -> Tuple[int, str, str]:
    """Execute command quietly without popping up command window."""
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
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout.strip(), stderr.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return -1, "", "Command timed out."
    except Exception as e:
        return -1, "", str(e)


def check_tools_installed() -> Tuple[bool, str]:
    """Check if adb.exe, fastboot.exe and gpt_both0.bin are ready."""
    if not os.path.isfile(ADB_EXE):
        return False, f"Không tìm thấy adb.exe tại: {ADB_EXE}"
    if not os.path.isfile(FASTBOOT_EXE):
        return False, f"Không tìm thấy fastboot.exe tại: {FASTBOOT_EXE}"
    if not os.path.isfile(GPT_BIN):
        return False, f"Không tìm thấy gpt_both0.bin tại: {GPT_BIN}"
    
    # Check GPT size
    size = os.path.getsize(GPT_BIN)
    if size != EXPECTED_GPT_SIZE:
        return False, f"File gpt_both0.bin có dung lượng không hợp lệ ({size} bytes, chuẩn là {EXPECTED_GPT_SIZE} bytes)."
    
    return True, "Đầy đủ công cụ và file phân vùng."


def verify_gpt_hash() -> bool:
    """Verify SHA256 of gpt_both0.bin."""
    if not os.path.isfile(GPT_BIN):
        return False
    try:
        hasher = hashlib.sha256()
        with open(GPT_BIN, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest().lower() == EXPECTED_GPT_SHA256.lower()
    except Exception:
        return False


def get_adb_devices() -> List[Dict[str, str]]:
    """Return list of connected ADB devices: [{'serial': ..., 'state': ...}]."""
    if not os.path.isfile(ADB_EXE):
        return []
    code, stdout, _ = run_command([ADB_EXE, "devices"])
    if code != 0:
        return []
    
    devices = []
    lines = stdout.splitlines()
    for line in lines[1:]:  # skip 'List of devices attached'
        parts = line.strip().split()
        if len(parts) >= 2:
            devices.append({"serial": parts[0], "state": parts[1]})
    return devices


def get_fastboot_devices() -> List[Dict[str, str]]:
    """Return list of connected Fastboot devices: [{'serial': ..., 'state': 'fastboot'}]."""
    if not os.path.isfile(FASTBOOT_EXE):
        return []
    code, stdout, _ = run_command([FASTBOOT_EXE, "devices"])
    if code != 0:
        return []
    
    devices = []
    lines = stdout.splitlines()
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 2 and parts[1] == "fastboot":
            devices.append({"serial": parts[0], "state": "fastboot"})
    return devices


def get_fastboot_var(var_name: str) -> Optional[str]:
    """Query a variable from fastboot (e.g. product, unlocked, is-userspace)."""
    if not os.path.isfile(FASTBOOT_EXE):
        return None
    code, stdout, stderr = run_command([FASTBOOT_EXE, "getvar", var_name], timeout=5)
    # fastboot outputs getvar to stderr on many versions
    combined = f"{stdout}\n{stderr}"
    for line in combined.splitlines():
        if f"{var_name}:" in line:
            return line.split(f"{var_name}:")[-1].strip()
    return None


def get_all_fastboot_vars() -> str:
    """Get all fastboot variables."""
    if not os.path.isfile(FASTBOOT_EXE):
        return "fastboot.exe không tồn tại."
    _, stdout, stderr = run_command([FASTBOOT_EXE, "getvar", "all"], timeout=10)
    return stdout if stdout else stderr


def adb_reboot_bootloader() -> Tuple[bool, str]:
    """Reboot from Android (ADB) to Fastboot."""
    code, stdout, stderr = run_command([ADB_EXE, "reboot", "bootloader"], timeout=15)
    if code == 0:
        return True, "Đã gửi lệnh chuyển sang chế độ FASTBOOT thành công."
    return False, stderr or stdout or "Lỗi khi chuyển sang Fastboot."


def adb_reboot_system() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([ADB_EXE, "reboot"], timeout=10)
    return code == 0, stderr or stdout or "Reboot system OK"


def adb_reboot_recovery() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([ADB_EXE, "reboot", "recovery"], timeout=10)
    return code == 0, stderr or stdout or "Reboot recovery OK"


def fastboot_reboot() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([FASTBOOT_EXE, "reboot"], timeout=10)
    return code == 0, stderr or stdout or "Reboot OK"


def fastboot_reboot_recovery() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([FASTBOOT_EXE, "reboot", "recovery"], timeout=10)
    return code == 0, stderr or stdout or "Reboot recovery OK"


def fastboot_reboot_bootloader() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([FASTBOOT_EXE, "reboot", "bootloader"], timeout=10)
    return code == 0, stderr or stdout or "Reboot bootloader OK"


def fastboot_reboot_edl() -> Tuple[bool, str]:
    code, stdout, stderr = run_command([FASTBOOT_EXE, "oem", "edl"], timeout=10)
    return code == 0, stderr or stdout or "Reboot EDL OK"


def fastboot_get_current_slot() -> str:
    """Get active slot ('a' or 'b')."""
    return get_fastboot_var("current-slot")


def fastboot_set_slot(slot: str) -> Tuple[bool, str]:
    """Change active slot ('a' or 'b')."""
    code, stdout, stderr = run_command([FASTBOOT_EXE, "set_active", slot], timeout=10)
    if code == 0:
        return True, f"Đã chuyển phân vùng hoạt động sang Slot {slot.upper()} thành công."
    return False, stderr or stdout or f"Lỗi khi chuyển sang Slot {slot.upper()}."


# =========================================================================
# APP MANAGEMENT & DEBLOATER FUNCTIONS (ADB)
# =========================================================================

XIAOMI_BLOATWARE_PRESET = {
    "com.miui.analytics": "Xiaomi Analytics (Thu thập dữ liệu ngầm & phân tích)",
    "com.miui.msa.global": "MIUI System Ads (Quảng cáo hệ thống Xiaomi)",
    "com.xiaomi.mipicks": "GetApps (Kho ứng dụng rác Xiaomi)",
    "com.mi.globalbrowser": "Mi Browser (Trình duyệt mặc định nhiều quảng cáo)",
    "com.miui.videoplayer": "Mi Video (Xem video kèm quảng cáo)",
    "com.miui.player": "Mi Music (Trình nghe nhạc kèm quảng cáo)",
    "com.miui.yellowpage": "Yellow Pages (Dịch vụ danh bạ trang vàng)",
    "com.xiaomi.payment": "Mi Pay (Dịch vụ ví & thanh toán Xiaomi)",
    "com.miui.cleanmaster": "Cleaner (Trình dọn rác đối tác Cheetah Mobile)",
    "com.miui.hybrid": "Quick Apps (Nền tảng ứng dụng tức thì ngầm)",
    "com.miui.bugreport": "Mi Bug Report (Báo cáo lỗi tự động ngầm)",
    "com.xiaomi.joyose": "Joyose (Tiến trình bóp xung nhịp & theo dõi game)",
    "com.facebook.katana": "Facebook App (Ứng dụng cài sẵn)",
    "com.facebook.services": "Facebook Services (Dịch vụ nền Facebook)",
    "com.facebook.system": "Facebook System Installer",
    "com.facebook.appmanager": "Facebook App Manager",
    "com.google.android.apps.tachyon": "Google Duo / Meet",
    "com.google.android.videos": "Google TV / Phim",
    "com.google.android.music": "YouTube Music cài sẵn",
    "com.miui.compass": "La bàn Xiaomi",
    "com.miui.notes": "Ghi chú Xiaomi (Tùy chọn gỡ)",
    "com.miui.calculator": "Máy tính Xiaomi (Tùy chọn gỡ)",
    "com.miui.weather2": "Thời tiết Xiaomi",
    "com.sohu.inputmethod.sogou.xiaomi": "Bàn phím Sogou Xiaomi",
}


def adb_list_packages(filter_type: str = "all") -> List[str]:
    """
    Get list of installed packages.
    filter_type: 'all', 'user' (-3), 'system' (-s), 'disabled' (-d), 'enabled' (-e)
    """
    cmd = [ADB_EXE, "shell", "pm", "list", "packages"]
    if filter_type == "user":
        cmd.append("-3")
    elif filter_type == "system":
        cmd.append("-s")
    elif filter_type == "disabled":
        cmd.append("-d")
    elif filter_type == "enabled":
        cmd.append("-e")

    code, stdout, _ = run_command(cmd, timeout=20)
    if code != 0 or not stdout:
        return []

    packages = []
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            pkg = line.replace("package:", "").strip()
            if pkg:
                packages.append(pkg)
    return sorted(packages)


def adb_uninstall_package(pkg_name: str, keep_data: bool = False) -> Tuple[bool, str]:
    """Uninstall package for user 0 (Safe debloat, easily reinstallable)."""
    cmd = [ADB_EXE, "shell", "pm", "uninstall", "--user", "0"]
    if keep_data:
        cmd.append("-k")
    cmd.append(pkg_name)
    code, stdout, stderr = run_command(cmd, timeout=15)
    output = f"{stdout}\n{stderr}".strip()
    if code == 0 and "Success" in output:
        return True, f"Gỡ bỏ thành công: {pkg_name}"
    return False, f"Thất bại khi gỡ {pkg_name}: {output or 'Lỗi không xác định'}"


def adb_disable_package(pkg_name: str) -> Tuple[bool, str]:
    """Disable package for user 0."""
    cmd = [ADB_EXE, "shell", "pm", "disable-user", "--user", "0", pkg_name]
    code, stdout, stderr = run_command(cmd, timeout=15)
    output = f"{stdout}\n{stderr}".strip()
    if code == 0 and ("disabled" in output.lower() or "new state" in output.lower()):
        return True, f"Đã vô hiệu hóa: {pkg_name}"
    return False, f"Không thể vô hiệu hóa {pkg_name}: {output}"


def adb_enable_package(pkg_name: str) -> Tuple[bool, str]:
    """Re-enable previously disabled package."""
    cmd = [ADB_EXE, "shell", "pm", "enable", pkg_name]
    code, stdout, stderr = run_command(cmd, timeout=15)
    output = f"{stdout}\n{stderr}".strip()
    if code == 0 and ("enabled" in output.lower() or "new state" in output.lower()):
        return True, f"Đã bật lại: {pkg_name}"
    return False, f"Không thể bật lại {pkg_name}: {output}"


def adb_install_apk(
    apk_path: str,
    reinstall: bool = True,
    downgrade: bool = False,
    grant_permissions: bool = True
) -> Tuple[bool, str]:
    """Install APK via ADB with options."""
    if not os.path.isfile(apk_path):
        return False, f"File APK không tồn tại: {apk_path}"

    cmd = [ADB_EXE, "install"]
    if reinstall:
        cmd.append("-r")
    if downgrade:
        cmd.append("-d")
    if grant_permissions:
        cmd.append("-g")
    cmd.append(apk_path)

    code, stdout, stderr = run_command(cmd, timeout=120)
    output = f"{stdout}\n{stderr}".strip()
    if code == 0 and "Success" in output:
        return True, f"Cài đặt thành công: {os.path.basename(apk_path)}"
    return False, f"Cài đặt thất bại: {output or 'Mã lỗi ' + str(code)}"


# =========================================================================
# DISPLAY & 120HZ REFRESH RATE TWEAKER (ADB)
# =========================================================================

def adb_get_wm_density() -> Tuple[str, str]:
    """Returns (physical_density, override_density)"""
    code, stdout, _ = run_command([ADB_EXE, "shell", "wm", "density"], timeout=5)
    physical = "320"
    override = ""
    for line in stdout.splitlines():
        line = line.strip()
        if "Physical density:" in line:
            physical = line.replace("Physical density:", "").strip()
        elif "Override density:" in line:
            override = line.replace("Override density:", "").strip()
    return physical, override


def adb_set_wm_density(density: int) -> Tuple[bool, str]:
    """Set custom display density (DPI)."""
    code, stdout, stderr = run_command([ADB_EXE, "shell", "wm", "density", str(density)], timeout=5)
    if code == 0:
        return True, f"Đã áp dụng độ phân giải {density} DPI thành công!"
    return False, stderr or stdout or "Lỗi khi đổi DPI."


def adb_reset_wm_density() -> Tuple[bool, str]:
    """Reset display density to default."""
    code, stdout, stderr = run_command([ADB_EXE, "shell", "wm", "density", "reset"], timeout=5)
    if code == 0:
        return True, "Đã khôi phục DPI về mặc định ban đầu!"
    return False, stderr or stdout or "Lỗi khi reset DPI."


def adb_get_refresh_rates() -> Dict[str, str]:
    """Get current user, min, and peak refresh rate settings."""
    rates = {}
    for key in ["user_refresh_rate", "min_refresh_rate", "peak_refresh_rate"]:
        _, stdout, _ = run_command([ADB_EXE, "shell", "settings", "get", "system", key], timeout=5)
        val = stdout.strip()
        rates[key] = val if val and val != "null" else "Auto"
    return rates


def adb_set_refresh_rate(mode: str) -> Tuple[bool, str]:
    """
    Set refresh rate behavior.
    mode: 'force_120', '90', '60', 'auto'
    """
    if mode == "force_120":
        run_command([ADB_EXE, "shell", "settings", "put", "system", "user_refresh_rate", "120"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "min_refresh_rate", "120"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "peak_refresh_rate", "120"], timeout=5)
        return True, "Đã ép tần số quét 120Hz mọi lúc (Khóa 120Hz chống tụt fps)!"
    elif mode == "90":
        run_command([ADB_EXE, "shell", "settings", "put", "system", "user_refresh_rate", "90"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "min_refresh_rate", "90"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "peak_refresh_rate", "90"], timeout=5)
        return True, "Đã cài đặt tần số quét 90Hz (Mượt mà & Tiết kiệm pin)!"
    elif mode == "60":
        run_command([ADB_EXE, "shell", "settings", "put", "system", "user_refresh_rate", "60"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "min_refresh_rate", "60"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "peak_refresh_rate", "60"], timeout=5)
        return True, "Đã cài đặt tần số quét 60Hz (Tiết kiệm pin tối đa)!"
    elif mode == "auto":
        run_command([ADB_EXE, "shell", "settings", "delete", "system", "min_refresh_rate"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "min_refresh_rate", "60"], timeout=5)
        run_command([ADB_EXE, "shell", "settings", "put", "system", "peak_refresh_rate", "120"], timeout=5)
        return True, "Đã khôi phục tần số quét tự động thích ứng (Dynamic 60Hz-120Hz)!"
    return False, "Chế độ không hợp lệ."


def adb_set_animation_scales(scale: float) -> Tuple[bool, str]:
    """Set system animation scale (0.5x, 1.0x, 0x)."""
    s = f"{scale:.1f}" if scale > 0 else "0"
    for anim in ["window_animation_scale", "transition_animation_scale", "animator_duration_scale"]:
        run_command([ADB_EXE, "shell", "settings", "put", "global", anim, s], timeout=5)
    return True, f"Đã chỉnh tốc độ hiệu ứng hệ thống về {s}x!"


def adb_get_animation_scale() -> str:
    """Get window animation scale."""
    _, stdout, _ = run_command([ADB_EXE, "shell", "settings", "get", "global", "window_animation_scale"], timeout=5)
    val = stdout.strip()
    return f"{val}x" if val and val != "null" else "1.0x"


def adb_restart_launcher() -> Tuple[bool, str]:
    """Restart launcher to cleanly reorganize and realign desktop icons."""
    # Force stop MIUI/HyperOS Home and AOSP launchers so they auto-restart with new layout
    run_command([ADB_EXE, "shell", "am", "force-stop", "com.miui.home"], timeout=5)
    run_command([ADB_EXE, "shell", "am", "force-stop", "com.google.android.apps.nexuslauncher"], timeout=5)
    run_command([ADB_EXE, "shell", "am", "force-stop", "com.android.launcher3"], timeout=5)
    return True, "Đã làm mới màn hình chính! Các biểu tượng ứng dụng sẽ tự động căn chỉnh lại ngay ngắn."


def adb_open_workstation_mode() -> Tuple[bool, str]:
    """Open hidden Workstation Mode (Desktop Mode) settings page on Xiaomi Pad."""
    code, stdout, stderr = run_command([
        ADB_EXE, "shell", "am", "start", "-n", "com.android.settings/.desktopmode.MiuiDesktopModeActivity"
    ], timeout=5)
    if code == 0:
        return True, "Đã mở trang cài đặt Chế độ máy trạm (Workstation Mode) trên màn hình máy tính bảng!"
    code, stdout, stderr = run_command([
        ADB_EXE, "shell", "am", "start", "-a", "miui.settings.intent.action.DESKTOP_MODE_SETTINGS"
    ], timeout=5)
    if code == 0:
        return True, "Đã mở trang cài đặt Chế độ máy trạm (Workstation Mode) trên màn hình máy tính bảng!"
    return False, f"Không thể mở: {stderr or stdout}"
