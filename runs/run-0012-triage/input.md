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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0012-triage/output.md`

## Request (raw, with any answers appended)

---
title: P0-5's identifier grep contradicts the Spec writer's inline-script allowance
labels: p0, prompts
---
**Where:** `plans/P0-intake-skeleton.md` P0-5: `grep -cE 'test_[a-z_]+\(|def |::' <spec> → 0`. Spec writer prompt, RULES: *"give the check as an inline script in the Acceptance line itself, which the verifier runs verbatim on both base and PR"*.

**What happened (T-0001 / SPEC-21 v1, 2026-10-01):** the writer followed the prompt and put a 30-line fixture builder in Acceptance (a Python heredoc with one `def sess(...)`). P0-5's grep returns 1. The item the grep exists to catch — acceptance rows that name a test function or an internal symbol in prose — is absent from v1; the critic flagged two inline-harness criteria (A1/A2) as NITs under rubric 2 and did not block.

**Why it matters:** as written, P0-5 fails every spec that uses the allowance the writer prompt grants, so the metric "code identifiers in acceptance" cannot distinguish a stale symbol in a criterion from a fixture builder.

**Proposed fix:** scope the grep to prose outside fenced code blocks (e.g. strip ```…``` blocks first), or restate P0-5 as "no acceptance criterion's expected result names a test function or internal symbol"; keep the inline-script allowance.
