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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0284-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0284-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v2)

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

## Evidence
- The Nanobot fork, the other repository that runs this factory (instance A), run-0259-implementer (2026-10-04), `~/dev/nanobot-upstream/.factory/state/runs/run-0259-implementer/output.md`, reports this under Out-of-scope observations: "The worktree had no `.venv`, and the shell inherits `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` from blue. As written, an acceptance command with `uv run --no-sync` in a fresh worktree makes an empty env and fails on imports (`No module named 'loguru'`, `No module named pytest`)." Its results section says the first attempt "ran with no project environment" and that the reported results are from the rerun. The implementer spent one full pass of acceptance commands before getting a real result.
- This repository: on 2026-10-04, `grep -l VIRTUAL_ENV .factory/state/runs/*/output.md` matches 27 run outputs. 24 of them are implementer, reviewer and verifier runs. The other three are this ticket's own triage, spec writer and critic runs (run-0274, run-0276, run-0279), so the count grows as this ticket's runs land. run-0060-verifier line 3 says: "Shell inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`; uv printed its "does not match the project environment path `.venv`…" warning". run-0216-verifier line 20 reports the same warning. Every build role on this instance sees the inherited value.
- The inherited environment is more than the variable. In this session, `echo $VIRTUAL_ENV` prints `/Users/dphang/dev/nanobot/.venv-test`, and the first `PATH` entry is `/Users/dphang/dev/nanobot/.venv-test/bin`. `which -a python pytest` lists `/Users/dphang/dev/nanobot/.venv-test/bin/python` and `/Users/dphang/dev/nanobot/.venv-test/bin/pytest` first. So a bare `python` or `pytest` in a role's shell runs the other repository's environment. Unsetting `VIRTUAL_ENV` alone would not change that.
- Reproduced again in this round on a fresh clone of this repository at `c2750bf`, under the HOME wrapper. `.venv` did not exist. `uv run --no-sync python -c 'import yaml'` printed uv's warning `` `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project environment path `.venv` and will be ignored ``, then `Creating virtual environment at: .venv`, then failed with `ModuleNotFoundError: No module named 'yaml'` and exit 1. So uv made an empty environment and the first import failed. Output: `.factory/state/runs/run-0283-spec_writer/scratch/repro-nosync.txt`. The harness clears that directory when the ticket moves on, so the lines that matter are quoted here. In round 1, `uv sync --frozen` in such a clone made the same command print `yaml ok`. The critic confirmed that in its round-1 review (sync exit 0 in 1 s, then `yaml ok`).
- In round 1, each acceptance command below was run on this checkout (`c2750bf`) under bash and under zsh. The critic's round-1 review re-ran three of them on the same commit and got the same output. `main` is still at `c2750bf` for this revision, and no acceptance command changed:
  - The wrapper scenario printed `ve=<scratch>/venv ph=<scratch>/venv fake_python=1 …` for both the role wrapper and the wrapped gate command. Today's wrapper passes an inherited `VIRTUAL_ENV` and `PYTHONHOME` straight through, and the fake environment's `python` still wins on `PATH`.
  - The sync scenarios printed `synced=no`: today the harness ignores an `environment_sync` key.
  - The failed-sync scenario printed `exit=0` for both run starts and `checker_checkouts=1`: today a run starts whatever the key says.
- Feasibility: in round 1, I applied a prototype of parts A to D to a scratch clone. It printed every THEN below exactly, under both shells. With that prototype, the harness suite gave `6 failed, 294 passed`. All six failures came from the expected wrapper text in `tests/factory/test_run_isolation.py`. With only that file's `WRAP` constant updated, the result was `300 passed`. This shows that no other existing test depends on the wrapper text or on run start's setup.
- The Nanobot harness has no fix to copy. `grep -rn -E "VIRTUAL_ENV|environment_sync|PYTHONHOME"` over `~/dev/nanobot-upstream/.factory` finds only notes in plans and specs (triage, confirmed by round 1's own read of run-0259).

## Root cause
- `factory/compose.py:74-78`, `wrap()`: it builds `(export HOME=<fresh>[ run_env exports]; <command>)`. It never removes an inherited virtual environment. A role's shell inherits the launching session's environment, so `VIRTUAL_ENV`, `PYTHONHOME` and the environment's `bin/` on `PATH` all reach every command and every gate command.
- `factory/compose.py:57-71`, `run_env()`: it accepts only name-to-value pairs, so an instance cannot use it to unset a variable.
- `factory/cli.py:238-263`, `_start_build_run()`: it creates the implementer's worktree (line 249, only when missing) or the checker's detached checkout (line 261) and copies `environment_files`. It runs no command, so a new copy has no `.venv`.
- `factory/instance.template.yaml` and `.factory/instance.yaml` have no key that names a sync command.

## Out of scope
- The wrapper's other behaviour: the fresh HOME, the `run_env` exports and their order, and the prose of the "Running code" section. Only the wrapper's prefix changes.
- Every gate command, acceptance criterion and check, on both instances.
- Other ways a Python environment can leak in (`PYTHONPATH`, conda's `CONDA_PREFIX`). Nothing reported them.
- A time limit on the sync.
- Setting `environment_sync` on either instance. That is an operator step.
- The `harness-bug:` prefix that the build workflow already puts on a refused run start's park reason.

## Open questions
none

## Decisions
- The wrapper fully deactivates an inherited virtual environment. It removes the exact entry `$VIRTUAL_ENV/bin` from `PATH`, then unsets `VIRTUAL_ENV` and `PYTHONHOME`, all before it sets HOME. Rejected: unsetting only the two variables, as the requester proposed. The activating shell also put the environment's `bin/` first on `PATH`, so a bare `python` or `pytest` would still run the other repository's environment (Evidence).
- The deactivation is built into the wrapper for every instance, not configured per instance. Rejected: a way to unset variables through `run_env`. Every instance needs the deactivation, and opting in would leave it off by default. `run_env` is the list of variables an instance gives the wrapper to export after the throwaway HOME. Its exports still come after the deactivation, so an instance that wants a particular environment can still name it there.
- `environment_sync` is one optional shell command, given as a string in `instance.yaml`. If it is absent or null, nothing runs, as today. Any other non-string or empty value is refused at run start, before any checkout is made.
- The sync runs at every build-role run start, for the implementer, reviewer and verifier, including the verifier that checks the parent ticket after all its sub-tickets merge. It runs in that run's checkout, after the environment files are copied, through the same wrapper as role commands, so it gets the throwaway HOME, the `run_env` exports and no inherited environment. Rejected: syncing only when the implementer's worktree is first created. The environment files are copied again at every run start. A conflict run, which is an implementer run after the merge step refused the branch, merges in the integration branch, the branch that finished tickets merge into. Either can change the lock file the environment was built from.
- A failed sync refuses the run start with exit 2. The refusal names `environment_sync`, the checkout, the command and its exit code, and gives the last 20 lines of its output. No run is recorded or put in flight, and a checker checkout made for the run is removed. The implementer's worktree is kept for the next dispatch. The build workflow, the script that dispatches the build roles in turn, then parks the ticket: it stops the ticket and leaves it for a human. It uses its existing park reason `harness-bug: run start <role>: …`, so a broken environment never reaches a checker as a code failure. Rejected: starting the role anyway with a note. The role would then rediscover the broken environment, which is the cost this change removes.
- When the sync ran, the run's record file, `meta.yaml`, stores the command under `environment_sync`. The "Where you work" section of the role's input gains one line: the command ran, the environment is already synced, and the role should not sync again unless its change alters the files the environment is built from.
- This change sets `environment_sync` on neither instance. The operator sets it after the runtime, the separate checkout the factory runs from, has moved to the new harness revision (Operator steps). Rejected: setting it on this instance in the PR. That writes the protected `.factory/**`, and the key has no effect until the runtime runs the new harness anyway.

## Risk
- Protected paths this change touches: harness (`factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`). It touches none of infra (`.factory/**`), generated (`docs/prompts/**`), `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, the reference harness or credentials. It does not change `factory/prompts/**`.
- Guardrail path: one existing test file, `tests/factory/test_run_isolation.py`. Only its `WRAP` constant changes, as declared under Tests to change.
- Blast radius: after the runtime upgrade, every role input's wrapper and every wrapped gate command on both instances carry the new prefix. A broken prefix would break every command every role runs. The first scenario runs the composed wrapper and the wrapped gate command under `sh`, and the prototype ran them under bash and zsh. The prefix does nothing when `VIRTUAL_ENV` is unset, and otherwise removes only the exact `$VIRTUAL_ENV/bin` entry from `PATH`.
- An instance whose commands relied on an inherited, activated environment loses it inside the wrapper. It can name that environment in `run_env`.
- The sync runs inside `run start`, which the workflow's clerk runs as one shell command. The clerk is the agent that runs the harness's store commands for a workflow, and its shell tool stops a command after 2 minutes by default. A slow sync, such as uv with a cold cache, can run past that limit. The clerk then reports a failure, the workflow parks the ticket, and a checker checkout may be left behind for the operator to remove with `git worktree remove`. A uv cache pinned through `run_env` (Operator steps) keeps a repeat sync short.
- The sync runs the checkout's own build configuration (uv installs the project itself when the project is a package) before the role starts. This happens under the throwaway HOME, and it is what the gate commands and the roles already do in the same checkout.
- Each build run start takes one sync longer.

## Operator steps
The factory does not run from the checkout where tickets merge. It runs from the runtime, a separate checkout of this repository pinned to one harness revision. A merged change therefore takes effect only after two steps, both described in README ("Upgrading the runtime" and "Accepting a harness revision"). First, the runtime is moved to the new revision. Second, each instance records that it accepts that revision, with `--accept-harness <commit>`; until then the harness refuses to work on that instance's store.

1. After this change merges, the runtime is upgraded and this instance has accepted the new revision. Then add `environment_sync: "uv sync --frozen"` to this repository's `.factory/instance.yaml`. That file is protected infra, so only the operator edits it. With the key set, every build checkout has the `.venv` that this repository's acceptance scenarios already assume ("after `uv sync --frozen`"). Optional: add `UV_CACHE_DIR` to `run_env`, as instance A does, so each sync reuses the uv cache instead of filling a new one in each throwaway HOME.
2. Tell the Driver that the key exists. The Driver is the separate operator-run session that runs instance A's tickets. After instance A accepts the new revision, the Driver may set `environment_sync: "uv sync --frozen --all-extras --dev"` there. Before it does, it should check that `run_env` holds every uv variable its gate commands set, because the sync sees only the throwaway HOME and the `run_env` exports. Today that holds: its gate commands set `UV_CACHE_DIR` and `UV_PYTHON_INSTALL_DIR`, and its `run_env` already pins both (`~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-27). Its `environment_files` copies the git-ignored `uv.lock` into each checkout before the sync runs.

=== design.md
## Proposed change
One PR, about 220 changed lines: about 45 in the harness, 150 in a new test file, 2 in an existing test and about 20 in documents.

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
2. After `copy_environment_files` in both branches (implementer, and checker including the parent-close verifier), if a command is set, run it like this: `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`. The sync's output must never reach run start's stdout, whose last line stays its JSON.
3. On exit 0, set `meta["environment_sync"] = cmd`.
4. On a non-zero exit:
   - For a checker, remove the checkout it just made (`gitops.remove_worktree`). Keep the implementer's worktree.
   - Raise `Refused(f"environment_sync failed in {wt} (exit {code}): {cmd}\n{last 20 lines of stdout+stderr}")`.
   - Because `meta.yaml` and the in-flight list are written only after `_start_build_run` returns, the refusal records no run and puts nothing in flight. The empty `runs/<id>/` directory that `next_run_id` reserved stays, as it does today for the other refusals inside `_start_build_run`.

**D. The role is told** (`factory/compose.py`, the "Where you work" block for implementer, reviewer and verifier). When `meta.get("environment_sync")` is set, append this line after the gate-commands line, as its own line, so that the gate line still ends with its last wrapped command:
`Environment: the harness ran this instance's environment sync, `<command>`, in this checkout through the running-code wrapper before you started, so the environment is already synced. Do not sync it again unless your change alters the files it is built from.`
When the key is not set, the input is as today.

**E. Tests.**
- Update the one constant listed under Tests to change.
- Add `tests/factory/test_environment_sync.py`. It is black-box through `bin/factory`, on throwaway stores, with a copy of the suite's fixture instance where the key is set, in the style of `test_run_isolation.py`. It covers:
  - the composed wrapper run under `sh` with a fake activated environment: `VIRTUAL_ENV` and `PYTHONHOME` are unset, the environment's `bin/` is off `PATH` while the other `PATH` entries stay in order, and a `PATH` with no environment is unchanged;
  - the sync at an implementer start and again at a later dispatch to the same worktree;
  - the sync at a reviewer start and at a parent-close verifier start;
  - the sync's environment: no `VIRTUAL_ENV`, a fresh HOME, the `run_env` exports;
  - a failed sync: exit 2, the refusal text, nothing in flight, no checker checkout, no `meta.yaml`;
  - a non-string `environment_sync` refused before any checkout is made;
  - the input line present when the sync ran and absent when no key is set.

**F. Documents.**
- `docs/design.md`, in the "Role-context block" paragraph:
  - add `environment_sync` to the parenthetical list of what `instance.yaml` holds;
  - say that the running-code wrapper first drops an inherited virtual environment (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset);
  - add one sentence: when the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails, and the role's input says the environment is already synced.
- `docs/changelog.md`: append the next contiguously numbered entry, after whatever entries have merged by then. It records parts A to D in prose and names `environment_sync`, `VIRTUAL_ENV`, `PYTHONHOME` and the "already synced" line.
- `dev/build-harness.spec.md`, part I: add one item after I.3. It says that each build checkout runs the instance's `environment_sync`, if set, through the running-code wrapper at `run start`, before the role starts, and that a failure refuses the run.
- `README.md`:
  - In "Roles, harness, workflows", extend the wrapper sentence: the wrapper also drops a Python virtual environment inherited from the launching shell (`VIRTUAL_ENV`, `PYTHONHOME`, and its `bin/` on `PATH`).
  - In "Adopting the factory in a repo", step 3: set `environment_sync` to the command that installs the repo's environment, so each build checkout starts synced.
  - Bump the status date if the merge falls on a later day.
- No copy under `docs/prompts/` or `factory/prompts/` changes: no prompt block names the wrapper's contents.

## Tests to change
- `tests/factory/test_run_isolation.py`, the `WRAP` constant (line 22) only. It holds the exact expected wrapper text that five tests (six cases) compare against: `test_triage_input_carries_the_section_right_after_the_output_file`, `test_planner_and_implementer_inputs_carry_the_section_once`, `test_implementer_gate_commands_come_wrapped`, `test_run_env_is_exported_after_home_in_file_order_and_quoted` and both cases of `test_empty_or_null_run_env_exports_nothing`. Part A changes that text by design. The constant gains the part A prefix, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the constant is a `str.format` template. No assertion is removed or loosened, and `SECTION` is unchanged. With the prototype, this was the only edit needed to go from `6 failed, 294 passed` to `300 passed`.

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
When `environment_sync` exits non-zero, `run start` MUST refuse with exit 2, naming `environment_sync` and the exit code and giving the command's output. It MUST leave no run in flight and no checker checkout behind.

#### Scenario: A failed sync refuses the run start, names the sync, and leaves no run or checker checkout
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once. The sync command computes its output text and exit code, so that neither `sync-2` nor `exit 3` appears in the command itself.
- WHEN `(SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"; . ${TMPDIR:-/tmp}/t0031-env.sh && $B run start --role implementer --ticket T-0001.1 >/dev/null 2>$T31/e1; i=$?; git -C $S/worktrees/T-0001.1 commit -q --allow-empty -m work && H=$(git -C $S/worktrees/T-0001.1 rev-parse HEAD) && $B ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T31/e2; r=$?; echo "implementer: exit=$i named=$(has environment_sync $T31/e1) code=$(has 'exit 3' $T31/e1) output=$(has sync-2 $T31/e1)"; echo "reviewer: exit=$r named=$(has environment_sync $T31/e2) code=$(has 'exit 3' $T31/e2) output=$(has sync-2 $T31/e2)"; echo "in_flight=$($B ticket show T-0001.1 --json | tail -1 | grep -c '"in_flight": \[\]') checker_checkouts=$(git worktree list | grep -c '/runs/')")`
- THEN it prints exactly `implementer: exit=2 named=1 code=1 output=1`, then `reviewer: exit=2 named=1 code=1 output=1`, then `in_flight=1 checker_checkouts=0`

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
- A role's wrapper and its wrapped gate command drop an inherited virtual environment → NEW. Today both lines print `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`. The wrapper passes the inherited `VIRTUAL_ENV` and `PYTHONHOME` through, and the fake environment's `python` is found first. Run on `c2750bf` under bash and zsh.
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so → NEW. Today it prints `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0`, then `again: synced=no`: the `environment_sync` key is ignored and the input has no sync line.
- A checker's checkout is synced before the checker starts, and its input says so → NEW. Today it prints `synced=no ve= venv_on_path=0 noted=0`.
- A failed sync refuses the run start, names the sync, and leaves no run or checker checkout → NEW. Today it prints `implementer: exit=0 named=0 code=0 output=0`, `reviewer: exit=0 named=0 code=0 output=0`, `in_flight=0 checker_checkouts=1`: both runs start, both stay in flight, and the checker's checkout exists.
- Without environment_sync, run start and the input are as before → REGRESSION. Prints `started=yes noted=0 recorded=0 files=0` today.
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes → NEW. Today it prints `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`.
- The changelog records the environment sync as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`: the last entry (53) names none of the four terms.
- The environment-sync change adds no whitespace errors → REGRESSION. Prints `exit=0` today.

## Responses
- [BLOCKING] glosses of runtime, accepting a harness revision and instance → FIXED. Problem now says what an instance is where `instance.yaml` is introduced. Evidence names instance A as the other repository that runs the factory. Operator steps open with a short paragraph: the runtime is the separate checkout pinned to one harness revision, it is moved first, and each instance then accepts the revision with `--accept-harness <commit>`. The paragraph points to README's "Upgrading the runtime" and "Accepting a harness revision". Decisions' first use of "runtime" carries the same gloss.
- [SHOULD-FIX] glosses in Decisions → FIXED. `run_env` (the variables an instance gives the wrapper to export), conflict run (an implementer run after the merge step refused the branch), integration branch (the branch finished tickets merge into), build workflow (the script that dispatches the build roles), parks (stops the ticket for a human) and `meta.yaml` (the run's record file) are each glossed at first use. The Driver is glossed in Operator step 2.
- [SHOULD-FIX] `UV_PYTHON_INSTALL_DIR` missing from instance A's `run_env` → DISAGREE with the premise, wording tightened anyway. `grep -n -E 'run_env|UV_CACHE_DIR|UV_PYTHON_INSTALL_DIR' ~/dev/nanobot-upstream/.factory/instance.yaml` prints `25:run_env:`, `26:  UV_CACHE_DIR: /Users/dphang/.cache/uv`, `27:  UV_PYTHON_INSTALL_DIR: /Users/dphang/.local/share/uv/python`. `git -C ~/dev/nanobot-upstream show HEAD:.factory/instance.yaml` has the same three lines, and the file's last commit is `70c593103` (2026-10-04 10:06). So `run_env` already pins both variables, and the sync would find uv's managed Pythons. The critic's citation of lines 25-26 stops one line short. Step 2 now names both variables. It also tells the Driver to check that `run_env` covers every uv variable its gate commands set before it sets the key, because that is the condition the critic's concern rests on.
- [NIT] the `VIRTUAL_ENV` count → FIXED. Evidence now gives the dated count, 27 on 2026-10-04: 24 implementer, reviewer and verifier runs, plus this ticket's own triage, spec writer and critic runs. It also says the count grows as this ticket's runs land.
- Also changed: the Evidence repro pointed to round 1's scratch file, which the harness has since cleared. I re-ran the repro in this round on a fresh clone at `c2750bf`, with the same result, and the bullet now cites `.factory/state/runs/run-0283-spec_writer/scratch/repro-nosync.txt`. design.md, both spec files and the Acceptance list are unchanged from v1.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The build spec calls the store branch factory-store
- WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints `old_name=0 new_name=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: merge-gate

# merge-gate

## Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.

## Your prior findings (round 1)

## Critic review, round 1 (spec v1)

Spot-checks made, all from `~/dev/spec-factory` at `c2750bf` (the spec's cited HEAD), under the fresh-HOME wrapper:

- Cited paths and lines: `factory/compose.py` `run_env()` at 57-71 and `wrap()` at 74-78 (an f-string returning `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"{exports}; {command})`, no deactivation); `factory/cli.py` `_start_build_run()` at 238-263, `add_worktree` at 249, `add_detached_worktree` at 261, `copy_environment_files` at 254 and 262, no command run; `tests/factory/test_run_isolation.py` line 22 `WRAP = '(export HOME=...{vars}; {cmd})'`; `store.Refused` (`factory/store.py:25`), `gitops.remove_worktree` (`factory/gitops.py:59`), `store.next_run_id` (`factory/store.py:171`); the "Where you work" block in `factory/compose.py:175-179`, whose gate line ends with the last wrapped command; `docs/design.md:60` "Role-context block" paragraph; `dev/build-harness.spec.md:294` part I with items 1-6; README "Roles, harness, workflows" (line 25) and "Adopting the factory in a repo" step 3 (line 270); changelog's last entry is 53; `grep environment_sync|VIRTUAL_ENV` over design, README, build spec and both instance files finds nothing. Refusals print to stderr and exit 2 (`factory/cli.py:1480-1483`). `build.js:68` parks with `harness-bug: run start ${role}: ${stderr}`. Instance A's `instance.yaml` has `environment_files: ["uv.lock"]` and `run_env: {UV_CACHE_DIR: ...}`, as Operator step 2 says.
- Acceptance commands run on a throwaway store from the fixture block: scenario 1 (wrapper) printed `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` twice; scenario 4 (no key) printed `started=yes noted=0 recorded=0 files=0`; the failed-sync scenario printed `implementer: exit=0 named=0 code=0 output=0`, `reviewer: exit=0 named=0 code=0 output=0`, `in_flight=0 checker_checkouts=1`. All three match the verification file's "today" lines, so the NEW items fail today for the stated reason and the regression item passes.
- The part A prefix, run verbatim under `sh`, `bash` and `zsh` with `VIRTUAL_ENV=/x/venv PYTHONHOME=/x/venv PATH=/x/venv/bin:/usr/bin:/bin`, printed `ve=unset ph=unset path=/usr/bin:/bin`; with no `VIRTUAL_ENV`, PATH was unchanged.
- The suite collects 300 tests today, matching the spec's `300 passed` figure.
- Operator step 1's command: a fresh clone at `c2750bf` under a fresh HOME, with the inherited venv's `bin/` dropped from PATH, ran `uv sync --frozen` with exit 0 in 1 s, after which `uv run --no-sync --frozen python -c 'import yaml'` printed `yaml ok` (`scratch/sync.log`).

Findings:

[BLOCKING] 6 Operator steps, step 1; Evidence, first bullet
Problem: The first paragraph of Operator steps says "the runtime is upgraded and this instance accepts the new harness" and Evidence opens with "The Nanobot instance", and neither "runtime", "accepts the harness" nor "instance" is glossed anywhere in the spec, so an operator new to this system has to infer that the factory runs from a separate checkout which must be upgraded, and that each repository's instance must accept the new harness revision before it runs it.
Evidence: Read Problem, Evidence, Decisions and Operator steps for a gloss of "instance", "runtime" and "accept"; Problem glosses "role", "harness", "wrapper", "gate commands" and `instance.yaml` only. `README.md` lines 214-240 ("Accepting a harness revision", "Upgrading the runtime") are where those terms are defined, and the spec does not point there.
Suggested fix: In the Problem's third paragraph, gloss "instance" where `instance.yaml` is introduced ("a repository that runs the factory is an instance; its configuration is `instance.yaml`"), and in Operator step 1 add one clause: "the runtime, the separate checkout the factory runs from, is upgraded to this harness revision, and this instance records that it accepts it (README, 'Accepting a harness revision')".

[SHOULD-FIX] 6 Decisions, bullets 2, 4, 5 and 6
Problem: Later Decisions use `run_env`, "conflict run", "integration branch", "parks the ticket", "the build workflow" and `meta.yaml` without saying what each is, so the reader has to guess what an export through `run_env` does or what parking means.
Evidence: Decisions bullet 2 "`run_env` exports still come after the deactivation"; bullet 4 "a conflict run merges the integration branch in"; bullet 5 "The build workflow then parks the ticket"; bullet 6 "the run's `meta.yaml` records". None is glossed earlier in the human-facing sections.
Suggested fix: Add a few words at each first use: `run_env` "(the variables an instance lists for the wrapper to export)", "a conflict run (an implementer run after the merge gate refused the branch)", "parks the ticket (stops it for a human)", "`meta.yaml` (the run's record)".

[SHOULD-FIX] 4 Operator steps, step 2
Problem: Instance A's gate commands pin `UV_PYTHON_INSTALL_DIR` as well as `UV_CACHE_DIR`, so a sync run under a fresh HOME with only `UV_CACHE_DIR` in `run_env` may not find uv's managed Python and would refuse every build run start on that instance until the Driver adds the second variable.
Evidence: `~/dev/nanobot-upstream/.factory/instance.yaml` lines 25-26 (`run_env: {UV_CACHE_DIR: /Users/dphang/.cache/uv}`) and lines 40-41 (gate commands carry `UV_CACHE_DIR=... UV_PYTHON_INSTALL_DIR=/Users/dphang/.local/share/uv/python`). The spec's step 2 mentions only the cache.
Suggested fix: In step 2, tell the Driver to put every uv variable its gate commands set, `UV_PYTHON_INSTALL_DIR` included, into `run_env` before setting `environment_sync`, since the sync sees only `run_env` and the fresh HOME.

[NIT] 1 Evidence, second bullet
Problem: The count "matches 25 run outputs" is 26 on the live store today because runs land between writing and reading; the bullet's point stands.
Evidence: `grep -l VIRTUAL_ENV .factory/state/runs/*/output.md | wc -l` prints 26 at `c2750bf` with the uncommitted store.
Suggested fix: Say "at least 24 role runs" or date the count; no other change.

No scoping, consistency or hidden-decision findings: the change fits one PR, `Tests to change` names only the `WRAP` constant whose six cases part A breaks by design, every protected path touched is under Risk, and the sync's placement (every run start, both branches, through the wrapper, refuse on failure) is decided in the open with the rejected options named.

Out-of-scope observations:
- `factory/compose.py` `wrap()` is an f-string; the part A prefix contains `${VIRTUAL_ENV:-}`, so the implementer must keep it in the separate module constant design A names rather than paste it into the f-string. The design already says "module constant", so no spec change.
- The exact-entry match `grep -vxF "$VIRTUAL_ENV/bin"` leaves a `bin/` whose PATH spelling differs from `$VIRTUAL_ENV` (for example a symlinked prefix). Activate scripts write the same string, and Risk says "only the exact entry", so this is noted, not asked for.

STATUS: REVISE
CONFIDENCE: high, every cited path and three of the eight acceptance commands were run on the cited HEAD and behave as the spec says; the only blocking item is a glossing gap in the operator-facing sections.
ESCALATIONS: none

## Previous spec version (v1)

=== proposal.md
## Problem
Every agent that builds or checks code here loses a first attempt to a broken Python environment. The cost lands on the three build roles: the implementer, which writes the change, and the reviewer and verifier, which check it. A role is one agent job that the harness starts. The harness is the program that prepares each agent run and keeps its records. Each build role works in a fresh copy of the repository. For the implementer that copy is a git worktree on its branch. For a checker it is a detached checkout of the commit under review. Today two things go wrong in that copy.

First, the role's shell inherits a Python virtual environment that was activated in the session that launched the factory. On this machine that environment belongs to another checkout of a different repository. Its `python` and `pytest` come first on `PATH`, and uv warns about it on every command. The running-code wrapper does not remove it. That wrapper is the one-line shell prefix every role is told to put around each command it runs. It gives the command a throwaway home directory, and it also wraps the repository's check commands (the gate commands).

Second, the fresh copy has no project environment (`.venv`). A check command that tells uv not to install anything (`uv run --no-sync`) runs in an empty environment and fails on its first import. The implementer, then the reviewer, then the verifier each find this out, install the environment themselves, and run again. A checker that does not can report the import failure as a defect in the code it is checking.

This change does three things:
- The wrapper drops an inherited virtual environment.
- A repository can name one command, `environment_sync`, in its per-repository configuration (`instance.yaml`). The harness runs it in each build copy before the role starts.
- The role is told that the environment is already synced.
A repository that does not set the command behaves as it does today, apart from the wrapper change.

## Evidence
- The Nanobot instance, run-0259-implementer (2026-10-04), `~/dev/nanobot-upstream/.factory/state/runs/run-0259-implementer/output.md`, reports this under Out-of-scope observations: "The worktree had no `.venv`, and the shell inherits `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` from blue. As written, an acceptance command with `uv run --no-sync` in a fresh worktree makes an empty env and fails on imports (`No module named 'loguru'`, `No module named pytest`)." Its results section says the first attempt "ran with no project environment" and that the reported results are from the rerun. The implementer spent one full pass of acceptance commands before getting a real result.
- This repository: `grep -l VIRTUAL_ENV .factory/state/runs/*/output.md` matches 25 run outputs. One of them is this ticket's own triage (run-0274), which leaves 24 role runs. run-0060-verifier line 3 says: "Shell inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`; uv printed its "does not match the project environment path `.venv`…" warning". run-0216-verifier line 20 reports the same warning. Every build role on this instance sees the inherited value.
- The inherited environment is more than the variable. In this session, `echo $VIRTUAL_ENV` prints `/Users/dphang/dev/nanobot/.venv-test`, and the first `PATH` entry is `/Users/dphang/dev/nanobot/.venv-test/bin`. `which -a python pytest` lists `/Users/dphang/dev/nanobot/.venv-test/bin/python` and `/Users/dphang/dev/nanobot/.venv-test/bin/pytest` first. So a bare `python` or `pytest` in a role's shell runs the other repository's environment. Unsetting `VIRTUAL_ENV` alone would not change that.
- Reproduced on a fresh detached checkout of this repository's HEAD `c2750bf`, under the HOME wrapper. `.venv` did not exist. `uv run --no-sync python -c 'import yaml'` failed with `ModuleNotFoundError: No module named 'yaml'`, because uv made an empty environment. After `uv sync --frozen`, the same command printed `yaml ok`, together with uv's warning `` `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project environment path `.venv` and will be ignored ``. Output: `scratch/repro-nosync.txt` in this run's directory.
- Each acceptance command below was run on this checkout (`c2750bf`) under bash and under zsh:
  - The wrapper scenario printed `ve=<scratch>/venv ph=<scratch>/venv fake_python=1 …` for both the role wrapper and the wrapped gate command. Today's wrapper passes an inherited `VIRTUAL_ENV` and `PYTHONHOME` straight through, and the fake environment's `python` still wins on `PATH`.
  - The sync scenarios printed `synced=no`: today the harness ignores an `environment_sync` key.
  - The failed-sync scenario printed `exit=0` for both run starts and `checker_checkouts=1`: today a run starts whatever the key says.
- Feasibility: I applied a prototype of parts A to D to a scratch clone. It printed every THEN below exactly, under both shells. With that prototype, the harness suite gave `6 failed, 294 passed`. All six failures came from the expected wrapper text in `tests/factory/test_run_isolation.py`. With only that file's `WRAP` constant updated, the result was `300 passed`. This shows that no other existing test depends on the wrapper text or on run start's setup.
- The Nanobot harness has no fix to copy. `grep -rn -E "VIRTUAL_ENV|environment_sync|PYTHONHOME"` over `~/dev/nanobot-upstream/.factory` finds only notes in plans and specs (triage, confirmed by this run's own read of run-0259).

## Root cause
- `factory/compose.py:74-78`, `wrap()`: it builds `(export HOME=<fresh>[ run_env exports]; <command>)`. It never removes an inherited virtual environment. A role's shell inherits the launching session's environment, so `VIRTUAL_ENV`, `PYTHONHOME` and the environment's `bin/` on `PATH` all reach every command and every gate command.
- `factory/compose.py:57-71`, `run_env()`: it accepts only name-to-value pairs, so an instance cannot use it to unset a variable.
- `factory/cli.py:238-263`, `_start_build_run()`: it creates the implementer's worktree (line 249, only when missing) or the checker's detached checkout (line 261) and copies `environment_files`. It runs no command, so a new copy has no `.venv`.
- `factory/instance.template.yaml` and `.factory/instance.yaml` have no key that names a sync command.

## Out of scope
- The wrapper's other behaviour: the fresh HOME, the `run_env` exports and their order, and the prose of the "Running code" section. Only the wrapper's prefix changes.
- Every gate command, acceptance criterion and check, on both instances.
- Other ways a Python environment can leak in (`PYTHONPATH`, conda's `CONDA_PREFIX`). Nothing reported them.
- A time limit on the sync.
- Setting `environment_sync` on either instance. That is an operator step.
- The `harness-bug:` prefix that the build workflow already puts on a refused run start's park reason.

## Open questions
none

## Decisions
- The wrapper fully deactivates an inherited virtual environment. It removes the exact entry `$VIRTUAL_ENV/bin` from `PATH`, then unsets `VIRTUAL_ENV` and `PYTHONHOME`, all before it sets HOME. Rejected: unsetting only the two variables, as the requester proposed. The activating shell also put the environment's `bin/` first on `PATH`, so a bare `python` or `pytest` would still run the other repository's environment (Evidence).
- The deactivation is built into the wrapper for every instance, not configured per instance. Rejected: a way to unset variables through `run_env`. Every instance needs the deactivation, and opting in would leave it off by default. `run_env` exports still come after the deactivation, so an instance that wants a particular environment can still name it there.
- `environment_sync` is one optional shell command, given as a string in `instance.yaml`. If it is absent or null, nothing runs, as today. Any other non-string or empty value is refused at run start, before any checkout is made.
- The sync runs at every build-role run start, for the implementer, reviewer and verifier, including the verifier that checks the parent ticket after all its sub-tickets merge. It runs in that run's checkout, after the environment files are copied, through the same wrapper as role commands, so it gets the throwaway HOME, the `run_env` exports and no inherited environment. Rejected: syncing only when the implementer's worktree is first created. The environment files are copied again at every run start, and a conflict run merges the integration branch in. Either can change the lock file the environment was built from.
- A failed sync refuses the run start with exit 2. The refusal names `environment_sync`, the checkout, the command and its exit code, and gives the last 20 lines of its output. No run is recorded or put in flight, and a checker checkout made for the run is removed. The implementer's worktree is kept for the next dispatch. The build workflow then parks the ticket with its existing reason `harness-bug: run start <role>: …`, so a broken environment never reaches a checker as a code failure. Rejected: starting the role anyway with a note. The role would then rediscover the broken environment, which is the cost this change removes.
- When the sync ran, the run's `meta.yaml` records the command as `environment_sync`. The "Where you work" section of the role's input gains one line: the command ran, the environment is already synced, and the role should not sync again unless its change alters the files the environment is built from.
- This change sets `environment_sync` on neither instance. The operator sets it after the runtime upgrade (Operator steps). Rejected: setting it on this instance in the PR. That writes the protected `.factory/**`, and the key has no effect until the runtime runs the new harness anyway.

## Risk
- Protected paths this change touches: harness (`factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml`). It touches none of infra (`.factory/**`), generated (`docs/prompts/**`), `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, the reference harness or credentials. It does not change `factory/prompts/**`.
- Guardrail path: one existing test file, `tests/factory/test_run_isolation.py`. Only its `WRAP` constant changes, as declared under Tests to change.
- Blast radius: after the runtime upgrade, every role input's wrapper and every wrapped gate command on both instances carry the new prefix. A broken prefix would break every command every role runs. The first scenario runs the composed wrapper and the wrapped gate command under `sh`, and the prototype ran them under bash and zsh. The prefix does nothing when `VIRTUAL_ENV` is unset, and otherwise removes only the exact `$VIRTUAL_ENV/bin` entry from `PATH`.
- An instance whose commands relied on an inherited, activated environment loses it inside the wrapper. It can name that environment in `run_env`.
- The sync runs inside `run start`, which the workflow's clerk runs as one shell command. The clerk is the agent that runs the harness's store commands for a workflow, and its shell tool stops a command after 2 minutes by default. A slow sync, such as uv with a cold cache, can run past that limit. The clerk then reports a failure, the workflow parks the ticket, and a checker checkout may be left behind for the operator to remove with `git worktree remove`. A uv cache pinned through `run_env` (Operator steps) keeps a repeat sync short.
- The sync runs the checkout's own build configuration (uv installs the project itself when the project is a package) before the role starts. This happens under the throwaway HOME, and it is what the gate commands and the roles already do in the same checkout.
- Each build run start takes one sync longer.

## Operator steps
1. After this merges, the runtime is upgraded and this instance accepts the new harness, add `environment_sync: "uv sync --frozen"` to this repository's `.factory/instance.yaml`. That file is protected infra. With the key set, every build checkout has the `.venv` that this repository's acceptance scenarios already assume ("after `uv sync --frozen`"). Optional: add `UV_CACHE_DIR` to `run_env`, as instance A (the Nanobot fork's instance) does, so each sync reuses the uv cache instead of filling a new one in each throwaway HOME.
2. Tell the Driver session that runs instance A that the key exists. After it accepts the new harness, it may set `environment_sync: "uv sync --frozen --all-extras --dev"`. Its `environment_files` copies the git-ignored `uv.lock` into each checkout before the sync runs, and its `run_env` already pins the uv cache.

=== design.md
## Proposed change
One PR, about 220 changed lines: about 45 in the harness, 150 in a new test file, 2 in an existing test and about 20 in documents.

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
2. After `copy_environment_files` in both branches (implementer, and checker including the parent-close verifier), if a command is set, run it like this: `subprocess.run(["sh", "-c", compose.wrap(cmd, compose.run_env(cfg))], cwd=wt, capture_output=True, text=True)`. The sync's output must never reach run start's stdout, whose last line stays its JSON.
3. On exit 0, set `meta["environment_sync"] = cmd`.
4. On a non-zero exit:
   - For a checker, remove the checkout it just made (`gitops.remove_worktree`). Keep the implementer's worktree.
   - Raise `Refused(f"environment_sync failed in {wt} (exit {code}): {cmd}\n{last 20 lines of stdout+stderr}")`.
   - Because `meta.yaml` and the in-flight list are written only after `_start_build_run` returns, the refusal records no run and puts nothing in flight. The empty `runs/<id>/` directory that `next_run_id` reserved stays, as it does today for the other refusals inside `_start_build_run`.

**D. The role is told** (`factory/compose.py`, the "Where you work" block for implementer, reviewer and verifier). When `meta.get("environment_sync")` is set, append this line after the gate-commands line, as its own line, so that the gate line still ends with its last wrapped command:
`Environment: the harness ran this instance's environment sync, `<command>`, in this checkout through the running-code wrapper before you started, so the environment is already synced. Do not sync it again unless your change alters the files it is built from.`
When the key is not set, the input is as today.

**E. Tests.**
- Update the one constant listed under Tests to change.
- Add `tests/factory/test_environment_sync.py`. It is black-box through `bin/factory`, on throwaway stores, with a copy of the suite's fixture instance where the key is set, in the style of `test_run_isolation.py`. It covers:
  - the composed wrapper run under `sh` with a fake activated environment: `VIRTUAL_ENV` and `PYTHONHOME` are unset, the environment's `bin/` is off `PATH` while the other `PATH` entries stay in order, and a `PATH` with no environment is unchanged;
  - the sync at an implementer start and again at a later dispatch to the same worktree;
  - the sync at a reviewer start and at a parent-close verifier start;
  - the sync's environment: no `VIRTUAL_ENV`, a fresh HOME, the `run_env` exports;
  - a failed sync: exit 2, the refusal text, nothing in flight, no checker checkout, no `meta.yaml`;
  - a non-string `environment_sync` refused before any checkout is made;
  - the input line present when the sync ran and absent when no key is set.

**F. Documents.**
- `docs/design.md`, in the "Role-context block" paragraph:
  - add `environment_sync` to the parenthetical list of what `instance.yaml` holds;
  - say that the running-code wrapper first drops an inherited virtual environment (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset);
  - add one sentence: when the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails, and the role's input says the environment is already synced.
- `docs/changelog.md`: append the next contiguously numbered entry, after whatever entries have merged by then. It records parts A to D in prose and names `environment_sync`, `VIRTUAL_ENV`, `PYTHONHOME` and the "already synced" line.
- `dev/build-harness.spec.md`, part I: add one item after I.3. It says that each build checkout runs the instance's `environment_sync`, if set, through the running-code wrapper at `run start`, before the role starts, and that a failure refuses the run.
- `README.md`:
  - In "Roles, harness, workflows", extend the wrapper sentence: the wrapper also drops a Python virtual environment inherited from the launching shell (`VIRTUAL_ENV`, `PYTHONHOME`, and its `bin/` on `PATH`).
  - In "Adopting the factory in a repo", step 3: set `environment_sync` to the command that installs the repo's environment, so each build checkout starts synced.
  - Bump the status date if the merge falls on a later day.
- No copy under `docs/prompts/` or `factory/prompts/` changes: no prompt block names the wrapper's contents.

## Tests to change
- `tests/factory/test_run_isolation.py`, the `WRAP` constant (line 22) only. It holds the exact expected wrapper text that five tests (six cases) compare against: `test_triage_input_carries_the_section_right_after_the_output_file`, `test_planner_and_implementer_inputs_carry_the_section_once`, `test_implementer_gate_commands_come_wrapped`, `test_run_env_is_exported_after_home_in_file_order_and_quoted` and both cases of `test_empty_or_null_run_env_exports_nothing`. Part A changes that text by design. The constant gains the part A prefix, with `${VIRTUAL_ENV:-}` written as `${{VIRTUAL_ENV:-}}` because the constant is a `str.format` template. No assertion is removed or loosened, and `SECTION` is unchanged. With the prototype, this was the only edit needed to go from `6 failed, 294 passed` to `300 passed`.

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
When `environment_sync` exits non-zero, `run start` MUST refuse with exit 2, naming `environment_sync` and the exit code and giving the command's output. It MUST leave no run in flight and no checker checkout behind.

#### Scenario: A failed sync refuses the run start, names the sync, and leaves no run or checker checkout
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once. The sync command computes its output text and exit code, so that neither `sync-2` nor `exit 3` appears in the command itself.
- WHEN `(SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"; . ${TMPDIR:-/tmp}/t0031-env.sh && $B run start --role implementer --ticket T-0001.1 >/dev/null 2>$T31/e1; i=$?; git -C $S/worktrees/T-0001.1 commit -q --allow-empty -m work && H=$(git -C $S/worktrees/T-0001.1 rev-parse HEAD) && $B ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T31/e2; r=$?; echo "implementer: exit=$i named=$(has environment_sync $T31/e1) code=$(has 'exit 3' $T31/e1) output=$(has sync-2 $T31/e1)"; echo "reviewer: exit=$r named=$(has environment_sync $T31/e2) code=$(has 'exit 3' $T31/e2) output=$(has sync-2 $T31/e2)"; echo "in_flight=$($B ticket show T-0001.1 --json | tail -1 | grep -c '"in_flight": \[\]') checker_checkouts=$(git worktree list | grep -c '/runs/')")`
- THEN it prints exactly `implementer: exit=2 named=1 code=1 output=1`, then `reviewer: exit=2 named=1 code=1 output=1`, then `in_flight=1 checker_checkouts=0`

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
- A role's wrapper and its wrapped gate command drop an inherited virtual environment → NEW. Today both lines print `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh`. The wrapper passes the inherited `VIRTUAL_ENV` and `PYTHONHOME` through, and the fake environment's `python` is found first. Run on `c2750bf` under bash and zsh.
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so → NEW. Today it prints `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0`, then `again: synced=no`: the `environment_sync` key is ignored and the input has no sync line.
- A checker's checkout is synced before the checker starts, and its input says so → NEW. Today it prints `synced=no ve= venv_on_path=0 noted=0`.
- A failed sync refuses the run start, names the sync, and leaves no run or checker checkout → NEW. Today it prints `implementer: exit=0 named=0 code=0 output=0`, `reviewer: exit=0 named=0 code=0 output=0`, `in_flight=0 checker_checkouts=1`: both runs start, both stay in flight, and the checker's checkout exists.
- Without environment_sync, run start and the input are as before → REGRESSION. Prints `started=yes noted=0 recorded=0 files=0` today.
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes → NEW. Today it prints `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0`.
- The changelog records the environment sync as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`: the last entry (53) names none of the four terms.
- The environment-sync change adds no whitespace errors → REGRESSION. Prints `exit=0` today.
