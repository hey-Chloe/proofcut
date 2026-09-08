"""Small deterministic text helpers; no network or model dependency."""

from __future__ import annotations

import re
from collections import Counter


WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{1,}|[\u4e00-\u9fff]{2,}|\d+(?:\.\d+)?%?")
STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "your", "you", "are",
    "was", "were", "have", "has", "into", "about", "then", "when", "what",
    "我们", "这个", "可以", "不是", "一个", "以及", "但是", "然后", "因为", "所以",
    "需要", "进行", "已经", "没有", "内容", "项目", "今天", "现在",
}


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def tokens(value: str) -> list[str]:
    result: list[str] = []
    for match in WORD_RE.findall(value.lower()):
        if "\u4e00" <= match[0] <= "\u9fff":
            if match not in STOPWORDS:
                result.append(match)
                result.extend(match[index:index + 2] for index in range(max(0, len(match) - 1)))
        elif match not in STOPWORDS:
            result.append(match)
    return result


def top_terms(value: str, limit: int = 5) -> list[str]:
    counts = Counter(tokens(value))
    return [term for term, _ in sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:limit]]


def truncate(value: str, limit: int) -> str:
    clean = normalize(value)
    if len(clean) <= limit:
        return clean
    return clean[: max(1, limit - 1)].rstrip("，,。.!！?") + "…"


def format_ms(value: int) -> str:
    total_seconds = value // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"
