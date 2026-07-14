# -*- coding: utf-8 -*-
"""
setup_emarx.py — EMARX 一键环境配置脚本。

安装 EMARX 所需的全部 Python 依赖和浏览器驱动，让新用户安装技能后无需手动配置即可使用 CNKI 检索等功能。

用法：
  python scripts/setup_emarx.py

功能：
  1. 检查 Python 版本（>= 3.9）
  2. 安装 EMARX 核心依赖（word 交付、格式转换等）
  3. 安装 CNKI 模块依赖（playwright、ocr、解析等）
  4. 安装 Playwright Chromium 浏览器
  5. 输出环境就绪报告
"""
import subprocess
import sys
from pathlib import Path


def check_python_version() -> bool:
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"错误：需要 Python >= 3.9，当前为 {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"Python 版本检查通过：{version.major}.{version.minor}.{version.micro}")
    return True


def install_requirements(req_path: Path) -> bool:
    if not req_path.exists():
        print(f"未找到依赖文件：{req_path}，跳过")
        return True

    print(f"正在安装依赖：{req_path}")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(req_path)]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"安装失败：{req_path}")
        return False
    print(f"安装成功：{req_path}")
    return True


def install_playwright_browsers() -> bool:
    print("正在安装 Playwright Chromium 浏览器（可能需要几分钟）...")
    cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print("Playwright 浏览器安装失败")
        return False
    print("Playwright Chromium 安装成功")
    return True


def check_pandoc() -> bool:
    result = subprocess.run(["pandoc", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print("pandoc 已安装")
        return True
    print("警告：未检测到 pandoc。Word 交付功能需要 pandoc，请从 https://pandoc.org/installing.html 安装。")
    return False


def main():
    print("=" * 60)
    print("EMARX 环境配置")
    print("=" * 60)

    if not check_python_version():
        sys.exit(1)

    script_dir = Path(__file__).resolve().parent
    skill_root = script_dir.parent

    # 安装 EMARX 核心依赖
    core_req = skill_root / "requirements.txt"
    if not install_requirements(core_req):
        sys.exit(1)

    # 安装 CNKI 模块依赖
    cnki_req = skill_root / "scripts" / "cnki" / "requirements.txt"
    if not install_requirements(cnki_req):
        sys.exit(1)

    # 安装 Playwright 浏览器
    if not install_playwright_browsers():
        sys.exit(1)

    # 检查 pandoc
    check_pandoc()

    print("=" * 60)
    print("EMARX 环境配置完成")
    print("=" * 60)
    print("现在可以运行：")
    print("  python scripts/cnki_cli.py search \"关键词\" --pages 3 --output workspace/cnki_results.json")


if __name__ == "__main__":
    main()
