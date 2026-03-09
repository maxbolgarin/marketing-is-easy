from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def slugify(value: str, fallback: str = "run") -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or fallback


def timestamp_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def dump_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def nearest_supported_video_seconds(seconds: int) -> str:
    supported = [4, 8, 12]
    nearest = min(supported, key=lambda s: abs(s - seconds))
    return str(nearest)


def poll_until(predicate, *, timeout_sec: int = 1800, interval_sec: int = 10):
    start = time.time()
    while True:
        result = predicate()
        if result is not None:
            return result
        if time.time() - start > timeout_sec:
            raise TimeoutError("Timed out while polling job status.")
        time.sleep(interval_sec)
