from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from proofcut.eval import evaluate_directory
from proofcut.export import write_exports
from proofcut.io import load_transcript
from proofcut.pipeline import build_content_pack


class ExportAndEvalTests(unittest.TestCase):
    def test_exports_valid_json_and_csv(self):
        pack = build_content_pack(load_transcript("fixtures/01_creator_claims.json"))
        with tempfile.TemporaryDirectory() as tmp:
            json_path, csv_path = write_exports(pack, tmp)
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            with csv_path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(loaded["schema_version"], "proofcut-content-pack-v1")
        self.assertEqual(len(rows), len(pack["evidence_ledger"]))

    def test_eval_requires_six_fixtures(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "one.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                evaluate_directory(tmp)

    def test_frozen_eval_passes(self):
        report = evaluate_directory("fixtures")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["aggregate"]["fixture_count"], 6)
        self.assertEqual(report["metrics"]["risk_probe_recall"], 1.0)
        self.assertEqual(report["metrics"]["unsupported_generated_field_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
