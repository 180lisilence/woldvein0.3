#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平野孤鸿 全能修改器 v0.3.1
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

# 单实例保护：修改器与游戏 DLL 通过固定路径的 lua_cmd.txt / lua_result.txt 通信，
# 多开会让两个实例的后台状态轮询互相覆盖命令文件（实机事故 2026-09-14：
# 注入面板 / 品阶升级 全部返回别的命令的结果 → 假失败）。这里用命名互斥体拦住第二个实例。
_SINGLE_INSTANCE_HANDLE = None


def _ensure_single_instance():
    """已有实例在运行时弹提示并退出（返回 True 表示可以继续）"""
    global _SINGLE_INSTANCE_HANDLE
    if os.name != "nt":
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        _SINGLE_INSTANCE_HANDLE = kernel32.CreateMutexW(None, False, "woldvein_trainer_mutex_v03")
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            ctypes.windll.user32.MessageBoxW(
                None,
                "检测到修改器已经在运行。\n\n"
                "多开会让两个实例互相覆盖游戏通信文件，导致注入/修改「失败」。\n"
                "请先关闭其它修改器窗口（含任务栏里多余的实例）再启动。",
                "woldvein Trainer",
                0x00000040,  # MB_ICONINFORMATION
            )
            return False
    except Exception:
        return True  # 保护失败不阻塞启动
    return True

# 确保项目根目录在Python模块搜索路径中
# 这样才能正确导入 src.* 模块
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.gui.main_gui import main

if __name__ == "__main__":
    # 单实例检查（多开会破坏与游戏 DLL 的命令文件通道）
    if not _ensure_single_instance():
        sys.exit(0)
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
