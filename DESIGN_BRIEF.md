# ProofCut local demo design brief

Frozen for implementation: 2026-09-07, Asia/Shanghai.

## Product route

- User: a creator or editor reviewing a transcript before republishing copy.
- Success: paste or import a transcript, run the real offline pipeline, inspect
  every candidate beside its timestamped source, and download the evidence pack.
- Primary archetype: Creative Tool.
- Supporting archetypes: AI Application workflow without an external model;
  Research Tool evidence trace.
- Primary task gravity: Create. Secondary: Investigate.
- Dominant object: one source-linked content segment, not a dashboard metric.
- Brand mode: none. This is a ProofCut-specific product surface and does not use
  KAI or XIAOYUE visual assets.

## Workflow and recovery

1. Start from the clearly labeled self-authored example, paste text, or import a
   `.json` / `.txt` transcript up to 1 MiB.
2. Run the same `load_transcript -> build_content_pack` path as the CLI.
3. Inspect release decision, segment count and source timestamp mode.
4. Review each generated field beside the exact source quote and risk decision.
5. Download canonical JSON or the evidence ledger CSV.

Invalid input remains in the editor and produces a specific recovery message.
The UI never implies that estimated text timestamps are media alignment.

## Reference strategy

- Main capability reference: Adobe Spectrum creative-tool principles; learn
  artwork-first hierarchy and contextual controls, not Adobe chrome or brand.
- Supporting capability: GitHub Primer data-role separation; learn readable
  status, source and output roles, not GitHub's navigation or visual skin.
- Accessibility baseline: semantic HTML, visible labels and focus, keyboard
  operation, 320 px reflow, reduced-motion support and WCAG 2.2 AA contrast.

## Art direction

Because ProofCut is an evidence-first creator tool with no real media preview,
the interface uses a compact transcript rail and a generous editorial evidence
stage. Warm paper surfaces distinguish source material; dark ink and a restrained
blue action color distinguish controls and decisions. Monospace is reserved for
timestamps, hashes and status values. There is no generic AI gradient, fake KPI,
testimonial, stock image or decorative chatbot shell.

- Desktop: 38/62 split between input rail and evidence stage.
- Mobile: input, run status, then results in one deliberate reading sequence.
- Borders: only around true inputs, actions and evidence boundaries.
- Motion: none required beyond native state changes.
- Media dependency: no. The authentic artifact is the timestamped text and its
  generated, source-linked content pack.

## Required states

- Loading/running: named stage and disabled duplicate Run action.
- Empty: direct invitation to load the included example or paste a transcript.
- Error: input preserved, reason visible, retry safe.
- Success: exact scope and downloadable artifacts visible.
- Offline: persistent local-only label; no credential or upload affordance.

## Evidence gaps

No user study, real creator workflow timing, public deployment, public repo,
external model quality or competition result is represented by this interface.
