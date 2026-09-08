"""Canonical JSON and CSV content-pack export."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


LEDGER_FIELDS = [
    "segment_id", "field", "candidate", "source_start_ms", "source_end_ms",
    "source_time_range", "source_utterance_start", "source_utterance_end",
    "source_quote", "supported", "risk_codes", "term_overlap", "transcript_sha256",
]


def canonical_json(pack: dict[str, Any]) -> str:
    return json.dumps(pack, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_exports(pack: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "content_pack.json"
    csv_path = target / "evidence_ledger.csv"
    json_path.write_text(canonical_json(pack), encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in pack["evidence_ledger"]:
            serializable = dict(row)
            serializable["risk_codes"] = "|".join(row["risk_codes"])
            writer.writerow(serializable)
    return json_path, csv_path
