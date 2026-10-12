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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0472-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0472-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0472-reviewer/wt` (branch `factory/T-0045.3`, base `1c5a1527f4c1b12b4f24ddb2aca0bfcac0ecfc52`, head `c8308f2ba30e01db463ee09dff27b778e8819b39`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0045.3

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

Sub-ticket: T-0045.3 (ST-3, part D of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0045/v2.md`). Branch `factory/T-0045.3`, commit `c8308f2` on base `1c5a152`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0045.3`.

## What changed

No test file in the harness suite imports from another test file now. A scenario fixture that more than one test file uses lives in one place, `tests/factory/_fixtures.py`. The harness itself does not change. The suite passes at 576 tests in a fresh clone.

**Part D, item 1: new `tests/factory/_fixtures.py`, 655 lines.**
- It holds every name in design.md's D table. Each body is copied byte for byte. I checked this by searching `_fixtures.py` for each original line range read from `git show HEAD:…`. The three ranges that do not match are the two renames below and `test_store_branch.py`'s `state`. That `state` was dropped because the copy from `test_live_store_guard.py` is identical and kept.
- The only import a moved body needs is `from ._cli import BIN, REPO, CliStore, approved_parent, cli, git_repo, js, tree`.
- No test function moved.
- The moved bodies also need some module-level names the table does not list, so those moved too, unchanged:
  - from `test_spec_amend.py`: `SPEC`, `TWO` and `spec`, which `Fixture`, `V1` and `V2` use;
  - from `test_drive.py`: `FIXTURE_INSTANCE`, which is `Store`'s default;
  - from `test_shepherd.py`: `STUBS`, `MAX_SPEC_ROUNDS` and `Run`, which `Shepherd` uses;
  - from `test_live_store_guard.py`: `RULE`, which `assert_refused` uses;
  - from `test_drive_build.py`: its stand-in `claude` script, which `BuildStore` uses.
- `test_drive_guard.py` also imported `assert_refused` and `request` from `test_live_store_guard.py`. The D table misses these two. The spec's rule says every name one test file imports from another moves, so they moved too.
- Two pairs of names would clash inside the single module. Each clash is fixed with one rename in `_fixtures.py`. Both are listed under ESCALATIONS:
  - `test_drive.py` and `test_drive_build.py` each define a different `STANDIN`, and both `Store` and `BuildStore` refer to the module-level name. The build one is now `BUILD_STANDIN`. This changes one token in `BuildStore`'s body: `write_text(STANDIN.format(` became `write_text(BUILD_STANDIN.format(`.
  - `test_store_branch.py` and `test_live_store_guard.py` each define a different `request`: one writes `r.md` with "# demo", the other `r2.md` with "# other". The table names the store-branch one, so it keeps the name. The live-store one is `other_request`. Its importers use `from ._fixtures import other_request as request`, so no call site changes.

**Part D, item 2: imports.**
- The files the names came from import them back from `._fixtures`, but only the names they still use:
  - `test_subtickets.py`, `test_build_startup.py`, `test_sibling_tests.py`, `test_spec_amend.py`, `test_spec_drift.py`, `test_drive.py`, `test_drive_build.py`, `test_live_store_guard.py`, `test_store_branch.py`, `test_shepherd.py` and `test_parent_close_reuse.py`.
  - `STANDIN` and `RULE` are no longer used in their old files, so they are not imported back.
- Every importer of another test file now imports from `._fixtures` or `._cli`:
  - `test_build_startup.py`, `test_drift_siblings.py`, `test_drive_build.py`, `test_drive_guard.py`, `test_killed_checker.py`, `test_live_store_guard.py`, `test_parent_close_reuse.py`, `test_plan_fields.py`, `test_role_inputs.py`, `test_spec_drift.py`, `test_stats.py`, `test_store_branch.py`, `test_store_migrate.py` and `test_whole_spec_plan.py`.
- The form of `js` follows the file it came from, as ST-1 left it:
  - `test_build_startup.py` and `test_plan_fields.py` took `js` from `test_subtickets.py`, whose copy asserts exit 0, so they import `js_ok as js`;
  - the importers of `test_instance.py`'s and `test_p0_cli.py`'s `js` import plain `js`.
- `cli as factory_cli` is kept in `test_stats.py`.
- The two `f = test_spec_amend.f` lines, and their `from . import test_spec_amend` imports, are now imports of `f`. The pytest fixtures `f` and `target` are imported with `# noqa: F401`, as before.
- Imports that the move left unused were removed:
  - `os`, `json`, `sys`, `Path` and `pytest` where nothing uses them any more;
  - `CliStore`, `approved_parent` and `git_repo` where only a moved body used them;
  - the `REPO` re-export, with its `noqa` comment, in `test_p0_cli.py` and `test_spec_amend.py`. It existed only for the importers this ticket rewrites.
- `test_instance.py` needed no change: ruff reports every name it imports as used. `test_store_migrate.py`: only its two import lines changed; its in-process CLI code is untouched.
- Two non-import lines changed in `test_shepherd.py`:
  - its docstring said "`Shepherd` at the bottom" and now says "`Shepherd`, in `_fixtures.py`";
  - the section header for the moved `Shepherd` was removed, since nothing followed it any more.

## Acceptance results

All commands ran from the worktree through the fresh-HOME wrapper. Each WHEN was taken verbatim from v2.md by script.

- **NEW: No test file imports from another test file**
  - Before: `cross-test imports: 27`, followed by the 27 sites from `test_build_startup.py:12` to `test_whole_spec_plan.py:24`.
  - After: `cross-test imports: 0`.
- **REGRESSION: The shared constants and wrappers are defined once.** After: `REPO=1 BIN=1 run=1 js=1 ticket=1 git_repo=1 approved_parent=1`.
- **REGRESSION: The approved-parent and empty-repository setups are written once.** After: `approved-parent sequences: 1 _cli.py:73` and `empty-commit repo setups: 1 _cli.py:63`.
- **REGRESSION: Only the duplicate test and its assertions are gone.** After:
  ```
  pair: 3
  removed: 1
  removed tests/factory/test_p0_cli.py::test_run_finish_without_output_is_killed
  added: 0
  missing: 2
  missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert cp.returncode == 0 and js(cp)['status'] == 'KILLED'
  missing test_p0_cli.py::test_run_finish_without_output_is_killed: assert yaml.safe_load((store / 'runs' / rid / 'meta.yaml').read_text())['status'
  ```
  stderr held only `tar: Failed to set default locale`, which the spec says to ignore.
- **REGRESSION: The suite is shorter.** After: `pairs: 3; test lines before: 28728, after: 28510, change: -218`. This sub-ticket's own pair adds 57 lines net (722 insertions, 665 deletions across 21 files): the 655-line `_fixtures.py` plus the import lines.
- **REGRESSION: A suite run in a fresh clone passes and adds nothing to the checkout.** After: `576 passed in 579.03s (0:09:39)`, then `paths changed: 0`, with nothing after it.
- **Gates**, each run exactly as written:
  - `git diff --check main...HEAD`: exit 0, no output;
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 564.68s (0:09:24)`.
- **Extra check, not a gate.** This repo configures no ruff, so I ran `ruff check --isolated --select F,E9,I --line-length 120 tests/factory` with the ruff in `~/dev/nanobot/.venv-test`, before and after.
  - Before: 4 F811 findings, all on the imported `target` fixture in `test_drive_guard.py`.
  - After: no F401, F821 or I001 findings. The remaining F811 findings are the same kind, an imported pytest fixture (`target` or `f`) used as a test argument. There are now more of them because `f` and `target` are imported in more files than before.

## Tests added/changed

- Added `tests/factory/_fixtures.py`. It is a helper module, not a test file: it is not named `test_*`, so pytest does not collect it.
- Changed, each listed under the sub-ticket's "Tests to change":
  - `test_p0_cli.py`, `test_subtickets.py`, `test_sibling_tests.py`, `test_spec_amend.py`, `test_whole_spec_plan.py`, `test_drive.py`, `test_shepherd.py`;
  - `test_build_startup.py`, `test_drive_build.py`, `test_plan_fields.py`, `test_drift_siblings.py`, `test_drive_guard.py`, `test_killed_checker.py`, `test_live_store_guard.py`;
  - `test_parent_close_reuse.py`, `test_role_inputs.py`, `test_spec_drift.py`, `test_stats.py`, `test_store_branch.py`, `test_store_migrate.py`.
- In each of these, only module-level helpers moved out and import lines changed, plus the `test_shepherd.py` docstring line and section header described above. No test function and no assertion changed. The assertion comparison above shows nothing missing except the one test ST-1 removed.
- These files are untouched:
  - `test_instance.py`, including T-0044's lines 109 and 354;
  - `_cli.py` and `conftest.py`;
  - `clean_harness_cli.py`;
  - the four design-block files (`test_writing_standard.py`, `test_coding_standard.py`, `test_turn_economy.py`, `test_decision_log.py`).

## Known gaps and uncertainties

- Two renames in `_fixtures.py` depart from "with the body unchanged": `BUILD_STANDIN` and `other_request`. The first changes one token in `BuildStore`'s body. They cannot be avoided once both members of each clashing pair live in one module. The tests do the same thing as before: the build store still writes the build stand-in, and the live-store tests still write `r2.md`.
- The D table is incomplete. It misses `test_live_store_guard.py`'s `assert_refused` and `request`, and the dependencies listed under item 1. I moved them under the spec's general rule.
- `MAX_PR_ROUNDS` stays in `test_shepherd.py`. Nothing uses it, so it did not move with `MAX_SPEC_ROUNDS`.
- `factory:` markers added: none.

## Out-of-scope observations

- Several moved docstrings still name helpers by their old file, for example `test_drive_build.py`'s "(test_drive.Store)", and "test_instance.STRIP" or "test_instance.cli" in `test_live_store_guard.py` and `test_store_branch.py`. These are prose references to where a helper comes from, so I left them alone. A later de-bloat ticket could update them.
- `test_store_branch.py` keeps its own `RULE`, identical to the one now in `_fixtures.py`. It is not in the D table and no other file imports it.
- `MAX_PR_ROUNDS` in `test_shepherd.py` is never used.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The gates and all six scenarios pass on this commit, and a script confirmed that every moved block except the two renames is a verbatim copy.
ESCALATIONS:
- The spec cannot be met exactly as written. Two pairs of names clash once they share one module: test_drive.py's and test_drive_build.py's `STANDIN`, and test_store_branch.py's and test_live_store_guard.py's `request`. So "body unchanged" cannot hold for both members of each pair. I renamed one of each pair in `_fixtures.py` (`BUILD_STANDIN`, `other_request`). That changes one token in `BuildStore`'s body; the `request` users import the new name under the old one. A human should confirm this small departure, or amend the spec to allow it.
- The spec's D table leaves out names that must move for the cross-test import count to reach 0: test_live_store_guard.py's `assert_refused` and `request`, which test_drive_guard.py imports, and the module-level names the moved bodies depend on. I moved them under the spec's general rule ("Every name a test file imports from another test file today moves into it").

## Diff `1c5a1527f4c1b12b4f24ddb2aca0bfcac0ecfc52...c8308f2ba30e01db463ee09dff27b778e8819b39`

diff --git a/tests/factory/_fixtures.py b/tests/factory/_fixtures.py
new file mode 100644
index 0000000..bc169fc
--- /dev/null
+++ b/tests/factory/_fixtures.py
@@ -0,0 +1,654 @@
+"""Scenario fixtures that more than one file of the harness suite uses: stores, targets and
+shepherds in a known state, with the constants and stand-ins they are built from. A test file
+imports them from here, never from another test file; the generic helpers are in `_cli.py`. Not
+named `test_*`, so pytest does not collect it.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import BIN, REPO, CliStore, approved_parent, cli, git_repo, js, tree
+
+# ----- a plan with lettered sub-tickets (test_subtickets.py) --------------------------------------
+
+PLAN_LETTERS = """# Plan — T-0001: alert the operator
+
+## Grounding for this plan
+Checked on this base.
+
+## Fixture (prelude for every sub-ticket)
+```
+cat > /tmp/fx.py <<'PY'
+## not a heading
+PY
+```
+
+## T-0001-A / Emit the truncation event
+**Depends on:** none. Lands first.
+
+**Parallel-safe:** yes, alongside T-0001-C. The two edit disjoint files.
+
+Scope: A
+
+## T-0001-C / Retire the margin signal
+**Depends on:** none. Lands second, before T-0001-B.
+
+**Parallel-safe:** yes, alongside T-0001-A (disjoint files).
+
+## T-0001-B / Re-anchor the check
+**Depends on:** T-0001-C.
+
+**Parallel-safe:** no. Same file as T-0001-C.
+
+## Coverage map
+- criterion 1 → T-0001-A
+
+## Out-of-scope observations
+none
+STATUS: PLANNED
+CONFIDENCE: high, fixture
+ESCALATIONS: none
+"""
+
+
+# ----- the store's ticket files (test_build_startup.py) -------------------------------------------
+
+def ticket_files(store: Path) -> list[str]:
+    return sorted(p.name for p in (store / "tickets").iterdir())
+
+
+# ----- a driver for build.js (test_sibling_tests.py) ----------------------------------------------
+
+# Drives factory/workflows/build.js on parent T-0001: each clerk command runs for real, each role run
+# returns an empty output (a killed run). Prints each park as `park <id>: <reason>`.
+BUILD_DRIVER = r"""
+import { readFileSync } from 'node:fs'
+import { spawnSync } from 'node:child_process'
+const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
+const agent = async (prompt) => {
+  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
+  if (!m) return ''
+  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
+  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
+}
+const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
+const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
+await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
+  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
+"""
+
+
+# ----- the t0027-amend.sh store fixture (test_spec_amend.py) --------------------------------------
+
+SPEC = """=== proposal.md
+## Problem
+{problem}
+## Decisions
+- {decision}
+=== design.md
+## Proposed change
+Edit `src/greet.py`.
+## Tests to change
+none
+=== specs/demo/spec.md
+## ADDED Requirements
+### Requirement: Greets
+{statement}
+
+#### Scenario: Greeting is printed
+- WHEN `{cmd}`
+- THEN it prints `{out}`
+{extra}=== verification.md
+## Acceptance
+- Greeting is printed → NEW
+{labels}"""
+
+TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n"
+
+
+def spec(decision="Greet by default.", cmd="echo hi", out="hi", problem="x", statement="The tool SHALL greet.",
+         extra="", labels="") -> str:
+    return SPEC.format(decision=decision, cmd=cmd, out=out, problem=problem, statement=statement, extra=extra,
+                       labels=labels)
+
+
+V1, V2 = spec(), spec(cmd="echo hello", out="hello")
+
+
+class Fixture(CliStore):
+    def __init__(self, tmp_path: Path):
+        self.tmp = tmp_path
+        self.store = tmp_path / "store"
+        self.target = tmp_path / "t"
+        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+
+    def file(self, name: str, text: str) -> str:
+        p = self.tmp / name
+        p.write_text(text)
+        return str(p)
+
+    def ticket(self, tid: str) -> dict:
+        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())
+
+    def plan(self, text: str = TWO) -> None:
+        self.ok("subticket", "add", "T-0001", "--file", self.file("plan.md", text))
+        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+
+    def amend(self, text: str, reason: str = "Seed the greeting.", intent: str = "unchanged",
+              tid: str = "T-0001") -> subprocess.CompletedProcess:
+        return self.cli("spec", "amend", tid, "--file", self.file("amend.md", text), "--reason", reason,
+                        "--intent", intent)
+
+    def snapshot(self) -> dict[str, bytes]:
+        return {str(p.relative_to(self.store)): p.read_bytes() for p in sorted(self.store.rglob("*")) if p.is_file()}
+
+    def change(self, rel: str) -> Path:
+        return self.store / "openspec" / "changes" / "T-0001" / rel
+
+
+@pytest.fixture
+def f(tmp_path: Path) -> Fixture:
+    f = Fixture(tmp_path)
+    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
+    for rel in ("src/greet.py", "src/other.py"):
+        (f.target / rel).parent.mkdir(parents=True, exist_ok=True)
+        (f.target / rel).write_text(f"# {rel}\n")
+    subprocess.run(["git", "-C", str(f.target), "add", "-A"], check=True)
+    subprocess.run(["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "land"],
+                   check=True)
+    f.ok("init")
+    f.ok("ticket", "new", "--file", f.file("req.md", "# Fixture\n\nGreet.\n"))
+    approved_parent(f.ok, "T-0001", f.file("v1.md", V1))
+    return f
+
+
+# ----- the spec drift checks (test_spec_drift.py) -------------------------------------------------
+
+def land(f: Fixture, *files: str) -> str:
+    """One commit on the target's main that appends a line to each file; returns its sha."""
+    for rel in files:
+        p = f.target / rel
+        p.parent.mkdir(parents=True, exist_ok=True)
+        with p.open("a") as fh:
+            fh.write(f"# {rel}\n")
+    git = ["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f"]
+    subprocess.run([*git, "add", "-A"], check=True)
+    subprocess.run([*git, "commit", "-qm", f"land {' '.join(files)}"], check=True)
+    return head(f)
+
+
+def head(f: Fixture) -> str:
+    return subprocess.run(["git", "-C", str(f.target), "rev-parse", "main"], capture_output=True, text=True,
+                          check=True).stdout.strip()
+
+
+def start(f: Fixture, tid: str = "T-0001.1") -> subprocess.CompletedProcess:
+    return f.cli("run", "start", "--role", "implementer", "--ticket", tid)
+
+
+def implementer_runs(f: Fixture) -> list[str]:
+    d = f.store / "runs"
+    return sorted(p.name for p in d.iterdir() if p.name.endswith("-implementer")) if d.exists() else []
+
+
+def drifted(f: Fixture, cp: subprocess.CompletedProcess, tid: str = "T-0001.1") -> str:
+    """Assert a drift refusal that reserved no run and wrote nothing to the sub-ticket; return its error."""
+    assert cp.returncode == 2, cp.stdout + cp.stderr
+    error = json.loads(cp.stdout.strip().splitlines()[-1])["error"]
+    assert error.startswith("BLOCKED from harness: spec drift: ")
+    assert error.endswith(f"Amend the spec (`spec amend T-0001`) or rule (`resolve {tid} --ruling F`)")
+    assert implementer_runs(f) == []
+    sub = f.ticket(tid)
+    assert sub["status"] == "ready-for-implementer" and sub["in_flight"] == [] and not sub.get("branch")
+    return error
+
+
+def started(cp: subprocess.CompletedProcess) -> None:
+    assert cp.returncode == 0, cp.stdout + cp.stderr
+
+
+# ----- the stand-in `claude` and the intake store of `factory drive` (test_drive.py) --------------
+
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+
+STANDIN = '''#!{python}
+import json, os, pathlib, sys, time
+cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
+with log.open("a") as f:
+    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
+                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
+role = cwd.name.split("-", 2)[2]
+plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
+nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
+nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
+time.sleep(p.get("sleep", 0))
+text, err = p.get("say", ""), "fail" in p
+if "write" in p:
+    text = "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
+    (cwd / "output.md").write_text(text)
+elif err:
+    text = p["fail"]
+print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
+                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
+sys.exit(1 if err else 0)
+'''
+
+
+class Store(CliStore):
+    """A throwaway store with T-0001 ready for triage, and the stand-in `claude` first on PATH."""
+
+    def __init__(self, tmp_path: Path, instance: Path = FIXTURE_INSTANCE):
+        self.tmp = tmp_path
+        self.root = tmp_path / "state"
+        self.log = tmp_path / "claude.log"
+        bindir = tmp_path / "bin"
+        bindir.mkdir()
+        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
+        (bindir / "claude").chmod(0o755)
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(instance),
+                    "PYTHONDONTWRITEBYTECODE": "1", "STANDIN_LOG": str(self.log),
+                    "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}"}
+        self.env.pop("FACTORY_DISPATCH", None)
+        req = tmp_path / "req.md"
+        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+        self.ok("ticket", "new", "--file", str(req))
+
+    def cli(self, *argv: str, plays: dict | None = None) -> subprocess.CompletedProcess:
+        env = {**self.env, "STANDIN_PLAYS": json.dumps(plays or {})}
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+    def drive(self, plays: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
+        cp = self.cli("drive", "T-0001", *extra, plays=plays)
+        return cp, json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def ticket(self, tid: str = "T-0001") -> dict:
+        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())
+
+    def runs(self) -> list[dict]:
+        return [yaml.safe_load(p.read_text()) for p in sorted(self.root.glob("runs/*/meta.yaml"))]
+
+    def calls(self) -> list[dict]:
+        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []
+
+    def events(self) -> list[str]:
+        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
+                for ln in p.read_text().splitlines() if ln.strip()]
+
+
+# ----- the build store of `factory drive` (test_drive_build.py) -----------------------------------
+
+BUILD_STANDIN = '''#!{python}
+import json, os, pathlib, re, sys, time
+t0 = time.time()
+cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
+with log.open("a") as f:
+    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
+                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
+role = cwd.name.split("-", 2)[2]
+plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
+nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
+nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
+time.sleep(p.get("sleep", 0))
+text, err = p.get("say", ""), "fail" in p
+if "write" in p:
+    head = re.search(r"^head: '?([0-9a-f]{{40}})", (cwd / "meta.yaml").read_text(), re.M)
+    text = (("Commit: %s\\n" % head[1]) if head else "") + ("Gate suite: PASS\\n" if role == "verifier" else "")
+    text += "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
+    (cwd / "output.md").write_text(text)
+elif err:
+    text = p["fail"]
+with log.with_name(log.name + ".times").open("a") as f:
+    f.write("%f %f\\n" % (t0, time.time()))
+print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
+                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
+sys.exit(1 if err else 0)
+'''
+
+
+class BuildStore(Store):
+    """Part A's store, with T-0001 approved at the spec gate (ready for its planner; a one-section
+    spec, so the planner is skipped), a scratch git repository as the target, and this file's
+    stand-in `claude`."""
+
+    def __init__(self, tmp_path):
+        super().__init__(tmp_path)
+        (tmp_path / "bin" / "claude").write_text(BUILD_STANDIN.format(python=sys.executable))
+        spec = tmp_path / "spec.md"
+        spec.write_text("## Problem\nx\n")
+        approved_parent(self.ok, "T-0001", spec)
+        self.target = git_repo(tmp_path / "target")
+        self.env.update(FACTORY_REPO=str(self.target), FACTORY_INTEGRATION_BRANCH="main")
+
+    def git(self, *argv: str, cwd=None) -> str:
+        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=cwd or self.target,
+                            capture_output=True, text=True, check=True)
+        return cp.stdout.strip()
+
+    def two_subtickets_at_checks(self) -> None:
+        """T-0001 planned into T-0001.1 and T-0001.2, independent, each at checks-in-flight on its own commit."""
+        plan = self.tmp / "plan.md"
+        plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n\n"
+                        "ST-2 / Two\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("subticket", "add", "T-0001", "--file", str(plan))
+        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+        for i in (1, 2):
+            self.git("checkout", "-qb", f"factory/T-0001.{i}", "main")
+            (self.target / f"f{i}.txt").write_text(f"{i}\n")
+            self.git("add", f"f{i}.txt")
+            self.git("commit", "-qm", f"w{i}")
+            self.git("checkout", "-q", "main")
+            head = self.git("rev-parse", f"factory/T-0001.{i}")
+            self.ok("ticket", "set", f"T-0001.{i}", "status=checks-in-flight", f"branch=factory/T-0001.{i}",
+                    f"head={head}")
+
+    def most_at_once(self) -> int:
+        spans = [tuple(map(float, ln.split())) for ln in (self.log.parent / (self.log.name + ".times"))
+                 .read_text().splitlines()]
+        return max([sum(a <= s < b for a, b in spans) for s, _ in spans] or [0])
+
+
+# ----- a scratch target with its own store (test_live_store_guard.py) -----------------------------
+
+RULE = "role runs may not write the live store"
+
+
+@pytest.fixture
+def target(tmp_path: Path) -> Path:
+    t = git_repo(tmp_path / "target")
+    cp = cli(t, "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    req = tmp_path / "r.md"
+    req.write_text("# demo\n\nDo the thing.\n")
+    assert cli(t, "ticket", "new", "--file", str(req)).returncode == 0
+    return t
+
+
+def state(target: Path) -> Path:
+    return target / ".factory" / "state"
+
+
+def start_triage(target: Path) -> str:
+    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001")
+    assert cp.returncode == 0, cp.stderr
+    return js(cp)["run_id"]
+
+
+def snapshot(target: Path) -> dict[str, bytes]:
+    return {**tree(target / ".factory"), **tree(target / ".claude")}
+
+
+def other_request(tmp_path: Path) -> str:
+    p = tmp_path / "r2.md"
+    p.write_text("# other\n\nDo another thing.\n")
+    return str(p)
+
+
+def assert_refused(cp, *details: str) -> None:
+    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
+    assert RULE in cp.stderr and "use a throwaway FACTORY_STATE" in cp.stderr
+    assert "FACTORY_DISPATCH" not in cp.stderr + cp.stdout
+    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
+    for d in details:
+        assert d in cp.stderr
+
+
+# ----- the store branch (test_store_branch.py) ----------------------------------------------------
+
+BRANCH = "factory-store"
+IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
+
+
+def git(cwd: Path, *argv: str, check: bool = True) -> str:
+    env = {**os.environ, **IDENT}
+    cp = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, env=env)
+    if check:
+        assert cp.returncode == 0, (argv, cp.stderr)
+    return cp.stdout.strip()
+
+
+def exclude(t: Path) -> Path:
+    p = Path(git(t, "rev-parse", "--git-path", "info/exclude"))
+    return p if p.is_absolute() else t / p
+
+
+def request(tmp_path: Path) -> str:
+    p = tmp_path / "r.md"
+    p.write_text("# demo\n\nDo the thing.\n")
+    return str(p)
+
+
+# ----- the shepherd: the routing table applied to the store CLI (test_shepherd.py) ----------------
+
+STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
+MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec
+
+
+def built_to_implementer(tmp_path, plan: str | None = None):
+    """A ticket approved, planned and split; returns the shepherd, the parent id and its sub-ticket ids."""
+    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
+    f.human_runs("init")
+    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
+    for role in ("triage", "spec_writer", "critic"):
+        f.dispatch(role, tid)
+    f.human_approves(tid)
+    if plan:
+        p = f.tmp / "plan.md"
+        p.write_text(plan + "STATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+        f.dispatch("planner", tid, stub_path=p)
+    else:
+        f.dispatch("planner", tid)
+    return f, tid, list(f.ok("ticket", "parent-check", tid)["subtickets"])
+
+
+class Run:
+    def __init__(self, run_id: str, input_text: str, sources: list[str], status: str | None):
+        self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status
+
+
+class Shepherd(CliStore):
+    def __init__(self, tmp_path: Path, case: str, with_repo: bool = False):
+        self.store = tmp_path / "state"
+        self.case = case
+        self.tmp = tmp_path
+        self.count: dict[str, int] = {}
+        self.last_join: dict = {}
+        self.repo: Path | None = None
+        if with_repo:  # a scratch target repo: one commit on `main`, the integration branch
+            self.repo = tmp_path / "target"
+            self.repo.mkdir()
+            self.git("init", "-q", "-b", "main")
+            self.git("config", "user.email", "fixture@example.com")
+            self.git("config", "user.name", "fixture")
+            (self.repo / "README.md").write_text("target repo\n")
+            self.git("add", "README.md")
+            self.git("commit", "-q", "-m", "initial")
+
+    def git(self, *argv: str, cwd: Path | None = None) -> str:
+        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
+        assert cp.returncode == 0, f"git {' '.join(argv)}: {cp.stderr}"
+        return cp.stdout
+
+    def repo_rev(self, ref: str) -> str:
+        return self.git("rev-parse", ref).strip()
+
+    # --- the store CLI, as the clerk runs it
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        env = {**os.environ, "FACTORY_STATE": str(self.store), "PYTHONDONTWRITEBYTECODE": "1"}
+        if self.repo:
+            env["FACTORY_REPO"] = str(self.repo)
+            env["FACTORY_INTEGRATION_BRANCH"] = "main"
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+    def ticket(self, tid: str) -> dict:
+        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())
+
+    def state(self, tid: str) -> str:
+        return self.ticket(tid)["status"]
+
+    def results(self, tid: str) -> dict:
+        return self.ok("results", "show", tid)["rows"]
+
+    def ready_implementers(self, parent: str) -> list[str]:
+        return self.ok("ticket", "ready-implementers", parent)["ready"]
+
+    def parent_check(self, parent: str) -> str:
+        return self.ok("ticket", "parent-check", parent)["state"]
+
+    def log(self) -> list[dict]:
+        return [json.loads(ln) for p in sorted((self.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
+
+    # --- the humans
+    def request(self, text: str) -> str:
+        p = self.tmp / f"request-{len(list(self.tmp.glob('request-*.md'))) + 1}.md"
+        p.write_text(text)
+        return self.ok("ticket", "new", "--file", str(p))["id"]
+
+    def human_runs(self, *argv: str) -> dict:
+        return self.ok(*argv)
+
+    def human_approves(self, tid: str) -> None:
+        self.ok("approve-spec", tid)
+
+    def human_answers(self, tid: str, text: str) -> None:
+        p = self.tmp / f"answer-{tid}-{self.ticket(tid)['history'].__len__()}.md"
+        p.write_text(text)
+        self.ok("resolve", tid, "--answer", str(p))
+
+    # --- one role run, then the routing table's row for its STATUS (as intake.js does)
+    def dispatch(self, role: str, tid: str, stub: str | None = None, finish: bool = True, stub_path: Path | None = None, route: bool = True,
+                 file: str = "thing.txt", merge_main: bool = False, no_change: bool = False, killed: bool = False) -> Run:
+        self.count[role] = self.count.get(role, 0) + 1
+        stub_path = stub_path or STUBS / (stub or f"{self.case}/{role}-{self.count[role]}.md")
+        rid = self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
+        composed = self.ok("run", "compose", rid)
+        input_text = (self.store / "runs" / rid / "input.md").read_text()
+        if not finish:
+            return Run(rid, input_text, composed["sources"], None)
+        meta = yaml.safe_load((self.store / "runs" / rid / "meta.yaml").read_text())
+        if role == "implementer":  # the stub implementer's one code change, committed on its branch
+            wt = Path(meta["worktree"])
+            if merge_main:  # a conflict run: merge the integration branch into the branch, nothing else
+                self.git("merge", "-q", "--no-edit", "main", cwd=wt)
+            elif no_change:
+                pass  # an implementer that returns without touching its branch
+            else:
+                (wt / file).write_text("the thing\n")
+                self.git("add", file, cwd=wt)
+                self.git("commit", "-q", "-m", f"{tid}: the thing", cwd=wt)
+        if killed:  # the run returned nothing (budget kill): no output, a KILLED row
+            status = self.ok("run", "finish", rid, "--status-override", "KILLED")["status"]
+            self.ok("run", "cleanup", rid)
+            self.ok("results", "record", tid, "--head", self.ok("ticket", "head", tid)["head"], "--role", role, "--run", rid, "--killed")
+            self.act_on_join(tid, rid)
+            return Run(rid, input_text, composed["sources"], status)
+        text = stub_path.read_text().replace("Commit: HEAD", f"Commit: {meta.get('head')}")
+        (self.store / "runs" / rid / "output.md").write_text(text)
+        status = self.ok("run", "finish", rid)["status"]
+        if role in ("reviewer", "verifier"):
+            self.ok("run", "cleanup", rid)
+        if route:
+            self.route(role, tid, rid, status, meta)
+        return Run(rid, input_text, composed["sources"], status)
+
+    def route(self, role: str, tid: str, rid: str, status: str, meta: dict | None = None) -> None:
+        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
+        park = lambda reason: self.ok("ticket", "park", tid, "--reason", reason, "--outputs", rid)  # noqa: E731
+        if role == "triage":
+            {"ACCEPT": lambda: go("ready-for-spec-writer"), "REJECT": lambda: go("closed"),
+             "CLARIFY": lambda: go("waiting-requester"), "NEEDS-HUMAN": lambda: park("NEEDS-HUMAN from triage")}[status]()
+        elif role == "spec_writer":
+            self.ok("spec", "add", tid, "--from-run", rid)  # every version the writer returns is kept
+            if status == "NEEDS-HUMAN":
+                park("NEEDS-HUMAN from spec writer")
+            else:
+                assert status in ("READY-FOR-CRITIC", "NEEDS-SPLIT"), status
+                go("ready-for-critic", "spec:init")
+        elif role == "critic":
+            if status == "APPROVE":
+                go("awaiting-spec-gate")
+            elif status == "ESCALATE":
+                park("ESCALATE from critic")
+            else:
+                assert status == "REVISE", status
+                if self.ticket(tid)["round"]["spec"] < MAX_SPEC_ROUNDS:
+                    go("ready-for-spec-writer", "spec:+1")
+                else:
+                    park("max rounds")
+        elif role == "planner":
+            if status == "PLANNED":
+                self.ok("spec", "tasks", tid, "--run", rid)
+                self.ok("plan", "add", tid, "--from-run", rid)
+                self.ok("subticket", "add", tid, "--run", rid)
+                go("planned")
+            else:
+                park(f"{status} from planner")
+        elif role == "implementer":
+            if status == "BLOCKED":
+                park("BLOCKED from implementer")
+            else:
+                assert status == "READY-FOR-REVIEW", status
+                moved = self.ok("ticket", "head", tid)
+                if moved["merge_refused"]:  # a conflict run that did not merge main in: ask the join, skip the checkers
+                    self.act_on_join(tid, rid)
+                else:
+                    go("checks-in-flight", "pr:init")
+        elif role in ("reviewer", "verifier"):
+            if self.ticket(tid)["status"] == "ready-for-parent-verify":
+                # | parent-close | VERIFIED archives the change, then closes; anything else parks the parent |
+                if status == "VERIFIED":
+                    self.ok("archive", tid)
+                    go("closed")
+                else:
+                    park(f"{status} from parent-close verifier")
+                return
+            head = self.ok("ticket", "head", tid)["head"]  # as build.js does: the CLI names the head, never the store file
+            assert self.ok("ticket", "show", tid, "--json")["head"] == head
+            self.ok("results", "record", tid, "--head", head, "--role", role, "--output", str(self.store / "runs" / rid / "output.md"), "--run", rid)
+            self.act_on_join(tid, rid)
+
+    def act_on_join(self, tid: str, rid: str | None = None) -> dict:
+        """`factory ticket join` decides; the dispatcher (build.js, and this shepherd) only carries it out."""
+        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
+        join = self.ok("ticket", "join", tid)
+        self.last_join = join
+        if join["decision"] == "merge":
+            go("ready-for-merge")
+            cp = self.cli("merge", tid)
+            if cp.returncode != 0:
+                again = self.ok("ticket", "join", tid)
+                self.last_join = again
+                if again["decision"] == "conflict":
+                    go("ready-for-implementer")
+                else:
+                    self.ok("ticket", "park", tid, "--reason", again["reason"])
+        elif join["decision"] == "revise":
+            go("ready-for-implementer", join["round_op"])
+        elif join["decision"] == "conflict":
+            if self.state(tid) != "ready-for-implementer":
+                go("ready-for-implementer")
+        elif join["decision"] == "park":
+            self.ok("ticket", "park", tid, "--reason", join["reason"], *(["--outputs", rid] if rid else []))
+        return join  # "wait": the other checker has not reported on this head yet
+
+
+# ----- a sub-ticket built to merged (test_parent_close_reuse.py) ----------------------------------
+
+def _parent_verifier_runs(f, tid: str) -> list[str]:
+    return [p.parent.name for p in (f.store / "runs").glob("*-verifier/meta.yaml")
+            if yaml.safe_load(p.read_text())["ticket"] == tid]
+
+
+def _build(f, st: str, file: str = "thing.txt"):
+    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file=file)
+    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
+    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
+    assert f.state(st) == "merged"
+    return ver
diff --git a/tests/factory/test_build_startup.py b/tests/factory/test_build_startup.py
index 7faefb3..783642a 100644
--- a/tests/factory/test_build_startup.py
+++ b/tests/factory/test_build_startup.py
@@ -8,8 +8,9 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import approved_parent
-from .test_subtickets import PLAN_LETTERS, js, run, ticket
+from ._cli import approved_parent, run, ticket
+from ._cli import js_ok as js
+from ._fixtures import PLAN_LETTERS, ticket_files
 
 
 def planner_run(store: Path, tid: str, plan: str) -> str:
@@ -20,10 +21,6 @@ def planner_run(store: Path, tid: str, plan: str) -> str:
     return rid
 
 
-def ticket_files(store: Path) -> list[str]:
-    return sorted(p.name for p in (store / "tickets").iterdir())
-
-
 def test_subticket_add_without_a_source_uses_the_recorded_planner_run(tmp_path):
     store = tmp_path / "state"
     (tmp_path / "r.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
diff --git a/tests/factory/test_drift_siblings.py b/tests/factory/test_drift_siblings.py
index d8909b0..d95c256 100644
--- a/tests/factory/test_drift_siblings.py
+++ b/tests/factory/test_drift_siblings.py
@@ -16,11 +16,17 @@ import subprocess
 import pytest
 import yaml
 
-from . import test_spec_amend
-from .test_spec_amend import V2, Fixture
-from .test_spec_drift import drifted, head, implementer_runs, land, start, started
-
-f = test_spec_amend.f  # the t0027-amend.sh store fixture, shared with test_spec_amend
+from ._fixtures import (  # noqa: F401  (f is the t0027-amend.sh store fixture)
+    V2,
+    Fixture,
+    drifted,
+    f,
+    head,
+    implementer_runs,
+    land,
+    start,
+    started,
+)
 
 ST1_THEN_ST2 = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n"
 ONE = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n"
diff --git a/tests/factory/test_drive.py b/tests/factory/test_drive.py
index b9cfaa0..fe3506d 100644
--- a/tests/factory/test_drive.py
+++ b/tests/factory/test_drive.py
@@ -21,76 +21,12 @@ from pathlib import Path
 
 import yaml
 
-from ._cli import BIN, REPO, CliStore
-
-FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
-
-STANDIN = '''#!{python}
-import json, os, pathlib, sys, time
-cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
-with log.open("a") as f:
-    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
-                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
-role = cwd.name.split("-", 2)[2]
-plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
-nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
-nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
-time.sleep(p.get("sleep", 0))
-text, err = p.get("say", ""), "fail" in p
-if "write" in p:
-    text = "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
-    (cwd / "output.md").write_text(text)
-elif err:
-    text = p["fail"]
-print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
-                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
-sys.exit(1 if err else 0)
-'''
+from ._cli import BIN, REPO
+from ._fixtures import FIXTURE_INSTANCE, Store
 
 TRIAGE_OK = {"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}]}
 
 
-class Store(CliStore):
-    """A throwaway store with T-0001 ready for triage, and the stand-in `claude` first on PATH."""
-
-    def __init__(self, tmp_path: Path, instance: Path = FIXTURE_INSTANCE):
-        self.tmp = tmp_path
-        self.root = tmp_path / "state"
-        self.log = tmp_path / "claude.log"
-        bindir = tmp_path / "bin"
-        bindir.mkdir()
-        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
-        (bindir / "claude").chmod(0o755)
-        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(instance),
-                    "PYTHONDONTWRITEBYTECODE": "1", "STANDIN_LOG": str(self.log),
-                    "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}"}
-        self.env.pop("FACTORY_DISPATCH", None)
-        req = tmp_path / "req.md"
-        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
-        self.ok("ticket", "new", "--file", str(req))
-
-    def cli(self, *argv: str, plays: dict | None = None) -> subprocess.CompletedProcess:
-        env = {**self.env, "STANDIN_PLAYS": json.dumps(plays or {})}
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-    def drive(self, plays: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
-        cp = self.cli("drive", "T-0001", *extra, plays=plays)
-        return cp, json.loads(cp.stdout.strip().splitlines()[-1])
-
-    def ticket(self, tid: str = "T-0001") -> dict:
-        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())
-
-    def runs(self) -> list[dict]:
-        return [yaml.safe_load(p.read_text()) for p in sorted(self.root.glob("runs/*/meta.yaml"))]
-
-    def calls(self) -> list[dict]:
-        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []
-
-    def events(self) -> list[str]:
-        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
-                for ln in p.read_text().splitlines() if ln.strip()]
-
-
 def test_an_approved_spec_stops_at_the_spec_gate_after_one_revision(tmp_path):
     s = Store(tmp_path)
     cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}, "--phase", "intake")
diff --git a/tests/factory/test_drive_build.py b/tests/factory/test_drive_build.py
index 645b36d..691f218 100644
--- a/tests/factory/test_drive_build.py
+++ b/tests/factory/test_drive_build.py
@@ -12,88 +12,18 @@ import json
 import os
 import signal
 import subprocess
-import sys
 import tempfile
 import time
 
 import yaml
 
-from ._cli import approved_parent, git_repo
-from .test_drive import BIN, REPO, Store
-
-STANDIN = '''#!{python}
-import json, os, pathlib, re, sys, time
-t0 = time.time()
-cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
-with log.open("a") as f:
-    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
-                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
-role = cwd.name.split("-", 2)[2]
-plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
-nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
-nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
-time.sleep(p.get("sleep", 0))
-text, err = p.get("say", ""), "fail" in p
-if "write" in p:
-    head = re.search(r"^head: '?([0-9a-f]{{40}})", (cwd / "meta.yaml").read_text(), re.M)
-    text = (("Commit: %s\\n" % head[1]) if head else "") + ("Gate suite: PASS\\n" if role == "verifier" else "")
-    text += "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
-    (cwd / "output.md").write_text(text)
-elif err:
-    text = p["fail"]
-with log.with_name(log.name + ".times").open("a") as f:
-    f.write("%f %f\\n" % (t0, time.time()))
-print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
-                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
-sys.exit(1 if err else 0)
-'''
+from ._cli import BIN, REPO
+from ._fixtures import BuildStore, Store
 
 OK_PLAYS = {"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}],
             "verifier": [{"write": "VERIFIED"}]}
 
 
-class BuildStore(Store):
-    """Part A's store, with T-0001 approved at the spec gate (ready for its planner; a one-section
-    spec, so the planner is skipped), a scratch git repository as the target, and this file's
-    stand-in `claude`."""
-
-    def __init__(self, tmp_path):
-        super().__init__(tmp_path)
-        (tmp_path / "bin" / "claude").write_text(STANDIN.format(python=sys.executable))
-        spec = tmp_path / "spec.md"
-        spec.write_text("## Problem\nx\n")
-        approved_parent(self.ok, "T-0001", spec)
-        self.target = git_repo(tmp_path / "target")
-        self.env.update(FACTORY_REPO=str(self.target), FACTORY_INTEGRATION_BRANCH="main")
-
-    def git(self, *argv: str, cwd=None) -> str:
-        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=cwd or self.target,
-                            capture_output=True, text=True, check=True)
-        return cp.stdout.strip()
-
-    def two_subtickets_at_checks(self) -> None:
-        """T-0001 planned into T-0001.1 and T-0001.2, independent, each at checks-in-flight on its own commit."""
-        plan = self.tmp / "plan.md"
-        plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n\n"
-                        "ST-2 / Two\nDepends on: none\nParallel-safe: yes\n")
-        self.ok("subticket", "add", "T-0001", "--file", str(plan))
-        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
-        for i in (1, 2):
-            self.git("checkout", "-qb", f"factory/T-0001.{i}", "main")
-            (self.target / f"f{i}.txt").write_text(f"{i}\n")
-            self.git("add", f"f{i}.txt")
-            self.git("commit", "-qm", f"w{i}")
-            self.git("checkout", "-q", "main")
-            head = self.git("rev-parse", f"factory/T-0001.{i}")
-            self.ok("ticket", "set", f"T-0001.{i}", "status=checks-in-flight", f"branch=factory/T-0001.{i}",
-                    f"head={head}")
-
-    def most_at_once(self) -> int:
-        spans = [tuple(map(float, ln.split())) for ln in (self.log.parent / (self.log.name + ".times"))
-                 .read_text().splitlines()]
-        return max([sum(a <= s < b for a, b in spans) for s, _ in spans] or [0])
-
-
 def roles_and_statuses(s: Store) -> list[tuple[str, str, str]]:
     return [(m["role"], m["ticket"], m["status"]) for m in s.runs()]
 
diff --git a/tests/factory/test_drive_guard.py b/tests/factory/test_drive_guard.py
index a1cad36..2bf4cc2 100644
--- a/tests/factory/test_drive_guard.py
+++ b/tests/factory/test_drive_guard.py
@@ -20,17 +20,18 @@ from pathlib import Path
 
 import pytest
 
-from .test_drive import STANDIN, Store
-from .test_drive_build import BuildStore
-from .test_instance import cli, js, tree
-from .test_live_store_guard import (  # noqa: F401  (target is a fixture)
+from ._cli import cli, js, tree
+from ._fixtures import (  # noqa: F401  (target is a fixture)
+    STANDIN,
+    BuildStore,
+    Store,
     assert_refused,
-    request,
     snapshot,
     start_triage,
     state,
     target,
 )
+from ._fixtures import other_request as request
 
 REJECT = {"triage": [{"write": "REJECT"}]}
 
diff --git a/tests/factory/test_killed_checker.py b/tests/factory/test_killed_checker.py
index b30dd08..caa21e4 100644
--- a/tests/factory/test_killed_checker.py
+++ b/tests/factory/test_killed_checker.py
@@ -10,7 +10,7 @@ from __future__ import annotations
 
 import pytest
 
-from .test_shepherd import built_to_implementer
+from ._fixtures import built_to_implementer
 
 
 @pytest.mark.parametrize("role", ["verifier", "reviewer"])
diff --git a/tests/factory/test_live_store_guard.py b/tests/factory/test_live_store_guard.py
index e1d410c..c556445 100644
--- a/tests/factory/test_live_store_guard.py
+++ b/tests/factory/test_live_store_guard.py
@@ -12,54 +12,15 @@ change a result; a case that needs the marker passes it explicitly.
 """
 from __future__ import annotations
 
-from pathlib import Path
-
-import pytest
-
-from .test_instance import cli, git_repo, js, tree
-
-RULE = "role runs may not write the live store"
-
-
-@pytest.fixture
-def target(tmp_path: Path) -> Path:
-    t = git_repo(tmp_path / "target")
-    cp = cli(t, "init", "--repo-name", "demo")
-    assert cp.returncode == 0, cp.stderr
-    req = tmp_path / "r.md"
-    req.write_text("# demo\n\nDo the thing.\n")
-    assert cli(t, "ticket", "new", "--file", str(req)).returncode == 0
-    return t
-
-
-def state(target: Path) -> Path:
-    return target / ".factory" / "state"
-
-
-def start_triage(target: Path) -> str:
-    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001")
-    assert cp.returncode == 0, cp.stderr
-    return js(cp)["run_id"]
-
-
-def snapshot(target: Path) -> dict[str, bytes]:
-    return {**tree(target / ".factory"), **tree(target / ".claude")}
-
-
-def request(tmp_path: Path) -> str:
-    p = tmp_path / "r2.md"
-    p.write_text("# other\n\nDo another thing.\n")
-    return str(p)
-
-
-def assert_refused(cp, *details: str) -> None:
-    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
-    assert RULE in cp.stderr and "use a throwaway FACTORY_STATE" in cp.stderr
-    assert "FACTORY_DISPATCH" not in cp.stderr + cp.stdout
-    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
-    for d in details:
-        assert d in cp.stderr
-
+from ._cli import cli, js
+from ._fixtures import (  # noqa: F401  (target is a fixture)
+    assert_refused,
+    snapshot,
+    start_triage,
+    state,
+    target,
+)
+from ._fixtures import other_request as request
 
 # ----- in flight ------------------------------------------------------------------------------
 
diff --git a/tests/factory/test_p0_cli.py b/tests/factory/test_p0_cli.py
index 04b65a8..4b1a56b 100644
--- a/tests/factory/test_p0_cli.py
+++ b/tests/factory/test_p0_cli.py
@@ -10,7 +10,7 @@ from pathlib import Path
 import pytest
 import yaml
 
-from ._cli import REPO, js, run, ticket  # noqa: F401  (test_role_inputs.py imports REPO from here)
+from ._cli import js, run, ticket
 
 TRAILER = "\nSTATUS: {s}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
 
diff --git a/tests/factory/test_parent_close_reuse.py b/tests/factory/test_parent_close_reuse.py
index 178789b..9936556 100644
--- a/tests/factory/test_parent_close_reuse.py
+++ b/tests/factory/test_parent_close_reuse.py
@@ -10,7 +10,7 @@ from __future__ import annotations
 
 import yaml
 
-from .test_shepherd import built_to_implementer
+from ._fixtures import _build, _parent_verifier_runs, built_to_implementer
 
 TWO_COVERING = ("T-0001.1 / First\n  Depends on: none\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
                 "T-0001.2 / Second\n  Depends on: T-0001.1\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
@@ -19,19 +19,6 @@ UNCOVERED = ("T-0001.1 / Do the thing\n  Depends on: none\n  Parallel-safe: yes\
              "Coverage map: the check → T-0001.1\n")
 
 
-def _parent_verifier_runs(f, tid: str) -> list[str]:
-    return [p.parent.name for p in (f.store / "runs").glob("*-verifier/meta.yaml")
-            if yaml.safe_load(p.read_text())["ticket"] == tid]
-
-
-def _build(f, st: str, file: str = "thing.txt"):
-    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file=file)
-    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
-    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
-    assert f.state(st) == "merged"
-    return ver
-
-
 def _assert_parent_close_still_required(f, tid: str) -> None:
     pc = f.ok("ticket", "parent-check", tid)
     assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] is None
diff --git a/tests/factory/test_plan_fields.py b/tests/factory/test_plan_fields.py
index 2cd180d..9092948 100644
--- a/tests/factory/test_plan_fields.py
+++ b/tests/factory/test_plan_fields.py
@@ -11,9 +11,9 @@ import subprocess
 
 import pytest
 
-from ._cli import approved_parent
-from .test_build_startup import ticket_files
-from .test_subtickets import js, run
+from ._cli import approved_parent, run
+from ._cli import js_ok as js
+from ._fixtures import ticket_files
 
 
 @pytest.fixture
diff --git a/tests/factory/test_role_inputs.py b/tests/factory/test_role_inputs.py
index 8c192f3..b81062d 100644
--- a/tests/factory/test_role_inputs.py
+++ b/tests/factory/test_role_inputs.py
@@ -10,8 +10,8 @@ from __future__ import annotations
 import subprocess
 import sys
 
-from .test_p0_cli import REPO, js, run
-from .test_shepherd import Shepherd
+from ._cli import REPO, js, run
+from ._fixtures import Shepherd
 
 FENCE = "```"
 
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index 683def4..acc97e6 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -7,22 +7,18 @@ mode), and the dispatcher routes on its STATUS. The human steps are the two gate
 answers to questions.
 
 The real dispatcher is factory/workflows/intake.js, a Workflow script that needs the Claude Code
-agent runtime, so it cannot run under pytest. `Shepherd` at the bottom applies the same routing
-table to the same store CLI; if the two ever disagree, the table in the design doc decides.
+agent runtime, so it cannot run under pytest. `Shepherd`, in `_fixtures.py`, applies the same
+routing table to the same store CLI; if the two ever disagree, the table in the design doc decides.
 """
 from __future__ import annotations
 
-import json
-import os
 import subprocess
 from pathlib import Path
 
 import yaml
 
-from ._cli import BIN, REPO, CliStore
+from ._fixtures import MAX_SPEC_ROUNDS, Shepherd, built_to_implementer
 
-STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
-MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec
 MAX_PR_ROUNDS = 2  # factory/config.yaml max_rounds.pr
 
 
@@ -388,23 +384,6 @@ def test_a_planned_parent_can_be_parked_and_a_closed_sibling_is_reported(tmp_pat
     assert f.state(tid) == "parked"
 
 
-def built_to_implementer(tmp_path, plan: str | None = None):
-    """A ticket approved, planned and split; returns the shepherd, the parent id and its sub-ticket ids."""
-    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
-    f.human_runs("init")
-    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
-    for role in ("triage", "spec_writer", "critic"):
-        f.dispatch(role, tid)
-    f.human_approves(tid)
-    if plan:
-        p = f.tmp / "plan.md"
-        p.write_text(plan + "STATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
-        f.dispatch("planner", tid, stub_path=p)
-    else:
-        f.dispatch("planner", tid)
-    return f, tid, list(f.ok("ticket", "parent-check", tid)["subtickets"])
-
-
 TWO_PARALLEL = "## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** none\n**Parallel-safe:** yes\n\n"
 CHAIN = "## ST-1 / First\n**Depends on:** none\n**Parallel-safe:** yes\n\n## ST-2 / Second\n**Depends on:** ST-1\n**Parallel-safe:** yes\n\n"
 REQUEST_CHANGES = "Commit: HEAD\nFindings: [BLOCKING] thing.txt:1: FINDING-ROUND-{n} → wrong\nSTATUS: REQUEST-CHANGES\nCONFIDENCE: high, fixture\nESCALATIONS: none\n"
@@ -586,196 +565,3 @@ def test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix(tmp_
     assert f.ok("ticket", "ready-implementers", tid)["resumable"] == [st]
     f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
     assert f.state(st) == "merged"
-
-
-# ----- the shepherd: the routing table applied to the store CLI ----------------------------------
-
-class Run:
-    def __init__(self, run_id: str, input_text: str, sources: list[str], status: str | None):
-        self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status
-
-
-class Shepherd(CliStore):
-    def __init__(self, tmp_path: Path, case: str, with_repo: bool = False):
-        self.store = tmp_path / "state"
-        self.case = case
-        self.tmp = tmp_path
-        self.count: dict[str, int] = {}
-        self.last_join: dict = {}
-        self.repo: Path | None = None
-        if with_repo:  # a scratch target repo: one commit on `main`, the integration branch
-            self.repo = tmp_path / "target"
-            self.repo.mkdir()
-            self.git("init", "-q", "-b", "main")
-            self.git("config", "user.email", "fixture@example.com")
-            self.git("config", "user.name", "fixture")
-            (self.repo / "README.md").write_text("target repo\n")
-            self.git("add", "README.md")
-            self.git("commit", "-q", "-m", "initial")
-
-    def git(self, *argv: str, cwd: Path | None = None) -> str:
-        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
-        assert cp.returncode == 0, f"git {' '.join(argv)}: {cp.stderr}"
-        return cp.stdout
-
-    def repo_rev(self, ref: str) -> str:
-        return self.git("rev-parse", ref).strip()
-
-    # --- the store CLI, as the clerk runs it
-    def cli(self, *argv: str) -> subprocess.CompletedProcess:
-        env = {**os.environ, "FACTORY_STATE": str(self.store), "PYTHONDONTWRITEBYTECODE": "1"}
-        if self.repo:
-            env["FACTORY_REPO"] = str(self.repo)
-            env["FACTORY_INTEGRATION_BRANCH"] = "main"
-        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
-
-    def ticket(self, tid: str) -> dict:
-        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())
-
-    def state(self, tid: str) -> str:
-        return self.ticket(tid)["status"]
-
-    def results(self, tid: str) -> dict:
-        return self.ok("results", "show", tid)["rows"]
-
-    def ready_implementers(self, parent: str) -> list[str]:
-        return self.ok("ticket", "ready-implementers", parent)["ready"]
-
-    def parent_check(self, parent: str) -> str:
-        return self.ok("ticket", "parent-check", parent)["state"]
-
-    def log(self) -> list[dict]:
-        return [json.loads(ln) for p in sorted((self.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
-
-    # --- the humans
-    def request(self, text: str) -> str:
-        p = self.tmp / f"request-{len(list(self.tmp.glob('request-*.md'))) + 1}.md"
-        p.write_text(text)
-        return self.ok("ticket", "new", "--file", str(p))["id"]
-
-    def human_runs(self, *argv: str) -> dict:
-        return self.ok(*argv)
-
-    def human_approves(self, tid: str) -> None:
-        self.ok("approve-spec", tid)
-
-    def human_answers(self, tid: str, text: str) -> None:
-        p = self.tmp / f"answer-{tid}-{self.ticket(tid)['history'].__len__()}.md"
-        p.write_text(text)
-        self.ok("resolve", tid, "--answer", str(p))
-
-    # --- one role run, then the routing table's row for its STATUS (as intake.js does)
-    def dispatch(self, role: str, tid: str, stub: str | None = None, finish: bool = True, stub_path: Path | None = None, route: bool = True,
-                 file: str = "thing.txt", merge_main: bool = False, no_change: bool = False, killed: bool = False) -> Run:
-        self.count[role] = self.count.get(role, 0) + 1
-        stub_path = stub_path or STUBS / (stub or f"{self.case}/{role}-{self.count[role]}.md")
-        rid = self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
-        composed = self.ok("run", "compose", rid)
-        input_text = (self.store / "runs" / rid / "input.md").read_text()
-        if not finish:
-            return Run(rid, input_text, composed["sources"], None)
-        meta = yaml.safe_load((self.store / "runs" / rid / "meta.yaml").read_text())
-        if role == "implementer":  # the stub implementer's one code change, committed on its branch
-            wt = Path(meta["worktree"])
-            if merge_main:  # a conflict run: merge the integration branch into the branch, nothing else
-                self.git("merge", "-q", "--no-edit", "main", cwd=wt)
-            elif no_change:
-                pass  # an implementer that returns without touching its branch
-            else:
-                (wt / file).write_text("the thing\n")
-                self.git("add", file, cwd=wt)
-                self.git("commit", "-q", "-m", f"{tid}: the thing", cwd=wt)
-        if killed:  # the run returned nothing (budget kill): no output, a KILLED row
-            status = self.ok("run", "finish", rid, "--status-override", "KILLED")["status"]
-            self.ok("run", "cleanup", rid)
-            self.ok("results", "record", tid, "--head", self.ok("ticket", "head", tid)["head"], "--role", role, "--run", rid, "--killed")
-            self.act_on_join(tid, rid)
-            return Run(rid, input_text, composed["sources"], status)
-        text = stub_path.read_text().replace("Commit: HEAD", f"Commit: {meta.get('head')}")
-        (self.store / "runs" / rid / "output.md").write_text(text)
-        status = self.ok("run", "finish", rid)["status"]
-        if role in ("reviewer", "verifier"):
-            self.ok("run", "cleanup", rid)
-        if route:
-            self.route(role, tid, rid, status, meta)
-        return Run(rid, input_text, composed["sources"], status)
-
-    def route(self, role: str, tid: str, rid: str, status: str, meta: dict | None = None) -> None:
-        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
-        park = lambda reason: self.ok("ticket", "park", tid, "--reason", reason, "--outputs", rid)  # noqa: E731
-        if role == "triage":
-            {"ACCEPT": lambda: go("ready-for-spec-writer"), "REJECT": lambda: go("closed"),
-             "CLARIFY": lambda: go("waiting-requester"), "NEEDS-HUMAN": lambda: park("NEEDS-HUMAN from triage")}[status]()
-        elif role == "spec_writer":
-            self.ok("spec", "add", tid, "--from-run", rid)  # every version the writer returns is kept
-            if status == "NEEDS-HUMAN":
-                park("NEEDS-HUMAN from spec writer")
-            else:
-                assert status in ("READY-FOR-CRITIC", "NEEDS-SPLIT"), status
-                go("ready-for-critic", "spec:init")
-        elif role == "critic":
-            if status == "APPROVE":
-                go("awaiting-spec-gate")
-            elif status == "ESCALATE":
-                park("ESCALATE from critic")
-            else:
-                assert status == "REVISE", status
-                if self.ticket(tid)["round"]["spec"] < MAX_SPEC_ROUNDS:
-                    go("ready-for-spec-writer", "spec:+1")
-                else:
-                    park("max rounds")
-        elif role == "planner":
-            if status == "PLANNED":
-                self.ok("spec", "tasks", tid, "--run", rid)
-                self.ok("plan", "add", tid, "--from-run", rid)
-                self.ok("subticket", "add", tid, "--run", rid)
-                go("planned")
-            else:
-                park(f"{status} from planner")
-        elif role == "implementer":
-            if status == "BLOCKED":
-                park("BLOCKED from implementer")
-            else:
-                assert status == "READY-FOR-REVIEW", status
-                moved = self.ok("ticket", "head", tid)
-                if moved["merge_refused"]:  # a conflict run that did not merge main in: ask the join, skip the checkers
-                    self.act_on_join(tid, rid)
-                else:
-                    go("checks-in-flight", "pr:init")
-        elif role in ("reviewer", "verifier"):
-            if self.ticket(tid)["status"] == "ready-for-parent-verify":
-                # | parent-close | VERIFIED archives the change, then closes; anything else parks the parent |
-                if status == "VERIFIED":
-                    self.ok("archive", tid)
-                    go("closed")
-                else:
-                    park(f"{status} from parent-close verifier")
-                return
-            head = self.ok("ticket", "head", tid)["head"]  # as build.js does: the CLI names the head, never the store file
-            assert self.ok("ticket", "show", tid, "--json")["head"] == head
-            self.ok("results", "record", tid, "--head", head, "--role", role, "--output", str(self.store / "runs" / rid / "output.md"), "--run", rid)
-            self.act_on_join(tid, rid)
-
-    def act_on_join(self, tid: str, rid: str | None = None) -> dict:
-        """`factory ticket join` decides; the dispatcher (build.js, and this shepherd) only carries it out."""
-        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
-        join = self.ok("ticket", "join", tid)
-        self.last_join = join
-        if join["decision"] == "merge":
-            go("ready-for-merge")
-            cp = self.cli("merge", tid)
-            if cp.returncode != 0:
-                again = self.ok("ticket", "join", tid)
-                self.last_join = again
-                if again["decision"] == "conflict":
-                    go("ready-for-implementer")
-                else:
-                    self.ok("ticket", "park", tid, "--reason", again["reason"])
-        elif join["decision"] == "revise":
-            go("ready-for-implementer", join["round_op"])
-        elif join["decision"] == "conflict":
-            if self.state(tid) != "ready-for-implementer":
-                go("ready-for-implementer")
-        elif join["decision"] == "park":
-            self.ok("ticket", "park", tid, "--reason", join["reason"], *(["--outputs", rid] if rid else []))
-        return join  # "wait": the other checker has not reported on this head yet
diff --git a/tests/factory/test_sibling_tests.py b/tests/factory/test_sibling_tests.py
index 67ce52c..acf8916 100644
--- a/tests/factory/test_sibling_tests.py
+++ b/tests/factory/test_sibling_tests.py
@@ -21,6 +21,7 @@ import pytest
 import yaml
 
 from ._cli import REPO, CliStore, approved_parent
+from ._fixtures import BUILD_DRIVER
 
 PLAN = """ST-1 / Interim
 Depends on: none
@@ -36,24 +37,6 @@ Tests to change:
 Protected paths: none
 """
 
-# Drives factory/workflows/build.js on parent T-0001: each clerk command runs for real, each role run
-# returns an empty output (a killed run). Prints each park as `park <id>: <reason>`.
-BUILD_DRIVER = r"""
-import { readFileSync } from 'node:fs'
-import { spawnSync } from 'node:child_process'
-const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
-const agent = async (prompt) => {
-  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
-  if (!m) return ''
-  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
-  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
-}
-const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
-const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
-await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
-  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
-"""
-
 
 class Fixture(CliStore):
     def __init__(self, tmp_path: Path):
diff --git a/tests/factory/test_spec_amend.py b/tests/factory/test_spec_amend.py
index 27f1bda..bc40a2e 100644
--- a/tests/factory/test_spec_amend.py
+++ b/tests/factory/test_spec_amend.py
@@ -11,96 +11,12 @@ scenario; v3 also changes the Decisions line.
 from __future__ import annotations
 
 import json
-import os
 import subprocess
-from pathlib import Path
 
 import pytest
 import yaml
 
-from ._cli import REPO, CliStore, approved_parent  # noqa: F401  (test_spec_drift.py imports REPO from here)
-
-SPEC = """=== proposal.md
-## Problem
-{problem}
-## Decisions
-- {decision}
-=== design.md
-## Proposed change
-Edit `src/greet.py`.
-## Tests to change
-none
-=== specs/demo/spec.md
-## ADDED Requirements
-### Requirement: Greets
-{statement}
-
-#### Scenario: Greeting is printed
-- WHEN `{cmd}`
-- THEN it prints `{out}`
-{extra}=== verification.md
-## Acceptance
-- Greeting is printed → NEW
-{labels}"""
-
-TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n"
-
-
-def spec(decision="Greet by default.", cmd="echo hi", out="hi", problem="x", statement="The tool SHALL greet.",
-         extra="", labels="") -> str:
-    return SPEC.format(decision=decision, cmd=cmd, out=out, problem=problem, statement=statement, extra=extra,
-                       labels=labels)
-
-
-V1, V2 = spec(), spec(cmd="echo hello", out="hello")
-
-
-class Fixture(CliStore):
-    def __init__(self, tmp_path: Path):
-        self.tmp = tmp_path
-        self.store = tmp_path / "store"
-        self.target = tmp_path / "t"
-        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
-                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
-
-    def file(self, name: str, text: str) -> str:
-        p = self.tmp / name
-        p.write_text(text)
-        return str(p)
-
-    def ticket(self, tid: str) -> dict:
-        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())
-
-    def plan(self, text: str = TWO) -> None:
-        self.ok("subticket", "add", "T-0001", "--file", self.file("plan.md", text))
-        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
-
-    def amend(self, text: str, reason: str = "Seed the greeting.", intent: str = "unchanged",
-              tid: str = "T-0001") -> subprocess.CompletedProcess:
-        return self.cli("spec", "amend", tid, "--file", self.file("amend.md", text), "--reason", reason,
-                        "--intent", intent)
-
-    def snapshot(self) -> dict[str, bytes]:
-        return {str(p.relative_to(self.store)): p.read_bytes() for p in sorted(self.store.rglob("*")) if p.is_file()}
-
-    def change(self, rel: str) -> Path:
-        return self.store / "openspec" / "changes" / "T-0001" / rel
-
-
-@pytest.fixture
-def f(tmp_path: Path) -> Fixture:
-    f = Fixture(tmp_path)
-    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
-    for rel in ("src/greet.py", "src/other.py"):
-        (f.target / rel).parent.mkdir(parents=True, exist_ok=True)
-        (f.target / rel).write_text(f"# {rel}\n")
-    subprocess.run(["git", "-C", str(f.target), "add", "-A"], check=True)
-    subprocess.run(["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "land"],
-                   check=True)
-    f.ok("init")
-    f.ok("ticket", "new", "--file", f.file("req.md", "# Fixture\n\nGreet.\n"))
-    approved_parent(f.ok, "T-0001", f.file("v1.md", V1))
-    return f
+from ._fixtures import V1, V2, Fixture, f, spec  # noqa: F401  (f is a fixture)
 
 
 def refused(f: Fixture, cp: subprocess.CompletedProcess, before: dict[str, bytes]) -> str:
diff --git a/tests/factory/test_spec_drift.py b/tests/factory/test_spec_drift.py
index 61ceb93..9c88234 100644
--- a/tests/factory/test_spec_drift.py
+++ b/tests/factory/test_spec_drift.py
@@ -14,65 +14,29 @@ design names `src/greet.py`, is approved.
 """
 from __future__ import annotations
 
-import json
 import shutil
 import subprocess
 
 import pytest
 import yaml
 
-from . import test_spec_amend
-from .test_sibling_tests import BUILD_DRIVER
-from .test_spec_amend import REPO, V1, V2, Fixture
-
-f = test_spec_amend.f  # the t0027-amend.sh store fixture, shared with test_spec_amend
+from ._cli import REPO
+from ._fixtures import (  # noqa: F401  (f is the t0027-amend.sh store fixture)
+    BUILD_DRIVER,
+    V1,
+    V2,
+    drifted,
+    f,
+    head,
+    implementer_runs,
+    land,
+    start,
+    started,
+)
 
 TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: {deps}\nParallel-safe: yes\n{extra}"
 
 
-def land(f: Fixture, *files: str) -> str:
-    """One commit on the target's main that appends a line to each file; returns its sha."""
-    for rel in files:
-        p = f.target / rel
-        p.parent.mkdir(parents=True, exist_ok=True)
-        with p.open("a") as fh:
-            fh.write(f"# {rel}\n")
-    git = ["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f"]
-    subprocess.run([*git, "add", "-A"], check=True)
-    subprocess.run([*git, "commit", "-qm", f"land {' '.join(files)}"], check=True)
-    return head(f)
-
-
-def head(f: Fixture) -> str:
-    return subprocess.run(["git", "-C", str(f.target), "rev-parse", "main"], capture_output=True, text=True,
-                          check=True).stdout.strip()
-
-
-def start(f: Fixture, tid: str = "T-0001.1") -> subprocess.CompletedProcess:
-    return f.cli("run", "start", "--role", "implementer", "--ticket", tid)
-
-
-def implementer_runs(f: Fixture) -> list[str]:
-    d = f.store / "runs"
-    return sorted(p.name for p in d.iterdir() if p.name.endswith("-implementer")) if d.exists() else []
-
-
-def drifted(f: Fixture, cp: subprocess.CompletedProcess, tid: str = "T-0001.1") -> str:
-    """Assert a drift refusal that reserved no run and wrote nothing to the sub-ticket; return its error."""
-    assert cp.returncode == 2, cp.stdout + cp.stderr
-    error = json.loads(cp.stdout.strip().splitlines()[-1])["error"]
-    assert error.startswith("BLOCKED from harness: spec drift: ")
-    assert error.endswith(f"Amend the spec (`spec amend T-0001`) or rule (`resolve {tid} --ruling F`)")
-    assert implementer_runs(f) == []
-    sub = f.ticket(tid)
-    assert sub["status"] == "ready-for-implementer" and sub["in_flight"] == [] and not sub.get("branch")
-    return error
-
-
-def started(cp: subprocess.CompletedProcess) -> None:
-    assert cp.returncode == 0, cp.stdout + cp.stderr
-
-
 # ----- the record -----------------------------------------------------------------------------
 
 def test_spec_add_records_the_integration_head(f):
diff --git a/tests/factory/test_stats.py b/tests/factory/test_stats.py
index 49fc59e..46b664d 100644
--- a/tests/factory/test_stats.py
+++ b/tests/factory/test_stats.py
@@ -19,9 +19,9 @@ import os
 import subprocess
 from pathlib import Path
 
-from .test_instance import BIN, STRIP, js, tree
-from .test_instance import cli as factory_cli
-from .test_live_store_guard import snapshot, start_triage, state, target  # noqa: F401  (target is a fixture)
+from ._cli import BIN, STRIP, js, tree
+from ._cli import cli as factory_cli
+from ._fixtures import snapshot, start_triage, state, target  # noqa: F401  (target is a fixture)
 
 # store, run id, ticket, model, spec_version, started, finished, wall_s, status
 RUNS = [
diff --git a/tests/factory/test_store_branch.py b/tests/factory/test_store_branch.py
index ec781a1..fe7d55c 100644
--- a/tests/factory/test_store_branch.py
+++ b/tests/factory/test_store_branch.py
@@ -12,36 +12,17 @@ their identity in GIT_AUTHOR_* / GIT_COMMITTER_*, because the suite runs under a
 """
 from __future__ import annotations
 
-import os
 import subprocess
 from pathlib import Path
 
 import pytest
 
-from .test_instance import cli, git_repo, js, tree
+from ._cli import cli, git_repo, js, tree
+from ._fixtures import BRANCH, IDENT, exclude, git, request, state
 
-BRANCH = "factory-store"
-IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
 RULE = "role runs may not write the live store"
 
 
-def git(cwd: Path, *argv: str, check: bool = True) -> str:
-    env = {**os.environ, **IDENT}
-    cp = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, env=env)
-    if check:
-        assert cp.returncode == 0, (argv, cp.stderr)
-    return cp.stdout.strip()
-
-
-def state(t: Path) -> Path:
-    return t / ".factory" / "state"
-
-
-def exclude(t: Path) -> Path:
-    p = Path(git(t, "rev-parse", "--git-path", "info/exclude"))
-    return p if p.is_absolute() else t / p
-
-
 def files(t: Path) -> dict[str, bytes]:
     """Every file under the target, its git directory aside, plus the exclude file."""
     snap = {k: v for k, v in tree(t).items() if not k.startswith(".git/")}
@@ -62,12 +43,6 @@ def target(tmp_path: Path) -> Path:
     return t
 
 
-def request(tmp_path: Path) -> str:
-    p = tmp_path / "r.md"
-    p.write_text("# demo\n\nDo the thing.\n")
-    return str(p)
-
-
 def start_triage(t: Path, tmp_path: Path) -> Path:
     assert cli(t, "ticket", "new", "--file", request(tmp_path)).returncode == 0
     cp = cli(t, "run", "start", "--role", "triage", "--ticket", "T-0001")
diff --git a/tests/factory/test_store_migrate.py b/tests/factory/test_store_migrate.py
index 77ee94b..e460c8c 100644
--- a/tests/factory/test_store_migrate.py
+++ b/tests/factory/test_store_migrate.py
@@ -23,8 +23,8 @@ from pathlib import Path
 import pytest
 import yaml
 
-from .test_instance import REPO, STRIP, cli, git_repo, js, tree
-from .test_store_branch import BRANCH, IDENT, exclude, git, request, state
+from ._cli import REPO, STRIP, cli, git_repo, js, tree
+from ._fixtures import BRANCH, IDENT, exclude, git, request, state
 
 NEW = ".factory/store"
 SCRATCH = "runs/run-0001-triage/scratch"
diff --git a/tests/factory/test_subtickets.py b/tests/factory/test_subtickets.py
index 5dfd2d0..d072939 100644
--- a/tests/factory/test_subtickets.py
+++ b/tests/factory/test_subtickets.py
@@ -8,45 +8,7 @@ import yaml
 
 from ._cli import REPO, approved_parent, run, ticket
 from ._cli import js_ok as js
-
-PLAN_LETTERS = """# Plan — T-0001: alert the operator
-
-## Grounding for this plan
-Checked on this base.
-
-## Fixture (prelude for every sub-ticket)
-```
-cat > /tmp/fx.py <<'PY'
-## not a heading
-PY
-```
-
-## T-0001-A / Emit the truncation event
-**Depends on:** none. Lands first.
-
-**Parallel-safe:** yes, alongside T-0001-C. The two edit disjoint files.
-
-Scope: A
-
-## T-0001-C / Retire the margin signal
-**Depends on:** none. Lands second, before T-0001-B.
-
-**Parallel-safe:** yes, alongside T-0001-A (disjoint files).
-
-## T-0001-B / Re-anchor the check
-**Depends on:** T-0001-C.
-
-**Parallel-safe:** no. Same file as T-0001-C.
-
-## Coverage map
-- criterion 1 → T-0001-A
-
-## Out-of-scope observations
-none
-STATUS: PLANNED
-CONFIDENCE: high, fixture
-ESCALATIONS: none
-"""
+from ._fixtures import PLAN_LETTERS
 
 PLAN_ST = """# Plan — T-0002 (SPEC-26): warn before a prompt stops fitting
 
diff --git a/tests/factory/test_whole_spec_plan.py b/tests/factory/test_whole_spec_plan.py
index f644648..c08422b 100644
--- a/tests/factory/test_whole_spec_plan.py
+++ b/tests/factory/test_whole_spec_plan.py
@@ -20,8 +20,7 @@ import pytest
 import yaml
 
 from ._cli import CliStore, git_repo
-from .test_parent_close_reuse import _build, _parent_verifier_runs
-from .test_shepherd import Shepherd
+from ._fixtures import Shepherd, _build, _parent_verifier_runs
 
 REASON = "one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run"
 SPEC_WRITER_OUTPUT = """=== proposal.md
