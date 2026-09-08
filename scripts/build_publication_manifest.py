"""Build a local publication manifest and scan only its intended file set."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_TREES = ("proofcut", "fixtures", "tests", "scripts")
ROOT_FILES = (
    ".gitignore",
    "LICENSE",
    "README.md",
    "CLAIM_BOUNDARY.md",
    "PROVENANCE.md",
    "DESIGN_BRIEF.md",
    "DEVPOST_SUBMISSION.md",
    "DEMO_SCRIPT_90S.md",
    "OFFICIAL_REQUIREMENTS_SNAPSHOT.md",
    "VISUAL_QA_REPORT.md",
    "pyproject.toml",
)
EVIDENCE_FILES = (
    "outputs/LOCAL_MVP_RECEIPT.json",
    "outputs/MANIFEST.sha256",
    "outputs/PACKAGE_SMOKE.json",
    "outputs/benchmark_report.json",
    "outputs/eval_report.json",
    "outputs/example/content_pack.json",
    "outputs/example/evidence_ledger.csv",
)
EXCLUDED_PARTS = {"__pycache__", "build", "dist", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
SECRET_RULES = {
    "PRIVATE_KEY_BLOCK": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "OPENAI_STYLE_KEY": re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "GITHUB_TOKEN": re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "AWS_ACCESS_KEY": re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GOOGLE_API_KEY": re.compile(rb"\bAIza[A-Za-z0-9_-]{30,}\b"),
    "SLACK_TOKEN": re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "ASSIGNED_SECRET": re.compile(
        rb"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"
    ),
}


def _tree_files(name: str):
    base = ROOT / name
    for path in sorted(item for item in base.rglob("*") if item.is_file()):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS or part.endswith(".egg-info") for part in relative.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def publication_files() -> list[Path]:
    paths: list[Path] = []
    for tree in SOURCE_TREES:
        paths.extend(_tree_files(tree))
    paths.extend(ROOT / name for name in ROOT_FILES)
    paths.extend(ROOT / name for name in EVIDENCE_FILES)
    unique = {path.resolve(): path for path in paths}
    return sorted(unique.values(), key=lambda path: path.relative_to(ROOT).as_posix())


def main() -> int:
    missing = [name for name in (*ROOT_FILES, *EVIDENCE_FILES) if not (ROOT / name).is_file()]
    records = []
    secret_findings = []
    for path in publication_files():
        if not path.is_file():
            continue
        data = path.read_bytes()
        relative = path.relative_to(ROOT).as_posix()
        records.append({"path": relative, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        for rule, pattern in SECRET_RULES.items():
            if pattern.search(data):
                secret_findings.append({"path": relative, "rule": rule})

    manifest_text = "".join(f"{item['sha256']}  {item['path']}\n" for item in records)
    manifest_path = ROOT / "outputs" / "PUBLICATION_MANIFEST.sha256"
    scan_path = ROOT / "outputs" / "PUBLICATION_SCAN.json"
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8") if (ROOT / "LICENSE").is_file() else ""
    provenance_text = (ROOT / "PROVENANCE.md").read_text(encoding="utf-8") if (ROOT / "PROVENANCE.md").is_file() else ""
    rights_checks = {
        "license_present": bool(license_text.strip()),
        "license_identified_as_mit": "MIT License" in license_text,
        "provenance_present": bool(provenance_text.strip()),
        "authorship_boundary_documented": "Authorship and competition-window boundary" in provenance_text,
        "dependency_boundary_documented": "Dependencies and external activity" in provenance_text,
        "no_symlink_in_publication_set": not any(path.is_symlink() for path in publication_files()),
    }
    status = "PASS" if not missing and not secret_findings and all(rights_checks.values()) else "FAIL"
    scan = {
        "schema_version": "proofcut-publication-scan-v1",
        "status": status,
        "scope": "INTENDED_PROOFCUT_PUBLICATION_SET_ONLY",
        "file_count": len(records),
        "publication_manifest_sha256": hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
        "missing": missing,
        "secret_pattern_findings": secret_findings,
        "secret_rules_checked": sorted(SECRET_RULES),
        "rights_checks": rights_checks,
        "excluded_artifact_classes": sorted(EXCLUDED_PARTS | {"*.egg-info", "*.pyc", "*.pyo", ".env", ".env.*"}),
        "self_referential_local_outputs_excluded": [
            "outputs/PUBLICATION_MANIFEST.sha256",
            "outputs/PUBLICATION_SCAN.json",
            "outputs/PUBLICATION_ARCHIVE_RECEIPT.json",
            "outputs/SUBMISSION_READINESS.json",
            "outputs/proofcut-publication-source.tar.gz",
        ],
        "claim_boundary": "Pattern scanning reduces accidental-publication risk but is not a complete security, privacy, license, or legal review. No credential location was read and no remote publication was performed.",
    }
    manifest_path.write_text(manifest_text, encoding="utf-8")
    scan_path.write_text(json.dumps(scan, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "file_count": len(records), "publication_manifest_sha256": scan["publication_manifest_sha256"], "secret_pattern_findings": len(secret_findings), "output": str(scan_path)}, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
