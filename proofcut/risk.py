"""Fail-visible source-support checks for candidate copy."""

from __future__ import annotations

import re
from typing import Any

from .text import normalize, tokens


NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_.])\d+(?:\.\d+)?%?(?![A-Za-z0-9_.])")
TIME_RANGE_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[–-]\s*\d{1,2}:\d{2}(?::\d{2})?)?\b")
ABSOLUTES = ("100%", "唯一", "保证", "绝对", "完全消除", "zero risk", "always", "never fails")
WRAPPER_TOKENS = {
    "原话证据", "来源", "source", "evidence", "重点", "关键词", "画面", "使用", "中性",
    "文字", "添加", "统计", "不加", "timestamp", "neutral", "text", "statistics",
    "原话", "话证", "证据", "不添", "添加", "加原", "原文", "文外", "外的", "的数",
    "数字", "字或", "或结", "结论", "使用", "用中", "中性", "性文", "文字",
}


def assess_claim(claim: str, source_text: str) -> dict[str, Any]:
    clean_claim = normalize(claim)
    clean_source = normalize(source_text)
    source_lower = clean_source.lower()
    claim_numbers = NUMBER_RE.findall(TIME_RANGE_RE.sub("", clean_claim))
    source_numbers = set(NUMBER_RE.findall(clean_source))
    risk_codes: list[str] = []
    missing_numbers = sorted({number for number in claim_numbers if number not in source_numbers})
    if missing_numbers:
        risk_codes.append("UNSUPPORTED_NUMBER")
    unsupported_absolutes = [term for term in ABSOLUTES if term.lower() in clean_claim.lower() and term.lower() not in source_lower]
    if unsupported_absolutes:
        risk_codes.append("UNSUPPORTED_ABSOLUTE")

    claim_terms = {term for term in tokens(clean_claim) if term not in WRAPPER_TOKENS}
    source_terms = set(tokens(clean_source))
    matched_terms = sorted(claim_terms & source_terms)
    overlap = len(matched_terms) / len(claim_terms) if claim_terms else 1.0
    if claim_terms and overlap < 0.45:
        risk_codes.append("LOW_SOURCE_OVERLAP")
    supported = not risk_codes
    return {
        "claim": clean_claim,
        "supported": supported,
        "risk_codes": risk_codes,
        "missing_numbers": missing_numbers,
        "term_overlap": round(overlap, 6),
        "matched_terms": matched_terms,
    }
