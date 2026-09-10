from __future__ import annotations

import json
import unittest
from http import HTTPStatus

from proofcut.web import MAX_BODY_BYTES, process_payload, route_get, route_run


class WebPipelineTests(unittest.TestCase):
    def test_json_payload_uses_real_pipeline(self):
        payload = {
            "filename": "sample.json",
            "content": json.dumps({
                "transcript_id": "web-test",
                "utterances": [
                    {"start_ms": 0, "end_ms": 3000, "text": "Every claim keeps its source."}
                ],
            }),
        }
        pack = process_payload(payload)
        self.assertEqual(pack["transcript"]["transcript_id"], "web-test")
        self.assertEqual(pack["summary"]["release_decision"], "PASS")

    def test_text_payload_marks_estimated_timestamps(self):
        pack = process_payload({"filename": "notes.txt", "content": "First source sentence. Second source sentence."})
        self.assertEqual(pack["transcript"]["timestamp_mode"], "estimated")

    def test_rejects_unsupported_extension_and_oversize(self):
        with self.assertRaisesRegex(ValueError, "only .json or .txt"):
            process_payload({"filename": "video.mp4", "content": "source"})
        with self.assertRaisesRegex(ValueError, "1 MiB"):
            process_payload({"filename": "large.txt", "content": "x" * (MAX_BODY_BYTES + 1)})


class WebRouteTests(unittest.TestCase):
    def test_health_and_assets(self):
        status, health_body, content_type = route_get("/api/health")
        health = json.loads(health_body)
        index_status, index_body, _ = route_get("/")
        html = index_body.decode("utf-8")
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(index_status, HTTPStatus.OK)
        self.assertEqual(content_type, "application/json; charset=utf-8")
        self.assertEqual(health["status"], "PASS")
        self.assertIn("Turn source lines", html)
        self.assertLess(html.index('id="file"'), html.index('class="file-action"'))

        css_status, css_body, _ = route_get("/app.css")
        css = css_body.decode("utf-8")
        self.assertEqual(css_status, HTTPStatus.OK)
        self.assertIn("body { margin: 0; min-width: 0; }", css)
        self.assertNotIn("body { margin: 0; min-width: 320px; }", css)
        self.assertIn(".input-actions { grid-template-columns: 1fr; }", css)
        self.assertIn('input[type="file"]:focus-visible + .file-action', css)
        js_status, js_body, _ = route_get("/app.js")
        self.assertEqual(js_status, HTTPStatus.OK)
        self.assertIn("Included example loaded locally and ready to run.", js_body.decode("utf-8"))

    def test_run_route_and_error_recovery(self):
        status, result = route_run(json.dumps({"filename": "sample.txt", "content": "A cited source sentence."}).encode())
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["pack"]["summary"]["segment_count"], 1)
        bad_status, bad_result = route_run(json.dumps({"filename": "sample.txt", "content": ""}).encode())
        self.assertEqual(bad_status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(bad_result["status"], "ERROR")

    def test_run_route_rejects_malformed_utterance_items(self):
        content = json.dumps({"utterances": [None]})
        status, result = route_run(json.dumps({"filename": "bad.json", "content": content}).encode())
        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(result["status"], "ERROR")
        self.assertIn("utterance 0 must be an object", result["error"])


if __name__ == "__main__":
    unittest.main()
