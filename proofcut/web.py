"""Dependency-free local web demo for the real ProofCut pipeline."""

from __future__ import annotations

import argparse
import json
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .export import canonical_json
from .io import load_transcript
from .pipeline import build_content_pack


MAX_BODY_BYTES = 1_048_576
PACKAGE_DIR = Path(__file__).resolve().parent
ASSET_DIR = PACKAGE_DIR / "web_assets"
EXAMPLE_PATH = ASSET_DIR / "example.json"


def process_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Parse browser-supplied source through the same loader used by the CLI."""
    filename = str(payload.get("filename") or "transcript.txt")
    content = payload.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Paste a transcript or import a non-empty .json/.txt file.")
    suffix = Path(filename).suffix.lower()
    if suffix not in {".json", ".txt"}:
        raise ValueError("ProofCut accepts only .json or .txt transcripts.")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_BODY_BYTES:
        raise ValueError("Transcript exceeds the 1 MiB local demo limit.")
    with tempfile.TemporaryDirectory(prefix="proofcut-demo-") as temporary:
        source = Path(temporary) / f"transcript{suffix}"
        source.write_bytes(encoded)
        transcript = load_transcript(source)
    return build_content_pack(transcript)


def _asset(name: str) -> bytes:
    return (ASSET_DIR / name).read_bytes()


def route_get(path: str) -> tuple[HTTPStatus, bytes, str]:
    """Resolve a GET route without requiring a listening socket."""
    assets = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/app.css": ("app.css", "text/css; charset=utf-8"),
        "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    }
    if path in assets:
        name, content_type = assets[path]
        return HTTPStatus.OK, _asset(name), content_type
    if path == "/api/example":
        return HTTPStatus.OK, EXAMPLE_PATH.read_bytes(), "application/json; charset=utf-8"
    if path == "/api/health":
        body = canonical_json({"status": "PASS", "mode": "LOCAL_DETERMINISTIC_OFFLINE"}).encode("utf-8")
        return HTTPStatus.OK, body, "application/json; charset=utf-8"
    body = canonical_json({"status": "ERROR", "error": "Route not found."}).encode("utf-8")
    return HTTPStatus.NOT_FOUND, body, "application/json; charset=utf-8"


def route_run(body: bytes) -> tuple[HTTPStatus, dict[str, Any]]:
    """Resolve the run API without requiring a listening socket."""
    try:
        if not body or len(body) > MAX_BODY_BYTES + 16_384:
            raise ValueError("Request must contain at most 1 MiB of transcript text.")
        payload = json.loads(body.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object.")
        return HTTPStatus.OK, {"status": "PASS", "pack": process_payload(payload)}
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, KeyError) as error:
        return HTTPStatus.BAD_REQUEST, {"status": "ERROR", "error": str(error)}


class ProofCutHandler(BaseHTTPRequestHandler):
    server_version = "ProofCutLocal/0.2"

    def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: HTTPStatus, value: dict[str, Any]) -> None:
        self._send(status, canonical_json(value).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        status, body, content_type = route_get(self.path)
        self._send(status, body, content_type)

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/api/run":
            self._json(HTTPStatus.NOT_FOUND, {"status": "ERROR", "error": "Route not found."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(HTTPStatus.BAD_REQUEST, {"status": "ERROR", "error": "Content-Length must be an integer."})
            return
        if length <= 0 or length > MAX_BODY_BYTES + 16_384:
            self._json(HTTPStatus.BAD_REQUEST, {"status": "ERROR", "error": "Request must contain at most 1 MiB of transcript text."})
            return
        status, result = route_run(self.rfile.read(length))
        self._json(status, result)

    def log_message(self, format: str, *args: object) -> None:
        return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local-only ProofCut demo.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(argv)
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        parser.error("The evidence-safe demo binds to localhost only.")
    server = ThreadingHTTPServer((args.host, args.port), ProofCutHandler)
    print(json.dumps({"status": "READY", "url": f"http://{args.host}:{server.server_port}", "mode": "LOCAL_DETERMINISTIC_OFFLINE"}, sort_keys=True), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
