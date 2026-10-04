Commit: fb72f7a7284a3208150c72ea20fe31299c9fdd4e

Round 2. The head changed from `d001090` (round 1) to `fb72f7a`, the implementer's fix round. That commit touches only `factory/cli.py`, `factory/gitops.py` and `tests/factory/test_store_branch.py` (`git show fb72f7a --stat`: 56 insertions, 18 deletions). I re-ran every criterion on the new head anyway, and re-ran the base as well.

How I ran it:
- PR: the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0268-verifier/wt`, clean, at `fb72f7a`. Local `main` and the merge-base are both `0b1abad`.
- Base: a fresh clone in this run's scratch directory (`scratch/base`), checked out detached at `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`.
- Setup: `uv sync --frozen` in both checkouts. Every command ran through the HOME wrapper, under `bash`, from the checkout root.
- Fixtures: `TMPDIR` was a fresh `/tmp/t0025ver-pr.*` or `/tmp/t0025ver-base.*` directory, outside every git repository, and removed afterwards. The parent's GIVEN block (input.md lines 487-523, copied verbatim) wrote `t0025-old.sh`, `t0025-b1.sh` and `t0025-gate.sh` there.
- Script: all 17 WHEN commands were copied byte for byte from input.md lines 119-170 into the generated script `scratch/acc.sh`. Outputs are in `scratch/pr.out` and `scratch/base.out`.

Per criterion:
- NEW | init creates the store on the factory-store branch | base `branch=main seen_by_main=6` | PR `branch=factory-store seen_by_main=0` | PASS
- NEW | init on a clone restores the store | base: git's "nothing to commit", then `exit=1 branch=main restored=1` | PR `exit=0 branch=factory-store restored=1` | PASS
- NEW | two remotes carrying the store branch are refused, both named | base `exit=0 store=written local_branch=0 names=0,0` | PR `exit=2 store=none local_branch=0 names=1,1` | PASS
- NEW | init from a scratch directory inside the store refuses | base `exit=0 phantom=written store=changed` / `found=` | PR `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- NEW | init from the store checkout on a detached HEAD refuses | base `exit=0 detached=yes phantom=written store=changed` / `found=` | PR `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- REGRESSION | a separate repository under a run's scratch directory gets its instance | base: not run (it passed on the PR; the batch run also printed `exit=0 instance=written live=ready-for-triage` on base) | PR `exit=0 instance=written live=ready-for-triage` | PASS
- NEW | a once-tracked store path is refused, nothing written | base `exit=0 instance=written names_path=0` | PR `exit=2 instance=none names_path=1` | PASS
- NEW | a sub-ticket merges after a store commit | base `exit=2 refused=1` | PR `exit=0 refused=0` | PASS
- REGRESSION | a sub-ticket is refused after a code commit to main | base: not run (the batch also printed `exit=2 refused=1` on base) | PR `exit=2 refused=1` | PASS
- NEW | the design doc names the store branch and the path rule | base `store_branch=0 tickets_branch=2 never_tracked=0` | PR `store_branch=1 tickets_branch=0 never_tracked=1` | PASS
- NEW | the build spec calls the store branch factory-store | base `old_name=16 new_name=0` | PR `old_name=0 new_name=1` | PASS
- NEW | the changelog records the store branch in one contiguous entry | base `CONTIGUOUS` / `0` | PR `CONTIGUOUS` / `1` | PASS
- NEW | intermediate: an existing plain store is left alone and pointed to `store migrate` | base `exit=0 branch=0 hint=0 dirty=0` (the planner's recorded output) | PR `exit=0 branch=1 hint=1 dirty=0` | PASS
- NEW | intermediate: README names the store branch, the `-ffdx` caution and drops the retired clause | base `store_branch=0 ffdx=0 old_cost=1` | PR `store_branch=1 ffdx=1 old_cost=0` | PASS
- NEW | intermediate: the changelog's last entry is 53 | base `52. After issue #45 (2026-10-0` | PR `53. After issue #46 (2026-10-0` | PASS
- REGRESSION | harness suite (with `TMPDIR=$P`) | base: not run (it also printed `265 passed in 207.85s` on base) | PR `283 passed in 217.01s (0:03:37)` | PASS
- REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | base: not run | PR `exit=0` | PASS

Every NEW criterion fails on base for the reason the spec gives. Each base output is identical to round 1's base output and to the parent's "today" outputs. Every NEW criterion passes on the PR.

Gate suite: PASS
  `git diff --check main...HEAD` was run exactly as written in the last criterion above: exit 0, no output. `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run exactly as written: exit 0, `283 passed in 236.01s (0:03:56)`. That is 280 from round 1 plus the 3 new test cases.

What the fix round changed (read in `git show fb72f7a -- factory/`, and in `factory/cli.py:846-1003` and `factory/gitops.py:31-35,106-124`):
- **Raw git calls.** Six of them now go through `gitops.git(..., check=False)`. That helper returns stripped stdout and never raises with `check=False` (`factory/gitops.py:31-35`). For `symbolic-ref -q`, `rev-parse -q --verify` and `rev-parse --git-common-dir`, stdout is empty exactly when the old code saw a non-zero exit. So the behaviour is unchanged.
- **Remote matching.** `remote_branches` now passes `refs/remotes/*/factory-store` to `for-each-ref`. This is the pattern design A.3.2 names.
- **The branch for A.3.1.** For an existing instance whose config and environment name no integration branch, the branch now comes from `_head_branch`. On a born branch this gives the same answer as `gitops.integration_branch`'s fallback: the branch name, or `HEAD` when detached. On an unborn branch it gives the branch name, where the old fallback raised git's error. The A.3.1 rule "an unborn branch counts as never tracked" now holds.

Probes (each in a fresh throwaway repository, outside every git repository, with a throwaway HOME; script `scratch/probes.sh`, output `scratch/probes.out`):
- **Clone with no real store branch on any remote.** Its only lookalike refs are `origin/factory-storex` and `origin/x/factory-store`. → `exit=0`, the store is a new orphan `factory-store` with no upstream, and stderr is empty. Neither lookalike is taken as the store, and neither counts as a second remote. → OK
- **Existing instance on an unborn `main`, store removed, `FACTORY_INTEGRATION_BRANCH=main`.** This takes the `gitops.integration_branch` path, which this round kept. → `exit=0`, the store is on `factory-store`, and the output has `"store_branch": "factory-store"`. → OK
- **Existing instance with no `integration_branch`, repo root on a detached HEAD whose history once tracked `.factory/state`.** This exercises the new `_head_branch` path on a born, detached HEAD. → `exit=2`, nothing written, and the message is `factory init: HEAD has tracked files under .factory/state (last in commit 2d0ccfb…)`. A.3.1 still refuses, and the new fallback does not skip the tracked-path test. → OK
- **A tag named `factory-store` exists, and `init --repo-name x` runs from a scratch directory inside the store, which is on its branch.** → `exit=2` with A.1.1's "is inside the store checkout" message, and no phantom. The full-ref comparison holds when a tag has the same name. → OK
- **Restore from a clone, then a second `init`.** → `exit=0`, `"written": []`, `"store_branch": "factory-store"`, one exclude line, clean `git status`. → OK
- **Clone whose only remote carrying the store branch is named `a/b`** (`refs/remotes/a/b/factory-store`). → `exit=0`. The store is a new, unborn orphan `factory-store` with no upstream, not a restore of `a/b/factory-store`. The pushed store history is not restored, and nothing warns about it. → CONCERN, not a FAIL. It matches the spec's literal pattern (A.3.2), it is not special-casing, it breaks no stated criterion, and the implementer lists it under Known gaps. See ESCALATIONS.

The probe fixtures landed under the system temp directory (`/var/folders/...`) rather than my `/tmp/t0025probe.*` directory, because `TMPDIR` did not reach the probe's `mktemp` calls. They were still outside every git repository, which is the property that matters.

Scope (read, not run): the full diff from `0b1abad` touches the same 8 files as round 1. They are `factory/cli.py`, `factory/gitops.py`, `tests/factory/test_store_branch.py` (new), `tests/factory/test_live_store_guard.py` (unchanged since `878c68b`, within the human ruling), `README.md`, `docs/design.md`, `docs/changelog.md` and `dev/build-harness.spec.md`. No `docs/prompts/**`, `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock` file changes.

STATUS: VERIFIED
CONFIDENCE: high. All 17 acceptance commands printed their THEN on `fb72f7a`. Every NEW criterion printed the spec's "today" output on `0b1abad`. Both gate commands exited 0. The probes of this round's three fixes behaved as the spec says.
ESCALATIONS:
- `init` does not restore a store pushed under a remote whose name contains a slash (`factory/gitops.py` `remote_branches`). Reproduced: a clone whose only copy of the store branch was `refs/remotes/a/b/factory-store` got a new, empty orphan store, with exit 0 and no warning. This follows design A.3.2's pattern (`refs/remotes/*/factory-store`, where git's `*` does not cross a `/`). It sits outside T-0025.1's criteria, and the implementer lists it as a Known gap. Neither real instance has such a remote today: Nanobot's remotes are `fork`, `nas` and `origin`. The decision for the operator is whether to accept this or have T-0025.2 match each name that `git remote` lists.
- Protected paths are touched, as the sub-ticket and the parent's Risk declare: harness (`factory/cli.py`, `factory/gitops.py`). The merge gate needs a human approval for them.
