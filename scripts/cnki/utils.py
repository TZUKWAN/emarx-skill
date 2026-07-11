"""Utility helpers."""

import random
import re
import time
from pathlib import Path
from typing import Optional


SAFE_FILENAME_RE = re.compile(r'[\\/:*?"<>|]')


def random_delay(min_sec: float = None, max_sec: float = None):
    """Sleep for a random duration to mimic human hesitation."""
    from . import config

    if min_sec is None:
        min_sec = config.DELAY_MIN
    if max_sec is None:
        max_sec = config.DELAY_MAX
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """Remove unsafe characters and limit length."""
    name = SAFE_FILENAME_RE.sub("_", name)
    name = re.sub(r"\s+", "_", name).strip("._")
    if len(name) > max_len:
        name = name[:max_len]
    return name or "unnamed"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_query_url(keyword: str) -> str:
    from . import config
    return f"{config.CNKI_SEARCH_URL}?kw={keyword}"


def try_float(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    try:
        return float(re.sub(r"[^\d.]", "", text))
    except ValueError:
        return None


def try_int(text: Optional[str]) -> Optional[int]:
    if not text:
        return None
    try:
        return int(re.sub(r"[^\d]", "", text))
    except ValueError:
        return None
