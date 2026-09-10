from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from proofcut.io import load_transcript


class InputTests(unittest.TestCase):
    def test_loads_frozen_json(self):
        transcript = load_transcript("fixtures/01_creator_claims.json")
        self.assertEqual(transcript["timestamp_mode"], "source")
        self.assertEqual(len(transcript["utterances"]), 5)

    def test_plain_timestamped_lines_retain_source_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("[00:00-00:05] First fact.\n[00:05-00:09] Second fact.", encoding="utf-8")
            transcript = load_transcript(path)
        self.assertEqual(transcript["timestamp_mode"], "source")
        self.assertEqual(transcript["utterances"][1]["start_ms"], 5000)

    def test_plain_unaligned_text_is_marked_estimated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("First sentence.\nSecond sentence.", encoding="utf-8")
            transcript = load_transcript(path)
        self.assertEqual(transcript["timestamp_mode"], "estimated")
        self.assertGreater(transcript["utterances"][1]["start_ms"], 0)

    def test_plain_chinese_sentences_split_without_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.txt"
            path.write_text("第一句话。第二句话！第三句话？", encoding="utf-8")
            transcript = load_transcript(path)
        self.assertEqual(len(transcript["utterances"]), 3)

    def test_rejects_overlapping_json_utterances(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"utterances": [
                {"start_ms": 0, "end_ms": 10, "text": "a"},
                {"start_ms": 9, "end_ms": 20, "text": "b"},
            ]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_transcript(path)

    def test_rejects_non_object_json_utterances(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"utterances": [None, 7, "text"]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "utterance 0 must be an object"):
                load_transcript(path)

    def test_rejects_boolean_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"utterances": [
                {"start_ms": False, "end_ms": True, "text": "a"}
            ]}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integer start_ms/end_ms"):
                load_transcript(path)

    def test_rejects_empty_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.txt"
            path.write_text("", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_transcript(path)


if __name__ == "__main__":
    unittest.main()
