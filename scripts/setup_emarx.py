# -*- coding: utf-8 -*-
"""
setup_emarx.py — EMARX 一键环境配置脚本。

自动创建 EMARX 专用虚拟环境并安装所有依赖，让用户安装 skill 后无需手动配置即可使用。

用法：
  python scripts/setup_emarx.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emarx_env import ensure_venv_and_reexec


def main():
    # 确保在 EMARX 虚拟环境中运行
    ensure_venv_and_reexec()

    print("=" * 60)
    print("EMARX 环境已就绪")
    print("=" * 60)
    print("现在可以运行：")
    print("  python scripts/cnki_cli.py search \"关键词\" --pages 3 --output workspace/cnki_results.json")


if __name__ == "__main__":
    main()
