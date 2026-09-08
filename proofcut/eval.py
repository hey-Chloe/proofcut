"""Independent local evaluation over frozen self-authored fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from .export import canonical_json
from .io import load_transcript
from .pipeline import build_content_pack
from .risk import assess_claim


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def evaluate_fixture(path: Path) -> dict[str, Any]:
    transcript = load_transcript(path)
    first = build_content_pack(transcript)
    second = build_content_pack(transcript)
    first_bytes = canonical_json(first).encode("utf-8")
    second_bytes = canonical_json(second).encode("utf-8")
    utterances = transcript["utterances"]
    span_pass = 0
    field_total = 0
    field_present = 0
    generated_supported = 0
    generated_total = 0
    for segment in first["segments"]:
        span = segment["source_span"]
        selected = utterances[span["utterance_start"]:span["utterance_end"] + 1]
        expected_quote = " ".join(item["text"] for item in selected)
        if (
            selected
            and span["start_ms"] == selected[0]["start_ms"]
            and span["end_ms"] == selected[-1]["end_ms"]
            and span["quote"] == expected_quote
        ):
            span_pass += 1
        for field in ("hook", "title", "caption", "seo_keywords", "thumbnail_brief"):
            field_total += 1
            field_present += bool(segment["content"].get(field, "").strip())
        for item in segment["risk_gate"]["fields"].values():
            generated_total += 1
            generated_supported += bool(item["supported"])

    probe_tp = probe_fp = probe_fn = probe_tn = 0
    source_text = " ".join(item["text"] for item in utterances)
    probe_results = []
    for probe in transcript.get("risk_probes", []):
        result = assess_claim(probe["text"], source_text)
        expected_supported = bool(probe["expected_supported"])
        predicted_unsupported = not result["supported"]
        expected_unsupported = not expected_supported
        if predicted_unsupported and expected_unsupported:
            probe_tp += 1
        elif predicted_unsupported and not expected_unsupported:
            probe_fp += 1
        elif not predicted_unsupported and expected_unsupported:
            probe_fn += 1
        else:
            probe_tn += 1
        probe_results.append({"text": probe["text"], "expected_supported": expected_supported, "result": result})

    return {
        "fixture": path.name,
        "fixture_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pack_sha256": hashlib.sha256(first_bytes).hexdigest(),
        "deterministic_byte_equal": first_bytes == second_bytes,
        "segment_count": len(first["segments"]),
        "span_pass": span_pass,
        "span_total": len(first["segments"]),
        "field_present": field_present,
        "field_total": field_total,
        "generated_supported": generated_supported,
        "generated_total": generated_total,
        "probe_confusion": {"tp": probe_tp, "fp": probe_fp, "fn": probe_fn, "tn": probe_tn},
        "probe_results": probe_results,
    }


def evaluate_directory(fixtures_dir: str | Path) -> dict[str, Any]:
    paths = sorted(Path(fixtures_dir).glob("*.json"))
    if len(paths) < 6:
        raise ValueError("evaluation requires at least six frozen JSON fixtures")
    records = [evaluate_fixture(path) for path in paths]
    aggregate = {
        "fixture_count": len(records),
        "segment_count": sum(item["segment_count"] for item in records),
        "deterministic_fixture_count": sum(item["deterministic_byte_equal"] for item in records),
        "span_pass": sum(item["span_pass"] for item in records),
        "span_total": sum(item["span_total"] for item in records),
        "field_present": sum(item["field_present"] for item in records),
        "field_total": sum(item["field_total"] for item in records),
        "generated_supported": sum(item["generated_supported"] for item in records),
        "generated_total": sum(item["generated_total"] for item in records),
        "probe_tp": sum(item["probe_confusion"]["tp"] for item in records),
        "probe_fp": sum(item["probe_confusion"]["fp"] for item in records),
        "probe_fn": sum(item["probe_confusion"]["fn"] for item in records),
        "probe_tn": sum(item["probe_confusion"]["tn"] for item in records),
    }
    metrics = {
        "determinism_rate": _ratio(aggregate["deterministic_fixture_count"], aggregate["fixture_count"]),
        "source_span_validity": _ratio(aggregate["span_pass"], aggregate["span_total"]),
        "generated_field_completeness": _ratio(aggregate["field_present"], aggregate["field_total"]),
        "supported_generated_field_rate": _ratio(aggregate["generated_supported"], aggregate["generated_total"]),
        "unsupported_generated_field_rate": round(1 - _ratio(aggregate["generated_supported"], aggregate["generated_total"]), 6),
        "risk_probe_recall": _ratio(aggregate["probe_tp"], aggregate["probe_tp"] + aggregate["probe_fn"]),
        "risk_probe_precision": _ratio(aggregate["probe_tp"], aggregate["probe_tp"] + aggregate["probe_fp"]),
        "supported_probe_specificity": _ratio(aggregate["probe_tn"], aggregate["probe_tn"] + aggregate["probe_fp"]),
    }
    status = "PASS" if all(value == 1.0 for key, value in metrics.items() if key != "unsupported_generated_field_rate") and metrics["unsupported_generated_field_rate"] == 0.0 else "FAIL"
    return {
        "schema_version": "proofcut-eval-report-v1",
        "status": status,
        "scope": "SELF_AUTHORED_FROZEN_FIXTURES_LOCAL_OFFLINE_ONLY",
        "aggregate": aggregate,
        "metrics": metrics,
        "fixtures": records,
        "claim_boundary": "No user study, creator time saving, production traffic, external model quality, or competition outcome is measured.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate ProofCut on frozen fixtures.")
    parser.add_argument("--fixtures", default="fixtures")
    parser.add_argument("--output", default="outputs/eval_report.json")
    args = parser.parse_args(argv)
    report = evaluate_directory(args.fixtures)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "metrics": report["metrics"], "output": str(output)}, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
