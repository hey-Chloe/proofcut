from __future__ import annotations

import unittest

from proofcut.risk import assess_claim


class RiskGateTests(unittest.TestCase):
    def test_supports_source_paraphrase_with_overlap(self):
        result = assess_claim("编辑需要保存来源时间戳", "编辑需要保存来源时间戳并回看原文")
        self.assertTrue(result["supported"])

    def test_flags_missing_number(self):
        result = assess_claim("This saves 90% of editing time.", "This helps editors check source text.")
        self.assertIn("UNSUPPORTED_NUMBER", result["risk_codes"])

    def test_flags_changed_chinese_adjacent_percentage(self):
        source = "这次流程优化后，我们的整体工作效率提升了10%，并且保持了原来的交付标准。"
        result = assess_claim("整体工作效率提升了90%，并且保持原来的交付标准。", source)
        self.assertFalse(result["supported"])
        self.assertIn("UNSUPPORTED_NUMBER", result["risk_codes"])
        self.assertEqual(result["missing_numbers"], ["90%"])

    def test_allows_supported_mixed_language_number(self):
        source = "Release v2 kept 3 safeguards and 准确率提升10%。"
        result = assess_claim("准确率提升10%，with 3 safeguards.", source)
        self.assertNotIn("UNSUPPORTED_NUMBER", result["risk_codes"])

    def test_does_not_treat_display_timestamp_as_claim_number(self):
        result = assess_claim("来源 00:10–00:30", "来源")
        self.assertNotIn("UNSUPPORTED_NUMBER", result["risk_codes"])

    def test_flags_unsupported_absolute(self):
        result = assess_claim("This tool always doubles reach.", "This tool suggests a caption.")
        self.assertIn("UNSUPPORTED_ABSOLUTE", result["risk_codes"])

    def test_flags_low_source_overlap(self):
        result = assess_claim("The product won an industry award.", "The editor reviewed a transcript.")
        self.assertIn("LOW_SOURCE_OVERLAP", result["risk_codes"])


if __name__ == "__main__":
    unittest.main()
