## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0005-triage/output.md`

## Request (raw, with any answers appended)

---
title: Routing table: a re-asked role's "Receives" column omits its own prior output
labels: design-doc, routing
---
**Where:** design doc §Routing table, resolution rule *"A question returns to the role that asked, with the answer"*, and the Triage row's Receives column: *"The request, ticket search"*.

**What happened (P0 run, 2026-10-01):** Triage asked a three-option scope question (NEEDS-HUMAN). After the human's `--answer`, the rule returns the ticket to Triage with the answer appended to the request. Per the table as written, the re-run Triage receives only the request + answer: it does not receive the question it asked, so it must re-derive the three options (and the ~3M context tokens of investigation behind them) before it can read the answer as an answer.

**Proposed fix:** in §Routing rules, "A question returns to the role that asked, with the answer **and that role's prior output**" and add the same to the Receives column for Triage and Spec writer NEEDS-HUMAN re-entries (the Spec writer round-2 row already does this for the critic loop; the human-question path should be symmetric).

**Fix as implemented on the Nanobot side:** `factory/compose.py` (triage sources: request + last Triage output) at `0f2e29136`.
