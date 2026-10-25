## Acceptance
- spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one → NEW; on `3e4705a` it prints `wrapped exit=0 versions=1 added=1 err=`, `worded exit=0 versions=2 added=2 err=` and `good exit=0 versions=3 added=3 err=`: every draft is stored.
- approve-spec still refuses a malformed spec → REGRESSION; it prints `exit=2 spec not pinned: …` on `3e4705a` and on the prototype.
- A store without current truth stores a malformed spec as before → REGRESSION; `exit=0 versions=1` on both.
- A spec writer's NEEDS-HUMAN draft is stored even when malformed → REGRESSION; `exit=0 versions=1` on both.
- A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script → NEW; on `3e4705a` both lines read `awaiting-spec-gate spec=1 versions=1 writer=1 critic=1 reason=`: the wrapped draft is stored and approved, and the writer runs once.
- A refusal in the last round parks with the refusal, quoted safely, in the driver and the script → NEW; on `3e4705a` the first pair reads `parked spec=1 versions=1 writer=1 critic=1 reason=harness-bug: unknown STATUS UNKNOWN from critic` and the second pair reads `parked spec=2 versions=2 writer=2 critic=2 reason=max rounds`: each malformed draft is stored and judged.
- The spec writer's next run receives the refusal and its refused output → NEW; on `3e4705a` it prints `first=0 heading= message= output= source=`: no second writer run exists.
- README, the design doc and the changelog describe the refusal route → NEW; on `3e4705a` it prints every field `no` and `growth=` empty, then `CONTIGUOUS`, then `entries=0 terms=0`.
- The suite passes, only the two listed test files change, and every added test file fails on the base → NEW; on `3e4705a` the second line is `changed= added=0`, so n is 0, not at least 1.

## Responses
- [BLOCKING] Gloss of `spec add`, `approve-spec`, `openspec/` and `verification.md`: FIXED. The Problem's first paragraph no longer uses "spec gate" or "harness" before they are glossed. It now says "the factory's own code". The second paragraph glosses the harness, the store, `spec add` (the command that stores a writer's draft as a new version) and `approve-spec` (the command the operator approves with at the gate). A new third paragraph glosses `verification.md` (the part that lists and labels the acceptance scenarios) and `openspec/` (where current truth lives). It also says that a store without `openspec/` gets no format check. Evidence and Decisions keep their wording and now rely on these glosses.
- [SHOULD-FIX] "runtime", "instance", "launch copy": FIXED. Risk now says what an instance is (one target repository's `.factory/` and store) and names the two. Operator step 1 glosses the runtime as the pinned harness checkout the factory runs from. Step 2 says what a launch copy is.
- [NIT] `first=` counted the word "refused": FIXED. It now counts the section heading `^## Your previous output, which the harness refused`, as the `heading=` field does. The THEN line (`first=0 …`) and the "fails today" text do not change. I could not re-run the command on `3e4705a`: the session's permission check refused to run the GIVEN block. The new pattern is narrower than the old one, because every line that matches the heading also contains "refused". The critic's own run of the old pattern printed `first=0`, so the new one prints `first=0` too.
- [NIT] The derived "refused" section and its edges: FIXED. The Decision now says that the section is derived when the input is built and is not a record of the refusal. It names both edges: a draft later stored by hand with `spec add --file` still shows as refused, and a draft refused only because current truth has changed since then does not show.

## Critic rounds

round 1 · spec v1 · run-0574-critic · REVISE

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

round 2 · spec v2 · run-0576-critic · APPROVE

# Critic review: T-0057 spec v2 (round 2)

## What I checked

- Scope this round: the four responses, the v1 to v2 diff (Problem paragraphs 1 to 3, the derived-section Decision, Risk, Operator steps, and the `first=` field of one acceptance command), and whether anything unchanged is BLOCKING and missed in round 1.
- `main` is still at `3e4705a`, with no local edits under `factory/`, `tests/`, `README.md` or `docs/`, so the round-1 path checks stand.
- The one acceptance command that changed. The writer said the session refused to re-run it. I ran the GIVEN block and the scenario "The spec writer's next run receives the refusal and its refused output" as the spec gives it, from `/Users/dphang/dev/spec-factory` under the fresh-HOME wrapper with `TMPDIR` in my scratch directory. On `3e4705a` it printed `first=0 heading= message= output= source=`, exactly the stated fails-today line. The ticket ended `awaiting-spec-gate` with one writer run and one critic run, as the verification line describes. The new `first=` pattern counts the section heading, so it no longer depends on the word "refused" appearing elsewhere in the briefing.
- The new Problem text against the writing standard (`docs/writing.md`). Paragraph 1 says what is wrong (the operator approves a spec and the code refuses it over a format mistake) and for whom (the operator). Paragraph 2 glosses the spec gate, the harness, the store, `spec add` and `approve-spec` before Evidence or Decisions use them. Paragraph 3 glosses `verification.md` and `openspec/`, and says a store without `openspec/` gets no check. Paragraph 4 glosses the round and the park. Every term of art the Evidence and Decisions sections lead with now has a gloss earlier in the Problem.
- Approved changes not yet archived: none, unchanged from round 1. T-0056 at the gate touches none of the README lines this change edits, as checked in round 1.
- Not checked, as in round 1: the suite scenario and the count of five breaking tests. The implementer's suite run is the proof.

## Findings

[NIT] 6 Problem, paragraphs 1 and 2
Problem: Paragraph 1 calls the harness "the factory's own code" and paragraph 2 then introduces "the harness" as a new name for the same thing, so the reader meets two names for one concept before the gloss ties them together.
Evidence: v2 diff, Problem paragraph 1 ("the factory's own code refuse it") and paragraph 2 ("The harness is the code that stores specs and moves tickets between agents"); `docs/writing.md` rule 9, one name per concept.
Suggested fix: In paragraph 2 write "The harness, that code, stores specs and moves tickets between agents", or leave it; a careful reader connects the two.

## Prior findings

- [BLOCKING] Gloss of `spec add`, `approve-spec`, `openspec/` and `verification.md`: RESOLVED. Each is glossed in the Problem's second or third paragraph, and "spec gate" and "harness" no longer appear in paragraph 1 before their glosses.
- [SHOULD-FIX] "runtime", "instance", "launch copy": RESOLVED. Risk glosses the instance and names both; Operator step 1 glosses the runtime; step 2 glosses the launch copy.
- [NIT] `first=` counted the word "refused": RESOLVED. The field now counts the section heading; I ran the changed command on `3e4705a` and it prints the stated `first=0`.
- [NIT] The derived "refused" section and its edges: RESOLVED. The Decision states that the section is derived when the input is built, is not a record, and names both edges.

## Out-of-scope observations

- As in round 1: a refusal followed by a good draft leaves no store event of its own, so `factory stats` cannot count bounced specs. The spec rejects a refusal record on purpose. A later ticket if the scorecard wants that figure.
