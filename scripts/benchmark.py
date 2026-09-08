"""Measure local deterministic pipeline latency without external I/O."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from proofcut.export import canonical_json  # noqa: E402
from proofcut.io import load_transcript  # noqa: E402
from proofcut.pipeline import build_content_pack  # noqa: E402


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((len(ordered) - 1) * fraction))))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", default="fixtures")
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--output", default="outputs/benchmark_report.json")
    args = parser.parse_args()
    fixture_paths = sorted((ROOT / args.fixtures).glob("*.json"))
    transcripts = [load_transcript(path) for path in fixture_paths]
    durations_ms: list[float] = []
    output_bytes = 0
    for _ in range(args.iterations):
        started = time.perf_counter_ns()
        packs = [build_content_pack(transcript) for transcript in transcripts]
        elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
        durations_ms.append(elapsed_ms)
        output_bytes = sum(len(canonical_json(pack).encode("utf-8")) for pack in packs)
    report = {
        "schema_version": "proofcut-local-benchmark-v1",
        "scope": "SIX_SELF_AUTHORED_FIXTURES_IN_MEMORY_LOCAL_MACHINE_ONLY",
        "fixture_count": len(transcripts),
        "iterations": args.iterations,
        "total_pipeline_runs": len(transcripts) * args.iterations,
        "median_batch_ms": round(statistics.median(durations_ms), 6),
        "p95_batch_ms": round(percentile(durations_ms, 0.95), 6),
        "min_batch_ms": round(min(durations_ms), 6),
        "max_batch_ms": round(max(durations_ms), 6),
        "output_bytes_per_six_fixture_batch": output_bytes,
        "fixture_set_sha256": hashlib.sha256("".join(hashlib.sha256(path.read_bytes()).hexdigest() for path in fixture_paths).encode()).hexdigest(),
        "claim_boundary": "Not a production throughput, model latency, network latency, or user time-saving measurement."
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
