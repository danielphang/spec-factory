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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0040-triage/output.md`

## Request (raw, with any answers appended)

---
title: Build spec: a spec pinned before `factory init` has no change folder; say how its parent closes
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part K (`factory archive`) and part B "Spec store"; `plans/P0-intake-skeleton.md` (the three pilot specs). The spec store activates when `factory init` creates `openspec/`; a store's specs pinned before that are one text each, with no `openspec/changes/<ID>/` folder.

**What happened (2026-10-01, Nanobot green):** the harness gained the spec store (`fffeddcf6`) while three pilot tickets (SPEC-21, SPEC-26, SPEC-27) were already `planned` with old-format specs pinned. `planned` has no routing edge back to the writer, so the only pipeline path to a four-part spec is a fresh ticket per request (triage, writer and critic again, 12–56M context tokens each). Left as they are, each pilot's parent-close VERIFIED will run `factory archive`, which exits 2 ("no change folder to archive") and parks the parent, as the rules say. Nothing in the documents says what the operator does with such a park.

**Why it matters:** every store that adopts the spec store after its first tickets has this cohort. Without a stated path the parks read as harness bugs, and each operator re-decides between re-intake and a hand archive.

**Proposed fix (spec K, one sentence; P0 plan, one line):** a parent whose pinned spec has no change folder (pinned before `factory init`, or in a store where `init` has not run) closes without archive: `archive` reports `no change folder` as a distinct refusal, and the resolution rule for that park is "close the parent as applied; its spec is not current truth, re-intake it as a new ticket if current truth should carry it". The P0 plan records the three pilots as that cohort.

**Fix as implemented on the Nanobot side:** none yet; `factory archive` already refuses with `has no change folder to archive` (green `fffeddcf6`).
