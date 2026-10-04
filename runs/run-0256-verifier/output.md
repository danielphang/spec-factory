Commit: d001090e9b0a535d55599ce5819c497572e07cf4

How I ran it. PR: the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0256-verifier/wt` at `d001090` (local `main` = `0b1abad` = merge-base). Base: a fresh clone in this run's scratch directory, checked out detached at `0b1abad474cb9c583ed8445fc33617f9f0bdc37b`. I did not use a `git archive` export, because `init` refuses there with "cannot read the harness revision". I ran `uv sync --frozen` in both. Every command went through the HOME wrapper under `bash`, from the checkout root. `TMPDIR` was a fresh `/tmp/t0025ver.*` directory, outside every git repository. The parent's GIVEN block (input.md lines 487-523) was sourced verbatim to write `t0025-old.sh`, `t0025-b1.sh` and `t0025-gate.sh` there, and the directory was removed afterwards. Each WHEN was copied byte for byte from the sub-ticket into a generated script (`scratch/acc.sh`), with outputs in `scratch/pr.out` and `scratch/base.out`.

Per criterion:
- NEW | init creates the store on the factory-store branch | base `branch=main seen_by_main=6` | PR `branch=factory-store seen_by_main=0` | PASS
- NEW | init on a clone restores the store | base git's "nothing to commit", then `exit=1 branch=main restored=1` | PR `exit=0 branch=factory-store restored=1` | PASS
- NEW | two remotes carrying the store branch refused, both named | base `exit=0 store=written local_branch=0 names=0,0` | PR `exit=2 store=none local_branch=0 names=1,1` | PASS
- NEW | init from a scratch directory inside the store refuses | base `exit=0 phantom=written store=changed` / `found=` | PR `exit=2 phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- NEW | init from the store checkout on a detached HEAD refuses | base `exit=0 detached=yes phantom=written store=changed` / `found=` | PR `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage` | PASS
- REGRESSION | separate repository under a run's scratch directory gets its instance | base: not run (it passed on the PR; it also printed the same on base as part of the batch: `exit=0 instance=written live=ready-for-triage`) | PR `exit=0 instance=written live=ready-for-triage` | PASS
- NEW | once-tracked store path refused, nothing written | base `exit=0 instance=written names_path=0` | PR `exit=2 instance=none names_path=1` | PASS
- NEW | sub-ticket merges after a store commit | base `exit=2 refused=1` | PR `exit=0 refused=0` | PASS
- REGRESSION | sub-ticket refused after a code commit to main | base: not run (it also printed `exit=2 refused=1` on base in the batch) | PR `exit=2 refused=1` | PASS
- NEW | design doc names the store branch and path rule | base `store_branch=0 tickets_branch=2 never_tracked=0` | PR `store_branch=1 tickets_branch=0 never_tracked=1` | PASS
- NEW | build spec calls the store branch factory-store | base `old_name=16 new_name=0` | PR `old_name=0 new_name=1` | PASS
- NEW | changelog: one contiguous entry | base `CONTIGUOUS` / `0` | PR `CONTIGUOUS` / `1` | PASS
- NEW | intermediate: an existing plain store is left alone and pointed to `store migrate` | base `exit=0 branch=0 hint=0 dirty=0` | PR `exit=0 branch=1 hint=1 dirty=0` | PASS
- NEW | intermediate: README store branch, `-ffdx`, retired clause | base `store_branch=0 ffdx=0 old_cost=1` | PR `store_branch=1 ffdx=1 old_cost=0` | PASS
- NEW | intermediate: changelog's last entry is 53 | base `52. After issue #45 (2026-10-0` | PR `53. After issue #46 (2026-10-0` | PASS
- REGRESSION | harness suite (with `TMPDIR=$P`) | base: not run | PR `280 passed in 220.33s (0:03:40)` | PASS
- REGRESSION | `git diff --check main...HEAD; echo "exit=$?"` | base: not run | PR `exit=0` | PASS

Every NEW criterion fails on base for the reason the spec gives, and its base output matches the parent's verification.md "today" output exactly. Every NEW criterion passes on the PR.

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output. `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `280 passed in 196.83s`.

Scope checks (read, not run):
- The diff touches 8 files: `factory/cli.py`, `factory/gitops.py`, `tests/factory/test_store_branch.py` (new, 15 tests covering each Part C item listed for A and the merge gate), `tests/factory/test_live_store_guard.py`, `README.md`, `docs/design.md`, `docs/changelog.md` and `dev/build-harness.spec.md`. It changes no `docs/prompts/**`, `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml` or `uv.lock` file.
- The `test_live_store_guard.py` edit is limited to the two tests the Human ruling names. Only their `init` branch changed: exit 2, A.1's message and the JSON error shape. The non-`init` commands still call `assert_refused` with the location-rule text, and `assert snapshot(target) == before` is kept. This matches the ruling.
- `init_cmd`'s order matches A.1-A.6:
  - `_refuse_inside_store` runs only with `FACTORY_INSTANCE` unset.
  - The config is loaded in memory, and `fence(inst, cfg, root)` comes right after `root`, unconditionally.
  - `_add_store_checkout` (tracked-path refusal, branch source, worktree, exclude line) runs before `store.write_text(cfg_path, ...)`.
  - The JSON output gains `store_branch`.
- `docs/design.md` gains "never tracked" and the code-checkout sentence in the role-context paragraph. README's ticket count is 52, which matches `ls .factory/state/tickets | wc -l` in the dev checkout today.

Probes (each in a fresh repository under `/tmp/t0025probe.*`, with a throwaway HOME, script `scratch/probes.sh` and `scratch/probe7.sh`):
- Repository with no commit at all (unborn `main`), then `init --repo-name u` → exit 0, store on `factory-store`, `store_branch: "factory-store"`, integration checkout sees nothing → OK
- `init` run twice → the second run prints `written: [] created: [] agents: []`, keeps `store_branch: "factory-store"`, leaves one exclude line (no duplicate) and the same `git status` → OK
- `init` from `src/deep` in the code checkout → instance at the repo root, store on `factory-store` (A.1 does not misfire on an ordinary subdirectory) → OK
- `.factory/state/a/b/c` tracked on `main` and then removed → exit 2, nothing written, no worktree, no branch; the message names the path and the commit → OK
- Path tracked only on a side branch, never on `main` → exit 0, store created (the test is scoped to the integration branch, as A.3.1 says) → OK
- Local `factory-store` with a commit, already checked out in another worktree → exit 2 with git's "already used by worktree" error, no `.factory`, no `.claude` → OK
- `FACTORY_INSTANCE` set, `init` from `.factory/state/runs/x` → A.1 skipped. #45's location rule refuses with exit 2, and no phantom is written → OK
- Clone whose only remote branch is `origin/feature/factory-store`, a code branch and not a store branch → `init` exits 0 and makes the store a checkout of a new local `factory-store` tracking `origin/feature/factory-store`. The store contains that branch's `code.txt` → CONCERN. `gitops.remote_branches` matches any remote-tracking ref ending in `/factory-store`, not `refs/remotes/<remote>/factory-store` as design A.3.2 specifies. The same matching would wrongly count `origin/feature/factory-store` as a second remote and refuse a legitimate clone. This is not special-casing, and no acceptance criterion covers it, so it is not a FAIL (see ESCALATIONS).
- `factory-store` still unborn (orphan, no commit) and already checked out in another worktree → `init` exits 0, and git lets a second worktree sit on the same unborn branch. A.3.2 keys on an existing local branch, and an unborn branch has no ref, so this follows the spec. It is a narrow git edge case → OK (noted only)

STATUS: VERIFIED
CONFIDENCE: high. All 17 acceptance commands printed their THEN on `d001090`. Every NEW criterion printed the spec's own "today" output on `0b1abad`. Both gates exited 0. The one probe concern lies outside the criteria.
ESCALATIONS:
- A remote branch whose name only ends in `factory-store` can be mistaken for the store branch (`factory/gitops.py` `remote_branches`, used by `_add_store_checkout` in `factory/cli.py`). The function filters with `r.endswith(f"/{branch}")`. So a remote code branch such as `origin/feature/factory-store` is treated as the remote store branch. Reproduced: on a clone whose only such ref was `origin/feature/factory-store`, `init` exited 0. It checked that code branch out as the store, with upstream `origin/feature/factory-store`, and `.factory/state/code.txt` was present. Design A.3.2 specifies `refs/remotes/*/factory-store`, and git's ref glob does not let `*` cross a `/`. The same matching would also refuse a clone that has both `origin/factory-store` and `origin/feature/factory-store` as "more than one remote". Suggested follow-up: match exactly `refs/remotes/<name>/factory-store` for each name `git remote` lists, or use `git for-each-ref refs/remotes/*/factory-store`, which is not the same when a remote's name contains a slash. This sits outside T-0025.1's acceptance criteria, so it does not change the verdict. It is a fix for the reviewer, or for T-0025.2, to pick up.
