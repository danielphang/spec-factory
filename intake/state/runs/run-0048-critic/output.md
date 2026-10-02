## Critic review — T-0011 spec v1 (round 1)

### Spot-checks (all from `~/dev/spec-factory`, `main`, HEAD `f0f7fa8`)

Grounding (rubric 1):
- `sed -n 309p docs/spec-factory.md` → `## Problem          what's wrong or missing, for whom`; `sed -n 45p prompts/02-spec-writer.md` identical. `sed -n 364p` and `prompts/03-spec-critic.md:18` both → `6. Sufficient: an implementer could start without asking a question.` Line 147 carries "SHOULD-FIX and NIT ride with APPROVE". RULES at 279–302 and RUBRIC at 350–364 are as described; the "Open questions stay open" bullet sits directly before "Anti-Goodharting", so insertion point B is unambiguous.
- `intake/state/approvals/T-0010/spec-v2.yaml` → `by: dphang`, `version: 2`. `run-0045-critic/output.md` line 17 is the single SHOULD-FIX, line 30 `STATUS: APPROVE`. `sed -n 3p intake/state/specs/T-0010/v2.md` opens with the quoted jargon.
- `grep -rn -i "plain language\|plain words\|terms\? of art\|plain gloss" docs specs plans prompts` → exit 1. `grep -c Sufficient specs/build-harness.md` → `0`. Line 74 lists Problem by name only. `intake/instance/config.yaml:19` → `critic: fable`. `issues/README.md:19` → issue #11, p0, T-0011, "in intake".
- `grep -rn "what's wrong or missing" docs specs plans prompts issues` hits only the two lines the spec replaces, so no other document quotes the old text.
- Triage `run-0046-triage/output.md` lines 17–18 carry A1 and A2 as the spec describes them.

Testable (rubric 2):
- Ran items 1, 2, 3, 4, 7 verbatim on `main`: `0`, `0`, `0`, clean diffs then `0`, `CONTIGUOUS LAST-IS-OTHER`. Each NEW item fails today for the stated reason.
- Traced each grep key in items 1–3 through the line wraps of proposed text A/B/C ("gloss / each term of art", "Read it as / that operator", "plain gloss on / first use"): `tr -s ' \n' '  '` joins them, so the counts 5/4/5 are reachable with the wording as given. Continuation indent of A is 20 spaces, matching the existing `## Decisions` continuation (line 315).
- Item 5 command shape: one smoke call `claude -p --safe-mode --model fable --tools "" --max-turns 1 --system-prompt ...` from inside this harness session returned the expected one-word reply, so the check is runnable by a verifier agent, not only from a terminal. I did not re-run the 10-call check; the recorded 5/5 vs 0/5 is the writer's result.
- `git ls-files` shows `intake/state/specs/T-0010/v2.md` and `intake/instance/config.yaml` are tracked, so a clean checkout of the PR branch has the fixture items 5–6 read.

Scope / decisions / consistency (rubric 3–6): three files, 35+/4−, "Tests to change: none" is true (no test files). Protected `generated` and guardrail `agent prompts` are declared under Risk with the piece-8 approval record (doc line 43). The four design calls (rubric 6 placement, BLOCKING, categories not words, no term-count metric) are each stated with reasons and offered to the gate. The verbatim wording for A–C and the two re-copy commands leave an implementer nothing to ask.

### Findings

[SHOULD-FIX] 4, 6 — Open questions / Proposed change C
Problem: Triage A2 says the writer "records the choice under Decisions, as T-0005 did", and the current FORMAT (`docs/spec-factory.md:314`) has a `## Decisions` section, but the spec has none; its four design calls are split between Proposed change C and an "Open questions: none" paragraph that then lists three choices.
Evidence: `grep -n -i "A2" intake/state/runs/run-0046-triage/output.md` line 18; `sed -n 314p docs/spec-factory.md`; the spec's `## Open questions` text. The calls are not hidden, so this is placement, not substance.
Suggested fix: Add `## Decisions` with four one-line entries (rubric 6 not 1 or 7; BLOCKING severity; categories of terms, not T-0010's words; term-count metric left out) and leave `## Open questions` as a bare `none`.

[NIT] 2 — Acceptance items 5–6, hit-detection grep
Problem: The regex `\[BLOCKING\][^A-Za-z]*(and [0-9][^A-Za-z]*)?Problem` misses a finding located as "the Problem section" or "§Problem"; undercounting only makes item 5 stricter, but it can let item 6 pass while a plain control was in fact blocked.
Evidence: regex read against the critic's `[SEVERITY] <rubric #> <location>` line format (`docs/spec-factory.md:350–399`); no run observed, so the effect is a possibility, not a measured one.
Suggested fix: Either accept the small blind spot in the item text, or widen to the finding header line (e.g. `^\[BLOCKING\][^\n]*\bProblem\b`) and re-record the counts once.

[NIT] 2 — Acceptance items 5–6, prompt fidelity
Problem: The check feeds the raw block `prompts/03-spec-critic.md` with no preamble and the `{2}` placeholder unfilled, while the running harness feeds preamble + rendered role.
Evidence: `grep -n '{[a-z0-9 ]*}' prompts/03-spec-critic.md` → line 41 `After round {2}`; the Evidence trials used the same raw shape, so the recorded rates are internally consistent.
Suggested fix: One sentence in the item 5 preamble saying the check runs the raw block, so a verifier does not treat the difference from the rendered prompt as a defect.

[NIT] 2, 6 — Proposed change D / item 7
Problem: Item 7 reads only lines matching `^[0-9]+\. `, so entry 41 must be a single line (as entries 1–40 are, and placed after entry 40, before the "Declined:" line), but D does not say so.
Evidence: `sed -n 690,698p docs/spec-factory.md`; `awk` on the Changelog section shows every numbered entry is one physical line.
Suggested fix: In D, say "as one line, directly after entry 40".

### Prior findings
n/a (round 1)

### Out-of-scope observations
- The critic prompt this run executes under is itself the older rubric (item 2 lacks the Operator-steps clause present at `docs/spec-factory.md:352–354`), confirming the writer's re-port-gap observation from the critic side. Until `intake/harness/factory/prompts/` and green's copies are re-ported, neither this change nor Changelog 37/39 reaches live runs; a follow-up ticket should carry that.
- The relayed operator request asks for a p0 GitHub issue; `issues/README.md:19` already records #11 (p0) for T-0011, so nothing further is needed from the pipeline on that point.
- Trial sizes for the rejected variants in Evidence are small (n = 1–3). The decisive comparison (proposed wording 9/10 vs baseline 0/11 on jargon, 0/10 vs 0/9 on plain) is adequately sized; the intermediate rows support the narrative but would not on their own justify a design choice.

STATUS: APPROVE
CONFIDENCE: high — every cited path, line and "today" output re-derived at f0f7fa8; item 5's command shape confirmed runnable in-harness; the one SHOULD-FIX is placement, not substance, and rides with APPROVE.
ESCALATIONS: none
