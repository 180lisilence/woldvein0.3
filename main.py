#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平野孤鸿 全能修改器 v0.3
主程序入口

功能说明：
    本程序是《平野孤鸿》(Ballads of Hongye, Steam AppID 2656540)的全能修改器。
    通过DLL注入 + inline-hook lua_pcall的方式，在游戏进程内部执行Lua脚本，
    实现资源修改、创造模式、热键（独立工具配置）、游戏监控、高级工具、世界系统等功能。

架构说明：
    main.py          → 程序入口，异常捕获
    src/gui/         → tkinter GUI界面（左侧导航 + 6 个页面）
    src/injector/    → DLL注入核心 + trainer.c源码
    src/lua_engine.py → Lua脚本执行引擎（命令文件通信）
    src/*.py         → 各功能模块

使用方式：
    1. 先启动游戏并进入存档
    2. 运行本程序（建议管理员权限以启用全局热键）
    3. 点击"注入DLL"按钮
    4. 等待Hook就绪提示后即可使用所有功能

技术要点：
    - DLL注入：CreateRemoteThread + LoadLibraryW（支持Unicode路径）
    - Hook方式：inline-hook Lua5X64.dll的lua_pcall函数
    - 通信机制：命令文件(lua_cmd.txt/lua_result.txt)轮询
    - 指令长度：自研x86-64解码器，失败时放弃安装而非硬编码回退
"""
import os
import sys

# 确保项目根目录在Python模块搜索路径中
# 这样才能正确导入 src.* 模块
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.gui.main_gui import main

if __name__ == "__main__":
    try:
        # 启动GUI主循环
        main()
    except KeyboardInterrupt:
        # 用户按 Ctrl+C 或关闭窗口，正常退出
        pass
    except Exception as e:
        # 未捕获异常，先写入日志再抛出
        try:
            from src.logger import log_error
            log_error(f"未捕获异常: {e}")
        except Exception as log_err:
            # logger 自身失败时只能 print 到 stderr
            import sys
            print(f"[FATAL] 日志记录失败: {log_err}", file=sys.stderr)
        raise
