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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0020-triage/output.md`

## Request (raw, with any answers appended)

---
title: P0-5's identifier grep contradicts the Spec writer's inline-script allowance
labels: p0, prompts
---
**Where:** `plans/P0-intake-skeleton.md` P0-5: `grep -cE 'test_[a-z_]+\(|def |::' <spec> → 0`. Spec writer prompt, RULES: *"give the check as an inline script in the Acceptance line itself, which the verifier runs verbatim on both base and PR"*.

**What happened (T-0001 / SPEC-21 v1, 2026-10-01):** the writer followed the prompt and put a 30-line fixture builder in Acceptance (a Python heredoc with one `def sess(...)`). P0-5's grep returns 1. The item the grep exists to catch — acceptance rows that name a test function or an internal symbol in prose — is absent from v1; the critic flagged two inline-harness criteria (A1/A2) as NITs under rubric 2 and did not block.

**Why it matters:** as written, P0-5 fails every spec that uses the allowance the writer prompt grants, so the metric "code identifiers in acceptance" cannot distinguish a stale symbol in a criterion from a fixture builder.

**Proposed fix:** scope the grep to prose outside fenced code blocks (e.g. strip ```…``` blocks first), or restate P0-5 as "no acceptance criterion's expected result names a test function or internal symbol"; keep the inline-script allowance.


## Answer 1

Operator decision (2026-10-01, Triage's question on P0-5): option **(c), two numbers.**

P0-5 gates on prose identifiers only: the Acceptance section with fenced blocks stripped must name no test function or internal symbol (0 hits). Separately, internal symbols that inline Acceptance scripts import or call from the package (not helpers the script defines itself) are counted and recorded in the metric table, without gating, so the runs show whether a stricter rule is needed.

## Your previous Triage output (the question you asked is answered above)

Type: bug

Title: P0-5's identifier grep fails any spec whose Acceptance uses an inline script, so it can't tell a fixture helper from a stale symbol

Summary: The writer prompt lets a spec give a check as an inline script inside the Acceptance line. P0-5's grep (`grep -cE 'test_[a-z_]+\(|def |::'`) runs over the whole spec file, so any helper `def` inside such a script scores as a violation. On T-0001 (SPEC-21) the only hit is a fixture builder that the prompt allows. The requester wants P0-5 to keep flagging test functions and internal symbols named in acceptance criteria, stop flagging fixture code the writer prompt permits, and keep the inline-script allowance.

Duplicate search: none found. The open tickets are T-0001 (status parser, parked), T-0002 (clerk schema), T-0003 (re-ask input), T-0004 (agents dir), T-0005 (protected live state, parked) and T-0007 (single-target harness). I checked `intake/state/tickets/*.yaml` and `issues/0*.md`, and none of them covers P0-5 or the identifier grep. No tickets are closed.

Evidence:
- The request quotes P0-5 as `grep -cE 'test_[a-z_]+\(|def |::' <spec> → 0`. In `plans/P0-intake-skeleton.md:46` the target is the whole file `knowledge_vault/sanitized_specs/T-0001.md`, not the Acceptance section. The metric row at `:56` is labelled "Code identifiers in acceptance | ... | 0 (P0-5)".
- The writer prompt's allowance is at `prompts/02-spec-writer.md:24-26` and `docs/spec-factory.md:270`: "give the check as an inline script in the Acceptance line itself, which the verifier runs verbatim on both base and PR". The rule that follows it, at `prompts/02-spec-writer.md:30-31` and `docs/spec-factory.md:275-276`, says "Acceptance never names a test function or an internal symbol". Critic rubric 2 (`docs/spec-factory.md:310-312`) says "no item names a test function or internal symbol".
- I re-ran the grep on the reference store (read only), `~/dev/nanobot-upstream/knowledge_vault/spec_factory/specs/`. It returns 1 for `T-0001/v1.md`, `v2.md`, `v3.md` and `T-0001.md`. Each hit is a fixture `def sess(...)` (v1:371, inside the Acceptance fence at v1:366-400). With fenced blocks stripped first (`awk '/^```/{f=!f;next} !f' <file> | grep -cE ...`) both v1 and v3 return 0. That confirms the requester's "returns 1" and shows the fence-stripping suggestion zeroes this case.
- The critic's round-1 output (`runs/run-0004-critic/output.md:109-113`) has "[NIT] #2 — A1/A2 name internal symbols". It cites `ContextGovernor().fit_to_budget` and `ContextGovernanceConfig`, which the inline script in v1 A1 imports and calls (v1:410, 413, 419), and the critic did not block on it. The current grep does not catch these at all, because its pattern only matches `def `, `test_x(` and `::`.
- The reference harness has no harness fix for this, and the issue names no Nanobot-side commit. `git log --all --grep=P0-5` on `~/dev/nanobot-upstream` finds only the P0 skeleton commit. The only as-built handling is an interpretation recorded in `knowledge_vault/spec_factory/P0_MEASUREMENTS.md:8` (commit 957249901): "v3: 0 outside code fences (1 inside the inline fixture script, which the writer prompt allows)".

Assumptions (inferences, not stated by the requester):
- The fix belongs in `plans/P0-intake-skeleton.md` (P0-5 and the metric row) and nowhere else, unless the human picks option (b) below. That option may also call for wording in the writer prompt or rubric 2, which is a design-doc change with a Changelog entry and a re-copy of `prompts/02-spec-writer.md` / `prompts/03-spec-critic.md`. `docs/spec-factory.md` does not mention P0-5. I confirmed this with a grep that found no match.
- The request does not mention scope, but it matters for any grep-based fix. P0-5 greps the whole spec, including Evidence and Root cause, and Root cause is where the format says symbols belong. Stripping fences alone would still flag a `file.py::test_x` written in Evidence prose. A fix that matches the requester's intent ("identifiers in acceptance") would probably limit the check to the Acceptance section.

Question for human: Should P0-5 count internal symbols that an inline Acceptance script imports or calls, like v1 A1's `ContextGovernor().fit_to_budget`? Or should it count only identifiers in criterion prose? The requester's two suggestions answer this differently. The writer rule and rubric 2 say "item", not "prose".
- (a) Prose only. P0-5 limits the check to the Acceptance section and strips fenced blocks before grepping. Everything inside an inline script is exempt from the metric, and symbol use there is left to the critic, as the NIT on A1/A2 was. This is the requester's first suggestion. T-0001 v1-v3 score 0.
- (b) Helper code exempt, symbol use counted. P0-5 is restated as: "no acceptance criterion names a test function or internal symbol, in prose or by importing/calling it in an inline script; helpers the script defines (e.g. `def sess`) don't count". It is checked by reading the spec, not by the grep alone. This is the requester's second suggestion read strictly. T-0001 v1 A1/A2 count as violations, and the writer prompt likely needs a line saying inline scripts drive the system black-box.
- (c) Two numbers. P0-5 gates on (a), prose identifiers in Acceptance = 0. Inline-script imports of package internals are also counted and recorded in the metric table, without gating, so the run can show whether (b) is needed.
Suggested priority (a suggestion only, priority is a human call): medium. P0-5 is a measurement and does not gate a merge, and the operator already applies interpretation (a) by hand in P0_MEASUREMENTS.md. But until this is decided, every P0 spec that uses the allowance reports a false 1.

Out-of-scope observations:
- `issues/README.md` says "each draft names the Nanobot-side commit where the fix already exists". Issue 06 names none, and I found none.
- The ticket title stored in `intake/state/tickets/T-0006.yaml` is the file stem `06_p05_grep_vs_inline_scripts`. It is not a defect, just a note.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I re-ran the evidence (grep counts, fence-stripped counts, critic NIT, rule text) on both checkouts, and the open point is a design scope question, not a missing fact.
ESCALATIONS: none
