@echo off
title Ballads of Hongye Trainer v0.4.1

rem 以本脚本所在目录为工作目录（整个文件夹搬动后路径自动跟随）
cd /d "%~dp0"

echo ============================================================
echo   Ballads of Hongye Trainer v0.4.1
echo ============================================================
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start. Please check Python installation.
    pause
)
