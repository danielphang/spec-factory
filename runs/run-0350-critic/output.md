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

STATUS: REVISE
CONFIDENCE: high; every cited path, log line and test pin was read, two acceptance commands ran as written and matched, and the one blocking item is a wording rule the rubric states outright.
ESCALATIONS: none
