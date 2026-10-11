## Problem

The harness (the code that runs the factory's agents and records their work) wrongly stops part of a planned change because an earlier part of the same change has merged. Twice in the last multi-part build, the operator had to step in by hand to restart work the plan expected to go ahead. The second time, no command could restart it, so the operator edited the ticket's record by hand.

Some background. A large approved request (a parent ticket) is split by a planner into parts (sub-tickets). Each part is built, checked and merged on its own into the integration branch, which is the target repository's main line. One part may depend on an earlier one and build on what it added. The parts of one parent are siblings. Before the first coding run of a part (its implementer run), the harness runs a spec drift check. That check looks for changes on the integration branch, made since the parent's spec was approved, that the spec did not plan for. One of its rules flags a test file that changed in the same commit as a file the spec's design names, because such a test may pin behaviour the spec is about to change. When the check finds drift, the harness parks the part, which means it stops and waits in the operator's queue. The operator then amends the spec or writes a ruling (`factory resolve <part> --ruling F`, a note that returns the part to its implementer and also stops the check from repeating).

Two problems, both for the operator:

1. **A sibling's merge counts as drift.** The test rule looks at every commit on the integration branch since the spec was approved, including the merges of the parent's own earlier parts. When part A adds a test and changes a file the design names, part B is parked as soon as A merges, although the plan said A would add that test. Today the operator must rule on every such false park. The fix keeps flagging commits and merges that come from anywhere else.
2. **One kind of park has no way back.** When the harness fails to start an implementer run for any reason other than a refusal it reports as blocked, the build parks the part as a harness bug (`harness-bug: run start implementer: …`). No `resolve` option accepts that park, so even after the cause is understood, the part cannot be returned to its implementer. In the second case below, the Workflow script (the older script that runs a build's steps) recorded a spec drift refusal in that harness-bug form. The operator had to edit the stored park reason by hand before `--ruling` would accept it. The driver (the program replacing the Workflow scripts) records drift refusals as plain blocked parks. It still parks every other start failure, such as a failed environment sync, as a harness bug.

## Evidence

- **First false park.** The parent T-0040 (issue #65, the driver) was planned in three parts. Part A, T-0040.1, merged as `2ad4d8c52`. `git show --stat 2ad4d8c52` prints the subject "Merge factory/T-0040.1: The driver core and the intake phase (T-0040.1)" and shows `factory/cli.py | 39` and `tests/factory/test_drive.py | 303`: the merge changed a file the design names and added a test. The store (the factory's record of tickets, runs and log events, kept in `.factory/store/`) then logs part B, T-0040.2, parked from `ready-for-implementer` (`ticket.parked`, 2026-10-10T06:37:15) with the reason `BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 since spec v4 was written at 37848dbb0`. That commit is the merge of B's own sibling: `.factory/store/tickets/T-0040.1.yaml:53-55` records it as `merge.main_after: 2ad4d8c5288474b823d4571ba03de82a706eabdf`.
- **Second false park, and no route back.** `.factory/store/tickets/T-0040.3.yaml:26-33` records part C parked with `harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 …; tests/factory/test_drive_build.py changed by 18fbe88ba …`. Both blamed commits are sibling merges. `18fbe88ba` is "Merge factory/T-0040.2: The build phase (T-0040.2)", which added `tests/factory/test_drive_build.py`, and `T-0040.2.yaml:60-62` records it as that part's `merge.main_after`. The log holds a `park.corrected` event by the operator at 2026-10-10T17:18:37 whose `previous` field is that harness-bug reason. The ruling that followed in the same second (history entry `resolve: ruling`) is the workaround.
- **Cause in code.** `factory/cli.py:316-347` (`_test_drift`) walks `git rev-list --first-parent --reverse <recorded head>..<tip>` and flags each test file changed by a commit that also changed a design-named file. It never reads the parent's merged sub-tickets. The sibling-tests check beside it, `_check_sibling_tests` (`factory/cli.py:245-269`), already reads each merged sibling's `merge.main_after` and `merge.base_before`. `factory merge` merges with `--no-ff` (its docstring at `factory/cli.py:957`, the git call at `factory/gitops.py:192`), so a recorded `main_after` is always a merge commit whose first-parent diff holds the whole sibling.
- **No resolve route.** `factory/cli.py:1183-1185`: `--ruling` refuses unless the park reason starts with `ESCALATE` or `BLOCKED`. `factory/cli.py:1223-1225`: `--redispatch` refuses unless the park came from `checks-in-flight` or `ready-for-merge`. `factory/drive.py:179-186` and `factory/workflows/build.js:79-84` park every run-start refusal that does not start `BLOCKED ` as `harness-bug: run start <role>: <stderr>`, from `ready-for-implementer` for the implementer.
- **Reproduced on a clone of `main` at `cce3d6f`**, run through the running-code wrapper:
  - "A merged sibling's merge is not drift…" printed `none: drift=1 greet=1 named=0 runs=0`. That is: part B, after only its sibling's merge, is refused for spec drift naming the sibling's test, and no implementer run starts. The `other`, `greet` and `merge` lines each print `greet=1`: every later refusal also names the sibling's test.
  - The critic ran "A ruling on a harness-bug park from an implementer's run start…" on `cce3d6f` and got `ruling=2 parked kept=no drift=1`, then `start=2 runs=0`. That is: `--ruling` refuses the harness-bug park, writes no ruling, and the part stays parked.
- **Proposed fix prototyped** in that clone (scratch, not committed): skip a merged sub-ticket's `main_after` in `_test_drift`; accept the harness-bug park in `--ruling` with Decision 4's refusal text. The drift scenario then prints its expected four lines, including `merge: drift=1 greet=0 named=1 runs=0`: a merged branch that is no sub-ticket's recorded merge still parks. `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed 512 passed, 8 failed. Six of the eight failed only because my run pointed the temporary directory inside a git checkout; rerun with the default temporary directory, they pass. The other two are the two cases of the one test listed under Tests to change, which asserts the old refusal text.
- Capabilities read: `openspec/specs/build-dispatch/spec.md`, `openspec/specs/human-resolution/spec.md`, `openspec/specs/harness-docs/spec.md`, and `openspec/specs/spec-amendment/spec.md` for the `t0027-amend.sh` fixture.
- The request cites no Nanobot-side harness fix, and none was checked.

## Root cause

- `factory/cli.py` `_test_drift`: the first-parent walk does not exclude the recorded merge commits (`merge.main_after`) of the parent's merged sub-tickets. A sibling's merge is a first-parent commit whose diff against its first parent holds everything the sibling changed, so any sibling that adds a test and touches a design-named file trips the rule for every later sibling.
- `factory/cli.py` `resolve`, `--ruling` branch: accepts only `ESCALATE…` and `BLOCKED…` reasons. A `harness-bug: run start implementer:` park from `ready-for-implementer` matches no mode, so it can only be cleared by editing the ticket file.

## Out of scope

- The other drift rule (an Acceptance field naming an unmerged sibling), the named-file and test-file patterns, and the "no implementer run and no ruling on file" condition are unchanged.
- `_check_sibling_tests` (the sibling-tests check) is unchanged.
- The Workflow scripts' clerk re-encoding a JSON refusal as a harness-bug reason is not fixed here. The driver does not do it, and issue #89 retires the scripts.
- `--redispatch`, `--accept-paths` and every other `resolve` route keep their current rules. Harness-bug parks other than an implementer's failed run start (for example `harness-bug: run compose implementer:`, or any checker's) stay refused by `--ruling`.
- A sibling merged by hand as a fast-forward and recorded with `ticket set` is not covered: only its last commit would be skipped. `factory merge` never fast-forwards.
- No change to `factory/drive.py`, `factory/workflows/*.js`, any role prompt, `docs/prompts/` or `factory/prompts/`.

## Open questions

none

## Decisions

- 1 (which commits are not drift): the test rule skips a first-parent commit that is the recorded merge (`merge.main_after`) of any merged sub-ticket of the same parent, from the current plan or an earlier one. Rejected: only the current plan's siblings. An earlier plan's merged sub-ticket is also this parent's own work, and the sibling-tests check already counts it the same way.
- 2 (later commits still count): only the sibling's exact merge commit is skipped, never merge commits in general. A later direct commit or merge from anywhere else that changes a test beside a design-named file is still drift, and the refusal names that commit.
- 3 (the resolve route): `resolve <id> --ruling F` also accepts a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer`. It writes F as the next ruling and returns the sub-ticket to `ready-for-implementer` at the same round, as a ruling on a `BLOCKED` park does. As with any ruling on file, the drift check does not run again for that sub-ticket. Rejected: widening `--redispatch` to this park. `--redispatch` re-runs the checkers today, and with no ruling on file a drift refusal would park the sub-ticket again. Rejected: accepting every harness-bug park from `ready-for-implementer`. A failed `run compose` leaves its run in flight, so the next run start would be refused again.
- 4 (refusal text): `--ruling` on any other park is refused with `--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an implementer's run start; <id> is <state> (<reason or 'no park'>)`, so the operator sees the new case.

## Risk

Blast radius: the drift check at an implementer's run start and one `resolve --ruling` branch. If the sibling skip were too broad, a real drift commit could go unflagged. The skip matches exact recorded merge commits of the same parent only. The `other`, `greet` and `merge` cases of the new build-dispatch scenario pin that a direct commit, a commit to the sibling's own test and a merge of a branch that is no sub-ticket's still park. The ruling widening touches one prefix from one state. Every other park keeps today's refusal, which the second human-resolution scenario pins.
Protected paths: `factory/cli.py`

## Operator steps

1. After merge, move the runtime checkout to the new harness revision. The runtime checkout is the copy of this repo the factory runs from, pinned to a revision each target has accepted. Then accept that revision on each instance (each repository the factory serves, with its own store) with `--accept-harness <commit>`; until then that instance refuses to run. Until both steps are done, the running factory still parks on sibling merges.

