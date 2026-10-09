## Acceptance

Each NEW item below was run on this checkout (`main` at `51e2af7`) and printed the "today" output shown. Each item except the documents scenario was also run, verbatim under bash, on a scratch prototype of design.md A-E and printed its THEN. The prototype changed no documents, so the documents scenario printed its "today" line there too. Those runs are from round 1 (run-0346). In round 2, `main` is still at `51e2af7`, and three NEW items were run again verbatim under the HOME wrapper, with the fixtures written to this run's scratch directory. "After a re-spec and a re-plan...", "The build of a re-planned parent..." and "A plan that depends on an old unmerged sub-ticket..." printed exactly the "today" output below. The prototype was not rebuilt in round 2, because this round changes only the wording of proposal.md.

- After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept → NEW. Today it prints `add: ` (no `superseded` in the output), `ready: "ready": ["T-0001.4"]`, `closed: "closed": ["T-0001.2"]`, `superseded: ` (no such list), `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=0`.
- The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version → NEW. Today it prints `moved: `, then `unrecorded: `: there is no `superseded` list, and `ticket set ... planned_from=` is refused as an unknown key. An implementation that read `spec.approved_version` instead would leave `T-0001.3` out of the `moved` list (worked from the rule in design.md B; not run).
- A second plan at the same approved version supersedes nothing → REGRESSION (prints its THEN today).
- A plan that depends on an old unmerged sub-ticket is refused and writes nothing → NEW. Today it prints `exit=0 names=0 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml `: the plan is accepted.
- A re-specced parent's planner input names the sub-tickets its plan supersedes → NEW. Today it prints `said=0 listed=3`.
- The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one → NEW. Today it prints `park T-0001: sub-ticket closed by a human: T-0001.2`, the Nanobot T-0024 park.
- A sub-ticket of the current plan that a human closed still parks the parent → REGRESSION (prints its THEN today).
- With the new plan merged, the re-planned parent reaches its final check and closes → NEW. Today it prints `check: "state": "planned"`, then `close=2 planned`.
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list → REGRESSION (current truth, unchanged).
- A re-plan is refused while a sub-ticket is not merged → REGRESSION (current truth, unchanged).
- A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets → NEW. Today it prints `exit=2 parked`. The refusal is `--replan needs every sub-ticket merged: T-0001.2 is closed, T-0001.3 is waiting-dependencies`.
- The design doc, build spec, README and changelog record superseded plans → NEW. Today it prints `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS`.
- The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors → REGRESSION (prints `whitespace=ok untouched=0` on `main`).

## Responses

- [BLOCKING] 6, unglossed "target" and "`factory-store`": FIXED. The Problem's first paragraph now reads "ticket T-0024 on Nanobot, one of the repositories the factory builds in", with no "target". Operator steps now read "On `factory-store`, the branch that holds Nanobot's ticket state". They also gloss `--accept-harness` as the step by which the operator moves Nanobot onto a harness revision, and no longer say "instance".
- [SHOULD-FIX] 6, first paragraph does not say who has the problem: FIXED. The first paragraph now names the operator, glossed as "the person who runs the factory and approves its work". It says the operator can get past the stop only by hand-editing the files where the factory keeps each ticket's state. The Problem now calls the person "the operator" throughout, in place of "the human". The quoted park reason "sub-ticket closed by a human" keeps its words.
- [NIT] 6, "pinned" unglossed: FIXED. Paragraph four now says T-0027 "adds a command that amends an approved spec after planning". It also introduces T-0027 as "approved but not yet built".
- Also changed, for one name per concept (writing standard rule 9): the Problem, Evidence, Out of scope, Risk and Operator steps now all call the Nanobot fix "the hand-made workaround", in place of a mix of that and "stand-in". One Decision now says "the operator approves with `approve-spec --edit`", in place of "the human". The design, the specs and the acceptance are unchanged from v1.

## Critic rounds

round 1 · spec v1 · run-0350-critic · REVISE

Round 1 review of T-0038 spec v1.

Spot-checks (all on `main` at `51e2af7`, the checkout the spec names):
- Cited code: `factory/store.py:228-235` `subtickets_of` (glob, sorted by id), `factory/cli.py:438-468` `subticket_add`, `471-484` `_create_subtickets` (writes `st["spec"]` at 478; nothing records the plan), `549-566` `ticket_ready_implementers` (every list from every sub-ticket), `738-751` `ticket_parent_check` (all-merged test), `912-917` `--replan` refusal, `1302-1306` `_reused_subticket_run`, `1335-1341` `_parent_close_verified`, `161-167` and `1365` guards, `680-688` merge release, `255` sibling-tests read, `492-495` `_planner_needed`, `factory/compose.py:318-322` planner section, `factory/workflows/build.js:264` park, `factory/subtickets.py:141` `ready_implementers`, `tests/factory/test_replan.py:108` `endswith` pin, `docs/design.md:109`, `dev/build-harness.spec.md:286` (the one line matching `ready-implementers PARENT`), `results/<head>/superseded-<n>/` at `cli.py:885-907`. All as described.
- Nanobot log, read only: lines 1392, 1396-1398, 1730-1732, 1751, 1753, 1780-1781 of `.factory/store/log/2026-10.jsonl` say what the Evidence says; `tickets/superseded/T-0024.1.yaml` exists with `approved_version: 2`, `T-0024.2.yaml` has 4.
- Tests pinning behaviour the Decisions touch: `test_shepherd.py:385` (`closed` list), `test_replan.py:108,117,127` (planner section bytes, `--replan` refusals), `test_build_startup.py:84-91` (`subtickets`, `remaining`). Each uses one approved version per parent, where the split marks nothing superseded, so none pins the overturned behaviour. "Tests to change: none" holds as far as reading goes; the `384 passed` claim I could not check without running the suite.
- `ticket set` (`cli.py:97-107`) accepts only a key already in the record, so `planned_from=` works once A writes the field at creation and clears it to null, as the fallback scenario needs. `approve-spec --edit` (`cli.py:788-789`) always adds a version, as the same-version Decision relies on. `ready_implementers` treats a closed sibling dependency as unmet (`subtickets.py:152-153`), which is why T-0001.3 is not in today's `ready`.
- Ran the two no-suite acceptance commands as written, under the HOME wrapper. Documents scenario printed `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS`; whitespace scenario printed `whitespace=ok untouched=0`. Both match the verification's "today" lines.
- Consistency: T-0023 decisions (same-version re-plan, next free ids, depends on existing) are kept, with the superseded exception declared. T-0027 v2 Decisions (its line 66, the moved `spec` record) are handled by `planned_from` and the fallback; both merge orders hold, and Risk says so. No `docs/prompts/` block contains `docs/design.md:109`.

Findings

[BLOCKING] 6 proposal.md, Problem first paragraph and Operator steps first paragraph
Problem: Two terms this system made up appear in a human-facing first paragraph before any gloss: "the Nanobot target's T-0024" (target: a repository the factory works on, a row of the README's terms table) and "Nanobot's `factory-store`" (the branch that holds a target's store, another row).
Evidence: `README.md:135` defines target and `README.md:137` defines `factory-store`; the Problem glosses them nowhere, and the Operator steps rely on the briefing's gloss, which the gate operator has not read. Rubric 6 makes an unglossed system term in a first paragraph BLOCKING even when a careful reader could work it out, so I am not waiving it; it is a one-clause fix at each site.
Suggested fix: Problem: "It happened on 2026-10-08 to ticket T-0024 on Nanobot, one of the repositories the factory builds in, and the operator now runs that ticket on a hand-made workaround." Operator steps: "on `factory-store`, the branch that holds Nanobot's store".

[SHOULD-FIX] 6 proposal.md, Problem first paragraph
Problem: The paragraph says what is wrong (the build stops for good) but names who has it only by implication; the affected people arrive in paragraph four.
Evidence: Writing standard rule 1 asks that a reader stopping after the first paragraph can say who has the problem.
Suggested fix: Add to the first sentence "and the operator can only hand-edit store records to get past it", or fold the suggested rewrite above, which names the operator.

[NIT] 6 proposal.md, Problem paragraph four
Problem: "a command that amends a pinned spec" uses "pinned" without saying what a pinned spec is.
Evidence: First use of "pinned" in the spec; the term is not general.
Suggested fix: "amends an approved spec after planning" or add "(the approved version the build works from)".

Not checked, for the implementer and verifier: the prototype outputs of the NEW scenarios, in particular that `_parent_close_verified` accepts the fixture's verifier run in "With the new plan merged, the re-planned parent reaches its final check and closes" (the fixture's merges carry no `main_after`, so the head test is vacuous there, which is fine for what the scenario tests), and `384 passed`. Both need the change built.

Substance: no blocking issue. The split rule (unmerged and `planned_from` below the parent's highest) handles the Nanobot stand-in record without migration, the T-0027 moved record, and the same-version re-plan; the `Depends on` refusal plus the planner line close the only way a new plan could wait on a superseded sub-ticket; every lettered part is needed; the protected path is declared.

Out-of-scope observations: none.

round 2 · spec v2 · run-0354-critic · APPROVE

Round 2 review of T-0038 spec v2.

Scope of this round: whether the three round-1 findings are resolved, and the text that changed. Per the v1→v2 diff, only proposal.md changed (Problem, Evidence, Out of scope, one Decision, Risk, Operator steps, all wording) plus the verification's preamble and a new Responses section. design.md, the four spec files and the acceptance items are byte-for-byte unchanged, so the round-1 spot-checks of cited code, log lines, test pins and consistency stand.

Spot-checks this round (`main` still at `51e2af7`, `git rev-parse --short HEAD`):
- Re-read `factory/store.py:228-235` (`subtickets_of`: glob of `tickets/<parent>.*.yaml`, sorted by index) and `factory/cli.py:438-484` (`subticket_add`, `_create_subtickets` writing `st["spec"]` at 478 and nothing about the plan). Both as the Root cause says.
- Ran both no-suite acceptance commands as written, under the HOME wrapper, from `~/dev/spec-factory`. Documents scenario printed `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS`; whitespace scenario printed `whitespace=ok untouched=0`. Both match the verification's "today" lines.
- Grepped proposal.md for the words the Responses say were removed: no "stand-in", no "the human", no "pinned", and "target"/"instance" no longer appear in Problem or Operator steps. The park reason "sub-ticket closed by a human" is kept verbatim, as the Responses say.
- Read the five human-facing sections as the gate operator. Problem, paragraph one, now says what is wrong (the build stops for good on old-plan work), for whom (the operator, glossed), and the cost (hand-editing ticket state files). "Nanobot" is glossed as one of the repositories the factory builds in. Evidence, Decisions and Open questions use only terms the Problem glossed earlier or gloss them inline (`planned_from` is defined in its first sentence). Operator steps gloss `factory-store` and `--accept-harness`.

Prior findings:
- [BLOCKING] 6, unglossed "target" and "`factory-store`" in Problem and Operator steps: RESOLVED. Problem reads "ticket T-0024 on Nanobot, one of the repositories the factory builds in"; Operator steps read "On `factory-store`, the branch that holds Nanobot's ticket state".
- [SHOULD-FIX] 6, first paragraph does not say who has the problem: RESOLVED. The operator is named and glossed in the first sentence, and the second sentence says what they must do by hand.
- [NIT] 6, "pinned" unglossed: RESOLVED. Now "amends an approved spec after planning", with T-0027 introduced as "approved but not yet built".

Findings

[SHOULD-FIX] 6 proposal.md, Operator steps first paragraph
Problem: "a harness revision that contains this change" uses "harness", this repo's name for its own program (README terms table, `README.md:44` and `:138`), with no gloss anywhere in proposal.md; the word's only earlier use is the Evidence's last paragraph ("the harness suite"), also unglossed.
Evidence: `grep -n harness` over proposal.md finds first use at the Evidence's final paragraph and again in Operator steps; neither says what the harness is. I did not raise this in round 1 on the v1 wording ("accepts a harness with this change"), and I am not blocking on it now: "harness" is a common word for the program that drives an agent pipeline, and a deeply technical reader lands on the right meaning from `--accept-harness` and "revision". It is still a system term a first-time reader has to infer.
Suggested fix: "Once Nanobot runs a revision of the harness, the factory's own program, that contains this change (...)".

[NIT] 6 proposal.md, Risk third paragraph
Problem: "The change reaches a target only after the runtime is moved to a revision that contains it and the instance accepts that harness" uses "target", "runtime" and "instance" where the Problem and Operator steps now say "Nanobot, one of the repositories the factory builds in" and `--accept-harness`; one concept, two vocabularies (writing standard rule 9).
Evidence: Risk is not one of the sections the rubric holds to the first-paragraph rule, so this is not blocking; the Responses say "instance" was removed, which is true of Operator steps but not of Risk.
Suggested fix: "The change reaches a repository the factory builds in only after that repository is moved onto a harness revision that contains it with `--accept-harness`."

Not checked, as in round 1 and unchanged: the prototype outputs of the NEW scenarios and `384 passed` need the change built; the implementer and verifier own them. The verification's new statement that three NEW items were re-run in round 2 is consistent with the "today" lines I reproduced for the two no-suite items, but I did not re-run the three fixture-based items myself.

Substance: unchanged from round 1 and still sound. The split rule (unmerged and `planned_from` below the parent's highest) covers the Nanobot record without a migration, the T-0027 moved record, and the same-version re-plan; the `Depends on` refusal and the planner line close the one route by which a new plan could wait on a superseded sub-ticket; every lettered part is needed; "Tests to change: none" holds against the pins I read in round 1 (`test_shepherd.py:385`, `test_replan.py:108,117,127`, `test_build_startup.py:84-91`, each one approved version per parent); the protected path `factory/**` is declared.

Out-of-scope observations: the dev checkout has an untracked file `.factory/answers/T-0037-answer.md` (`git status --short`). It belongs to another ticket and does not touch this spec.
