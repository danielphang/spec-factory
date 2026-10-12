Sub-ticket: T-0045.3 (ST-3, part D of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Branch `factory/T-0045.3`, commit `c8308f2` on base `1c5a152`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0045.3`.

## What changed

No test file in the harness suite imports from another test file now. A scenario fixture that more than one test file uses lives in one place, `tests/factory/_fixtures.py`. The harness itself does not change. The suite passes at 576 tests in a fresh clone.

**Part D, item 1: new `tests/factory/_fixtures.py`, 655 lines.**
- It holds every name in design.md's D table. Each body is copied byte for byte. I checked this by searching `_fixtures.py` for each original line range read from `git show HEAD:…`. The three ranges that do not match are the two renames below and `test_store_branch.py`'s `state`. That `state` was dropped because the copy from `test_live_store_guard.py` is identical and kept.
- The only import a moved body needs is `from ._cli import BIN, REPO, CliStore, approved_parent, cli, git_repo, js, tree`.
- No test function moved.
- The moved bodies also need some module-level names the table does not list, so those moved too, unchanged:
  - from `test_spec_amend.py`: `SPEC`, `TWO` and `spec`, which `Fixture`, `V1` and `V2` use;
  - from `test_drive.py`: `FIXTURE_INSTANCE`, which is `Store`'s default;
  - from `test_shepherd.py`: `STUBS`, `MAX_SPEC_ROUNDS` and `Run`, which `Shepherd` uses;
  - from `test_live_store_guard.py`: `RULE`, which `assert_refused` uses;
  - from `test_drive_build.py`: its stand-in `claude` script, which `BuildStore` uses.
- `test_drive_guard.py` also imported `assert_refused` and `request` from `test_live_store_guard.py`. The D table misses these two. The spec's rule says every name one test file imports from another moves, so they moved too.
- Two pairs of names would clash inside the single module. Each clash is fixed with one rename in `_fixtures.py`. Both are listed under ESCALATIONS:
  - `test_drive.py` and `test_drive_build.py` each define a different `STANDIN`, and both `Store` and `BuildStore` refer to the module-level name. The build one is now `BUILD_STANDIN`. This changes one token in `BuildStore`'s body: `write_text(STANDIN.format(` became `write_text(BUILD_STANDIN.format(`.
  - `test_store_branch.py` and `test_live_store_guard.py` each define a different `request`: one writes `r.md` with "# demo", the other `r2.md` with "# other". The table names the store-branch one, so it keeps the name. The live-store one is `other_request`. Its importers use `from ._fixtures import other_request as request`, so no call site changes.

**Part D, item 2: imports.**
- The files the names came from import them back from `._fixtures`, but only the names they still use:
  - `test_subtickets.py`, `test_build_startup.py`, `test_sibling_tests.py`, `test_spec_amend.py`, `test_spec_drift.py`, `test_drive.py`, `test_drive_build.py`, `test_live_store_guard.py`, `test_store_branch.py`, `test_shepherd.py` and `test_parent_close_reuse.py`.
  - `STANDIN` and `RULE` are no longer used in their old files, so they are not imported back.
- Every importer of another test file now imports from `._fixtures` or `._cli`:
  - `test_build_startup.py`, `test_drift_siblings.py`, `test_drive_build.py`, `test_drive_guard.py`, `test_killed_checker.py`, `test_live_store_guard.py`, `test_parent_close_reuse.py`, `test_plan_fields.py`, `test_role_inputs.py`, `test_spec_drift.py`, `test_stats.py`, `test_store_branch.py`, `test_store_migrate.py` and `test_whole_spec_plan.py`.
- The form of `js` follows the file it came from, as ST-1 left it:
  - `test_build_startup.py` and `test_plan_fields.py` took `js` from `test_subtickets.py`, whose copy asserts exit 0, so they import `js_ok as js`;
  - the importers of `test_instance.py`'s and `test_p0_cli.py`'s `js` import plain `js`.
- `cli as factory_cli` is kept in `test_stats.py`.
- The two `f = test_spec_amend.f` lines, and their `from . import test_spec_amend` imports, are now imports of `f`. The pytest fixtures `f` and `target` are imported with `# noqa: F401`, as before.
- Imports that the move left unused were removed:
  - `os`, `json`, `sys`, `Path` and `pytest` where nothing uses them any more;
  - `CliStore`, `approved_parent` and `git_repo` where only a moved body used them;
  - the `REPO` re-export, with its `noqa` comment, in `test_p0_cli.py` and `test_spec_amend.py`. It existed only for the importers this ticket rewrites.
- `test_instance.py` needed no change: ruff reports every name it imports as used. `test_store_migrate.py`: only its two import lines changed; its in-process CLI code is untouched.
- Two non-import lines changed in `test_shepherd.py`:
  - its docstring said "`Shepherd` at the bottom" and now says "`Shepherd`, in `_fixtures.py`";
  - the section header for the moved `Shepherd` was removed, since nothing followed it any more.

## Acceptance results

All commands ran from the worktree through the fresh-HOME wrapper. Each WHEN was taken verbatim from v2.md by script.

- **NEW: No test file imports from another test file**
  - Before: `cross-test imports: 27`, followed by the 27 sites from `test_build_startup.py:12` to `test_whole_spec_plan.py:24`.
  - After: `cross-test imports: 0`.
- **REGRESSION: The shared constants and wrappers are defined once.** After: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`.
- **REGRESSION: The approved-parent and empty-repository setups are written once.** After: `approved-parent sequences: 1 _cli.py:73` and `empty-commit repo setups: 1 _cli.py:63`.
- **REGRESSION: Only the duplicate test and its assertions are gone.** After:
  ```
  pair: 3
  removed: 1
  removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed
  added: 0
  missing: 2
  missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert cp.returncode == 0 and js(cp)['status'] == 'KILLED'
  missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert yaml.safe_load((store / 'runs' / rid / 'meta.yaml').read_text())['status'
  ```
  stderr held only `tar: Failed to set default locale`, which the spec says to ignore.
- **REGRESSION: The suite is shorter.** After: `pairs: 3; test lines before: 28728, after: 28510, change: -218`. This sub-ticket's own pair adds 57 lines net (722 insertions, 665 deletions across 21 files): the 655-line `_fixtures.py` plus the import lines.
- **REGRESSION: A suite run in a fresh clone passes and adds nothing to the checkout.** After: `576 passed in 579.03s (0:09:39)`, then `paths changed: 0`, with nothing after it.
- **Gates**, each run exactly as written:
  - `git diff --check main...HEAD`: exit 0, no output;
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 564.68s (0:09:24)`.
- **Extra check, not a gate.** This repo configures no ruff, so I ran `ruff check --isolated --select F,E9,I --line-length 120 tests/factory` with the ruff in `~/dev/nanobot/.venv-test`, before and after.
  - Before: 4 F811 findings, all on the imported `target` fixture in `test_drive_guard.py`.
  - After: no F401, F821 or I001 findings. The remaining F811 findings are the same kind, an imported pytest fixture (`target` or `f`) used as a test argument. There are now more of them because `f` and `target` are imported in more files than before.

## Tests added/changed

- Added `tests/factory/_fixtures.py`. It is a helper module, not a test file: it is not named `test_*`, so pytest does not collect it.
- Changed, each listed under the sub-ticket's "Tests to change":
  - `test_p0_cli.py`, `test_subtickets.py`, `test_sibling_tests.py`, `test_spec_amend.py`, `test_whole_spec_plan.py`, `test_drive.py`, `test_shepherd.py`;
  - `test_build_startup.py`, `test_drive_build.py`, `test_plan_fields.py`, `test_drift_siblings.py`, `test_drive_guard.py`, `test_killed_checker.py`, `test_live_store_guard.py`;
  - `test_parent_close_reuse.py`, `test_role_inputs.py`, `test_spec_drift.py`, `test_stats.py`, `test_store_branch.py`, `test_store_migrate.py`.
- In each of these, only module-level helpers moved out and import lines changed, plus the `test_shepherd.py` docstring line and section header described above. No test function and no assertion changed. The assertion comparison above shows nothing missing except the one test ST-1 removed.
- These files are untouched:
  - `test_instance.py`, including T-0044's lines 109 and 354;
  - `_cli.py` and `conftest.py`;
  - `clean_harness_cli.py`;
  - the four design-block files (`test_writing_standard.py`, `test_coding_standard.py`, `test_turn_economy.py`, `test_decision_log.py`).

## Known gaps and uncertainties

- Two renames in `_fixtures.py` depart from "with the body unchanged": `BUILD_STANDIN` and `other_request`. The first changes one token in `BuildStore`'s body. They cannot be avoided once both members of each clashing pair live in one module. The tests do the same thing as before: the build store still writes the build stand-in, and the live-store tests still write `r2.md`.
- The D table is incomplete. It misses `test_live_store_guard.py`'s `assert_refused` and `request`, and the dependencies listed under item 1. I moved them under the spec's general rule.
- `MAX_PR_ROUNDS` stays in `test_shepherd.py`. Nothing uses it, so it did not move with `MAX_SPEC_ROUNDS`.
- `factory:` markers added: none.

## Out-of-scope observations

- Several moved docstrings still name helpers by their old file, for example `test_drive_build.py`'s "(test_drive.Store)", and "test_instance.STRIP" or "test_instance.cli" in `test_live_store_guard.py` and `test_store_branch.py`. These are prose references to where a helper comes from, so I left them alone. A later de-bloat ticket could update them.
- `test_store_branch.py` keeps its own `RULE`, identical to the one now in `_fixtures.py`. It is not in the D table and no other file imports it.
- `MAX_PR_ROUNDS` in `test_shepherd.py` is never used.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The gates and all six scenarios pass on this commit, and a script confirmed that every moved block except the two renames is a verbatim copy.
ESCALATIONS:
- The spec cannot be met exactly as written. Two pairs of names clash once they share one module: test_drive.py's and test_drive_build.py's `STANDIN`, and test_store_branch.py's and test_live_store_guard.py's `request`. So "body unchanged" cannot hold for both members of each pair. I renamed one of each pair in `_fixtures.py` (`BUILD_STANDIN`, `other_request`). That changes one token in `BuildStore`'s body; the `request` users import the new name under the old one. A human should confirm this small departure, or amend the spec to allow it.
- The spec's D table leaves out names that must move for the cross-test import count to reach 0: test_live_store_guard.py's `assert_refused` and `request`, which test_drive_guard.py imports, and the module-level names the moved bodies depend on. I moved them under the spec's general rule ("Every name a test file imports from another test file today moves into it").
