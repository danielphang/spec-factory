Sub-ticket: T-0045.1 (ST-1, part A of T-0045; parent spec `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`)
Branch: `factory/T-0045.1`, head `3478d1fddf4b207fdf0a04ba34ae5459ec11968c`, base `2b9baf506852d6f74124b1f5eadbdd84f6bad52b`. One commit. 32 files changed, 120 insertions, 247 deletions.

## What changed

Before this change, each file in the harness test suite (`tests/factory/`, the tests for the code that runs the factory) had its own copy of the same small helpers. A suite run also left `.pyc` files in the harness package. This sub-ticket adds one shared helper module, stops the bytecode writes, and deletes one duplicate test. No harness code, command or document changes.

A.1 — new `tests/factory/_cli.py`. It holds `REPO`, `BIN`, `CLEAN_CLI`, `STRIP`, `cli`, `run`, `run_env`, `js`, `js_ok`, `ticket` and `tree`.
- `STRIP`, `CLEAN_CLI` and `cli` are moved from `test_instance.py` unchanged, including the launcher-split comment.
- `run` is `test_p0_cli.py`'s form, with `stdin=None`. Passing `input=None` to `subprocess.run` is the same as not passing it, so the plain-form callers are unaffected.
- `run_env` is the environment-dict form from `test_redispatch_rows.py`.
- `js` only parses. `js_ok` asserts `cp.returncode == 0`, with stderr as the message, and then calls `js`.
- `ticket(store, tid="T-0001")`.
- `tree` is as in `test_instance.py`.

The leading underscore keeps pytest from collecting the file.

A.2 — 30 test files delete their module-level copies and import the names from `._cli`:
- Files whose `js` asserted exit 0 import `js_ok as js`: `test_redispatch_rows`, `test_replan`, `test_resolve_rulings`, `test_store_setup`, `test_subtickets` and `test_superseded_plan`.
- The two environment-dict files, `test_redispatch_rows` and `test_resolve_rulings`, import `run_env as run`.
- Some stdlib imports (`os`, `json`, `subprocess`, `sys`, `yaml`) were used only by the deleted copies. I removed them, and nothing else.
- Some files still have their names imported by other test files. Those files import the names back, so the cross-file imports keep working until ST-3:
  - `test_instance.py` exports `BIN`, `REPO`, `STRIP`, `cli`, `js` and `tree`.
  - `test_drive.py` exports `BIN` and `REPO`.
  - `test_spec_amend.py` exports `REPO`.
  - `test_subtickets.py` exports `js`, `run` and `ticket`.
  - `test_p0_cli.py` exports `REPO`, `js` and `run`. Its `REPO` is used only by `test_role_inputs.py`, so that import carries `# noqa: F401` with the reason.
- `cli` in `test_store_setup.py` and `test_harness_lock.py` stays, and so does `git_repo` in `test_instance.py` and `test_store_setup.py`. ST-2 handles those.
- An AST comparison of every class and function that survives in the 31 edited test files found 0 changed bodies. That includes the four design-block helpers named in the parent spec's Out of scope and every test function in `test_instance.py`.

A.3 — `tests/factory/conftest.py` now sets `os.environ["PYTHONDONTWRITEBYTECODE"] = "1"` and `sys.dont_write_bytecode = True`, under one comment line saying why.

A.4 — I deleted `test_run_finish_without_output_is_killed` from `test_p0_cli.py`. `test_empty_output.py:62-63` still covers the KILLED override.

## Acceptance results

I ran every command from the worktree through the fresh-HOME wrapper. A NEW check is new behaviour that should fail before the change and pass after it.

- **NEW "Only the duplicate test and its assertions are gone"** (the parent's command, run exactly as written):
  - Before, on `2b9baf5`: `pair: 0`, `removed: 0`, `added: 0`, `missing: 0`. HEAD was `main`, so there was nothing to compare.
  - After, on `3478d1f`:
    ```
    pair: 1
    removed: 1
    removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed
    added: 0
    missing: 2
    missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert cp.returncode == 0 and js(cp)['status'] == 'KILLED'
    missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert yaml.safe_load((store / 'runs' / rid / 'meta.yaml').read_text())['status'
    ```
    Exactly the one test is gone, no test was added, and the only assertions missing are that test's two. tar also printed `Failed to set default locale` twice on stderr; the spec says to expect this.
- **NEW "The suite is shorter"**:
  - Before: `pairs: 0; test lines before: 0, after: 0, change: 0`.
  - After: `pairs: 1; test lines before: 9710, after: 9583, change: -127`. The test files are 127 lines shorter in total.
- **NEW "A suite run in a fresh clone passes and adds nothing to the checkout"**:
  - Before, on `2b9baf5`: `577 passed in 404.51s (0:06:44)`, then `paths changed: 13`. These were `./factory/__pycache__` and 12 `.pyc` files in it.
  - After, on `3478d1f`: `576 passed in 545.63s (0:09:05)`, then `paths changed: 0`, with nothing after it. The suite passes, and the run no longer writes into the checkout. 576 is 577 minus the deleted test.
- **NEW, intermediate: "The shared constants and wrappers are defined once"**:
  - Before: `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`.
  - After: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1`, which is the expected interim value. `git_repo=2` and `approved_parent=1` are ST-2's work.
- **Gates**, run exactly as written:
  - `git diff --check main...HEAD` exited 0 with no output, so the diff has no whitespace errors.
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 526.71s (0:08:46)`, exit 0. I logged it to `scratch/gate.log` and waited for it to finish.
  - After the gate run, `git status --ignored` in the worktree shows only `tests/factory/__pycache__/` and `.venv/`, and no `factory/__pycache__`. The spec expects pytest to write `tests/factory/__pycache__`.

## Tests added/changed

- Added `tests/factory/_cli.py`. It is a helper module, not a test file.
- Changed `tests/factory/conftest.py`: it gains the bytecode guard (parent Decision: the guard goes in conftest).
- Changed `tests/factory/test_p0_cli.py`: the duplicate test is deleted (parent Decision: the removed test), and its helper copies are replaced by imports.
- Changed the other 29 files listed under "Tests to change": their module-level helper copies are replaced by imports. No assertion inside a test function changed.

## Known gaps and uncertainties

1. **The `cli` functions of `test_coding_standard.py` and `test_writing_standard.py` stay.** The sub-ticket keeps only those of `test_store_setup.py` and `test_harness_lock.py`, but these two do not have the same body as the shared `cli`, so swapping them would change what the tests do:
   - `test_coding_standard.py`'s `cli` asserts exit 0 on every call. Swapping it would drop that assertion from the module fixture.
   - Neither function has the launcher split. They always run `bin/factory`. The shared `cli` runs `clean_harness_cli.py` (the test-only launcher that skips the uncommitted-edit refusal) for every command except `init` and `paths`. `test_store_setup.py`'s `cli` has the same body as `test_writing_standard.py`'s, and the parent design keeps it for exactly that reason ("one has no launcher split").

   I followed the parent's Out-of-scope rule for helpers with differing bodies. The acceptance checks do not count `cli`. If the operator wants these two swapped too, it is a one-line import change in each file. For `test_coding_standard.py` it also needs a decision on where its exit-0 assertion goes.
2. **`STRIP` now also removes `FACTORY_DISPATCH` in five files.** The five files had a 5-name `STRIP`: `test_coding_standard`, `test_harness_lock`, `test_store_setup`, `test_turn_economy` and `test_writing_standard`. They now import the 6-name tuple moved from `test_instance.py`, which also lists `FACTORY_DISPATCH`. That variable is the dispatcher's marker that lets a write through while runs are in flight on the live store. None of these files sets or checks it (grep: it appears only in `test_store_branch.py` and `test_live_store_guard.py`). So the change only stops a value inherited from a dispatcher shell from reaching these subprocesses. The suite passes with it.
3. `test_p0_cli.py` carries one `# noqa: F401` for the `REPO` it only re-exports. It goes away when ST-3 moves cross-file imports out.
4. The `.pyc` check relies on `sys.dont_write_bytecode` being set before `test_cost_once.py` and `test_subtickets.py` load harness modules through `importlib`. conftest runs before collection, so it is set in time. The fresh-clone check above shows this: `paths changed: 0`.

`factory:` markers added: none.

## Out-of-scope observations

- In the sub-ticket's listing, `test_turn_economy.py` keeps its own `_cli` function at line 77. It is a separate helper under another name with no launcher split, and I left it alone. It may belong in a later pass.
- Suite runs on this machine took 6:44 to 9:05. The suite gate is now close to the 10-minute foreground limit some runners use.

## Responses to findings

n/a, first round.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All four NEW checks and both gates were run on `3478d1f` and printed the expected output. The two deviations, the two `cli` functions kept and `STRIP` widened, are listed under Known gaps with their effect.
ESCALATIONS: none
