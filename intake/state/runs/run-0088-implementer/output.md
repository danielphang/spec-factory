Sub-ticket: T-0012.4 (parent `intake/state/specs/T-0012/v3.md`, design C.2–C.5). Branch `factory/T-0012.4`, worktree `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.4`. There is no remote, so the branch is the PR. Head is `010d1b00c5835c7022a72771c63f63f8b6ab3707`. Merge-base with `main` is `bed7e28`. `main` is `f809c69`, which changes only `intake/state/**`. I did not merge it in: this is not a conflict run, and the gate uses `main...HEAD`.

This run continues implementer run-0069, which left the C implementation on the branch and stopped as BLOCKED on one existing test. The operator has since ruled on that test (Tests to change). This run applied that ruling, fixed a whitespace slip in run-0069's commit, re-read the C code, and re-ran every acceptance command and gate.

Commits (`git log --oneline main..HEAD`):
- `7a89605` test(T-0012.4): harness lock tests (C.2-C.5), red before the guard (run-0069)
- `fe6303c` harness(T-0012.4): harness lock — refuse an unaccepted or modified harness on the instance's own store, --accept-harness (C.2-C.4) (run-0069)
- `954eff7` test(T-0012.4): changed paths are listed in git's order; compare them as a set (run-0069)
- `1ac0ec3` test(T-0012.4): give the pre-lock instance test a lock (operator ruling 2026-10-03; C.2 stands) (this run)
- `010d1b0` harness(T-0012.4): restore the space lost before = on PROTECTED_PLACEHOLDER (this run)

Final diff (`git diff --stat main...HEAD`): `factory/cli.py` +6/-1, `factory/instance.py` +52, `tests/factory/test_harness_lock.py` +281 (new), `tests/factory/test_instance.py` +1. In total, 4 files, 340 insertions and 1 deletion.

## What changed (per lettered part)

- **C.2: lock check on the instance's own store.**
  - `factory/cli.py` `main()` now resolves the instance (`instance.require()`), loads its config and gets the store root. It then calls `instance.guard(inst, cfg, root, a.accept_harness)` before running the command.
  - `init` and `paths` still return through the existing early branch, so they are exempt.
  - `guard()` (`factory/instance.py`) returns at once unless `is_own_store()` is true, which means `FACTORY_STATE` is unset or resolves to the instance's `state_dir`.
  - It compares `read_lock()`, the stripped first line of `<instance>/harness.lock` (`None` when the file is missing or empty), with `harness_revision()` (C.1, from T-0012.3).
  - On a mismatch it refuses with `harness <rev> is not the revision this instance accepted (<lock>|none); rerun with --accept-harness <rev> to accept it`, and the command exits 2. Every refusal happens before the command runs, so nothing is written.
- **C.3: `--accept-harness SHA`.**
  - It is a top-level argparse option (`factory/cli.py`, `build_parser`), so it is written before the subcommand.
  - The SHA must match `[0-9a-f]{40}` and equal the running revision. Otherwise the command exits 2, and the lock is unchanged and nothing is logged.
  - On a match, the harness writes `<rev>\n` to the lock and logs a `harness.accepted` event (`instance`, `old`, `new`) in the instance's store. Then the command runs.
- **C.4: uncommitted harness edits are refused.**
  - `harness_changes()` runs `git -C <HARNESS> status --porcelain -- factory bin/factory agents pyproject.toml uv.lock`. `<HARNESS>` is the running checkout.
  - If git prints anything, the command is refused with `harness <path> has uncommitted changes:` followed by one path per line.
  - This check runs before the accept step, so `--accept-harness` cannot override it.
  - If `git status` fails, or the revision cannot be read, the command is also refused (exit 2) rather than allowed through.
- **C.5:** new test file `tests/factory/test_harness_lock.py` (24 cases).
- **Changes in this run:**
  - `tests/factory/test_instance.py`: one line, exactly as the operator ruled (see Tests added/changed).
  - `factory/instance.py`: `fe6303c` had turned `PROTECTED_PLACEHOLDER = "…"` into `PROTECTED_PLACEHOLDER ="…"`. That was an accidental formatting change. `010d1b0` restores the line, which is now identical to `main` again. Behaviour does not change.

## Acceptance results

Method:
- I extracted every WHEN from input.md with a script (`str` slicing between the backticks), not by retyping, and ran each one with `bash` from the checkout under test after `uv sync --frozen`.
- For missing-lock-refused, the script substituted `rm -f $T/.factory/harness.lock` for the `printf … > $T/.factory/harness.lock` part of lock-mismatch-refused, after asserting that the original text appears exactly once.
- **Before:** a scratch clone of the branch, detached at `main` (`f809c69`, the recorded base, with harness code identical to `bed7e28`), with its own `uv sync --frozen`.
- **After:** the worktree at `010d1b0`. `git status --porcelain` was empty before and after the runs.

| Scenario | Label | Before (`f809c69`) | After (`010d1b0`) |
|---|---|---|---|
| lock-mismatch-refused | NEW | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| accept-current-revision-rewrites-lock | NEW | `init=0` / `exit=2 lock_is_rev=no logged=0` | `init=0` / `exit=0 lock_is_rev=yes logged=1` |
| accept-other-revision-refused | REGRESSION | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` | same |
| throwaway-store-ignores-lock | REGRESSION | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same |
| dirty-harness-refused | NEW | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` |
| missing-lock-refused | NEW | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` |
| init-and-paths-exempt | REGRESSION | `paths=0 init=0 lock=0000000000000000000000000000000000000000` | same |
| accept-does-not-override-dirty | REGRESSION | `exit=2 lock_same=yes tickets=0` | same |
| harness-files-in-repo | REGRESSION (T-0012.3) | — | `agents=6 green_only=0` |
| role-prompt-text-unchanged | REGRESSION (T-0012.3) | — | `changed=0 of 14` |
| init-creates-instance-in-throwaway-target | REGRESSION (T-0012.3) | — | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` |
| store-command-from-subdirectory-uses-target-instance | REGRESSION (T-0012.3) | — | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` |
| command-outside-any-instance-refused | REGRESSION (T-0012.3) | — | `exit=2 created=0 names_instance=1` |
| factory-instance-override-from-elsewhere | REGRESSION (T-0012.3) | — | `init=0` / `found=1` |
| composed-input-opens-with-instance-context | REGRESSION (T-0012.3) | — | `init=0` / `first=[CTX-MARKER for demo]` |
| run-system-prompt-names-instance | REGRESSION (T-0012.3) | — | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` |
| paths-name-harness-workflows-and-instance | REGRESSION (T-0012.3) | — | `init=0` / `True True True True` |
| harness-suite-passes-after-uv-sync | REGRESSION | (run-0069 at `bed7e28`: `sync=0` / `92 passed`) | `sync=0` / `116 passed in 76.71s (0:01:16)` |
| green-harness-still-present | REGRESSION | — | `green keeps its harness` |
| whitespace (sub-ticket diff) | REGRESSION | — | `git diff --check main...HEAD` → `exit=0` |

Every NEW criterion failed at base as described and now passes. Every REGRESSION criterion passes. The four C regressions pass at base vacuously, as the operator's relabel notes. The discriminating evidence is the new tests below.

I also ran whitespace-clean with `BASE=$(git rev-parse main)`: `git diff --check "$BASE" HEAD` → `exit=0`.

Gate commands, run from the worktree exactly as written:
- `git diff --check main...HEAD` → no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 77.48s (0:01:17)`.

## Tests added/changed

- **Added: `tests/factory/test_harness_lock.py`** (24 cases, run-0069).
  - Red evidence, re-run this run: I copied the file into the base clone and ran it against base code, which gave `18 failed, 6 passed in 5.10s`.
  - The 6 that pass at base are the "must not refuse" cases: `test_fresh_init_lock_is_the_running_revision_and_commands_run`, `test_lock_compares_its_stripped_first_line`, `test_init_and_paths_are_exempt_and_leave_the_lock`, `test_throwaway_store_runs_whatever_the_lock_says`, `test_ignored_and_non_harness_changes_do_not_count` and `test_modified_harness_still_runs_throwaway_stores_init_and_paths`.
  - All 24 pass at head.
  - Coverage:
    - **C.2:** a mismatched, empty or missing lock is refused with the exact message. Five different commands are refused. `init` and `paths` are exempt. `FACTORY_STATE` pointing elsewhere is not checked, and `FACTORY_STATE` naming the own store is checked.
    - **C.3:** accepting the current revision rewrites the lock and logs `old`/`new`. A short SHA, another 40-hex value, a prefix and an uppercase SHA are each refused, with the tree unchanged.
    - **C.4**, on a local clone so this checkout is never edited: a modified tracked file and an untracked file under `agents/` are refused and named. `--accept-harness` does not override a dirty harness. Ignored files and non-harness edits do not count. A dirty harness still runs throwaway stores, `init` and `paths`.
    - **Upgrade flow:** a docs-only commit does not trip the lock, a `factory/` commit does, and `--accept-harness <new>` clears it.
- **Changed: `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`.**
  - It is listed under Tests to change by the operator's ruling of 2026-10-03.
  - The change is one added line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`.
  - **Why:** the test predates the lock and builds an instance with no `harness.lock`, which C.2 refuses.
  - Before the line, at `954eff7` with a clean tree: `1 failed, 21 deselected`, and the assertion at line 247 fails. After it: `1 passed, 21 deselected in 0.61s`.
  - No assertion was changed, and `config` was not exempted.

## Known gaps and uncertainties

- **The suite passes only from a committed harness tree.**
  - Evidence: in a scratch clone of head, I appended `# dev edit` to `factory/__init__.py` and ran the suite. It gave `23 failed, 93 passed`: 17 in `test_harness_lock.py` and 6 in `test_instance.py`.
  - Cause: those tests build own-store targets (`FACTORY_STATE` unset) driven by this checkout's `bin/factory`, so C.4 refuses them by design.
  - C.4's prose says "a harness under development ... still runs its own tests against throwaway stores". That holds for the imported suite but not for the B/C tests, which use own stores.
  - The gate runs on committed branches, so it is unaffected.
  - I hit this myself in this run. A run with `factory/instance.py` uncommitted failed the listed test with the C.4 message. I confirmed the cause with a reverted probe edit (`harness … has uncommitted changes:\nfactory/__init__.py`), and the test passed once committed.
  - I did not change the tests, because that would be a design choice beyond this sub-ticket.
- **`--accept-harness` is silently ignored where the guard does not apply:** with `init` or `paths`, and when the store in use is not the instance's own. The spec does not say what should happen there, and a reviewer may prefer a refusal.
- **Format of changed paths in the C.4 message.** They come out in `git status --porcelain` order, taken as `line[3:]`. A rename prints `old -> new`, and git quotes paths that contain special characters.
- **Names and formats the spec leaves open.** The log event is called `harness.accepted`; the spec does not name it. The lock is written as `<rev>\n`, the same format `init` writes.
- **Which checkout is checked.** The revision and dirty checks use the running checkout (`instance.HARNESS`), not `instance.yaml`'s `harness:` value. This follows the plan's reading. A refusal on a mismatch between the two is out of scope.
- **Merge-base.** The branch does not contain `f809c69`, the recorded base, which changes only `intake/state/**`. I did not merge `main` in, because this is not a conflict run.
- **Who wrote what.** The C code and tests were written by run-0069. I re-read the code diff in full (`git diff main...HEAD -- factory`) and re-ran everything above, but I did not write it.
- **Commit messages.** My two commits follow the branch's existing message style (no trailers).

## Out-of-scope observations

- The `factory/workflows/*.js` header comments do not mention `--accept-harness` or the upgrade step (run-0069 noted this too). The README is covered by E.6.
- See the first gap above: if the B/C tests should run from a dirty dev checkout, as C.4's text implies, they would need to drive a clean clone or a throwaway store. That is a spec/test-design question for a later ticket.

## Conflict-run resolution (run-0085)

The merge gate refused head `010d1b0` because it did not contain `main` (`68e8945`). I merged `main` into the branch with `git merge --no-ff main` (no rebase, no force-push), which made merge commit `a5f13292ab8f2a5655daba442f45d81ed81d8a94`, now the branch head. There were no conflicts. `main` had moved from `bed7e28` only under `intake/state/**` (pipeline records: approvals, log, plan, run records, sub-ticket specs, tickets). The branch touches none of those paths. After the merge, `git merge-base --is-ancestor main HEAD` succeeds, and `git diff --stat main HEAD` shows exactly this sub-ticket's four files (`factory/cli.py`, `factory/instance.py`, `tests/factory/test_harness_lock.py` (new), `tests/factory/test_instance.py` +1; 340 insertions, 1 deletion), the same as before. The harness revision (`git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`) is still `010d1b00c5835c7022a72771c63f63f8b6ab3707`, because the merge changes no harness path. I re-ran the gates in the worktree after `uv sync --frozen` (exit 0), with `FACTORY_*` unset and a clean tree: `git diff --check main...HEAD` printed nothing and exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `116 passed in 88.72s (0:01:28)`. Nothing else changed. The statements above that head is `010d1b0` and that `main` was not merged in describe the pre-merge state. The merge supersedes them.

## Conflict-run resolution (run-0088)

The merge gate refused head `a5f13292ab8f2a5655daba442f45d81ed81d8a94` because it did not contain `main`, which had moved to `6921dfd` (the T-0012.5 merge). I merged `main` into the branch with `git merge --no-ff main` (no rebase, no force-push). That made merge commit `be292addbee09d9b2709fd84b54e63de8e9f6477`, now the branch head. There were no conflicts. `main` brought in only `dev/build-harness.spec.md`, `docs/changelog.md` and `docs/design.md` (7 insertions, 6 deletions). The branch touches none of them.

Checks after the merge:
- `git merge-base --is-ancestor main HEAD` succeeds.
- `git diff --stat main HEAD` still shows exactly this sub-ticket's four files, with 340 insertions and 1 deletion.
- The harness revision is still `010d1b00c5835c7022a72771c63f63f8b6ab3707`, because no harness path changed.
- Gates, run from the worktree after `uv sync --frozen` (exit 0), with no `FACTORY_*` set and a clean tree before and after: `git diff --check main...HEAD` printed nothing and exited 0, and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `116 passed in 81.80s (0:01:21)`.

Nothing else changed. The round-1 reviewer (APPROVE, two NITs) and verifier (VERIFIED) findings were on `a5f1329`, and the code diff they checked is unchanged.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Both merges were conflict-free and brought in only paths this branch does not touch. The code diff against `main` and the harness revision are unchanged, and both gates pass at `be292ad` (`116 passed`).
ESCALATIONS: none
