# -*- coding: utf-8 -*-
"""
cnki/env_check.py — 检查 CNKI 模块运行环境是否就绪。

在调用 CNKI 功能前运行，若缺少依赖或浏览器，给出友好提示或尝试自动安装。
"""
import importlib
import subprocess
import sys
from pathlib import Path


REQUIRED_PACKAGES = [
    "playwright",
    "requests",
    "bs4",
    "lxml",
    "PIL",
    "cv2",
    "numpy",
    "ddddocr",
    "playwright_stealth",
]


def check_python_version() -> bool:
    version = sys.version_info
    return version.major >= 3 and version.minor >= 9


def check_package(package: str) -> bool:
    try:
        importlib.import_module(package)
        return True
    except ImportError:
        return False


def check_all_packages() -> tuple[list[str], list[str]]:
    missing = []
    ready = []
    for pkg in REQUIRED_PACKAGES:
        if check_package(pkg):
            ready.append(pkg)
        else:
            missing.append(pkg)
    return ready, missing


def check_playwright_browser() -> bool:
    """检查 Playwright Chromium 是否已安装。"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                p.chromium.launch()
                return True
            except Exception:
                return False
    except Exception:
        return False


def auto_install(skill_root: Path | None = None) -> bool:
    """尝试自动安装缺失的依赖和浏览器。"""
    print("检测到环境未就绪，尝试自动安装...")

    if skill_root is None:
        skill_root = Path(__file__).resolve().parent.parent.parent

    req_files = [
        skill_root / "requirements.txt",
        skill_root / "scripts" / "cnki" / "requirements.txt",
    ]

    for req in req_files:
        if req.exists():
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "-r", str(req)]
            )
            if result.returncode != 0:
                print(f"安装依赖失败：{req}")
                return False

    result = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    if result.returncode != 0:
        print("安装 Playwright Chromium 失败")
        return False

    return True


def ensure_ready(auto: bool = False, skill_root: Path | None = None) -> bool:
    """
    确保环境就绪。

    参数：
      auto: 如果环境未就绪，是否尝试自动安装
    """
    if not check_python_version():
        print("错误：CNKI 模块需要 Python >= 3.9")
        return False

    ready_pkgs, missing_pkgs = check_all_packages()
    browser_ok = check_playwright_browser()

    if missing_pkgs:
        print(f"缺少 Python 依赖：{', '.join(missing_pkgs)}")
    if not browser_ok:
        print("缺少 Playwright Chromium 浏览器")

    if not missing_pkgs and browser_ok:
        return True

    if auto:
        return auto_install(skill_root)

    print("请运行以下命令完成配置：")
    print("  python scripts/setup_emarx.py")
    return False


def main():
    ok = ensure_ready(auto=False)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
