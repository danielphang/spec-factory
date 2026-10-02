---
title: Spec writer: the Problem section must be readable by the operator who approves it, in plain language
labels: p0, design-doc
---
**Where:** `docs/spec-factory.md` §2 Spec writer, the FORMAT line `## Problem          what's wrong or missing, for whom` and the RULES; `prompts/02-spec-writer.md` (copy of that block); §3 Spec critic rubric (nothing checks readability for the gate's reader).

**What happened (2026-10-02, spec-factory intake T-0010):** the operator read the approved spec at the gate and said "the problem's prose is incomprehensible. what does it mean". The Problem section opened: "Some specs were pinned before `factory init` created `openspec/`. A parent whose spec was pinned that way has no `openspec/changes/<ID>/` folder. Its parent-close VERIFIED runs `factory archive`, which exits 2, and `build.js` parks the parent (build spec part H)." Five terms of art in three sentences (pinned, parent-close VERIFIED, archive, exit 2, parks), none defined, written for the harness builder. The critic approved it in round 2 without a finding on it. Once translated ("the factory has no handler for a ticket whose spec predates the spec store; when such a ticket finishes, it parks and the documents don't say what you do"), the operator approved it.

**Why it matters:** the spec gate is the one place the human decides, and the Problem section is what they read first. A Problem the operator cannot read without a translator defeats the gate: they approve on the translator's word, not the spec's. Every spec the factory writes passes this gate.

**Proposed fix (design doc §2 and §3, re-copy prompts/02 and 03):**
- FORMAT: `## Problem          what's wrong or missing, for whom, in plain language for the human who approves this spec: no harness terms of art (pinned, parent-close, archive, park, exit codes) without a plain gloss on first use; the detail belongs under Evidence and Root cause`.
- RULES, Spec writer: "The Problem section is written for the operator at the gate, not for the harness builder or the next role. If a reader who has not seen the design doc could not say what is wrong and for whom, rewrite it."
- Critic rubric: add to rubric 1 or 6: "Problem reads without the design doc: a plain statement of what is wrong and for whom; terms of art are glossed."
- Acceptance for the writer's own output (P0-5 style measurement, not gating): count harness terms of art in Problem; report in the P0 metric table.

**Fix as implemented on the Nanobot side:** none; prompts re-copy on green follows the doc change.
