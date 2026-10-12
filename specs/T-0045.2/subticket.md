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
