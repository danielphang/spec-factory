Commit: a78de4b5a03a3c2f87e9976542035fb4a1ab0f07 (branch `factory/T-0023.2`, base `2e61b852d1da27a85208eb94c8d10b8a5557e2c7`; `git status --porcelain` in the worktree is empty)

Round 1.

## What I checked, and how

1. Test integrity. `git diff --stat main...HEAD` lists seven files: `README.md`, `docs/changelog.md`, `factory/cli.py`, `factory/compose.py`, `factory/subtickets.py` and the two new test files `tests/factory/test_replan.py` and `tests/factory/test_resolve_rulings.py`. No existing test file, CI config, `AGENTS.md`, skill or prompt is touched. The sub-ticket's "Tests to change: none" holds.

2. Correctness, against the parent spec v2 parts A and I and the sub-ticket's notes. I read the three changed functions in the worktree and ran every acceptance WHEN of the sub-ticket verbatim, in bash, under the HOME wrapper, with `TMPDIR` set to my scratch directory and the parent's GIVEN block written there first (`scratch/accept.sh`). Every result matches the THEN:
   - BLOCKED ruling: `exit=0 ready-for-implementer pr=0`, `ruling=kept`, `in_input=1`. The park is accepted, the round is untouched, the ruling file is byte-identical, and the implementer's composed input carries it.
   - ESCALATE from critic: `exit=0 ready-for-critic`. The old route is unchanged.
   - Re-plan: `exit=0 ready-for-planner`, `in_input=1 listed=2`. The planner input ends with the `## Sub-tickets already under T-0001` section, its lead sentence, and `- T-0001.1 / First: merged`, `- T-0001.2 / Second: merged`, exactly as I4 specifies.
   - Re-plan refused while a sub-ticket is closed: `names=1`, then `parked spec-v1.yaml ` (still parked, no ruling file).
   - Later plan: `"id": "T-0001.3"`, `"depends_on": ["T-0001.2"]`, `"ready": ["T-0001.3"]`.
   - Reused id: `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `.
   - README: `replan=1 gap=0`. Changelog: `51 CONTIGUOUS`, then `4`.
   - New test files: `20 passed in 12.90s`, exit 0.
   The refusal and section texts in the code (`factory/cli.py:757, 785, 788, 791, 801`; `factory/subtickets.py:58`; `factory/compose.py:162-164`) match the spec's wording character for character, and the changelog clause and the README Unstick row match J1 (S1) and J2 verbatim.

   Edge cases the spec implies (my own probes, same harness):
   - `--replan` on a sub-ticket or an unparked parent is refused with the parked-parent message, naming the actual state (`T-0001.1 is merged`, `T-0001 is planned`).
   - A later plan with the explicit label `T-0001.3` and `Depends on: .1` yields `"id": "T-0001.3"`, `"depends_on": ["T-0001.1"]`: the `.n` shorthand reaches an existing sub-ticket.
   - With an existing `T-0001.10`, the planner section lists `.1, .2, .10` in numeric order and the next plan takes `T-0001.11`: `store.subtickets_of` sorts by integer index (`factory/store.py:221`) and `parse` takes the max index, not the count (`factory/subtickets.py:59`).
   - Labels `T-0001.4` then `T-0001.3` with `Depends on: T-0001.4`: refused with "cannot resolve", not silently mis-wired. This is the pre-existing ambiguity the PR's Known gaps names; the parent's Decisions rejected honouring explicit ids, so it stays.

3. Scope. Everything in the diff is parts A, I, J1 (S1 clause), J2 and J4. The one addition the spec did not spell out, "a re-plan" in the Unstick row's "What you decide" cell, is declared in the PR description and is the same row J2 edits. J4: the status date already reads `2026-10-04` (`README.md:9`), today. No `--redispatch`, `init_cmd`, `build.js`, `docs/design.md` or `dev/build-harness.spec.md` change.

4. Silent behaviour changes. Three, all ordered by the spec: the `--ruling` refusal text (A1), a planner input that gains a section only when the parent already has sub-tickets (I4), and `subticket add` on a parent that already has sub-tickets now adds instead of refusing `already exists` (I1, I2). See Out-of-scope observations for the last one's side effect.

5. Security and data safety. `--replan` copies a human-given file into the store with `shutil.copyfile`, exactly as `--ruling` already does. Every refusal happens before `copyfile` and `move`, so a refused re-plan writes no ruling and no resolve record; the acceptance run and `test_a_replan_is_refused_while_a_sub_ticket_is_not_merged_and_writes_nothing` confirm it. No destructive operation, no secret, no new path outside the store.

6. Protected paths. `factory/cli.py`, `factory/compose.py`, `factory/subtickets.py`: all three are declared on the sub-ticket's "Protected paths" line and in the parent's Risk section. Listed under ESCALATIONS; the merge gate needs a human approval.

7. Coding standard. Rule 1: the new code reuses `store.subtickets_of`, `_next_n`, `_rel`, `move` and `shutil.copyfile`; no new helper, type or dependency. Rule 2: the PR description names the callers of `parse`, `resolve` and `compose`; I confirmed `parse` has one production caller (`factory/cli.py:407`) and the two test callers keep the default `existing=()`. Rule 3: no shortcut with a known limit; "factory: markers added: none" is stated. Rule 5: `replan`, `ruling`, `merged` are the names the README and store already use. Rule 6: neither test file patches a path. Lean already.

8. Gates, run exactly as written from the worktree on `a78de4b`:
   - `git diff --check main...HEAD` exited 0: no whitespace errors.
   - `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `235 passed in 185.40s (0:03:05)`: the 215 tests on base plus the 20 new ones.
   - The REGRESSION scenario "The harness suite passes with an uncommitted harness edit" printed `235 passed in 210.18s (0:03:30)`, and no `/tmp/t0023-suite.*` directory remained. The new test files run `bin/factory` on `tmp_path` stores, so the harness lock does not reach them mid-edit.

## Findings

- [SHOULD-FIX] PR description: What changed: "sub-ticket" and "routing table" are used at first mention without a gloss ("an implementer (the agent that writes the code for one sub-ticket)"; "state changes the routing table already allows"). The writing standard's reader is new to this system and has not read the parent spec, which is where these are glossed → the operator at the gate reads two factory-made names before learning what they are. One clause each would do: a sub-ticket is one unit of a ticket's plan, built and merged on its own; the routing table is the list of state changes the harness allows.

No BLOCKING finding. net: Lean already.

Prior findings: none (round 1).

## Out-of-scope observations

- `subticket add` has lost its collision safety net for a planner re-run outside `--replan`. Before this change, a second plan on a parent that already had sub-tickets was refused with `T-0001.1 already exists`. Now it is numbered after them, whatever their state, because I2 passes the existing ids and says "its other checks are unchanged". A parent sent back with a plain `ticket transition parked → ready-for-planner` after a successful `subticket add --run` would therefore gain `.3`, `.4` beside live `.1`, `.2`. The parent puts a re-plan while any sub-ticket is not merged out of scope, so this is the spec's choice, not a defect of this PR. A guard in `subticket_add` refusing when any existing sub-ticket is not `merged` or `closed` would be a one-line follow-up.
- A BLOCKED ruling is accepted on any parked ticket whose reason starts with `BLOCKED`, not only on a sub-ticket. On a parent ticket it moves the parent to `ready-for-implementer`, a state no parent should hold (probe: `exit=0 ready-for-implementer` on T-0001 parked `BLOCKED from implementer` from `ready-for-spec-writer`). Only an implementer parks with BLOCKED, and it only runs on sub-tickets, so no real path reaches this. The spec did not ask for the check.
- The implementer's zsh observation is correct. Under zsh the refused-re-plan scenario prints `names=2` because `2>&1 >/dev/null |` sends stdout to both targets (MULTIOS), and a refusal prints its text on stderr and in the JSON `error` on stdout. Under bash it prints `names=1`. The code is right; the scenario's expected value holds only in a POSIX shell.
- The README now describes `--replan` and the BLOCKED ruling above "Where this can go" although neither has run on a real ticket, against "Maintaining this page". The approved spec orders the J2 edit and the acceptance check `gap=0` requires it, so the spec wins here; the implementer declares it under Known gaps.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance WHEN of the sub-ticket, both gates and the uncommitted-edit suite scenario ran on the committed head with the outputs above; the diff is confined to the lettered parts and the three declared harness files.
ESCALATIONS:
- Protected paths touched, all declared on the sub-ticket's "Protected paths" line and in the parent's Risk section: harness `factory/cli.py`, `factory/compose.py`, `factory/subtickets.py`. The merge gate needs a human approval for these.
- The scenario "A re-plan is refused while a sub-ticket is not merged" prints `names=2` under zsh and `names=1` under bash or sh, as the implementer reported and I reproduced. Decide: the verifier runs this change's scenarios in bash, or a later spec revision sends stderr to a file and greps that file. No code change is needed.
