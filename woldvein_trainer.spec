# -*- mode: python ; coding: utf-8 -*-
import os
import sys

block_cipher = None

# SPECPATH 由 PyInstaller 注入：本 spec 文件所在目录（即项目根），勿硬编码绝对路径
PROJECT_DIR = os.path.abspath(SPECPATH) if 'SPECPATH' in globals() else os.path.dirname(os.path.abspath(__file__))

a = Analysis(
    ['main.py'],
    pathex=[PROJECT_DIR],
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
    hooksconfig={},
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
    name='woldvein_trainer',
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
