"""Build a content-addressed local-only ProofCut MVP receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


INCLUDED = (
    "proofcut",
    "fixtures",
    "tests",
    "scripts",
    ".gitignore",
    "README.md",
    "PROVENANCE.md",
    "CLAIM_BOUNDARY.md",
    "DESIGN_BRIEF.md",
    "DEVPOST_SUBMISSION.md",
    "DEMO_SCRIPT_90S.md",
    "OFFICIAL_REQUIREMENTS_SNAPSHOT.md",
    "VISUAL_QA_REPORT.md",
    "pyproject.toml",
    "LICENSE",
)


def files(root: Path):
    for name in INCLUDED:
        path = root / name
        if path.is_file():
            yield path
        elif path.is_dir():
            yield from sorted(item for item in path.rglob("*") if item.is_file() and "__pycache__" not in item.parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval", default="outputs/eval_report.json")
    parser.add_argument("--benchmark", default="outputs/benchmark_report.json")
    parser.add_argument("--package-smoke", default="outputs/PACKAGE_SMOKE.json")
    parser.add_argument("--output", default="outputs/LOCAL_MVP_RECEIPT.json")
    parser.add_argument("--manifest", default="outputs/MANIFEST.sha256")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    records = []
    for path in files(root):
        data = path.read_bytes()
        records.append({"path": path.relative_to(root).as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest_text = "".join(f"{item['sha256']}  {item['path']}\n" for item in records)
    eval_path = root / args.eval
    evaluation = json.loads(eval_path.read_text(encoding="utf-8"))
    benchmark_path = root / args.benchmark
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    package_smoke_path = root / args.package_smoke
    package_smoke = json.loads(package_smoke_path.read_text(encoding="utf-8"))
    receipt = {
        "schema_version": "proofcut-local-mvp-receipt-v1",
        "scope": "LOCAL_DETERMINISTIC_OFFLINE_ONLY",
        "status": "PASS" if evaluation["status"] == "PASS" and package_smoke.get("status") == "PASS" else "FAIL",
        "file_count": len(records),
        "manifest_sha256": hashlib.sha256(manifest_text.encode()).hexdigest(),
        "eval_report_sha256": hashlib.sha256(eval_path.read_bytes()).hexdigest(),
        "benchmark_report_sha256": hashlib.sha256(benchmark_path.read_bytes()).hexdigest(),
        "package_smoke_report_sha256": hashlib.sha256(package_smoke_path.read_bytes()).hexdigest(),
        "metrics": evaluation["metrics"],
        "benchmark": benchmark,
        "package_smoke": package_smoke,
        "claim_boundary": {
            "registration": "NOT_PERFORMED",
            "paid_api": "NOT_CALLED",
            "deployment": "NOT_DEPLOYED",
            "public_repository": "NOT_CREATED",
            "official_submission": "NOT_SUBMITTED",
            "competition_result": "UNCLAIMED"
        },
        "files": records,
    }
    manifest_path = root / args.manifest
    output_path = root / args.output
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(manifest_text, encoding="utf-8")
    output_path.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "manifest_sha256": receipt["manifest_sha256"], "eval_report_sha256": receipt["eval_report_sha256"], "benchmark_report_sha256": receipt["benchmark_report_sha256"], "package_smoke_report_sha256": receipt["package_smoke_report_sha256"], "file_count": receipt["file_count"]}, sort_keys=True))
    return 0 if receipt["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
