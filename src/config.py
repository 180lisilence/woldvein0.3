"""
woldvein Trainer v0.3 - 配置管理模块

功能说明：
    管理修改器的所有配置项，包括游戏路径、热键映射、创造模式选项、窗口位置等。
    配置以JSON格式存储在config.json中，打包后位于EXE所在目录。

核心设计：
    - DEFAULT_CONFIG：默认配置字典，包含所有可配置项
    - _deep_merge()：递归深合并，用户配置覆盖默认值，嵌套字典逐键补全
    - load_config()：加载配置文件，不存在或损坏时返回默认配置
    - save_config()：保存配置到JSON文件

配置项说明：
    game_path       游戏根目录路径
    game_exe        游戏EXE相对路径
    steam_app_id    Steam应用ID（2656540）
    dll_path        自定义DLL路径（空则使用内置DLL）
    hotkeys         热键映射字典（功能名→热键组合）
    creative_mode   创造模式子选项（满级/解锁/无限资源/无限制升级）
    window          窗口位置和大小
    auto_detect_game 是否自动检测游戏进程
    hotkeys_enabled 是否启用全局热键
    theme           UI主题（"dark"深色 / "light"浅色）
"""
import json
import os
import sys
import copy

from .hotkey_defs import get_default_hotkeys
from .constants import (
    DEFAULT_GAME_PATH,
    GAME_EXE_REL,
    STEAM_APP_ID,
    runtime_config_dir,
)

# 配置文件路径：兼容PyInstaller打包环境
# 打包后(sys.frozen=True)：优先%LOCALAPPDATA%\woldvein_trainer\config.json
#   （避免EXE放在Program Files等无权限目录时写入失败）
# 开发环境：项目根目录/config.json
_config_dir = runtime_config_dir()
os.makedirs(_config_dir, exist_ok=True)
CONFIG_PATH = os.path.join(_config_dir, "config.json")

# 默认配置：所有可配置项的默认值
# 用户配置文件中缺少的键会从这里补全（深合并）
DEFAULT_CONFIG = {
    # 游戏相关路径
    "game_path": DEFAULT_GAME_PATH,
    "game_exe": GAME_EXE_REL,
    "steam_app_id": STEAM_APP_ID,
    # DLL路径：空字符串表示使用打包内置的DLL
    "dll_path": "",
    # 全局热键映射：功能名 → 热键组合（keyboard库格式）
    "hotkeys": get_default_hotkeys(),  # 唯一定义源：src/hotkey_defs.py
    # 创造模式子选项（开启创造模式时哪些子功能生效）
    "creative_mode": {
        "max_boom": True,              # 鸿业等级满级
        "unlock_all_buildings": True,  # 全建筑解锁（只显示最高等级）
        "infinite_resources": True,    # 无限资源（建造不消耗）
        "unlimited_upgrade": True,     # 无限制升级（解锁全部功能）
    },
    # 窗口位置和大小（None表示居中）
    "window": {
        "width": None,
        "height": None,
        "x": None,
        "y": None,
    },
    # 自动检测游戏进程（每5秒检测一次）
    "auto_detect_game": True,
    # 是否启用全局热键（需要管理员权限）
    "hotkeys_enabled": True,
    # UI主题（v0.3 新增："dark"深色 / "light"浅色）
    "theme": "dark",
}


def _deep_merge(base, override):
    """
    递归深合并两个字典。

    参数：
        base: 基础字典（默认配置）
        override: 覆盖字典（用户配置）

    返回：
        合并后的新字典（不修改原字典）

    规则：
        - 两个字典都有的键且值都是字典 → 递归合并
        - 其他情况 → override覆盖base
        - 所有值都深拷贝，避免引用共享
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # 嵌套字典：递归合并
            result[key] = _deep_merge(result[key], value)
        else:
            # 非字典或base中不存在：直接覆盖
            result[key] = copy.deepcopy(value)
    return result


def _safe_print(msg):
    """安全打印，避免windowed打包下sys.stdout为None时崩溃"""
    try:
        print(msg)
    except Exception:
        pass


def load_config():
    """
    加载配置文件。

    返回：
        配置字典（已与默认配置深合并，嵌套缺键不会崩溃）

    处理逻辑：
        1. 配置文件存在 → 读取JSON → 深合并默认配置
        2. 配置文件不存在或损坏 → 返回默认配置的深拷贝
        3. JSON解析失败 → 打印警告，返回默认配置
    """
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if not isinstance(cfg, dict):
                # 配置文件内容不是字典，使用默认配置
                return copy.deepcopy(DEFAULT_CONFIG)
            # 深合并：用户配置覆盖默认，嵌套字典逐键补全
            return _deep_merge(DEFAULT_CONFIG, cfg)
        except Exception as e:
            _safe_print(f"[Config] 加载配置失败: {e}，使用默认配置")
    return copy.deepcopy(DEFAULT_CONFIG)


def save_config(config):
    """
    保存配置到JSON文件。

    参数：
        config: 配置字典

    返回：
        True表示保存成功，False表示失败

    特点：
        - ensure_ascii=False：中文不转义，可读性好
        - indent=2：缩进格式化
        - 自动创建目录
    """
    try:
        parent = os.path.dirname(CONFIG_PATH)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        _safe_print(f"[Config] 保存配置失败: {e}")
        return False
