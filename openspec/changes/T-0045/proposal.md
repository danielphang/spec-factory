## Problem

The harness's own test suite has no shared helper code, so every implementer who edits a test pays twice: once to find every copy of a helper, and again when an edit to one test file breaks a different one. The harness is the code that runs the factory. Its suite, `tests/factory/`, is 47 Python files, 9,710 lines and 577 passing tests. Each file writes its own copy of the same small helpers:
- where the repository is, and where the factory's command-line entry point is;
- a function that calls that entry point;
- a function that reads its JSON reply;
- the five calls that take a ticket past the spec gate, the point where a human approves a design;
- the two git calls that make an empty repository.

When a file needed a helper that only another file had, it imported it from that other test file. Fourteen test files do this. Every later ticket that touches tests pays this cost.

There are two smaller problems. First, a suite run leaves Python bytecode files (`.pyc`) in the harness package directory. The rest of the suite deliberately avoids writing bytecode. Second, one test checks a strict subset of what another test checks.

The change is to test code only. The harness's behaviour, commands and documents stay as they are.

## Evidence

All runs were on `~/dev/spec-factory` at `0ba4e4f`, the head of `main`. That commit changes only `dev/` after `927bc53`, the commit the request measured. Every command ran through the run's fresh-HOME wrapper. Exception: in round 1, a first draft of the collection check ran once without the wrapper, and the same command then ran again under the wrapper, which gave the output quoted below.

**Baseline suite, and what a run writes into the checkout.** The last acceptance command makes a fresh clone of HEAD, lists every path, runs the suite, and lists the paths again. pytest's own cache of the test modules is left out of both lists. Output:
```
577 passed in 283.89s (0:04:43)
paths changed: 13
	./factory/__pycache__
	./factory/__pycache__/__init__.cpython-312.pyc
	... cli, compose, cost, drive, gitops, instance, specstore, status, store, subtickets, tripwire
```
This means the suite passes, and a run in a clean clone adds 12 bytecode files to the harness package `factory/`. The request named only one of them, `drive.cpython-312.pyc`. A second run in the same clone at 577 passed, with only `os.environ["PYTHONDONTWRITEBYTECODE"] = "1"` added to `tests/factory/conftest.py`, still left `cost.cpython-312.pyc` and `subtickets.cpython-312.pyc`. A third run that also set `sys.dont_write_bytecode = True` there left nothing under `factory/`. Only `tests/factory/__pycache__/__init__…pyc` and `conftest…pyc` appeared, which pytest writes before `conftest.py` runs. All three runs: 577 passed.

**Imports from other test files.** The first acceptance command walks every file's import statements. It printed `cross-test imports: 27`, from 14 files: test_build_startup, test_drift_siblings, test_drive_build, test_drive_guard, test_killed_checker, test_live_store_guard, test_parent_close_reuse, test_plan_fields, test_role_inputs, test_spec_drift, test_stats, test_store_branch, test_store_migrate and test_whole_spec_plan. That is 14 files, not the request's twelve. Two of the imports take a whole module (`from . import test_spec_amend`) to reuse its pytest fixture `f`: `test_drift_siblings.py:23`, `test_spec_drift.py:28`.

**Copies of each helper.** The second command counts module-level definitions. It printed `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`. So 30 files define the repository constant and 29 the entry-point constant. 10 define the call wrapper, 11 the JSON reader and 6 the ticket reader. These match the request. The 11 JSON readers differ in one way: 6 assert that the command exited 0 and 5 do not.

**Repeated setups.** The third command finds the exact five-call sequence: `ready-for-spec-writer`, `spec add --file`, `ready-for-critic --round spec:init`, `awaiting-spec-gate`, and `approve-spec` with its result neither assigned nor asserted. It printed `approved-parent sequences: 13`, at test_build_startup:22, test_drive_build:65, test_environment_sync:58, test_gate_paths:56, test_redispatch_rows:45, test_replan:58, test_run_isolation:62, test_sibling_tests:114, test_spec_amend:112, and test_subtickets:88, :164 and :198, test_superseded_plan:61. The request counted 21 files. Its looser count includes sites that assert a step or change the order, such as `test_spec_drift.py:83-90`, which lands a commit between two steps, and `test_p0_cli.py:182-186`, which asserts the approval. Those sites test the sequence and stay as they are. The same command printed `empty-commit repo setups: 11`, at test_coding_standard:41, test_drive_build:70, test_environment_sync:50, test_harness_lock:74, test_instance:42, test_resolve_rulings:41, test_run_isolation:72, test_store_setup:48, test_turn_economy:93, test_whole_spec_plan:65 and test_writing_standard:36. Each runs `git init -b main` and then an empty commit. The request said about 20.

**The bin/factory wrapper inside classes.** There are 13 classes, each with a `cli` and an `ok` method; `ok` runs `cli`, asserts exit 0 and parses the JSON (`grep -n "^    def ok(" tests/factory/test_*.py`). A 14th, `test_results_commit.py:25`, has only `cli`. In 10 of them `cli` is the same single line. The others differ:
- `test_drive.py:72` passes the stand-in plays to the fake `claude`;
- `test_environment_sync.py:69` takes a venv flag;
- `test_shepherd.py:625` builds its environment on every call;
- `test_results_commit.py:35` builds its environment on every call;
- `test_critic_approved_changes.py:42` has only `ok`.

**The duplicate test.** `test_p0_cli.py:118` `test_run_finish_without_output_is_killed` starts a triage run, composes it, then finishes it with `--status-override KILLED`. It asserts exit 0, `status == "KILLED"` in the reply, and `KILLED` in the run's `meta.yaml`, in two assert statements (lines 123-124). `test_empty_output.py:61` `test_status_override_killed_still_records_killed` does the same on the same kind of run, set up by its `Store` (`test_empty_output.py:22-33`). Its `ok` asserts exit 0. It asserts the same two statuses and also checks the `run.killed` event. So the first test checks a strict subset of the second, and its name is stale: a finish with no output is now EMPTY-OUTPUT.

**The stray directory.** `~/dev/spec-factory/core/b.py/` is an empty, untracked directory. `stat` gives it a birth time of 2026-10-07 07:58:46 -0700. That falls inside the T-0033 spec writer's run, run-0311, which ran from 07:54:34 to 08:14:08 -0700 that day. Its output mentions `core/b.py`. `tests/factory/test_merge_protected_paths.py` was added a day later, in `ba3fea8` at 2026-10-08 23:30. Its fixture writes `core/b.py` under `tmp_path / "t"` (lines 62 and 73-76). So no test made this directory. The clone run above also shows that no test now writes anything into the checkout except bytecode.

**Comparing only this ticket's own changes (round 2).** Another approved ticket, T-0044 (the de-bloat ticket that deletes the unread `force_push_allowed` setting, state `planned`), changes two assertions inside test functions in `tests/factory/test_instance.py` (its `design.md` part B and Tests to change). A comparison of the whole suite before and after this ticket would count those as missing if T-0044 merged in between. The merge gate merges each sub-ticket with `git merge --no-ff` (`factory/gitops.py:192`) and the message `Merge {branch}: {title} ({id})` (`factory/cli.py:990`), where the branch is `factory/<id>` (`factory/gitops.py:43`). So each of this ticket's merges has the integration branch before it as its first parent, and the difference across that merge is exactly that sub-ticket's change. The two comparison commands under Acceptance use that. On `0ba4e4f` they print `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` and `pairs: 0; test lines before: 0, after: 0, change: 0`. In a throwaway clone of `0ba4e4f` I then made three commits and merged two of them into `main` with `--no-ff`: one that deletes the duplicate test (lines 118-125), merged as `Merge factory/T-0045.1: part A`; then one that deletes T-0044's `and cfg["force_push_allowed"] is False` from `test_instance.py:109`, merged as `Merge factory/T-0044.1: unread setting`; then an unmerged branch commit that adds `tests/factory/_cli.py` and deletes the first three lines of `test_replan.py`. With the branch checked out, the first command printed `pair: 2`, `removed: 14` (the duplicate test and the 13 tests of `test_replan.py`, which no longer collects), `added: 0`, `missing: 2`, both from `test_p0_cli.py::test_run_finish_without_output_is_killed`. T-0044's assertion change was not counted. With `main` checked out, it printed `pair: 1`, `removed: 1`, the duplicate test only, `added: 0`, `missing: 2`. The line command printed `pairs: 1; test lines before: 9710, after: 9702, change: -8` on `main`. Both commands gave the same output under bash and zsh.

## Root cause

- No shared module exists. `tests/factory/` has `conftest.py`, which sets the instance environment, and `clean_harness_cli.py`, a test-only launcher. Neither holds helpers, so each new file copied the helpers it needed or imported them from a sibling test file.
- Bytecode: the suite sets `PYTHONDONTWRITEBYTECODE` call by call, in 34 places. `conftest.py` does not set it. Four sites write bytecode anyway:
  - `role_argv` (`test_drive.py:199-204`) starts Python with the inherited environment;
  - `without_evidence` (`test_role_inputs.py:19-24`) does the same;
  - `test_cost_once.py:19-21` loads `factory/cost.py` inside the pytest process through `importlib`;
  - `test_subtickets.py:179-181` and `:204` load `factory/subtickets.py` the same way.

  An `importlib` load writes bytecode unless the interpreter flag `sys.dont_write_bytecode` is set. The environment variable alone does not stop it, as the second prototype run showed.

## Out of scope

- Any change under `factory/`, `bin/factory`, `agents/`, the documents or `README.md`. No command, state, stop or path changes.
- The bodies of the four design-block tests (`test_writing_standard.py:63`, `test_coding_standard.py:72`, `test_turn_economy.py:49`, `test_decision_log.py:248`), which a later ticket changes. Their files' module-level helpers are in scope.
- Speeding up `built_to_implementer` (`test_shepherd.py:391`).
- `ticket`, `events` and `runs` methods on the fixture classes, which the request's proposed `Store` class would also carry. They read different attributes per class. Cut: the ticket names only the wrapper pair.
- Other helpers repeated in a few files with differing bodies: the `git` variants, `files`, `events`, `finish`, `start`, and the `cli` of `test_store_setup.py` and `test_harness_lock.py`.
- The bytecode pytest writes for `tests/factory/__init__.py` and `conftest.py` before `conftest.py` runs.
- `clean_harness_cli.py` and the in-process uses of the CLI in `test_store_migrate.py`, which another ticket changes.
- Removing the per-call `PYTHONDONTWRITEBYTECODE` settings, which still work.
- Removing the stray `core/b.py/` directory. It is untracked operator state; see Operator steps.

## Open questions

none

## Decisions

- Test files never import from another test file. Shared code lives in two non-test modules. `tests/factory/_cli.py` holds the generic helpers: constants, wrappers, the JSON readers, the ticket reader and the two setups. `tests/factory/_fixtures.py` holds the scenario fixtures that more than one test file uses. Standing: a later ticket that needs a helper in a second file moves it to one of these two modules. Rejected: one module for everything, which would put the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build beside eight-line wrappers. Also rejected: `conftest.py` fixtures, whose names apply to every file, while four files define their own `target`.
- The JSON reader comes in two forms. `js` only parses. `js_ok` asserts exit 0 and then parses. Each file imports the form its own copy had, under the name `js`, so no call site changes and the exit check stays opt-in per caller. Rejected: a `check=` argument at each call, which touches every call site.
- `conftest.py` sets both `PYTHONDONTWRITEBYTECODE=1` in the environment and `sys.dont_write_bytecode = True`. Rejected: adding `env=` at each Python start, the request's suggestion. It misses the two in-process loads, as the prototype showed.
- The check that nothing is written into the checkout leaves out `tests/factory/__pycache__`. pytest writes two files there before `conftest.py` can act. Only the person running pytest can stop that.
- The removed test is `test_p0_cli.py`'s KILLED-override test. The test in `test_empty_output.py` keeps all three of its checks.
- The approved-parent helper takes a caller's `ok` function, the ticket id and a spec file. It runs the five calls and returns the ticket id. Ticket creation stays with the caller. Sites that use `spec add --from-run`, assert a step, or put other work between steps keep their own calls. Cut: the request's `plan` argument. A plan is not part of the repeated five calls.
- The class-level `cli`/`ok` pair comes from one base class. Each class still builds its own environment, so the instance copy, the venv and the PATH stand-in stay where they are. A class whose `cli` differs overrides `cli` only.
- The acceptance checks name helper names (`REPO`, `js`, and so on) and the one test this change removes. The subject of this ticket is the suite's own structure, so those names are the behaviour being checked.
- Changed in round 2: the checks that compare with a base compare across each of this ticket's own merges into `main` (each `Merge factory/T-0045.<n>` commit against its first parent), plus the unmerged commits of the checked-out branch (`git merge-base HEAD main` against `HEAD`), and add up the results. Other tickets' changes to the same files are therefore never counted, whichever order they merge in. Rejected: v1's single base, the commit before this ticket's first merge, which counts T-0044's two assertion changes if T-0044 merges in between (critic, round 1). Rejected: the critic's suggested THEN with a second outcome when T-0044 has merged. Three more de-bloat tickets in the same sweep (T-0046, T-0047, T-0048) edit the same files and would each need a clause of their own.

## Risk

Blast radius: the test suite only. A wrong move can break tests, and the suite run catches that. It can also silently drop an assertion, and the assertion comparison catches that. The harness does not change.

Sequencing: T-0044, the de-bloat ticket that deletes the unread `force_push_allowed` setting, edits two assertions inside test functions in `tests/factory/test_instance.py`, a file whose module-level helpers this ticket moves. Neither ticket's edits overlap the other's lines. The comparison checks of this ticket count only this ticket's own merges, so they hold under either merge order. The later tickets in the same sweep, and the one that changes the four design-block tests, touch the same files and should follow this one to avoid merge conflicts.

Protected paths: none

## Operator steps

- After merge, remove the stray empty directory a role run left in the dev checkout: `rmdir ~/dev/spec-factory/core/b.py ~/dev/spec-factory/core`.
- Optionally clear the bytecode earlier suite runs left there: `rm -rf ~/dev/spec-factory/factory/__pycache__`.

