# ProofCut local demo — visual QA report

Checked: 2026-09-07, Asia/Shanghai.

Result: `PASS_WITH_EVIDENCE_LIMITS`. No unresolved Critical or Major issue was
found in the covered local-demo flow. This is an expert heuristic and browser
interaction review, not user research or owner preference acceptance.

## Test contract

- Route: local ProofCut workspace.
- User and task: a creator/editor imports or pastes a transcript, generates a
  pack, reviews exact evidence and downloads artifacts.
- Archetype: Creative Tool with Research Tool evidence trace.
- Primary gravity: Create; secondary: Investigate.
- Dominant object: source-linked segment.
- Brand mode: none.
- Browser evidence: Codex in-app browser DOM, interaction and computed-style
  inspection using the frozen self-authored example.
- Widths covered: desktop 1264 CSS px; mobile 390 CSS px; required reflow at
  320 CSS px. Reduced-motion CSS is present; no nonessential motion is used.
- States covered: loading, success, invalid/empty input error, restored/ready,
  disabled downloads before result, populated evidence, keyboard focus.

## Core-flow evidence

- Automatic example load completed through the real page logic with 2 segments.
- Browser errors and warnings: 0.
- Empty input produced the exact recoverable error `Paste a transcript or import
  a non-empty .json/.txt file.` and preserved the editor.
- Restore Example changed status to `Included example loaded locally and ready
  to run.` after the initial stalled-status bug was fixed.
- Keyboard order: wordmark → transcript → Run → file input → Restore Example.
- File input focus produced a visible 3 px solid outline on its label.
- At 320 px: `innerWidth=320`, `clientWidth=305`, document and body
  `scrollWidth=305`; there was no horizontal overflow after the fix.
- At 390 px, actions recompose to a deliberate single column and the field hint
  moves beneath its label.

## Fixed issue ledger

| ID | Severity | Before | Root cause | Fix | After |
| --- | --- | --- | --- | --- | --- |
| VQA-01 | Major | 320 px produced horizontal scrolling | `body` forced a 320 px minimum inside the scrollbar-reduced client area | removed the forced minimum and added a regression assertion | document/body scroll width equals 305 px client width |
| VQA-02 | Major | restoring the example from the error state left a permanent loading message | the non-auto-run branch never set ready state | explicit ready status in `loadExample(false)` | precise ready message visible |
| VQA-03 | Major | keyboard focus on the visually hidden file input was not visible | label preceded the input and `:focus-within` could not match | input now precedes its label; adjacent-focus selector supplies outline | file step is visible in keyboard sequence |
| VQA-04 | Minor | mobile import action occupied an isolated half row | desktop two-column action grid persisted | mobile actions now use one column | 390/320 px actions read as one sequence |

## Art Direction evaluation

| Dimension | Result | Evidence |
| --- | --- | --- |
| Structural Fit | PASS | transcript rail and evidence stage give the main source-linked object priority; mobile preserves task order |
| Visual Fidelity | PASS | live desktop/mobile inspection found consistent typography, spacing and state detail after fixes |
| Media Quality | PASS / not media-dependent | the authentic artifact is timestamped text and generated evidence; no fake image or placeholder is used |
| Typography | PASS | editorial heading, readable source copy and monospace evidence roles remain distinct across covered widths |
| Surface / Border Discipline | PASS | boundaries mark inputs, evidence and actionable controls; no nested dashboard-card grid or decorative shadow stack |
| Product Authenticity | PASS | included data is labeled self-authored; outputs, error state and local-only scope are real and no KPI/testimonial is invented |
| Reference Appropriateness | PASS | creative-tool hierarchy and evidence/data role separation were adapted without copying a reference brand skin |

## Evidence limits and untested scope

- No persistent screenshot baseline or pixel diff was accepted as Golden.
- No axe-core or other automated accessibility scan was run; the report covers
  semantic inspection, keyboard order, visible focus and reflow only.
- No screen-reader session, Safari/Firefox run, touch-device run, zoom-to-400%
  check, real creator transcript, media player, public deployment or networked
  production environment was tested.
- The user has not performed visual preference or usability acceptance. The UI
  remains a reviewed local candidate, not a user-validated design baseline.
