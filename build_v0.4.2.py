# -*- coding: utf-8 -*-
"""
0.4.2 打包脚本
1. 备份源码
2. PyInstaller打包
3. 复制资源文件
4. 制作安装包
"""
import os
import sys
import shutil
import time
import subprocess

PROJECT_DIR = r"D:\pingye_pack\releases\woldvein_trainer"
BACKUP_DIR = r"D:\pingye_pack\backups"
BUILD_DIR = os.path.join(PROJECT_DIR, "build_output")
DIST_DIR = os.path.join(PROJECT_DIR, "dist_final")

VERSION = "0.4.2"
APP_NAME = "woldvein_trainer"
EXE_NAME = "平野孤鸿修改器_v0.4.2.exe"


def backup():
    """备份源码"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_name = f"woldvein_trainer_backup_{timestamp}_v{VERSION}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    print(f"[1/5] 备份源码到: {backup_path}")
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # 复制项目文件（排除__pycache__, build, dist_final, logs）
    shutil.copytree(
        PROJECT_DIR,
        backup_path,
        ignore=shutil.ignore_patterns(
            "__pycache__", "build", "dist_final", "logs", "*.pyc", "errorlog.txt"
        )
    )
    print(f"  ✅ 备份完成")
    return backup_path


def create_spec():
    """创建PyInstaller spec文件"""
    print(f"[2/5] 创建PyInstaller spec文件")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[r'{PROJECT_DIR}'],
    binaries=[],
    datas=[
        ('dist/woldvein_trainer.dll', 'dist'),
        ('assets', 'assets'),
        ('config.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'src.constants',
        'src.config',
        'src.logger',
        'src.lua_engine',
        'src.lua_lib',
        'src.resource_editor',
        'src.resource_defs',
        'src.creative_mode',
        'src.advanced_tools',
        'src.cheat_tools',
        'src.world_tools',
        'src.game_status',
        'src.game_monitor',
        'src.hotkey_defs',
        'src.hotkey_manager',
        'src.injector',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_path = os.path.join(PROJECT_DIR, f"{APP_NAME}.spec")
    with open(spec_path, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"  ✅ spec文件已创建: {spec_path}")
    return spec_path


def build_exe(spec_path):
    """用PyInstaller打包"""
    print(f"[3/5] PyInstaller打包中...")
    
    # 清理旧的构建目录
    for d in ["build", "dist_final"]:
        p = os.path.join(PROJECT_DIR, d)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)
    
    # 执行PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(PROJECT_DIR, "build"),
        spec_path
    ]
    
    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_DIR, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ❌ 打包失败")
        print(f"  STDOUT: {result.stdout[-2000:]}")
        print(f"  STDERR: {result.stderr[-2000:]}")
        return False
    
    print(f"  ✅ 打包完成")
    return True


def copy_extra_files():
    """复制额外文件到打包目录"""
    print(f"[4/5] 复制额外文件")
    
    exe_dir = os.path.join(DIST_DIR, APP_NAME)
    if not os.path.exists(exe_dir):
        exe_dir = DIST_DIR  # onefile模式
    
    # 复制启动bat
    bat_src = os.path.join(PROJECT_DIR, f"启动修改器_v{VERSION}.bat")
    if os.path.exists(bat_src):
        shutil.copy2(bat_src, os.path.join(DIST_DIR, f"启动修改器_v{VERSION}.bat"))
        print(f"  ✅ 复制启动bat")
    
    # 复制README
    readme_src = os.path.join(PROJECT_DIR, "README.md")
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, os.path.join(DIST_DIR, "README.md"))
        print(f"  ✅ 复制README")
    
    # 复制CHANGELOG
    changelog_src = os.path.join(PROJECT_DIR, "CHANGELOG.md")
    if os.path.exists(changelog_src):
        shutil.copy2(changelog_src, os.path.join(DIST_DIR, "CHANGELOG.md"))
        print(f"  ✅ 复制CHANGELOG")
    
    # 列出打包结果
    print(f"\n  打包目录内容:")
    for item in os.listdir(DIST_DIR):
        item_path = os.path.join(DIST_DIR, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path) / 1024 / 1024
            print(f"    {item} ({size:.1f} MB)")
        else:
            print(f"    {item}/ (目录)")
    
    return True


def make_zip():
    """制作压缩包"""
    print(f"[5/5] 制作压缩包")
    
    zip_name = f"woldvein_trainer_v{VERSION}"
    zip_path = os.path.join(r"D:\pingye_pack\releases", zip_name)
    
    # 用shutil.make_archive
    shutil.make_archive(zip_path, 'zip', DIST_DIR)
    
    final_zip = zip_path + ".zip"
    size = os.path.getsize(final_zip) / 1024 / 1024
    print(f"  ✅ 压缩包已创建: {final_zip} ({size:.1f} MB)")
    return final_zip


def main():
    print("=" * 60)
    print(f"  woldvein_trainer v{VERSION} 打包脚本")
    print("=" * 60)
    print()
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print(f"PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ 未安装PyInstaller，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller安装完成")
    
    print()
    
    # 1. 备份
    backup_path = backup()
    
    # 2. 创建spec
    spec_path = create_spec()
    
    # 3. 打包
    if not build_exe(spec_path):
        print("\n❌ 打包失败，请检查错误信息")
        return
    
    # 4. 复制额外文件
    copy_extra_files()
    
    # 5. 制作压缩包
    zip_path = make_zip()
    
    print()
    print("=" * 60)
    print("  ✅ 打包完成！")
    print("=" * 60)
    print(f"  源码备份: {backup_path}")
    print(f"  打包目录: {DIST_DIR}")
    print(f"  压缩包:   {zip_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
