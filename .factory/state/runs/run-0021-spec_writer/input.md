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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0021-spec_writer/output.md`

## Ticket (Triage output)

Type: bug

Title: P0-5 gates only on identifiers in Acceptance prose (fenced blocks stripped), and separately records internal symbols that inline Acceptance scripts import or call

Summary: P0-5 in `plans/P0-intake-skeleton.md` greps the whole spec with `grep -cE 'test_[a-z_]+\(|def |::'`. So any spec that uses the writer prompt's inline-script allowance scores a violation for a fixture helper such as `def sess(...)`, and the "Code identifiers in acceptance" metric cannot tell a stale symbol in a criterion from allowed fixture code. Following the operator's decision (option c, 2026-10-01), P0-5 should gate on prose only: the Acceptance section, with fenced blocks stripped, names no test function or internal symbol (0 hits). Separately, the metric table should count and record, without gating, the package-internal symbols that inline Acceptance scripts import or call. Helpers the script defines itself are not counted. The point is that the runs can then show whether a stricter rule is needed. The writer prompt's inline-script allowance stays as it is.

Duplicate search: none. I checked all seven tickets in `intake/state/tickets/*.yaml`: T-0001 to T-0005 are `awaiting-spec-gate` on unrelated subjects, T-0006 is this request, and T-0007 is the single-target harness. I also checked `issues/0*.md`. Nothing else covers P0-5 or the identifier grep.

Evidence:
- The current text is at `plans/P0-intake-skeleton.md:46`: P0-5 runs `grep -cE 'test_[a-z_]+\(|def |::' knowledge_vault/sanitized_specs/T-0001.md` → 0 over the whole file. The metric row at `:56` reads "Code identifiers in acceptance | "doubled", ten relint commits | 0 (P0-5)".
- The writer prompt's allowance is at `prompts/02-spec-writer.md:24-26` and `docs/spec-factory.md:270`: "give the check as an inline script in the Acceptance line itself, which the verifier runs verbatim on both base and PR". The rule after it, at `prompts/02-spec-writer.md:30-31` and `docs/spec-factory.md:275-276`, reads "Acceptance never names a test function or an internal symbol". `docs/spec-factory.md` never mentions P0-5, which I confirmed with a grep in the previous run.
- I re-ran the checks in this run, read only, on `~/dev/nanobot-upstream/knowledge_vault/spec_factory/specs/`:
  - On the whole file, the current grep returns 1 for `T-0001/v1.md`, `T-0001/v3.md` and `T-0001.md`, and 5 for `T-0003.md`. Every T-0003 hit is a fixture `def` (`skill`, `summary`, `need`) at lines 172-235, inside its Acceptance section (`## Acceptance` at :152, next heading at :271).
  - The gate under the operator's rule is the Acceptance section only, with fences stripped: `awk '/^## /{a=($0 ~ /^## Acceptance/)} a' <spec> | awk '/^```/{f=!f;next} !f' | grep -cE 'test_[a-z_]+\(|def |::'`. It returns 0 for all four files.
  - The recorded number has at least one real case to count. T-0001 v1's Acceptance contains `from nanobot.agent.context_governance import ContextGovernanceConfig, ContextGovernor` (Acceptance-relative line 50). Those are the symbols the round-1 critic flagged as "[NIT] #2 — A1/A2 name internal symbols" (`runs/run-0004-critic/output.md:109-113`).
- No harness fix exists. The issue names no Nanobot-side commit, and `git log --all --grep=P0-5` on `~/dev/nanobot-upstream` finds only the P0 skeleton commit. The only as-built handling is a manual interpretation at `~/dev/nanobot-upstream/knowledge_vault/spec_factory/P0_MEASUREMENTS.md:8`: "0 outside code fences (1 inside the inline fixture script, which the writer prompt allows)".
- Operator answer (Answer 1): "P0-5 gates on prose identifiers only: the Acceptance section with fenced blocks stripped must name no test function or internal symbol (0 hits). Separately, internal symbols that inline Acceptance scripts import or call from the package (not helpers the script defines itself) are counted and recorded in the metric table, without gating."

Assumptions (inferences, not stated by the requester or operator):
- The change is limited to `plans/P0-intake-skeleton.md`: the P0-5 line, plus the metric table (a restated row and a new non-gating row, or one row that carries both numbers). The writer prompt, critic rubric 2, `docs/spec-factory.md`, `specs/build-harness.md` and `prompts/` are unchanged, because the operator kept the allowance and nothing in option (c) changes role wording. If the spec writer finds a design-doc line that conflicts, the change follows the design doc's Changelog and re-copy conventions.
- "Internal symbols ... from the package" means names that an inline script imports from, or calls on, the system under test (in the reference store, `nanobot.*`). The spec writer should pin down how that count is taken, for example a grep for `from <pkg>`/`import <pkg>` lines inside Acceptance fences plus the names they bind. It must be runnable as written from `~/dev/spec-factory`. Whether attribute calls on an imported object (`ContextGovernor().fit_to_budget`) count as separate symbols is a counting detail the operator did not fix. I'd count each imported or called package name once per criterion, but that's my suggestion, not a requirement.
- "Prose identifiers" keeps the current pattern (`test_x(`, `def `, `::`), applied to the de-fenced Acceptance section. Widening the pattern itself was not requested.
- Acceptance for the eventual spec should include a check that the restated P0-5 command returns 0 on a fixture whose only hit is a fenced helper `def`. It should also include a check that returns nonzero when a criterion's prose names `file.py::test_x`. A new criterion that only passes on the current T-0001 proves nothing about the scope change.

Reason: n/a (ACCEPT). The operator answered the open design question with option (c), and every fact the fix needs is in the request, the answer, and the files cited above.
Suggested priority (a suggestion only, priority is a human call): medium. P0-5 is a measurement, not a merge gate, but every P0 spec that uses the inline-script allowance currently reports a false 1.

Out-of-scope observations:
- `issues/README.md` says each draft names the Nanobot-side commit where the fix already exists. Issue 06 names none, and none exists.
- `intake/state/tickets/T-0006.yaml` still has the file stem `06_p05_grep_vs_inline_scripts` as its title. The Title above can replace it.

STATUS: ACCEPT
CONFIDENCE: high. I re-ran the current and restated greps on both checkouts this run. The operator's answer settles the only open decision, and what's left is wording for the spec writer.
ESCALATIONS: none

## Request (raw)

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
