import json
import os
from typing import Any, Dict


DEFAULTS: Dict[str, Any] = {
    "subs": ["wallstreetbets", "stocks"],
    "lookback_hours": 240,
    "threshold": 0.0,
    "weights": {"mentions": 10.0, "upvotes": 0.1, "comments": 0.5},
    "limits": {"posts_per_sub": 100, "comments_per_post": 200},
    "output_path": "data/hotstocks.json",
    "permalinks_per_ticker": 3,
    "ticker_whitelist": [],
    "ticker_blacklist": [],
}


def load_config(path: str) -> Dict[str, Any]:
    # Prefer explicit path; if missing, try sample; then fall back to defaults
    cfg: Dict[str, Any] = {}
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        sample = os.path.join(os.path.dirname(__file__), "config.sample.json")
        if os.path.exists(sample):
            with open(sample, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        else:
            cfg = {}

    # Merge defaults
    merged = DEFAULTS.copy()
    for k, v in cfg.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            mv = merged[k].copy()
            mv.update(v)
            merged[k] = mv
        else:
            merged[k] = v

    # Basic validation
    if not merged.get("subs"):
        raise ValueError("Config must include non-empty 'subs' list")
    if not isinstance(merged.get("threshold"), (int, float)):
        raise ValueError("Config 'threshold' must be numeric")

    return merged

