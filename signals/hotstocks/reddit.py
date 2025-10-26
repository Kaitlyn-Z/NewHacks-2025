import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


BASE = "https://www.reddit.com"
USER_AGENT = "HotStocksPipeline/0.1 (by u/anonymous)"


def _http_get_json(url: str, params: Optional[Dict[str, str]] = None, retries: int = 3, sleep_s: float = 0.8):
    if params:
        url = f"{url}?{urlencode(params)}"
    last_err = None
    for i in range(retries):
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    raise HTTPError(url, resp.status, resp.reason, resp.headers, None)
                return json.loads(resp.read().decode("utf-8", errors="ignore"))
        except (HTTPError, URLError, TimeoutError) as e:
            last_err = e
            time.sleep(sleep_s * (1 + i))
    if last_err:
        raise last_err


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def fetch_recent_posts(sub: str, lookback_hours: int = 24, limit: int = 100) -> List[Dict]:
    """
    Fetch recent posts for a subreddit via public JSON. Stops at lookback window or after limit.
    """
    collected: List[Dict] = []
    after: Optional[str] = None
    window_start = _now_utc() - timedelta(hours=lookback_hours)
    fetched = 0

    while fetched < limit:
        page_limit = min(100, limit - fetched)
        params = {"limit": str(page_limit)}
        if after:
            params["after"] = after
        url = f"{BASE}/r/{sub}/new.json"
        data = _http_get_json(url, params)
        children = (data or {}).get("data", {}).get("children", [])
        if not children:
            break
        for ch in children:
            d = ch.get("data", {})
            created_utc = d.get("created_utc")
            if created_utc is None:
                continue
            created_dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
            if created_dt < window_start:
                # Stop early if we've reached outside the window
                return collected
            post = {
                "id": d.get("id"),
                "title": d.get("title"),
                "selftext": d.get("selftext"),
                "score": d.get("score"),
                "num_comments": d.get("num_comments"),
                "permalink": d.get("permalink"),
                "subreddit": d.get("subreddit"),
                "created_utc": created_utc,
            }
            collected.append(post)
            fetched += 1
            if fetched >= limit:
                break
        after = (data or {}).get("data", {}).get("after")
        if not after:
            break
        time.sleep(0.5)
    return collected


def _walk_comments(nodes: Iterable[Dict], out: List[str], limit: int) -> None:
    for n in nodes:
        if len(out) >= limit:
            return
        kind = n.get("kind")
        if kind != "t1":  # comment
            # may be more comments or listings
            d = n.get("data", {})
            if d.get("children"):
                _walk_comments(d.get("children"), out, limit)
            continue
        d = n.get("data", {})
        body = d.get("body")
        if body:
            out.append(body)
        # recurse replies
        replies = d.get("replies")
        if isinstance(replies, dict):
            _walk_comments(replies.get("data", {}).get("children", []), out, limit)


def fetch_comments_for_post(permalink: str, limit: int = 200) -> List[str]:
    """
    Fetch a subset of comments for a post via public JSON, returns bodies.
    """
    if not permalink:
        return []
    url = f"{BASE}{permalink}.json"
    data = _http_get_json(url, params={"sort": "top", "limit": str(min(500, limit))})
    if not isinstance(data, list) or len(data) < 2:
        return []
    comments_listing = data[1]
    children = (comments_listing or {}).get("data", {}).get("children", [])
    bodies: List[str] = []
    _walk_comments(children, bodies, limit)
    return bodies

