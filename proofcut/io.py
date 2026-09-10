"""Input parsing for timestamped JSON and plain-text transcripts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


TIMESTAMPED_LINE = re.compile(
    r"^\s*\[(?P<start>\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*"
    r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?)\]\s*(?P<text>.+?)\s*$"
)
SENTENCE_SPLIT = re.compile(r"(?<=[。！？.!?])\s*|\n+")


def _clock_to_ms(value: str) -> int:
    parts = [int(part) for part in value.split(":")]
    if len(parts) == 2:
        minutes, seconds = parts
        return (minutes * 60 + seconds) * 1000
    hours, minutes, seconds = parts
    return (hours * 3600 + minutes * 60 + seconds) * 1000


def _validate_utterances(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not raw:
        raise ValueError("transcript must contain at least one utterance")
    utterances: list[dict[str, Any]] = []
    last_end = -1
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ValueError(f"utterance {index} must be an object")
        text = str(item.get("text", "")).strip()
        start_ms = item.get("start_ms")
        end_ms = item.get("end_ms")
        if not text:
            raise ValueError(f"utterance {index} has empty text")
        if not isinstance(start_ms, int) or not isinstance(end_ms, int):
            raise ValueError(f"utterance {index} needs integer start_ms/end_ms")
        if start_ms < 0 or end_ms <= start_ms:
            raise ValueError(f"utterance {index} has invalid time range")
        if start_ms < last_end:
            raise ValueError(f"utterance {index} overlaps or is out of order")
        utterances.append(
            {
                "index": index,
                "start_ms": start_ms,
                "end_ms": end_ms,
                "speaker": str(item.get("speaker", "speaker")),
                "text": text,
            }
        )
        last_end = end_ms
    return utterances


def parse_json_transcript(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("utterances"), list):
        raise ValueError("JSON transcript needs an utterances array")
    return {
        "transcript_id": str(payload.get("transcript_id") or path.stem),
        "title": str(payload.get("title") or path.stem),
        "language": str(payload.get("language") or "unknown"),
        "timestamp_mode": "source",
        "utterances": _validate_utterances(payload["utterances"]),
        "risk_probes": payload.get("risk_probes", []),
    }


def parse_text_transcript(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise ValueError("plain-text transcript is empty")
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    timestamped = [TIMESTAMPED_LINE.match(line) for line in lines]
    utterances: list[dict[str, Any]] = []
    if timestamped and all(timestamped):
        for match in timestamped:
            assert match is not None
            utterances.append(
                {
                    "start_ms": _clock_to_ms(match.group("start")),
                    "end_ms": _clock_to_ms(match.group("end")),
                    "text": match.group("text"),
                }
            )
        mode = "source"
    else:
        sentences = [chunk.strip() for chunk in SENTENCE_SPLIT.split(raw) if chunk.strip()]
        cursor_ms = 0
        for sentence in sentences:
            duration_ms = max(2000, min(15000, len(sentence) * 120))
            utterances.append(
                {"start_ms": cursor_ms, "end_ms": cursor_ms + duration_ms, "text": sentence}
            )
            cursor_ms += duration_ms
        mode = "estimated"
    return {
        "transcript_id": path.stem,
        "title": path.stem,
        "language": "unknown",
        "timestamp_mode": mode,
        "utterances": _validate_utterances(utterances),
        "risk_probes": [],
    }


def load_transcript(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".json":
        return parse_json_transcript(source)
    return parse_text_transcript(source)
