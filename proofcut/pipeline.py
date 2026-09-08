"""Deterministic transcript-to-content-pack pipeline."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from .risk import assess_claim
from .text import format_ms, normalize, tokens, top_terms, truncate


def _sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _adjacent_overlap(left: str, right: str) -> float:
    left_terms, right_terms = set(tokens(left)), set(tokens(right))
    union = left_terms | right_terms
    return len(left_terms & right_terms) / len(union) if union else 0.0


def segment_utterances(utterances: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Greedy topical segmentation with bounded, deterministic segment sizes."""
    groups: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for utterance in utterances:
        if current:
            overlap = _adjacent_overlap(current[-1]["text"], utterance["text"])
            boundary = len(current) >= 3 or (len(current) >= 2 and overlap < 0.035)
            if boundary:
                groups.append(current)
                current = []
        current.append(utterance)
    if current:
        if len(current) == 1 and groups and len(groups[-1]) < 4:
            groups[-1].extend(current)
        else:
            groups.append(current)
    return groups


def _content_for(source_text: str, terms: list[str], time_range: str) -> dict[str, str]:
    lead = truncate(source_text, 72)
    term_label = " · ".join(terms[:3]) if terms else "source evidence"
    return {
        "hook": f"原话证据：{lead}",
        "title": truncate(lead, 42),
        "caption": f"{truncate(source_text, 140)}（来源 {time_range}）",
        "seo_keywords": term_label,
        "thumbnail_brief": f"画面重点：{truncate(source_text, 80)}",
    }


def build_content_pack(transcript: dict[str, Any]) -> dict[str, Any]:
    utterances = transcript["utterances"]
    transcript_hash = _sha256_json(
        {"transcript_id": transcript["transcript_id"], "utterances": utterances}
    )
    segments: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    for ordinal, group in enumerate(segment_utterances(utterances), start=1):
        source_text = normalize(" ".join(item["text"] for item in group))
        start_ms, end_ms = group[0]["start_ms"], group[-1]["end_ms"]
        time_range = f"{format_ms(start_ms)}–{format_ms(end_ms)}"
        terms = top_terms(source_text)
        content = _content_for(source_text, terms, time_range)
        segment_id = f"{transcript['transcript_id']}-s{ordinal:02d}"
        field_risks: dict[str, Any] = {}
        for field, candidate in content.items():
            assessment = assess_claim(candidate, source_text)
            field_risks[field] = assessment
            ledger.append(
                {
                    "segment_id": segment_id,
                    "field": field,
                    "candidate": candidate,
                    "source_start_ms": start_ms,
                    "source_end_ms": end_ms,
                    "source_time_range": time_range,
                    "source_utterance_start": group[0]["index"],
                    "source_utterance_end": group[-1]["index"],
                    "source_quote": source_text,
                    "supported": assessment["supported"],
                    "risk_codes": assessment["risk_codes"],
                    "term_overlap": assessment["term_overlap"],
                    "transcript_sha256": transcript_hash,
                }
            )
        segments.append(
            {
                "segment_id": segment_id,
                "source_span": {
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "time_range": time_range,
                    "utterance_start": group[0]["index"],
                    "utterance_end": group[-1]["index"],
                    "quote": source_text,
                },
                "topic_terms": terms,
                "content": content,
                "risk_gate": {
                    "decision": "PASS" if all(item["supported"] for item in field_risks.values()) else "REVIEW",
                    "fields": field_risks,
                },
            }
        )
    unsupported_count = sum(not row["supported"] for row in ledger)
    return {
        "schema_version": "proofcut-content-pack-v1",
        "generator": {"name": "ProofCut", "version": "0.2.0", "mode": "deterministic_offline"},
        "transcript": {
            "transcript_id": transcript["transcript_id"],
            "title": transcript["title"],
            "language": transcript["language"],
            "timestamp_mode": transcript["timestamp_mode"],
            "sha256": transcript_hash,
            "utterance_count": len(utterances),
        },
        "segments": segments,
        "evidence_ledger": ledger,
        "summary": {
            "segment_count": len(segments),
            "ledger_row_count": len(ledger),
            "unsupported_generated_claim_count": unsupported_count,
            "release_decision": "PASS" if unsupported_count == 0 else "REVIEW",
            "claim_boundary": "LOCAL_DETERMINISTIC_FIXTURE_OR_USER_SUPPLIED_TRANSCRIPT_ONLY",
        },
    }
