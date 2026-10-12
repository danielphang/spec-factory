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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0462-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0462-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0462-reviewer/wt` (branch `factory/T-0045.1`, base `2b9baf506852d6f74124b1f5eadbdd84f6bad52b`, head `3478d1fddf4b207fdf0a04ba34ae5459ec11968c`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0045.1

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

## Diff `2b9baf506852d6f74124b1f5eadbdd84f6bad52b...3478d1fddf4b207fdf0a04ba34ae5459ec11968c`

diff --git a/tests/factory/_cli.py b/tests/factory/_cli.py
new file mode 100644
index 0000000..bcc3213
--- /dev/null
+++ b/tests/factory/_cli.py
@@ -0,0 +1,56 @@
+"""Helpers the harness suite shares: where the repository and `bin/factory` are, the wrappers that
+call it, the JSON readers and the ticket reader. A test file imports them from here, never from
+another test file. Not named `test_*`, so pytest does not collect it.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
+STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD",
+         "FACTORY_DISPATCH")
+
+
+def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
+    # init and paths are exempt from the harness lock and keep exercising bin/factory's own hand-over
+    # of the caller's directory; every other command runs the launcher that stubs only the
+    # uncommitted-edit refusal (design C.4), so the suite runs in a checkout with an uncommitted edit.
+    cmd = [str(BIN)] if argv[:1] in (("init",), ("paths",)) else [sys.executable, str(CLEAN_CLI)]
+    return subprocess.run([*cmd, *argv], capture_output=True, text=True, env=env, cwd=cwd)
+
+
+def run(store: Path, *argv: str, stdin: str | None = None) -> subprocess.CompletedProcess:
+    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO, input=stdin)
+
+
+def run_env(env: dict, *argv: str) -> subprocess.CompletedProcess:
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
+                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)
+
+
+def js(cp: subprocess.CompletedProcess) -> dict:
+    return json.loads(cp.stdout.strip().splitlines()[-1])
+
+
+def js_ok(cp: subprocess.CompletedProcess) -> dict:
+    assert cp.returncode == 0, cp.stderr
+    return js(cp)
+
+
+def ticket(store: Path, tid: str = "T-0001") -> dict:
+    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
+
+
+def tree(path: Path) -> dict[str, bytes]:
+    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
diff --git a/tests/factory/conftest.py b/tests/factory/conftest.py
index c7450df..b30619e 100644
--- a/tests/factory/conftest.py
+++ b/tests/factory/conftest.py
@@ -11,8 +11,12 @@ subprocess environment (the shepherd's scratch target) still overrides it.
 from __future__ import annotations
 
 import os
+import sys
 from pathlib import Path
 
 _HERE = Path(__file__).resolve()
 os.environ["FACTORY_INSTANCE"] = str(_HERE.parent / "fixtures" / "instance")
 os.environ.setdefault("FACTORY_REPO", str(_HERE.parents[2]))
+# No .pyc in the checkout: the variable covers every Python subprocess, the flag in-process importlib loads.
+os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
+sys.dont_write_bytecode = True
diff --git a/tests/factory/test_capability_index.py b/tests/factory/test_capability_index.py
index 9ac00dd..7f540f1 100644
--- a/tests/factory/test_capability_index.py
+++ b/tests/factory/test_capability_index.py
@@ -9,15 +9,13 @@ decision often names no capability. Black-box through `bin/factory`.
 """
 from __future__ import annotations
 
-import os
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import REPO, run
+
 CAPS = ("alpha", "beta", "gamma")
 SPEC = "\n".join([
     "=== proposal.md", "## Problem", "Beta is lax.", "## Evidence", "Read `openspec/specs/gamma/spec.md`.",
@@ -27,11 +25,6 @@ SPEC = "\n".join([
     "=== verification.md", "## Acceptance", "- strict → NEW; today lax", ""])
 
 
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-
 def ok(store: Path, *argv: str) -> str:
     cp = run(store, *argv)
     assert cp.returncode == 0, cp.stderr
diff --git a/tests/factory/test_coding_standard.py b/tests/factory/test_coding_standard.py
index f063b93..33c1067 100644
--- a/tests/factory/test_coding_standard.py
+++ b/tests/factory/test_coding_standard.py
@@ -15,10 +15,9 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO, STRIP
+
 STANDARD = REPO.resolve() / "docs" / "coding.md"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
 FENCE = "`" * 3
 
 
diff --git a/tests/factory/test_critic_approved_changes.py b/tests/factory/test_critic_approved_changes.py
index 6eed6a3..9a6cac6 100644
--- a/tests/factory/test_critic_approved_changes.py
+++ b/tests/factory/test_critic_approved_changes.py
@@ -15,8 +15,8 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 HEADING = "## Approved changes not yet archived"
 
 
diff --git a/tests/factory/test_decision_log.py b/tests/factory/test_decision_log.py
index 87b541b..fd49661 100644
--- a/tests/factory/test_decision_log.py
+++ b/tests/factory/test_decision_log.py
@@ -8,26 +8,15 @@ from __future__ import annotations
 
 import datetime as dt
 import json
-import os
 import re
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-FENCE = "`" * 3
-
-
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
+from ._cli import REPO, js, run, ticket
 
-def js(cp):
-    return json.loads(cp.stdout.strip().splitlines()[-1])
+FENCE = "`" * 3
 
 
 def today() -> str:
@@ -47,10 +36,6 @@ def events(store: Path, name: str) -> list[dict]:
     return [json.loads(ln) for ln in run(store, "log", "tail", "-n", "200", "--event", name).stdout.splitlines()]
 
 
-def ticket(store: Path) -> dict:
-    return yaml.safe_load((store / "tickets" / "T-0001.yaml").read_text())
-
-
 @pytest.fixture
 def store(tmp_path: Path) -> Path:
     s = tmp_path / "state"
diff --git a/tests/factory/test_drive.py b/tests/factory/test_drive.py
index d8b2ddf..726c849 100644
--- a/tests/factory/test_drive.py
+++ b/tests/factory/test_drive.py
@@ -21,8 +21,8 @@ from pathlib import Path
 
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 
 STANDIN = '''#!{python}
diff --git a/tests/factory/test_empty_output.py b/tests/factory/test_empty_output.py
index ea97fd2..0323f1b 100644
--- a/tests/factory/test_empty_output.py
+++ b/tests/factory/test_empty_output.py
@@ -15,8 +15,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
 
 
 class Store:
diff --git a/tests/factory/test_environment_sync.py b/tests/factory/test_environment_sync.py
index ca2ec2f..0fd1728 100644
--- a/tests/factory/test_environment_sync.py
+++ b/tests/factory/test_environment_sync.py
@@ -17,8 +17,8 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 GIT_ID = {"GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@x", "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@x"}
 DUMP = "env > synced.env"  # a sync that records the environment it ran in
diff --git a/tests/factory/test_gate_paths.py b/tests/factory/test_gate_paths.py
index 3323b29..3da0926 100644
--- a/tests/factory/test_gate_paths.py
+++ b/tests/factory/test_gate_paths.py
@@ -19,8 +19,8 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 UNSCOPED = "git diff --check main...HEAD"
 SCOPED = "sh -c 'exit 7'"
diff --git a/tests/factory/test_harness_lock.py b/tests/factory/test_harness_lock.py
index 8285c74..f1de71e 100644
--- a/tests/factory/test_harness_lock.py
+++ b/tests/factory/test_harness_lock.py
@@ -24,9 +24,8 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+from ._cli import CLEAN_CLI, REPO, STRIP, js, tree
+
 HARNESS_PATHS = ("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")
 ZERO = "0" * 40
 
@@ -61,14 +60,6 @@ def revision(harness: Path) -> str:
     return git(harness, "log", "-1", "--format=%H", "--", *HARNESS_PATHS).strip()
 
 
-def tree(path: Path) -> dict[str, bytes]:
-    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
-
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
 def make_target(path: Path, harness: Path) -> Path:
     path.mkdir(parents=True)
     git(path, "init", "-q", "-b", "main")
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
index 39a1083..c444cbd 100644
--- a/tests/factory/test_instance.py
+++ b/tests/factory/test_instance.py
@@ -6,35 +6,16 @@ harness resolves the instance the way it does for an operator: from the working
 """
 from __future__ import annotations
 
-import json
 import os
 import subprocess
-import sys
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD",
-         "FACTORY_DISPATCH")
-NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
-
-
-def cli(cwd: Path, *argv: str, **extra: str) -> subprocess.CompletedProcess:
-    env = {k: v for k, v in os.environ.items() if k not in STRIP}
-    env.update({"PYTHONDONTWRITEBYTECODE": "1", **extra})
-    # init and paths are exempt from the harness lock and keep exercising bin/factory's own hand-over
-    # of the caller's directory; every other command runs the launcher that stubs only the
-    # uncommitted-edit refusal (design C.4), so the suite runs in a checkout with an uncommitted edit.
-    cmd = [str(BIN)] if argv[:1] in (("init",), ("paths",)) else [sys.executable, str(CLEAN_CLI)]
-    return subprocess.run([*cmd, *argv], capture_output=True, text=True, env=env, cwd=cwd)
+from ._cli import BIN, REPO, STRIP, cli, js, tree
 
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    return json.loads(cp.stdout.strip().splitlines()[-1])
+NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
 
 
 def git_repo(path: Path) -> Path:
@@ -45,10 +26,6 @@ def git_repo(path: Path) -> Path:
     return path
 
 
-def tree(path: Path) -> dict[str, bytes]:
-    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}
-
-
 def harness_status() -> str:
     return subprocess.run(["git", "-C", str(REPO), "status", "--porcelain"], capture_output=True, text=True).stdout
 
diff --git a/tests/factory/test_merge_protected_paths.py b/tests/factory/test_merge_protected_paths.py
index 0e87552..2407455 100644
--- a/tests/factory/test_merge_protected_paths.py
+++ b/tests/factory/test_merge_protected_paths.py
@@ -22,8 +22,8 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE = REPO / "tests" / "factory" / "fixtures" / "instance"
 
 # Drives factory/workflows/build.js with a stub clerk: each command gets the reply of the longest key
diff --git a/tests/factory/test_p0_cli.py b/tests/factory/test_p0_cli.py
index 4c3f14d..04b65a8 100644
--- a/tests/factory/test_p0_cli.py
+++ b/tests/factory/test_p0_cli.py
@@ -4,31 +4,13 @@ Black-box through `bin/factory`, as the P0 acceptance items are written.
 """
 from __future__ import annotations
 
-import json
-import os
-import subprocess
 import sys
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-
-
-def run(store: Path, *argv: str, stdin: str | None = None) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO, input=stdin)
-
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
-def ticket(store: Path, tid: str) -> dict:
-    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
-
+from ._cli import REPO, js, run, ticket  # noqa: F401  (test_role_inputs.py imports REPO from here)
 
 TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
 
@@ -115,15 +97,6 @@ def test_run_compose_then_finish_parses_status_and_clears_in_flight(store, req):
     assert t["in_flight"] == [] and t["title"] == "Do the thing" and t["type"] == "feature"
 
 
-def test_run_finish_without_output_is_killed(store, req):
-    run(store, "ticket", "new", "--file", str(req))
-    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
-    run(store, "run", "compose", rid)
-    cp = run(store, "run", "finish", rid, "--status-override", "KILLED")
-    assert cp.returncode == 0 and js(cp)["status"] == "KILLED"
-    assert yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())["status"] == "KILLED"
-
-
 def test_status_parse_last_status_line_wins_and_needs_both_followers(tmp_path, store):
     p = tmp_path / "m.md"
     p.write_text("body\nSTATUS: APPROVE\nmore\nSTATUS: REVISE\nCONFIDENCE: high, ok\nESCALATIONS:\n- one\n- two\n")
diff --git a/tests/factory/test_redispatch_rows.py b/tests/factory/test_redispatch_rows.py
index a877f54..84db4ab 100644
--- a/tests/factory/test_redispatch_rows.py
+++ b/tests/factory/test_redispatch_rows.py
@@ -11,28 +11,17 @@ Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_re
 from __future__ import annotations
 
 import json
-import os
-import subprocess
 from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import js_ok as js
+from ._cli import run_env as run
+
 HEAD = "ab" * 20
 ST = "T-0001.1"
 
 
-def run(env: dict, *argv: str) -> subprocess.CompletedProcess:
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
-                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)
-
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
 @pytest.fixture
 def env(tmp_path: Path) -> dict:
     """A scratch store: T-0001 approved and split into T-0001.1, which is in its checks on HEAD."""
diff --git a/tests/factory/test_replan.py b/tests/factory/test_replan.py
index adf55e1..63773e2 100644
--- a/tests/factory/test_replan.py
+++ b/tests/factory/test_replan.py
@@ -9,35 +9,20 @@ Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_de
 """
 from __future__ import annotations
 
-import json
-import os
 import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import run, ticket
+from ._cli import js_ok as js
+
 NOTE = "Re-plan: add one fix for the case-insensitive path.\n"
 SECTION = "## Sub-tickets already under T-0001"
 FIRST_PLAN = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n"
 
 
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
-def ticket(store: Path, tid: str) -> dict:
-    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
-
-
 def files(d: Path) -> list[str]:
     return sorted(str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()) if d.exists() else []
 
diff --git a/tests/factory/test_request_frontmatter.py b/tests/factory/test_request_frontmatter.py
index b665887..e7b6830 100644
--- a/tests/factory/test_request_frontmatter.py
+++ b/tests/factory/test_request_frontmatter.py
@@ -8,20 +8,12 @@ silently and only failed later, in an editor's preview.
 from __future__ import annotations
 
 import json
-import os
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-
-
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+from ._cli import run
 
 
 @pytest.fixture
diff --git a/tests/factory/test_resolve_rulings.py b/tests/factory/test_resolve_rulings.py
index 7299488..4666127 100644
--- a/tests/factory/test_resolve_rulings.py
+++ b/tests/factory/test_resolve_rulings.py
@@ -6,31 +6,16 @@ Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_de
 """
 from __future__ import annotations
 
-import json
-import os
 import subprocess
 from pathlib import Path
 
 import pytest
-import yaml
-
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-RULING = "Ruling: take the second approach.\n"
-
-
-def run(env: dict, *argv: str) -> subprocess.CompletedProcess:
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True,
-                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **env}, cwd=REPO)
 
+from ._cli import ticket
+from ._cli import js_ok as js
+from ._cli import run_env as run
 
-def js(cp: subprocess.CompletedProcess) -> dict:
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
-def ticket(store: Path, tid: str) -> dict:
-    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
+RULING = "Ruling: take the second approach.\n"
 
 
 @pytest.fixture
diff --git a/tests/factory/test_results_commit.py b/tests/factory/test_results_commit.py
index 0908d58..3c2bb4f 100644
--- a/tests/factory/test_results_commit.py
+++ b/tests/factory/test_results_commit.py
@@ -15,8 +15,8 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 HEAD = "0" * 40
 REVIEWER_TAIL = "Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n"
 VERIFIER_TAIL = "Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n"
diff --git a/tests/factory/test_run_isolation.py b/tests/factory/test_run_isolation.py
index c3b41f1..b8e0dd7 100644
--- a/tests/factory/test_run_isolation.py
+++ b/tests/factory/test_run_isolation.py
@@ -16,8 +16,8 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
         'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})')
diff --git a/tests/factory/test_run_scratch.py b/tests/factory/test_run_scratch.py
index c5e3667..6d7d970 100644
--- a/tests/factory/test_run_scratch.py
+++ b/tests/factory/test_run_scratch.py
@@ -14,8 +14,8 @@ import re
 import subprocess
 from pathlib import Path
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 PRECEDENCE = "takes precedence over any other instruction to use a session scratchpad"
 ACCEPT = "Type: bug\nTitle: A\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index f50d301..239aaf9 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -19,8 +19,8 @@ from pathlib import Path
 
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
 MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec
 MAX_PR_ROUNDS = 2  # factory/config.yaml max_rounds.pr
diff --git a/tests/factory/test_sibling_tests.py b/tests/factory/test_sibling_tests.py
index a66bfff..19898a1 100644
--- a/tests/factory/test_sibling_tests.py
+++ b/tests/factory/test_sibling_tests.py
@@ -20,8 +20,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
 
 PLAN = """ST-1 / Interim
 Depends on: none
diff --git a/tests/factory/test_spec_amend.py b/tests/factory/test_spec_amend.py
index c7332f0..08e9d4f 100644
--- a/tests/factory/test_spec_amend.py
+++ b/tests/factory/test_spec_amend.py
@@ -18,8 +18,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
 
 SPEC = """=== proposal.md
 ## Problem
diff --git a/tests/factory/test_spec_store.py b/tests/factory/test_spec_store.py
index c7d933d..060a7ee 100644
--- a/tests/factory/test_spec_store.py
+++ b/tests/factory/test_spec_store.py
@@ -2,26 +2,14 @@
 compose additions from spec-factory T-0003 and T-0008, black-box through `bin/factory`."""
 from __future__ import annotations
 
-import json
-import os
-import subprocess
 from pathlib import Path
 
 import pytest
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
-
-
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+from ._cli import js, run
 
-
-def js(cp):
-    return json.loads(cp.stdout.strip().splitlines()[-1])
+TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
 
 
 def meta(store: Path, rid: str) -> dict:
diff --git a/tests/factory/test_store_setup.py b/tests/factory/test_store_setup.py
index c63b9c1..84b68ff 100644
--- a/tests/factory/test_store_setup.py
+++ b/tests/factory/test_store_setup.py
@@ -13,16 +13,15 @@ exempts (`init`, `paths`), so the file passes in a checkout with an uncommitted
 """
 from __future__ import annotations
 
-import json
 import os
 import shutil
 import subprocess
 from pathlib import Path
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO, STRIP
+from ._cli import js_ok as js
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
 RULE = "runs/** -whitespace"
 
 
@@ -33,11 +32,6 @@ def cli(cwd: Path, *argv: str, **env: str) -> subprocess.CompletedProcess:
     return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=e, cwd=cwd)
 
 
-def js(cp: subprocess.CompletedProcess) -> dict:
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
 def git(repo: Path, *argv: str) -> subprocess.CompletedProcess:
     return subprocess.run(["git", "-C", str(repo), "-c", "user.email=f@x", "-c", "user.name=f", *argv],
                           capture_output=True, text=True)
diff --git a/tests/factory/test_subtickets.py b/tests/factory/test_subtickets.py
index 728a1c2..9c06468 100644
--- a/tests/factory/test_subtickets.py
+++ b/tests/factory/test_subtickets.py
@@ -2,15 +2,12 @@
 `T-0001-A` or `ST-1` ids, bold field names, shared preludes, and a dependency on another parent."""
 from __future__ import annotations
 
-import json
-import os
-import subprocess
 from pathlib import Path
 
 import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import REPO, run, ticket
+from ._cli import js_ok as js
 
 PLAN_LETTERS = """# Plan — T-0001: alert the operator
 
@@ -67,16 +64,6 @@ ESCALATIONS: none
 """
 
 
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-
-def js(cp):
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
 def planned_parent(store: Path, tmp_path: Path, n: int, plan: str) -> str:
     """A parent ticket approved (old-format spec; no spec store) with `plan` as its planner output."""
     req = tmp_path / f"r{n}.md"
@@ -99,10 +86,6 @@ def planned_parent(store: Path, tmp_path: Path, n: int, plan: str) -> str:
     return tid, subs
 
 
-def ticket(store: Path, tid: str) -> dict:
-    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
-
-
 def test_lettered_ids_become_numbered_sub_tickets_in_plan_order(tmp_path):
     store = tmp_path / "state"
     tid, subs = planned_parent(store, tmp_path, 21, PLAN_LETTERS)
diff --git a/tests/factory/test_superseded_plan.py b/tests/factory/test_superseded_plan.py
index c6ab61d..ce0a9e1 100644
--- a/tests/factory/test_superseded_plan.py
+++ b/tests/factory/test_superseded_plan.py
@@ -10,15 +10,14 @@ Black-box through `bin/factory` on a throwaway store (FACTORY_STATE), as test_re
 from __future__ import annotations
 
 import json
-import os
 import subprocess
 from pathlib import Path
 
 import pytest
-import yaml
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import run, ticket
+from ._cli import js_ok as js
+
 OLD_PLAN = ("ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\n"
             "ST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n")
 NEW_PLAN = "ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n"
@@ -26,20 +25,6 @@ SUPERSEDES_LINE = ("Not merged and planned from an earlier approved version, so
                    "not depend on them: T-0001.2, T-0001.3")
 
 
-def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
-    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
-    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-
-def js(cp: subprocess.CompletedProcess) -> dict:
-    assert cp.returncode == 0, cp.stderr
-    return json.loads(cp.stdout.strip().splitlines()[-1])
-
-
-def ticket(store: Path, tid: str) -> dict:
-    return yaml.safe_load((store / "tickets" / f"{tid}.yaml").read_text())
-
-
 def add_plan(store: Path, tmp_path: Path, text: str, name: str) -> subprocess.CompletedProcess:
     (tmp_path / name).write_text(text)
     return run(store, "subticket", "add", "T-0001", "--file", str(tmp_path / name))
diff --git a/tests/factory/test_tripwire.py b/tests/factory/test_tripwire.py
index 9968c83..2dc3326 100644
--- a/tests/factory/test_tripwire.py
+++ b/tests/factory/test_tripwire.py
@@ -19,8 +19,8 @@ import subprocess
 import uuid
 from pathlib import Path
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO
+
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 SECRET = '{"token": "TRIPWIRE-SECRET-A"}\n'
 OUT = "Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"
diff --git a/tests/factory/test_turn_economy.py b/tests/factory/test_turn_economy.py
index 5205fe0..69422eb 100644
--- a/tests/factory/test_turn_economy.py
+++ b/tests/factory/test_turn_economy.py
@@ -15,9 +15,8 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+from ._cli import BIN, REPO, STRIP
+
 FENCE = "`" * 3
 
 BULLET = [
diff --git a/tests/factory/test_whole_spec_plan.py b/tests/factory/test_whole_spec_plan.py
index 7f0939e..3059676 100644
--- a/tests/factory/test_whole_spec_plan.py
+++ b/tests/factory/test_whole_spec_plan.py
@@ -20,11 +20,10 @@ from pathlib import Path
 import pytest
 import yaml
 
+from ._cli import BIN, REPO
 from .test_parent_close_reuse import _build, _parent_verifier_runs
 from .test_shepherd import Shepherd
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
 REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
 SPEC_WRITER_OUTPUT = """=== proposal.md
 ## Problem
diff --git a/tests/factory/test_writing_standard.py b/tests/factory/test_writing_standard.py
index ebdc8cf..a690b1f 100644
--- a/tests/factory/test_writing_standard.py
+++ b/tests/factory/test_writing_standard.py
@@ -14,10 +14,9 @@ from pathlib import Path
 
 import pytest
 
-REPO = Path(__file__).resolve().parents[2]
-BIN = REPO / "bin" / "factory"
+from ._cli import BIN, REPO, STRIP
+
 STANDARD = REPO.resolve() / "docs" / "writing.md"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
 FENCE = "`" * 3
