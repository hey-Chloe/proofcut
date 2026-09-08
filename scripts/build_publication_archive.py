"""Create and verify a deterministic local-only archive from the publication manifest."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "outputs" / "PUBLICATION_MANIFEST.sha256"
ARCHIVE_PATH = ROOT / "outputs" / "proofcut-publication-source.tar.gz"
RECEIPT_PATH = ROOT / "outputs" / "PUBLICATION_ARCHIVE_RECEIPT.json"
FORBIDDEN_PARTS = {
    "__pycache__",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".swp", ".swo"}


def read_manifest() -> list[tuple[str, str]]:
    rows = []
    for line in MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        rows.append((digest, name))
    if not rows:
        raise ValueError("publication manifest is empty")
    if len(rows) != len({name for _, name in rows}):
        raise ValueError("publication manifest contains duplicate paths")
    return rows


def forbidden_reason(name: str) -> str | None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return "UNSAFE_PATH"
    if any(part in FORBIDDEN_PARTS or part.endswith(".egg-info") for part in path.parts):
        return "EXCLUDED_ARTIFACT_CLASS"
    if any(part == ".env" or part.startswith(".env.") for part in path.parts):
        return "ENVIRONMENT_FILE"
    if path.suffix in FORBIDDEN_SUFFIXES or path.name == ".DS_Store":
        return "CACHE_OR_EDITOR_FILE"
    return None


def archive_bytes(rows: list[tuple[str, str]]) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for expected_digest, name in sorted(rows, key=lambda row: row[1]):
            source = ROOT / name
            if not source.is_file() or source.is_symlink():
                raise ValueError(f"manifest member is not a regular file: {name}")
            data = source.read_bytes()
            actual_digest = hashlib.sha256(data).hexdigest()
            if actual_digest != expected_digest:
                raise ValueError(f"manifest hash mismatch before archive: {name}")
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            archive.addfile(info, io.BytesIO(data))
    compressed = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=compressed, compresslevel=9, mtime=0) as handle:
        handle.write(tar_buffer.getvalue())
    return compressed.getvalue()


def verify_archive(data: bytes, rows: list[tuple[str, str]]) -> dict[str, object]:
    expected = {name: digest for digest, name in rows}
    member_hashes = {}
    non_regular = []
    forbidden = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = archive.getmembers()
        for member in members:
            reason = forbidden_reason(member.name)
            if reason:
                forbidden.append({"path": member.name, "reason": reason})
            if not member.isfile():
                non_regular.append(member.name)
                continue
            extracted = archive.extractfile(member)
            if extracted is None:
                non_regular.append(member.name)
                continue
            member_hashes[member.name] = hashlib.sha256(extracted.read()).hexdigest()
    names = list(member_hashes)
    return {
        "member_set_exact": set(names) == set(expected) and len(names) == len(expected),
        "member_hashes_exact": member_hashes == expected,
        "non_regular_members": non_regular,
        "forbidden_members": forbidden,
        "member_count": len(names),
    }


def main() -> int:
    rows = read_manifest()
    first = archive_bytes(rows)
    second = archive_bytes(rows)
    verification = verify_archive(first, rows)
    deterministic = first == second
    status = "PASS" if deterministic and verification["member_set_exact"] and verification["member_hashes_exact"] and not verification["non_regular_members"] and not verification["forbidden_members"] else "FAIL"
    ARCHIVE_PATH.write_bytes(first)
    receipt = {
        "schema_version": "proofcut-publication-archive-v1",
        "status": status,
        "scope": "LOCAL_DETERMINISTIC_PUBLICATION_SOURCE_ARCHIVE_ONLY",
        "archive": ARCHIVE_PATH.name,
        "archive_bytes": len(first),
        "archive_sha256": hashlib.sha256(first).hexdigest(),
        "publication_manifest_sha256": hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest(),
        "deterministic_byte_equal": deterministic,
        **verification,
        "claim_boundary": "The archive was created and verified locally. It was not uploaded, published, pushed, registered, or submitted.",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "archive": str(ARCHIVE_PATH), "archive_sha256": receipt["archive_sha256"], "member_count": receipt["member_count"], "deterministic_byte_equal": deterministic}, sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
