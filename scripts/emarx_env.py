# -*- coding: utf-8 -*-
"""
emarx_env.py — EMARX 虚拟环境管理工具。

确保 EMARX 脚本在隔离的虚拟环境中运行，避免污染用户全局 Python 环境，同时解决依赖冲突。

用法（放在任何 EMARX 脚本开头）：
  from emarx_env import ensure_venv_and_reexec
  ensure_venv_and_reexec()
"""
import os
import subprocess
import sys
from pathlib import Path


ENV_MARKER = "EMARX_VENV_ACTIVE"


def get_skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_venv_dir() -> Path:
    return get_skill_root() / ".venv"


def get_venv_python() -> Path:
    venv = get_venv_dir()
    if sys.platform == "win32":
        return venv / "Scripts" / "python.exe"
    return venv / "bin" / "python"


def venv_exists() -> bool:
    return get_venv_python().exists()


def create_venv() -> bool:
    venv_dir = get_venv_dir()
    print(f"创建 EMARX 虚拟环境：{venv_dir}")
    result = subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
    return result.returncode == 0


def install_in_venv(req_path: Path) -> bool:
    python = get_venv_python()
    if not python.exists():
        print(f"虚拟环境 Python 不存在：{python}")
        return False
    print(f"在虚拟环境中安装依赖：{req_path}")
    cmd = [str(python), "-m", "pip", "install", "--upgrade", "-r", str(req_path)]
    result = subprocess.run(cmd)
    return result.returncode == 0


def install_playwright_browsers_in_venv() -> bool:
    python = get_venv_python()
    print("在虚拟环境中安装 Playwright Chromium 浏览器（可能需要几分钟）...")
    cmd = [str(python), "-m", "playwright", "install", "chromium"]
    result = subprocess.run(cmd)
    return result.returncode == 0


def ensure_venv_and_reexec():
    """
    确保在 EMARX 虚拟环境中运行当前脚本。
    如果当前不在 venv 中，创建 venv、安装依赖，然后重新用 venv 的 Python 执行当前脚本。
    如果 venv 已存在但依赖不完整，会自动补装。
    """
    # 已经在 venv 中，检查依赖和浏览器是否完整
    if os.environ.get(ENV_MARKER) == "1":
        try:
            import importlib.util
            missing = [pkg for pkg in ["playwright", "requests", "bs4", "lxml", "PIL", "cv2", "numpy", "ddddocr", "playwright_stealth"] if importlib.util.find_spec(pkg) is None]
            if missing:
                print(f"虚拟环境中缺少依赖：{', '.join(missing)}，正在补装...")
                skill_root = get_skill_root()
                core_req = skill_root / "requirements.txt"
                cnki_req = skill_root / "scripts" / "cnki" / "requirements.txt"
                if core_req.exists():
                    install_in_venv(core_req)
                if cnki_req.exists():
                    install_in_venv(cnki_req)
            # 确保浏览器已安装
            install_playwright_browsers_in_venv()
        except Exception as exc:
            print(f"检查 venv 依赖时出错：{exc}")
        return

    skill_root = get_skill_root()
    venv_python = get_venv_python()

    # 如果 venv 不存在，创建并安装
    if not venv_python.exists():
        print("EMARX 虚拟环境未就绪，正在自动配置...")
        if not create_venv():
            print("创建虚拟环境失败")
            sys.exit(1)

    # 无论 venv 是否刚创建，都确保依赖完整
    core_req = skill_root / "requirements.txt"
    cnki_req = skill_root / "scripts" / "cnki" / "requirements.txt"

    if core_req.exists() and not install_in_venv(core_req):
        print("安装核心依赖失败")
        sys.exit(1)

    if cnki_req.exists() and not install_in_venv(cnki_req):
        print("安装 CNKI 依赖失败")
        sys.exit(1)

    if not install_playwright_browsers_in_venv():
        print("安装浏览器失败")
        sys.exit(1)

    print("EMARX 虚拟环境配置完成")

    # 用 venv 的 Python 重新执行当前脚本
    new_env = os.environ.copy()
    new_env[ENV_MARKER] = "1"
    new_env["PATH"] = str(venv_python.parent) + os.pathsep + os.environ.get("PATH", "")

    cmd = [str(venv_python)] + sys.argv
    print(f"切换到虚拟环境运行：{' '.join(cmd)}")
    result = subprocess.run(cmd, env=new_env)
    sys.exit(result.returncode)
