Sub-ticket: T-0025.1 (T-0025-A, parent T-0025 approved spec v5, issue #46). Branch `factory/T-0025.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0025.1`. Commits `fdf4436` and `939552d`, on base `0b1abad`.

**Status: blocked on one gate, as the spec predicted.** The change is built. All 15 acceptance commands print what their THEN says. The harness suite has 2 failures out of 280. Both are existing #45 tests in `tests/factory/test_live_store_guard.py`, and the spec forbids me to edit them. Each one runs `init` from inside a store's `runs/` or `worktrees/` and checks for #45's location-rule message. With this change, `init` is refused earlier (part A.1), with the message A.1 specifies. The exit code is still 2 and nothing is written. Parent spec "Tests to change" says to report such a test and not edit it. So this needs a human decision (ESCALATIONS).

## What changed

Terms used below:
- **store**: the factory's ticket records.
- **instance**: a target repo's `.factory/` directory.
- **integration branch**: `main` here.
- **store branch**: `factory-store`.

**Part A, `init` (`factory/cli.py` `init_cmd`, plus helpers in `factory/gitops.py`):**
- **A.1.** When `FACTORY_INSTANCE` is unset, `init` refuses in two cases. Both checks are in `_refuse_inside_store`.
  - The caller's git top level has `refs/heads/factory-store` checked out. This includes an unborn branch.
  - The instance found by walking up from the caller has a store that is the top level. It also refuses when the top level lies under that store and is in the same repository: `gitops.common_dir` compares `--path-format=absolute --git-common-dir` at both places.
  - If the found config cannot be read or has no string `state_dir`, the second check does not apply.
  - Each refusal message is one line and is worded as in the spec.
- **A.2.**
  - For a new instance, the config is loaded in memory from `_new_instance_yaml`. Nothing is written yet.
  - #45's `fence(inst, cfg, root)` is called right after `root`, unconditionally.
  - The existing refusals are kept: no `--repo-name`, a new instance with a throwaway store, and `_revision()`.
- **A.3.** Applies only to the instance's own store, and only when its path does not exist.
  - `gitops.last_tracked` finds the last commit on the branch that touched the store path. If there is one, `init` refuses and names the path and that commit. An unborn branch, or any ref with no commit, counts as never tracked.
  - Which branch is checked:
    - existing instance: `gitops.integration_branch`;
    - new instance: `_head_branch`, the checked-out branch, or `HEAD` when detached.
  - Source of the store branch:
    - a local `factory-store` if one exists;
    - otherwise the remote-tracking branches named `factory-store`, found by `gitops.remote_branches`. More than one is refused and each `<remote>/factory-store` is named. Exactly one is checked out with `git worktree add --track -b factory-store <path> <remote>/factory-store`;
    - otherwise `git worktree add --orphan -b factory-store <path>`.
  - A git failure is re-raised as `Refused` ("factory init: cannot check out the store at …").
  - When the path is inside the repo, `/<path>/` is then added to `git rev-parse --git-path info/exclude`, unless that line is already there.
- **A.4.** `instance.yaml` is written only after A.1 to A.3. Then come `context.md`, `harness.lock`, the agents and the store files, as before.
- **A.5.** An own store that already existed and is not `factory-store`'s checkout is left alone, with a hint on stderr:
  - a plain directory (not a worktree of this repo) gets "…is not on its branch factory-store; factory store migrate --to PATH moves it";
  - a worktree of this repo on a detached HEAD gets "…is on a detached HEAD; check out factory-store there".
- **A.6.** The JSON output gains `store_branch`. It is `"factory-store"` when the store in use is the own store and is that branch's checkout, otherwise `null`.

**Part C (A items and the merge gate):** a new file, `tests/factory/test_store_branch.py`, with 15 tests (list below).

**Part D (A items):**
- `docs/design.md`:
  - The piece 1 row (`:39`) and "Smallest thing that works" (`:76`, twice) now say `factory-store` where they said `tickets`.
  - The role-context paragraph (`:60`) now describes the store as a git worktree of `factory-store` at a path the integration branch has "never tracked". It explains why the path must be untracked and that the branch never moves the integration branch. It adds one sentence on a command run from a code checkout.
  - No prompt block changed, so nothing under `docs/prompts/` needed re-copying.
- `dev/build-harness.spec.md`: all 16 lines that named the store branch `tickets`, `refs/heads/tickets` or `HEAD:tickets` now name `factory-store`. Mentions of the `tickets/` directory are untouched.
- `docs/changelog.md`: entry 53, one line, starting `53. After issue #46 (2026-10-04),`. It sits after entry 52 and before `Declined:`.
- `README.md`:
  - a "store branch" row in "Terms used on this page";
  - the target bullet in "Where it runs";
  - step 1 of "Adopting the factory in a repo";
  - a new how-to, "Committing and pushing the store", with both cautions;
  - the "Parallel builds across tickets" paragraph drops the retired clause and says a store committed on its branch no longer moves the integration branch;
  - the ticket count, 18 → 49, plus one history clause naming #46. The status date is already 2026-10-04, which is today.

Callers of the functions I changed (grep of `factory/` and `tests/`):
- `init_cmd` is reached only through the `init` subparser (`factory/cli.py` `p.set_defaults(fn=init_cmd)`).
- `_git_toplevel` and `_new_instance_yaml` are called only from `init_cmd`.
- The new gitops helpers are used only by `init_cmd`'s helpers. Part B is expected to reuse `last_tracked`.

## Acceptance results

How I ran them:
- From the worktree root, through the wrapper, under `bash`.
- `TMPDIR` pointed at a directory outside every git repository, as the plan requires; I removed it afterwards.
- The GIVEN block was run once, verbatim.

"Before" is base `0b1abad`. "After" is HEAD `939552d`.

| Scenario | Kind | Before | After |
|---|---|---|---|
| init creates store on factory-store | NEW | `branch=main seen_by_main=6` | `branch=factory-store seen_by_main=0` |
| clone restores store | NEW | git's "nothing to commit" lines, then `exit=1 branch=main restored=1` | `exit=0 branch=factory-store restored=1` |
| two remotes refused | NEW | `exit=0 store=written local_branch=0 names=0,0` | `exit=2 store=none local_branch=0 names=1,1` |
| init from scratch inside store | NEW | `exit=0 phantom=written store=changed` / `found=` | `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` |
| init from detached store | NEW | `exit=0 detached=yes phantom=written store=changed` / `found=` | `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` |
| separate repo under scratch | REGRESSION | (base) `exit=0 instance=written live=ready-for-triage` | `exit=0 instance=written live=ready-for-triage` |
| once-tracked path refused | NEW | `exit=0 instance=written names_path=0` | `exit=2 instance=none names_path=1` |
| merge after store commit | NEW | `exit=2 refused=1` | `exit=0 refused=0` |
| refused after code commit | REGRESSION | `exit=2 refused=1` | `exit=2 refused=1` |
| design doc | NEW | `store_branch=0 tickets_branch=2 never_tracked=0` | `store_branch=1 tickets_branch=0 never_tracked=1` |
| build spec | NEW | `old_name=16 new_name=0` | `old_name=0 new_name=1` |
| changelog contiguous | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `1` |
| old plain store (intermediate) | NEW | `exit=0 branch=0 hint=0 dirty=0` | `exit=0 branch=1 hint=1 dirty=0` |
| README (intermediate) | NEW | `store_branch=0 ffdx=0 old_cost=1` | `store_branch=1 ffdx=1 old_cost=0` |
| changelog last entry (intermediate) | NEW | `52. After issue #45 (2026-10-0` | `53. After issue #46 (2026-10-0` |
| harness suite | REGRESSION | — | **`2 failed, 278 passed in 224.27s`** (FAILS) |
| whitespace (`git diff --check main...HEAD`) | REGRESSION | — | `exit=0` |

What the table shows:
- Every NEW "before" matched the spec's "today" output, re-captured on a base that includes #45. #45 did not change any of them.
- Every "after" matches its THEN, except the harness suite.

**Gate commands, as written, on `939552d`:**
- `git diff --check main...HEAD` → `exit=0`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `2 failed, 278 passed in 224.66s`. The failures:
  - `test_live_store_guard.py::test_marked_writes_from_a_runs_scratch_directory_are_refused`
  - `test_live_store_guard.py::test_marked_writes_from_under_worktrees_are_refused`

  Each fails on `assert RULE in cp.stderr`, where RULE is "role runs may not write the live store". stderr is now "factory init: <dir> is inside the store checkout <target>/.factory/state (branch factory-store); run init from the repository root".

**Same tests on the base.** I checked out `factory/` from `0b1abad` in the worktree, ran `pytest tests/factory/test_live_store_guard.py`, and got `11 passed`. Then I restored HEAD; the worktree is clean. So my change causes the two failures. They are not a defect in the base.

**What still holds for those two cases.** I replicated both with `bin/factory` on a fresh target with a run in flight and `FACTORY_DISPATCH=1`:
- init from the run's scratch directory → `scratch_init exit=2`;
- init from `worktrees/T-0001/sub` → `worktrees_init exit=2`;
- a cksum snapshot of `.factory` and `.claude`, taken before and after → `store+agents unchanged`.

So the protection the tests exist for (exit 2, nothing written) holds. Only the message text differs.

## Tests added/changed

New file `tests/factory/test_store_branch.py`, 15 tests. On the base, 14 fail and 1 passes. The one that passes is the code-commit regression, as it should. All 15 pass on HEAD.
- `test_a_new_store_is_the_checkout_of_its_branch_unseen_by_the_integration_checkout`
- `test_a_store_commit_leaves_the_integration_branch_where_it_was`
- `test_a_clone_restores_the_store_from_the_branch`: checks the upstream is `origin/factory-store` and that `written` is empty.
- `test_two_remotes_carrying_the_branch_are_refused_naming_both`: checks nothing is written (exclude file included) and no local branch is created.
- `test_a_store_path_the_integration_branch_once_tracked_is_refused`: checks the message names the path and the commit, and is one line.
- `test_a_failed_worktree_step_writes_no_instance_file`: the branch is already checked out elsewhere.
- `test_init_from_inside_the_store_is_refused_and_writes_nothing[on-branch|detached]`
- `test_with_factory_instance_set_a1_does_not_apply`: with a throwaway store the call succeeds. With the own store, #45's location rule refuses.
- `test_init_in_a_separate_repository_under_a_runs_scratch_directory_makes_its_instance`
- `test_an_existing_plain_store_is_left_alone_and_pointed_to_store_migrate`: also checks that a second `init` there is a no-op.
- `test_a_detached_store_worktree_is_left_alone_with_its_own_hint`
- `test_a_second_init_is_a_no_op`
- `test_a_sub_ticket_merges_after_a_store_commit`
- `test_a_sub_ticket_is_still_refused_after_a_code_commit`

I changed no existing test.

## Known gaps and uncertainties

- **The suite gate fails on the two #45 tests above.** It is not fixed, because the spec forbids editing them. I did not change A.1's message to contain #45's text: that would satisfy the assertion while contradicting the spec's A.1 wording.
- **The hint names a command that does not exist yet.** The A.5 hint points to `factory store migrate --to PATH`, which arrives with T-0025.2. Until that merges, the hint is ahead of the code. This is spec-mandated (A.5); the intermediate acceptance check requires `hint=1`.
- **Which store `store_branch` reports on.** It is reported only when the store in use is the own store. With `FACTORY_STATE` naming a throwaway store it is always `null`. That is my reading of "when the own store is that branch's checkout". It also avoids running `git worktree list` in whatever repo `FACTORY_REPO` names.
- **Branch check for an existing instance.** A.3.1 uses `gitops.integration_branch`. With no configured branch and an unborn HEAD at the repo root, that call raises git's error as a refusal instead of counting as never tracked. A new instance on an unborn branch is handled: `_head_branch` plus the ref check in `last_tracked`.
- **One remote: explicit command.** With exactly one remote, I use the explicit `--track -b factory-store <path> <remote>/factory-store` rather than git's guess-the-remote form. The result is the same. It does not depend on `checkout.guess` or `checkout.defaultRemote`.
- **The README describes untried behaviour.** "Committing and pushing the store" describes something no real ticket has run yet. README's "Ground truth only" rule says a thing appears only after it has run. Spec part D requires the section, so I wrote it, and I stated that both existing stores are still plain directories.
- **The ticket count.** README's ticket count is 49, from `ls .factory/state/tickets | wc -l` in the live dev checkout. That count includes three ticket files not yet committed (`T-0025.1`, `T-0025.2`, `T-0026`). The tracked copy at `0b1abad` holds 46. The page said 18, which was already stale.
- **Diff size.** 507 insertions and 49 deletions across 7 files. The test file is 296 of those lines. The parent estimated part A at about 70 lines and part C at about 210.
- factory: markers added: none.
- **Possible effect on another session.** While stopping my own background suite runs, I ran `pkill -f "pytest -q -p no:cacheprovider tests/factory"`. That pattern would also have stopped an identical suite run by another session on this machine at that moment. I could not check whether one was running.
- **Scratch-directory exception.** Per the plan, the fixture `TMPDIR` was a system temp directory outside every git repository (`/private/var/folders/.../tmp.2CANsJQ9t1`), not my scratch directory. I removed it afterwards. The suite's `/tmp/t0025-suite.*` directories were removed too.

## Out-of-scope observations

- `gitops.integration_branch` raises on an unborn HEAD when nothing configures the branch. That affects every caller, not only `init`.
- README's "Where things live" row and "Maintaining this page" table still give `.factory/state/`. Those lines belong to T-0025.2.

STATUS: BLOCKED
CONFIDENCE: high, all 15 acceptance commands match their THEN on HEAD, and the only gate failure is the conflict the parent spec predicted, confirmed to pass on the base.
ESCALATIONS:
- The harness suite gate cannot pass without changing two existing tests that the approved spec does not list under "Tests to change": `tests/factory/test_live_store_guard.py::test_marked_writes_from_a_runs_scratch_directory_are_refused` and `::test_marked_writes_from_under_worktrees_are_refused`. Both pass on the base (`11 passed`) and fail on this branch. They run `init` from inside a store's `runs/` or `worktrees/` and assert #45's location-rule text. A.1 now refuses first, with exit 2 and nothing written; I checked that directly. Decide: either amend the spec's "Tests to change" so each test's `init` call accepts A.1's refusal (exit 2, A.1's message, snapshot unchanged), which re-dispatches this sub-ticket to edit only those two tests; or overrule A.1's ordering. Parent spec (Risk; Tests to change) anticipated this case and said to report it.
