import json
import os
from datetime import datetime, timezone
from typing import Any, Dict


def _ensure_dir(path: str) -> None:
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)


def write_output(path: str, payload: Dict[str, Any]) -> None:
    """
    Write JSON under data/ with metadata. If items empty, include a clear message.
    """
    out = dict(payload)
    out["generated_at"] = datetime.now(timezone.utc).isoformat()
    if not out.get("items"):
        out.setdefault("message", "No hot tickers met the threshold within the lookback window.")
    _ensure_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

