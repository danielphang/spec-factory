## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0469-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0469-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0469-verifier/wt` (branch `factory/T-0045.2`, base `6ac73f13f1768bd09a6cc1da3879be8ead51e381`, head `a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0045.2

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

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`

=== proposal.md
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

=== design.md
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

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: Test files share code only through helper modules
No file of the harness suite SHALL import from another test file; code that more than one test file uses MUST live in a non-test helper module.

#### Scenario: No test file imports from another test file
- WHEN `.venv/bin/python -c 'import ast,pathlib; bad=[f"{p.name}:{n.lineno}" for p in sorted(pathlib.Path("tests/factory").glob("*.py")) for n in ast.walk(ast.parse(p.read_text())) if (isinstance(n,ast.ImportFrom) and (any(s.startswith("test_") for s in (n.module or "").split(".")) or any(a.name.startswith("test_") for a in n.names))) or (isinstance(n,ast.Import) and any(s.startswith("test_") for a in n.names for s in a.name.split(".")))]; print(f"cross-test imports: {len(bad)}", *bad)'`
- THEN it prints `cross-test imports: 0`

### Requirement: Each shared test helper is written once
The repository and entry-point constants, the call wrapper, the JSON reader, the ticket reader, the empty-repository setup and the approved-parent setup SHALL each be defined in exactly one place in the harness suite, and this stays a standing guard: a later test file that needs one of them imports it.

#### Scenario: The shared constants and wrappers are defined once
- WHEN `.venv/bin/python -c 'import ast,pathlib,collections; c=collections.Counter(t.id if isinstance(n,ast.Assign) else n.name for p in pathlib.Path("tests/factory").glob("*.py") for n in ast.parse(p.read_text()).body for t in (n.targets if isinstance(n,ast.Assign) else [n]) if isinstance(t,(ast.Name,ast.FunctionDef))); print(*(f"{k}={c[k]}" for k in ("REPO","BIN","run","js","ticket","git_repo","approved_parent")))'`
- THEN it prints `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`

#### Scenario: The approved-parent and empty-repository setups are written once
- WHEN `.venv/bin/python -c 'import pathlib; L={p:p.read_text().splitlines() for p in sorted(pathlib.Path("tests/factory").glob("*.py"))}; ap=[f"{p.name}:{i+1}" for p,l in L.items() for i in range(1,len(l)-3) if "ready-for-spec-writer" in l[i-1] and "\"spec\", \"add\"" in l[i] and "\"spec:init\"" in l[i+1] and "awaiting-spec-gate" in l[i+2] and "\"approve-spec\"" in l[i+3] and "assert" not in l[i+3] and " = " not in l[i+3]]; gr=[f"{p.name}:{i+1}" for p,l in L.items() for i,x in enumerate(l) if "\"-b\", \"main\"" in x and "\"init\"" in x and any("--allow-empty" in y for y in l[i:i+4])]; print(f"approved-parent sequences: {len(ap)}", *ap); print(f"empty-commit repo setups: {len(gr)}", *gr)'`
- THEN each of the two lines reports either `0`, or `1` followed by a single site in `_cli.py`

### Requirement: The refactor keeps every test and assertion but the one duplicate
Across this change's own merges and unmerged commits, the harness suite SHALL lose exactly the one duplicate test and gain none, and every assert statement in every other test function MUST still be present in that function.

#### Scenario: Only the duplicate test and its assertions are gone
The command compares each `Merge factory/T-0045.<n>` commit reachable from HEAD with its first parent, and `git merge-base HEAD main` with HEAD, and adds up the results, so changes other tickets make to the same files are never counted. A collection failure shows as removed tests. tar may print a locale warning on stderr; it is not part of the result.
- WHEN `T=$(mktemp -d); { for m in $(git log --format=%H --grep='^Merge factory/T-0045[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do [ -d "$T/$s" ] || { mkdir "$T/$s" && git archive "$s" | tar -x -C "$T/$s" && ln -s "$PWD/.venv" "$T/$s/.venv" && (cd "$T/$s" && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/factory 2>&1 | grep '::' | sort > ids); }; done; echo "pair $b $h"; comm -23 "$T/$b/ids" "$T/$h/ids" | sed 's/^/removed /'; comm -13 "$T/$b/ids" "$T/$h/ids" | sed 's/^/added /'; .venv/bin/python -c 'import ast,pathlib,sys; A=lambda r: {f"{p.name}::{n.name}": {ast.unparse(a) for a in ast.walk(n) if isinstance(a,ast.Assert)} for p in sorted(pathlib.Path(r,"tests/factory").glob("test_*.py")) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith("test_")}; b,h=A(sys.argv[1]),A(sys.argv[2]); [print(f"missing {k}: {a[:80]}") for k in sorted(b) for a in sorted(b[k]-h.get(k,set()))]' "$T/$b" "$T/$h"; done > "$T/out"; for k in pair removed added missing; do echo "$k: $(grep -c "^$k " "$T/out")"; grep "^$k " "$T/out" | grep -v '^pair '; done; rm -rf "$T"`
- THEN `pair:` is at least 1; `removed: 1` is followed by exactly `removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed`; it prints `added: 0`; and it prints `missing: 2`, followed by two lines that both start `missing test_p0_cli.py::test_run_finish_without_output_is_killed:`

#### Scenario: The suite is shorter
The command adds up the test-file line counts over the same pairs as the scenario above.
- WHEN `{ for m in $(git log --format=%H --grep='^Merge factory/T-0045[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do printf '%s ' $(git ls-tree --name-only "$s" tests/factory/ | grep '\.py$' | while read f; do git show "$s:$f"; done | wc -l); done; echo; done | awk '{n++; b+=$1; h+=$2} END {print "pairs: " n+0 "; test lines before: " b+0 ", after: " h+0 ", change: " h-b}'`
- THEN `pairs` is at least 1 and `change` is negative, and the verifier reports the line

### Requirement: A suite run writes nothing into the checkout
A run of the harness suite SHALL pass and leave every path of the checkout as it was, except pytest's own cache of the test modules in `tests/factory/__pycache__`.

#### Scenario: A suite run in a fresh clone passes and adds nothing to the checkout
The command gives pytest its own temporary directory under `/tmp`, as the existing harness-suite scenario does, and removes it when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0045-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && cd $T/c && find . \( -path ./.git -o -path ./tests/factory/__pycache__ \) -prune -o -print | sort > $T/before && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; find . \( -path ./.git -o -path ./tests/factory/__pycache__ \) -prune -o -print | sort > $T/after; echo "paths changed: $(comm -3 $T/before $T/after | wc -l | tr -d ' ')"; comm -3 $T/before $T/after; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and the next line is `paths changed: 0` with nothing after it

=== verification.md
## Acceptance

- No test file imports from another test file → NEW. Today it prints `cross-test imports: 27` and 27 sites in 14 files.
- The shared constants and wrappers are defined once → NEW. Today it prints `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`.
- The approved-parent and empty-repository setups are written once → NEW. Today it prints `approved-parent sequences: 13` and `empty-commit repo setups: 11`, with their sites, none in `_cli.py`.
- Only the duplicate test and its assertions are gone → NEW. Today no `Merge factory/T-0045.` commit exists and HEAD is `main`, so nothing is compared. It prints `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` (run on `0ba4e4f`).
- The suite is shorter → NEW. Today it prints `pairs: 0; test lines before: 0, after: 0, change: 0` (run on `0ba4e4f`).
- A suite run in a fresh clone passes and adds nothing to the checkout → NEW. Today it prints `577 passed in 283.89s (0:04:43)`, then `paths changed: 13`: `factory/__pycache__` and 12 `.pyc` files in it.

## PR description (the implementer's output)

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

## Diff `6ac73f13f1768bd09a6cc1da3879be8ead51e381...a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4`

diff --git a/tests/factory/_cli.py b/tests/factory/_cli.py
index bcc3213..ebfb936 100644
--- a/tests/factory/_cli.py
+++ b/tests/factory/_cli.py
@@ -1,6 +1,7 @@
 """Helpers the harness suite shares: where the repository and `bin/factory` are, the wrappers that
-call it, the JSON readers and the ticket reader. A test file imports them from here, never from
-another test file. Not named `test_*`, so pytest does not collect it.
+call it, the JSON readers, the ticket reader, the two setups (an empty repository and a parent past
+the spec gate) and `CliStore`, the base of the fixture classes. A test file imports them from here,
+never from another test file. Not named `test_*`, so pytest does not collect it.
 """
 from __future__ import annotations
 
@@ -54,3 +55,37 @@ def ticket(store: Path, tid: str = "T-0001") -> dict:
 
 def tree(path: Path) -> dict[str, bytes]:
     return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
+
+
+def git_repo(path: Path) -> Path:
+    """A git repository at `path` on branch `main`, with one empty commit."""
+    path.mkdir(parents=True, exist_ok=True)
+    for argv in (["init", "-q", "-b", "main"],
+                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
+        subprocess.run(["git", "-C", str(path), *argv], check=True, capture_output=True)
+    return path
+
+
+def approved_parent(ok, tid: str, spec: Path | str) -> str:
+    """Take ticket `tid` past the spec gate with `spec` as its spec (old format; no spec store).
+    `ok(*argv)` runs one factory command and fails the test on a non-zero exit."""
+    ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
+    ok("spec", "add", tid, "--file", str(spec))
+    ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+    ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
+    ok("approve-spec", tid)
+    return tid
+
+
+class CliStore:
+    """One `cli` and `ok` for a fixture class that runs `bin/factory` in the environment `self.env`,
+    which the subclass builds."""
+    env: dict
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
+        return js(cp)
diff --git a/tests/factory/test_build_startup.py b/tests/factory/test_build_startup.py
index 97f4d3a..7faefb3 100644
--- a/tests/factory/test_build_startup.py
+++ b/tests/factory/test_build_startup.py
@@ -8,24 +8,10 @@ from pathlib import Path
 import pytest
 import yaml
 
+from ._cli import approved_parent
 from .test_subtickets import PLAN_LETTERS, js, run, ticket
 
 
-def approved_parent(store: Path, tmp_path: Path) -> str:
-    """A parent past the spec gate (old-format spec; no spec store), with no plan yet."""
-    req = tmp_path / "r.md"
-    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
-    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
-    spec = tmp_path / "s.md"
-    spec.write_text("## Problem\nx\n")
-    js(run(store, "ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(store, "spec", "add", tid, "--file", str(spec)))
-    js(run(store, "ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(store, "ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(store, "approve-spec", tid))
-    return tid
-
-
 def planner_run(store: Path, tid: str, plan: str) -> str:
     rid = js(run(store, "run", "start", "--role", "planner", "--ticket", tid))["run_id"]
     js(run(store, "run", "compose", rid))
@@ -40,7 +26,10 @@ def ticket_files(store: Path) -> list[str]:
 
 def test_subticket_add_without_a_source_uses_the_recorded_planner_run(tmp_path):
     store = tmp_path / "state"
-    tid = approved_parent(store, tmp_path)
+    (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "s.md").write_text("## Problem\nx\n")
+    tid = js(run(store, "ticket", "new", "--file", str(tmp_path / "r.md")))["id"]
+    approved_parent(lambda *a: js(run(store, *a)), tid, tmp_path / "s.md")
     rid = planner_run(store, tid, PLAN_LETTERS)
     js(run(store, "plan", "add", tid, "--from-run", rid))
     out = js(run(store, "subticket", "add", tid))
@@ -50,7 +39,10 @@ def test_subticket_add_without_a_source_uses_the_recorded_planner_run(tmp_path):
 
 def test_subticket_add_without_a_source_takes_the_latest_plan(tmp_path):
     store = tmp_path / "state"
-    tid = approved_parent(store, tmp_path)
+    (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "s.md").write_text("## Problem\nx\n")
+    tid = js(run(store, "ticket", "new", "--file", str(tmp_path / "r.md")))["id"]
+    approved_parent(lambda *a: js(run(store, *a)), tid, tmp_path / "s.md")
     first = planner_run(store, tid, PLAN_LETTERS)
     js(run(store, "plan", "add", tid, "--from-run", first))
     second = planner_run(store, tid, PLAN_LETTERS)
@@ -62,7 +54,10 @@ def test_subticket_add_without_a_source_takes_the_latest_plan(tmp_path):
 @pytest.mark.parametrize("plan_from", ["none", "file"])
 def test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run(tmp_path, plan_from):
     store = tmp_path / "state"
-    tid = approved_parent(store, tmp_path)
+    (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "s.md").write_text("## Problem\nx\n")
+    tid = js(run(store, "ticket", "new", "--file", str(tmp_path / "r.md")))["id"]
+    approved_parent(lambda *a: js(run(store, *a)), tid, tmp_path / "s.md")
     if plan_from == "file":
         plan = tmp_path / "plan.md"
         plan.write_text(PLAN_LETTERS)
@@ -77,7 +72,10 @@ def test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run(tmp
 
 def test_ready_implementers_lists_every_sub_ticket_in_id_order(tmp_path):
     store = tmp_path / "state"
-    tid = approved_parent(store, tmp_path)
+    (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "s.md").write_text("## Problem\nx\n")
+    tid = js(run(store, "ticket", "new", "--file", str(tmp_path / "r.md")))["id"]
+    approved_parent(lambda *a: js(run(store, *a)), tid, tmp_path / "s.md")
     rid = planner_run(store, tid, PLAN_LETTERS)
     js(run(store, "plan", "add", tid, "--from-run", rid))
     js(run(store, "ticket", "transition", tid, "--to", "planned", "--by", "t"))
diff --git a/tests/factory/test_coding_standard.py b/tests/factory/test_coding_standard.py
index 33c1067..2f5d693 100644
--- a/tests/factory/test_coding_standard.py
+++ b/tests/factory/test_coding_standard.py
@@ -15,7 +15,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import BIN, REPO, STRIP
+from ._cli import BIN, REPO, STRIP, git_repo
 
 STANDARD = REPO.resolve() / "docs" / "coding.md"
 FENCE = "`" * 3
@@ -35,11 +35,7 @@ def system_prompts(tmp_path_factory) -> dict[str, str]:
     in a fresh scratch target on a throwaway store (FACTORY_STATE), as in the spec's scenario. The
     ticket's status is set by `ticket set` so that each role can start."""
     tmp = tmp_path_factory.mktemp("coding")
-    t = tmp / "target"
-    t.mkdir()
-    for argv in (["init", "-q", "-b", "main"],
-                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
-        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
+    t = git_repo(tmp / "target")
     req = tmp / "r.md"
     req.write_text("# demo\n\nDo the thing.\n")
     store = {"FACTORY_STATE": str(tmp / "s")}
diff --git a/tests/factory/test_critic_approved_changes.py b/tests/factory/test_critic_approved_changes.py
index 9a6cac6..3f7f7a9 100644
--- a/tests/factory/test_critic_approved_changes.py
+++ b/tests/factory/test_critic_approved_changes.py
@@ -8,14 +8,13 @@ source. The body is `none` with no such change, and the section is left out with
 """
 from __future__ import annotations
 
-import json
 import os
 import subprocess
 from pathlib import Path
 
 import pytest
 
-from ._cli import BIN, REPO
+from ._cli import CliStore
 
 HEADING = "## Approved changes not yet archived"
 
@@ -28,7 +27,7 @@ def spec(decision: str, requirement: str) -> str:
             "=== verification.md\n## Acceptance\n- It acts → NEW\n")
 
 
-class Store:
+class Store(CliStore):
     def __init__(self, tmp_path: Path, spec_store: bool = True):
         self.tmp = tmp_path
         self.root = tmp_path / "store"
@@ -39,11 +38,6 @@ class Store:
         if spec_store:
             self.ok("init")
 
-    def ok(self, *argv: str) -> dict:
-        cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-        assert cp.returncode == 0, cp.stdout + cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def ticket(self, tid: str, title: str, text: str) -> None:
         """A new ticket `tid` with spec v1 `text`, at ready-for-critic."""
         req, sp = self.tmp / f"{tid}-req.md", self.tmp / f"{tid}-spec.md"
diff --git a/tests/factory/test_drive.py b/tests/factory/test_drive.py
index 726c849..b9cfaa0 100644
--- a/tests/factory/test_drive.py
+++ b/tests/factory/test_drive.py
@@ -21,7 +21,7 @@ from pathlib import Path
 
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import BIN, REPO, CliStore
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 
@@ -50,7 +50,7 @@ sys.exit(1 if err else 0)
 TRIAGE_OK = {"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}]}
 
 
-class Store:
+class Store(CliStore):
     """A throwaway store with T-0001 ready for triage, and the stand-in `claude` first on PATH."""
 
     def __init__(self, tmp_path: Path, instance: Path = FIXTURE_INSTANCE):
@@ -73,11 +73,6 @@ class Store:
         env = {**self.env, "STANDIN_PLAYS": json.dumps(plays or {})}
         return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
 
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def drive(self, plays: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
         cp = self.cli("drive", "T-0001", *extra, plays=plays)
         return cp, json.loads(cp.stdout.strip().splitlines()[-1])
diff --git a/tests/factory/test_drive_build.py b/tests/factory/test_drive_build.py
index 240c6f0..645b36d 100644
--- a/tests/factory/test_drive_build.py
+++ b/tests/factory/test_drive_build.py
@@ -18,6 +18,7 @@ import time
 
 import yaml
 
+from ._cli import approved_parent, git_repo
 from .test_drive import BIN, REPO, Store
 
 STANDIN = '''#!{python}
@@ -61,14 +62,8 @@ class BuildStore(Store):
         (tmp_path / "bin" / "claude").write_text(STANDIN.format(python=sys.executable))
         spec = tmp_path / "spec.md"
         spec.write_text("## Problem\nx\n")
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-        self.ok("spec", "add", "T-0001", "--file", str(spec))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-        self.ok("approve-spec", "T-0001")
-        self.target = tmp_path / "target"
-        self.git("init", "-q", "-b", "main", str(self.target), cwd=tmp_path)
-        self.git("commit", "-q", "--allow-empty", "-m", "init")
+        approved_parent(self.ok, "T-0001", spec)
+        self.target = git_repo(tmp_path / "target")
         self.env.update(FACTORY_REPO=str(self.target), FACTORY_INTEGRATION_BRANCH="main")
 
     def git(self, *argv: str, cwd=None) -> str:
diff --git a/tests/factory/test_empty_output.py b/tests/factory/test_empty_output.py
index 0323f1b..d1e049b 100644
--- a/tests/factory/test_empty_output.py
+++ b/tests/factory/test_empty_output.py
@@ -9,16 +9,15 @@ from __future__ import annotations
 
 import json
 import os
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import CliStore
 
 
-class Store:
+class Store(CliStore):
     """A throwaway store with one ticket, T-0001, and one triage run started on it."""
 
     def __init__(self, tmp_path: Path):
@@ -31,14 +30,6 @@ class Store:
         self.ok("run", "compose", self.rid)
         self.run_dir = self.root / "runs" / self.rid
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def meta(self) -> dict:
         return yaml.safe_load((self.run_dir / "meta.yaml").read_text())
 
diff --git a/tests/factory/test_environment_sync.py b/tests/factory/test_environment_sync.py
index 0fd1728..023d8e1 100644
--- a/tests/factory/test_environment_sync.py
+++ b/tests/factory/test_environment_sync.py
@@ -17,7 +17,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import BIN, REPO, CliStore, approved_parent, git_repo
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 GIT_ID = {"GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@x", "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@x"}
@@ -25,7 +25,7 @@ DUMP = "env > synced.env"  # a sync that records the environment it ran in
 FAIL = "echo sync-$((1+1)) >&2; echo out-line; exit $((2+1))"  # output and exit code are computed
 
 
-class Target:
+class Target(CliStore):
     """T-0001 approved and split into T-0001.1, ready for its implementer, on an instance whose
     `run_env` exports T31_CACHE and whose `environment_sync` is `sync` (None: the key is absent)."""
 
@@ -43,22 +43,16 @@ class Target:
             f.write("run_env: {T31_CACHE: /tmp/t31-cache}\n")
             if sync is not None:
                 f.write(f"environment_sync: {json.dumps(sync)}\n")
-        self.repo.mkdir()
         self.env = {**os.environ, **GIT_ID, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(inst),
                     "FACTORY_REPO": str(self.repo), "FACTORY_INTEGRATION_BRANCH": "main",
                     "PYTHONDONTWRITEBYTECODE": "1"}
-        self.git("init", "-q", "-b", "main")
-        self.git("commit", "-q", "--allow-empty", "-m", "init")
+        git_repo(self.repo)
         req, spec, plan = tmp_path / "req.md", tmp_path / "spec.md", tmp_path / "plan.md"
         req.write_text("# F\n\nDo x.\n")
         spec.write_text("## Problem\nx\n")
         plan.write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
         self.ok("ticket", "new", "--file", str(req))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-        self.ok("spec", "add", "T-0001", "--file", str(spec))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-        self.ok("approve-spec", "T-0001")
+        approved_parent(self.ok, "T-0001", spec)
         self.ok("subticket", "add", "T-0001", "--file", str(plan))
 
     def git(self, *argv: str, cwd: Path | None = None) -> str:
diff --git a/tests/factory/test_gate_paths.py b/tests/factory/test_gate_paths.py
index 3da0926..d8854c4 100644
--- a/tests/factory/test_gate_paths.py
+++ b/tests/factory/test_gate_paths.py
@@ -10,7 +10,6 @@ its own `gate_commands`, and a scratch target repo, as the spec's t0028-sub.sh f
 """
 from __future__ import annotations
 
-import json
 import os
 import shutil
 import subprocess
@@ -19,14 +18,14 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import CliStore, approved_parent
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 UNSCOPED = "git diff --check main...HEAD"
 SCOPED = "sh -c 'exit 7'"
 
 
-class Target:
+class Target(CliStore):
     """T-0001.1 at checks-in-flight, its one commit changing `changed`; I is its implementer run."""
 
     def __init__(self, tmp_path: Path, gate: str, changed: str = "docs/b.md"):
@@ -52,11 +51,7 @@ class Target:
         (tmp_path / "spec.md").write_text("## Problem\nx\n")
         (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
         self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-        self.ok("spec", "add", "T-0001", "--file", str(tmp_path / "spec.md"))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-        self.ok("approve-spec", "T-0001")
+        approved_parent(self.ok, "T-0001", tmp_path / "spec.md")
         self.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
         self.implementer = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
         wt = self.root / "worktrees" / "T-0001.1"
@@ -77,14 +72,6 @@ class Target:
         assert cp.returncode == 0, cp.stderr
         return cp.stdout.strip()
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def composed(self, rid: str) -> tuple[str, dict]:
         self.ok("run", "compose", rid)
         d = self.root / "runs" / rid
diff --git a/tests/factory/test_harness_lock.py b/tests/factory/test_harness_lock.py
index f1de71e..d9f91c0 100644
--- a/tests/factory/test_harness_lock.py
+++ b/tests/factory/test_harness_lock.py
@@ -24,7 +24,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import CLEAN_CLI, REPO, STRIP, js, tree
+from ._cli import CLEAN_CLI, REPO, STRIP, git_repo, js, tree
 
 HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
 ZERO = "0" * 40
@@ -61,9 +61,7 @@ def revision(harness: Path) -> str:
 
 
 def make_target(path: Path, harness: Path) -> Path:
-    path.mkdir(parents=True)
-    git(path, "init", "-q", "-b", "main")
-    git(path, "commit", "-q", "--allow-empty", "-m", "init")
+    git_repo(path)
     cp = cli(harness, path, "init", "--repo-name", "demo")
     assert cp.returncode == 0, cp.stderr
     return path
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
index c444cbd..fc9e4e7 100644
--- a/tests/factory/test_instance.py
+++ b/tests/factory/test_instance.py
@@ -13,19 +13,11 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO, STRIP, cli, js, tree
+from ._cli import BIN, REPO, STRIP, cli, git_repo, js, tree
 
 NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
 
 
-def git_repo(path: Path) -> Path:
-    path.mkdir(parents=True, exist_ok=True)
-    for argv in (["init", "-q", "-b", "main"],
-                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
-        subprocess.run(["git", "-C", str(path), *argv], check=True, capture_output=True)
-    return path
-
-
 def harness_status() -> str:
     return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout
 
diff --git a/tests/factory/test_merge_protected_paths.py b/tests/factory/test_merge_protected_paths.py
index 2407455..0ef2751 100644
--- a/tests/factory/test_merge_protected_paths.py
+++ b/tests/factory/test_merge_protected_paths.py
@@ -22,7 +22,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import REPO, CliStore
 
 FIXTURE = REPO / "tests" / "factory" / "fixtures" / "instance"
 
@@ -52,7 +52,7 @@ console.log(lines.join('\n'))
 """
 
 
-class Gate:
+class Gate(CliStore):
     """The t0033-gate.sh fixture. `risk` is the line T-0001's approved spec carries in its Risk
     section (None: T-0001 is never approved and has no sub-ticket; the commit lands on T-0001's own
     branch). `changes` as in the fixture: `p` appends to p, `p-` deletes p, `p>q` renames p to q."""
@@ -129,14 +129,6 @@ class Gate:
                             capture_output=True, text=True, check=True)
         return cp.stdout.strip()
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def refused(self, *argv: str) -> str:
         cp = self.cli(*argv)
         assert cp.returncode == 2, cp.stdout + cp.stderr
diff --git a/tests/factory/test_plan_fields.py b/tests/factory/test_plan_fields.py
index 6221f30..2cd180d 100644
--- a/tests/factory/test_plan_fields.py
+++ b/tests/factory/test_plan_fields.py
@@ -11,14 +11,18 @@ import subprocess
 
 import pytest
 
-from .test_build_startup import approved_parent, ticket_files
+from ._cli import approved_parent
+from .test_build_startup import ticket_files
 from .test_subtickets import js, run
 
 
 @pytest.fixture
 def store(tmp_path):
     root = tmp_path / "state"
-    tid = approved_parent(root, tmp_path)
+    (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+    (tmp_path / "s.md").write_text("## Problem\nx\n")
+    tid = js(run(root, "ticket", "new", "--file", str(tmp_path / "r.md")))["id"]
+    approved_parent(lambda *a: js(run(root, *a)), tid, tmp_path / "s.md")
 
     def add(plan: str) -> subprocess.CompletedProcess:
         f = tmp_path / "plan.md"
diff --git a/tests/factory/test_redispatch_rows.py b/tests/factory/test_redispatch_rows.py
index 84db4ab..9d6d441 100644
--- a/tests/factory/test_redispatch_rows.py
+++ b/tests/factory/test_redispatch_rows.py
@@ -15,6 +15,7 @@ from pathlib import Path
 
 import pytest
 
+from ._cli import approved_parent
 from ._cli import js_ok as js
 from ._cli import run_env as run
 
@@ -30,11 +31,7 @@ def env(tmp_path: Path) -> dict:
     (tmp_path / "spec.md").write_text("## Problem\nx\n")
     (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
     js(run(e, "ticket", "new", "--file", str(tmp_path / "req.md")))
-    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(e, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
-    js(run(e, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(e, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(e, "approve-spec", "T-0001"))
+    approved_parent(lambda *a: js(run(e, *a)), "T-0001", tmp_path / "spec.md")
     js(run(e, "subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md")))
     js(run(e, "ticket", "set", ST, "status=checks-in-flight", f"head={HEAD}"))
     return e
diff --git a/tests/factory/test_replan.py b/tests/factory/test_replan.py
index 63773e2..7bf79c6 100644
--- a/tests/factory/test_replan.py
+++ b/tests/factory/test_replan.py
@@ -15,7 +15,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import run, ticket
+from ._cli import approved_parent, run, ticket
 from ._cli import js_ok as js
 
 NOTE = "Re-plan: add one fix for the case-insensitive path.\n"
@@ -39,11 +39,7 @@ def store(tmp_path: Path) -> Path:
     (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
     (tmp_path / "spec.md").write_text("## Problem\nx\n")
     js(run(s, "ticket", "new", "--file", str(tmp_path / "req.md")))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(s, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(s, "approve-spec", "T-0001"))
+    approved_parent(lambda *a: js(run(s, *a)), "T-0001", tmp_path / "spec.md")
     return s
 
 
diff --git a/tests/factory/test_resolve_rulings.py b/tests/factory/test_resolve_rulings.py
index 4666127..9697bf6 100644
--- a/tests/factory/test_resolve_rulings.py
+++ b/tests/factory/test_resolve_rulings.py
@@ -6,12 +6,11 @@ Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_de
 """
 from __future__ import annotations
 
-import subprocess
 from pathlib import Path
 
 import pytest
 
-from ._cli import ticket
+from ._cli import git_repo, ticket
 from ._cli import js_ok as js
 from ._cli import run_env as run
 
@@ -22,10 +21,7 @@ RULING = "Ruling: take the second approach.\n"
 def env(tmp_path: Path) -> dict:
     """A scratch store and target repo: T-0001 past the spec gate (no spec store)."""
     store = tmp_path / "store"
-    target = tmp_path / "target"
-    subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
-    subprocess.run(["git", "-C", str(target), "-c", "user.email=f@x", "-c", "user.name=f",
-                    "commit", "-q", "--allow-empty", "-m", "init"], check=True)
+    target = git_repo(tmp_path / "target")
     e = {"FACTORY_STATE": str(store), "FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"}
     (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
     (tmp_path / "spec.md").write_text("## Problem\nx\n")
diff --git a/tests/factory/test_results_commit.py b/tests/factory/test_results_commit.py
index 3c2bb4f..5a4c07a 100644
--- a/tests/factory/test_results_commit.py
+++ b/tests/factory/test_results_commit.py
@@ -15,27 +15,24 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import CliStore
 
 HEAD = "0" * 40
 REVIEWER_TAIL = "Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n"
 VERIFIER_TAIL = "Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n"
 
 
-class Store:
+class Store(CliStore):
     def __init__(self, tmp: Path):
         self.root = tmp / "store"
         self.tmp = tmp
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
         req = tmp / "r.md"
         req.write_text("# x\n\nthe thing\n")
         cp = self.cli("ticket", "new", "--file", str(req))
         assert cp.returncode == 0, cp.stderr
         self.tid = json.loads(cp.stdout.strip().splitlines()[-1])["id"]
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        env = {**os.environ, "FACTORY_STATE": str(self.root), "PYTHONDONTWRITEBYTECODE": "1"}
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
     def record(self, role: str, output: str | None, *extra: str) -> subprocess.CompletedProcess:
         argv = ["results", "record", self.tid, "--head", HEAD, "--role", role, "--run", "R1", *extra]
         if output is not None:
diff --git a/tests/factory/test_run_isolation.py b/tests/factory/test_run_isolation.py
index b8e0dd7..b388c80 100644
--- a/tests/factory/test_run_isolation.py
+++ b/tests/factory/test_run_isolation.py
@@ -8,7 +8,6 @@ changes `instance.yaml`, on a copy of the suite's fixture instance (FACTORY_INST
 """
 from __future__ import annotations
 
-import json
 import os
 import shutil
 import subprocess
@@ -16,7 +15,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import BIN, REPO
+from ._cli import CliStore, approved_parent, git_repo
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
@@ -28,7 +27,7 @@ SECTION = ("\n## Running code\nRun every test, script or prototype through this
            "protected path outside the repository.\n")
 
 
-class Store:
+class Store(CliStore):
     def __init__(self, tmp_path: Path, run_env: str | None = None):
         self.tmp = tmp_path
         self.root = tmp_path / "state"
@@ -40,14 +39,6 @@ class Store:
                 f.write(run_env)
             self.env["FACTORY_INSTANCE"] = str(inst)
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def request(self) -> None:
         p = self.tmp / "req.md"
         p.write_text("# Fixture\n\nThe bot should do the thing.\n")
@@ -58,20 +49,12 @@ class Store:
         self.request()
         spec = self.tmp / "spec.md"
         spec.write_text("## Problem\nx\n")
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-        self.ok("spec", "add", "T-0001", "--file", str(spec))
-        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-        self.ok("approve-spec", "T-0001")
+        approved_parent(self.ok, "T-0001", spec)
 
     def implementer_ready(self) -> None:
         """One sub-ticket of an approved T-0001, in a scratch target repo with a `main` branch."""
         self.approved()
-        target = self.tmp / "target"
-        target.mkdir()
-        for argv in (["init", "-q", "-b", "main"],
-                     ["-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q", "--allow-empty", "-m", "init"]):
-            subprocess.run(["git", "-C", str(target), *argv], check=True, capture_output=True)
+        target = git_repo(self.tmp / "target")
         self.env.update({"FACTORY_REPO": str(target), "FACTORY_INTEGRATION_BRANCH": "main"})
         plan = self.tmp / "plan.md"
         plan.write_text("T-0001.1 / Do it\nDepends on: none\nParallel-safe: yes\n")
diff --git a/tests/factory/test_run_scratch.py b/tests/factory/test_run_scratch.py
index 6d7d970..6d83542 100644
--- a/tests/factory/test_run_scratch.py
+++ b/tests/factory/test_run_scratch.py
@@ -8,20 +8,19 @@ fixture instance, like test_run_isolation.py.
 """
 from __future__ import annotations
 
-import json
 import os
 import re
 import subprocess
 from pathlib import Path
 
-from ._cli import BIN, REPO
+from ._cli import REPO, CliStore
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 PRECEDENCE = "takes precedence over any other instruction to use a session scratchpad"
 ACCEPT = "Type: bug\nTitle: A\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"
 
 
-class Store:
+class Store(CliStore):
     def __init__(self, tmp_path: Path):
         self.tmp = tmp_path
         self.root = tmp_path / "state"
@@ -29,14 +28,6 @@ class Store:
                     "PYTHONDONTWRITEBYTECODE": "1"}
         self.n = 0
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def request(self) -> str:
         self.n += 1
         p = self.tmp / f"req{self.n}.md"
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index 239aaf9..683def4 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -19,7 +19,7 @@ from pathlib import Path
 
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import BIN, REPO, CliStore
 
 STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
 MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec
@@ -595,7 +595,7 @@ class Run:
         self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status
 
 
-class Shepherd:
+class Shepherd(CliStore):
     def __init__(self, tmp_path: Path, case: str, with_repo: bool = False):
         self.store = tmp_path / "state"
         self.case = case
@@ -629,11 +629,6 @@ class Shepherd:
             env["FACTORY_INTEGRATION_BRANCH"] = "main"
         return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
 
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def ticket(self, tid: str) -> dict:
         return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())
 
diff --git a/tests/factory/test_sibling_tests.py b/tests/factory/test_sibling_tests.py
index 19898a1..67ce52c 100644
--- a/tests/factory/test_sibling_tests.py
+++ b/tests/factory/test_sibling_tests.py
@@ -20,7 +20,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import REPO, CliStore, approved_parent
 
 PLAN = """ST-1 / Interim
 Depends on: none
@@ -55,7 +55,7 @@ await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STA
 """
 
 
-class Fixture:
+class Fixture(CliStore):
     def __init__(self, tmp_path: Path):
         self.tmp = tmp_path
         self.store = tmp_path / "store"
@@ -63,14 +63,6 @@ class Fixture:
         self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
                     "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def git(self, *argv: str) -> str:
         cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=self.target,
                             capture_output=True, text=True, check=True)
@@ -109,11 +101,7 @@ def build(tmp_path: Path, path: str, merged: bool = True, readd: bool = False, p
     req.write_text("# Fixture\n\nThe bot should do the thing.\n")
     spec.write_text("## Problem\nx\n")
     f.ok("ticket", "new", "--file", str(req))
-    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-    f.ok("spec", "add", "T-0001", "--file", str(spec))
-    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-    f.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-    f.ok("approve-spec", "T-0001")
+    approved_parent(f.ok, "T-0001", spec)
     subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
     base = f.commit("base", test_old="def test_old(): pass\n")
     f.git("checkout", "-qb", "sib")
diff --git a/tests/factory/test_spec_amend.py b/tests/factory/test_spec_amend.py
index 08e9d4f..27f1bda 100644
--- a/tests/factory/test_spec_amend.py
+++ b/tests/factory/test_spec_amend.py
@@ -18,7 +18,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import REPO, CliStore, approved_parent  # noqa: F401  (test_spec_drift.py imports REPO from here)
 
 SPEC = """=== proposal.md
 ## Problem
@@ -55,7 +55,7 @@ def spec(decision="Greet by default.", cmd="echo hi", out="hi", problem="x", sta
 V1, V2 = spec(), spec(cmd="echo hello", out="hello")
 
 
-class Fixture:
+class Fixture(CliStore):
     def __init__(self, tmp_path: Path):
         self.tmp = tmp_path
         self.store = tmp_path / "store"
@@ -63,14 +63,6 @@ class Fixture:
         self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
                     "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def file(self, name: str, text: str) -> str:
         p = self.tmp / name
         p.write_text(text)
@@ -107,11 +99,7 @@ def f(tmp_path: Path) -> Fixture:
                    check=True)
     f.ok("init")
     f.ok("ticket", "new", "--file", f.file("req.md", "# Fixture\n\nGreet.\n"))
-    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
-    f.ok("spec", "add", "T-0001", "--file", f.file("v1.md", V1))
-    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
-    f.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
-    f.ok("approve-spec", "T-0001")
+    approved_parent(f.ok, "T-0001", f.file("v1.md", V1))
     return f
 
 
diff --git a/tests/factory/test_store_setup.py b/tests/factory/test_store_setup.py
index 84b68ff..cb1b8ae 100644
--- a/tests/factory/test_store_setup.py
+++ b/tests/factory/test_store_setup.py
@@ -18,7 +18,7 @@ import shutil
 import subprocess
 from pathlib import Path
 
-from ._cli import BIN, REPO, STRIP
+from ._cli import BIN, REPO, STRIP, git_repo
 from ._cli import js_ok as js
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
@@ -37,13 +37,6 @@ def git(repo: Path, *argv: str) -> subprocess.CompletedProcess:
                           capture_output=True, text=True)
 
 
-def git_repo(path: Path) -> Path:
-    path.mkdir(parents=True, exist_ok=True)
-    assert git(path, "init", "-q", "-b", "main").returncode == 0
-    assert git(path, "commit", "-q", "--allow-empty", "-m", "init").returncode == 0
-    return path
-
-
 def commit_all(repo: Path, msg: str) -> None:
     assert git(repo, "add", "-A").returncode == 0
     assert git(repo, "commit", "-q", "-m", msg).returncode == 0
diff --git a/tests/factory/test_subtickets.py b/tests/factory/test_subtickets.py
index 9c06468..5dfd2d0 100644
--- a/tests/factory/test_subtickets.py
+++ b/tests/factory/test_subtickets.py
@@ -6,7 +6,7 @@ from pathlib import Path
 
 import yaml
 
-from ._cli import REPO, run, ticket
+from ._cli import REPO, approved_parent, run, ticket
 from ._cli import js_ok as js
 
 PLAN_LETTERS = """# Plan — T-0001: alert the operator
@@ -71,11 +71,7 @@ def planned_parent(store: Path, tmp_path: Path, n: int, plan: str) -> str:
     tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
     spec = tmp_path / f"s{n}.md"
     spec.write_text("## Problem\nx\n")
-    js(run(store, "ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(store, "spec", "add", tid, "--file", str(spec)))
-    js(run(store, "ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(store, "ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(store, "approve-spec", tid))
+    approved_parent(lambda *a: js(run(store, *a)), tid, spec)
     rid = js(run(store, "run", "start", "--role", "planner", "--ticket", tid))["run_id"]
     js(run(store, "run", "compose", rid))
     (store / "runs" / rid / "output.md").write_text(plan)
@@ -143,11 +139,7 @@ def test_subticket_add_refuses_a_plan_with_no_sub_tickets_and_a_dependency_on_no
     js(run(store, "ticket", "new", "--file", str(req)))
     spec = tmp_path / "s.md"
     spec.write_text("## Problem\nx\n")
-    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(store, "spec", "add", "T-0001", "--file", str(spec)))
-    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(store, "approve-spec", "T-0001"))
+    approved_parent(lambda *a: js(run(store, *a)), "T-0001", spec)
     f = tmp_path / "p.md"
     f.write_text("# Plan\nno sub-tickets here\n")
     cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
@@ -177,11 +169,7 @@ def test_a_bullet_that_names_a_sub_ticket_is_not_a_head_and_a_repeated_id_is_ref
     spec = tmp_path / "s.md"
     spec.write_text("## Problem\nx\n")
     js(run(store, "ticket", "new", "--file", str(req)))
-    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(store, "spec", "add", "T-0001", "--file", str(spec)))
-    js(run(store, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(store, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(store, "approve-spec", "T-0001"))
+    approved_parent(lambda *a: js(run(store, *a)), "T-0001", spec)
     cp = run(store, "subticket", "add", "T-0001", "--file", str(f))
     assert cp.returncode == 2 and "used more than once" in cp.stderr
     import importlib.util
diff --git a/tests/factory/test_superseded_plan.py b/tests/factory/test_superseded_plan.py
index ce0a9e1..dec879d 100644
--- a/tests/factory/test_superseded_plan.py
+++ b/tests/factory/test_superseded_plan.py
@@ -15,7 +15,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import run, ticket
+from ._cli import approved_parent, run, ticket
 from ._cli import js_ok as js
 
 OLD_PLAN = ("ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\n"
@@ -42,11 +42,7 @@ def store(tmp_path: Path) -> Path:
     (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
     (tmp_path / "spec.md").write_text("## Problem\nx\n")
     js(run(s, "ticket", "new", "--file", str(tmp_path / "req.md")))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t"))
-    js(run(s, "spec", "add", "T-0001", "--file", str(tmp_path / "spec.md")))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
-    js(run(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t"))
-    js(run(s, "approve-spec", "T-0001"))
+    approved_parent(lambda *a: js(run(s, *a)), "T-0001", tmp_path / "spec.md")
     return s
 
 
diff --git a/tests/factory/test_tripwire.py b/tests/factory/test_tripwire.py
index 2dc3326..e9ae556 100644
--- a/tests/factory/test_tripwire.py
+++ b/tests/factory/test_tripwire.py
@@ -19,14 +19,14 @@ import subprocess
 import uuid
 from pathlib import Path
 
-from ._cli import BIN, REPO
+from ._cli import CliStore
 
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 SECRET = '{"token": "TRIPWIRE-SECRET-A"}\n'
 OUT = "Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"
 
 
-class Inst:
+class Inst(CliStore):
     """A scratch instance and store with ticket T-0001 ready for triage. `tripwire` is the YAML
     text appended to the instance (None: no key)."""
 
@@ -45,14 +45,6 @@ class Inst:
         self.ok("ticket", "new", "--file", str(req))
         (tmp_path / "out.md").write_text(OUT)
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, cp.stderr
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def start(self) -> str:
         return self.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
 
diff --git a/tests/factory/test_turn_economy.py b/tests/factory/test_turn_economy.py
index 69422eb..54787df 100644
--- a/tests/factory/test_turn_economy.py
+++ b/tests/factory/test_turn_economy.py
@@ -15,7 +15,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import BIN, REPO, STRIP
+from ._cli import BIN, REPO, STRIP, git_repo
 
 FENCE = "`" * 3
 
@@ -87,11 +87,7 @@ def run_prompts(tmp_path_factory) -> dict[str, str]:
     scratch target with a throwaway store (FACTORY_STATE). `ticket set` gives the ticket the status
     each role starts from."""
     tmp = tmp_path_factory.mktemp("economy")
-    t = tmp / "target"
-    t.mkdir()
-    for argv in (["init", "-q", "-b", "main"],
-                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
-        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
+    t = git_repo(tmp / "target")
     req = tmp / "r.md"
     req.write_text("# demo\n\nDo the thing.\n")
     store = {"FACTORY_STATE": str(tmp / "s")}
diff --git a/tests/factory/test_whole_spec_plan.py b/tests/factory/test_whole_spec_plan.py
index 3059676..f644648 100644
--- a/tests/factory/test_whole_spec_plan.py
+++ b/tests/factory/test_whole_spec_plan.py
@@ -14,13 +14,12 @@ from __future__ import annotations
 import json
 import os
 import shutil
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-from ._cli import BIN, REPO
+from ._cli import CliStore, git_repo
 from .test_parent_close_reuse import _build, _parent_verifier_runs
 from .test_shepherd import Shepherd
 
@@ -52,7 +51,7 @@ ESCALATIONS: none
 """
 
 
-class Parent:
+class Parent(CliStore):
     """T-0001 at ready-for-planner: one spec-writer run ending `status`, its output approved as v1."""
 
     def __init__(self, tmp_path: Path, status: str = "READY-FOR-CRITIC", extra: str = "", spec_store: bool = False):
@@ -61,9 +60,7 @@ class Parent:
         repo = tmp_path / "t"
         self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(repo),
                     "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
-        subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
-        subprocess.run(["git", "-C", str(repo), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-q",
-                        "--allow-empty", "-m", "init"], check=True)
+        git_repo(repo)
         if spec_store:
             self.ok("init")
         (tmp_path / "req.md").write_text("# F\n\nDo x.\n")
@@ -77,14 +74,6 @@ class Parent:
         self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
         self.ok("approve-spec", "T-0001")
 
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
-
-    def ok(self, *argv: str) -> dict:
-        cp = self.cli(*argv)
-        assert cp.returncode == 0, f"{' '.join(argv)}: {cp.stderr}"
-        return json.loads(cp.stdout.strip().splitlines()[-1])
-
     def tickets(self) -> list[str]:
         return sorted(p.name for p in (self.root / "tickets").iterdir())
 
diff --git a/tests/factory/test_writing_standard.py b/tests/factory/test_writing_standard.py
index a690b1f..245bd42 100644
--- a/tests/factory/test_writing_standard.py
+++ b/tests/factory/test_writing_standard.py
@@ -14,7 +14,7 @@ from pathlib import Path
 
 import pytest
 
-from ._cli import BIN, REPO, STRIP
+from ._cli import BIN, REPO, STRIP, git_repo
 
 STANDARD = REPO.resolve() / "docs" / "writing.md"
 FENCE = "`" * 3
@@ -30,11 +30,7 @@ def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
 def system_prompt(tmp_path: Path) -> str:
     """The system prompt of one triage run started in a fresh scratch target, on a throwaway store
     (FACTORY_STATE) as in the spec's scenario, so it does not depend on a clean harness checkout."""
-    t = tmp_path / "target"
-    t.mkdir()
-    for argv in (["init", "-q", "-b", "main"],
-                 ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "init"]):
-        subprocess.run(["git", "-C", str(t), *argv], check=True, capture_output=True)
+    t = git_repo(tmp_path / "target")
     req = tmp_path / "r.md"
     req.write_text("# demo\n\nDo the thing.\n")
     store = tmp_path / "s"
