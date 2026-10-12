# Plan for T-0045: one shared helper module for the harness tests

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

### ST-2 / Write the two setups once, and give the fixture classes one shared `cli`/`ok` pair
Depends on: ST-1
Parallel-safe: no (it edits `_cli.py` and test files that ST-1 and the last sub-ticket also edit)

Parent: T-0045 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts B and C of design.md.
- B.1 and B.2: add `git_repo(path)` and `approved_parent(ok, tid, spec)` to `_cli.py`.
- B.3: replace the 13 five-call sequences and the 11 empty-repository setups that the third acceptance command lists. Class sites pass `self.ok` or `f.ok`. Module sites pass `lambda *a: js_ok(run(store, *a))`, or the `run_env` form. Delete `test_build_startup.py`'s own `approved_parent`. Its callers there and in `test_plan_fields.py` create the ticket, then call the shared helper. Delete the `git_repo` copies in `test_instance.py` and `test_store_setup.py`. Each file keeps the name `git_repo` by importing it from `._cli`, because other test files import it from `test_instance.py` until the last sub-ticket.
- C.1: add class `CliStore` to `_cli.py`.
- C.2: the 14 classes part C names subclass `CliStore` and delete their identical `cli` and `ok`. A class whose `cli` differs keeps only its `cli`. That is `test_drive.py`'s `Store` and `test_shepherd.py`'s `Shepherd`, and `test_results_commit.py`'s `Store` unless it sets `self.env` once in `__init__`. `test_environment_sync.py`'s `Target` keeps both methods. Each class still builds its own environment.

Acceptance:
- NEW. "The shared constants and wrappers are defined once".
  - WHEN `.venv/bin/python -c 'import ast,pathlib,collections; c=collections.Counter(t.id if isinstance(n,ast.Assign) else n.name for p in pathlib.Path("tests/factory").glob("*.py") for n in ast.parse(p.read_text()).body for t in (n.targets if isinstance(n,ast.Assign) else [n]) if isinstance(t,(ast.Name,ast.FunctionDef))); print(*(f"{k}={c[k]}" for k in ("REPO","BIN","run","js","ticket","git_repo","approved_parent")))'`
  - THEN it prints `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`.
- NEW. "The approved-parent and empty-repository setups are written once".
  - WHEN the parent's command for that scenario is run.
  - THEN each of the two lines reports either `0`, or `1` followed by a single site in `_cli.py`.
- NEW, intermediate check: the 14 classes share one `cli`/`ok` pair.
  - WHEN `.venv/bin/python -c 'import ast,pathlib; W={"test_drive.py":"Store","test_run_isolation.py":"Store","test_run_scratch.py":"Store","test_empty_output.py":"Store","test_results_commit.py":"Store","test_critic_approved_changes.py":"Store","test_gate_paths.py":"Target","test_environment_sync.py":"Target","test_merge_protected_paths.py":"Gate","test_shepherd.py":"Shepherd","test_sibling_tests.py":"Fixture","test_spec_amend.py":"Fixture","test_whole_spec_plan.py":"Parent","test_tripwire.py":"Inst"}; C={(p.name,c.name):c for p in sorted(pathlib.Path("tests/factory").glob("test_*.py")) for c in ast.walk(ast.parse(p.read_text())) if isinstance(c,ast.ClassDef)}; m=lambda c,x: any(isinstance(n,ast.FunctionDef) and n.name==x for n in c.body); print("not CliStore:", *[f"{f}:{k}" for f,k in W.items() if not any(ast.unparse(b).endswith("CliStore") for b in C[(f,k)].bases)] or ["none"]); print("own ok:", *[f"{f}:{k}" for (f,k),c in sorted(C.items()) if m(c,"ok")] or ["none"]); print("own cli:", *[f"{f}:{k}" for (f,k),c in sorted(C.items()) if m(c,"cli")] or ["none"])'`
  - THEN it prints `not CliStore: none`, then `own ok: test_environment_sync.py:Target`. The third line starts `own cli:` and lists `test_drive.py:Store`, `test_environment_sync.py:Target` and `test_shepherd.py:Shepherd`, plus `test_results_commit.py:Store` if that class still builds its environment on every call, and nothing else. Today it prints all 14 classes on the first line, 13 on the second and 13 on the third.
- REGRESSION. "Only the duplicate test and its assertions are gone". Its pairs are now ST-1's merge and this branch.
  - WHEN the parent's command for that scenario is run.
  - THEN `pair:` is at least 2. `removed: 1` is followed by exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`. It prints `added: 0`. It prints `missing: 2`, followed by two lines that both start `missing test_p0_cli.py::test_run_finish_without_output_is_killed:`.
- REGRESSION. "The suite is shorter".
  - WHEN the parent's command for that scenario is run.
  - THEN `pairs` is at least 2 and `change` is negative. Report the line.
- REGRESSION. "A suite run in a fresh clone passes and adds nothing to the checkout". This also checks that the harness suite passes.
  - WHEN the parent's command for that scenario is run.
  - THEN the first line reports a number of passed tests and no `failed` or `error`. The next line is `paths changed: 0`, with nothing after it.

Interim tests: none

Tests to change:
- `tests/factory/test_coding_standard.py`: its empty-repository setup becomes a `git_repo` call. Line 72 is untouched.
- `tests/factory/test_turn_economy.py`: its empty-repository setup in the `run_prompts` fixture becomes a `git_repo` call. Line 49 is untouched.
- `tests/factory/test_writing_standard.py`: its empty-repository setup in the `system_prompt` fixture becomes a `git_repo` call. Line 63 is untouched.
- `tests/factory/test_harness_lock.py`: its empty-repository setup becomes a `git_repo` call.
- `tests/factory/test_store_setup.py`: its `git_repo` copy goes, imported from `._cli`.
- `tests/factory/test_redispatch_rows.py`: the five-call sequence becomes an `approved_parent` call.
- `tests/factory/test_replan.py`: the five-call sequence becomes an `approved_parent` call.
- `tests/factory/test_resolve_rulings.py`: its empty-repository setup becomes a `git_repo` call.
- `tests/factory/test_superseded_plan.py`: the five-call sequence becomes an `approved_parent` call.
- `tests/factory/test_environment_sync.py`: both setups replaced. `Target` subclasses `CliStore` and keeps its own `cli` and `ok`.
- `tests/factory/test_gate_paths.py`: the five-call sequence is replaced, and `Target` subclasses `CliStore`.
- `tests/factory/test_run_isolation.py`: both setups replaced, and `Store` subclasses `CliStore`.
- `tests/factory/test_instance.py`: its `git_repo` copy moves to `_cli.py` and is imported back.
- `tests/factory/test_subtickets.py`: its three five-call sequences become `approved_parent` calls.
- `tests/factory/test_sibling_tests.py`: the five-call sequence is replaced, and `Fixture` subclasses `CliStore`.
- `tests/factory/test_spec_amend.py`: the five-call sequence is replaced, and `Fixture` subclasses `CliStore`.
- `tests/factory/test_whole_spec_plan.py`: its empty-repository setup is replaced, and `Parent` subclasses `CliStore`.
- `tests/factory/test_build_startup.py`: its own `approved_parent` goes, and its callers create the ticket and then call the shared one.
- `tests/factory/test_drive_build.py`: both setups replaced.
- `tests/factory/test_plan_fields.py`: imports `approved_parent` from `._cli`, and its callers create the ticket first.
- `tests/factory/test_critic_approved_changes.py`: `Store` subclasses `CliStore` and loses its `ok`.
- `tests/factory/test_empty_output.py`: `Store` subclasses `CliStore`.
- `tests/factory/test_merge_protected_paths.py`: `Gate` subclasses `CliStore`.
- `tests/factory/test_results_commit.py`: `Store` subclasses `CliStore`.
- `tests/factory/test_run_scratch.py`: `Store` subclasses `CliStore`.
- `tests/factory/test_tripwire.py`: `Inst` subclasses `CliStore`.
- `tests/factory/test_drive.py`: `Store` subclasses `CliStore`, keeps its own `cli` and inherits `ok`.
- `tests/factory/test_shepherd.py`: `Shepherd` subclasses `CliStore`, keeps its own `cli` and inherits `ok`.

Protected paths: none

Out of scope:
- any sequence that asserts a step, uses `spec add --from-run`, or puts other work between the steps, such as `test_spec_drift.py:83-90` and `test_p0_cli.py:182-186`;
- the request's `plan` argument for `approved_parent`;
- `ticket`, `events` and `runs` methods on the classes, and the other repeated helpers the parent leaves out (`git` variants, `files`, `events`, `finish`, `start`);
- moving any class or fixture out of its test file, and any import from one test file into another;
- everything under the parent's Out of scope.

---

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

Coverage map:
- No test file imports from another test file → ST-3
- The shared constants and wrappers are defined once → ST-2 (partly checked early in ST-1; REGRESSION in ST-3)
- The approved-parent and empty-repository setups are written once → ST-2 (REGRESSION in ST-3)
- Only the duplicate test and its assertions are gone → ST-1 (REGRESSION in ST-2 and ST-3)
- The suite is shorter → ST-1 (REGRESSION in ST-2 and ST-3)
- A suite run in a fresh clone passes and adds nothing to the checkout → ST-1 (REGRESSION in ST-2 and ST-3)

STATUS: PLANNED
CONFIDENCE: high. The spec fixes the order and contents of each part. I re-ran the static checks on `main` at `2b9baf5`, and they match the spec's baseline. I did not re-run the five-minute suite or the fresh-clone check, so the baseline counts of 577 passed and 13 changed paths come from the spec's own run.
ESCALATIONS: none
