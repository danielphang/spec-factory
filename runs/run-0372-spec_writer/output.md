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

## Evidence
- The Nanobot fork, the other repository that runs this factory (instance A), run-0259-implementer (2026-10-04), `~/dev/nanobot-upstream/.factory/store/runs/run-0259-implementer/output.md`. Line 59, under Out-of-scope observations: "The worktree had no `.venv`, and the shell inherits `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` from blue. As written, an acceptance command with `uv run --no-sync` in a fresh worktree makes an empty env and fails on imports". Line 15 says the first attempt "ran with no project environment" and that the reported results are from the rerun. The implementer spent one full pass of acceptance commands before getting a real result.
- This repository, on 2026-10-09: `grep -l VIRTUAL_ENV .factory/store/runs/*/output.md` matches 31 run outputs. 26 are build-role runs (10 implementer, 5 reviewer, 11 verifier). The other 5 are this ticket's own triage, spec writer and critic runs. `.factory/store/runs/run-0060-verifier/output.md` line 3 says: "Shell inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`; uv printed its "does not match the project environment path `.venv` and will be ignored" warning". `run-0216-verifier/output.md` line 20 says the suite run "printed a `uv` warning that the inherited `VIRTUAL_ENV` was ignored". This ticket's own implementer, run-0366 (line 90), had the same environment first on `PATH`.
- The inherited environment is more than the variable. In this session, `echo $VIRTUAL_ENV` prints `/Users/dphang/dev/nanobot/.venv-test`, and the first `PATH` entry is `/Users/dphang/dev/nanobot/.venv-test/bin`. So a bare `python` or `pytest` in a role's shell runs the other repository's environment. Unsetting `VIRTUAL_ENV` alone would not change that.
- Reproduced in this round on a fresh clone at `b002c95`, under the HOME wrapper, with no `.venv`. `uv run --no-sync python -c 'import yaml'` printed `` warning: `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project environment path `.venv` and will be ignored ``, then `Creating virtual environment at: .venv`, then `ModuleNotFoundError: No module named 'yaml'`, exit 1. The harness clears this run's scratch directory when the ticket moves on, so the lines that matter are quoted here.
- Today's behaviour of every acceptance command below, run in this round on a clone at `b002c95` under bash and under zsh (each under a fresh HOME and `TMPDIR`):
  - The wrapper scenario printed `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` for both the role wrapper and the wrapped gate command. Today's wrapper passes an inherited `VIRTUAL_ENV` and `PYTHONHOME` straight through, and the fake environment's `python` still wins on `PATH`.
  - The sync scenarios printed `synced=no`: today the harness ignores an `environment_sync` key.
  - The failed-sync scenario printed `exit=0` for both run starts, `in_flight=0 checker_checkouts=1 meta=2`: today a run starts whatever the key says.
- The existing tests that pin the wrapper text. `grep -rln -e 'pwd -P' -e 'mktemp -d)' -e 'export HOME' tests/factory/` on `b002c95` lists two files: `tests/factory/test_run_isolation.py` (its `WRAP` constant, line 22) and `tests/factory/test_gate_paths.py` (line 217, the `want` string in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`, which T-0028 added on 2026-10-05). The run-0366 implementer hit the second one: "`1 failed, 423 passed`", the failure being that test (its output, line 59).
- Feasibility, re-run in this round. I applied a prototype of parts A to D to a scratch clone of `b002c95` (harness diff: `factory/cli.py` +15, `factory/compose.py` +25/-3, `factory/instance.template.yaml` +4). The harness suite on the unchanged clone: `408 passed`. With the prototype: `7 failed, 401 passed`. The seven are the six cases that compare against `WRAP` in `test_run_isolation.py` and the one case of the `test_gate_paths.py` test above whose gate is an unscoped mapping. With only the two edits listed under Tests to change: `408 passed`. So no other test pins the wrapper text, and none pins run start's setup in a way the change breaks (the suite's fixture instances set no `environment_sync`, so part C runs nothing for them). The prototype printed every THEN below exactly, under bash and zsh, apart from the three document scenarios, which it did not cover.
- The build workflow passes a park reason to the shell inside double quotes (`factory/workflows/build.js:62`: `--reason "${reason.replace(/"/g, "'")}"`). It replaces double quotes only, so a backtick or `$` in the reason is expanded by the shell. A refused run start's reason is `harness-bug: run start <role>: <stderr>` (line 84). In this round, `sh -c 'echo "--reason \"harness-bug: run start implementer: error: No `echo EXPANDED` found\""'` printed `--reason "harness-bug: run start implementer: error: No EXPANDED found"`. uv's own errors carry backticks: `uv sync --frozen` in an empty directory printed ``error: No `pyproject.toml` found in current directory or any parent directory``. Version 2 put the sync's last 20 output lines and its command into the refusal, so a failed `uv sync` would have had part of its message run as a command, or lost, on its way into the park reason. T-0033's decision of 2026-10-09 keeps the merge gate's refusal free of these characters for the same reason.
- Since 2026-10-04, T-0032 removed the gate-commands line from the reviewer's input; it now says "The verifier runs the gate commands on this head; you do not run them" (`factory/compose.py:318-319`). T-0028 added "SKIPPED" lines after the gate line (lines 324-325). Version 2 placed the new input line "after the gate-commands line", which the reviewer no longer has. The reviewer prompt still lets it "run a narrow command to confirm a specific finding, such as one test" (`factory/prompts/reviewer.md:9`), so its checkout still needs a working environment.
- The Nanobot harness has no fix to copy. Triage's `grep -rn -E "VIRTUAL_ENV|environment_sync|PYTHONHOME"` over `~/dev/nanobot-upstream/.factory` found only notes in plans and specs.

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

## Responses
Responses to the operator's change request of 2026-10-09 (`approvals/T-0031/changes-1.md`):
- 1, list the `test_gate_paths.py` test and check the whole suite → FIXED. Tests to change now lists `tests/factory/test_gate_paths.py` line 217, with the reason and the exact new lines, and says nothing else in the file changes. To find any other test that pins the wrapper text or run start's setup, I ran the whole suite on a prototype of parts A to D: `7 failed, 401 passed`. All seven were the six `WRAP` cases and this one case. With the two listed edits: `408 passed`, the same as the unchanged base. A grep for the wrapper's text over `tests/factory/` finds only these two files.
- 2, refresh Evidence and line references → FIXED. Every `compose.py`, `cli.py` and `build.js` line number is re-read on `b002c95`. Store paths now use `.factory/store` (T-0025), on both instances. The `VIRTUAL_ENV` count is re-derived (31 on 2026-10-09). The no-sync repro and every scenario's "today" output were re-run in this round, under bash and zsh. The changelog's last entry is now 63.
- 3, declare protected paths on the Risk line → FIXED. Risk opens with the declaration line, naming the three harness files the change touches: `factory/compose.py`, `factory/cli.py` and `factory/instance.template.yaml`. No other protected path is touched.
- 4, keep the design and Decisions unless the refresh shows a conflict → two conflicts found, so two changes; everything else is kept:
  - The failed-sync refusal no longer carries the command or its output. They go to `runs/<id>/environment-sync.log`, and the refusal names that file. Since 2026-10-04, T-0033 recorded that the build workflow passes a park reason to the shell in double quotes, which expand backticks and `$`. uv's errors contain backticks (Evidence). The failed-sync requirement and scenario change to match. The scenario now also checks that the refusal carries no such character and that the log holds the output. Its "today" output was re-run.
  - The "already synced" line goes at the end of the "Where you work" block, not after the gate-commands line. Since T-0032 the reviewer's input has no gate-commands line, and since T-0028 SKIPPED lines follow it. The scenarios find the line anywhere in the input, so they are unchanged.
  - Also changed: the Decision on where the sync runs adds why the reviewer is still synced (its prompt lets it run one test). Risk adds the empty-`PATH`-entry edge case that run-0366 found, and notes that readers of `runs/` skip a directory with no `meta.yaml`.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. The prototype printed every non-document THEN under bash and zsh, and the full suite ran 408 passed with exactly the two listed test edits.
ESCALATIONS: none
