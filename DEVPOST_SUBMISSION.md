# ProofCut — Devpost submission copy

Status: local draft only. No repository URL, video URL or official submission
exists yet.

## Project name

ProofCut

## Tagline

Source-linked creator copy you can audit before you publish.

## Short description

ProofCut turns a timestamped transcript into hooks, titles, captions, SEO terms
and thumbnail briefs while keeping every generated field connected to its exact
source quote and time range. A deterministic risk gate surfaces unsupported
numbers, absolute language and low source overlap for human review.

## Inspiration

The hard part of repurposing a transcript is not generating more text. It is
knowing which source line supports each claim when an editor reviews a title,
caption or thumbnail brief. Most content generators make output easy to create
and evidence hard to inspect. ProofCut makes that relationship the main product
object.

## What it does

1. Accepts timestamped JSON, timestamped text or plain text.
2. Creates deterministic topical segments.
3. Produces a hook, title, caption, SEO terms and thumbnail brief for each
   segment.
4. Attaches the exact source quote, utterance indices, time range and transcript
   SHA-256 to every field.
5. Runs a fail-visible lexical gate for unsupported numbers, configured absolute
   claims and low source overlap.
6. Exports canonical `content_pack.json` and an editor-friendly
   `evidence_ledger.csv`.

The included local web demo runs the same Python pipeline as the CLI. It is not
a mockup and makes no network request.

## How we built it

ProofCut uses Python's standard library only. The domain path is:

```text
validated transcript
→ bounded topical segmentation
→ extractive content composition
→ field-level source-support assessment
→ canonical JSON + CSV evidence ledger
```

The CLI and localhost web app both call `load_transcript` and
`build_content_pack`; the interface does not maintain a second demonstration
implementation. The evaluation reruns six frozen, self-authored fixtures twice,
checks byte determinism and source-span validity, and evaluates labeled risk
probes. A content-addressed manifest freezes the source, tests, fixtures and
submission materials.

## Challenges

- Preserving source traceability without pretending that a lexical gate is a
  factuality oracle.
- Supporting both real timestamp ranges and unaligned text without presenting
  estimated timestamps as media alignment.
- Making the demo judgeable while keeping the runtime dependency-free and
  strictly local.
- Keeping every claim about the project inside the evidence actually produced
  by the local test and receipt pipeline.

## Accomplishments

- A working CLI and local browser workflow produce real JSON and CSV artifacts.
- Every candidate field is linked to an exact source span and transcript hash.
- The current frozen local evaluation covers six synthetic, self-authored
  fixtures and includes deterministic replay plus labeled risk probes.
- Empty, success and recoverable error states are implemented without sending
  transcript content to an API.

These are local build facts, not user-study, production or competition results.

## What we learned

Evidence needs to be modeled at the field level. Linking only an overall summary
to a transcript does not help an editor identify which title word, number or
caption claim requires review. We also learned to separate a useful warning
heuristic from a truth guarantee: ProofCut shows the exact checks that fired and
leaves the publishing decision to the editor.

## What's next

- Add opt-in model adapters without allowing them to bypass the evidence ledger.
- Connect source timestamps to a real media player after alignment is verified.
- Run creator usability sessions and measure review behavior before making any
  time-saving claim.
- Expand multilingual risk probes and property-based input tests.

## Built with

Python 3 · standard library · HTML · CSS · JavaScript · JSON · CSV

## Links still required for submission

- Public source repository: required, not created.
- Short demo video: optional, not recorded or uploaded.
