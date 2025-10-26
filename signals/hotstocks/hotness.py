from typing import Dict, List, Set, Tuple


def aggregate_and_score(
    *,
    all_posts: List[dict],
    post_level_tickers: Dict[str, Set[str]],
    mention_counts: Dict[str, int],
    post_metrics: Dict[str, dict],
    weights: Dict[str, float],
    permalinks_per_ticker: int = 3,
) -> Dict[str, dict]:
    """
    Aggregate per-ticker metrics and compute hotness.
    - mentions: total occurrences across posts + comments
    - upvotes/comments: sum per post that mentions the ticker (title/selftext)
    - permalinks: top post permalinks by score for that ticker
    """
    per_ticker = {t: {"mentions": c, "upvotes": 0, "comments": 0, "permalinks": []} for t, c in mention_counts.items()}

    # Gather per-ticker post-based metrics
    posts_by_id = {p.get("id"): p for p in all_posts}
    for pid, tickers in post_level_tickers.items():
        met = post_metrics.get(pid, {})
        score = int(met.get("score") or 0)
        ncom = int(met.get("num_comments") or 0)
        link = met.get("permalink")
        for t in tickers:
            if t not in per_ticker:
                per_ticker[t] = {"mentions": 0, "upvotes": 0, "comments": 0, "permalinks": []}
            per_ticker[t]["upvotes"] += score
            per_ticker[t]["comments"] += ncom
            if link:
                per_ticker[t]["permalinks"].append((score, link))

    # Keep top permalinks and compute hotness
    w_mentions = float(weights.get("mentions", 1.0))
    w_upvotes = float(weights.get("upvotes", 0.01))
    w_comments = float(weights.get("comments", 0.05))

    result: Dict[str, dict] = {}
    for t, m in per_ticker.items():
        links: List[Tuple[int, str]] = m.get("permalinks", [])
        links.sort(key=lambda x: x[0], reverse=True)
        pl = [l for _, l in links[:permalinks_per_ticker]]
        mentions = int(m.get("mentions", 0))
        upvotes = int(m.get("upvotes", 0))
        comments = int(m.get("comments", 0))
        hotness = w_mentions * mentions + w_upvotes * upvotes + w_comments * comments
        result[t] = {
            "mentions": mentions,
            "upvotes": upvotes,
            "comments": comments,
            "hotness": float(hotness),
            "permalinks": pl,
        }
    return result

