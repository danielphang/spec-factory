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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0397-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0397-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0397-verifier/wt` (branch `factory/T-0031.2`, base `2bd99697e3bdbe0ae735294afae1b3109070d7c6`, head `da50576fd4215aa31d4d8091e089c8f50cb791e5`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0031.2

### ST-1 / Role commands drop an inherited VIRTUAL_ENV, and build checkouts start with a synced environment
Depends on: none
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0031/v3.md` (T-0031, approved spec v3). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: every lettered part of the parent's Proposed change, A to F.

Notes for the implementer: `main` has moved since the spec was checked at `b002c95` (T-0027 merged). The code the spec names is unchanged, but its line numbers have moved. Re-locate it before you edit. Lines checked on `main` at `2bd9969`:
- `wrap()` and `run_env()`: `factory/compose.py:147-168`.
- The "Where you work" block: `factory/compose.py:343-354`. The SKIPPED lines are at 352 and `parts.append(where)` is at 354.
- `_start_build_run()`: `factory/cli.py:361-392`.
- The `meta.yaml` write is at `factory/cli.py:227` and the in-flight append at 238. Both still come after `_start_build_run` returns at 226.

The changelog's last entry is now 65, so this change appends 66, the next free number, as part F allows.

Acceptance:
Run each item from the repository root of the checkout under test, after `uv sync --frozen`. Use the GIVEN fixture block of the first scenario, written once, exactly as the parent spec gives it.
- NEW. A role's wrapper and its wrapped gate command drop an inherited virtual environment.
  WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && for c in "$(wrapper $S/runs/$R/input.md ". $T31/probe.sh")" "$(gate $S/runs/$R/input.md)"; do VIRTUAL_ENV=$V PYTHONHOME=$V PATH=$V/bin:$PATH sh -c "$c"; done)`
  THEN it prints exactly two lines, each `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh`.
- NEW. An implementer's worktree is synced through the wrapper at every dispatch, and its input says so.
  WHEN the parent's command for this scenario, verbatim (it sets `SYNC="'env > synced.env'"`, starts the implementer twice with a fake `VIRTUAL_ENV` on `PATH`, and finishes the first run with `--status-override KILLED` in between).
  THEN it prints exactly `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1`, then `again: synced=yes`.
- NEW. A checker's checkout is synced before the checker starts, and its input says so.
  WHEN the parent's command for this scenario, verbatim (a reviewer start on a commit on `factory/T-0001.1`).
  THEN it prints exactly `synced=yes ve=0 venv_on_path=0 noted=1`.
- NEW. A failed sync refuses the run start with a one-line reason, keeps its output in a log, and leaves no run or checker checkout.
  WHEN the parent's command for this scenario, verbatim (`SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"`, then an implementer start and a reviewer start).
  THEN it prints exactly `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `in_flight=1 checker_checkouts=0 meta=0`.
- REGRESSION. Without environment_sync, run start and the input are as before.
  WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "started=$([ -n "$R" ] && echo yes || echo no) noted=$(grep -c 'already synced' $S/runs/$R/input.md) recorded=$(grep -c '^environment_sync:' $S/runs/$R/meta.yaml) files=$(git -C $S/worktrees/T-0001.1 status --porcelain --untracked-files=all | grep -c .)")`
  THEN it prints exactly `started=yes noted=0 recorded=0 files=0`.
- NEW. The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes.
  WHEN the parent's command for this scenario, verbatim.
  THEN it prints exactly `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0`.
- NEW. The changelog records the environment sync as its last entry.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
  THEN it prints `CONTIGUOUS`, then `4`.
- REGRESSION. The environment-sync change adds no whitespace errors.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`.
- Intermediate check, REGRESSION. The harness suite passes with the two listed test edits and the new `tests/factory/test_environment_sync.py`, and with no other existing test changed.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  THEN it reports no failures.

Interim tests: none

Tests to change: the parent's list, and nothing else:
- `tests/factory/test_run_isolation.py`: the `WRAP` constant (line 22) only. It gains the part A prefix, as the parent gives it.
- `tests/factory/test_gate_paths.py`: the `want` line (line 217) only, in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. It gains the part A prefix, as the parent gives it.

Protected paths: `factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml` (the parent's whole Risk list).

Out of scope:
- Setting `environment_sync` on either instance (Operator steps).
- Anything on T-0031.1's v2 branch.
- `build.js` park-reason quoting.
- Other leak paths, such as `PYTHONPATH` and `CONDA_PREFIX`.
- A time limit on the sync.
- Any prompt copy under `docs/prompts/` or `factory/prompts/`.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The spec's design asks for one PR of about 225 lines with one changelog entry. Its parts depend on each other through the same code and tests. Part A (the wrapper prefix) is what makes the sync's environment clean in part C, and the sync scenarios check both at once (`ve=0 venv_on_path=0`). Parts B to D share `factory/compose.py` and `factory/cli.py` and one new test file. Part F writes one changelog entry for A to D. Splitting A from B–D would need two changelog entries or a document part that waits on both, and two serial merges on the same two files. That adds a re-verify round and makes neither review nor rollback easier.

This plan supersedes T-0031.1, which was planned from v2 and is parked. Its branch `factory/T-0031.1` holds one commit (`f13e707`) built to v2. The new sub-ticket does not depend on it and does not build on that branch.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0031/v3.md`

=== proposal.md
## Problem
Every agent that builds or checks code here loses a first attempt to a broken Python environment. The cost lands on the three build roles: the implementer, which writes the change, and the reviewer and verifier, which check it. A role is one agent job that the harness starts. The harness is the program that prepares each agent run and keeps its records. Each build role works in a fresh copy of the repository. For the implementer that copy is a git worktree on its branch. For a checker it is a detached checkout of the commit under review. Today two things go wrong in that copy.

First, the role's shell inherits a Python virtual environment that was activated in the session that launched the factory. On this machine that environment belongs to another checkout of a different repository. Its `python` and `pytest` come first on `PATH`, and uv warns about it on every command. The running-code wrapper does not remove it. That wrapper is the one-line shell prefix every role is told to put around each command it runs. It gives the command a throwaway home directory, and it also wraps the repository's check commands (the gate commands).

Second, the fresh copy has no project environment (`.venv`). A check command that tells uv not to install anything (`uv run --no-sync`) runs in an empty environment and fails on its first import. The implementer, then the reviewer, then the verifier each find this out, install the environment themselves, and run again. A checker that does not can report the import failure as a defect in the code it is checking.

This change does three things:
- The wrapper drops an inherited virtual environment.
- A repository can name one command, `environment_sync`, in its configuration file. A repository that runs the factory is called an instance, and its configuration file is `instance.yaml`. The harness runs the command in each build copy before the role starts.
- The role is told that the environment is already synced.
A repository that does not set the command behaves as it does today, apart from the wrapper change.

This is the third version of this spec. The operator approved version 2 on 2026-10-04. Its build then stopped: an existing test, added after version 2 was written, checks the old wrapper text, and version 2 did not list it as a test the change may edit. This version lists it, re-checks every reference against the current `main` (`b002c95`), and changes the design in two places where later merges conflict with it (Decisions, marked "Changed from version 2").

## Root cause
- `factory/compose.py:164-168`, `wrap()`: it builds `(export HOME=<fresh>[ run_env exports]; <command>)`. It never removes an inherited virtual environment. A role's shell inherits the launching session's environment, so `VIRTUAL_ENV`, `PYTHONHOME` and the environment's `bin/` on `PATH` all reach every command. The "Running code" section (line 183) and the gate-commands line (lines 321-323) both use it.
- `factory/compose.py:147-161`, `run_env()`: it accepts only name-to-value pairs, so an instance cannot use it to unset a variable.
- `factory/cli.py:269-299`, `_start_build_run()`: it creates the implementer's worktree (line 281, only when missing) or the checker's detached checkout (line 295) and copies `environment_files` (lines 286 and 296). It runs no command, so a new copy has no `.venv`.
- `factory/instance.template.yaml` and `.factory/instance.yaml` have no key that names a sync command.

## Out of scope
- The wrapper's other behaviour: the fresh HOME, the `run_env` exports and their order, and the prose of the "Running code" section. Only the wrapper's prefix changes.
- Every gate command, acceptance criterion and check, on both instances.
- Other ways a Python environment can leak in (`PYTHONPATH`, conda's `CONDA_PREFIX`). Nothing reported them.
- A time limit on the sync.
- Setting `environment_sync` on either instance. That is an operator step.
- The `harness-bug:` prefix that the build workflow already puts on a refused run start's park reason.
- The build workflow's quoting of park reasons (`build.js:62`), which expands a backtick or `$` in any reason. This change keeps its own refusal free of them; other refusals that relay arbitrary text are a separate issue.

## Open questions
none

## Decisions
- The wrapper fully deactivates an inherited virtual environment. It removes the exact entry `$VIRTUAL_ENV/bin` from `PATH`, then unsets `VIRTUAL_ENV` and `PYTHONHOME`, all before it sets HOME. Rejected: unsetting only the two variables, as the requester proposed. The activating shell also put the environment's `bin/` first on `PATH`, so a bare `python` or `pytest` would still run the other repository's environment (Evidence).
- The deactivation is built into the wrapper for every instance, not configured per instance. Rejected: a way to unset variables through `run_env`. Every instance needs the deactivation, and opting in would leave it off by default. `run_env` is the list of variables an instance gives the wrapper to export after the throwaway HOME. Its exports still come after the deactivation, so an instance that wants a particular environment can still name it there.
- `environment_sync` is one optional shell command, given as a string in `instance.yaml`. If it is absent or null, nothing runs, as today. Any other non-string or empty value is refused at run start, before any checkout is made.
- The sync runs at every build-role run start, for the implementer, reviewer and verifier, including the verifier that checks the parent ticket after all its sub-tickets merge. It runs in that run's checkout, after the environment files are copied, through the same wrapper as role commands, so it gets the throwaway HOME, the `run_env` exports and no inherited environment. Rejected: syncing only when the implementer's worktree is first created. The environment files are copied again at every run start. A conflict run, which is an implementer run after the merge step refused the branch, merges in the integration branch, the branch that finished tickets merge into. Either can change the lock file the environment was built from. The reviewer is synced too, although it no longer runs the gate commands: its prompt still lets it run one test to confirm a finding (Evidence).
- Changed from version 2: a failed sync refuses the run start with exit 2 and a one-line error, `environment_sync failed (exit <code>) in <checkout>; its command and output are in <log>`. The log is `runs/<id>/environment-sync.log`, in the run directory that run start had already reserved. It holds the command, the exit code and the command's full output. The error carries neither the command nor its output. No run is recorded or put in flight, and a checker checkout made for the run is removed. The implementer's worktree is kept for the next dispatch. The build workflow, the script that dispatches the build roles in turn, then parks the ticket: it stops the ticket and leaves it for a human. It uses its existing park reason `harness-bug: run start <role>: …`, so a broken environment never reaches a checker as a code failure. Rejected: version 2's error with the command and its last 20 output lines. The workflow passes the reason to the shell in double quotes, which expand the backticks that uv's errors contain, and the command is the operator's free text (Evidence). Rejected: starting the role anyway with a note. The role would then rediscover the broken environment, which is the cost this change removes.
- When the sync ran, the run's record file, `meta.yaml`, stores the command under `environment_sync`. Changed from version 2: the role's input gains one line at the end of its "Where you work" section, after any SKIPPED lines. The line says the command ran, the environment is already synced, and the role should not sync again unless its change alters the files the environment is built from. Rejected: version 2's "after the gate-commands line", which the reviewer's input no longer has (Evidence).
- This change sets `environment_sync` on neither instance. The operator sets it after the runtime, the separate checkout the factory runs from, has moved to the new harness revision (Operator steps). Rejected: setting it on this instance in the PR. That writes the protected `.factory/**`, and the key has no effect until the runtime runs the new harness anyway.

## Risk
Protected paths: `factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`

- These three harness files are the only protected paths this change touches. It touches none of infra (`.factory/**`), generated (`docs/prompts/**`), `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `factory/prompts/**`, `factory/workflows/**`, the reference harness or credentials.
- Guardrail paths: two existing test files, `tests/factory/test_run_isolation.py` and `tests/factory/test_gate_paths.py`. In each, one expected-text line changes, as listed under Tests to change.
- Blast radius: after the runtime upgrade, every role input's wrapper and every wrapped gate command on both instances carry the new prefix. A broken prefix would break every command every role runs. The first scenario runs the composed wrapper and the wrapped gate command under `sh`, and the prototype ran them under bash and zsh. The prefix does nothing when `VIRTUAL_ENV` is unset. Otherwise it removes only the exact `$VIRTUAL_ENV/bin` entry from `PATH`. Its `tr`/`paste` round trip also drops an empty `PATH` entry (one that means the current directory), as run-0366 found; no reported setup relies on one.
- An instance whose commands relied on an inherited, activated environment loses it inside the wrapper. It can name that environment in `run_env`.
- The sync runs inside `run start`, which the workflow's clerk runs as one shell command. The clerk is the agent that runs the harness's store commands for a workflow, and its shell tool stops a command after 2 minutes by default. A slow sync, such as uv with a cold cache, can run past that limit. The clerk then reports a failure, the workflow parks the ticket, and a checker checkout may be left behind for the operator to remove with `git worktree remove`. A uv cache pinned through `run_env` (Operator steps) keeps a repeat sync short.
- The sync runs the checkout's own build configuration (uv installs the project itself when the project is a package) before the role starts. This happens under the throwaway HOME, and it is what the gate commands and the roles already do in the same checkout.
- Each build run start takes one sync longer. A failed sync leaves its reserved run directory holding only `environment-sync.log`. Every reader of `runs/` already skips a directory with no `meta.yaml` (`factory/compose.py:20-21`, `factory/specstore.py:277-280`, `factory/cli.py:1446-1449`).

## Operator steps
The factory does not run from the checkout where tickets merge. It runs from the runtime, a separate checkout of this repository pinned to one harness revision. A merged change therefore takes effect only after two steps, both described in README ("Upgrading the runtime" and "Accepting a harness revision"). First, the runtime is moved to the new revision. Second, each instance records that it accepts that revision, with `--accept-harness <commit>`; until then the harness refuses to work on that instance's store.

1. After this change merges, the runtime is upgraded and this instance has accepted the new revision. Then add `environment_sync: "uv sync --frozen"` to this repository's `.factory/instance.yaml`. That file is protected infra, so only the operator edits it. With the key set, every build checkout has the `.venv` that this repository's acceptance scenarios already assume ("after `uv sync --frozen`"). Optional: add `UV_CACHE_DIR` to `run_env`, as instance A does, so each sync reuses the uv cache instead of filling a new one in each throwaway HOME.
2. Tell the Driver that the key exists. The Driver is the separate operator-run session that runs instance A's tickets. After instance A accepts the new revision, the Driver may set `environment_sync: "uv sync --frozen --all-extras --dev"` there. Before it does, it should check that `run_env` holds every uv variable its gate commands set, because the sync sees only the throwaway HOME and the `run_env` exports. Today that holds: its gate commands set `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR`, and its `run_env` pins both (`~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-27). Its `environment_files` copies `uv.lock` into each checkout (line 54) before the sync runs.

=== design.md
## Proposed change
One PR, about 225 changed lines: about 45 in the harness, 150 in a new test file, 5 in two existing tests and about 20 in documents.

**A. The wrapper drops an inherited virtual environment** (`factory/compose.py`, `wrap()`).
- Put this prefix, verbatim, right after the opening parenthesis and before `export HOME=`:
  `[ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; `
  (here `'\n'` is the two characters backslash and `n` inside single quotes, so `tr` gets a newline).
- The wrapper becomes `(<prefix>export HOME="$(cd "$(mktemp -d)" && pwd -P)"[ run_env exports]; <command>)`.
- It must contain no backtick, because it is shown inside backticks.
- Keep it as a module constant with a one-line comment saying what it does.
- Update the docstring. Leave the "Running code" section's prose unchanged.
- Gate commands pick up the prefix through the same `wrap()`.

**B. The `environment_sync` key** (`factory/instance.template.yaml`, `factory/compose.py`).
- Template: add `environment_sync: null` after `run_env`, with a comment. The comment says: one shell command the harness runs in each build checkout at run start, through the running-code wrapper, after the environment files are copied (for example `uv sync --frozen`); null means none; a failure refuses the run.
- `compose.environment_sync(cfg) -> str | None`: absent or null gives None. A non-empty string gives that string. Anything else raises `store.Refused` with text that names `environment_sync`.

**C. Sync at run start** (`factory/cli.py`, `_start_build_run()`).
1. Call `compose.environment_sync(cfg)` first, before any worktree or checkout is created, so that a bad value writes nothing.
2. After the checkout is set up and `copy_environment_files` has run, in both branches (implementer, and checker including the parent-close verifier), if a command is set, run it like this: `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`. The sync's output must never reach run start's stdout, whose last line stays its JSON.
3. On exit 0, set `meta["environment_sync"] = cmd`.
4. On a non-zero exit:
   - Write `d / "environment-sync.log"` (`d` is the run directory `_start_build_run` receives): the command, the exit code, then the command's stdout and stderr in full.
   - For a checker, remove the checkout it just made (`gitops.remove_worktree`). Keep the implementer's worktree.
   - Raise `Refused(f"environment_sync failed (exit {code}) in {wt}; its command and output are in {log}")`, one line, with no command text and no output.
   - Because `meta.yaml` and the in-flight list are written only after `_start_build_run` returns (`factory/cli.py:225` and `236`), the refusal records no run and puts nothing in flight.

**D. The role is told** (`factory/compose.py`, the "Where you work" block, lines 315-326). When `meta.get("environment_sync")` is set, append this line at the end of the block, after any SKIPPED lines and before `parts.append(where)`, as its own line ending in a newline. It applies to the implementer, reviewer and verifier alike:
`Environment: the harness ran this instance's environment sync, `<command>`, in this checkout through the running-code wrapper before you started, so the environment is already synced. Do not sync it again unless your change alters the files it is built from.`
When the key is not set, the input is as today.

**E. Tests.**
- Make the two edits listed under Tests to change.
- Add `tests/factory/test_environment_sync.py`. It is black-box through `bin/factory`, on throwaway stores, with a copy of the suite's fixture instance where the key is set, in the style of `test_run_isolation.py`. It covers:
  - the composed wrapper run under `sh` with a fake activated environment: `VIRTUAL_ENV` and `PYTHONHOME` are unset, the environment's `bin/` is off `PATH` while the other `PATH` entries stay in order, and a `PATH` with no environment is unchanged;
  - the sync at an implementer start and again at a later dispatch to the same worktree;
  - the sync at a reviewer start and at a parent-close verifier start;
  - the sync's environment: no `VIRTUAL_ENV`, a fresh HOME, the `run_env` exports;
  - a failed sync: exit 2, the one-line refusal with no backtick, `$` or double quote, the log holding the command and its output, nothing in flight, no checker checkout, no `meta.yaml`;
  - a non-string `environment_sync` refused before any checkout is made;
  - the input line present, for an implementer and a reviewer, when the sync ran, and absent when no key is set.

**F. Documents.**
- `docs/design.md`, in the "Role-context block" paragraph:
  - add `environment_sync` to the parenthetical list of what `instance.yaml` holds;
  - say that the running-code wrapper first drops an inherited virtual environment (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset);
  - add one sentence: when the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the output in the run's `environment-sync.log`), and the role's input says the environment is already synced.
- `docs/changelog.md`: append the next contiguously numbered entry (64 on today's `main`, or the next free number when it merges). It records parts A to D in prose and names `environment_sync`, `VIRTUAL_ENV`, `PYTHONHOME` and the "already synced" line.
- `dev/build-harness.spec.md`, part I: add one item after I.3. It says that each build checkout runs the instance's `environment_sync`, if set, through the running-code wrapper at `run start`, before the role starts, and that a failure refuses the run with its output in `runs/<id>/environment-sync.log`.
- `README.md`:
  - In "Roles, harness, workflows", extend the wrapper sentence (line 30): the wrapper also drops a Python virtual environment inherited from the launching shell (`VIRTUAL_ENV`, `PYTHONHOME`, and its `bin/` on `PATH`).
  - In "Adopting the factory in a repo", step 3: set `environment_sync` to the command that installs the repo's environment, so each build checkout starts synced.
  - Bump the status date if the merge falls on a later day.
- No copy under `docs/prompts/` or `factory/prompts/` changes: no prompt block names the wrapper's contents.

## Tests to change
- `tests/factory/test_run_isolation.py`, the `WRAP` constant (line 22) only. It holds the exact expected wrapper text that five tests (six cases) compare against: `test_triage_input_carries_the_section_right_after_the_output_file`, `test_planner_and_implementer_inputs_carry_the_section_once`, `test_implementer_gate_commands_come_wrapped`, `test_run_env_is_exported_after_home_in_file_order_and_quoted` and both cases of `test_empty_or_null_run_env_exports_nothing`. Part A changes that text by design. The constant gains the part A prefix, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the constant is a `str.format` template. The prototype's replacement for line 22, which made those six cases pass:

```python
WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
        'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})')
```

  No assertion is removed or loosened, and `SECTION` is unchanged.
- `tests/factory/test_gate_paths.py`, line 217 only: the `want` string in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. It builds the expected wrapped gate command from the old wrapper text, so its unscoped-mapping case fails once part A adds the prefix. The expected text gains the part A prefix before `export HOME=`, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the string is an f-string. Nothing else in the file changes: the test's other two cases (`want` empty), its assertions and every other test stay as they are. The prototype's replacement for line 217 (two lines, same indentation):

```python
    want = (f"`([ -z \"${{VIRTUAL_ENV:-}}\" ] || PATH=$(printf %s \"$PATH\" | tr : '\\n' | grep -vxF \"$VIRTUAL_ENV/bin\" | paste -sd: -); "
            f"unset VIRTUAL_ENV PYTHONHOME; export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else "")
```

- No other existing test changes. The whole suite went from `7 failed, 401 passed` with the prototype to `408 passed` with these two edits, the same count as the unchanged base (Evidence).

=== specs/run-environment/spec.md
## ADDED Requirements

### Requirement: The running-code wrapper drops an inherited virtual environment
The running-code wrapper in every role's input, and around every gate command, MUST remove `$VIRTUAL_ENV/bin` from `PATH` and unset `VIRTUAL_ENV` and `PYTHONHOME` before it sets the fresh HOME and exports `run_env`, and SHALL still give each command a fresh HOME and the `run_env` exports.

#### Scenario: A role's wrapper and its wrapped gate command drop an inherited virtual environment
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0031-env.sh <<'EOF'
# Sourced from the repo root, with SYNC set to an environment_sync value for instance.yaml, or empty
# for none. Makes a scratch target with its own instance, used on a throwaway store $S, whose T-0001
# is approved and split into T-0001.1, ready for its implementer. The instance exports T31_CACHE
# through run_env and has one gate command, which runs the probe. $V is a fake virtualenv holding a
# `python`. The shell is left in the target.
B=$PWD/bin/factory; T31=$(cd "$(mktemp -d)" && pwd -P); V=$T31/venv
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
rid() { tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'; }
has() { grep -qF -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
wrapper() { sed -n 's/^.*home directory: `\([^`]*\)`\. Put your command.*$/\1/p' "$1" | sed "s#<command>#$2#"; }
gate() { sed -n 's/^.*each is already wrapped): `\([^`]*\)`$/\1/p' "$1"; }
mkdir -p $V/bin && printf '#!/bin/sh\necho fake\n' > $V/bin/python && chmod +x $V/bin/python
printf 'echo "ve=${VIRTUAL_ENV:-unset} ph=${PYTHONHOME:-unset} fake_python=$(command -v python | grep -c %s) cache=${T31_CACHE:-unset} home=$([ "$HOME" = "%s" ] && echo caller || echo fresh)"\n' "$V/bin" "$HOME" > $T31/probe.sh
git init -q -b main $T31/tgt && cd $T31/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1
grep -v -e '^run_env:' -e '^gate_commands:' -e '^environment_sync:' .factory/instance.yaml > $T31/i.yaml
printf 'run_env: {T31_CACHE: /tmp/t31-cache}\ngate_commands: [". %s/probe.sh"]\n%s\n' "$T31" "${SYNC:+environment_sync: $SYNC}" >> $T31/i.yaml && mv $T31/i.yaml .factory/instance.yaml
export FACTORY_STATE=$T31/store; S=$T31/store
printf '# F\n\nDo x.\n' > $T31/req.md && printf '## Problem\nx\n' > $T31/spec.md
$B ticket new --file $T31/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
$B spec add T-0001 --file $T31/spec.md >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T31/plan.md && $B subticket add T-0001 --file $T31/plan.md >/dev/null
EOF
```

- WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && for c in "$(wrapper $S/runs/$R/input.md ". $T31/probe.sh")" "$(gate $S/runs/$R/input.md)"; do VIRTUAL_ENV=$V PYTHONHOME=$V PATH=$V/bin:$PATH sh -c "$c"; done)`
- THEN it prints exactly two lines, each `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` (the first from the role's wrapper, the second from the wrapped gate command)

### Requirement: Each build checkout is synced before its role starts
When the instance sets `environment_sync`, `run start` for the implementer, reviewer and verifier SHALL run that command once in the run's checkout, at every run start, after the environment files are copied, through the running-code wrapper. The role's input SHALL then name the command and say the environment is already synced.

#### Scenario: An implementer's worktree is synced through the wrapper at every dispatch, and its input says so
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC="'env > synced.env'"; . ${TMPDIR:-/tmp}/t0031-env.sh && E=$S/worktrees/T-0001.1/synced.env && R=$(VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "first: synced=$([ -f $E ] && echo yes || echo no) ve=$(grep -c '^VIRTUAL_ENV=' $E 2>/dev/null) venv_on_path=$(grep '^PATH=' $E 2>/dev/null | grep -c "$V/bin") cache=$(has T31_CACHE=/tmp/t31-cache $E) home=$(grep -qx "HOME=$HOME" $E 2>/dev/null && echo caller || echo fresh) noted=$(grep 'env > synced.env' $S/runs/$R/input.md | grep -c 'already synced')" && $B run finish $R --status-override KILLED >/dev/null && rm -f $E && VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role implementer --ticket T-0001.1 >/dev/null && echo "again: synced=$([ -f $E ] && echo yes || echo no)")`
- THEN it prints exactly `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1`, then `again: synced=yes`

#### Scenario: A checker's checkout is synced before the checker starts, and its input says so
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC="'env > synced.env'"; . ${TMPDIR:-/tmp}/t0031-env.sh && git checkout -q -b factory/T-0001.1 && git commit -q --allow-empty -m work && H=$(git rev-parse HEAD) && git checkout -q main && $B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null && R=$(VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role reviewer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && E=$S/runs/$R/wt/synced.env && echo "synced=$([ -f $E ] && echo yes || echo no) ve=$(grep -c '^VIRTUAL_ENV=' $E 2>/dev/null) venv_on_path=$(grep '^PATH=' $E 2>/dev/null | grep -c "$V/bin") noted=$(grep 'env > synced.env' $S/runs/$R/input.md | grep -c 'already synced')")`
- THEN it prints exactly `synced=yes ve=0 venv_on_path=0 noted=1`

### Requirement: A failed sync stops the run before it starts
When `environment_sync` exits non-zero, `run start` MUST refuse with exit 2 and a one-line error that names `environment_sync`, the exit code and a log file in the run's directory holding the command's output, and that carries no backtick, `$` or double quote. It MUST leave no run in flight and no checker checkout behind.

#### Scenario: A failed sync refuses the run start with a one-line reason, keeps its output in a log, and leaves no run or checker checkout
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once. The sync command computes its output text and exit code, so that neither `sync-2` nor `exit 3` appears in the command itself, and it contains `$`, so a refusal that quoted it would count.
- WHEN `(SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"; . ${TMPDIR:-/tmp}/t0031-env.sh && $B run start --role implementer --ticket T-0001.1 >/dev/null 2>$T31/e1; i=$?; git -C $S/worktrees/T-0001.1 commit -q --allow-empty -m work && H=$(git -C $S/worktrees/T-0001.1 rev-parse HEAD) && $B ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T31/e2; r=$?; rep() { L=$(sed -n 's/^.* are in \(.*environment-sync\.log\)$/\1/p' "$2"); echo "$1: exit=$3 named=$(has environment_sync "$2") code=$(has 'exit 3' "$2") shell_chars=$(tr -cd '\140$\042' < "$2" | wc -c | tr -d ' ') logged=$(has sync-2 "$L")"; }; rep implementer $T31/e1 $i; rep reviewer $T31/e2 $r; echo "in_flight=$($B ticket show T-0001.1 --json | tail -1 | grep -c '"in_flight": \[\]') checker_checkouts=$(git worktree list | grep -c '/runs/') meta=$(find $S/runs -name meta.yaml | grep -c .)")`
- THEN it prints exactly `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `in_flight=1 checker_checkouts=0 meta=0`

### Requirement: Without environment_sync, run start and the input are unchanged
When the instance does not set `environment_sync`, `run start` SHALL run no command in the checkout, record no sync, and the role's input SHALL carry no sync line.

#### Scenario: Without environment_sync, run start and the input are as before
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "started=$([ -n "$R" ] && echo yes || echo no) noted=$(grep -c 'already synced' $S/runs/$R/input.md) recorded=$(grep -c '^environment_sync:' $S/runs/$R/meta.yaml) files=$(git -C $S/worktrees/T-0001.1 status --porcelain --untracked-files=all | grep -c .)")`
- THEN it prints exactly `started=yes noted=0 recorded=0 files=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the environment sync and the dropped virtual environment
`docs/design.md` SHALL name `environment_sync` and say the wrapper drops `VIRTUAL_ENV`. `dev/build-harness.spec.md` SHALL name `environment_sync`. `factory/instance.template.yaml` SHALL carry an `environment_sync` key. `README.md` SHALL name `environment_sync` and `VIRTUAL_ENV`. `docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap. No prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change. The change MUST add no whitespace errors.

#### Scenario: The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes
- WHEN `(echo "design=$(grep -c environment_sync docs/design.md | awk '{print ($1 > 0)}') design_venv=$(grep -c VIRTUAL_ENV docs/design.md | awk '{print ($1 > 0)}') build_spec=$(grep -c environment_sync dev/build-harness.spec.md | awk '{print ($1 > 0)}') template=$(grep -c '^environment_sync:' factory/instance.template.yaml) readme=$(grep -c environment_sync README.md | awk '{print ($1 > 0)}') readme_venv=$(grep -c VIRTUAL_ENV README.md | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0`

#### Scenario: The changelog records the environment sync as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `4`

#### Scenario: The environment-sync change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
Each "today" result below was run in this round on a clone at `b002c95`, under bash and under zsh, with a fresh HOME and `TMPDIR`.
- A role's wrapper and its wrapped gate command drop an inherited virtual environment → NEW. Today both lines print `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`. The wrapper passes the inherited `VIRTUAL_ENV` and `PYTHONHOME` through, and the fake environment's `python` is found first.
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so → NEW. Today it prints `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0`, then `again: synced=no`: the `environment_sync` key is ignored and the input has no sync line.
- A checker's checkout is synced before the checker starts, and its input says so → NEW. Today it prints `synced=no ve= venv_on_path=0 noted=0`.
- A failed sync refuses the run start with a one-line reason, keeps its output in a log, and leaves no run or checker checkout → NEW. Today it prints `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `reviewer: exit=0 named=0 code=0 shell_chars=0 logged=0`, `in_flight=0 checker_checkouts=1 meta=2`: both runs start, both stay in flight, and the checker's checkout exists.
- Without environment_sync, run start and the input are as before → REGRESSION. Prints `started=yes noted=0 recorded=0 files=0` today.
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes → NEW. Today it prints `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`.
- The changelog records the environment sync as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`: the last entry (63) names none of the four terms.
- The environment-sync change adds no whitespace errors → REGRESSION. Prints `exit=0` today.

## PR description (the implementer's output)

Sub-ticket: T-0031.2 (parent T-0031, approved spec v3, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0031/v3.md`)
Branch: `factory/T-0031.2`, one commit `da50576` on base `2bd9969`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0031.2`.

## What changed
Build roles lost their first attempt to a broken Python environment. Their shells inherited the launching session's activated virtual environment (here `/Users/dphang/dev/nanobot/.venv-test`, which this run's own shell also had). Their fresh checkouts also had no `.venv`. The build roles are the implementer, the reviewer and the verifier. This change fixes both problems.

- **A. Wrapper** (`factory/compose.py`). The running-code wrapper is the shell prefix every role puts around each command, and the harness puts around each gate command. A new module constant `_DROP_VENV` holds the spec's prefix, verbatim, with a one-line comment. `wrap()` now emits `(<prefix>export HOME=...[ run_env exports]; <command>)`, and its docstring says so. The "Running code" prose is unchanged. Gate commands get the prefix through the same `wrap()`. I grepped the callers of `wrap()` before editing: `compose.py` (the Running code section and the gate-commands line) and, new in this change, `cli._sync_environment`.
- **B. Key** (`factory/instance.template.yaml`, `factory/compose.py`). The template gains `environment_sync: null` after `run_env`, with the comment the spec asks for. `compose.environment_sync(cfg)` returns None when the key is absent or null. It returns a non-empty string as given. Any other value raises `store.Refused` with text that names `environment_sync`.
- **C. Sync at run start** (`factory/cli.py`). `_start_build_run` reads the key first, before any checkout is made. The new `_sync_environment` runs after `copy_environment_files` in both branches. That covers the implementer and every checker, including the parent-close verifier. The checker branch runs it before `diff.patch` is written. It runs `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`, so its output never reaches stdout. On exit 0 it sets `meta["environment_sync"]`. On a non-zero exit it does three things:
  - It writes `runs/<id>/environment-sync.log`, holding the command, the exit code, and the full stdout and stderr.
  - For a checker, it removes the checkout with `gitops.remove_worktree`. The implementer's worktree is kept.
  - It raises `Refused("environment_sync failed (exit N) in <wt>; its command and output are in <log>")`.
  Because the refusal comes before `meta.yaml` and the in-flight list are written, no run is recorded.
- **D. Input line** (`factory/compose.py`, "Where you work"). When `meta["environment_sync"]` is set, the section gains the spec's `Environment: ...` line, word for word. It comes after any SKIPPED lines and before `parts.append(where)`.
- **E. Tests.** The two listed edits are made, each matching the spec's prototype text. The new test file is `tests/factory/test_environment_sync.py`, listed below.
- **F. Documents.**
  - `docs/design.md`, "Role-context block" paragraph: `environment_sync` is added to the list of what `instance.yaml` holds. The wrapper sentence now says it first drops an inherited virtual environment (`VIRTUAL_ENV`, `PYTHONHOME`, its `bin/` off `PATH`). One sentence is added on the sync, the refusal and its log, and the "already synced" input line.
  - `docs/changelog.md`: entry 66 (issue #51) records parts A to D and the rejected alternatives.
  - `dev/build-harness.spec.md`, part I: a sub-item under I.3 (see Known gaps).
  - `README.md`: one sentence added after the wrapper sentence in "Roles, harness, workflows". In "Adopting the factory in a repo", step 3 now says to set `environment_sync`. The status date is already 2026-10-09, today, so it was not bumped.
  - No file under `docs/prompts/` or `factory/prompts/` changes.

## Acceptance results
How they ran: each command was run from the worktree root after `uv sync --frozen`, through the wrapper (fresh HOME). The fixture file is the spec's GIVEN block, written verbatim to `$TMPDIR/t0031-env.sh`, with `TMPDIR` set to this run's scratch directory. The scenario commands were copied verbatim into `scratch/acc.sh`. The before outputs are in `scratch/acc-before.txt` and the after outputs in `scratch/acc-after.txt`. The after run was repeated under zsh, and S1 to S4 printed the same.

| Scenario | Before (base `2bd9969`) | After (`da50576`) |
|---|---|---|
| NEW wrapper and gate drop the inherited venv | two lines `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` | two lines `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` |
| NEW implementer synced at every dispatch | `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0` / `again: synced=no` | `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1` / `again: synced=yes` |
| NEW checker synced | `synced=no ve= venv_on_path=0 noted=0` | `synced=yes ve=0 venv_on_path=0 noted=1` |
| NEW failed sync refuses | `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0` / `reviewer: exit=0 ...` / `in_flight=0 checker_checkouts=1 meta=2` | `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `in_flight=1 checker_checkouts=0 meta=0` |
| REGRESSION without the key | `started=yes noted=0 recorded=0 files=0` | `started=yes noted=0 recorded=0 files=0` |
| NEW documents | `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0` | `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0` |
| NEW changelog | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `4` |
| REGRESSION whitespace | `exit=0` | `exit=0` |

Every NEW "before" matches the spec's verification.md "today" output.

Gates on `da50576`, each run exactly as written:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `496 passed in 309.94s`. That includes the 10 new tests and the two edited ones. The spec's figure of 408 was measured at `b002c95`; `main` has gained tests since.

## Tests added/changed
- Added `tests/factory/test_environment_sync.py`, 10 tests. It is black-box through `bin/factory`, on throwaway stores, with a copy of the fixture instance and a scratch target repo. It covers:
  - the composed wrapper under `sh` with a fake activated venv: both variables are unset, and only the exact `<venv>/bin` entry leaves `PATH`, with the other entries kept in order (a `<venv>/binx` entry stays). A `PATH` with no venv is unchanged.
  - an implementer sync at the first and at a later dispatch;
  - a reviewer sync, and a parent-close verifier sync;
  - the sync's environment: no `VIRTUAL_ENV` or venv `bin/`, a fresh HOME, and the `run_env` export;
  - a failed sync, for both the implementer and the reviewer: exit 2, a single line with no backtick, `$` or double quote and no command text or output, the log holding the command, its output and `exit: 3`, a run directory holding only the log, nothing in flight, no checker checkout, and the implementer's worktree kept;
  - malformed values (`[uv, sync]`, `""`, `3`) refused with no worktree and no run directory;
  - with no key: nothing recorded, no input line and a clean worktree, for an implementer and a reviewer.
  With the `factory/` changes stashed, 9 of the 10 failed for the expected reasons. The no-key test passed, as a regression test should.
- Changed `tests/factory/test_run_isolation.py`, the `WRAP` constant only. Part A changes the expected wrapper text by design. This is the replacement the spec gives.
- Changed `tests/factory/test_gate_paths.py`, the `want` line only, in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. The reason is the same, and this is also the spec's replacement.
- No other existing test changed.

## Known gaps and uncertainties
- **Deviation, refusal timing.** Spec part C.1 says to call `compose.environment_sync(cfg)` first in `_start_build_run` "so that a bad value writes nothing". The run directory is reserved before `_start_build_run` runs. A refusal there would leave an empty `runs/<id>/` behind. So I also call it in `run_start` next to `compose.gate_entries(cfg)`, before the run id is reserved, as that function already does (`factory/cli.py:218`). `_start_build_run` still reads the key first (line 367). A malformed value therefore leaves no run directory, and the test asserts that.
- **Placement in the build spec.** Part F says "add one item after I.3". Renumbering I.4 to I.6 would break references elsewhere: `dev/build-harness.spec.md` lines 97, 206, 411 and 507, and `dev/build-harness.plan.md`. So the addition is an indented sub-item of I.3, and the numbers stay as they are.
- **README tense.** README's "Maintaining this page" says behaviour appears above "Where this can go" only after it has run on a real ticket. The spec asks for the two README sentences in this PR, and I followed the spec. The sync has not yet run on a real ticket, because neither instance sets the key yet (Operator steps).
- **Test without `PYTHONHOME`.** The new tests launch `bin/factory` with `VIRTUAL_ENV` and the venv `bin/` on `PATH`, but not `PYTHONHOME`. Pointing `PYTHONHOME` at the fake venv breaks the harness's own interpreter ("No module named 'encodings'"). The wrapper test covers `PYTHONHOME`.
- **Sync time limit.** As the spec's Risk says, the sync has no time limit and runs inside the clerk's `run start` call.
- `factory:` markers added: none.

## Out-of-scope observations
- On macOS, `mktemp -d` ignores `TMPDIR` in this environment. So the scenarios' temporary targets went to `/var/folders/.../T/`, not this run's scratch directory. Only the fixture file and the logs are in scratch.
- The operator's step to set `environment_sync` on each instance is still pending, by design.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All eight acceptance commands and both gates were run on `da50576` and printed the expected output, and the four NEW scenarios that test behaviour printed the spec's "today" output on the base.
ESCALATIONS: none

## Diff `2bd99697e3bdbe0ae735294afae1b3109070d7c6...da50576fd4215aa31d4d8091e089c8f50cb791e5`

diff --git a/README.md b/README.md
index 51be5e8..bd08bf1 100644
--- a/README.md
+++ b/README.md
@@ -28,6 +28,7 @@ built, who checked it against what, and why it was allowed through.
 declared inputs: the critic never sees the writer's reasoning, the reviewer never sees the
 implementer's.
 Every role's input carries a wrapper that runs a command with a fresh temporary HOME, and the repo's check commands come already wrapped.
+The wrapper also drops a Python virtual environment inherited from the launching shell (`VIRTUAL_ENV`, `PYTHONHOME`, and its `bin/` on `PATH`).
 It does not stop a write to an absolute path.
 
 | Role | Does | Model |
@@ -587,7 +588,10 @@ From inside the target repo, with `R` the runtime (`~/dev/spec-factory-harness`)
    command covers: `{command: "<command>", paths: [":(exclude)dev/"]}`. A sub-ticket whose changes
    touch none of them skips that command. Prefer exclude pathspecs, so a new file still runs the
    command. Set `run_env` for any tool whose cache lives under HOME,
-   so it still finds that cache from inside the fresh temporary HOME.
+   so it still finds that cache from inside the fresh temporary HOME. Set `environment_sync` to the
+   command that installs the repo's environment (for example `uv sync --frozen`), so each build
+   checkout starts synced: `run start` runs it in the checkout before the role starts, and refuses
+   the run if it fails.
 
 The repo is now a target. "Starting a run" is the rest.
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 4b989d6..814042c 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -297,6 +297,7 @@ Resumption after a human decision: the `/factory` skill re-runs `build.js` for t
 1. System prompt = the agent definition (`factory/prompts/preamble.md` is read by its first instruction); the clerk records it in `runs/<run_id>/system-prompt.txt`.
 2. Input composed by `factory run compose RUN` (B): the role-context block (doc §Harness), then exactly the declared sources (H), written as `runs/<run_id>/input.md` with `input_sources:` in `meta.yaml` **before** the role runs; the role's prompt is a pointer to that file, so what the role saw is auditable and no second composition path exists.
 3. Mutating roles get `isolation: 'worktree'` (E7), which the Workflow tool creates and removes; the implementer's `git push` uses the implementer key via `GIT_SSH_COMMAND` set in its agent definition's `env:` (not verified: whether agent-definition frontmatter supports `env:`; fallback: a `factory git-push ticket/<ID>` wrapper the implementer is allowed to run, which supplies the key). Checkers run read+shell in a checkout the clerk made; they have no key, so a push fails at authentication.
+   - Environment sync: when the instance sets `environment_sync`, `run start` runs that command in each build checkout (the implementer's worktree at every dispatch, and each checker's checkout) through the running-code wrapper, after the environment files are copied and before the role starts. A failure refuses the run, with the command and its output in `runs/<id>/environment-sync.log`.
 4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6).
 5. Empty output (doc §Routing rules): no time or token budget is enforced, and `agent()` reports no reason a run stopped, so no empty output is a budget kill. A run that ends without its output file, or with a blank one, is `EMPTY-OUTPUT` in `run finish`, whether `agent()` returned text, blank text or `null` (a user skip or a terminal error). When the returned text is non-blank, the script keeps its last 4000 characters with `run last-message`. The same role is re-dispatched once, on the same inputs and in the same round; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs as outputs and records no result row for it, so `resolve --redispatch` re-runs only that role. A thrown `agent()` stays `KILLED`, parked `agent call failed: <role>: <error>`, with no re-dispatch. Until a run returns, a hung agent blocks `parallel()` and every sibling in that join; the user skipping the agent is the one manual stop (E7; Open question 4).
 6. After each run: `meta.yaml` complete, the checker worktree removed by the clerk (`factory run cleanup RUN`). The run's `runs/<run_id>/scratch/` stays until its ticket's next state change other than `parked`, which removes it (`store.save_ticket`).
diff --git a/docs/changelog.md b/docs/changelog.md
index 4c0c3f6..d90de0a 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -67,5 +67,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 63. After issue #57 (2026-10-05), where the merge gate merged changes to protected paths without reading any declaration of them, while the code reviewer's prompt promised that the gate would require a human approval: the approved spec's Risk section is now the authorization. The spec writer declares every protected path the change will touch on one line of Risk, `Protected paths: none` or `Protected paths:` followed by backticked entries, one path or glob per entry, with no brace lists; the human approves that line at the spec gate. At merge, the gate compares the changed paths, from the merge base with the integration branch and with both sides of a move, against the instance's in-repo protected globs and the pinned spec's line. It refuses each undeclared protected path by name, with an error that starts `BLOCKED from merge gate`, and the build parks the sub-ticket with that error. The human answers the park with `resolve --accept-paths F`, which accepts those paths for that sub-ticket and returns it to its checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its implementer at the same round. A ruling on a reviewer's ESCALATE now returns the sub-ticket to its checks, with the results that did not pass set aside, instead of to the spec critic, a step that never runs for a sub-ticket. Check 6 of the code reviewer prompt says what the gate does, the spec writer's FORMAT gives the declaration line, and the design's gate lines, piece 7, piece 8, piece 9 and the resolution rules drop the per-PR approval for protected paths. Rejected: reading every backticked path in Risk, since Risk sections also name paths they promise not to touch; and a human approval on every change to a protected path, which would have stopped 18 of the last 20 merges in this repository.
 64. After issue #76 (2026-10-09), where five of the seven role prompts, triage, planner, implementer, code reviewer and verifier, lacked the reading rules that #73 gave the spec writer and critic, though the implementer and verifier run test suites and other long commands, and every later turn re-sends what a run has read. Each of the five prompts gains the critic's Turn economy bullet, word for word: put independent reads and commands in one turn, read a line range once grep has found it, and send long output to a file in the run's scratch directory and grep or tail it. The spec writer's sentence on writing the spec in as few writes as possible stays out. The bullet goes directly before the declared-path rule in the implementer's and verifier's RULES, last in the code reviewer's WHAT YOU RUN, and last in the planner's and triage's RULES. #74's replay (entry 59) found that these rules cut the spec writer's tokens by about 37% at the same quality, but it tested the critic's reading rules only together with a cap on checking, and that pair saved nothing and made the critic check less. Nothing else in the five prompts changes, and the hook that would refuse whole-file reads and uncapped searches stays with #65. The runtime moves to these prompts only after the operator's replay of past implementer and verifier runs, with the old and the new prompts, holds quality. Rejected: a shared preamble line, which would also reach the spec writer and critic, which already carry the rules.
 65. After issues #44 and #50 (2026-10-04), where scenarios approved at the spec gate could not pass once another ticket merged first, and nothing could correct the pinned spec: on the Nanobot target, two scenarios of its ticket T-0008 created no policy file after a merged ticket made one mandatory, rulings let the build go on, and archive would still have written the unamended scenarios into current truth; here, T-0012's pinned spec was edited in place by hand, and a test that merged after T-0032's spec was written blocked T-0032.1's implementer. A human now amends a pinned spec with `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged`. It writes F as the next version and makes it the approved one, which every later role run receives. It re-pins the change folder but keeps the planner's `tasks.md`, so archive writes the amended scenarios. `--intent` is required: the harness checks that the Problem, every Decisions line, and each requirement's name, operation and statement are unchanged. It refuses `--intent changed`, or any such difference, with a restart note that names the merged sub-tickets a restart keeps, the unmerged ones it discards, and the commands to re-spec and re-plan or to close and re-file. It also refuses, writing nothing, while any run is in flight on the ticket or its sub-tickets, on a sub-ticket, at the gate, on a closed or archived ticket, and for a version that fails the gate's checks. Each amendment is recorded in `approvals/<ticket id>/amendment-<n>.md`, logged as `spec.amended`, and changes no ticket state. Every stored spec version now records the integration branch's head in `specs/<ticket id>/v<n>.yaml`. Before a sub-ticket's first implementer run, `run start` checks for spec drift: its Acceptance names an unmerged sibling it does not depend on, or a test file changed since its parent's approved version was written, in a commit that also changed a file the design names, and no Tests to change list names it. Drift refuses the run with an error that starts `BLOCKED from harness: spec drift:`, and the build parks the sub-ticket; the human amends, rules, or both, and a ruling on file stops the check. Measured on both stores' history, the test rule would have caught 9 of 10 known breaks and parks about half of all sub-tickets. The critic now receives every other approved change not yet archived, with the requirements it changes and its decisions, and its rubric item 5 makes a scenario BLOCKING when its setup would not hold whichever of the two tickets merges first. Rejected: the build spec's unbuilt `resolve --amend-spec`, because an amendment may be needed while the ticket is not stopped; a critic run on every amendment, which needs a new route; running each scenario at build start, whose expected failure is prose a program cannot compare; and a new park status for drift, which needs a new `resolve` route.
+66. After issue #51 (2026-10-04), where every build role lost its first attempt to a broken Python environment: a role's shell inherited the virtual environment activated in the session that launched the factory, which on this machine belongs to another repository's checkout, and each fresh build checkout had no `.venv`, so a `uv run --no-sync` check failed on its first import until the implementer, then the reviewer, then the verifier each installed the environment themselves. The running-code wrapper, around every role command and every gate command, now first removes the exact `$VIRTUAL_ENV/bin` entry from `PATH` and unsets `VIRTUAL_ENV` and `PYTHONHOME`, then sets the fresh HOME and the `run_env` exports as before. An instance may name one shell command, `environment_sync`, in `instance.yaml`. `run start` runs it through that wrapper in the run's checkout, the implementer's worktree at every dispatch and each checker's checkout, including the parent-close verifier's, after the environment files are copied and before the role starts. On success the run's `meta.yaml` records the command and the role's input ends its "Where you work" section with a line saying the environment is already synced and should not be synced again unless the change alters the files it is built from. A failed sync refuses the run start with exit 2 and one line naming the exit code and the run's `environment-sync.log`, which holds the command and its full output; no run is recorded or put in flight, and a checker's checkout is removed while the implementer's worktree is kept. Without the key nothing runs and the input is as before. Rejected: unsetting only the two variables, which leaves the environment's `python` first on `PATH`; an opt-in way to unset variables through `run_env`, which would leave the deactivation off by default; syncing only when the implementer's worktree is first created, because the environment files and a conflict run's merge can change the lock file at a later dispatch; and quoting the command or its output in the refusal, because the build workflow expands backticks and `$` in a park reason.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 19d37e6..4c1fdb0 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -65,7 +65,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
 
diff --git a/factory/cli.py b/factory/cli.py
index 02741dc..4e90169 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -215,6 +215,7 @@ def run_start(a, root, cfg):
         _check_sibling_tests(root, cfg, t)
     if a.role in BUILD_ROLES:
         compose.gate_entries(cfg)  # a malformed gate entry refuses here, before a run id is reserved
+        compose.environment_sync(cfg)  # so does a malformed environment_sync
     baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
     rid = store.next_run_id(root, a.role)
     model = a.model or cfg["models"][a.role]
@@ -361,7 +362,9 @@ def _tests_to_change_section(design_text: str) -> str:
 def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent_close: bool) -> None:
     """Worktrees for the build roles (build spec I.3, local stand-in): the implementer gets the
     ticket's branch (created from the integration branch at first dispatch); each checker gets a
-    detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch."""
+    detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch. Each
+    checkout then runs the instance's `environment_sync`, if set (`_sync_environment`)."""
+    sync = compose.environment_sync(cfg)
     repo = gitops.repo_root(cfg)
     integ = gitops.integration_branch(cfg, repo)
     store.ensure_gitignore(root)
@@ -376,6 +379,7 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
         meta.update({"branch": branch, "base": gitops.rev(repo, integ), "head": gitops.rev(repo, branch),
                      "worktree": str(wt), "resolution": "conflict" if t.get("merge_refused") else None,
                      "environment_files": gitops.copy_environment_files(cfg, repo, wt)})
+        _sync_environment(cfg, sync, meta, repo, wt, d, checker=False)
     else:
         head = gitops.rev(repo, integ) if parent_close else t.get("head")
         base = (t.get("parent_base") or head) if parent_close else gitops.rev(repo, integ)
@@ -386,11 +390,29 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
         wt = d / "wt"
         gitops.add_detached_worktree(repo, wt, head)
         meta["environment_files"] = gitops.copy_environment_files(cfg, repo, wt)
+        _sync_environment(cfg, sync, meta, repo, wt, d, checker=True)
         if not parent_close:
             store.write_text(d / "diff.patch", gitops.diff(repo, base, head))
         meta.update({"branch": t.get("branch"), "base": base, "head": head, "worktree": str(wt)})
 
 
+def _sync_environment(cfg: dict, sync: str | None, meta: dict, repo: Path, wt: Path, d: Path, checker: bool) -> None:
+    """Run the instance's `environment_sync` in the checkout `wt` through the running-code wrapper and
+    record it in `meta`. A failure writes runs/<id>/environment-sync.log, removes a checker's checkout,
+    and refuses the run start with one line that carries neither the command nor its output."""
+    if sync is None:
+        return
+    cp = subprocess.run(["sh", "-c", compose.wrap(sync, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)
+    if cp.returncode == 0:
+        meta["environment_sync"] = sync
+        return
+    log = d / "environment-sync.log"
+    store.write_text(log, f"command: {sync}\nexit: {cp.returncode}\n--- stdout\n{cp.stdout}--- stderr\n{cp.stderr}")
+    if checker:
+        gitops.remove_worktree(repo, wt)
+    raise Refused(f"environment_sync failed (exit {cp.returncode}) in {wt}; its command and output are in {log}")
+
+
 def run_last_message(a, root, cfg):
     """Keep the agent's last message with a run that ended EMPTY-OUTPUT, so a human can see why."""
     d = _run_dir(root, a.run)
diff --git a/factory/compose.py b/factory/compose.py
index 177d41b..84e9d38 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -161,11 +161,29 @@ def run_env(cfg: dict) -> dict:
     return env
 
 
+def environment_sync(cfg: dict) -> str | None:
+    """The instance's `environment_sync`: one shell command `run start` runs in each build checkout,
+    through the running-code wrapper. Absent or null is None; anything but a non-empty string is refused."""
+    cmd = cfg.get("environment_sync")
+    if cmd is None:
+        return None
+    if not isinstance(cmd, str) or not cmd.strip():
+        raise store.Refused(f"environment_sync must be one shell command as a non-empty string, or null, not {cmd!r}")
+    return cmd
+
+
+# Deactivates a virtual environment inherited from the launching shell: its bin/ off PATH, then
+# VIRTUAL_ENV and PYTHONHOME unset. Shown inside backticks in role input, so it holds no backtick.
+_DROP_VENV = ('[ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" '
+              '| paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; ')
+
+
 def wrap(command: str, env: dict) -> str:
-    """`command` in a subshell with HOME set to a fresh temporary directory, then each `run_env`
-    variable exported in file order. A subshell, so the export covers every part of `a && b`."""
+    """`command` in a subshell that first drops an inherited virtual environment (`_DROP_VENV`), then
+    sets HOME to a fresh temporary directory, then exports each `run_env` variable in file order. A
+    subshell, so the export covers every part of `a && b`."""
     exports = "".join(f" {k}={shlex.quote(str(v))}" for k, v in env.items())
-    return f'(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})'
+    return f'({_DROP_VENV}export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})'
 
 
 def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]:
@@ -351,6 +369,10 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
                          else "none (every gate command is skipped below)") + "\n")
         where += "".join(f"SKIPPED by the harness for this diff, do not run: `{s['command']}`: {s['reason']}\n"
                          for s in skipped)
+        if meta.get("environment_sync"):
+            where += (f"Environment: the harness ran this instance's environment sync, `{meta['environment_sync']}`, "
+                      "in this checkout through the running-code wrapper before you started, so the environment is "
+                      "already synced. Do not sync it again unless your change alters the files it is built from.\n")
         parts.append(where)
         if role == "implementer":
             if t.get("merge_refused"):
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index e55c29e..ed65b60 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -38,6 +38,10 @@ environment_files: []
 # Variables the running-code wrapper exports after the throwaway HOME, for tools that keep a cache
 # under HOME (for example UV_CACHE_DIR: /Users/me/.cache/uv). HOME itself is refused.
 run_env: {}
+# One shell command the harness runs in each build checkout at run start, through the running-code
+# wrapper, after the environment files are copied (for example `uv sync --frozen`). null means none.
+# A failure refuses the run.
+environment_sync: null
 force_push_allowed: false
 models:
   triage: opus
diff --git a/tests/factory/test_environment_sync.py b/tests/factory/test_environment_sync.py
new file mode 100644
index 0000000..ca2ec2f
--- /dev/null
+++ b/tests/factory/test_environment_sync.py
@@ -0,0 +1,254 @@
+"""The running-code wrapper drops an inherited virtual environment, and the instance's
+`environment_sync` runs in each build checkout at run start (T-0031).
+
+Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE), a scratch target
+repo (FACTORY_REPO) and a copy of the suite's fixture instance (FACTORY_INSTANCE) with the keys
+under test appended. A fake virtual environment, a directory holding `bin/python`, stands in for
+the one a launching session activated.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+GIT_ID = {"GIT_AUTHOR_NAME": "f", "GIT_AUTHOR_EMAIL": "f@x", "GIT_COMMITTER_NAME": "f", "GIT_COMMITTER_EMAIL": "f@x"}
+DUMP = "env > synced.env"  # a sync that records the environment it ran in
+FAIL = "echo sync-$((1+1)) >&2; echo out-line; exit $((2+1))"  # output and exit code are computed
+
+
+class Target:
+    """T-0001 approved and split into T-0001.1, ready for its implementer, on an instance whose
+    `run_env` exports T31_CACHE and whose `environment_sync` is `sync` (None: the key is absent)."""
+
+    def __init__(self, tmp_path: Path, sync: str | None):
+        self.tmp = tmp_path
+        self.root = tmp_path / "state"
+        self.repo = tmp_path / "target"
+        self.venv = tmp_path / "venv"
+        (self.venv / "bin").mkdir(parents=True)
+        (self.venv / "bin" / "python").write_text("#!/bin/sh\necho fake\n")
+        (self.venv / "bin" / "python").chmod(0o755)
+        inst = tmp_path / "inst"
+        shutil.copytree(FIXTURE_INSTANCE, inst)
+        with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
+            f.write("run_env: {T31_CACHE: /tmp/t31-cache}\n")
+            if sync is not None:
+                f.write(f"environment_sync: {json.dumps(sync)}\n")
+        self.repo.mkdir()
+        self.env = {**os.environ, **GIT_ID, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(inst),
+                    "FACTORY_REPO": str(self.repo), "FACTORY_INTEGRATION_BRANCH": "main",
+                    "PYTHONDONTWRITEBYTECODE": "1"}
+        self.git("init", "-q", "-b", "main")
+        self.git("commit", "-q", "--allow-empty", "-m", "init")
+        req, spec, plan = tmp_path / "req.md", tmp_path / "spec.md", tmp_path / "plan.md"
+        req.write_text("# F\n\nDo x.\n")
+        spec.write_text("## Problem\nx\n")
+        plan.write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("ticket", "new", "--file", str(req))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", "T-0001", "--file", str(spec))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", "T-0001")
+        self.ok("subticket", "add", "T-0001", "--file", str(plan))
+
+    def git(self, *argv: str, cwd: Path | None = None) -> str:
+        cp = subprocess.run(["git", "-C", str(cwd or self.repo), *argv], capture_output=True, text=True,
+                            env=self.env, check=True)
+        return cp.stdout.strip()
+
+    def cli(self, *argv: str, venv: bool = False) -> subprocess.CompletedProcess:
+        """`bin/factory`, launched from a shell with the fake virtual environment activated when `venv`
+        (VIRTUAL_ENV and its bin/ first on PATH; not PYTHONHOME, which would break the harness's own
+        interpreter: the wrapper test covers PYTHONHOME)."""
+        env = self.env
+        if venv:
+            env = {**env, "VIRTUAL_ENV": str(self.venv), "PATH": f"{self.venv}/bin:{env['PATH']}"}
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+    def ok(self, *argv: str, venv: bool = False) -> dict:
+        cp = self.cli(*argv, venv=venv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def start(self, role: str, tid: str) -> str:
+        return self.ok("run", "start", "--role", role, "--ticket", tid, venv=True)["run_id"]
+
+    def input_of(self, run_id: str) -> str:
+        self.ok("run", "compose", run_id)
+        return (self.root / "runs" / run_id / "input.md").read_text(encoding="utf-8")
+
+    def meta(self, run_id: str) -> dict:
+        return yaml.safe_load((self.root / "runs" / run_id / "meta.yaml").read_text(encoding="utf-8"))
+
+    def ticket(self, tid: str) -> dict:
+        return self.ok("ticket", "show", tid, "--json")
+
+    def worktree(self) -> Path:
+        return self.root / "worktrees" / "T-0001.1"
+
+    def ready_for_checks(self) -> str:
+        """A commit on T-0001.1's branch (in the implementer's worktree when one exists), and the
+        ticket set to checks."""
+        if self.worktree().is_dir():
+            self.git("commit", "-q", "--allow-empty", "-m", "work", cwd=self.worktree())
+            head = self.git("rev-parse", "HEAD", cwd=self.worktree())
+        else:
+            self.git("branch", "factory/T-0001.1", "main")
+            self.git("checkout", "-q", "factory/T-0001.1")
+            self.git("commit", "-q", "--allow-empty", "-m", "work")
+            head = self.git("rev-parse", "HEAD")
+            self.git("checkout", "-q", "main")
+        self.ok("ticket", "set", "T-0001.1", "status=checks-in-flight", "branch=factory/T-0001.1", f"head={head}")
+        return head
+
+    def checker_checkouts(self) -> list[str]:
+        return [ln for ln in self.git("worktree", "list").splitlines() if "/runs/" in ln]
+
+
+def synced_env(path: Path) -> dict:
+    """The `env > synced.env` dump as name -> value (single-line values only, which is all we read)."""
+    out = {}
+    for line in path.read_text().splitlines():
+        name, sep, value = line.partition("=")
+        if sep:
+            out[name] = value
+    return out
+
+
+def assert_synced_clean(t: Target, dump: Path) -> None:
+    env = synced_env(dump)
+    assert "VIRTUAL_ENV" not in env and "PYTHONHOME" not in env, env
+    assert f"{t.venv}/bin" not in env["PATH"].split(":")
+    assert env["T31_CACHE"] == "/tmp/t31-cache", "the run_env exports reach the sync"
+    assert env["HOME"] != os.environ["HOME"] and Path(env["HOME"]).is_dir(), "the sync gets a fresh HOME"
+
+
+def sync_line(text: str) -> list[str]:
+    where = text.split("\n## Where you work\n", 1)[1].split("\n## ", 1)[0]
+    return [ln for ln in where.splitlines() if ln.startswith("Environment: ")]
+
+
+def wrapper_in(text: str) -> str:
+    section = text.split("\n## Running code\n", 1)[1].split("\n## ", 1)[0]
+    found = [s for s in section.split("`")[1::2] if "<command>" in s]
+    assert len(found) == 1, section
+    return found[0]
+
+
+PROBE = 'printf "%s|%s|%s\\n" "${VIRTUAL_ENV-unset}" "${PYTHONHOME-unset}" "$PATH"'
+
+
+def test_the_composed_wrapper_drops_an_inherited_virtual_environment_and_keeps_the_rest_of_path(tmp_path):
+    t = Target(tmp_path, None)
+    text = t.input_of(t.start("implementer", "T-0001.1"))
+    wrapped = wrapper_in(text).replace("<command>", PROBE)
+    venv_bin = f"{t.venv}/bin"
+    rest = f"/x/one:{venv_bin}x:/x/two:/usr/bin:/bin"  # `<venv>/binx` is not the exact entry, so it stays
+    cp = subprocess.run(["sh", "-c", wrapped], capture_output=True, text=True, check=True,
+                        env={"VIRTUAL_ENV": str(t.venv), "PYTHONHOME": str(t.venv), "PATH": f"{venv_bin}:{rest}",
+                             "HOME": os.environ["HOME"]})
+    assert cp.stdout == f"unset|unset|{rest}\n"
+    plain = "/x/one:/x/two:/usr/bin:/bin"
+    cp = subprocess.run(["sh", "-c", wrapped], capture_output=True, text=True, check=True,
+                        env={"PATH": plain, "HOME": os.environ["HOME"]})
+    assert cp.stdout == f"unset|unset|{plain}\n", "a PATH with no environment is unchanged"
+
+
+def test_an_implementer_worktree_is_synced_at_every_dispatch_and_its_input_says_so(tmp_path):
+    t = Target(tmp_path, DUMP)
+    run_id = t.start("implementer", "T-0001.1")
+    dump = t.worktree() / "synced.env"
+    assert_synced_clean(t, dump)
+    assert t.meta(run_id)["environment_sync"] == DUMP
+    lines = sync_line(t.input_of(run_id))
+    assert lines == [f"Environment: the harness ran this instance's environment sync, `{DUMP}`, in this checkout "
+                     "through the running-code wrapper before you started, so the environment is already synced. "
+                     "Do not sync it again unless your change alters the files it is built from."]
+    t.ok("run", "finish", run_id, "--status-override", "KILLED")
+    dump.unlink()
+    again = t.start("implementer", "T-0001.1")
+    assert dump.is_file(), "a later dispatch to the same worktree syncs again"
+    assert t.meta(again)["environment_sync"] == DUMP
+
+
+def test_a_reviewer_checkout_is_synced_before_the_reviewer_starts_and_its_input_says_so(tmp_path):
+    t = Target(tmp_path, DUMP)
+    t.ready_for_checks()
+    run_id = t.start("reviewer", "T-0001.1")
+    assert_synced_clean(t, t.root / "runs" / run_id / "wt" / "synced.env")
+    assert t.meta(run_id)["environment_sync"] == DUMP
+    assert len(sync_line(t.input_of(run_id))) == 1
+
+
+def test_the_parent_close_verifier_checkout_is_synced(tmp_path):
+    t = Target(tmp_path, DUMP)
+    t.ok("ticket", "set", "T-0001", "status=ready-for-parent-verify")
+    run_id = t.start("verifier", "T-0001")
+    assert_synced_clean(t, t.root / "runs" / run_id / "wt" / "synced.env")
+    assert t.meta(run_id)["environment_sync"] == DUMP
+    assert len(sync_line(t.input_of(run_id))) == 1
+
+
+def assert_refused_and_logged(t: Target, cp: subprocess.CompletedProcess) -> Path:
+    assert cp.returncode == 2
+    lines = cp.stderr.strip().splitlines()
+    assert len(lines) == 1, cp.stderr
+    line = lines[0]
+    assert line.startswith("environment_sync failed (exit 3) in "), line
+    assert not set(line) & set('`$"'), "the refusal carries no shell-expanding character"
+    assert "sync-" not in line and "out-line" not in line and "echo" not in line, "nor the command or its output"
+    log = Path(line.rsplit(" are in ", 1)[1])
+    assert log.name == "environment-sync.log" and log.parent.parent == t.root / "runs"
+    body = log.read_text()
+    assert FAIL in body and "sync-2" in body and "out-line" in body and "exit: 3" in body
+    assert sorted(p.name for p in log.parent.iterdir()) == ["environment-sync.log"], "no meta.yaml, no checkout"
+    return log
+
+
+def test_a_failed_sync_refuses_the_implementer_start_and_keeps_its_worktree(tmp_path):
+    t = Target(tmp_path, FAIL)
+    cp = t.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.1", venv=True)
+    assert_refused_and_logged(t, cp)
+    assert t.ticket("T-0001.1")["in_flight"] == []
+    assert t.worktree().is_dir(), "the implementer's worktree is kept for the next dispatch"
+
+
+def test_a_failed_sync_refuses_the_reviewer_start_and_removes_its_checkout(tmp_path):
+    t = Target(tmp_path, FAIL)
+    t.ready_for_checks()
+    cp = t.cli("run", "start", "--role", "reviewer", "--ticket", "T-0001.1", venv=True)
+    log = assert_refused_and_logged(t, cp)
+    assert not (log.parent / "wt").exists() and t.checker_checkouts() == []
+    assert t.ticket("T-0001.1")["in_flight"] == []
+
+
+@pytest.mark.parametrize("value", ["[uv, sync]", '""', "3"])
+def test_a_malformed_environment_sync_is_refused_before_any_checkout_or_run(tmp_path, value):
+    t = Target(tmp_path, None)
+    inst = Path(t.env["FACTORY_INSTANCE"]) / "instance.yaml"
+    inst.write_text(inst.read_text() + f"environment_sync: {value}\n")
+    cp = t.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.1", venv=True)
+    assert cp.returncode == 2 and "environment_sync" in cp.stderr, cp.stderr
+    assert not t.worktree().exists()
+    assert not (t.root / "runs").exists() or list((t.root / "runs").iterdir()) == []
+
+
+def test_without_the_key_nothing_runs_and_no_input_carries_the_line(tmp_path):
+    t = Target(tmp_path, None)
+    run_id = t.start("implementer", "T-0001.1")
+    assert "environment_sync" not in t.meta(run_id) and sync_line(t.input_of(run_id)) == []
+    assert t.git("status", "--porcelain", "--untracked-files=all", cwd=t.worktree()) == ""
+    t.ok("run", "finish", run_id, "--status-override", "KILLED")
+    t.ready_for_checks()
+    rev = t.start("reviewer", "T-0001.1")
+    assert "environment_sync" not in t.meta(rev) and sync_line(t.input_of(rev)) == []
diff --git a/tests/factory/test_gate_paths.py b/tests/factory/test_gate_paths.py
index c4586b1..3323b29 100644
--- a/tests/factory/test_gate_paths.py
+++ b/tests/factory/test_gate_paths.py
@@ -214,7 +214,8 @@ def test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does(tmp_p
     t = Target(tmp_path, SCOPED_GATE)
     t.set_gate(gate)
     _, text, meta = t.checker()
-    want = f"`(export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else ""
+    want = (f"`([ -z \"${{VIRTUAL_ENV:-}}\" ] || PATH=$(printf %s \"$PATH\" | tr : '\\n' | grep -vxF \"$VIRTUAL_ENV/bin\" | paste -sd: -); "
+            f"unset VIRTUAL_ENV PYTHONHOME; export HOME=\"$(cd \"$(mktemp -d)\" && pwd -P)\"; {UNSCOPED})`" if UNSCOPED in gate else "")
     assert _gate_line(text).endswith("each is already wrapped): " + want)
     assert _skipped_lines(text) == [] and meta["gate_skipped"] == []
 
diff --git a/tests/factory/test_run_isolation.py b/tests/factory/test_run_isolation.py
index 164a927..c3b41f1 100644
--- a/tests/factory/test_run_isolation.py
+++ b/tests/factory/test_run_isolation.py
@@ -19,7 +19,8 @@ import pytest
 REPO = Path(__file__).resolve().parents[2]
 BIN = REPO / "bin" / "factory"
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
-WRAP = '(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})'
+WRAP = ('([ -z "${{VIRTUAL_ENV:-}}" ] || PATH=$(printf %s "$PATH" | tr : \'\\n\' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); '
+        'unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"{vars}; {cmd})')
 SECTION = ("\n## Running code\nRun every test, script or prototype through this wrapper, which gives it a "
            "fresh temporary HOME so it cannot write the operator's real home directory: `{wrapper}`. Put your "
            "command in place of <command>. This includes every test or check command the briefing above gives. "
