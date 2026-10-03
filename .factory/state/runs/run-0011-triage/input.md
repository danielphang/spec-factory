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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0011-triage/output.md`

## Request (raw, with any answers appended)

---
title: Faux-spec "target operational state" steps live under a protected path; the pipeline cannot verify them
labels: nanobot-config, triage-finding
---
**Where:** Nanobot `factory/config.yaml` protected paths (`credentials: ~/.nanobot/**`) vs. legacy faux specs whose §Target operational state and validation criteria act on the live instance (install a daily cron, replace workspace skills, "the daily cron stays silent on healthy days").

**Triage's finding (SPEC-21 → T-0001, 2026-10-01):** criteria 1–7 are in-repo and verifiable; criterion 8 (live soak) and the operational steps are operator work under the protected path and cannot be acceptance items for any role.

**Proposal (design level, small):** the Spec writer FORMAT gains an optional `## Operator steps` section: actions on protected or live state that the human performs after merge, explicitly *not* acceptance. Otherwise every ported faux spec will either leak live-state steps into Acceptance (unverifiable → SPEC-DEFECT) or silently drop them.
