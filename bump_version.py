#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""woldvein Trainer - 一键升级版本号

用法:
  python bump_version.py                   # 显示当前版本与用法
  python bump_version.py 0.4.6             # 升级版本号（交互输入 changelog 描述，回车跳过）
  python bump_version.py 0.4.6 -m "描述"   # 升级版本号 + 指定 changelog 描述
  python bump_version.py 0.4.6 --build     # 升级版本号 + 立即打包（无描述则交互输入）
  python bump_version.py 0.4.6 --dry-run   # 试运行：只显示将做什么，不写任何文件

版本号唯一源：src/constants.py 的 APP_VERSION，改这里全项目自动跟随。
"""
import argparse
import datetime
import os
import re
import subprocess
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTANTS_PATH = os.path.join(PROJECT_DIR, "src", "constants.py")
CHANGELOG_PATH = os.path.join(PROJECT_DIR, "CHANGELOG.md")
BUILD_SCRIPT = os.path.join(PROJECT_DIR, "build_release.py")
VERSION_RE = re.compile(r'APP_VERSION\s*=\s*"([^"]+)"')
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def read_constants():
    """读取 constants.py，保留原始编码（UTF-8 BOM 或不带）。"""
    with open(CONSTANTS_PATH, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"
    text = raw.decode(encoding)
    return text, encoding


def get_current_version():
    text, _ = read_constants()
    m = VERSION_RE.search(text)
    if not m:
        print(f"[错误] 未在 {CONSTANTS_PATH} 中找到 APP_VERSION")
        sys.exit(1)
    return m.group(1)


def main():
    parser = argparse.ArgumentParser(description="一键升级版本号")
    parser.add_argument("new_version", nargs="?", help="新版本号，如 0.4.6")
    parser.add_argument("-m", "--message", default=None, help="CHANGELOG 变更描述（一行）")
    parser.add_argument("--build", action="store_true", help="升级后立即执行 build_release.py 打包")
    parser.add_argument("--dry-run", action="store_true", help="试运行：只打印计划，不写任何文件")
    args = parser.parse_args()

    if not os.path.exists(CONSTANTS_PATH):
        print(f"[错误] 未找到 {CONSTANTS_PATH}，请确认脚本位于项目根目录")
        sys.exit(1)

    current = get_current_version()
    print(f"当前版本: v{current}")

    if not args.new_version:
        print("\n用法:")
        print("  python bump_version.py 0.4.6             # 升级 + 交互填写描述")
        print('  python bump_version.py 0.4.6 -m "描述"    # 升级 + 指定描述')
        print("  python bump_version.py 0.4.6 --build      # 升级 + 立即打包")
        print("  python bump_version.py 0.4.6 --dry-run    # 试运行")
        return

    new = args.new_version.strip()
    if not SEMVER_RE.match(new):
        print(f"[错误] 版本号格式非法: {new!r}，应为 x.y.z（如 0.4.6）")
        sys.exit(1)

    if new == current:
        print(f"[提示] 新版本号与当前版本相同（v{current}），无需修改")
        return

    # 版本回退警告（不阻止）
    def _ver_key(v):
        return tuple(int(x) for x in v.split("."))
    if _ver_key(new) < _ver_key(current):
        print(f"[警告] 新版本 {new} 小于当前 {current}，确认是要回退版本吗？")

    # CHANGELOG 描述：-m 优先，否则交互输入（回车跳过）
    message = args.message
    if message is None and not args.dry_run:
        try:
            message = input(f"CHANGELOG 描述（回车跳过，留空占位）: ").strip()
        except EOFError:
            message = ""
    if message is None:
        message = ""
    if not message:
        message = "（待补充）"

    today = datetime.date.today().isoformat()
    changelog_entry = (
        f"## v{new} ({today})\n\n"
        f"### 变更\n"
        f"- {message}\n\n"
        f"---\n\n"
    )

    # 计划输出
    print("\n====== 执行计划 ======")
    print(f"  1. {CONSTANTS_PATH}\n     APP_VERSION \"{current}\" -> \"{new}\"")
    print(f"  2. {CHANGELOG_PATH}\n     顶部插入: ## v{new} ({today}) - {message}")
    if args.build:
        print("  3. 运行 build_release.py 打包")
    print("=======================")

    if args.dry_run:
        print("\n[dry-run] 未写入任何文件。")
        return

    # 1. 更新 constants.py（保留原编码/BOM）
    text, encoding = read_constants()
    text_new, n = VERSION_RE.subn(f'APP_VERSION = "{new}"', text, count=1)
    if n != 1:
        print("[错误] 版本号替换失败")
        sys.exit(1)
    with open(CONSTANTS_PATH, "w", encoding=encoding, newline="") as f:
        f.write(text_new)
    print(f"[OK] 版本号已更新: v{current} -> v{new}")

    # 2. 更新 CHANGELOG（插到第一个版本条目之前）
    if os.path.exists(CHANGELOG_PATH):
        with open(CHANGELOG_PATH, "rb") as f:
            raw = f.read()
        if raw.startswith(b"\xef\xbb\xbf"):
            enc = "utf-8-sig"
        else:
            enc = "utf-8"
        cl_text = raw.decode(enc)
        # 找第一个 "## v" 的位置，把新条目插到它前面
        m = re.search(r"^## v", cl_text, re.M)
        if m:
            cl_text = cl_text[: m.start()] + changelog_entry + cl_text[m.start():]
        else:
            cl_text = changelog_entry + cl_text
        with open(CHANGELOG_PATH, "w", encoding=enc, newline="") as f:
            f.write(cl_text)
        print(f"[OK] CHANGELOG 已插入 v{new} 条目")
    else:
        print(f"[跳过] 未找到 CHANGELOG.md（{CHANGELOG_PATH}）")

    # 3. 验证
    print("[验证] 重新读取 APP_VERSION ...")
    after = get_current_version()
    if after != new:
        print(f"[错误] 验证失败: 期望 {new}，实际 {after}")
        sys.exit(1)
    print(f"[OK] 验证通过: APP_VERSION = v{after}")

    # 4. 可选打包
    if args.build:
        if not os.path.exists(BUILD_SCRIPT):
            print(f"[错误] 未找到打包脚本 {BUILD_SCRIPT}")
            sys.exit(1)
        print("\n[打包] 调用 build_release.py ...")
        rc = subprocess.call([sys.executable, BUILD_SCRIPT], cwd=PROJECT_DIR)
        if rc != 0:
            print(f"[错误] 打包失败（退出码 {rc}）")
            sys.exit(rc)
        print("[OK] 打包完成")

    print(f"\n✅ 完成！当前版本 v{after}。")
    if not args.build:
        print("提示: 加 --build 可一步完成「升级 + 打包」。")

    # 目录名一致性提醒
    dirname = os.path.basename(PROJECT_DIR)
    m = re.search(r"(\d+\.\d+\.\d+)", dirname)
    if m and m.group(1) != new:
        print(f"[提醒] 目录名 {dirname} 与版本号 v{new} 不一致（目录名只是文件夹名，不影响打包，可自行决定是否重命名）")


if __name__ == "__main__":
    main()
