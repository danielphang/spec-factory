Sub-ticket: T-0023.2 (plan label T-0023-S1), "Resolve verbs: a ruling on a BLOCKED park, and re-plan after a failed parent close (parts A and I)". Parent: T-0023, approved spec v2 (issue #39). Branch `factory/T-0023.2`, commit `a78de4b` on base `2e61b85`.

## What changed

A ticket is "parked" when the harness stops and waits for a human, and `factory resolve` is the command a human runs to move it on. Before this change, two common parks had no supported way out. An implementer (the agent that writes the code for one sub-ticket) that reported BLOCKED could not be given a ruling. A parent ticket whose final whole-spec check failed after all its sub-tickets merged could not be sent back for a fix plan. Both now have a `resolve` mode, and both use state changes the routing table already allows.

**Part A (H1): `--ruling` accepts a BLOCKED park.** `factory/cli.py` `resolve`, the `--ruling` branch (lines 750-757):
- A park whose reason starts with `BLOCKED` now returns the sub-ticket to `ready-for-implementer`.
- The round is left as it was. The ruling is copied to the next `approvals/<id>/ruling-<n>.md`, as for ESCALATE. No compose change was needed: the implementer's input already includes every ruling file (`factory/compose.py`, the implementer branch).
- ESCALATE parks route as before: to the planner if the reason names the planner, otherwise to the critic.
- NEEDS-HUMAN and CLARIFY parks are still told to `use --answer`.
- Every other refusal now reads `--ruling applies to an ESCALATE or BLOCKED park; <id> is <state> (<reason>)`.

**Part I (H9): re-plan after a failed parent-close check.** The parent-close check is the last verifier run, on the merged result, after every sub-ticket has merged.
- I1, `factory/subtickets.py` `parse(planner_output, parent, existing=())`. `existing` is the list of the parent's sub-ticket ids already in the store.
  - New sub-tickets are numbered from the highest existing index plus 1. With no existing sub-tickets they still start at 1.
  - A plan head line that reuses an existing id is refused: `<label>: <label> is already a sub-ticket of <parent>; give the new sub-ticket another id`.
  - A `Depends on:` reference that names an existing sub-ticket is kept as a dependency. That check comes after the new-id and label lookups and before the "not a sub-ticket of this plan" refusal.
  - The module docstring now says this.
- I2, `factory/cli.py` `subticket_add` (line 407): it passes the existing ids from `store.subtickets_of`. Its other checks are unchanged.
- I3, `factory/cli.py` `resolve`: new `--replan F`, tried after `--redispatch` and before `--close` (lines 783-796; the option is at line 1149).
  - It is refused unless the ticket is parked: `--replan applies to a parked parent; <id> is <state>`.
  - It is refused when the ticket has no sub-tickets: `--replan applies to a parent with sub-tickets; <id> has none`.
  - It is refused when any sub-ticket has not merged. The message names each one with its state, for example `--replan needs every sub-ticket merged: T-0001.2 is closed`.
  - Otherwise it copies F to the next `approvals/<id>/ruling-<n>.md` and moves the ticket to `ready-for-planner`. The record has kind `replan` and the ruling path. The round is unchanged.
  - `--decision` now refuses `--replan` too, and the "resolve needs one of" message lists `--replan F`.
- I4, `factory/compose.py`, the planner branch (lines 160-164): when the parent has sub-tickets, a section is appended after the rulings. It is headed `## Sub-tickets already under <tid>` and its first line is the one in the spec. Then comes one line per sub-ticket, `- <id> / <title>: <status>`, in id order. With no sub-tickets the planner's input is unchanged. `build.js` is unchanged, as I4 says.

**J1, J2, J4 (documents).**
- `docs/changelog.md`, entry 51: the S1 clause from J1 is appended to the existing single line. There is no new entry number.
- `README.md`, "Where a human decides", Unstick row: `--ruling F` now says "(a role escalated, or an implementer reported itself blocked)". After `--redispatch` there is the J2 text for `--replan F`.
- `README.md`, "Gap, as of today" paragraph: its first two sentences are deleted, and the tripwire sentence is the J2 wording.
- One addition the spec did not spell out: the row's "What you decide" cell gains "a re-plan", so that it matches the new verb.
- J4: the status-header date is already `2026-10-04`, which is today and the expected merge date, so it is unchanged.

**Callers checked (coding rule 2).** `subtickets.parse` has one production caller, `cli.subticket_add`. Its test callers in `tests/factory/test_subtickets.py` (lines 185 and 209) use the default `existing=()`, so their behaviour is the same. `resolve` is reached only from the CLI: `grep -n resolve factory/workflows/*.js` finds nothing. `compose.compose` has one caller, `cli.run_compose`.

## Acceptance results

All commands ran from the worktree root, inside the HOME wrapper. Where a command needed the fixture scripts, `TMPDIR` pointed to my scratch directory, and I first wrote `t0023-parent.sh` and `t0023-closed.sh` there from the parent's GIVEN block, verbatim. I did not write `t0023-wf.mjs`, because none of this sub-ticket's scenarios uses it. Unless noted, the outputs below are from bash. See "Known gaps" for one zsh difference.

| Scenario | Kind | Before (base `2e61b85`) | After (`a78de4b`) |
|---|---|---|---|
| A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling | NEW | `exit=2 parked pr=0` / `ruling=missing` / `in_input=0` | `exit=0 ready-for-implementer pr=0` / `ruling=kept` / `in_input=1` |
| A ruling on a critic ESCALATE still returns the ticket to the critic | REGRESSION | | `exit=0 ready-for-critic` |
| A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | NEW | `exit=2 parked` / `in_input=0 listed=0` | `exit=0 ready-for-planner` / `in_input=1 listed=2` |
| A re-plan is refused while a sub-ticket is not merged | NEW | `names=0` / `parked spec-v1.yaml ` | `names=1` / `parked spec-v1.yaml ` under bash and sh. zsh prints `names=2` (Known gaps). |
| A later plan's sub-tickets take the next free ids and may depend on a merged sibling | NEW | `"ready": []` only | `"id": "T-0001.3"` / `"depends_on": ["T-0001.2"]` / `"ready": ["T-0001.3"]` |
| A plan that reuses an existing sub-ticket id is refused and writes nothing | REGRESSION | | `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `. The refusal now comes from the reused-label check. `test_replan.py` asserts its text. |
| The README describes the new resolve verbs | NEW | `replan=0 gap=1` | `replan=1 gap=0` |
| Intermediate check: the changelog entry carries this seam's clause | NEW | `51 CONTIGUOUS` / `1` (only S4's `uncommitted`) | `51 CONTIGUOUS` / `4` |
| Intermediate check: the new test files pass | NEW | 14 failed, 6 passed. The 6 that pass are the unchanged behaviours: the two ESCALATE routes, the NEEDS-HUMAN refusal, a first plan's input, first-plan numbering and the unknown-dependency refusal. | `20 passed in 11.25s` |
| The harness suite passes with an uncommitted harness edit | REGRESSION | | `235 passed in 191.97s (0:03:11)`. Afterwards no `/tmp/t0023-suite.*` directory was left. |
| The change adds no whitespace errors | REGRESSION | | `exit=0` |

How the meanings above were read:
- `pr=0` means the round was not touched.
- `ruling=kept` means the ruling file is byte-identical to F.
- `in_input=1` means the ruling text is in the implementer's composed input.
- `listed=2` means both sub-ticket lines appear exactly as specified.
- `4` means the entry contains `BLOCKED`, `--replan`, `next free` and `uncommitted`.

For the "Before" column of the new test files, I copied both files into a clean clone at the base commit and ran them there.

Gate commands, each run exactly as written on `a78de4b`:
- `(export HOME=…; git diff --check main...HEAD)` exited 0. No whitespace errors.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `235 passed in 158.95s (0:02:38)`. That is the 215 tests from before this change plus the 20 new ones.

## Tests added/changed

- New: `tests/factory/test_resolve_rulings.py`, 7 tests (A3).
  - A BLOCKED ruling: the state, the round left at its pre-set value of 1, `parked` cleared, the ruling file, and the ruling in the composed implementer input and its sources.
  - A second BLOCKED ruling takes `ruling-2`.
  - ESCALATE from the critic and ESCALATE from the planner route as before.
  - NEEDS-HUMAN still says `use --answer`.
  - The new refusal text, on another park reason and on an unparked ticket. In both cases nothing is written.
- New: `tests/factory/test_replan.py`, 13 tests (I5).
  - The re-plan move: the JSON result, the history and resolve record, the round unchanged, merged sub-tickets still merged, the ruling file, and the planner input. The input has the ruling before the sub-ticket section and the section's exact text.
  - The refusals: a sub-ticket not merged (nothing written), every unmerged sub-ticket named, no sub-tickets (nothing written), the parent not parked, `--decision` with `--replan`, and the "needs one of" message.
  - A first plan's planner input has no sub-ticket section, and a first plan is still numbered from `.1`.
  - A later plan takes `.3` and `.4`. Its dependencies on a merged sibling, by full id and by the `.1` shorthand, are kept, and `ready-implementers` releases `.3`.
  - Numbering follows the highest existing index, not the count.
  - A reused label is refused with the exact message, and no ticket or spec file is written.
  - A dependency on a sub-ticket that does not exist is still refused.
- Both files drive `bin/factory` on throwaway stores (`FACTORY_STATE` under `tmp_path`), as the plan asks. The suite scenario confirms they pass in a checkout with an uncommitted harness edit.
- Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- **The not-merged refusal scenario prints `names=2` under zsh.** Under bash and sh it prints `names=1`, as specified. The reason is zsh's MULTIOS option: zsh sends stdout both to `/dev/null` and into the pipe in `2>&1 >/dev/null |`. A refused command prints its refusal on stderr and also as the `error` field of a JSON line on stdout, so grep counts two lines. That stdout behaviour already existed (the parent's Evidence for H2). With `setopt NO_MULTIOS`, zsh prints `names=1`. The code is correct; the expected output holds only in a POSIX shell. A verifier that runs scenarios in zsh, as this environment's tool shell does, will see `names=2`.
- **The README now describes behaviour that has not yet run on a real ticket.** "Maintaining this page" says a thing appears above "Where this can go" only after that. I made the J2 edit because the approved spec orders it, and the old "Gap" sentence would otherwise be false once this merges.
- **A pre-existing ambiguity, not introduced here.** If a plan uses `T-0001.n` labels that do not match the ids the store assigns, a `Depends on: T-0001.n` resolves to the assigned id first. An example is labels `T-0001.4` then `T-0001.3`, numbered `.3` and `.4`. With this change that can also happen in a re-plan. The parent's Decisions rejected honouring explicit ids, so I did not change this.
- `factory:` markers added: none.

## Out-of-scope observations

- The parent's own out-of-scope note still holds: `resolve --ruling` on `ESCALATE from reviewer` sends the sub-ticket to `ready-for-critic`. The design (`docs/design.md` line 102) returns it to the implementer instead. I did not touch that route.
- `resolve --replan` writes F as a ruling, and the planner already receives every ruling of the parent, so the planner also sees older rulings from the first plan. That is consistent with how rulings work today. I note it only because a re-plan's input may now include stale rulings.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run on the committed head, with the outputs above, and the new tests were shown to fail on base. The one exception is the not-merged refusal scenario, which matches only under a POSIX shell.
ESCALATIONS:
- The scenario "A re-plan is refused while a sub-ticket is not merged" prints `names=2` instead of `names=1` when run under zsh. A verifier using zsh would report a false failure. Under bash or sh, it prints `names=1`. Decide: run this change's scenarios with bash, or, at the next spec revision, amend the scenario to send stderr to a file and grep that file, for example `2>$T23/err >/dev/null; grep -c T-0001.2 $T23/err`, as other scenarios in this spec already do. The harness behaviour that causes it, refusals echoed as JSON on stdout, is by design and out of scope.
