@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Ballads of Hongye Trainer v0.3

cd /d "%~dp0"

echo ========================================
echo   Ballads of Hongye Trainer v0.3
echo   Source Code Mode
echo ========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing dependencies...
    pip install psutil keyboard pystray pillow
)

echo [START] Launching trainer...
echo.

python main.py
set "EXIT_CODE=!errorlevel!"

if !EXIT_CODE! neq 0 (
    echo.
    echo [ERROR] Program exited with code !EXIT_CODE!
    pause
)

endlocal
