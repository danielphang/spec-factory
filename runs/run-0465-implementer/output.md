Sub-ticket: T-0045.2 (ST-2, parts B and C of T-0045 v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Branch `factory/T-0045.2`, head `a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4`, base `6ac73f1`. Worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0045.2`.

## What changed

The harness's test suite (`tests/factory/`, the tests of the code that runs the factory) now writes two setups and the fixture classes' command wrappers once each, in the shared helper module `tests/factory/_cli.py`. Before this change they were copied into each file. Only test code changed: 29 files, 122 lines added and 270 removed.

**B. The two setups.**
- B.1: `git_repo(path)` was added to `_cli.py`, with the body of the `test_instance.py` copy. It makes the directory, runs `git init -q -b main`, makes one empty commit under a fixed identity, and returns the path. The copies in `test_instance.py` and `test_store_setup.py` are deleted. Both files import the name back from `._cli`. That keeps `test_live_store_guard.py`, `test_store_branch.py` and `test_store_migrate.py` working, because they still import `git_repo` from `test_instance.py` until ST-3.
- B.2: `approved_parent(ok, tid, spec)` was added to `_cli.py`. It runs the five calls that take a ticket past the spec gate (the point where a human approves a design) and returns `tid`. `ok(*argv)` is the caller's function that runs one factory command and fails the test on a non-zero exit.
- B.3: the 13 five-call sequences and the 11 empty-repository setups are replaced with calls to these helpers.
  - Class sites pass `self.ok` or `f.ok`.
  - Module sites pass `lambda *a: js(run(store, *a))`. In every one of those files `js` is already `js_ok`, so the exit-0 check is unchanged. The files are `test_redispatch_rows.py` (the `run_env` form), `test_replan.py`, `test_superseded_plan.py`, `test_subtickets.py` (3 sites), `test_build_startup.py` and `test_plan_fields.py`.
  - `test_build_startup.py`'s own `approved_parent` is deleted. Its four callers, and the `store` fixture in `test_plan_fields.py`, now write the request and spec files, create the ticket, and then call the shared helper.
  - The empty-repository sites are `test_coding_standard.py`, `test_turn_economy.py`, `test_writing_standard.py`, `test_harness_lock.py` (`make_target`), `test_resolve_rulings.py`, `test_drive_build.py`, `test_environment_sync.py`, `test_run_isolation.py` and `test_whole_spec_plan.py`.

**C. One `cli`/`ok` pair for the fixture classes.**
- C.1: class `CliStore` was added to `_cli.py`. A subclass sets `self.env`.
  - `cli(*argv)` runs `[BIN, *argv]` with `env=self.env, cwd=REPO`.
  - `ok(*argv)` asserts exit 0, with the argv and stderr as the message, and returns the parsed JSON.
- C.2: the 14 classes subclass `CliStore`, and each deletes its identical `cli` and `ok`. Four classes keep a method of their own:
  - `test_drive.py:Store` keeps its `cli`, which takes the `plays` argument.
  - `test_shepherd.py:Shepherd` keeps its `cli`, which builds the environment on each call.
  - `test_environment_sync.py:Target` keeps both methods, because both take the `venv` flag.
  - `test_results_commit.py:Store` now sets `self.env` once in `__init__`, so it drops its `cli` too. Nothing in that file changes `os.environ` or `self.root` after `__init__`; `grep -n "monkeypatch\|os.environ\["` on it finds nothing.
- Each class still builds its own environment.

**Imports.** The deletions left some imports unused: `json`, `subprocess`, `BIN` and `REPO` in 11 files. They are removed. `test_spec_amend.py` keeps `REPO`, with `# noqa: F401`, because `test_spec_drift.py:26` imports `REPO` from it (`from .test_spec_amend import REPO, V1, V2, Fixture`). ST-3 removes that import.

**Callers checked** (coding standard rule 2). `grep -rn "import.*git_repo\|import.*approved_parent" tests/factory/*.py` lists every importer of the two names. Those that import from `test_instance.py` get `_cli`'s `git_repo` through it. The only callers of the deleted `test_build_startup.approved_parent` were `test_build_startup.py:43,53,65,80` and `test_plan_fields.py:21`. All five are rewritten.

## Acceptance results

Every command ran from the worktree through the fresh-HOME wrapper. The worktree's `.venv` was made by `uv sync --frozen`. The three REGRESSION commands are the spec's text, copied into scratch scripts. `grep -F` confirmed that each script is verbatim in `v2.md`.

| Criterion | Before (base `6ac73f1`) | After (`a7368d0`) | What the result shows |
|---|---|---|---|
| NEW: shared constants and wrappers defined once | `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1` | `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1` | Pass. Only `git_repo` was still copied after ST-1. The one `approved_parent` before was `test_build_startup.py`'s; now it is `_cli.py`'s. |
| NEW: setups written once | `approved-parent sequences: 13` (the 13 sites) and `empty-commit repo setups: 11` (the 11 sites) | `approved-parent sequences: 1 _cli.py:73` and `empty-commit repo setups: 1 _cli.py:63` | Pass. Each setup is now written once, in `_cli.py`. |
| NEW (intermediate): the 14 classes share one pair | all 14 on the first line, 13 on the second, 13 on the third | `not CliStore: none`, `own ok: test_environment_sync.py:Target`, `own cli: test_drive.py:Store test_environment_sync.py:Target test_shepherd.py:Shepherd` | Pass. `test_results_commit.py:Store` no longer has a `cli`, because it builds `self.env` once. |
| REGRESSION: only the duplicate test and its assertions are gone | (not run on base) | `pair: 2`, `removed: 1`, `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`, `added: 0`, `missing: 2`, then two lines starting `missing test_p0_cli.py::test_run_finish_without_output_is_killed:` | Pass. The two pairs are ST-1's merge and this branch. This branch removes no test and no assertion; the one removal is ST-1's. |
| REGRESSION: the suite is shorter | (not run on base) | `pairs: 2; test lines before: 19293, after: 19018, change: -275` | Pass. Across ST-1 and ST-2, the test files are 275 lines shorter. |
| REGRESSION: a suite run in a fresh clone passes and adds nothing to the checkout | (not run on base) | `576 passed in 602.19s (0:10:02)`, then `paths changed: 0` with nothing after it | Pass. The suite passes on a clean checkout of HEAD and writes nothing into it. 576 is the 577 tests the spec counted, less ST-1's removed one. |

Gates, run on commit `a7368d0`, each exactly as written in the input:
- `git diff --check main...HEAD`: no output, exit 0. No whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 611.15s (0:10:11)`. A run on the same tree before the commit also printed `576 passed in 609.10s`.

## Tests added/changed

No test was added. No assertion inside a `test_*` function changed: the assertion-comparison scenario above reports nothing missing apart from ST-1's deletion. Every file this branch touches is listed under the sub-ticket's "Tests to change". Each edit is the replacement that list names:
- the setup swaps in `test_coding_standard.py`, `test_turn_economy.py` and `test_writing_standard.py`, outside their design-block tests at lines 72, 49 and 63;
- `test_harness_lock.py`, `test_store_setup.py`, `test_instance.py`, `test_redispatch_rows.py`, `test_replan.py`, `test_resolve_rulings.py`, `test_superseded_plan.py`, `test_subtickets.py`, `test_build_startup.py`, `test_drive_build.py` and `test_plan_fields.py` (B);
- `test_environment_sync.py`, `test_gate_paths.py`, `test_run_isolation.py`, `test_sibling_tests.py`, `test_spec_amend.py` and `test_whole_spec_plan.py` (B and C);
- `test_critic_approved_changes.py`, `test_empty_output.py`, `test_merge_protected_paths.py`, `test_results_commit.py`, `test_run_scratch.py`, `test_tripwire.py`, `test_drive.py` and `test_shepherd.py` (C).

`test_instance.py` changed only in its import line and the deleted `git_repo`. T-0044's lines are not touched.

## Known gaps and uncertainties

- Some behaviour changes that no test should depend on. The suite passes with all of them.
  - **Commit identity.** The empty commit in `git_repo` is made as `t <t@t>`. Six sites used to make it as `f <f@x>`: `test_store_setup.py`, `test_resolve_rulings.py`, `test_run_isolation.py`, `test_whole_spec_plan.py`, `test_drive_build.py` and `test_environment_sync.py` (through `GIT_ID`). Later commits at those sites keep their own identity.
  - **Existing directory.** `test_harness_lock.py:make_target` used `mkdir(parents=True)`, which raises if the directory exists. `git_repo` uses `exist_ok=True`, so that error no longer happens. Nothing calls `make_target` on an existing path.
  - **Failure messages.** `test_critic_approved_changes.py:Store.ok` put stdout and stderr in its failure message. `CliStore.ok` puts the argv and stderr there, as design C.1 specifies. A failing `ok` call in that file no longer shows stdout.
- `test_build_startup.py` and `test_plan_fields.py` now repeat the same four lines (request file, spec file, `ticket new`, `approved_parent`) at five call sites. The old helper held them once. This follows the spec's Decision that ticket creation stays with the caller. It costs about 15 lines in those two files.
- The `# noqa: F401` on `test_spec_amend.py`'s import line keeps a name another test file imports. It should go when ST-3 removes the cross-test imports.
- factory: markers added: none.
- Lint: the repo has no lint gate. As an extra check, I ran ruff (`--isolated --select E,F,I,W`) on `tests/factory` before and after. It finds no new problem, and three existing import-order findings are gone.

## Out-of-scope observations

- Five-call sequences the spec leaves out are unchanged. `test_resolve_rulings.py:24-41` splits the sequence across the `env` fixture and `approved()`. `test_spec_drift.py` and `test_p0_cli.py` are named out of scope.
- `test_results_commit.py:Store.__init__` and `test_drive.py:Store.drive` still parse JSON by hand instead of calling `ok` or `js`. That is outside this sub-ticket.
- A full suite run takes about 10 minutes on this machine. The spec measured 4 min 43 s, and two runs here were concurrent. A verifier budget built on the spec's figure may be tight.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All three NEW checks and all three REGRESSION checks print what the spec expects, and the gate suite passes on the commit (576 passed).
ESCALATIONS: none
