# -*- coding: utf-8 -*-
"""
woldvein Trainer 一键打包脚本（通用版，无硬编码）

设计原则：
    - 版本号唯一来源：src/constants.py::APP_VERSION（改版本只改一处）
    - 路径全部基于项目根目录自动推导，不依赖任何绝对路径
    - 打包流程 = PyInstaller（EXE）→ Inno Setup（安装包）

用法：
    python build_release.py               # 全流程：EXE + 安装包
    python build_release.py --no-installer  # 只打 PyInstaller EXE
    python build_release.py --no-exe         # 只打 Inno Setup 安装包（使用 dist_final 已有 EXE）

产物：
    dist_final/woldvein_trainer.exe              # PyInstaller 单文件 EXE
    woldvein_trainer_v<版本>_setup.exe           # Inno Setup 安装包（项目根目录）
"""
import os
import sys
import shutil
import subprocess
import argparse

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from src.constants import APP_VERSION  # 版本号唯一源，勿在本文件硬编码

EXE_DIR = os.path.join(PROJECT_DIR, "dist_final")   # PyInstaller 输出目录
BUILD_DIR = os.path.join(PROJECT_DIR, "build")      # PyInstaller 工作目录
SPEC_PATH = os.path.join(PROJECT_DIR, "woldvein_trainer.spec")
ISS_PATH = os.path.join(PROJECT_DIR, "installer_build", "setup.iss")
SETUP_EXE = os.path.join(PROJECT_DIR, f"woldvein_trainer_v{APP_VERSION}_setup.exe")

# Inno Setup 常见安装位置（按顺序探测，可用环境变量 INNO_SETUP_PATH 覆盖）
_ISCC_CANDIDATES = [
    os.environ.get("INNO_SETUP_PATH", ""),
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
    r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    r"C:\Program Files\Inno Setup 5\ISCC.exe",
]


def _find_iscc():
    """定位 ISCC.exe；找不到返回 None，不硬编码死路径。"""
    for cand in _ISCC_CANDIDATES:
        if cand and os.path.isfile(cand):
            return cand
    # 最后尝试 PATH
    which = shutil.which("ISCC.exe")
    if which:
        return which
    return None


def _run(cmd, cwd=None):
    """执行外部命令并回显关键输出。"""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"  ❌ 命令失败 (exit {result.returncode})")
        if result.stdout:
            print(f"  STDOUT(尾部): {result.stdout[-2000:]}")
        if result.stderr:
            print(f"  STDERR(尾部): {result.stderr[-2000:]}")
        return False
    if result.stdout:
        print(f"  {result.stdout.strip()[-800:]}")
    return True


def build_exe():
    """PyInstaller 打包单文件 EXE → dist_final/"""
    print(f"[1/2] PyInstaller 打包 EXE (v{APP_VERSION})")
    try:
        import PyInstaller
        print(f"  PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("  ❌ 未安装 PyInstaller，请先执行: pip install pyinstaller")
        return False

    # 清理旧产物（保留历史备份由版本管理负责）
    if os.path.isdir(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--distpath", EXE_DIR,
        "--workpath", BUILD_DIR,
        SPEC_PATH,
    ]
    if not _run(cmd, cwd=PROJECT_DIR):
        return False

    exe = os.path.join(EXE_DIR, "woldvein_trainer.exe")
    if not os.path.isfile(exe):
        print(f"  ❌ 未找到产物: {exe}")
        return False
    size_mb = os.path.getsize(exe) / 1024 / 1024
    print(f"  ✅ EXE 完成: {exe} ({size_mb:.1f} MB)")
    return True


def build_installer():
    """Inno Setup 制作安装包；版本号通过 /D 传入，覆盖 setup.iss 默认值。"""
    print(f"[2/2] Inno Setup 打包安装包 (v{APP_VERSION})")
    iscc = _find_iscc()
    if not iscc:
        print("  ❌ 未找到 ISCC.exe，请安装 Inno Setup 6，或用环境变量 INNO_SETUP_PATH 指定路径")
        return False

    if not os.path.isfile(ISS_PATH):
        print(f"  ❌ 未找到脚本: {ISS_PATH}")
        return False

    cmd = [iscc, f"/DMyAppVersion={APP_VERSION}", ISS_PATH]
    ok = _run(cmd, cwd=os.path.join(PROJECT_DIR, "installer_build"))
    if not ok:
        return False
    if os.path.isfile(SETUP_EXE):
        size_mb = os.path.getsize(SETUP_EXE) / 1024 / 1024
        print(f"  ✅ 安装包完成: {SETUP_EXE} ({size_mb:.1f} MB)")
        return True
    print(f"  ⚠️  未在预期位置找到安装包（可能 OutputDir 有变化），请检查 ISCC 输出")
    return True


def main():
    parser = argparse.ArgumentParser(description="woldvein Trainer 一键打包")
    parser.add_argument("--no-installer", action="store_true", help="只打 EXE，跳过安装包")
    parser.add_argument("--no-exe", action="store_true", help="跳过 EXE，直接用 dist_final 已有产物打安装包")
    args = parser.parse_args()

    print("=" * 60)
    print(f"  woldvein Trainer v{APP_VERSION} 打包")
    print("=" * 60)

    ok = True
    if not args.no_exe:
        ok = build_exe() and ok
    if not args.no_installer:
        if not args.no_exe:
            exe = os.path.join(EXE_DIR, "woldvein_trainer.exe")
            if not os.path.isfile(exe):
                print("  ❌ dist_final/woldvein_trainer.exe 不存在，无法制作安装包")
                return
        ok = build_installer() and ok

    print("=" * 60)
    if ok:
        print("  ✅ 打包完成！")
        print(f"  版本: {APP_VERSION}（来源 src/constants.py）")
        if not args.no_exe:
            print(f"  EXE: {os.path.join(EXE_DIR, 'woldvein_trainer.exe')}")
        if not args.no_installer:
            print(f"  安装包: {SETUP_EXE}")
    else:
        print("  ❌ 打包失败，请根据上方错误信息处理")
    print("=" * 60)


if __name__ == "__main__":
    main()
