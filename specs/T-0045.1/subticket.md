### ST-1 / Add the shared test module `_cli.py`, stop the suite writing bytecode, and remove the duplicate test
Depends on: none
Parallel-safe: no (the next two sub-tickets build on `_cli.py` and edit the same test files)

Parent: T-0045 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A, items 1 to 4 of design.md:
- add `tests/factory/_cli.py` with `REPO`, `BIN`, `STRIP`, `CLEAN_CLI`, `cli`, `run`, `run_env`, `js`, `js_ok`, `ticket` (with its `tid="T-0001"` default) and `tree`;
- in each test file that has its own copy of one of these at module level, delete the copy and import the name from `._cli`. Import `js_ok as js` where the file's copy asserted exit 0, and `run_env as run` in the two files that pass an environment dict. Leave the `cli` functions of `test_store_setup.py` and `test_harness_lock.py` as they are;
- add the bytecode guard to `tests/factory/conftest.py`: `os.environ["PYTHONDONTWRITEBYTECODE"] = "1"` and `sys.dont_write_bytecode = True`, with one comment line saying why;
- delete `test_run_finish_without_output_is_killed` from `test_p0_cli.py`.

Acceptance:
- NEW. "Only the duplicate test and its assertions are gone".
  - WHEN the parent's command for that scenario is run on this branch. It compares `git merge-base HEAD main` with HEAD.
  - THEN `pair:` is at least 1. `removed: 1` is followed by exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`. It prints `added: 0`. It prints `missing: 2`, followed by two lines that both start `missing test_p0_cli.py::test_run_finish_without_output_is_killed:`.
- NEW. "The suite is shorter".
  - WHEN the parent's command for that scenario is run.
  - THEN `pairs` is at least 1 and `change` is negative. Report the line.
- NEW. "A suite run in a fresh clone passes and adds nothing to the checkout". This also checks that the harness suite passes.
  - WHEN the parent's command for that scenario is run.
  - THEN the first line reports a number of passed tests, 576 if no other ticket has added tests since `2b9baf5`, and no `failed` or `error`. The next line is `paths changed: 0`, with nothing after it.
- NEW, intermediate check: the shared constants and wrappers are defined once, except the two setups. Those are the next sub-ticket's.
  - WHEN the parent's command for "The shared constants and wrappers are defined once" is run.
  - THEN it prints `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=2 approved_parent=1`.

Interim tests: none

Tests to change:
- `tests/factory/conftest.py`: gains the bytecode guard (parent Decision: the guard goes in conftest).
- `tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`: deleted (parent Decision: the removed test). The rest of the file: its helper copies replaced by imports.
- `tests/factory/test_capability_index.py`: helper copies replaced by imports.
- `tests/factory/test_decision_log.py`: module-level helper copies only. `_design_block` at line 248 is untouched.
- `tests/factory/test_request_frontmatter.py`: helper copies replaced by imports.
- `tests/factory/test_spec_store.py`: helper copies replaced by imports.
- `tests/factory/test_coding_standard.py`: module-level helper copies only. Line 72 is untouched.
- `tests/factory/test_turn_economy.py`: module-level helper copies only. Line 49 is untouched.
- `tests/factory/test_writing_standard.py`: module-level helper copies only. Line 63 is untouched.
- `tests/factory/test_harness_lock.py`: helper copies replaced by imports. Its own `cli` stays.
- `tests/factory/test_store_setup.py`: helper copies replaced by imports. Its own `cli` and its `git_repo` stay until the next sub-ticket.
- `tests/factory/test_redispatch_rows.py`: helper copies replaced by imports (`run_env as run`).
- `tests/factory/test_replan.py`: helper copies replaced by imports.
- `tests/factory/test_resolve_rulings.py`: helper copies replaced by imports (`run_env as run`).
- `tests/factory/test_superseded_plan.py`: helper copies replaced by imports.
- `tests/factory/test_critic_approved_changes.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_empty_output.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_merge_protected_paths.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_results_commit.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_run_scratch.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_tripwire.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_environment_sync.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_gate_paths.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_run_isolation.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_drive.py`: `REPO` and `BIN` replaced by imports. `test_drive_build.py` still imports both names from it.
- `tests/factory/test_shepherd.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_instance.py`: its `STRIP`, `CLEAN_CLI`, `cli`, `js`, `tree`, `REPO` and `BIN` move to `_cli.py` and are imported back. The assertions at lines 109 and 354 are untouched.
- `tests/factory/test_subtickets.py`: helper copies replaced by imports (`js_ok as js`).
- `tests/factory/test_sibling_tests.py`: `REPO` and `BIN` replaced by imports.
- `tests/factory/test_spec_amend.py`: `REPO` and `BIN` replaced by imports. `test_spec_drift.py` still imports `REPO` from it.
- `tests/factory/test_whole_spec_plan.py`: `REPO` and `BIN` replaced by imports.

Protected paths: none

Out of scope:
- `git_repo`, `approved_parent`, the five-call sequences, the empty-repository setups, and the classes' `cli` and `ok` methods;
- any import from one test file into another, and `_fixtures.py`;
- removing the per-call `PYTHONDONTWRITEBYTECODE` settings, which still work;
- everything under the parent's Out of scope.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) divides the change into four lettered parts that must run in order: A, B, C, D (design.md, "Proposed change"). This plan makes three sub-tickets from them. ST-1 is part A, ST-2 is parts B and C together, and ST-3 is part D. Each one runs alone, after the one before it.

Why B and C are one sub-ticket: the spec already says they cannot run in parallel. Six test files are in both parts (`test_environment_sync.py`, `test_gate_paths.py`, `test_run_isolation.py`, `test_sibling_tests.py`, `test_spec_amend.py`, `test_whole_spec_plan.py`), and both parts add code to `_cli.py`. Separately they are about 170 and 110 changed lines, so together they are about the size of A. Both are mechanical swaps of a copied helper for a shared one, and both are caught by the same check: the suite passes, and no assertion is missing. Keeping them apart would cost one more implementer, reviewer and verifier cycle, and the verifier's checks include two full suite runs of about five minutes each. It would not make either part easier to review or roll back.

Why D is not split: the spec allows cutting D in two (the `test_shepherd.py` fixtures, then the rest). Both halves would write `_fixtures.py` and rewrite the import lines of the same importing files, such as `test_whole_spec_plan.py`, which imports from both `test_shepherd.py` and `test_parent_close_reuse.py`. The cross-test import scenario passes only after both halves. D is a move with no changed bodies, and it reads well with `git diff --color-moved`. So it stays one sub-ticket.

What I checked on this checkout. `main` is at `2b9baf5`. That is the spec's base `0ba4e4f` plus T-0044.1's merge. T-0044.1 changed only lines 109 and 354 of `tests/factory/test_instance.py`, inside test functions, as the spec's Risk section expects. All commands ran through the fresh-HOME wrapper.
- `tests/factory/_cli.py` and `tests/factory/_fixtures.py` do not exist. The suite is 47 files and 9,710 lines.
- The three static scenarios print what verification.md records as today's output: `cross-test imports: 27` (the same 27 sites), `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`, `approved-parent sequences: 13` and `empty-commit repo setups: 11` (the same sites).
- The line-count scenario prints `pairs: 0; test lines before: 0, after: 0, change: 0`, because no `Merge factory/T-0045.` commit exists yet.
- Every copy of `REPO`, `BIN`, `run`, `js` and `ticket` is in a file the parent marks A. I compared the bodies with their docstrings left out:
  - `tree` and `git_repo` have no behavioural difference between copies;
  - `run` comes in the three forms the spec names (plain, with `stdin`, and with an environment dict);
  - `js` either asserts exit 0 or does not. The copies in `test_instance.py` and `test_p0_cli.py` do not assert. The copy in `test_subtickets.py` does.
- Today 13 of the 14 classes that part C names have their own `ok`, and 13 have their own `cli`. The two exceptions: `test_results_commit.py`'s `Store` has no `ok`, and `test_critic_approved_changes.py`'s `Store` has no `cli`.
- The harness counts only files named `test_*` as tests (`factory/cli.py`, `TEST_FILE_RE`). So `_cli.py`, `_fixtures.py` and `conftest.py` are helper files, and a later sub-ticket that edits them lists nothing under "added by".

Two things every sub-ticket must keep:
- Until ST-3 lands, files that import a helper from another test file must keep working. So when ST-1 removes a file's copy of a helper, that file imports the name back from `._cli`. An example is `test_instance.py`'s `cli`, `js`, `tree` and `git_repo`, which `test_live_store_guard.py`, `test_store_branch.py`, `test_store_migrate.py`, `test_stats.py` and `test_drive_guard.py` import from it today. The suite run in each sub-ticket's Acceptance catches a broken import.
- The design-block helpers named in the parent's Out of scope (`test_writing_standard.py:63`, `test_coding_standard.py:72`, `test_turn_economy.py:49`, `test_decision_log.py:248`) stay byte for byte. So do T-0044's two lines in `test_instance.py`.

Running the checks: run every command below from `~/dev/spec-factory` through the running-code wrapper. The long commands are in the parent spec, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`, under each scenario's name. Run them exactly as written there.

---
