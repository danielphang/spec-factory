# Critic review: T-0057 spec v1 (round 1)

## What I checked

- Cited paths and lines on `main` at `3e4705a`: `factory/cli.py:104-128` (`ticket set`, `_check_edge`) and `:407-410` (`spec_add`), `factory/common.py:29-39`, `factory/human.py:66`, `:115-120`, `:142`, `factory/specstore.py:25`, `:179-216`, `:223-237`, `:51` (`is_active` is just "the `openspec/` directory exists"), `factory/drive.py:294-297`, `:318-327`, `:288`, `:160` (the driver's park also turns `"` into `'`, so the parity claim about quotes holds), `factory/workflows/intake.js:78`, `:184`, `:188-189`, `:204-212`, `factory/compose.py:275-296`, `factory/store.py:196-198` (`spec:init` sets the round to 1 only when it is 0, so a round of 2 set before the move to the critic survives it), `.factory/instance.yaml:26`, `:57`, `:61` (`parked → ready-for-spec-writer` is an edge, so the Risk section's recovery command is valid), `factory/instance.template.yaml:70`. All land where the spec says.
- The incident record: `.factory/store/specs/T-0047/v1.md` lines 499-500, 509 and 514-515 hold the three labels as described; the store log holds `spec.added` v1 from `run-0478-spec_writer` at 17:33 and v2 from a gate edit at 18:07.
- Current-truth pins the change must respect: harness-code pins `human.py`'s definition list (the check stays there), `specstore.applies(root, deltas)` once across the command modules, `harness-bug: .*stderr` once in `drive.py`, `cli.py` under 900 lines (880 today). `compose.py` imports nothing from `human.py` today and `human.py` imports nothing from `compose.py`, so the proposed import is cycle-free. harness-docs caps README at 1,185 (1,184 today). Approved changes not yet archived: none. T-0056, at the gate, edits none of the README lines E1 and E2 touch (`grep` of its spec for the paragraph and the Spec writer row finds nothing).
- Acceptance commands run as written from `~/dev/spec-factory` under the fresh-HOME wrapper, with `TMPDIR` pointed at my scratch directory, after the GIVEN block. Every one printed exactly the output the spec states for `3e4705a`:
  - "spec add refuses…": `wrapped exit=0 versions=1 added=1 err=`, `worded exit=0 versions=2 added=2 err=`, `good exit=0 versions=3 added=3 err=`.
  - "approve-spec still refuses…": `exit=2 spec not pinned: scenario 'the thing works' has no NEW/REGRESSION label in verification.md`.
  - "A store without current truth…": `exit=0 versions=1`.
  - "A refused draft goes back…" (script and driver): `awaiting-spec-gate spec=1 versions=1 writer=1 critic=1 reason=` twice.
  - "A refusal in the last round parks…" (both pairs): `… reason=harness-bug: unknown STATUS UNKNOWN from critic` twice, then `parked spec=2 versions=2 writer=2 critic=2 reason=max rounds` twice.
  - "The spec writer's next run receives…": `first=0 heading= message= output= source=`.
  - "README, the design doc and the changelog…": `formed=no truth=no round=no edge=no row=no design=no growth=`, `CONTIGUOUS`, `entries=0 terms=0`.
- Not checked: the suite scenario and the claim that exactly five existing tests break. I ran no test suite. The other test files that build an `openspec/` store and store a writer's spec (`_fixtures.py`, `test_capability_index.py`, `test_critic_approved_changes.py`, `test_whole_spec_plan.py`) each carry a labelled `→ NEW`/`→ REGRESSION` line, which is consistent with the spec's count, but the implementer's suite run is the proof.
- `factory stats` normalises a park reason to its first two `: `-separated fields, so the new parks will group as `max rounds: spec not added`, a row of their own beside `max rounds`. That is the normaliser working as designed, not a defect.

## Findings

[BLOCKING] 6 Decisions, first bullet; Evidence, first bullet
Problem: The operator-facing sections use `spec add`, `approve-spec`, an `openspec/` tree and `verification.md` without ever saying what they are, so the gate reader has to infer that `spec add` is the command that stores a writer's draft, `approve-spec` the command the operator runs at the gate, and `openspec/` the directory that holds current truth.
Evidence: The Problem glosses "spec gate", "harness", "current truth" and "round" but names no command and no directory. Evidence's first bullet opens with "`approve-spec` refused" and "`verification.md`"; Decisions' first bullet opens with "When the store has an `openspec/` tree, `spec add` runs the same check as `approve-spec`". The only tie between `openspec/` and current truth is in a fixture comment inside a scenario, which the operator is not expected to read. The Problem's first paragraph also uses "spec gate" and "the harness" one paragraph before their glosses; same fix.
Suggested fix: In the Problem's second paragraph add one sentence each: the harness stores a writer's draft with the command `spec add` and the operator approves with `approve-spec`; current truth lives in the store's `openspec/` directory, and a store without that directory has no current truth; `verification.md` is the part of a spec that labels each scenario NEW or REGRESSION. Then the later sections can use the names as they do now.

[SHOULD-FIX] 6 Operator steps; Risk
Problem: "Upgrade the runtime", "both instances" and "a launch copy" are factory terms a first-time reader cannot place from this spec alone.
Evidence: Operator steps 1 and 2 and the Risk paragraph use them; none of Problem, Evidence or Decisions glosses "runtime" (the pinned checkout the factory runs from) or "instance" (one target repository's `.factory/` and store). Step 2 does gloss the launch copy by what it holds, which is enough.
Suggested fix: One clause each at first use, for example "upgrade the runtime, the pinned harness checkout the factory runs from, and accept it in both instances, this repository's and the Nanobot fork's".

[NIT] 2 Scenario "The spec writer's next run receives the refusal and its refused output"
Problem: `first=$(grep -c 'refused' …)` on the first writer's whole input is a weak proxy for "no refusal section"; a later edit to the instance briefing that happens to contain the word "refused" would fail the scenario with the harness correct (today the briefing contains "refuses" once, so it passes by one letter).
Evidence: Ran the command on `3e4705a`; `grep -c 'refuse'` on the same file prints 1.
Suggested fix: Count the section heading instead, as the second half of the command already does: `first=$(grep -c '^## Your previous output, which the harness refused' run-0001…/input.md)`.

[NIT] 4 Decisions, "The writer's next input is built from what the store already holds"
Problem: The detector treats any READY-FOR-CRITIC or NEEDS-SPLIT writer run with no `spec.added` naming it as refused and re-runs the check now, so a draft the operator stored by hand with `spec add --file` after fixing it would still appear as "refused" in the next writer's input if the original output is malformed, and a draft refused only because current truth has since changed would not appear.
Evidence: Part D's rule as written; `spec.added`'s `source` is the run id only for `--from-run` (`factory/common.py:38`, `factory/cli.py:409`).
Suggested fix: None needed for this ticket; state the edge in the Decision so a later reader does not take the section as a store record of a refusal.

## Out-of-scope observations

- A refusal at `spec add` leaves no event in the store beyond the `ticket.set` round bump; `factory stats` will count the park but cannot count a refusal that was followed by a good draft. The Decisions bullet rejects a refusal record deliberately. If the north-star scorecard later wants "specs the harness bounced", that is a new ticket.

## Prior findings
none (round 1)

STATUS: REVISE
CONFIDENCE: high, every cited path and seven of nine acceptance commands checked by hand on `3e4705a` and matched; the one BLOCKING item is a gloss gap in the human-facing sections, fixable in a few sentences
ESCALATIONS: none
