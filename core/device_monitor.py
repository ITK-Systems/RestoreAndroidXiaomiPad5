import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.adb_fastboot import (
    get_adb_devices,
    get_fastboot_devices,
    get_fastboot_var
)


class DeviceMonitorThread(QThread):
    """Background polling thread to detect device connection status in real-time."""
    
    # mode: 'NONE', 'ADB', 'UNAUTHORIZED', 'FASTBOOT'
    # serial: device serial or ''
    # status_text: friendly text description
    # details: dict of extra info (product, state, etc.)
    status_changed = pyqtSignal(str, str, str, dict)

    def __init__(self, poll_interval: float = 1.5, parent=None):
        super().__init__(parent)
        self.poll_interval = poll_interval
        self._running = True
        self._last_signature = None

    def run(self):
        while self._running:
            try:
                self._check_devices()
            except Exception:
                pass
            
            # Sleep in small slices to allow rapid thread stopping
            steps = int(self.poll_interval / 0.1)
            for _ in range(steps):
                if not self._running:
                    break
                time.sleep(0.1)

    def stop(self):
        self._running = False
        self.wait(1000)

    def _check_devices(self):
        # 1. Check Fastboot first (Fastboot is the primary restore target)
        fastboot_devs = get_fastboot_devices()
        if fastboot_devs:
            dev = fastboot_devs[0]
            serial = dev.get("serial", "Unknown")
            product = get_fastboot_var("product") or "nabu"
            unlocked = get_fastboot_var("unlocked") or "yes"
            sig = f"FASTBOOT:{serial}:{product}"
            
            if sig != self._last_signature:
                self._last_signature = sig
                self.status_changed.emit(
                    "FASTBOOT",
                    serial,
                    f"Đã kết nối FASTBOOT ({product})",
                    {"product": product, "unlocked": unlocked, "serial": serial}
                )
            return

        # 2. Check ADB devices
        adb_devs = get_adb_devices()
        if adb_devs:
            dev = adb_devs[0]
            serial = dev.get("serial", "Unknown")
            state = dev.get("state", "device")
            
            if state == "unauthorized":
                sig = f"ADB_UNAUTH:{serial}"
                if sig != self._last_signature:
                    self._last_signature = sig
                    self.status_changed.emit(
                        "UNAUTHORIZED",
                        serial,
                        "Thiết bị Android chưa cho phép Gỡ lỗi USB (Cần bấm 'Cho phép' trên màn hình)",
                        {"state": "unauthorized", "serial": serial}
                    )
                return
            elif state == "device":
                sig = f"ADB:{serial}"
                if sig != self._last_signature:
                    self._last_signature = sig
                    self.status_changed.emit(
                        "ADB",
                        serial,
                        "Đã kết nối Android (ADB Online)",
                        {"state": "online", "serial": serial}
                    )
                return
            elif state == "recovery":
                sig = f"RECOVERY:{serial}"
                if sig != self._last_signature:
                    self._last_signature = sig
                    self.status_changed.emit(
                        "ADB",
                        serial,
                        "Đã kết nối thiết bị ở chế độ Recovery",
                        {"state": "recovery", "serial": serial}
                    )
                return

        # 3. No device found
        sig = "NONE"
        if sig != self._last_signature:
            self._last_signature = sig
            self.status_changed.emit(
                "NONE",
                "",
                "Chưa phát hiện thiết bị. Vui lòng kết nối cáp USB với Xiaomi Pad 5.",
                {}
            )
