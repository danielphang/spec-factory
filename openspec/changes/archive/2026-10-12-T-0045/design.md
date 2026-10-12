## Proposed change

This change is too large for one reviewable change, so it is marked NEEDS-SPLIT. Estimated sizes: A is about 260 changed lines, B about 170, C about 110, and D about 500 moved lines plus about 40 import lines. D's diff is about 1,000 lines, but it is move-only and reads with `git diff --color-moved`. The planner may cut D in two: the fixtures from `test_shepherd.py`, about 215 lines, and the rest, about 300. Every part touches files the others touch, so they run in order, A, B, C, D, and none is parallel-safe with another.

A. **The shared module, the bytecode guard and the duplicate test.**
1. Add `tests/factory/_cli.py`. Its leading underscore keeps pytest from collecting it. It contains:
   - `REPO` and `BIN`, as today.
   - `STRIP`, `CLEAN_CLI` and `cli(cwd, *argv, **extra)`, moved from `test_instance.py:21-33` unchanged. They keep the launcher split: `init` and `paths` run `bin/factory`; every other command runs `clean_harness_cli.py`.
   - `run(store, *argv, stdin=None)`, as `test_p0_cli.py:20-22`.
   - `run_env(env, *argv)`, as `test_redispatch_rows.py:26-28`.
   - `js(cp)`, which parses the last stdout line. `js_ok(cp)`, which asserts `cp.returncode == 0` with stderr as the message and then parses.
   - `ticket(store, tid="T-0001")`. The default lets `test_decision_log.py`'s `ticket(store)` calls stay as written.
   - `tree(path)`, as `test_instance.py:48-49`.
2. Each test file that defines any of these at module level deletes its copy and imports from `._cli`. A file whose copy of `js` asserted exit 0 imports `js_ok as js`. The others import `js`. The two env-dict files import `run_env as run`. `test_instance.py` imports back what it moved. The `cli` functions of `test_store_setup.py` and `test_harness_lock.py` stay: one has no launcher split, and the other takes a harness argument.
3. In `tests/factory/conftest.py`, add `os.environ["PYTHONDONTWRITEBYTECODE"] = "1"` and `sys.dont_write_bytecode = True`, with one comment line saying why.
4. Delete `test_run_finish_without_output_is_killed` from `test_p0_cli.py` (lines 118-124).

B. **The two setups.** Depends on A.
1. Add `git_repo(path)` to `_cli.py`, with the body of `test_instance.py:40-45`: make the directory, `git init -q -b main`, then an empty commit under a fixed identity. It returns the path.
2. Add `approved_parent(ok, tid, spec)` to `_cli.py`. `ok(*argv)` runs one factory command and fails the test on a non-zero exit. The helper runs the transition to `ready-for-spec-writer`, `spec add <tid> --file <spec>`, the transition to `ready-for-critic --round spec:init`, the transition to `awaiting-spec-gate`, and `approve-spec <tid>`, then returns `tid`.
3. Replace the 13 five-call sequences and the 11 empty-repository setups that the third acceptance command lists. Class sites pass `self.ok` or `f.ok`. Module sites pass `lambda *a: js_ok(run(store, *a))`, or the `run_env` form. `test_build_startup.py`'s own `approved_parent` is deleted. Its callers there and in `test_plan_fields.py` create the ticket and then call the shared helper. The `git_repo` copies in `test_instance.py` and `test_store_setup.py` go.

C. **One `cli`/`ok` pair for the fixture classes.** Depends on A.
1. Add class `CliStore` to `_cli.py`. A subclass sets `self.env`. `cli(*argv)` runs `[BIN, *argv]` with `capture_output=True, text=True, env=self.env, cwd=REPO`. `ok(*argv)` calls `self.cli(*argv)`, asserts exit 0 with the argv and stderr in the message, and returns the parsed JSON.
2. These classes subclass it and delete their identical `cli` and `ok`:
   - `Store` in `test_drive.py`, `test_run_isolation.py`, `test_run_scratch.py`, `test_empty_output.py`, `test_results_commit.py` and `test_critic_approved_changes.py`;
   - `Target` in `test_gate_paths.py` and `test_environment_sync.py`;
   - `Gate` in `test_merge_protected_paths.py`;
   - `Shepherd` in `test_shepherd.py`;
   - `Fixture` in `test_sibling_tests.py` and `test_spec_amend.py`;
   - `Parent` in `test_whole_spec_plan.py`;
   - `Inst` in `test_tripwire.py`.

   A class whose `cli` differs keeps its own `cli` and inherits `ok`: `test_drive.py`'s plays, `test_shepherd.py`'s per-call environment, and `test_results_commit.py`'s per-call environment, unless that class sets `self.env` once in `__init__`. `test_environment_sync.py` keeps both of its methods, because both take the venv flag. Each class keeps building its own environment.

D. **No test file imports from another.** Depends on A, B and C.
1. Add `tests/factory/_fixtures.py`. Every name a test file imports from another test file today moves into it. Each body moves unchanged; only its imports are rewritten to `._cli`. No test function moves. The names, grouped by the file they come from:

   | From | Names |
   |---|---|
   | `test_subtickets.py` | `PLAN_LETTERS` |
   | `test_build_startup.py` | `ticket_files` |
   | `test_sibling_tests.py` | `BUILD_DRIVER` |
   | `test_spec_amend.py` | `V1`, `V2`, `Fixture` and the pytest fixture `f` |
   | `test_spec_drift.py` | `land`, `head`, `start`, `implementer_runs`, `drifted`, `started` |
   | `test_drive.py` | `STANDIN`, `Store` |
   | `test_drive_build.py` | `BuildStore` |
   | `test_live_store_guard.py` | the pytest fixture `target`, plus `state`, `start_triage`, `snapshot` |
   | `test_store_branch.py` | `BRANCH`, `IDENT`, `git`, `exclude`, `request`; its `state` is identical to the live-store one, so one copy is kept |
   | `test_shepherd.py` | `Shepherd`, `built_to_implementer` |
   | `test_parent_close_reuse.py` | `_build`, `_parent_verifier_runs` |
2. The files the names came from import them back from `._fixtures`. Every file that imported them from a test file imports them from `._fixtures` or `._cli` instead. The two `f = test_spec_amend.f` lines become imports of `f`. Pytest fixtures keep their `# noqa: F401` imports, as today.

## Tests to change

Every file below is edited only by replacing its helpers with imports or calls to the shared ones; no assertion in a test function changes, except the one deletion in A.4. The letters name the parts that edit each file.
- `tests/factory/conftest.py` (A): gains the bytecode guard (Decision: guard in conftest).
- `tests/factory/test_p0_cli.py` (A, D): loses `test_run_finish_without_output_is_killed` (Decision: the removed test) and its copied helpers.
- `tests/factory/test_capability_index.py` (A)
- `tests/factory/test_decision_log.py` (A): module-level helpers only; the design-block test at line 248 is untouched.
- `tests/factory/test_request_frontmatter.py` (A)
- `tests/factory/test_spec_store.py` (A)
- `tests/factory/test_coding_standard.py` (A, B): module-level helpers only; the test at line 72 is untouched.
- `tests/factory/test_turn_economy.py` (A, B): module-level helpers only; the test at line 49 is untouched.
- `tests/factory/test_writing_standard.py` (A, B): module-level helpers only; the test at line 63 is untouched.
- `tests/factory/test_harness_lock.py` (A, B)
- `tests/factory/test_store_setup.py` (A, B)
- `tests/factory/test_redispatch_rows.py` (A, B)
- `tests/factory/test_replan.py` (A, B)
- `tests/factory/test_resolve_rulings.py` (A, B)
- `tests/factory/test_superseded_plan.py` (A, B)
- `tests/factory/test_critic_approved_changes.py` (A, C)
- `tests/factory/test_empty_output.py` (A, C)
- `tests/factory/test_merge_protected_paths.py` (A, C)
- `tests/factory/test_results_commit.py` (A, C)
- `tests/factory/test_run_scratch.py` (A, C)
- `tests/factory/test_tripwire.py` (A, C)
- `tests/factory/test_environment_sync.py` (A, B, C)
- `tests/factory/test_gate_paths.py` (A, B, C)
- `tests/factory/test_run_isolation.py` (A, B, C)
- `tests/factory/test_drive.py` (A, C, D)
- `tests/factory/test_shepherd.py` (A, C, D)
- `tests/factory/test_instance.py` (A, B, D): module-level helpers only; the assertions at lines 109 and 354, which T-0044 edits, are untouched.
- `tests/factory/test_subtickets.py` (A, B, D)
- `tests/factory/test_sibling_tests.py` (A, B, C, D)
- `tests/factory/test_spec_amend.py` (A, B, C, D)
- `tests/factory/test_whole_spec_plan.py` (A, B, C, D)
- `tests/factory/test_build_startup.py` (B, D)
- `tests/factory/test_drive_build.py` (B, D)
- `tests/factory/test_plan_fields.py` (B, D)
- `tests/factory/test_drift_siblings.py` (D)
- `tests/factory/test_drive_guard.py` (D)
- `tests/factory/test_killed_checker.py` (D)
- `tests/factory/test_live_store_guard.py` (D)
- `tests/factory/test_parent_close_reuse.py` (D)
- `tests/factory/test_role_inputs.py` (D)
- `tests/factory/test_spec_drift.py` (D)
- `tests/factory/test_stats.py` (D)
- `tests/factory/test_store_branch.py` (D)
- `tests/factory/test_store_migrate.py` (D): imports only; its in-process CLI code is untouched.

