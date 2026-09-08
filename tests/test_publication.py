from __future__ import annotations

import hashlib
import unittest

from scripts.build_publication_archive import archive_bytes, forbidden_reason, verify_archive
from scripts.build_publication_manifest import ROOT, publication_files


class PublicationSafetyTests(unittest.TestCase):
    def test_publication_allowlist_stays_inside_project(self):
        root = ROOT.resolve()
        for path in publication_files():
            path.resolve().relative_to(root)

    def test_publication_allowlist_excludes_generated_artifacts(self):
        names = [path.relative_to(ROOT).as_posix() for path in publication_files()]
        self.assertFalse(any("__pycache__" in name or ".egg-info" in name for name in names))
        self.assertNotIn("outputs/proofcut-publication-source.tar.gz", names)
        self.assertNotIn("outputs/PUBLICATION_ARCHIVE_RECEIPT.json", names)

    def test_forbidden_archive_members_are_rejected(self):
        self.assertEqual(forbidden_reason("proofcut/__pycache__/module.pyc"), "EXCLUDED_ARTIFACT_CLASS")
        self.assertEqual(forbidden_reason(".env.production"), "ENVIRONMENT_FILE")
        self.assertEqual(forbidden_reason("../outside.txt"), "UNSAFE_PATH")
        self.assertIsNone(forbidden_reason("proofcut/pipeline.py"))

    def test_archive_bytes_are_deterministic_and_exact(self):
        source = ROOT / ".gitignore"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        rows = [(digest, ".gitignore")]
        first = archive_bytes(rows)
        second = archive_bytes(rows)
        self.assertEqual(first, second)
        verification = verify_archive(first, rows)
        self.assertTrue(verification["member_set_exact"])
        self.assertTrue(verification["member_hashes_exact"])
        self.assertEqual(verification["forbidden_members"], [])


if __name__ == "__main__":
    unittest.main()
