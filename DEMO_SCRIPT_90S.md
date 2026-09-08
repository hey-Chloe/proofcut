# ProofCut 90-second demo script

Target duration: 85–90 seconds. Record the local browser and terminal only. Do
not call the project an AI fact checker or claim measured time savings.

## 00:00–00:10 — problem and boundary

**Screen:** ProofCut opens with the included example and the persistent
“Local only · deterministic · no model or upload” label.

**Voice:** “Content tools make copy fast, but reviewing where every claim came
from is still hard. ProofCut turns a transcript into creator copy with the
source evidence attached.”

## 00:10–00:27 — real input and run

**Screen:** Briefly show the JSON transcript, then click **Generate evidence
pack**.

**Voice:** “This is a self-authored timestamped transcript. The browser sends it
only to a localhost Python server, which runs the same validated pipeline as the
command-line tool.”

## 00:27–00:51 — inspect the result

**Screen:** Show PASS, segment count, SOURCE timestamp mode, then one segment's
exact quote, title and caption.

**Voice:** “ProofCut creates topical segments and five reusable fields: hook,
title, caption, SEO terms and thumbnail brief. Each field keeps the exact quote,
time range, utterance indices and transcript hash. The gate exposes its decision
field by field.”

## 00:51–01:05 — show fail-visible behavior

**Screen:** Replace the input with invalid or empty JSON and run; show that the
input is preserved and a recovery message appears. Restore the example.

**Voice:** “Bad input fails visibly without deleting the editor's work. Plain
text is supported too, but its generated timing is explicitly labeled estimated,
not media alignment.”

## 01:05–01:20 — artifacts and proof

**Screen:** Download JSON and CSV, then switch to a terminal showing the test
command and current PASS receipt.

**Voice:** “The output downloads as canonical JSON and an editor-friendly
evidence ledger. Six frozen self-authored fixtures check deterministic replay,
source spans, complete fields and labeled risk probes.”

## 01:20–01:30 — honest close

**Screen:** Return to the boundary note.

**Voice:** “A pass is a review signal, not a guarantee of truth. ProofCut makes
the evidence visible and keeps the final publishing decision human.”
