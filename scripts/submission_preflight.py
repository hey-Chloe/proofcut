"""Audit local ProofCut submission materials without external side effects."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "DEVPOST_SUBMISSION.md",
    "DEMO_SCRIPT_90S.md",
    "OFFICIAL_REQUIREMENTS_SNAPSHOT.md",
    "VISUAL_QA_REPORT.md",
    "DESIGN_BRIEF.md",
    "outputs/LOCAL_MVP_RECEIPT.json",
    "outputs/MANIFEST.sha256",
    "outputs/PACKAGE_SMOKE.json",
    "outputs/PUBLICATION_MANIFEST.sha256",
    "outputs/PUBLICATION_SCAN.json",
    "outputs/PUBLICATION_ARCHIVE_RECEIPT.json",
    "outputs/proofcut-publication-source.tar.gz",
    "proofcut/web.py",
    "proofcut/web_assets/index.html",
    "proofcut/web_assets/app.css",
    "proofcut/web_assets/app.js",
)


def main() -> int:
    missing = [name for name in REQUIRED if not (ROOT / name).is_file()]
    receipt_path = ROOT / "outputs" / "LOCAL_MVP_RECEIPT.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
    package_smoke_path = ROOT / "outputs" / "PACKAGE_SMOKE.json"
    package_smoke = json.loads(package_smoke_path.read_text(encoding="utf-8")) if package_smoke_path.is_file() else {}
    publication_scan_path = ROOT / "outputs" / "PUBLICATION_SCAN.json"
    publication_scan = json.loads(publication_scan_path.read_text(encoding="utf-8")) if publication_scan_path.is_file() else {}
    archive_receipt_path = ROOT / "outputs" / "PUBLICATION_ARCHIVE_RECEIPT.json"
    archive_receipt = json.loads(archive_receipt_path.read_text(encoding="utf-8")) if archive_receipt_path.is_file() else {}
    manifest_path = ROOT / "outputs" / "MANIFEST.sha256"
    manifest_errors: list[str] = []
    if manifest_path.is_file():
        for line in manifest_path.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            path = ROOT / name
            if not path.is_file():
                manifest_errors.append(f"MISSING:{name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                manifest_errors.append(f"SHA_MISMATCH:{name}")
    publication_manifest_path = ROOT / "outputs" / "PUBLICATION_MANIFEST.sha256"
    publication_manifest_errors: list[str] = []
    if publication_manifest_path.is_file():
        for line in publication_manifest_path.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            path = ROOT / name
            if not path.is_file():
                publication_manifest_errors.append(f"MISSING:{name}")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                publication_manifest_errors.append(f"SHA_MISMATCH:{name}")
    archive_path = ROOT / "outputs" / "proofcut-publication-source.tar.gz"
    archive_receipt_current = (
        archive_path.is_file()
        and publication_manifest_path.is_file()
        and archive_receipt.get("archive_sha256") == hashlib.sha256(archive_path.read_bytes()).hexdigest()
        and archive_receipt.get("publication_manifest_sha256") == hashlib.sha256(publication_manifest_path.read_bytes()).hexdigest()
    )
    publication_chain_current = (
        archive_receipt_current
        and publication_manifest_path.is_file()
        and publication_scan.get("publication_manifest_sha256") == hashlib.sha256(publication_manifest_path.read_bytes()).hexdigest()
        and publication_scan.get("file_count") == archive_receipt.get("member_count")
    )

    checks = {
        "required_local_files_present": not missing,
        "local_mvp_receipt_pass": receipt.get("status") == "PASS",
        "manifest_current": not manifest_errors,
        "deterministic_offline_scope": receipt.get("scope") == "LOCAL_DETERMINISTIC_OFFLINE_ONLY",
        "official_submission_unclaimed": receipt.get("claim_boundary", {}).get("official_submission") == "NOT_SUBMITTED",
        "isolated_package_install_pass": package_smoke.get("status") == "PASS" and package_smoke.get("installed_import") == "PASS",
        "publication_secret_rights_scan_pass": publication_scan.get("status") == "PASS" and not publication_scan.get("secret_pattern_findings"),
        "publication_manifest_current": not publication_manifest_errors,
        "publication_archive_pass": archive_receipt.get("status") == "PASS" and archive_receipt.get("member_set_exact") is True and archive_receipt.get("member_hashes_exact") is True and archive_receipt.get("deterministic_byte_equal") is True and publication_chain_current,
    }
    local_ready = all(checks.values())
    report = {
        "schema_version": "proofcut-submission-readiness-v1",
        "status": "NEEDS_EXTERNAL_ACTION" if local_ready else "LOCAL_FIX_REQUIRED",
        "local_ready": local_ready,
        "checks": checks,
        "missing": missing,
        "manifest_errors": manifest_errors,
        "publication_manifest_errors": publication_manifest_errors,
        "publication_archive_sha256": archive_receipt.get("archive_sha256"),
        "manifest_sha256": receipt.get("manifest_sha256"),
        "external_gates": [
            "USER_CONFIRMS_ELIGIBILITY_AND_JOINS_HACKATHON",
            "USER_AUTHORIZES_PUBLIC_REPOSITORY_CREATION_AND_CODE_PUBLICATION",
            "OPTIONAL_DEMO_VIDEO_IS_RECORDED_AND_UPLOADED",
            "USER_REVIEWS_AND_AUTHORIZES_FINAL_DEVPOST_SUBMISSION",
        ],
        "claim_boundary": "Local readiness is not registration, publication, submission, judging, finalist status, or an award.",
    }
    output = ROOT / "outputs" / "SUBMISSION_READINESS.json"
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "local_ready": local_ready, "output": str(output)}, sort_keys=True))
    return 0 if local_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
