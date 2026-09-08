"""Command line interface for ProofCut."""

from __future__ import annotations

import argparse
import json

from .export import write_exports
from .io import load_transcript
from .pipeline import build_content_pack


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an evidence-linked creator content pack offline.")
    parser.add_argument("--input", required=True, help="Transcript .json or .txt")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args(argv)
    pack = build_content_pack(load_transcript(args.input))
    json_path, csv_path = write_exports(pack, args.output)
    print(json.dumps({
        "status": "PASS",
        "json": str(json_path),
        "csv": str(csv_path),
        "summary": pack["summary"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
