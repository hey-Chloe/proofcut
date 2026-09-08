# ProofCut

ProofCut is a local, deterministic creator-workflow MVP for the AI Content
Engine Hackathon. It turns a timestamped transcript into topical segments and
exports evidence-linked candidate copy:

```text
transcript JSON / text
  -> deterministic topical segments
  -> source utterance span + timestamp + exact quote
  -> hook / title / caption / SEO keywords / thumbnail brief
  -> unsupported-claim risk gate
  -> content_pack.json + evidence_ledger.csv
```

Status: `LOCAL_MVP_PASS / LOCAL_DEMO_IMPLEMENTED / DETERMINISTIC_OFFLINE / NOT_SUBMITTED`.

The code uses only the Python standard library. It makes no network request,
loads no model and reads no credential. The current generator is deliberately
extractive/template-based: it optimizes for inspectability and a truthful
end-to-end demo, not creative-copy quality.

## Quick start

From this directory:

```bash
python3 -m proofcut.cli \
  --input fixtures/01_creator_claims.json \
  --output outputs/example
```

Outputs:

- `outputs/example/content_pack.json`: segments, content fields, per-field risk
  assessments and source pointers.
- `outputs/example/evidence_ledger.csv`: one row per segment/content field,
  suitable for spreadsheet review or download from the local UI.

## Local browser demo

Run the dependency-free localhost app from this directory:

```bash
python3 -m proofcut.web --port 8765
```

Then open <http://127.0.0.1:8765>. The interface loads a clearly labeled,
self-authored example; accepts `.json` and `.txt` transcripts up to 1 MiB; runs
the same `load_transcript -> build_content_pack` path as the CLI; displays each
generated field beside its exact source span; and downloads canonical JSON or
CSV. It binds to localhost only and makes no external request.

The input JSON contract is:

```json
{
  "transcript_id": "example-01",
  "title": "Example",
  "language": "en",
  "utterances": [
    {"start_ms": 0, "end_ms": 5000, "speaker": "host", "text": "Source text."}
  ]
}
```

Utterances must be non-empty, ordered, non-overlapping and use integer
millisecond bounds. Plain text is also accepted:

- `[00:00-00:05] Text` lines retain `timestamp_mode=source`.
- Unaligned prose receives deterministic estimated timestamps and is explicitly
  labeled `timestamp_mode=estimated`; those values are not media alignment.

## Test and evaluate

```bash
python3 -m unittest discover -s tests -v
python3 -m proofcut.eval \
  --fixtures fixtures \
  --output outputs/eval_report.json
python3 scripts/benchmark.py
python3 scripts/build_receipt.py
python3 scripts/build_publication_manifest.py
python3 scripts/build_publication_archive.py
python3 scripts/submission_preflight.py
```

The independent evaluation reruns each of six frozen, self-authored fixtures
twice and measures byte determinism, source-span validity, field completeness,
generated-copy gate results and labeled risk probes. It does not measure human
editing time, creator preference, semantic factuality on open-domain data or
production reliability.

The benchmark command measures only local in-memory processing of the six tiny
fixtures. It is useful as a reproducibility receipt, not as production
throughput, model latency or a creator time-saving claim.

## Risk gate

The gate is fail-visible, not an oracle. It checks:

- a number in candidate copy that is absent from its source span;
- unsupported absolute language such as `100%`, `保证` or `always`;
- low lexical overlap with the cited source.

A `PASS` means only that these deterministic checks did not fire. It is not a
guarantee of truth. A future LLM adapter must remain optional and must not be
allowed to bypass the source ledger or risk gate.

See `PROVENANCE.md` for origin and `CLAIM_BOUNDARY.md` for allowed claims.
`DEVPOST_SUBMISSION.md` and `DEMO_SCRIPT_90S.md` are local submission drafts;
`OFFICIAL_REQUIREMENTS_SNAPSHOT.md` records the current official gate. No public
repository, registration or official submission has been performed.

The publication scripts operate on an explicit allowlist inside this project
only. They create a deterministic local source archive, verify every archive
member against `outputs/PUBLICATION_MANIFEST.sha256`, and reject cache, build,
environment and credential-like artifacts. This is a local safety gate, not a
remote publication or complete security/legal audit.
