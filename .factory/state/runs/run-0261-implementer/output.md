Sub-ticket: T-0025.1 (T-0025-A, parent T-0025 approved spec v5, issue #46). Branch `factory/T-0025.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0025.1`, base `0b1abad`. Commits: `fdf4436` and `939552d` (run-0241, the first build), `878c68b` and `d001090` (run-0247), and `fb72f7a` (this run, fix round 1).

**This is fix round 1. All four review findings are fixed. Both gates pass on `fb72f7a`, and all 17 acceptance commands print their expected output.** The round fixed two real defects in `init`:
- `init` could check out an unrelated remote code branch as the store.
- `init` raised git's error on an unborn branch, where the spec says it should create the store.

It also routes `init`'s git calls through the repo's existing helper and adds two sentences the coding standard requires in this description.

## What changed

Terms used below:
- **store**: the directory of files where the factory keeps its ticket records.
- **instance**: a target repo's `.factory/` directory, which is the factory's per-repository setup.
- **integration branch**: the branch finished work merges into. Here that is `main`.
- **store branch**: `factory-store`, the branch the store now lives on. It is checked out as a git worktree at the store's path. A git worktree is a second working directory of the same repository.

**This round (`fb72f7a`), per finding:**
- **Remote store branch matching** (`factory/gitops.py` `remote_branches`). The function now asks git for `refs/remotes/*/factory-store`, which is the pattern design A.3.2 gives. Git's `*` in that pattern stops at a slash. So a code branch such as `origin/x/factory-store` no longer counts as a remote carrying the store branch. Before this fix, a clone whose only such branch was `origin/x/factory-store` got that code branch checked out as its store. A clone that had both `origin/factory-store` and `origin/x/factory-store` was refused as "more than one remote".
- **Unborn branch on an existing instance** (`factory/cli.py` `init_cmd`, part A.3.1). An unborn branch is a branch with no commit yet. Take an existing instance with no `integration_branch` configured and no `FACTORY_INTEGRATION_BRANCH` set. `init` now names the branch with `_head_branch`, which also works on an unborn branch. So the missing store is created, as A.3.1 says, because an unborn branch has tracked nothing. Before, `gitops.integration_branch` fell back to `git rev-parse --abbrev-ref HEAD`, and on an unborn branch that call refused with git's error. When a branch is configured or set in the environment, `gitops.integration_branch` is still used, unchanged.
- **Reuse of `gitops.git`.** Six raw `subprocess.run` git calls now go through `gitops.git(..., check=False)`, the repo's existing git helper:
  - `_refuse_inside_store`: A.1.1's `symbolic-ref` check.
  - `_head_branch`.
  - `_store_hint`: the detached check now calls `_head_branch(root) == "HEAD"`.
  - `_add_store_checkout`: the local-branch check.
  - `gitops.common_dir`.
  - `gitops.last_tracked`.

  Behaviour is the same in each case. With `check=False`, the helper returns stdout stripped, and that output is empty in exactly the cases where the old code tested for a non-zero exit. One check departs from the reviewer's literal suggestion. A.1.1 still compares the full ref, `refs/heads/factory-store`, and not `_head_branch(top) == "factory-store"`. The reason: `--short` prints `heads/factory-store` when a tag or other ref of the same name exists, so the full ref is the exact check.

**Built in earlier rounds and unchanged here** (described in full in run-0247's description):
- **Part A** (`init_cmd`), steps A.1 to A.6:
  - A.1: refusals from inside the store.
  - A.2: config in memory, with #45's fence call kept unconditional right after `root`.
  - A.3: for a missing own store: the refusal of a once-tracked path, the choice of branch source, the worktree step and the exclude line.
  - A.4: the instance written last.
  - A.5: the hints for an existing store.
  - A.6: `store_branch` in the JSON output.
- **Part C:** `tests/factory/test_store_branch.py`, now 18 tests.
- **Part D:** `docs/design.md`, `dev/build-harness.spec.md`, `docs/changelog.md` entry 53, and the README items the sub-ticket lists.
- **The two tests in `tests/factory/test_live_store_guard.py`** changed under the human ruling on run-0241.

Callers of existing functions this diff changes:
- `init_cmd` has one caller: the `init` subparser in `build_parser` (`p.set_defaults(fn=init_cmd)`, `factory/cli.py:1246`), found with `grep -n init_cmd factory/*.py`.
- Every other function the diff touches is new on this branch. The `factory/` hunks against base are all inside `init_cmd` or are additions: `git diff 0b1abad...HEAD -- factory/ | grep '^@@'`.

The diff from `0b1abad` now touches 8 files, with 561 insertions and 53 deletions.

## Acceptance results

How I ran them:
- From the worktree root on `fb72f7a`, through the HOME wrapper, under `bash`.
- `TMPDIR` pointed at a fresh `/tmp/t0025acc.*` directory, outside every git repository, which I removed afterwards.
- The script `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0261-implementer/scratch/acc.sh` was generated from this run's input. It holds the parent's GIVEN block (input lines 487-523) and the 17 WHEN commands, each copied byte for byte. Its output is in `scratch/acc.out`.

"Before" is base `0b1abad`, as run-0241 captured it and the verifier (run-0256) reproduced it.

| Scenario | Kind | Before (`0b1abad`) | After (`fb72f7a`) |
|---|---|---|---|
| init creates store on factory-store | NEW | `branch=main seen_by_main=6` | `branch=factory-store seen_by_main=0` |
| clone restores store | NEW | git's "nothing to commit", then `exit=1 branch=main restored=1` | `exit=0 branch=factory-store restored=1` |
| two remotes refused | NEW | `exit=0 store=written local_branch=0 names=0,0` | `exit=2 store=none local_branch=0 names=1,1` |
| init from scratch inside store | NEW | `exit=0 phantom=written store=changed` / `found=` | `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` |
| init from detached store | NEW | `exit=0 detached=yes phantom=written store=changed` / `found=` | `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` |
| separate repo under scratch | REGRESSION | n/a | `exit=0 instance=written live=ready-for-triage` |
| once-tracked path refused | NEW | `exit=0 instance=written names_path=0` | `exit=2 instance=none names_path=1` |
| merge after store commit | NEW | `exit=2 refused=1` | `exit=0 refused=0` |
| refused after code commit | REGRESSION | n/a | `exit=2 refused=1` |
| design doc | NEW | `store_branch=0 tickets_branch=2 never_tracked=0` | `store_branch=1 tickets_branch=0 never_tracked=1` |
| build spec | NEW | `old_name=16 new_name=0` | `old_name=0 new_name=1` |
| changelog contiguous | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `1` |
| old plain store (intermediate) | NEW | `exit=0 branch=0 hint=0 dirty=0` | `exit=0 branch=1 hint=1 dirty=0` |
| README (intermediate) | NEW | `store_branch=0 ffdx=0 old_cost=1` | `store_branch=1 ffdx=1 old_cost=0` |
| changelog last entry (intermediate) | NEW | `52. After issue #45 (2026-10-0` | `53. After issue #46 (2026-10-0` |
| harness suite (with `TMPDIR`) | REGRESSION | n/a | `283 passed in 212.54s (0:03:32)` |
| whitespace | REGRESSION | n/a | `exit=0` |

Every "after" matches its THEN. Every REGRESSION command printed its expected output, so none needed a re-run on the base.

Gate commands, run exactly as written on `fb72f7a`:
- `git diff --check main...HEAD` exited 0 with no output. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `283 passed in 193.57s`. That is the previous 280 plus this round's 3 new test cases, with no failures.

## Tests added/changed

- Added this round, to `tests/factory/test_store_branch.py`. That file is new on this branch, so it is not an existing test on `main`.
  - `test_a_remote_branch_whose_name_only_ends_in_the_store_branch_is_not_the_store`, in two cases:
    - `decoy-only`: a clone whose only such branch is `origin/x/factory-store` gets a new orphan store without that branch's `code.txt`.
    - `decoy-and-store`: a clone with both branches restores from `origin/factory-store` and is not refused.

    Before the fix, the first case failed because `code.txt` was in the store. The second failed with exit 2: "more than one remote carries it (origin/factory-store, origin/x/factory-store)".
  - `test_an_existing_instance_on_an_unborn_branch_counts_as_never_tracked`. It sets up a repo with no commit, then an instance, then removes the store and runs `init` again. Before the fix it failed with exit 2 and `git rev-parse --abbrev-ref HEAD: fatal: ambiguous argument 'HEAD'`.
- No other test changed this round. The two `test_live_store_guard.py` tests changed in run-0247 under the human ruling, and are unchanged since.

## Known gaps and uncertainties

- **factory: markers added: none.** A grep of the diff for `^\+.*(#|//) ?factory:` finds none. A `factory:` marker is the coding standard's comment for a deliberate shortcut with a known limit.
- **A remote whose name contains a slash is not seen.** Remote names may contain a slash, for example `a/b`. Git's `refs/remotes/*/factory-store` pattern does not match `refs/remotes/a/b/factory-store`. On a clone whose only remote copy of the store branch sits under such a remote, `init` would start a new orphan store branch instead of restoring that copy. The spec gives this pattern (A.3.2), and I followed it. An exact match against the names `git remote` lists would cover this case. I did not build that, because it goes past the spec and the reviewer's fix.
- **The unborn-branch fix repeats one precedence check.** `init_cmd` now reads `FACTORY_INTEGRATION_BRANCH` and `cfg["integration_branch"]` to decide whether to call `gitops.integration_branch`. This repeats the first two steps of that function. The alternative was to change `gitops.integration_branch`'s own fallback. That function has four other callers, `merge_cmd` among them, and the sub-ticket says to leave `merge_cmd` unchanged. So I kept the fix local.
- These gaps carry over from run-0247:
  - The two edited guard tests do not compare the caller's directory at the start of A.1's message.
  - The A.5 hint names `factory store migrate`, which arrives with T-0025.2.
  - `store_branch` is `null` whenever `FACTORY_STATE` names a throwaway store.
  - README's ticket count (52) includes ticket files that have not been committed yet.
  - The diff is larger than the parent estimated.
  - The HOME wrapper leaves empty `mktemp -d` directories in the system temp directory.
- **The one item from run-0247's list that this round removes:** the unborn-branch error on an existing instance is fixed.

## Out-of-scope observations

- `gitops.integration_branch` still raises on an unborn HEAD for its other callers (`factory/cli.py` worktree creation, merge and others). This was not changed here.
- README lines that still give `.factory/state/` as the live store's location belong to T-0025.2, as the sub-ticket's Out of scope says.

## Responses to findings

- Reviewer [BLOCKING] reuse (`factory/cli.py:849` and the other raw git calls) → FIXED `fb72f7a`. All six calls now go through `gitops.git(check=False)`. A.1.1 keeps the full-ref comparison, for the reason given in What changed.
- Reviewer [SHOULD-FIX] `remote_branches` matched any ref ending in `/factory-store` → FIXED `fb72f7a`. The function now passes `refs/remotes/*/factory-store` to `for-each-ref` and drops the `endswith` filter. I ran a probe on git 2.54.0 with refs `origin/factory-store`, `origin/x/factory-store`, `a/b/factory-store`, `nas/factory-store` and `origin/factory-storex`. The pattern listed only `nas/factory-store` and `origin/factory-store`, which shows that `*` matches a single path segment. A new test covers both of the reviewer's cases.
- Reviewer [SHOULD-FIX] description must state factory: markers and callers → FIXED in this description: "factory: markers added: none" is under Known gaps, and `init_cmd`'s caller is under What changed.
- Reviewer [NIT] unborn HEAD on an existing instance with no `integration_branch` → FIXED `fb72f7a`, with a new test. I used a local fallback to `_head_branch`, as the reviewer suggested. It is applied only when neither the config nor the environment names a branch. So `FACTORY_INTEGRATION_BRANCH` keeps its precedence.
- Verifier escalation (the same `remote_branches` defect) → FIXED `fb72f7a`, as above.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 17 acceptance commands printed their THEN on `fb72f7a`, both gate commands passed on that commit (`exit 0`; `283 passed`), and each fix has a test that failed before it for the reason the finding gives.
ESCALATIONS: protected path touched, as the sub-ticket and the parent's Risk declare: harness (`factory/cli.py`, `factory/gitops.py`). The merge gate needs a human approval for it.
