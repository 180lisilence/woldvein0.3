@echo off
title 平野孤鸿修改器 - 热键配置工具
echo ========================================
echo   平野孤鸿修改器 - 热键配置工具 v0.3
echo ========================================
echo.
cd /d "%~dp0"
python hotkey_configurator.py
if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请确认已安装 Python 3.10+
    pause
)
