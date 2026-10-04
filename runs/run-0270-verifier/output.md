Commit: 267ef3b4861ff29564a468c471d26f77c7f510e0

How this ran:
- PR: the given worktree `run-0270-verifier/wt`, detached at `267ef3b`, after `uv sync --frozen`. `git status --porcelain` was empty.
- Base: a detached worktree of `7a437ee` (equal to `main`), made in this run's scratch directory and removed afterwards.
- Every command ran under `bash` through the HOME wrapper, from the root of the checkout under test.
- Before each batch of scenarios, the parent's GIVEN block ran verbatim with `TMPDIR` set to a fresh `/tmp/t0025-ver.XXXXXX`, outside every git repository. That directory was removed after the batch.
- Each WHEN was copied verbatim from the sub-ticket or from the parent's T-0025-A list into its own file, and run once.

Per criterion:
- NEW | store migrate carries the store to factory-store at the new path
  - base: `exit=2` / `branch= same_tree=no scratch= old=kept main_tracks=9 seen_by_main=0` / `state_dir=.factory/state ticket=ready-for-triage` (argparse rejects `store`, as the spec predicts)
  - PR: `exit=0` / `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0` / `state_dir=.factory/store ticket=ready-for-triage`
  - PASS
- NEW | store migrate refuses an uncommitted store and a run in flight
  - base: `uncommitted: exit=2 names=0 branch=0` / `in flight: exit=2 names=0 branch=0 new=none`
  - PR: `uncommitted: exit=2 names=1 branch=0` / `in flight: exit=2 names=1 branch=0 new=none`
  - PASS
- NEW | A checkout of an older commit leaves the moved store untouched
  - base: `live=lost on=main`
  - PR: `live=live on=main`
  - PASS
- NEW | The README describes the store branch and the move
  - base: `store_branch=1 migrate=0 ffdx=1 premove=0 old_cost=0 old_refs=4`
  - PR: `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`
  - PASS
- REGRESSION | The changelog records the store branch in one contiguous entry | base: not run | PR: `CONTIGUOUS` / `1` | PASS
- NEW | Intermediate check: entry 53 names `store migrate`, and no entry 54 was added | base: `53. ` / `0` | PR: `53. ` / `1` | PASS
- REGRESSION | the eleven T-0025-A scenarios plus A's plain-store intermediate check | base: not run | PASS. On the PR each printed its THEN:
  - init creates the store on factory-store: `branch=factory-store seen_by_main=0`
  - init on a clone restores the store: `exit=0 branch=factory-store restored=1`
  - two remotes carry the branch: `exit=2 store=none local_branch=0 names=1,1`
  - init from a scratch directory inside the store: `exit=2 phantom=none store=unchanged` / `found=ready-for-triage`
  - init from a store on a detached HEAD: `exit=2 detached=yes phantom=none store=unchanged` / `found=ready-for-triage`
  - init in a separate repository under scratch: `exit=0 instance=written live=ready-for-triage`
  - init at a once-tracked store path: `exit=2 instance=none names_path=1`
  - merge after a store commit: `exit=0 refused=0`
  - merge after a code commit to main: `exit=2 refused=1`
  - design doc: `store_branch=1 tickets_branch=0 never_tracked=1`
  - build spec: `old_name=0 new_name=1`
  - plain-store intermediate check (plan `.factory/state/plans/T-0025.md`): `exit=0 branch=1 hint=1 dirty=0`
- REGRESSION | The harness suite passes | `(P=$(mktemp -d /tmp/t0025-suite.XXXXXX); TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")` | base: not run | PR: `300 passed in 266.48s (0:04:26)` | PASS
- REGRESSION | The store-branch change adds no whitespace errors | `(git diff --check main...HEAD; echo "exit=$?")` | base: not run | PR: `exit=0` | PASS

Every NEW criterion fails on the base for the reason the spec gives: `store` is not a command there, and the README and changelog lack B's text. Every NEW criterion passes on the PR.

The scope items not covered by a WHEN were checked by hand:
- The live store `~/dev/spec-factory/.factory/state/tickets` holds 52 tickets, and the README says 52.
- The README status date at `:9` is 2026-10-04.
- `git diff --stat 7a437ee HEAD` lists only `README.md`, `docs/changelog.md`, `factory/cli.py` and the new `tests/factory/test_store_migrate.py`. No existing test and no `.factory/**` file is touched.

Gate suite: PASS
  `git diff --check main...HEAD`: no output, exit 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `300 passed in 385.00s (0:06:24)`, exit 0.

Probes (all on the PR, on the `t0025-old.sh` fixture):
- A real copy mismatch, with no monkeypatch. Setup: `*.pyc` was ignored only by the integration branch's root `.gitignore`, and `.factory/state/a.pyc` was placed in the store. Result: `exit=1`. Stderr read `factory: RuntimeError: factory store migrate: the copy at .factory/store does not match: 0 ignored files at the new path, 1 listed; removed the new worktree and branch factory-store, the store at .factory/state is unchanged`. Afterwards: `new=none old=kept branch=0 wts=1 yaml=same exclude=same tracked=9 dirty=0`. → OK. The undo path works outside the test's monkeypatch. Two points about the message:
  - It names a file count, not a file. The spec says "naming the first file that differs", but here no file's bytes differ, so there is no such file to name.
  - The `RuntimeError` prefix is noise. The implementer disclosed both.
  - This store cannot be migrated until the file is removed. The implementer disclosed that too.
- Run from a subdirectory (`sub/`) with `--to .factory/deep/store`. The store held an ignored file with a space and a non-ASCII character in its path and a NUL byte in its content, plus a 3 MB random file. Result: `exit=0`, `copied: 2`, `same=yes big=yes state_dir=.factory/deep/store ex=1 ticket=ready-for-triage seen=0` → OK. PATH resolves against the repo root, not the caller's directory, and nested parent directories are created.
- A trailing slash: `--to .factory/store/`. Result: `exit=0`, `state_dir=.factory/store/`, and `ticket show` finds T-0001. A second `migrate` after committing is refused with `exit=2 ... is already the checkout of factory-store` → OK.
- A sibling path sharing the old store's name as a prefix: `--to .factory/state2`. The new inside-the-store refusal does not fire on it: `exit=0 state_dir=.factory/state2 old=gone new=yes` → OK. The check compares whole path components, not a string prefix.
- A run in flight with no `FACTORY_DISPATCH` marker. #45's fence refuses first: `exit=2 branch=0 new=none`, with stderr `role runs may not write the live store (...; in flight: run-0001-triage); use a throwaway FACTORY_STATE` → OK. With the marker, the acceptance scenario above shows that B's own refusal names the run.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran as written on both trees. Each NEW criterion failed on the base for the spec's stated reason and passed on `267ef3b`. Both gate commands and the suite command passed. A real mismatch, with no test hook, was undone completely.
ESCALATIONS:
- `store migrate` has one refusal the spec does not list: it refuses a PATH inside the old store. The implementer added it, disclosed it, and asked for a decision. It looks correct. Without it, step 5's deletion of the old store would also delete the new checkout and every ignored file just copied there. A gate edit to refusal 7 would bring the spec into line. This is for the operator. It is not a criterion failure.
- Spec wording, minor: B step 4 says to exit 1 "naming the first file that differs". When the mismatch is a file-count or `git status` difference (probe 1), there is no such file, and the message names the count instead. Consider rewording step 4 to "naming the first difference".
