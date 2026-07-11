"""Captcha solving helpers."""

import base64
import io
import random
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from .utils import random_delay


def _pil_to_cv(img: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


class CaptchaSolver(ABC):
    @abstractmethod
    def solve_image(self, image: Image.Image) -> str:
        """Return text from an image captcha."""

    @abstractmethod
    def solve_slider(
        self, background: Image.Image, slider: Image.Image
    ) -> int:
        """Return horizontal offset for a slider captcha."""


class LocalCaptchaSolver(CaptchaSolver):
    """Local OCR + OpenCV slider solver."""

    def __init__(self):
        self._ocr = None

    def _get_ocr(self):
        if self._ocr is None:
            import ddddocr

            self._ocr = ddddocr.DdddOcr(show_ad=False)
        return self._ocr

    def solve_image(self, image: Image.Image) -> str:
        ocr = self._get_ocr()
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="PNG")
        result = ocr.classification(buf.getvalue())
        return result or ""

    def solve_slider(
        self, background: Image.Image, slider: Image.Image
    ) -> int:
        bg_cv = _pil_to_cv(background)
        slider_cv = _pil_to_cv(slider)

        # Convert to grayscale
        bg_gray = cv2.cvtColor(bg_cv, cv2.COLOR_BGR2GRAY)
        slider_gray = cv2.cvtColor(slider_cv, cv2.COLOR_BGR2GRAY)

        # Remove alpha channel if present by using only the mask
        if slider.mode == "RGBA":
            alpha = np.array(slider)[:, :, 3]
            _, mask = cv2.threshold(alpha, 128, 255, cv2.THRESH_BINARY)
            slider_gray = cv2.bitwise_and(slider_gray, slider_gray, mask=mask)

        # Template matching to find slider position
        result = cv2.matchTemplate(bg_gray, slider_gray, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val < 0.3:
            raise RuntimeError(f"Slider match confidence too low: {max_val}")
        return max_loc[0]


class TwoCaptchaSolver(CaptchaSolver):
    """Optional 2captcha integration (requires API key)."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def solve_image(self, image: Image.Image) -> str:
        import requests

        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        resp = requests.post(
            "http://2captcha.com/in.php",
            data={
                "key": self.api_key,
                "method": "base64",
                "body": b64,
                "json": 1,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != 1:
            raise RuntimeError(f"2captcha error: {data}")
        captcha_id = data["request"]
        # Poll for result
        for _ in range(30):
            time.sleep(5)
            res = requests.get(
                f"http://2captcha.com/res.php?key={self.api_key}&action=get&id={captcha_id}&json=1",
                timeout=30,
            )
            res.raise_for_status()
            rdata = res.json()
            if rdata.get("status") == 1:
                return rdata["request"]
            if rdata.get("request") == "CAPCHA_NOT_READY":
                continue
            raise RuntimeError(f"2captcha error: {rdata}")
        raise RuntimeError("2captcha timeout")

    def solve_slider(
        self, background: Image.Image, slider: Image.Image
    ) -> int:
        # 2captcha supports different methods; keep local fallback for now.
        raise NotImplementedError("Use local slider solver or implement 2captcha geetest method")


def create_solver(solver_type: str, api_key: Optional[str] = None) -> CaptchaSolver:
    if solver_type == "2captcha":
        if not api_key:
            raise ValueError("2captcha solver requires TWOCAPTCHA_API_KEY")
        return TwoCaptchaSolver(api_key)
    return LocalCaptchaSolver()


def solve_block_puzzle(original_b64: str, jigsaw_b64: str) -> int:
    """Solve CNKI block-puzzle captcha by masked normalized cross-correlation.

    The function expects two base64-encoded PNG images from the CNKI verify
    API or DOM: the full background (310x155) and the jigsaw mask strip
    (47x155) with an opaque puzzle piece. It returns the horizontal offset
    in original-image pixels where the puzzle piece should be placed.
    """
    bg = np.array(Image.open(io.BytesIO(base64.b64decode(original_b64))))
    jg = np.array(Image.open(io.BytesIO(base64.b64decode(jigsaw_b64))))

    if jg.shape[2] != 4:
        raise ValueError("Jigsaw image must have an alpha channel")

    alpha = jg[:, :, 3]
    _, mask = cv2.threshold(alpha, 128, 255, cv2.THRESH_BINARY)
    ys, xs = np.where(mask > 128)
    if xs.size == 0:
        raise RuntimeError("Empty jigsaw mask")

    x0, y0 = int(xs.min()), int(ys.min())
    x1, y1 = int(xs.max()) + 1, int(ys.max()) + 1
    piece = jg[y0:y1, x0:x1, :3]
    mask_c = mask[y0:y1, x0:x1]

    h, w = bg.shape[:2]
    ph, pw = piece.shape[:2]
    if ph > h or pw > w:
        raise RuntimeError(f"Jigsaw piece {piece.shape} larger than background {bg.shape}")

    best_ncc = -1.0
    best_x = 0
    # Search over all possible placements; pieces can appear at any y.
    for y in range(0, h - ph + 1):
        for x in range(0, w - pw + 1):
            roi = bg[y:y + ph, x:x + pw].astype(float)
            vals = []
            for c in range(3):
                a = roi[:, :, c][mask_c > 128]
                b = piece[:, :, c][mask_c > 128]
                if a.size == 0 or b.size == 0 or a.std() == 0 or b.std() == 0:
                    continue
                vals.append(float(np.corrcoef(a, b)[0, 1]))
            score = float(np.mean(vals)) if vals else -1.0
            if score > best_ncc:
                best_ncc = score
                best_x = x

    if best_ncc < 0.3:
        raise RuntimeError(f"Block-puzzle match confidence too low: {best_ncc}")
    return best_x


def solve_block_puzzle_from_images(original: Image.Image, jigsaw: Image.Image) -> int:
    """Convenience wrapper that accepts PIL images."""
    def _to_b64(img: Image.Image) -> str:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    return solve_block_puzzle(_to_b64(original), _to_b64(jigsaw))


def human_like_drag(page, handle, offset_x: int, duration: float = 0.6):
    """Drag a slider handle by offset_x with random jitter."""
    box = handle.bounding_box()
    if not box:
        raise RuntimeError("Cannot get slider handle bounding box")
    start_x = int(box["x"] + box["width"] / 2)
    start_y = int(box["y"] + box["height"] / 2)
    page.mouse.move(start_x, start_y)
    random_delay(0.1, 0.3)
    page.mouse.down()
    steps = max(10, int(duration * 40))
    for i in range(1, steps + 1):
        t = i / steps
        # Add random overshoot and jitter
        current_offset = offset_x * (t + random.uniform(-0.02, 0.02))
        current_offset = max(0, min(offset_x, current_offset))
        cx = start_x + int(current_offset) + random.randint(-2, 2)
        cy = start_y + random.randint(-2, 2)
        page.mouse.move(cx, cy)
        time.sleep(duration / steps)
    page.mouse.up()
    random_delay(0.3, 0.8)


def save_captcha_debug(background: Image.Image, slider: Optional[Image.Image], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    background.save(path)
    if slider:
        slider.save(path.with_suffix(".slider.png"))
