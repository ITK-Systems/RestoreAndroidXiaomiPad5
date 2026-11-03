@echo off
chcp 65001 >nul
title Xiaomi Pad 5 (nabu) - Android Restore Tool Pro
cd /d "%~dp0"

echo ============================================================
echo   XIAOMI PAD 5 (NABU) - ANDROID RESTORE TOOL PRO
echo   Khoi phuc 100%% Android - Go bo Windows 11 & ESP
echo ============================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python tren he thong. Vui long cai dat Python 3.10+ de chay ung dung.
    pause
    exit /b 1
)

echo Dang khoi chay giao dien phan mem...
python app.py
if %errorlevel% neq 0 (
    echo.
    echo [Luu y] Ung dung da dong voi ma loi %errorlevel%.
    pause
)
