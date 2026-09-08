from __future__ import annotations

import unittest

from proofcut.export import canonical_json
from proofcut.io import load_transcript
from proofcut.pipeline import build_content_pack, segment_utterances


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.transcript = load_transcript("fixtures/01_creator_claims.json")
        self.pack = build_content_pack(self.transcript)

    def test_builds_required_content_fields(self):
        required = {"hook", "title", "caption", "seo_keywords", "thumbnail_brief"}
        for segment in self.pack["segments"]:
            self.assertEqual(set(segment["content"]), required)

    def test_ledger_has_one_row_per_segment_field(self):
        self.assertEqual(len(self.pack["evidence_ledger"]), len(self.pack["segments"]) * 5)

    def test_source_spans_are_monotonic(self):
        spans = [segment["source_span"] for segment in self.pack["segments"]]
        self.assertTrue(all(span["end_ms"] > span["start_ms"] for span in spans))
        self.assertTrue(all(left["end_ms"] <= right["start_ms"] for left, right in zip(spans, spans[1:])))

    def test_generated_pack_passes_risk_gate(self):
        self.assertEqual(self.pack["summary"]["unsupported_generated_claim_count"], 0)
        self.assertEqual(self.pack["summary"]["release_decision"], "PASS")

    def test_pipeline_is_byte_deterministic(self):
        left = canonical_json(build_content_pack(self.transcript))
        right = canonical_json(build_content_pack(self.transcript))
        self.assertEqual(left.encode(), right.encode())

    def test_segmenter_bounds_group_size(self):
        groups = segment_utterances(self.transcript["utterances"])
        self.assertTrue(all(1 <= len(group) <= 4 for group in groups))

    def test_transcript_hash_changes_with_source(self):
        changed = dict(self.transcript)
        changed["utterances"] = [dict(item) for item in self.transcript["utterances"]]
        changed["utterances"][0]["text"] += " Changed."
        other = build_content_pack(changed)
        self.assertNotEqual(self.pack["transcript"]["sha256"], other["transcript"]["sha256"])


if __name__ == "__main__":
    unittest.main()
