# ProofCut provenance

Initial MVP: 2026-09-03, Asia/Shanghai.

Local demo and submission-readiness additions: 2026-09-07, Asia/Shanghai.

## Authorship and competition-window boundary

- The pipeline code under `proofcut/`, its original tests and receipt scripts
  were newly authored in this directory on 2026-09-03. The local web interface,
  its tests, design brief and submission-readiness material were newly authored
  here on 2026-09-07. Both dates are inside the official hackathon build window.
- All six JSON fixtures are synthetic, self-authored text created for this local
  evaluation. They contain no customer transcript, private conversation,
  copyrighted video transcript or competition-provided secret data.
- No existing VoiceOps, Kaggriculture, media-pipeline or third-party project
  source file was copied into this implementation.
- The high-level design reuses general know-how already present in the workspace:
  evidence pointers, immutable hashes, explicit synthetic labels and fail-closed
  claim boundaries. Those are design concepts, not copied implementation.
- The scout/brief existed before this implementation and is planning material;
  it is not counted as application functionality.

## Dependencies and external activity

- Runtime dependencies: Python standard library only.
- No external model, API, SaaS, browser automation, network request or paid call
  is used by the MVP, tests or evaluation.
- No registration, team creation, organizer contact, deployment, public
  repository, public video or official submission was performed by this build.
- The browser demo binds only to localhost. Its HTML, CSS and JavaScript contain
  no third-party asset, remote font, analytics, CDN or external API request.

## Reproduction identity

`scripts/build_receipt.py` hashes the source, fixtures, tests, scripts and these
documentation files into `outputs/MANIFEST.sha256` and records the aggregate
manifest identity in `outputs/LOCAL_MVP_RECEIPT.json`.

This directory is not inside a Git repository in the current workspace, so no
Git commit identity is claimed. The SHA manifest is a local byte-identity
receipt, not a substitute for a future competition repository and commit log.
