### ST-3 / Move every helper that test files import from each other into `_fixtures.py`
Depends on: ST-1, ST-2
Parallel-safe: no (it rewrites the imports of files the earlier two sub-tickets edit, and it moves classes that ST-2 changes)

Parent: T-0045 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part D, items 1 and 2 of design.md:
- add `tests/factory/_fixtures.py`. Move into it every name in design.md's D table, with the body unchanged. Rewrite only its imports to `._cli`. Keep one copy of `state`. No test function moves;
- the files the names came from import them back from `._fixtures`;
- every file that imports from another test file imports from `._fixtures` or `._cli` instead. Where a name came from a file's `js`, import the same form that file imported after ST-1. `test_subtickets.py`'s `js` asserts exit 0, so its importers take `js_ok as js`. The `js` of `test_instance.py` and of `test_p0_cli.py` does not assert, so their importers take `js`. Keep aliases such as `cli as factory_cli`;
- the two `f = test_spec_amend.f` lines and their `from . import test_spec_amend` imports become imports of `f`. Pytest fixtures keep their `# noqa: F401` imports.

Acceptance:
- NEW. "No test file imports from another test file".
  - WHEN `.venv/bin/python -c 'import ast,pathlib; bad=[f"{p.name}:{n.lineno}" for p in sorted(pathlib.Path("tests/factory").glob("*.py")) for n in ast.walk(ast.parse(p.read_text())) if (isinstance(n,ast.ImportFrom) and (any(s.startswith("test_") for s in (n.module or "").split(".")) or any(a.name.startswith("test_") for a in n.names))) or (isinstance(n,ast.Import) and any(s.startswith("test_") for a in n.names for s in a.name.split(".")))]; print(f"cross-test imports: {len(bad)}", *bad)'`
  - THEN it prints `cross-test imports: 0`.
- REGRESSION. "The shared constants and wrappers are defined once".
  - WHEN the command in ST-2's Acceptance for that scenario is run.
  - THEN it prints `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`.
- REGRESSION. "The approved-parent and empty-repository setups are written once".
  - WHEN the parent's command for that scenario is run.
  - THEN each of the two lines reports either `0`, or `1` followed by a single site in `_cli.py`.
- REGRESSION. "Only the duplicate test and its assertions are gone". Its pairs are now ST-1's and ST-2's merges and this branch. A test function that moved, or a test file that no longer collects, shows here.
  - WHEN the parent's command for that scenario is run.
  - THEN `pair:` is at least 3. `removed: 1` is followed by exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`. It prints `added: 0`. It prints `missing: 2`, followed by two lines that both start `missing test_p0_cli.py::test_run_finish_without_output_is_killed:`.
- REGRESSION. "The suite is shorter".
  - WHEN the parent's command for that scenario is run.
  - THEN `pairs` is at least 3 and `change` is negative. Report the line. This sub-ticket can add a few lines of its own, because it adds import lines. The THEN applies to the sum.
- REGRESSION. "A suite run in a fresh clone passes and adds nothing to the checkout". This also checks that the harness suite passes.
  - WHEN the parent's command for that scenario is run.
  - THEN the first line reports a number of passed tests and no `failed` or `error`. The next line is `paths changed: 0`, with nothing after it.

The class check in ST-2's Acceptance does not apply here. It looks for the classes in their original test files, and this sub-ticket moves some of them to `_fixtures.py`.

Interim tests: none

Tests to change:
- `tests/factory/test_p0_cli.py`: `REPO`, `js` and `run`, which `test_role_inputs.py` imports from it, now come from `._cli` there.
- `tests/factory/test_instance.py`: names other files imported from it now come from `._cli`. Its own imports may shrink to what it uses.
- `tests/factory/test_subtickets.py`: `PLAN_LETTERS` moves to `_fixtures.py` and is imported back.
- `tests/factory/test_sibling_tests.py`: `BUILD_DRIVER` moves and is imported back.
- `tests/factory/test_spec_amend.py`: `V1`, `V2`, `Fixture` and the fixture `f` move and are imported back.
- `tests/factory/test_whole_spec_plan.py`: imports from `._fixtures` instead of two test files.
- `tests/factory/test_drive.py`: `STANDIN` and `Store` move and are imported back.
- `tests/factory/test_shepherd.py`: `Shepherd` and `built_to_implementer` move and are imported back.
- `tests/factory/test_build_startup.py`: `ticket_files` moves and is imported back. Its import from `test_subtickets.py` is rewritten.
- `tests/factory/test_drive_build.py`: `BuildStore` moves and is imported back. Its import from `test_drive.py` is rewritten.
- `tests/factory/test_plan_fields.py`: imports rewritten.
- `tests/factory/test_drift_siblings.py`: imports rewritten, including its `f`.
- `tests/factory/test_drive_guard.py`: imports rewritten.
- `tests/factory/test_killed_checker.py`: imports rewritten.
- `tests/factory/test_live_store_guard.py`: the fixture `target`, plus `state`, `start_triage` and `snapshot`, move and are imported back. Its import from `test_instance.py` is rewritten.
- `tests/factory/test_parent_close_reuse.py`: `_build` and `_parent_verifier_runs` move and are imported back.
- `tests/factory/test_role_inputs.py`: imports rewritten.
- `tests/factory/test_spec_drift.py`: `land`, `head`, `start`, `implementer_runs`, `drifted` and `started` move and are imported back. Its imports, including its `f`, are rewritten.
- `tests/factory/test_stats.py`: imports rewritten.
- `tests/factory/test_store_branch.py`: `BRANCH`, `IDENT`, `git`, `exclude` and `request` move and are imported back. Its `state` is dropped in favour of the one shared copy.
- `tests/factory/test_store_migrate.py`: imports only. Its in-process CLI code is untouched.

Protected paths: none

Out of scope:
- any change to a moved body other than its imports;
- moving any test function;
- `clean_harness_cli.py` and the in-process CLI code in `test_store_migrate.py`;
- everything under the parent's Out of scope.

---

Notes:
- The three sub-tickets do not change what the parent asks for. The only planning choice is putting parts B and C in one sub-ticket, for the reasons given at the top.
- Every scenario is cumulative over this ticket's own merges. Each sub-ticket's verifier therefore also re-checks what the earlier ones did. Nothing in the comparisons depends on T-0044 or on later tickets in the de-bloat sweep.
- No sub-ticket changes a command, state, stop or path, so README is not touched (parent Out of scope).
- Operator steps after the parent closes are the parent's: remove `core/b.py` and, if wanted, `factory/__pycache__`.

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
