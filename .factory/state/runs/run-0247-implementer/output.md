Sub-ticket: T-0025.1 (T-0025-A, parent T-0025 approved spec v5, issue #46). Branch `factory/T-0025.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0025.1`, on base `0b1abad`. Commits: `fdf4436` and `939552d` (run-0241, the first build), then `878c68b` and `d001090` (this run).

**This change is ready for review. The full suite now passes: 280 of 280 tests.** The first build of this sub-ticket (run-0241) was blocked on two existing tests. Those tests checked the wrong message after the change: they still expected the older refusal text, although `init` was still refused with exit 2 and wrote nothing. A human ruling then allowed exactly those two tests to change. This run makes that change and nothing else in the tests, re-derives one README number, and re-runs every acceptance command and both gates.

## What changed

Terms used below:
- **store**: the directory of files where the factory keeps its ticket records.
- **instance**: a target repo's `.factory/` directory, the factory's per-repository setup.
- **integration branch**: the branch finished work merges into. Here that is `main`.
- **store branch**: `factory-store`, the branch the store now lives on. It is checked out as a git worktree (a second working directory of the same repository) at the store's path.

**This run (`878c68b`, `d001090`):**
- `tests/factory/test_live_store_guard.py`, in exactly the two tests the human ruling names. Each test now checks the `init` call against the new refusal (part A.1). The checks are: exit code 2, A.1's message (`is inside the store checkout <store> (branch factory-store); run init from the repository root`), and the usual JSON error shape. Before, each test checked for the location-rule text that T-0024 (#45) added. Every other assertion in the two tests is unchanged. That includes the non-`init` commands, which still check the location-rule text, and each test's before/after store snapshot.
- `README.md:481`: the ticket count is now 52. That is what README's own check, `ls .factory/state/tickets | wc -l`, prints today. Run-0241 had written 49, and tickets have been added since.

**Already built in run-0241 and unchanged here:**
- **Part A: `init` (`factory/cli.py` `init_cmd`, with helpers in `factory/gitops.py`).**
  - A.1: when `FACTORY_INSTANCE` is unset, `init` refuses in two cases. The first is when the caller's git top level has `factory-store` checked out. The second is when that top level is the store of the instance found by walking up from the caller, or lies under that store in the same repository (the same `--git-common-dir`).
  - A.2: the config is loaded in memory. #45's fence call stays right after `root` and runs unconditionally.
  - A.3: this applies only to a missing own store. `init` refuses a path the integration branch has ever tracked. It then checks out the store branch: a local branch if one exists, or exactly one remote's copy. It refuses when more than one remote carries the branch and names each one. With no branch anywhere, it creates an orphan. Any git failure becomes a refusal before anything is written. It also adds the exclude line.
  - A.4: `instance.yaml` and the other instance files are written only after A.1 to A.3.
  - A.5: an existing store that is not the `factory-store` checkout is left alone. A hint on stderr tells a plain directory apart from a detached store worktree.
  - A.6: the JSON output gains `store_branch`.
- **Part C:** `tests/factory/test_store_branch.py`, 15 new tests. These cover the A items and the merge gate.
- **Part D:**
  - `docs/design.md`: the piece 1 row, "Smallest thing that works" (twice), and the role-context paragraph, which now has "never tracked" and the code-checkout sentence. No prompt block changed.
  - `dev/build-harness.spec.md`: all 16 store-branch mentions of `tickets` now say `factory-store`.
  - `docs/changelog.md`: entry 53.
  - `README.md`: the "store branch" term, the target bullet, adoption step 1, the "Committing and pushing the store" how-to with both cautions, the "Parallel builds" paragraph, and the status date.

The diff from base `0b1abad` touches 8 files, with 524 insertions and 54 deletions.

## Acceptance results

How I ran them: from the worktree root, through the HOME wrapper, under `bash`. `TMPDIR` pointed at a fresh `/tmp/t0025acc.*` directory, which lies outside every git repository. The parent's GIVEN block was written there verbatim, and the directory was removed afterwards. Script: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0247-implementer/scratch/acc.sh`.

"Before" is base `0b1abad`, as run-0241 captured it. Code has not changed since. "After" is this run, on `878c68b` for the scenario rows and on `d001090` for the gate and the last three rows.

| Scenario | Kind | Before | After |
|---|---|---|---|
| init creates store on factory-store | NEW | `branch=main seen_by_main=6` | `branch=factory-store seen_by_main=0` |
| clone restores store | NEW | git's "nothing to commit", then `exit=1 branch=main restored=1` | `exit=0 branch=factory-store restored=1` |
| two remotes refused | NEW | `exit=0 store=written local_branch=0 names=0,0` | `exit=2 store=none local_branch=0 names=1,1` |
| init from scratch inside store | NEW | `exit=0 phantom=written store=changed` / `found=` | `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` |
| init from detached store | NEW | `exit=0 detached=yes phantom=written store=changed` / `found=` | `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` |
| separate repo under scratch | REGRESSION | — | `exit=0 instance=written live=ready-for-triage` |
| once-tracked path refused | NEW | `exit=0 instance=written names_path=0` | `exit=2 instance=none names_path=1` |
| merge after store commit | NEW | `exit=2 refused=1` | `exit=0 refused=0` |
| refused after code commit | REGRESSION | — | `exit=2 refused=1` |
| design doc | NEW | `store_branch=0 tickets_branch=2 never_tracked=0` | `store_branch=1 tickets_branch=0 never_tracked=1` |
| build spec | NEW | `old_name=16 new_name=0` | `old_name=0 new_name=1` |
| changelog contiguous | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `1` |
| old plain store (intermediate) | NEW | `exit=0 branch=0 hint=0 dirty=0` | `exit=0 branch=1 hint=1 dirty=0` |
| README (intermediate) | NEW | `store_branch=0 ffdx=0 old_cost=1` | `store_branch=1 ffdx=1 old_cost=0` |
| changelog last entry (intermediate) | NEW | `52. After issue #45 (2026-10-0` | `53. After issue #46 (2026-10-0` |
| harness suite (with `TMPDIR`) | REGRESSION | — | `280 passed in 223.39s` |
| whitespace | REGRESSION | — | `exit=0` |

What the table shows:
- Every "after" matches its THEN.
- Every NEW "before" failed as the spec said it would.
- Both REGRESSION scenarios print what they printed on the base.

Gate commands, run exactly as written:
- `git diff --check main...HEAD`: prints `exit=0` on `d001090`. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: prints `280 passed in 223.51s` on `878c68b`, and `280 passed in 223.88s` on `d001090`, the final head. No test fails.
- `tests/factory/test_live_store_guard.py` alone: `11 passed`. Both changed tests pass.

## Tests added/changed

- Added (run-0241): `tests/factory/test_store_branch.py`, 15 tests. On the base, 14 of them fail and one passes: the regression that a code commit is still refused. All 15 pass on HEAD.
- Changed (this run, under the human ruling):
  - `test_live_store_guard.py::test_marked_writes_from_a_runs_scratch_directory_are_refused`
  - `test_live_store_guard.py::test_marked_writes_from_under_worktrees_are_refused`

  The change was needed for this reason. Each test runs `init` from inside a store's `runs/` or `worktrees/`, and the store is now a `factory-store` checkout. So A.1 refuses the call before #45's location rule runs. The behaviour the tests protect still holds: the call exits 2, and the before/after snapshot of `.factory` and `.claude` is unchanged. Only the refusal message differs. Each test still checks its non-`init` commands against the location-rule text.

## Known gaps and uncertainties

- **The two edited tests check part of A.1's message, not all of it.** They do not compare the caller's directory at the start of the message. The harness gets that directory from `instance.caller_cwd()`, which may come back resolved or unresolved, so matching it exactly would make the tests brittle. The tests do check the store path, the branch and the instruction.
- **The A.5 hint names a command that does not exist yet.** It points to `factory store migrate --to PATH`, which comes with T-0025.2. Until that merges, the hint is ahead of the code. The spec requires the hint (A.5), and the intermediate check expects `hint=1`.
- **`store_branch` describes only the own store.** With `FACTORY_STATE` naming a throwaway store, it is always `null`. That is my reading of "when the own store is that branch's checkout".
- **One case raises an error instead of counting as never tracked.** For an existing instance, A.3.1 uses `gitops.integration_branch`. When no branch is configured and HEAD is unborn at the repo root, that call raises git's error as a refusal. A new instance on an unborn branch is handled.
- **The README describes behaviour no real ticket has used yet.** README's "Ground truth only" rule says a thing should appear only after it has run. Spec part D requires the "Committing and pushing the store" section anyway. The section says that both existing stores are still plain directories.
- **The README ticket count, 52, includes tickets nobody has committed yet.** The `ls` in the live dev checkout includes ticket files the operator has not committed. The tracked copy at `0b1abad` holds 46 tickets.
- **The diff is larger than the parent estimated.** It has 524 insertions and 54 deletions. The parent estimated about 70 lines for part A and 210 for part C. The test file alone is 296 lines.
- **My scratch files are not all in the scratch directory.** The acceptance fixtures used `/tmp/t0025acc.*`, which I removed, because the plan requires a `TMPDIR` outside every git repository. The HOME wrapper also leaves empty `mktemp -d` directories in the system temp directory.

## Out-of-scope observations

- `gitops.integration_branch` raises an error on an unborn HEAD when no branch is configured. That affects every caller, not only `init`.
- Some lines in README still give `.factory/state/` as the store's location: the "Where things live" row and the "Maintaining this page" table. Those lines belong to T-0025.2.

## Responses to findings

No review findings yet. Response to the human ruling on run-0241's escalation: FIXED in `878c68b`. Only the two named tests changed, and only their `init` assertions changed. A.1's ordering and message are as the spec states.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN on this head, and both gate commands passed on the final commit `d001090`.
ESCALATIONS: none
