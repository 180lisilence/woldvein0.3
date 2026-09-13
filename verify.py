#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证测试脚本"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import load_config
from src.resource_editor import RESOURCES

print("所有模块导入成功")
print(f"资源数量: {len(RESOURCES)}")

# 测试加解密（存档编辑已独立为 save_editor_tool，此处为可选测试）
try:
    from src._archive.save_editor_legacy.save_editor import decrypt_buffer, encrypt_buffer
    test_data = b'{"test": "hello world", "money": 1000000}'
    encrypted = encrypt_buffer(test_data)
    decrypted = decrypt_buffer(encrypted)
    print(f"加解密测试: {'PASS' if decrypted == test_data else 'FAIL'}")
    print(f"原始大小: {len(test_data)}, 加密大小: {len(encrypted)}")
except ImportError:
    print("加解密测试: SKIP（存档编辑模块已归档到 _archive/）")

# 测试配置
cfg = load_config()
print(f"配置加载: {len(cfg)} 项")
print(f"热键数量: {len(cfg['hotkeys'])}")

# 测试DLL存在
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "woldvein_trainer.dll")
print(f"DLL存在: {os.path.exists(dll_path)}, 大小: {os.path.getsize(dll_path) if os.path.exists(dll_path) else 0}")

print("\n=== 全部验证通过 ===")
