Sub-ticket: T-0025.2 (T-0025-B), parent T-0025 approved spec v5 (issue #46). Branch `factory/T-0025.2`, one commit `267ef3b` on base `7a437ee`.

## What changed

The store is the directory where the factory keeps its records: tickets, runs, verdicts and its log. On both real instances it is still a plain directory tracked on the integration branch, the branch that finished work merges into. After T-0025-A, a new store is a git worktree of its own branch, `factory-store`. This change adds the command that moves an existing store onto that branch.

**Part B: `factory store migrate --to PATH`** (`factory/cli.py`):
- `build_parser` gains a `store` subcommand group with `migrate --to PATH`. It is not on #45's read-only list. While a run is in flight, #45's fence refuses it unless it carries `FACTORY_DISPATCH=1`, the marker the dispatcher puts on its own commands.
- `store_migrate` checks every refusal before the first write. Each one exits 2, writes nothing and names what is in the way. In spec order:
  1. the store in use is not the instance's own;
  2. the store is already the `factory-store` checkout, or a local `factory-store` branch already exists;
  3. the integration branch is not checked out at the repository root (detached HEAD included);
  4. a run is in flight (each run id is named);
  5. a git worktree lies under the store (each one is named);
  6. a store file is uncommitted or untracked (each file is named);
  7. PATH exists, or the integration branch has ever tracked a file under it, checked with A's `gitops.last_tracked`;
  8. `instance.yaml` has no `state_dir:` line.
- Steps 1 to 6 follow the spec:
  1. One root commit is built with `commit-tree` from `<branch>:<state_dir>`. Its message names the source commit and the `git log` command for the earlier history. Then `git branch factory-store`.
  2. `git worktree add PATH factory-store`.
  3. Every file git ignores under the old store is copied to PATH.
  4. The copy is verified. On a mismatch, or on any exception during steps 2 to 4, the command runs `git worktree remove --force`, `worktree prune` and `branch -D factory-store`, removes the directories it created, and exits 1 naming the first file that differs.
  5. `git rm -r -q --cached <state_dir>`, then the exclude line. Only the value on the `state_dir:` line is rewritten; comments are kept. Then `rmtree` of the old store.
  6. `store.migrated` is logged in the new store, the spec's JSON is printed, and a reminder goes to stderr.
- The command makes no commit on the integration branch and pushes nothing.
- Helpers in `factory/cli.py`:
  - `_ignored_files` lists every file git ignores under the store.
  - `_copy_mismatch` runs step 4's three checks.
  - `_exclude_store` is the exclude-file writer, moved out of A's `_add_store_checkout` so that `init` and `migrate` share it. Its only callers are `_add_store_checkout` (`factory/cli.py:903`) and `store_migrate` (`:1129`).

**Part C (B items):** `tests/factory/test_store_migrate.py` (new file; 17 tests):
- the success case:
  - the tree is carried byte for byte, as one root commit whose message names the source commit;
  - ignored files are copied, including a nested git repository and a symlink;
  - `state_dir` is rewritten, and a separate test checks that an inline comment survives;
  - the old path is untracked and removed, and `main` is not committed;
  - the new path is excluded, and later commands (`ticket show`, `paths`) find the moved store;
  - `store.migrated` is logged;
- a copy that does not match: it exits 1, and the old store, `instance.yaml`, the refs, the worktrees and the index are unchanged, with no `factory-store` branch and no new path;
- every refusal, 12 parametrized cases, plus a store already on its branch. Each exits 2, and a snapshot of the files, exclude file, refs, worktree list and index is unchanged;
- a checkout of the pre-move commit and back leaves the new store's files, including an uncommitted one, unchanged.

**Part D (B items):**
- `docs/changelog.md`: entry 53 gains the `store migrate` clause on the same line. No entry 54 was added.
- `README.md`:
  - new how-to "Moving an existing store onto its branch", with the preconditions, `factory store migrate --to .factory/store`, the six steps, the commits afterwards, the "from before the move" note, and the rollback (`rm .factory/store/.git && git worktree prune`, never `git worktree remove`);
  - the target bullet says both existing stores stay plain directories until their operator runs the command;
  - the two diagram labels change from `state/` to `store/`;
  - the four live-store location lines now name `.factory/store/`, at `README.md:527`, `:542`, `:581` and `:586` after this change;
  - ticket count re-derived: `ls .factory/state/tickets | wc -l` printed `52`, unchanged; the status date is already 2026-10-04.

## Acceptance results

Every command ran from the worktree root through the HOME wrapper under `bash`. Beforehand, the parent's GIVEN block ran verbatim with `TMPDIR` set to a fresh `/tmp/t0025-impl.*` directory, which was removed afterwards. The fixtures' own `mktemp -d` calls landed under `/var/folders/.../T`, which is also outside every git repository.

| Command | Before (base `7a437ee`) | After (`267ef3b`) |
|---|---|---|
| store migrate carries the store (NEW) | `exit=2` / `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0` / `state_dir=.factory/state ticket=ready-for-triage` | `exit=0` / `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0` / `state_dir=.factory/store ticket=ready-for-triage` |
| store migrate refuses uncommitted and in flight (NEW) | `uncommitted: exit=2 names=0 branch=0` / `in flight: exit=2 names=0 branch=0 new=none` | `uncommitted: exit=2 names=1 branch=0` / `in flight: exit=2 names=1 branch=0 new=none` |
| older checkout leaves the moved store (NEW) | `live=lost on=main` | `live=live on=main` |
| README describes branch and move (NEW) | `store_branch=1 migrate=0 ffdx=1 premove=0 old_cost=0 old_refs=4` | `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0` |
| entry 53 names store migrate, no 54 (NEW) | `53. ` / `0` | `53. ` / `1` |
| changelog contiguous (REGRESSION) | n/a | `CONTIGUOUS` / `1` |

- Before the change, each NEW command printed the spec's "today" output: `store` was an argparse `invalid choice`. After the change, each prints its THEN.
- The in-flight refusal was confirmed to be migrate's own, not #45's fence. With the marker, it printed `factory store migrate: runs in flight on the store: run-0001-triage; wait until they finish`. Without the marker, #45's fence refused first with `role runs may not write the live store (...; in flight: run-0001-triage)`.
- **T-0025-A scenarios (REGRESSION):** all eleven parent WHENs, taken verbatim from the input file, printed their THENs on `267ef3b`:
  - `branch=factory-store seen_by_main=0`;
  - `exit=0 branch=factory-store restored=1`;
  - `exit=2 store=none local_branch=0 names=1,1`;
  - `exit=2 phantom=none store=unchanged` / `found=ready-for-triage`;
  - `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage`;
  - `exit=0 instance=written live=ready-for-triage`;
  - `exit=2 instance=none names_path=1`;
  - `exit=0 refused=0`;
  - `exit=2 refused=1`;
  - `store_branch=1 tickets_branch=0 never_tracked=1`;
  - `old_name=0 new_name=1`.

  The plain-store intermediate check, from the plan at `.factory/state/plans/T-0025.md:140`, printed `exit=0 branch=1 hint=1 dirty=0`. So the store that A leaves alone is still left alone.
- **Harness suite (REGRESSION),** `(P=$(mktemp -d /tmp/t0025-suite.XXXXXX); TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")` printed `300 passed in 239.19s (0:03:59)`.
- **Whitespace (REGRESSION),** `(git diff --check main...HEAD; echo "exit=$?")` printed `exit=0`.
- **Gate commands,** each run exactly as written: `git diff --check main...HEAD` exited 0 with no output; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `300 passed in 218.03s`.
- **Red first:** `tests/factory/test_store_migrate.py` ran before the code existed and printed `17 failed`. After the change it printed `17 passed`.

## Tests added/changed

- Added: `tests/factory/test_store_migrate.py` (new file). It reuses the helpers in `test_instance.py` and `test_store_branch.py` by import and does not modify them. The plan's departure explains why the file is separate: after A merged, `test_store_branch.py` became an existing test file.
- Changed: none.

## Known gaps and uncertainties

- **One refusal the spec does not list (please confirm).** `migrate` also refuses a PATH that lies inside the old store, for example `--to .factory/state/runs/x`. Step 5 deletes the old directory after verification, so without this refusal it would delete the new worktree with it, and every ignored file would be lost. Refusal 7's never-tracked test does not catch a path under the store that was never tracked. The refusal is checked with the others, exits 2 and writes nothing, and it has its own test case. A reviewer may want this raised as a spec change instead.
- **A pre-check folded into the refusal phase.** If `<branch>:<state_dir>` is not a tree, the command refuses with "the store … is not tracked on …". This happens, for example, when a store excluded from git has an empty `git status`. Without the check, step 1's `commit-tree` would fail. The fail-before-writing rule required one of the two.
- **Nested git repositories.** `git ls-files --others --ignored` lists a nested repository (a role's clone in its scratch directory) as `dir/`, not as its files. `_ignored_files` expands each such entry into its files and symlinks, so each one is copied and verified. "Copied" counts files after that expansion. Empty directories are not carried. A `factory:` marker in `_ignored_files` records this. factory: markers added: 1 (`factory/cli.py`, `_ignored_files`).
- **The file-count check.** Step 4's count lists the ignored files again inside the new worktree, under the store's own ignore rules. Suppose a file under the old store is ignored only by the integration checkout's root `.gitignore`, say `*.pyc`. The new worktree does not ignore it, so its `git status` is not clean and the migration exits 1, undone. That is the spec's behaviour, but such a store cannot be migrated until the file is removed.
- **The step-4 failure message.** The mismatch exits 1 through `main()`'s generic handler, so stderr reads `factory: RuntimeError: factory store migrate: the copy at … does not match: runs/…/n.txt differs; …`. The file is named as required, but the `RuntimeError` prefix is cosmetic noise.
- **How the mismatch is tested.** The test runs the CLI in a subprocess through an inline `python -c` launcher that patches `shutil.copy2`. The production CLI honours no switch. It cannot run in-process, because pytest imports `tests/factory` as the top-level package `factory`, which shadows the harness package.
- **Refusal 3 when `integration_branch` is unset.** With no `integration_branch` in the config, the harness takes whatever branch is checked out as the integration branch (`gitops.integration_branch`). In that case only a detached HEAD fails refusal 3.
- **The value written to `state_dir`.** It is PATH exactly as given, with no YAML quoting.
- **Lint.** ruff `I001` (import order) is reported on `factory/cli.py`. It is pre-existing: `main`'s copy reports the same error, and this change does not touch the imports.

## Out-of-scope observations

- The parent's Operator steps 2 and 3 are still to do: run the migration on this repo and on the Nanobot repo, and edit `.factory/context.md` and `.factory/README.md`. Until then, the README names `.factory/store/` as this repo's store location, which does not exist yet. The parent's Risk section accepts this.
- The README's "Re-derive with" cell for the ticket count now reads `ls .factory/store/tickets | wc -l`. That command fails on this repo until the migration runs.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every NEW and REGRESSION command printed its THEN on the committed head, and the full suite passed (300) under both gate forms; one extra refusal is disclosed for review.
ESCALATIONS:
- Please confirm or reject one refusal the spec does not list. `store migrate --to PATH` refuses when PATH lies inside the old store. The spec's step 5 deletes the old store after verification, so without this refusal such a PATH would delete the new checkout too, and every ignored run file would be lost. It is checked with the spec's eight refusals, exits 2, writes nothing, and is tested. If the operator wants the spec to say so, a one-line Gate edit adding it to refusal 7 covers it.
