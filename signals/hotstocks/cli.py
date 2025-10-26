import argparse
import traceback
from .config import load_config
from .reddit import fetch_recent_posts, fetch_comments_for_post
from .tickers import extract_tickers
from .hotness import aggregate_and_score
from .io import write_output


def run_pipeline(cfg: dict) -> dict:
    subs = cfg["subs"]
    lookback_hours = int(cfg.get("lookback_hours", 240))
    limits = cfg.get("limits", {})
    posts_per_sub = int(limits.get("posts_per_sub", 100))
    comments_per_post = int(limits.get("comments_per_post", 200))
    weights = cfg.get("weights", {"mentions": 1.0, "upvotes": 0.1, "comments": 0.2})
    threshold = float(cfg.get("threshold", 750.0))
    permalinks_per_ticker = int(cfg.get("permalinks_per_ticker", 3))
    whitelist = set(map(str.upper, cfg.get("ticker_whitelist", []))) or None
    blacklist = set(map(str.upper, cfg.get("ticker_blacklist", [])))

    all_posts = []
    for sub in subs:
        posts = fetch_recent_posts(sub, lookback_hours=lookback_hours, limit=posts_per_sub)
        all_posts.extend(posts)

    # Extract tickers from post title/selftext and comments
    post_level_tickers = {}  # post_id -> set(tickers) found in post content
    mention_counts = {}  # ticker -> total mentions across posts+comments
    post_metrics = {}  # post_id -> dict of fields (score, num_comments, permalink)

    for p in all_posts:
        post_id = p.get("id")
        title = p.get("title") or ""
        body = p.get("selftext") or ""
        merged = f"{title}\n{body}"
        tickers_in_post = extract_tickers(merged, whitelist=whitelist, blacklist=blacklist)
        if tickers_in_post:
            post_level_tickers[post_id] = tickers_in_post
        # Mentions in post content counted as occurrences
        for t, cnt in extract_tickers(merged, whitelist=whitelist, blacklist=blacklist, count_occurrences=True).items():
            mention_counts[t] = mention_counts.get(t, 0) + cnt
        post_metrics[post_id] = {
            "score": int(p.get("score") or 0),
            "num_comments": int(p.get("num_comments") or 0),
            "permalink": p.get("permalink"),
        }

    # Fetch and scan comments per post (limited)
    for p in all_posts:
        post_id = p.get("id")
        permalink = p.get("permalink")
        try:
            comments = fetch_comments_for_post(permalink, limit=comments_per_post)
        except Exception:
            comments = []
        for c in comments:
            for t, cnt in extract_tickers(c, whitelist=whitelist, blacklist=blacklist, count_occurrences=True).items():
                mention_counts[t] = mention_counts.get(t, 0) + cnt

    scored = aggregate_and_score(
        all_posts=all_posts,
        post_level_tickers=post_level_tickers,
        mention_counts=mention_counts,
        post_metrics=post_metrics,
        weights=weights,
        permalinks_per_ticker=permalinks_per_ticker,
    )

    # Apply threshold
    items = [
        {
            "ticker": t,
            "hotness": round(m["hotness"], 6),
            "mentions": int(m.get("mentions", 0)),
            "total_upvotes": int(m.get("upvotes", 0)),
            "total_comments": int(m.get("comments", 0)),
            "permalinks": m.get("permalinks", []),
        }
        for t, m in scored.items()
        if m.get("hotness", 0.0) >= threshold
    ]
    # Sort by hotness desc
    items.sort(key=lambda x: x["hotness"], reverse=True)

    return {
        "window_hours": lookback_hours,
        "threshold": threshold,
        "items": items,
        "all_count": len(scored),
    }


def get_hot_tickers(cfg: dict) -> list[str]:
    return [it["ticker"] for it in run_pipeline(cfg)["items"]]


def find_posts_with_tickers(cfg: dict, tickers: list[str]) -> list[dict]:
    """
    Return recent Reddit posts that mention any of the given tickers.
    Each item includes subreddit, title, tickers_found, score, num_comments, and permalink.
    """
    subs = cfg["subs"]
    lookback_hours = int(cfg.get("lookback_hours", 240))
    limits = cfg.get("limits", {})
    posts_per_sub = int(limits.get("posts_per_sub", 100))

    # Normalize tickers for matching
    whitelist = set(t.upper() for t in tickers)
    blacklist = set(map(str.upper, cfg.get("ticker_blacklist", [])))

    all_posts = []
    for sub in subs:
        posts = fetch_recent_posts(sub, lookback_hours=lookback_hours, limit=posts_per_sub)
        all_posts.extend(posts)

    results = []
    for p in all_posts:
        title = p.get("title") or ""
        body = p.get("selftext") or ""
        merged = f"{title}\n{body}"

        # Only find tickers from your provided list
        found = extract_tickers(merged, whitelist=whitelist, blacklist=blacklist)
        if found:
            results.append({
                "subreddit": p.get("subreddit"),
                "title": title.strip(),
                "tickers_found": list(found),
                "score": int(p.get("score") or 0),
                "num_comments": int(p.get("num_comments") or 0),

            })
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description="Reddit hot stocks pipeline")
    parser.add_argument(
        "--config",
        default="signals/hotstocks/config.local.json",
        help="Path to local config JSON (default: signals/hotstocks/config.local.json)",
    )
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
        result = run_pipeline(cfg)
        output_path = cfg.get("output_path", "data/hotstocks.json")
        write_output(output_path, result)
        print(f"Wrote output: {output_path}")
        if not result["items"]:
            print("No tickers met the threshold. See message in JSON artifact.")
        return 0
    except Exception as e:
        print("Pipeline failed:", str(e))
        traceback.print_exc()
        # Attempt to write a failure artifact if possible
        try:
            write_output(
                "data/hotstocks.json",
                {
                    "window_hours": None,
                    "threshold": None,
                    "items": [],
                    "message": f"Pipeline error: {e}",
                },
            )
        except Exception:
            pass
        return 1
