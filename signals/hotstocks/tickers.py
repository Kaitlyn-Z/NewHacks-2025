import re
from typing import Dict, Iterable, Optional, Set


_DOLLAR_TICKER = re.compile(r"\$([A-Za-z]{1,5})\b")
_BARE_TICKER = re.compile(r"\b([A-Z]{1,5})\b")

# Conservative stopwords to reduce obvious false positives.
_STOPWORDS: Set[str] = {
    "I", "A", "AN", "AND", "OR", "THE", "TO", "YOLO", "USA", "USD",
    "SEC", "CEO", "CFO", "ETF", "GDP", "CPI", "FOMC", "AI", "WSB",
    "S", "U", "US", "EDIT", "ALL", "ARE", "WITH", "VERY", "TRADE", 
    "FAKE", "OF", "EPS", "EPG", "DD", "RFK", "AMA", "CNBC", "P",
    "D", "BUT", "IIRC", "RIP"
}


def _normalize(candidate: str) -> Optional[str]:
    t = candidate.upper()
    if not (1 <= len(t) <= 5):
        return None
    if t in _STOPWORDS:
        return None
    return t


def extract_tickers(
    text: str,
    *,
    whitelist: Optional[Set[str]] = None,
    blacklist: Optional[Set[str]] = None,
    count_occurrences: bool = False,
):
    """
    Extract tickers from text.
    - Matches $AAPL style and bare uppercase up to 5 chars.
    - Applies stopwords and optional white/black lists.
    - When count_occurrences=True, returns dict of ticker->count.
    """
    if not text:
        return {} if count_occurrences else set()

    found: Iterable[str] = []
    dollar = [m.group(1) for m in _DOLLAR_TICKER.finditer(text)]
    bare = [m.group(1) for m in _BARE_TICKER.finditer(text)]
    found = list(dollar) + list(bare)

    def accept(sym: str) -> Optional[str]:
        s = _normalize(sym)
        if not s:
            return None
        if blacklist and s in blacklist:
            return None
        if whitelist is not None and s not in whitelist:
            return None
        return s

    if count_occurrences:
        counts: Dict[str, int] = {}
        for sym in found:
            s = accept(sym)
            if not s:
                continue
            counts[s] = counts.get(s, 0) + 1
        return counts

    out: Set[str] = set()
    for sym in found:
        s = accept(sym)
        if s:
            out.add(s)
    return out

