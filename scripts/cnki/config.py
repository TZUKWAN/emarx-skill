"""Configuration loader."""

import os
from pathlib import Path


def _env(key: str, default=None):
    return os.environ.get(key, default)


def _env_bool(key: str, default: bool = False) -> bool:
    val = _env(key, str(default).lower())
    return val.lower() in ("1", "true", "yes", "on")


def _env_float(key: str, default: float) -> float:
    try:
        return float(_env(key, default))
    except ValueError:
        return default


def _env_int(key: str, default: int) -> int:
    try:
        return int(_env(key, default))
    except ValueError:
        return default


# EMARX 集成修改：默认把工作目录设为当前运行目录（而不是 scripts/cnki 上级），
# 这样 storage_state 和 downloads 会落在 EMARX 工作空间或用户指定的目录。
PROJECT_ROOT = Path(_env("CNKI_PROJECT_ROOT", Path.cwd()))

STORAGE_STATE_PATH = Path(_env("CNKI_STORAGE_STATE", PROJECT_ROOT / ".cnki_storage_state.json"))
DOWNLOAD_DIR = Path(_env("CNKI_DOWNLOAD_DIR", PROJECT_ROOT / "downloads"))
HEADLESS = _env_bool("CNKI_HEADLESS", True)
REMOTE_DEBUGGING_URL = _env("CNKI_REMOTE_DEBUGGING_URL", "http://localhost:9222")
USER_DATA_DIR = _env("CNKI_USER_DATA_DIR", "")
CDP_CONNECT = _env_bool("CNKI_CDP_CONNECT", False)

CAPTCHA_SOLVER = _env("CAPTCHA_SOLVER", "local")  # local | 2captcha
TWOCAPTCHA_API_KEY = _env("TWOCAPTCHA_API_KEY", "")

DELAY_MIN = _env_float("CNKI_DELAY_MIN", 2.0)
DELAY_MAX = _env_float("CNKI_DELAY_MAX", 5.0)
MAX_PAGES = _env_int("CNKI_MAX_PAGES", 10)
RESULTS_PER_PAGE = _env_int("CNKI_RESULTS_PER_PAGE", 20)

CNKI_FILTER_CORE = _env_bool("CNKI_FILTER_CORE", True)
CNKI_FILTER_CSSCI = _env_bool("CNKI_FILTER_CSSCI", True)

CNKI_HOME = "https://www.cnki.net"
CNKI_KNS = "https://kns.cnki.net"
CNKI_SEARCH_URL = "https://kns.cnki.net/kns8s/defaultresult/index"
CNKI_BRIEF_URL = "https://kns.cnki.net/kns8s/brief"
