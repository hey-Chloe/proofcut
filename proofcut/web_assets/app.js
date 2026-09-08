"use strict";

const elements = {
  transcript: document.querySelector("#transcript"),
  file: document.querySelector("#file"),
  run: document.querySelector("#run"),
  example: document.querySelector("#example"),
  error: document.querySelector("#input-error"),
  status: document.querySelector("#status"),
  summary: document.querySelector("#summary"),
  empty: document.querySelector("#empty"),
  segments: document.querySelector("#segments"),
  template: document.querySelector("#segment-template"),
  downloadJson: document.querySelector("#download-json"),
  downloadCsv: document.querySelector("#download-csv"),
};

let filename = "01_creator_claims.json";
let currentPack = null;

function setStatus(state, message) {
  elements.status.dataset.state = state;
  elements.status.querySelector(".status-mark").textContent = state === "success" ? "✓" : state === "error" ? "!" : "→";
  elements.status.querySelector("span:last-child").textContent = message;
}

function setBusy(busy) {
  elements.run.disabled = busy;
  elements.example.disabled = busy;
  elements.file.disabled = busy;
  elements.run.textContent = busy ? "Building source links…" : "Generate evidence pack";
}

function fieldLabel(name) {
  return name.replaceAll("_", " ");
}

function render(pack) {
  currentPack = pack;
  const summary = pack.summary;
  document.querySelector("#summary-release").textContent = summary.release_decision;
  document.querySelector("#summary-segments").textContent = String(summary.segment_count);
  document.querySelector("#summary-time").textContent = pack.transcript.timestamp_mode.toUpperCase();
  document.querySelector("#summary-risk").textContent = String(summary.unsupported_generated_claim_count);
  elements.summary.hidden = false;
  elements.empty.hidden = true;
  elements.segments.replaceChildren();

  for (const segment of pack.segments) {
    const fragment = elements.template.content.cloneNode(true);
    fragment.querySelector(".segment-id").textContent = segment.segment_id;
    fragment.querySelector(".segment-title").textContent = segment.content.title;
    fragment.querySelector(".time").textContent = segment.source_span.time_range;
    fragment.querySelector(".quote").textContent = segment.source_span.quote;
    const gate = fragment.querySelector(".gate");
    gate.textContent = segment.risk_gate.decision;
    gate.classList.toggle("review", segment.risk_gate.decision !== "PASS");
    const fields = fragment.querySelector(".content-fields");
    for (const [name, value] of Object.entries(segment.content)) {
      const row = document.createElement("div");
      const label = document.createElement("dt");
      const content = document.createElement("dd");
      const state = document.createElement("dd");
      const assessment = segment.risk_gate.fields[name];
      label.textContent = fieldLabel(name);
      content.textContent = value;
      state.textContent = assessment.supported ? "PASS" : "REVIEW";
      state.className = "field-state" + (assessment.supported ? "" : " review");
      state.title = assessment.risk_codes.join(", ") || "No configured lexical risk fired";
      row.append(label, content, state);
      fields.append(row);
    }
    elements.segments.append(fragment);
  }
  elements.downloadJson.disabled = false;
  elements.downloadCsv.disabled = false;
  setStatus("success", `Built ${summary.segment_count} source-linked segments locally. Nothing was uploaded.`);
}

async function runPipeline() {
  elements.error.hidden = true;
  setBusy(true);
  setStatus("running", "Running the deterministic segment, copy and claim-gate stages…");
  try {
    const response = await fetch("/api/run", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({filename, content: elements.transcript.value}),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "The local pipeline could not process this transcript.");
    render(result.pack);
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
    setStatus("error", "Input was preserved. Fix the issue above and run again.");
  } finally {
    setBusy(false);
  }
}

async function loadExample(run = true) {
  setBusy(true);
  setStatus("running", "Loading the included self-authored fixture…");
  try {
    const response = await fetch("/api/example");
    if (!response.ok) throw new Error("Included example is unavailable.");
    elements.transcript.value = await response.text();
    filename = "01_creator_claims.json";
    if (run) {
      await runPipeline();
    } else {
      setStatus("ready", "Included example loaded locally and ready to run.");
    }
  } catch (error) {
    elements.error.textContent = error.message;
    elements.error.hidden = false;
    setStatus("error", "Could not load the included example.");
  } finally {
    setBusy(false);
  }
}

function csvValue(value) {
  const text = Array.isArray(value) ? value.join("|") : String(value ?? "");
  return `"${text.replaceAll('"', '""')}"`;
}

function download(name, body, type) {
  const url = URL.createObjectURL(new Blob([body], {type}));
  const link = document.createElement("a");
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

elements.run.addEventListener("click", runPipeline);
elements.example.addEventListener("click", () => loadExample(false));
elements.file.addEventListener("change", async () => {
  const selected = elements.file.files[0];
  if (!selected) return;
  if (selected.size > 1_048_576) {
    elements.error.textContent = "Transcript exceeds the 1 MiB local demo limit.";
    elements.error.hidden = false;
    return;
  }
  filename = selected.name;
  elements.transcript.value = await selected.text();
  elements.error.hidden = true;
  setStatus("ready", `${selected.name} is loaded locally and ready to run.`);
});
elements.downloadJson.addEventListener("click", () => {
  if (currentPack) download("content_pack.json", JSON.stringify(currentPack, null, 2) + "\n", "application/json");
});
elements.downloadCsv.addEventListener("click", () => {
  if (!currentPack) return;
  const rows = currentPack.evidence_ledger;
  const headers = Object.keys(rows[0] || {});
  const body = [headers.map(csvValue).join(","), ...rows.map(row => headers.map(key => csvValue(row[key])).join(","))].join("\n") + "\n";
  download("evidence_ledger.csv", body, "text/csv;charset=utf-8");
});

loadExample(true);
