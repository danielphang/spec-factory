Sub-ticket: T-0016.1 (parent T-0016, approved spec v1). Branch `factory/T-0016.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0016.1`, base `924513ecb731b57f4396b602ff31a1169150b3e3`, head `d45f0601ba30199152da28af556513dd2fc0caf0` (two commits: `50fd7a3` the change, `d45f060` a fix to the new test file).

## What changed

Each build used to run the full test suite about six times when only two of those runs could change the verdict. It also started a parent-close run that repeated a check already made. A parent-close run is the final verifier run on the merged code, made after every sub-ticket has merged. This change removes the runs that cannot change a verdict. Every refusal the checks gave before still happens.

- **A. Implementer prompt.** Changed in three places: the design block `## 5. Implementer` in `docs/design.md`, its copy `docs/prompts/05-implementer.md` (re-copied from the block), and the runtime prompt `factory/prompts/implementer.md`.
  - Step 2 now runs only the NEW checks before the edit. A NEW check is one that must fail before the change.
  - Step 5 runs every acceptance check, then the gates. A check that already ran a gate command exactly as written on the same commit counts as that gate's run.
  - A REGRESSION check is one that must pass both before and after. One that fails at step 5 is run on the base. If it fails there too, the implementer stops and escalates.
  - The PR DESCRIPTION line now reads `NEW: before and after; REGRESSION: after, and base if it failed`.
  - The runtime copy keeps its own differences: the gate wording in step 5 ("the gate commands listed in your input under "Where you work", each exactly as written") and the no-rebase wording in step 6.
- **B. Verifier prompt.** Changed in the same three places: `## 7. Verifier`, `docs/prompts/07-verifier.md` and `factory/prompts/verifier.md`.
  - Step 3 runs only the NEW checks on the base. It runs a REGRESSION check on the base only when that check fails on the PR.
  - Step 4 gains the sentence that a step 2 command which ran a gate command exactly as written on the PR is that gate's run.
  - The `Per criterion:` line gains `(base: not run, for a REGRESSION that passed on the PR)`.
  - The verdict rules did not change. A wrong NEW check is SPEC-DEFECT, and a gate failure is FAILED. The runtime copy keeps its own step 4 gate wording.
- **C. Parent close can reuse a run** (`factory/cli.py`, `factory/workflows/build.js`).
  - New `_reused_subticket_run(root, cfg, t)` returns a run id only when spec conditions (1) to (4) all hold:
    1. The parent has exactly one sub-ticket, it is merged and has `main_after`, and the parent has `parent_base`.
    2. The integration branch is still at that `main_after`.
    3. The `verifier` results row for the merged head is VERIFIED with a `run_id`. That run's `meta.yaml` has `status: VERIFIED`, `head` equal to the merged head, and `base` equal to `parent_base`.
    4. The parent's pinned `specs/<id>/v<approved_version>.md` has at least one scenario, and every scenario name occurs in `specs/<sub id>/subticket.md`.
  - `_parent_close_verified` now returns the id of the run that verifies the parent, or `None`. That is the parent's own VERIFIED run, found as before, or else the reused run. Both callers keep their truth test: `ticket_transition` (`factory/cli.py:157`) and `archive_cmd` (`factory/cli.py:926`). I found them with `grep -rn _parent_close_verified factory bin tests agents`, and there are no other callers.
  - `ticket_transition` to `closed` on a parent adds `verified_by: <run id>` to the history entry it appends.
  - `ticket parent-check` adds `"reuse"` to its JSON. The value is a run id when the parent is `ready-for-parent-verify`, and `null` otherwise. The command makes no other change to the store.
  - `build.js` phase 3 now starts with clerk `ticket parent-check`. If `reuse` names a run, the script logs that the run stands for the parent-close run and starts no verifier. It then goes to `archive` with that run id as the park outputs. Otherwise the verifier runs as before. Archive, transition and park handling are unchanged.
  - Callers of `parent-check`: `build.js` phase 2 (it reads only `state`, so the new field does not affect it), the new call in phase 3, and the tests.
- **D. Records.**
  - `docs/design.md` Archive paragraph (line 82) and the Merge gate row of the routing table (line 126) now carry the rule, including "stands for the parent-close run".
  - `dev/build-harness.spec.md:285` describes the `parent-check` `reuse` field and the skip.
  - `docs/changelog.md` has entry 45, after 44 and before `Declined:`.
  - `README.md` "How a ticket moves" gains one sentence, which ends "the sub-ticket's verifier already checked the same code against the same starting point."
- **E. Tests.** A new file, `tests/factory/test_parent_close_reuse.py`, plus a one-line edit to each of the two listed tests in `test_shepherd.py`.

## Acceptance results

All commands were run with bash from the worktree root, before any edit and again at the final head `d45f060`. Every before output matches the "today" output in the parent's `verification.md`, and every after output matches the THEN line.

| Scenario | Label | Before (at `924513e`) | After (at `d45f060`) |
|---|---|---|---|
| implementer-runs-regression-checks-once | NEW | `design.md new=0 after=0 old=1` / `05-implementer.md new=0 after=0 old=1` / `implementer.md new=0 after=0 old=1` | `design.md new=1 after=1 old=0` / `05-implementer.md new=1 after=1 old=0` / `implementer.md new=1 after=1 old=0` |
| verifier-runs-regression-on-base-only-on-failure | NEW | `design.md new=0 onfail=0 old=1 defect=1 gate=2` / `07-verifier.md new=0 onfail=0 old=1 defect=1 gate=1` / `verifier.md new=0 onfail=0 old=1 defect=1 gate=1` | `design.md new=1 onfail=1 old=0 defect=1 gate=2` / `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1` / `verifier.md new=1 onfail=1 old=0 defect=1 gate=1` |
| one-run-serves-scenario-and-gate | NEW | `design.md=0 05-implementer.md=0 07-verifier.md=0 implementer.md=0 verifier.md=0 ` | `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1 ` |
| changed-blocks-copied-verbatim | REGRESSION | `05-implementer verbatim` / `07-verifier verbatim` | `05-implementer verbatim` / `07-verifier verbatim` |
| one-sub-ticket-parent-closes-on-its-verified-run (`fx one`) | NEW | `one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` | `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier` |
| parent-close-run-still-required-otherwise (`fx moved/two/uncovered`) | REGRESSION | `moved: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` / `two: subs=2 … reuse=None refused …` / `uncovered: subs=1 … reuse=None refused …` | the same three lines, unchanged |
| rule-recorded-in-design-build-spec-readme-changelog | NEW | `design=0 buildspec=0 readme=0 changelog=missing` | `design=1 buildspec=1 readme=1 changelog=before-declined` |

What the results show:
- The `defect` and `gate` counts are the same before and after. The spec-defect and gate-failure refusals are kept in every copy.
- `fx one` shows the new close: the parent closes with no verifier run of its own (`parent_runs=0`), and its history names the sub-ticket's run.
- The three REGRESSION lines show that every other case still refuses the close.
- I ran `fx` exactly as written in the parent spec's GIVEN.

Gates at `d45f060`:
- `git diff --check main...HEAD`: exit 0, no output. No whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `136 passed in 217.97s`. The suite passed in full: 131 existing tests and the 5 new ones.

The first suite run, at `50fd7a3`, gave `1 failed, 135 passed`. The failure was in my own new test `test_a_parent_close_run_is_still_required_with_two_sub_tickets`. Both sub-tickets wrote the same file with the same content, so the second implementer's `git commit` had nothing to commit. Commit `d45f060` gives each sub-ticket its own file. The production code did not change between the two runs.

## Tests added/changed

- **Added** `tests/factory/test_parent_close_reuse.py`, which reuses `built_to_implementer` from `test_shepherd.py` the way `test_killed_checker.py` does. Before the `cli.py` change, all 5 tests failed with `KeyError: 'reuse'`. After it, all 5 pass.

  | Test | What it checks |
  |---|---|
  | `test_a_single_sub_ticket_parent_closes_and_archives_on_its_verified_run` | `parent-check` reports `reuse` equal to the sub-ticket's verifier run. `archive` and then the plain close both succeed. The last history entry has `verified_by` set to that run. No verifier run exists for the parent, and current truth holds the scenario. |
  | `…when_main_moved_after_the_merge` | An empty commit on `main` after the merge leaves `reuse` null. The close and `archive` are both refused, and no parent verifier run exists. |
  | `…with_two_sub_tickets` | Both sub-ticket texts name the scenario, and `main` has not moved since the last merge. `reuse` is still null and the close is refused. |
  | `…when_the_sub_ticket_misses_a_scenario` | The sub-ticket text does not name `asked once`. `reuse` is null and the close is refused. |
  | `…when_the_verified_run_had_another_base` | The branch has two commits. After the verifier run starts, `main` fast-forwards to the branch's first commit, so the merge still goes through, but `parent_base` is not the verifier run's `base`. `reuse` is null and the close is refused. |

- **Changed**, both listed under "Tests to change": `test_shepherd.py::test_the_planned_ticket_is_built_checked_merged_and_archived` and `test_shepherd.py::test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run`.
  - Each gains only `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")`, after the sub-ticket merges and before `f.parent_check(tid)`.
  - The reason: both tests build one sub-ticket that names the parent's only scenario and leave `main` unmoved, so under part C their parent would close on the sub-ticket's run. With `main` moved, the parent-close run they exist to test is required again.
  - No assertion was removed or weakened.

## Known gaps and uncertainties

- **One `factory:` marker added**, at `factory/cli.py:867`. It names the limit: one sub-ticket only, and scenario coverage is read from scenario names found in the sub-ticket's text. It names the upgrade trigger: widen it only when the store can check a coverage map per sub-ticket.
- **Scenario names are matched as plain substrings.** A scenario named `asked once` also counts as covered by a sub-ticket text that says only `asked once more`. Real scenario names are kebab-case and longer, which makes such a clash unlikely. The spec chose "each name occurs in" the text.
- **The `build.js` skip has no automated test.** That script runs only inside the workflow runtime. I checked that it parses, by compiling it as an async function body with node. Its logic needs review against part C, and Operator step 2 will observe it on the first real build.
- **The base-mismatch test uses a constructed history.** It fast-forwards `main` to a commit inside the branch while the verifier runs. That is the only way I found to reach "VERIFIED, but the run's base differs from `parent_base`" through the CLI with one sub-ticket. It exercises condition (3)'s base comparison through real commands, not by editing store files.
- **A reused close has no second, independent verifier run.** The spec's Decisions accept this.
- **The README edit is ahead of a real run.** "Maintaining this page" says a behaviour appears above "Where this can go" only after it has run on a real ticket. The spec's Decisions chose to change "How a ticket moves" in this ticket, and Operator step 2 confirms it on the first real build. The status-header date was already 2026-10-03, today, so bumping it left the text unchanged.
- **I ran every acceptance command before the edit**, as this run's prompt (the old step 2) required. That includes the REGRESSION ones. The new step 2 applies from the next run after the runtime upgrade.
- **The first `fx` run used `python3` from the PATH.** `bin/factory` falls back to it because the worktree had no `.venv` until `uv run` created one. The later runs used the project venv, and the outputs were the same.

## Out-of-scope observations

- `factory/workflows/build.js` lines 3 and 7, the `meta` description and the Close phase detail, still say every build makes one parent-close verifier run. They are labels, not behaviour. I left them because part C does not name them.
- The README's "While that final run is in progress…" sentence still holds for the runs that happen. With a reused close, that step finishes at once.

## Responses to findings

None. This is the first round.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All seven acceptance commands match their THEN lines at the final head, both gates pass (check exit 0, 136 passed), and the five new tests failed before the `cli.py` change and pass after it. The `build.js` skip is the one part checked only by reading it.
ESCALATIONS: none
