import os
import sys

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
PLATFORM_TOOLS_DIR = os.path.join(TOOLS_DIR, "platform-tools")
APKS_DIR = os.path.join(TOOLS_DIR, "apks")
os.makedirs(APKS_DIR, exist_ok=True)

# Executables
ADB_EXE = os.path.join(PLATFORM_TOOLS_DIR, "adb.exe")
FASTBOOT_EXE = os.path.join(PLATFORM_TOOLS_DIR, "fastboot.exe")

# Files
GPT_BIN = os.path.join(TOOLS_DIR, "gpt_both0.bin")
EXPECTED_GPT_SIZE = 45056
EXPECTED_GPT_SHA256 = "5316799dae4858d0d08c5448699724b0e7848d2484eb5b9487e178bcc15be00d"

# Remote Download URLs
URL_PLATFORM_TOOLS = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
URL_GPT_BOTH0 = "https://github.com/erdilS/Port-Windows-11-Xiaomi-Pad-5/releases/download/Files/gpt_both0.bin"

# Device Identifiers for Xiaomi Pad 5
TARGET_CODENAME = "nabu"
TARGET_DEVICE_NAME = "Xiaomi Pad 5"

# App Info
APP_NAME = "Xiaomi Pad 5 (nabu) - Android Restore Tool Pro"
APP_VERSION = "1.0.0"
APP_AUTHOR = "ITK"
APP_SIGNATURE = "Created by ITK"
