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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0509-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0509-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0509-reviewer/wt` (branch `factory/T-0051.1`, base `88c65e147495debccaef62986a15df1ee54b59f4`, head `5e00a1f5261b2576ae6243b46ac8895f71042ff9`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0051.1

T-0051.1 / Get one harness-suite run well under the 10-minute tool-call cap, and name a background wait in the EMPTY-OUTPUT park reason (spec-factory #106)
Depends on: none
Parallel-safe: yes

Parent: T-0051, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- One suite run passes in under three minutes
- Two suite runs at once each pass in under five minutes
- Four stand-ins of one role started together all reply, 200 times over
- No test is removed and only the two listed assertions change
- The gate's suite command, as the instance lists it, passes in under three minutes
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
- One empty reviewer run followed by a real one routes on the real one
- An implementer that returns nothing twice parks as EMPTY-OUTPUT
- An intake role's second empty output in a row parks as EMPTY-OUTPUT
- An intake role that ends waiting twice parks with the waiting reason, in the driver and the script
- A build checker that ends waiting twice parks with the waiting reason, in the driver and the script
- A role whose last message is not about waiting parks with the plain reason
- The design doc and build spec name the waiting park reason, and no prompt copy changes
- The README names pytest-xdist and the waiting reason
- The changelog records issue 106 as its last entry, without a numbering gap
- The parallel-suite change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0051/v3.md`

=== proposal.md
## Problem

The factory's own test suite now takes six to ten minutes to run once, and the AI agents that must run it are cut off at ten minutes per command. This suite, the harness suite, is the 583 tests in `tests/factory/` that check the harness (the factory's code that runs each agent and enforces its rules). The agents are roles: the implementer writes a change and the verifier checks it, and both run the suite. A role runs each command through a tool call that is stopped after ten minutes. When the suite gets near that limit, a role starts it in the background and ends its turn to wait for it. Ending its turn ends the role's run, so it never writes its result.

The harness then does what it does for any run that ends without its output file. It records the run as EMPTY-OUTPUT, runs the same role once more on the same inputs, and parks the ticket after a second EMPTY-OUTPUT. A park stops the ticket until a human acts on it. A large ticket is built as sub-tickets, pieces that are each built, checked and merged on their own. On 2026-10-12 this stopped sub-ticket T-0047.2: both of its verifier runs ended on "Waiting for the suite runs to finish before writing the output."

Three things need fixing:

- **One suite run is too slow.** The tests run one after another on one CPU core. Most of each test's time is spent starting the factory's command-line program as a new process, about 5,600 times per run.
- **The park reason hides the cause.** A park after a background wait reads `EMPTY-OUTPUT from verifier`, the same as an agent that wrote nothing for any other reason. The human cannot tell from it that a plain redispatch (re-running the same role on the same commit) is likely to end the same way.
- **One suite test fails now and then under load.** The test stands in for the agent program with a small script. Each copy of that script counts its own calls in a shared file, with no lock. Two copies that start at the same moment can read the file while the other is rewriting it. The reader then crashes. The test runs it as a checker, one of the two roles (reviewer and verifier) that check a sub-ticket's commit, so the harness records that checker run as killed.

The proposed change has five lettered parts, and later sections refer to them by letter:

- **Part A** runs the suite's tests in parallel across CPU cores. A run then takes about a minute and a half on this machine, and two at once take under three minutes.
- **Part B** makes the gate commands use that parallel form, with no change to their text. Gate commands are the checks every sub-ticket must pass before merge; the verifier runs them.
- **Part C** puts a lock around the test stand-in's counter.
- **Part D** makes the park reason say so when either empty run's last message says it is waiting on a command.
- **Part E** updates the design documents, the README and the changelog.

No role prompt changes.

## Root cause

- Slow suite: the tests run one at a time, and about 5,600 CLI process starts per run dominate their time (Evidence). Nothing in the suite's configuration runs tests in parallel.
- Park reason: the three EMPTY-OUTPUT park sites write a fixed reason and never look at the last message the run left. `run last-message` stores that message but reports nothing about it.
- Flaky test: the two stand-ins in `tests/factory/_fixtures.py` (`STANDIN` and `BUILD_STANDIN`) update their per-role call counter without a lock. `Path.write_text` truncates the file before it writes, so a copy that reads at that moment gets an empty string, and `int('')` raises.

## Out of scope

- No role prompt changes, the preamble included. The request rules that out until the golden baseline exists (#96 row 4a).
- No change to the EMPTY-OUTPUT route itself: one automatic re-run, then a park; no result row; `resolve --redispatch` unchanged.
- The gate command text in `.factory/instance.yaml` does not change.
- Calling the CLI in-process in the suite. It was measured, and it is cut (Decisions).
- A release-file condition in the flaky test, in place of its 2-second sleeps. The failure it would prevent was not seen in 246 stressed runs; one failure there has no kept output (Evidence). The kill the request saw comes from the counter race, which Part C fixes.
- `test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit` (`test_drive_build.py:111`) depends on its 1.5-second sleeps overlapping in the same way. It did not fail in any run above. It is left as it is.
- No test is removed, and no assertion changes except the two under Tests to change.

## Open questions

none

## Decisions

- Part A runs the suite with pytest-xdist alone (`-n auto`): 66.80 to 146.81 s per run, and under 170 s for two at once. Rejected: calling the CLI in-process, alone (113 to 117 s) or with pytest-xdist (27 to 31 s). The test package's name shadows the harness package, so it needs a swap of the module table around every call, or a `tests/__init__.py` that writes into the checkout. It would also stop about 5,400 CLI calls per run from crossing a real process boundary. The parallel run alone meets the target with margin.
- pytest-xdist is switched on once, in `pyproject.toml` (`[tool.pytest.ini_options] addopts = "-n auto"`). So the gate command, the README's suite command and every current-truth scenario that runs the suite use it with no text change. That is Part B. Rejected: adding `-n auto` to `gate_commands`, which changes an infra path and leaves every scenario command running sequentially.
- Standing, for later tickets: the harness suite runs in parallel worker processes. A new test must not depend on test order. It must not share a file, port, environment variable or other process-wide state with another test, outside its own `tmp_path`.
- The suite gains a dev dependency, pytest-xdist, which `uv run --frozen` installs from the lock. This is a deliberate exception to the 2026-10-04 T-0023 decision, "the suite does not need node today and adding that would change what the gate needs", and the request asks for it.
- The flaky test is fixed at its measured cause: a file lock around both stand-ins' call counter. Its 2-second sleeps stay. Rejected: the triage's reading, that the sleeps should become a condition the test waits on. No failure of that kind was seen, though one stressed failure has no kept output (Evidence).
- The time bounds are under 180 s for one run, from the request's target of 3 minutes, and under 300 s for each of two runs at once. Measured: 66.80 to 146.81 s, and 162.35 to 169.66 s.
- `run last-message` alone decides whether a run was waiting, from the text it keeps, and prints `"waiting": true` or `false`. The driver and both scripts read that field. Rejected: a pattern in each of the three callers, three definitions of one rule. Also rejected: a separate command, one more store call per empty run.
- A kept message counts as waiting when, ignoring case, it contains the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`. It is a hint, not a route: a wrong match only adds a misleading phrase to a park a human reads anyway.
- The park reason is `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either of the two runs was waiting, and `EMPTY-OUTPUT from <role>` otherwise. The prefix is kept so that anything that reads the reason's start reads it as before. A failed `run last-message` call counts as not waiting.
- The README's "Empty output" entry stops saying that it has not fired on a real ticket. It fired on T-0047.2.

## Risk

- Any checkout whose Python environment lacks pytest-xdist fails every suite command after this merges, with `error: unrecognized arguments: -n`, until it runs `uv sync --frozen`. `uv run --frozen` (the gate command) syncs on its own. Scenarios already say "after `uv sync --frozen`". The runtime upgrade step in the README already runs `uv sync --frozen`. The dev checkout needs it once (Operator steps).
- `-n auto` starts one worker per CPU core: 10 here, 20 for two runs at once. A test that shares state with another would now fail intermittently. None does today: all 583 passed in each of 14 full parallel runs.
- The time bounds were measured on this 10-core machine. On a much slower machine the three timing scenarios could fail with no defect in the change.
- A park reason now has two forms for EMPTY-OUTPUT. `factory stats` counts the waiting form as its own row. `resolve`'s checks on park reasons read `NEEDS-HUMAN`, `ESCALATE`, `BLOCKED` and `harness-bug` prefixes (`factory/human.py:211-226`) and are unaffected.
- `tests/factory/_fixtures.py` changes. It is a helper module that every driver test uses, not a test file under the harness's test-file rule (`factory/drift.py:38`).

Protected paths: `pyproject.toml`, `uv.lock`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`

## Operator steps

1. After the merge, run `uv sync --frozen` in `~/dev/spec-factory`, so that its `.venv` has pytest-xdist. Until then, `.venv/bin/python -m pytest ... tests/factory` there stops with `unrecognized arguments: -n`.
2. When the runtime moves to the merged revision, the README's existing upgrade step, `uv sync --frozen` in `~/dev/spec-factory-harness`, installs it there. Nothing new is needed.

=== design.md
## Proposed change

One PR; about 130 changed lines, 27 of them in `uv.lock`.

A. **Parallel suite.**
   - Run `uv add --dev pytest-xdist` (pin `>=3.8.0`). `pyproject.toml`'s `dev` group gains it, and `uv.lock` gains `execnet` and `pytest-xdist` only.
   - Add `[tool.pytest.ini_options]` with `addopts = "-n auto"` to `pyproject.toml`, under a one-line comment: the suite runs across every CPU core so that one run stays well under the 10-minute limit of a single agent tool call.
   - Change no test's code for this part.
   - Confirm that `--collect-only` lists the same test ids as before.

B. **The gate and the verifier's suite checks use the parallel form.** Part A's `addopts` covers them. The gate command in `.factory/instance.yaml` and every scenario command keep their text. Do not edit `.factory/instance.yaml`.

C. **Stand-ins safe to start together.** In `tests/factory/_fixtures.py`, in both `STANDIN` and `BUILD_STANDIN`:
   - Hold an exclusive `fcntl.flock` on a lock file beside the log (for example `log.with_name(log.name + ".lock")`) around the read, increment and write of the `.n-<role>` counter.
   - Import `fcntl` in each stand-in's import line.
   - Change nothing else in either stand-in. Plays, the log line, the times file and the reply stay as they are.
   - Do not change `test_drive_build.py`.

D. **The park reason names a background wait.**
   1. `factory/cli.py`: next to `run_last_message`, add one module constant, a case-insensitive regex for the rule in Decisions: `\bwait(?:ing)?\b|\bstill (?:running|in progress)\b|\bin the background\b`. `run last-message` adds `"waiting": <bool>` to the JSON it prints, from that regex on the `--text` it keeps. Nothing else in the command changes, and the file stays under 900 lines.
   2. `factory/drive.py`:
      - `run_once` keeps the result of its `run last-message` call. It returns `"waiting": True` only when that call returned `waiting` true, and `False` in every other case, including when no call was made or the call failed.
      - `run_role` parks with `EMPTY-OUTPUT from {role}: ended its turn waiting on a background command` when either run returned `waiting` true, and with today's reason otherwise.
      - The phrase is one module constant.
   3. `factory/workflows/intake.js` and `factory/workflows/build.js` make the same change in `runOnce` and `runRole`. `runOnce` returns `waiting` from the `run last-message` clerk reply (`=== true`). `runRole` adds the phrase to the reason when either run's `waiting` is true.
   4. Tests: update the two assertions under Tests to change. Add one new test function to `tests/factory/test_empty_output.py`, using that file's `Store`: a kept message that does not say it is waiting, such as "I could not finish: the input file was missing.", prints `"waiting": false`. Do not import from another test file.

E. **Documents.**
   - `docs/design.md`: at the end of the bullet that starts `- A role run that ends without writing its output is EMPTY-OUTPUT`, add one sentence. It says that when either run's last message says it is still waiting on a command it started, the park reason adds `ended its turn waiting on a background command`, because a plain re-dispatch would end the same way. The routing-table rows stay as they are.
   - `dev/build-harness.spec.md`:
     - In the `factory run last-message` bullet (line 206), add that it also prints `waiting`: whether T says the run is still waiting on a command.
     - In the Empty output item (line 306), add the second reason form next to `EMPTY-OUTPUT from <role>`.
   - `README.md`:
     - Under "Installing the harness", say that the suite runs across every CPU core with pytest-xdist, set in `pyproject.toml`.
     - In the `- **Empty output.**` bullet, add the waiting reason, with the phrase `ended its turn waiting on a background command`. Replace "It is tested, and has not yet fired on a real ticket." with a sentence saying that it has fired on a real ticket. No ticket id goes in the body.
     - Bump the status header's date.
   - `docs/changelog.md`: add entry 71, `71. After issue #106 (2026-10-12), ...`. It records the parallel suite (pytest-xdist), the stand-in lock, the waiting park reason with its phrase, and the rejected in-process route, in the style of entry 57.
   - Do not change any `docs/prompts/` file or role prompt.

## Tests to change

- `tests/factory/test_drive.py:57`, in `test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message`. Its stand-in triage says "still waiting on my commands", and the test asserts `parked["reason"] == "EMPTY-OUTPUT from triage"`. Under the Decision on the park reason it becomes `"EMPTY-OUTPUT from triage: ended its turn waiting on a background command"`.
- `tests/factory/test_empty_output.py:63`, in `test_last_message_is_kept_for_an_empty_output_run`. It asserts that `run last-message` prints exactly `{"ok", "run_id", "last_message"}`. Under the Decision that `run last-message` reports `waiting`, the expected object gains `"waiting": True`, because its text "The suite is still running; ..." is a waiting message. The same file also gains the new test function of Part D.4.

`tests/factory/test_drive_build.py:60` also asserts `== "EMPTY-OUTPUT from reviewer"`, and it does not change. Its stand-in reviewer says `""`, and the driver sends only a non-blank message to `run last-message` (`factory/drive.py:241`, guarded by `and said`), so its reason stays plain. No other existing test pins the old reason or the old `run last-message` output (`grep -rn "EMPTY-OUTPUT from" tests/` lists these three sites). With exactly the two changes above, the full suite passed on the Part D prototype.

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: One harness-suite run finishes in under three minutes
One run of the harness suite, as `.venv/bin/python -m pytest -q -p no:cacheprovider tests/factory` runs it after `uv sync --frozen`, SHALL pass every test and finish in under 180 seconds on the operator's machine.

#### Scenario: One suite run passes in under three minutes
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the script written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0051-time.py <<'EOF'
# .venv/bin/python t0051-time.py N LIMIT CMD...: from the checkout under test, starts N copies of the shell
# command CMD at once, each with its own fresh TMPDIR under /tmp, and stops any copy still running
# LIMIT seconds after the start. Prints one line per copy, in order: its output's last line, or
# `stopped`, then ` | under LIMIT s` or ` | over LIMIT s` by its own wall time.
import os, shutil, subprocess, sys, tempfile, time
n, limit, cmd = int(sys.argv[1]), float(sys.argv[2]), " ".join(sys.argv[3:])
t0, runs = time.monotonic(), []
for _ in range(n):
    d = tempfile.mkdtemp(prefix="t0051-time.", dir="/tmp")
    runs.append((d, subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                     env={**os.environ, "TMPDIR": d}, start_new_session=True)))
for d, p in runs:
    try:
        out, _ = p.communicate(timeout=max(0.1, limit - (time.monotonic() - t0)))
        last, took = (out.strip().splitlines() or [""])[-1], time.monotonic() - t0
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9); p.communicate(); last, took = "stopped", limit + 1
    shutil.rmtree(d, ignore_errors=True)
    print(f"{last} | {'under' if took < limit else 'over'} {limit:g} s")
EOF
```

- WHEN `.venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 1 180 .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`
- THEN it prints one line that reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 180 s`

### Requirement: Two harness-suite runs at once each finish in under five minutes
Two runs of the harness suite started at the same moment SHALL each pass every test and finish in under 300 seconds on the operator's machine.

#### Scenario: Two suite runs at once each pass in under five minutes
Needs the GIVEN block of "One suite run passes in under three minutes" run once.
- WHEN `.venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 2 300 .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`
- THEN it prints two lines, each of which reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 300 s`

### Requirement: The suite's stand-in agent replies when several copies of one role start at once
Each stand-in for the `claude` program that the harness suite's driver tests use MUST reply with its JSON object and exit 0 when several copies of the same role start at the same moment and share one log.

#### Scenario: Four stand-ins of one role started together all reply, 200 times over
The script names the suite's helper module and its two stand-in programs, because this ticket's subject is the suite's own reliability (as the standing 2026-10-12 T-0045 decision allows for the suite's structure).
- GIVEN the script written by the block below, run once at column 0 as shown

```sh
cat > ${TMPDIR:-/tmp}/t0051-standin.py <<'EOF'
# .venv/bin/python t0051-standin.py, from the checkout under test: for each stand-in `claude` of the
# harness suite (the intake one and the build one), 200 times, starts four copies of the same role
# at once from four run directories that share one log, as the driver does for the checkers of four
# sub-tickets. Prints `<stand-in>: 200 rounds, <n> with a copy that did not reply, counter <c>`, where
# a copy that did not reply exited non-zero or printed no JSON object, and <c> is the stand-in's own
# count of verifier calls at the end (800 when no call was lost).
import json, os, subprocess, sys, tempfile, pathlib
sys.path.insert(0, "tests")
from factory import _fixtures as F  # the suite's helper module (tests/factory/_fixtures.py)
for name in ("STANDIN", "BUILD_STANDIN"):
    t = pathlib.Path(tempfile.mkdtemp()); exe = t / "claude"
    exe.write_text(getattr(F, name).format(python=sys.executable)); exe.chmod(0o755)
    env = {**os.environ, "STANDIN_LOG": str(t / "claude.log"), "STANDIN_PLAYS": json.dumps({"verifier": [{"say": "x"}]})}
    bad = 0
    for i in range(200):
        dirs = [t / f"r{i}" / f"run-000{k}-verifier" for k in (1, 2, 3, 4)]
        for d in dirs:
            d.mkdir(parents=True)
        ps = [subprocess.Popen([str(exe)], cwd=d, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for d in dirs]
        res = [(p.wait(), p.stdout.read()) for p in ps]
        def replied(rc, out):
            try:
                return rc == 0 and isinstance(json.loads(out), dict)
            except ValueError:
                return False
        bad += not all(replied(rc, out) for rc, out in res)
    nf = t / "claude.log.n-verifier"
    print(f"{name}: 200 rounds, {bad} with a copy that did not reply, counter {nf.read_text().strip() if nf.exists() else 'none'}")
EOF
```

- WHEN `.venv/bin/python -B ${TMPDIR:-/tmp}/t0051-standin.py`
- THEN it prints exactly `STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`, then `BUILD_STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`

### Requirement: This change keeps every test and assertion but the two the waiting park reason changes
Across this change's own merges and unmerged commits, the harness suite SHALL lose no test, and every assert statement in every existing test function MUST still be present in that function, except the two assertions listed under Tests to change.

#### Scenario: No test is removed and only the two listed assertions change
The command compares each `Merge factory/T-0051.<n>` commit reachable from HEAD with its first parent, and `git merge-base HEAD main` with HEAD, and adds up the results, so changes other tickets make to the same files are never counted. A collection failure shows as removed tests. tar may print a locale warning on stderr; it is not part of the result.
- WHEN `T=$(mktemp -d); { for m in $(git log --format=%H --grep='^Merge factory/T-0051[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do [ -d "$T/$s" ] || { mkdir "$T/$s" && git archive "$s" | tar -x -C "$T/$s" && ln -s "$PWD/.venv" "$T/$s/.venv" && (cd "$T/$s" && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/factory 2>&1 | grep '::' | sort > ids); }; done; echo "pair $b $h"; comm -23 "$T/$b/ids" "$T/$h/ids" | sed 's/^/removed /'; comm -13 "$T/$b/ids" "$T/$h/ids" | sed 's/^/added /'; .venv/bin/python -c 'import ast,pathlib,sys; A=lambda r: {f"{p.name}::{n.name}": {ast.unparse(a) for a in ast.walk(n) if isinstance(a,ast.Assert)} for p in sorted(pathlib.Path(r,"tests/factory").glob("test_*.py")) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith("test_")}; b,h=A(sys.argv[1]),A(sys.argv[2]); [print(f"missing {k}: {a[:80]}") for k in sorted(b) for a in sorted(b[k]-h.get(k,set()))]' "$T/$b" "$T/$h"; done > "$T/out"; for k in pair removed added missing; do echo "$k: $(grep -c "^$k " "$T/out")"; grep "^$k " "$T/out" | grep -v '^pair '; done; rm -rf "$T"`
- THEN `pair:` is at least 1; it prints `removed: 0`; every `added` line names a test in `tests/factory/test_empty_output.py`; and it prints `missing: 2`, followed by exactly one line that starts `missing test_drive.py::test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message: assert parked['reason'] == 'EMPTY-OUTPUT from triage'` and one that starts `missing test_empty_output.py::test_last_message_is_kept_for_an_empty_output_run: assert res == {'ok': True, 'run_id': s.rid, 'last_message':`

=== specs/gate-commands/spec.md
## ADDED Requirements

### Requirement: The gate's suite command finishes in under three minutes
The harness-suite command in this repository's `gate_commands` SHALL, run as written, pass every test and finish in under 180 seconds on the operator's machine.

#### Scenario: The gate's suite command, as the instance lists it, passes in under three minutes
Needs the GIVEN block of "One suite run passes in under three minutes" (this change, harness-suite) run once.
- WHEN `(C=$(sed -n 's/^  - "\(uv run .*tests\/factory\)"$/\1/p' .factory/instance.yaml); echo "gate: $C"; .venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 1 180 "$C")`
- THEN it prints exactly `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then one line that reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 180 s`

=== specs/build-dispatch/spec.md
## MODIFIED Requirements

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run, and as `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run's kept last message says it is still waiting on a command.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

## ADDED Requirements

### Requirement: The EMPTY-OUTPUT park says when a role ended its turn waiting on a command
`factory run last-message` MUST print `"waiting": true` when the text it keeps contains, ignoring case, the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`, and `"waiting": false` otherwise. `factory drive` and both Workflow scripts SHALL park a second EMPTY-OUTPUT in a row as `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run's `run last-message` call printed `"waiting": true`, and as `EMPTY-OUTPUT from <role>` otherwise. The driver and the script MUST still leave the same records.

#### Scenario: An intake role that ends waiting twice parks with the waiting reason, in the driver and the script
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" (current truth, build-dispatch) run once.
- WHEN `(P='{"triage": [{"say": "Waiting for the suite runs to finish before writing the output."}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh; for side in script drive; do echo "$side $(sed -n 's/^ticket T-0001 .*reason=//p' $D/$side.records)"; done)`
- THEN it prints exactly `parked script=2/2 drive=2/2 same`, then `script EMPTY-OUTPUT from triage: ended its turn waiting on a background command`, then `drive EMPTY-OUTPUT from triage: ended its turn waiting on a background command`

#### Scenario: A build checker that ends waiting twice parks with the waiting reason, in the driver and the script
Needs the GIVEN blocks named in "An intake role that ends waiting twice parks with the waiting reason, in the driver and the script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": "Waiting for the suite runs to finish before writing the output."}], "verifier": [{"write": "SPEC-DEFECT"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh; for side in script drive; do echo "$side $(sed -n 's/^ticket T-0001.1 .*reason=//p' $D/$side.records)"; done)`
- THEN it prints exactly `planned script=4/4 drive=4/4 same`, then `script EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, then `drive EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`

#### Scenario: A role whose last message is not about waiting parks with the plain reason
Needs the GIVEN blocks named in "An intake role that ends waiting twice parks with the waiting reason, in the driver and the script" run once.
- WHEN `(P='{"triage": [{"say": "I could not finish: the input file was missing."}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh; for side in script drive; do echo "$side $(sed -n 's/^ticket T-0001 .*reason=//p' $D/$side.records)"; done)`
- THEN it prints exactly `parked script=2/2 drive=2/2 same`, then `script EMPTY-OUTPUT from triage`, then `drive EMPTY-OUTPUT from triage`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the parallel suite and the waiting park reason
`docs/design.md`'s EMPTY-OUTPUT rule and `dev/build-harness.spec.md` SHALL name the waiting park reason, and the build spec's `run last-message` entry SHALL name its `waiting` field. `README.md` SHALL name pytest-xdist, and its Empty output entry SHALL give the waiting reason and no longer say it has not fired on a real ticket. `docs/changelog.md` SHALL gain entry 71 for issue #106, numbered without a gap. No `docs/prompts/` file SHALL change, and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec name the waiting park reason, and no prompt copy changes
- WHEN `(echo "design=$(grep '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md | grep -c 'ended its turn waiting on a background command') spec=$(grep -c 'ended its turn waiting on a background command' dev/build-harness.spec.md | awk '{print ($1 > 0)}') cli=$(grep '^- .factory run last-message' dev/build-harness.spec.md | grep -c 'waiting') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 spec=1 cli=1 prompts=0`

#### Scenario: The README names pytest-xdist and the waiting reason
- WHEN `(B=$(awk '/^- \*\*Empty output\.\*\*/{f=1; print; next} f && /^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "bullet=$(grep -c '^- \*\*Empty output\.\*\*' README.md) waiting=$(echo "$B" | grep -c 'ended its turn waiting on a background command') unfired=$(echo "$B" | grep -c 'has not yet fired') xdist=$(grep -c 'pytest-xdist' README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `bullet=1 waiting=1 unfired=0 xdist=1`

#### Scenario: The changelog records issue 106 as its last entry, without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; L=$(grep '^[0-9]*\. ' docs/changelog.md | tail -1); echo "$L" | grep -c '^71\. After issue #106 '; echo "$L" | grep -oF -e 'pytest-xdist' -e 'ended its turn waiting on a background command' -e 'EMPTY-OUTPUT' -e 'stand-in' -e 'in-process' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The parallel-suite change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints exactly `exit=0`

=== verification.md
## Acceptance

Each item was run through the running-code wrapper on `main` at `88c65e1` and on a scratch prototype of Parts A to D, except where it says otherwise. The prototype had no document changes, so the four document items were run on `main` only. Two base runs were not made, because their result follows from a measured one; each says so.

- One suite run passes in under three minutes → NEW. Fails today: the suite runs one test at a time, 385.56 s on this machine, so the script stops it and prints `stopped | over 180 s`. The prototype printed `583 passed in 93.99s (0:01:33) | under 180 s`.
- Two suite runs at once each pass in under five minutes → NEW. Fails today: one run alone takes 385.56 s, so each of the two must print `stopped | over 300 s`. Not run on `main`; the script stops both at 300 s, so the verifier's base run fits in one tool call. The prototype printed two lines, `583 passed in 162.35s` and `583 passed in 162.48s`, each `| under 300 s`.
- Four stand-ins of one role started together all reply, 200 times over → NEW. Fails today: on this revision's script, `STANDIN: 200 rounds, 13 with a copy that did not reply, counter 769` and `BUILD_STANDIN: 200 rounds, 21 with a copy that did not reply, counter 763`. The counts vary run to run: the script exactly as written here, run again on `main`, printed `5 ... counter 777` and `16 ... counter 765`. A locked prototype of Part C printed `0` and `counter 800` for both. A fix that swallows the parse error and restarts the count would still print a counter below 800. This is the deterministic check of the cause of the intermittent failure of the test at `test_drive_build.py:123`.
- No test is removed and only the two listed assertions change → NEW. Fails today: with no change, HEAD equals its merge base, so it prints `pair: 0` and `missing: 0`. The prototype printed `pair: 1`, `removed: 0`, `added: 0`, `missing: 2` and the two expected lines. The new test of Part D.4 will add one `added` line.
- The gate's suite command, as the instance lists it, passes in under three minutes → NEW. Fails today: the first line is as expected, then `stopped | over 180 s`, because on `main` the gate command runs the suite one test at a time (385.56 s). Not run on `main`; the same command form printed `stopped | over 180 s` there in the item above. The prototype printed `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then `583 passed in 97.65s (0:01:37) | under 180 s`.
The four scenarios of the MODIFIED requirement "A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT":
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows → NEW. Fails today: the first line is `park T-0001.1: EMPTY-OUTPUT from reviewer`, with no waiting phrase. The other three lines are the same before and after.
- One empty reviewer run followed by a real one routes on the real one → REGRESSION. Passed on `main` and on the prototype.
- An implementer that returns nothing twice parks as EMPTY-OUTPUT → REGRESSION. Passed on both.
- An intake role's second empty output in a row parks as EMPTY-OUTPUT → REGRESSION. Passed on both. The stub store's `run last-message` reply carries no `waiting`, so the reason stays plain.
- An intake role that ends waiting twice parks with the waiting reason, in the driver and the script → NEW. Fails today: `script EMPTY-OUTPUT from triage` and `drive EMPTY-OUTPUT from triage`.
- A build checker that ends waiting twice parks with the waiting reason, in the driver and the script → NEW. Fails today: `script EMPTY-OUTPUT from reviewer` and `drive EMPTY-OUTPUT from reviewer`.
- A role whose last message is not about waiting parks with the plain reason → REGRESSION. Prints the expected three lines on `main` and on the prototype.
- The design doc and build spec name the waiting park reason, and no prompt copy changes → NEW. Fails today: `design=0 spec=0 cli=0 prompts=0`.
- The README names pytest-xdist and the waiting reason → NEW. Fails today: `bullet=1 waiting=0 unfired=1 xdist=0`.
- The changelog records issue 106 as its last entry, without a numbering gap → NEW. Fails today: `CONTIGUOUS`, then `0`, then `0`; the last entry is 70.
- The parallel-suite change adds no whitespace errors → REGRESSION. On `main` there is no diff, and it prints `exit=0`.

These current-truth scenarios were run on the prototype and print their current-truth results unchanged:
- build-dispatch: "The driver takes the intake fixtures through the same routes as the intake script" and "The driver takes the build fixtures through the same routes as the build script".
- harness-suite: "A suite run in a fresh clone passes and adds nothing to the checkout" and "The harness suite passes with an uncommitted harness edit".
- harness-code: "factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines", which reads 890 lines.

## PR description (the implementer's output)

Sub-ticket: T-0051.1 (parent T-0051, approved spec v3, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0051/v3.md`). Branch `factory/T-0051.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0051.1`, base `88c65e1`, head `5e00a1f` (two commits: `ac71304` holds the change, and `5e00a1f` adds one `factory:` comment).

## What changed

One run of the harness suite now takes about 100 seconds instead of more than six minutes. The harness suite is the 584 tests in `tests/factory/` that check the factory's own code. The suite's test stand-ins no longer crash when several copies start at once. When an agent ends its turn waiting on a command it started in the background, the park reason now says so. A park is the stop that holds a ticket until a human acts on it.

- **A. Parallel suite.** `uv add --dev 'pytest-xdist>=3.8.0'` added pytest-xdist to the `dev` group in `pyproject.toml`. In `uv.lock` it added only `execnet` 2.1.2 and `pytest-xdist` 3.8.0. `pyproject.toml` gains `[tool.pytest.ini_options] addopts = "-n auto"` under the one-line comment the spec asks for. No test code changed for this part. Collection is unchanged apart from the new test: the "No test is removed" scenario printed `removed: 0` and one `added` line.
- **B. Gate and scenarios.** This part needed no edit: Part A's `addopts` covers the gate command and every scenario that runs the suite. `.factory/instance.yaml` is untouched.
- **C. Stand-in lock.** In `tests/factory/_fixtures.py`, `STANDIN` and `BUILD_STANDIN` now take an exclusive `fcntl.flock` around the read, increment and write of the `.n-<role>` counter. The lock file is `<log>.lock`, next to the log. Both stand-ins now import `fcntl`. Nothing else in either stand-in changed, and `test_drive_build.py` is untouched.
- **D. Waiting park reason.**
  - `factory/cli.py` gains the module constant `WAITING`, the regex from the spec. `run last-message` adds `"waiting": bool(WAITING.search(a.text))` to its JSON. `cli.py` is 891 lines.
  - In `factory/drive.py`, `run_once` keeps the result of its `run last-message` call. It returns `waiting` as `True` only when that call printed `waiting` true, and `False` otherwise, including when no call is made or the call fails. `run_role` adds the constant `WAITING_REASON` (`": ended its turn waiting on a background command"`) to the park reason when either run was waiting.
  - `factory/workflows/intake.js` and `factory/workflows/build.js` make the same change in `runOnce` and `runRole`, using `kept.waiting === true`. Each script has its own `WAITING_REASON` constant.
  - Callers, found by grep (`run_once(`, `runOnce(`, `last-message` under `factory/`): `run_once` and `runOnce` are called only from `run_role` and `runRole`, two calls each. `run last-message` is called only from those three `run_once`/`runOnce` functions. Neither change affects any other caller.
- **E. Documents.**
  - `docs/design.md`: one sentence at the end of the EMPTY-OUTPUT bullet.
  - `dev/build-harness.spec.md`: the `run last-message` bullet now names `waiting` and its rule. The Empty output item (line 306) gives the second reason form.
  - `README.md`: "Installing the harness" names pytest-xdist and where it is set. The Empty output bullet gives the waiting reason. "has not yet fired" is replaced by a sentence saying it fired on a real ticket, with no ticket id. The status date is now 2026-10-13.
  - `docs/changelog.md`: entry 71 for issue #106. No `docs/prompts/` file or role prompt changed.

## Acceptance results

I ran every command exactly as the spec words it, through the running-code wrapper, from the worktree. A diff of each command against the spec's `- WHEN` lines matched all 16. The GIVEN blocks came from the spec and the current-truth `human-resolution` and `build-dispatch` specs, written once into `TMPDIR=<scratch>/tmp`. The timing results below are from `ac71304`. The change in `5e00a1f` is a comment only. Both gates were re-run on `5e00a1f`, and so were the three checks that compare HEAD with main ("No test is removed", "The design doc and build spec name the waiting park reason", "The parallel-suite change adds no whitespace errors"). Their results were the same.

| Scenario | Kind | Before (base `88c65e1`) | After |
|---|---|---|---|
| One suite run passes in under three minutes | NEW | `stopped \| over 180 s` | `584 passed in 98.19s (0:01:38) \| under 180 s` |
| Two suite runs at once each pass in under five minutes | NEW | not run: one base run alone did not finish within 180 s (row above), so this one must be stopped at 300 s; the spec skipped it for the same reason | `584 passed in 163.04s (0:02:43) \| under 300 s`, then `584 passed in 166.12s (0:02:46) \| under 300 s` |
| Four stand-ins of one role started together all reply, 200 times over | NEW | `STANDIN: 200 rounds, 6 with a copy that did not reply, counter 785`, then `BUILD_STANDIN: 200 rounds, 4 ..., counter 786` | `STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`, then `BUILD_STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800` |
| No test is removed and only the two listed assertions change | NEW | `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` | `pair: 1`, `removed: 0`, `added: 1` (`test_empty_output.py::test_last_message_that_is_not_about_waiting_prints_waiting_false`), `missing: 2`, and exactly the two expected `missing` lines. tar also printed `Failed to set default locale` on stderr, which the scenario says to ignore. |
| The gate's suite command, as the instance lists it, passes in under three minutes | NEW | not run, as the spec says; the "One suite run" row shows the same command form stopping at 180 s | `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then `584 passed in 93.50s (0:01:33) \| under 180 s` |
| A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows | NEW | `park T-0001.1: EMPTY-OUTPUT from reviewer` (other three lines as expected) | `park T-0001.1: EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT `, `verifier: VERIFIED `, `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` |
| One empty reviewer run followed by a real one routes on the real one | REGRESSION | n/a | `park T-0001.1: SPEC-DEFECT from verifier`, `reviewer: EMPTY-OUTPUT APPROVE ` |
| An implementer that returns nothing twice parks as EMPTY-OUTPUT | REGRESSION | n/a | `park T-0001.2: EMPTY-OUTPUT from implementer`, `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` |
| An intake role's second empty output in a row parks as EMPTY-OUTPUT | REGRESSION | n/a | `start: triage`, `start: triage`, `park: EMPTY-OUTPUT from triage` |
| An intake role that ends waiting twice parks with the waiting reason, in the driver and the script | NEW | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage`, `drive EMPTY-OUTPUT from triage` | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage: ended its turn waiting on a background command`, `drive EMPTY-OUTPUT from triage: ended its turn waiting on a background command` |
| A build checker that ends waiting twice parks with the waiting reason, in the driver and the script | NEW | `planned script=4/4 drive=4/4 same`, `script EMPTY-OUTPUT from reviewer`, `drive EMPTY-OUTPUT from reviewer` | `planned script=4/4 drive=4/4 same`, `script EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, `drive EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command` |
| A role whose last message is not about waiting parks with the plain reason | REGRESSION | n/a | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage`, `drive EMPTY-OUTPUT from triage` |
| The design doc and build spec name the waiting park reason, and no prompt copy changes | NEW | `design=0 spec=0 cli=0 prompts=0` | `design=1 spec=1 cli=1 prompts=0` |
| The README names pytest-xdist and the waiting reason | NEW | `bullet=1 waiting=0 unfired=1 xdist=0` | `bullet=1 waiting=1 unfired=0 xdist=1` |
| The changelog records issue 106 as its last entry, without a numbering gap | NEW | `CONTIGUOUS`, `0`, `0` | `CONTIGUOUS`, `1`, `5` |
| The parallel-suite change adds no whitespace errors | REGRESSION | n/a | `exit=0` |

Every NEW command failed before the change as the spec's verification.md describes. The stand-in counts vary from run to run, as the spec says they do.

Gates on head `5e00a1f`, each run exactly as written:
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `584 passed in 105.98s (0:01:45)` and exited 0. The suite has 584 tests: 583 before, plus the new one.

The current-truth harness-code scenario "factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines" printed `891 3`: 891 lines, under 900, and all three definitions it looks for are still present.

## Tests added/changed

- Changed, as listed under Tests to change: `tests/factory/test_drive.py:57`. The expected reason is now `"EMPTY-OUTPUT from triage: ended its turn waiting on a background command"`, because its stand-in triage says "still waiting on my commands".
- Changed, as listed under Tests to change: `tests/factory/test_empty_output.py:63`. The expected object gains `"waiting": True`, because its text says "still running".
- Added: `test_empty_output.py::test_last_message_that_is_not_about_waiting_prints_waiting_false`, which Part D.4 asks for. It uses that file's `Store`. The spec places it in this existing file, not in a new one.
- `tests/factory/_fixtures.py` changed under Part C. It is a helper module, not a test file (spec Risk).

I watched the three tests fail before the code change: `3 failed, 1 passed`.

## Known gaps and uncertainties

- The time bounds hold on this 10-core machine: 93 to 106 s for one run, and 163 to 166 s for each of two runs at once. On a much slower machine the timing scenarios could fail with no defect in the change (spec Risk).
- Any checkout whose `.venv` lacks pytest-xdist now fails every suite command with `unrecognized arguments: -n` until it runs `uv sync --frozen`. Operator step 1 of the spec covers this for `~/dev/spec-factory`.
- The waiting match is a plain word match. Any last message that says "wait" for another reason also matches. Per the spec's Decisions this changes only the park reason's wording, never the route. `factory:` markers added: one, above `WAITING` in `factory/cli.py`. It names this limit, and replacing the match if a misleading waiting reason is ever seen as the upgrade trigger.
- `README.md` now describes the waiting reason in "What is built", though the reason itself has not yet fired on a real ticket. The page's "Maintaining this page" rule keeps such things under "Where this can go" until they have run. I followed the approved spec (Part E), which asks for the sentence there.
- `dev/build-harness.spec.md` line 276 (the `runRole` paragraph) still says a second EMPTY-OUTPUT "parks `EMPTY-OUTPUT from <role>`", with no mention of the waiting form. Part E lists only lines 206 and 306, so I left it. That paragraph points to item I.5 (line 306), which now gives both forms.
- I did not touch the README's "Related work and history" paragraph (issue numbers, store counts, runtime commit). The operator's post-merge `dev:` commits have been updating it.

## Out-of-scope observations

- 13 suite tests fail when `TMPDIR` points inside the spec-factory checkout. My first gate run had `TMPDIR` set to this run's scratch directory and printed `13 failed, 571 passed`. The failures were in `test_instance.py`, `test_cost_once.py`, `test_stats.py`, `test_environment_sync.py` and `test_spec_drift.py`. Each test expected to be outside any git repository or factory instance, but `tmp_path` was inside one. With the system `TMPDIR`, all 584 tests pass. I did not re-run those tests on the base commit to confirm that they fail there too. The cause is where the temporary directory sits, not this change.

## Responses to findings (round 2+)

n/a (round 1)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every scenario printed its expected result, both gates pass on the head, and the timing bounds held with margin on this machine.
ESCALATIONS: none

## Diff `88c65e147495debccaef62986a15df1ee54b59f4...5e00a1f5261b2576ae6243b46ac8895f71042ff9`

diff --git a/README.md b/README.md
index caf527b..708b851 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-12. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-13. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -573,7 +573,9 @@ uv sync --frozen --project ~/dev/spec-factory-harness
 
 `uv sync` gives the harness its interpreter and dependencies (`pyproject.toml`, `uv.lock`);
 `bin/factory` runs the `factory` package with that environment. The runtime is what targets run;
-the dev checkout is where you merge.
+the dev checkout is where you merge. The suite runs across every CPU core with pytest-xdist, set
+once in `pyproject.toml`, so that one run stays well under the 10-minute limit of a single agent
+tool call.
 
 ### Adopting the factory in a repo
 
@@ -998,11 +1000,13 @@ the column can undercount.
   supersedes. It is tested, and has not yet fired on a real ticket.
 - **Empty output.** A role run that ends without writing its output file is run once more on the
   same inputs, and the harness keeps the agent's last message with the run. A second run in a row
-  that ends the same way parks the ticket. The harness enforces no time or token budget and cannot
+  that ends the same way parks the ticket. When either run's last message says it was still waiting
+  on a command it started, the park reason adds `ended its turn waiting on a background command`,
+  because a plain re-run is likely to end the same way. The harness enforces no time or token budget and cannot
   tell why a run stopped, so it never labels such a run a budget kill. The code reviewer judges the
   diff and leaves the test suite and the gate commands to the verifier. Every role is told to wait
-  for the commands it starts before it ends its turn. It is tested, and has not yet fired on a real
-  ticket.
+  for the commands it starts before it ends its turn. It has fired on a real ticket: both runs of
+  one verifier ended their turns waiting for the test suite.
 - **Protected paths at merge.** The merge gate refuses a change to a protected path that the
   approved spec does not declare on the `Protected paths:` line of its Risk section, and names
   each such path. The human approves that line at the spec gate, so a declared path merges with
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 7e0bb54..f26c6cf 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -203,7 +203,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 - `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model:` the instance's `models[R]`, which `--model M` only cross-checks; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when `--model M` names a model other than the instance's `models[R]` (`model <M> refused for <R>: the instance names <model>`; checked before the ticket is read), or when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
 - `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` and the pinned spec version it used as `spec_version:` in `meta.yaml` (a run keeps that version even if the spec is re-pinned while it is in flight, K). The file opens with the repo's role-context block (doc §Harness), ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`). The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
 - `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H). A missing or blank `output.md` with no override is `EMPTY-OUTPUT` (error `empty output`, logged `run.finished`); `--status-override KILLED` still records `KILLED` and logs `run.killed`.
-- `factory run last-message RUN --text=T` → on a run whose `meta.yaml` status is `EMPTY-OUTPUT`, writes T plus one newline to `runs/<RUN>/last-message.md` and prints its path; on any other run, exit 2 and nothing written (I.5).
+- `factory run last-message RUN --text=T` → on a run whose `meta.yaml` status is `EMPTY-OUTPUT`, writes T plus one newline to `runs/<RUN>/last-message.md` and prints its path and `waiting`: whether T says the run is still waiting on a command (ignoring case, the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`); on any other run, exit 2 and nothing written (I.5).
 - `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT); `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`; `factory plan whole-spec PARENT` → when the approved spec needs one sub-ticket (the parent has no sub-ticket and no earlier planner run, its latest spec-writer run did not end `NEEDS-SPLIT`, and the approved spec has no `##` or `###` heading, other than a `### Requirement:` line, naming seams), creates `<PARENT>.1` from the whole spec in `ready-for-implementer`, its text naming every scenario, writes the same text to `plans/<PARENT>.md` and, with a spec store, `openspec/changes/<PARENT>/tasks.md`, logs `plan.skipped`, and prints `"planner": "skipped"`; otherwise prints `"planner": "needed"` with the reason and writes nothing (exit 2 when PARENT is not `ready-for-planner`, has a run in flight, has no approved spec, or has no change folder under an active spec store).
 - **Operator commands** (`approve-spec`, `approve-pr`, `approve-guardrail`, `request-changes`, `resolve`, `queue apply`, `merge`, `ticket new`, `results record`) refuse with exit 2, stderr `set FACTORY_KEY`, nothing written or logged, when `FACTORY_KEY` is unset (item 78); reads (`ticket show`, `results show`, `queue`, `log tail`) never need it. `gate-run` always uses the harness key.
 
@@ -303,7 +303,7 @@ Resumption after a human decision: the `/factory` skill re-runs `build.js` for t
 3. Mutating roles get `isolation: 'worktree'` (E7), which the Workflow tool creates and removes; the implementer's `git push` uses the implementer key via `GIT_SSH_COMMAND` set in its agent definition's `env:` (not verified: whether agent-definition frontmatter supports `env:`; fallback: a `factory git-push ticket/<ID>` wrapper the implementer is allowed to run, which supplies the key). Checkers run read+shell in a checkout the clerk made; they have no key, so a push fails at authentication.
    - Environment sync: when the instance sets `environment_sync`, `run start` runs that command in each build checkout (the implementer's worktree at every dispatch, and each checker's checkout) through the running-code wrapper, after the environment files are copied and before the role starts. A failure refuses the run, with the command and its output in `runs/<id>/environment-sync.log`.
 4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6). Under `factory drive`, the tool restriction is the role process's `--tools` and `--allowedTools` instead (R6).
-5. Empty output (doc §Routing rules): no time or token budget is enforced, and `agent()` reports no reason a run stopped, so no empty output is a budget kill. A run that ends without its output file, or with a blank one, is `EMPTY-OUTPUT` in `run finish`, whether `agent()` returned text, blank text or `null` (a user skip or a terminal error). When the returned text is non-blank, the script keeps its last 4000 characters with `run last-message`. The same role is re-dispatched once, on the same inputs and in the same round; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs as outputs and records no result row for it, so `resolve --redispatch` re-runs only that role. A thrown `agent()` stays `KILLED`, parked `agent call failed: <role>: <error>`, with no re-dispatch. Until a run returns, a hung agent blocks `parallel()` and every sibling in that join; the user skipping the agent is the one manual stop (E7; Open question 4).
+5. Empty output (doc §Routing rules): no time or token budget is enforced, and `agent()` reports no reason a run stopped, so no empty output is a budget kill. A run that ends without its output file, or with a blank one, is `EMPTY-OUTPUT` in `run finish`, whether `agent()` returned text, blank text or `null` (a user skip or a terminal error). When the returned text is non-blank, the script keeps its last 4000 characters with `run last-message`. The same role is re-dispatched once, on the same inputs and in the same round; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>`, or `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run's `run last-message` printed `waiting` true, with both runs as outputs and records no result row for it, so `resolve --redispatch` re-runs only that role. A thrown `agent()` stays `KILLED`, parked `agent call failed: <role>: <error>`, with no re-dispatch. Until a run returns, a hung agent blocks `parallel()` and every sibling in that join; the user skipping the agent is the one manual stop (E7; Open question 4).
 6. After each run: `meta.yaml` complete, the checker worktree removed by the clerk (`factory run cleanup RUN`). The run's `runs/<run_id>/scratch/` stays until its ticket's next state change other than `parked`, which removes it (`store.save_ticket`).
 
 ### J. Secrets (piece 12)
diff --git a/docs/changelog.md b/docs/changelog.md
index 124f7bc..59e1061 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -72,5 +72,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 68. After issue #85 (2026-10-10), where the spec drift check parked two sub-tickets of the driver ticket T-0040 for their own siblings' merges, and the second park had no command to clear it: the test rule walked every first-parent commit on the integration branch since the spec was written, so the `--no-ff` merge of T-0040.1, which changed `factory/cli.py` and added `tests/factory/test_drive.py`, parked T-0040.2, and the merges of T-0040.1 and T-0040.2 parked T-0040.3. The Workflow script recorded T-0040.3's drift refusal as `harness-bug: run start implementer: …`, which `resolve --ruling` refused, so the operator edited the stored park reason by hand before the ruling. The test rule now skips a first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans; every other commit and merge still counts. `resolve --ruling F` now also accepts a `harness-bug: run start implementer:` park from `ready-for-implementer`, which means the harness failed to start an implementer run: F becomes the next ruling and the sub-ticket returns to its implementer at the same round, as for BLOCKED, and the ruling on file keeps the drift check from running again. Any other harness-bug park, such as a failed `run compose` or a checker's failed run start, is still refused, and the refusal text names the new case. Rejected: skipping only the current plan's siblings, since an earlier plan's merged sub-ticket is also the parent's own work; skipping merge commits in general; widening `--redispatch`, which re-runs the checkers and would meet the same drift refusal with no ruling on file; accepting every harness-bug park from `ready-for-implementer`, since a failed `run compose` leaves its run in flight.
 69. After issue #86 (2026-10-11), where an operator driving two tickets of the Nanobot target at once could not restart one drive while the other had a run in flight: `factory drive` met the live-store fence when it started, before it set its marker, so a re-run of the T-0036 drive was refused, naming an implementer run of T-0035. Typing the marker in front of the command got past the fence, but the fence's in-flight rule was also the only thing that stopped a second drive of the same ticket, and a marked second drive of a ticket with a run in flight parked that ticket. `factory drive` is now exempt from the fence's in-flight rule: it starts unmarked beside other tickets' runs. It keeps the location rule, so it is refused from inside the own store's `runs/` or `worktrees/`, marked or not. It keeps the harness lock, and given `--accept-harness` it is fenced in full, because an acceptance rewrites the lock. In place of the in-flight rule it has a same-ticket guard, checked before it sets its marker or writes its status file, whether or not the caller is marked and on any store, a throwaway store included. It refuses with exit 2, writing nothing, while the ticket or one of its sub-tickets has a run in flight, naming the runs. It also refuses while `drive/<ticket>.yaml` has no `ended` and its `pid` is live, meaning signal 0 reaches it or is refused for permission, naming the pid and the file. A dead, missing or non-integer pid does not block, and neither refusal names the marker. README's driver how-to no longer tells the operator to type the marker. This overturns T-0040's decision of 2026-10-10 (entry 67) that the driver is a write like any other, and its rejection of exempting it; the operator made the exemption standing for every later runner command. Rejected: applying the guard only on an own store, as the fence is, since two drivers damage a ticket's records on any store; checking with a process query that a live pid is a `factory drive` process, a platform-dependent query for the rare pid reused after a SIGKILLed driver, so the refusal names the pid and README says to delete the status file when it is not a driver; and a lock against two drives of the same ticket started in the same instant, since the reported case was two different tickets and the window is a few store reads long.
 70. After issue #70 (2026-10-11), where the operator could not tell which checks pay for themselves: the figures behind a model choice, such as the code reviewer changing an outcome in 4 of 94 runs, came from a hand-written count over both stores, and the one token report, `factory/cost.py`, counted most model calls about twice, because Claude Code writes one transcript record per streamed block of a reply and each record carries the whole call's usage (issue #61). `factory/cost.py` now counts each message id once, from its last record, and its `calls` column counts message ids. Measured over every transcript matched to a run when the change was specified, the old count was 1.89 times the new one for the Nanobot store and 1.94 times for this one; the new count of a driver run's transcript equals that run's cost record. A new command, `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...` (`factory/stats.py`), reads one or more stores and prints four tables: runs and verdicts by role and model, with kills, changed outcomes, BLOCKING findings and the implementer's gate failures fixed before hand-off; parks by normalised reason, taking a park's corrected reason when the correction is dated before `--until`, with the spec gate, resolution and merge decisions; each spec defect a verifier or implementer caught, against the runs that wrote and critiqued that spec; and each role's wall time and tokens, from the run's cost record, else its transcript under `--transcripts`, else none. `--until` makes a past figure repeatable on a growing store. `stats` writes nothing and must read a live store during a run and from a checkout the instance has not accepted, so, like `paths`, it skips the instance lookup, the live-store fence and the harness lock and ignores `--accept-harness`; the fence's read-only list gains it. Its count corrects one figure in `docs/principles.md` §4: the reviewer's BLOCKING findings are 3, one in each REQUEST-CHANGES run, not 1. Rejected: JSON output, which no consumer needs yet; adding `stats` only to the fence's read-only list, since the lock would still refuse it outside the accepted runtime; searching `~/.claude/projects` by default, which ties the command to one machine's layout and costs about 12 seconds a call; counting every mention of BLOCKING, which counts "No BLOCKING findings", or the round-2 restatements marked RESOLVED; matching a transcript only by the store's current path, which loses every run from before an unrecorded store move; ignoring park corrections, which reports the error a human fixed, and applying corrections dated after `--until`, which moves a past figure; and reading gate failures from the implementer's output, which states only final results. Figures quoted from `factory/cost.py` before this change, such as those in entries 58 and 67, stay as history and are not restated.
+71. After issue #106 (2026-10-12), where both verifier runs of one sub-ticket started the harness suite in the background, ended their turns to wait for it and so wrote no output: one run of the suite took six to ten minutes, against the 10-minute limit of a single agent tool call. The ticket parked as `EMPTY-OUTPUT from verifier`, a reason that did not say why. The harness suite now runs across every CPU core with pytest-xdist, a new dev dependency, switched on once in `pyproject.toml` (`addopts = "-n auto"`), so the gate command and every scenario that runs the suite use it with no change to their text; one run measured 66.80 to 146.81 seconds when the change was specified, against 385.56 seconds one test at a time. A new test must not depend on test order, or share a file, port, environment variable or other process-wide state with another test outside its own `tmp_path`. Adding pytest-xdist is a deliberate exception to the 2026-10-04 decision not to add to what the gate needs. The suite's two stand-in `claude` programs now hold a file lock around their per-role call counter, so a copy of one role started beside another no longer reads the counter while the other rewrites it, which had now and then crashed a checker run under load. `factory run last-message` also prints `waiting`: true when the kept message contains, ignoring case, the word `wait` or `waiting`, or `still running`, `still in progress` or `in the background`. The driver and both workflow scripts park a second EMPTY-OUTPUT in a row as `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command` when either run was waiting, and as `EMPTY-OUTPUT from <role>` otherwise; the route itself is unchanged, and no role prompt changes. Rejected: calling the CLI in-process in the suite, which was faster but needs a module-table swap around every call and stops most CLI calls from crossing a real process boundary; adding `-n auto` to the gate command, which leaves every scenario that runs the suite running one test at a time; and deciding waiting in each caller or in a separate command, rather than once in `run last-message`.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index f04e077..6efb79e 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -103,7 +103,7 @@ Rules the table relies on:
 - The PR loop routes only after CI and both checker results for the current head are recorded. One implementer run then receives all three outputs. Never launch a second implementer run on a branch that already has one in flight.
 - The dispatcher reads a role's trailer by its labels, not by line position. The last `STATUS:` line wins; CONFIDENCE is the next line labelled `CONFIDENCE:` after it, and ESCALATIONS the next line labelled `ESCALATIONS:` after that. Lines between labelled lines are continuation (a wrapped reason, a remark), so a verbose but well-formed verdict routes on its STATUS. A trailer with no CONFIDENCE or no ESCALATIONS line after its last STATUS is a parse failure, which routes as a STATUS not in this table.
 - A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a second EMPTY-OUTPUT in a row, a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
-- A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs.
+- A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs. When either run's last message says it is still waiting on a command it started, the park reason adds `ended its turn waiting on a background command`, because a plain re-dispatch is likely to end the same way.
 - When a human resolves a parked ticket:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
   - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes. A sub-ticket parked `harness-bug: run start implementer:` from `ready-for-implementer`, because the harness failed to start its implementer run, also returns to its implementer with the ruling, same round. A ruling on any other harness-bug park is refused.
diff --git a/factory/cli.py b/factory/cli.py
index 3085c25..1b88875 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -295,6 +295,12 @@ def _sync_environment(cfg: dict, sync: str | None, meta: dict, repo: Path, wt: P
     raise Refused(f"environment_sync failed (exit {cp.returncode}) in {wt}; its command and output are in {log}")
 
 
+# A kept last message that says the run ended its turn still waiting on a command it started.
+# factory: a word match, not a reading of intent: any message that mentions waiting matches. It only
+# adds a phrase to a park a human reads; replace it if a misleading waiting reason is seen.
+WAITING = re.compile(r"\bwait(?:ing)?\b|\bstill (?:running|in progress)\b|\bin the background\b", re.I)
+
+
 def run_last_message(a, root, cfg):
     """Keep the agent's last message with a run that ended EMPTY-OUTPUT, so a human can see why."""
     d = _run_dir(root, a.run)
@@ -302,7 +308,8 @@ def run_last_message(a, root, cfg):
     if st != "EMPTY-OUTPUT":
         raise Refused(f"{a.run} is {st or 'not finished'}, not EMPTY-OUTPUT: no last message to keep")
     store.write_text(d / "last-message.md", a.text + "\n")
-    out({"ok": True, "run_id": a.run, "last_message": _rel(root, d / "last-message.md")})
+    out({"ok": True, "run_id": a.run, "last_message": _rel(root, d / "last-message.md"),
+         "waiting": bool(WAITING.search(a.text))})
 
 
 def run_cleanup(a, root, cfg):
diff --git a/factory/drive.py b/factory/drive.py
index 0b2dee2..9d020f5 100644
--- a/factory/drive.py
+++ b/factory/drive.py
@@ -48,6 +48,9 @@ ALLOWED = "Read,Grep,Glob,Bash,WebFetch,WebSearch"
 PROMPT = ("Your entire input is the file {run}/input.md; read it first and follow it. "
           "Write your complete output to {run}/output.md and return the same text.")
 KILL_AFTER_S = 10
+# Added to an EMPTY-OUTPUT park when either run's last message says it was still waiting on a
+# command: a plain re-dispatch would likely end the same way.
+WAITING_REASON = ": ended its turn waiting on a background command"
 
 
 def call(*argv: str) -> dict:
@@ -179,7 +182,8 @@ class Driver:
         second = await self.run_once(role, ticket)
         if not second or second["status"] != "EMPTY-OUTPUT":
             return second
-        self.park(ticket, f"EMPTY-OUTPUT from {role}", [first["runId"], second["runId"]])
+        waiting = WAITING_REASON if first["waiting"] or second["waiting"] else ""
+        self.park(ticket, f"EMPTY-OUTPUT from {role}{waiting}", [first["runId"], second["runId"]])
         return None
 
     async def run_once(self, role: str, ticket: str) -> dict | None:
@@ -238,11 +242,13 @@ class Driver:
             self.step(f"parked: {fin['parked']}", ticket)
             return None
         said = reply.get("result").strip() if isinstance(reply.get("result"), str) else ""
+        waiting = False
         if fin["status"] == "EMPTY-OUTPUT" and said:
-            call("run", "last-message", rid, "--text=" + said[-4000:])
+            waiting = call("run", "last-message", rid, "--text=" + said[-4000:]).get("waiting") is True
         esc = fin.get("escalations") or []
         self.step(f"{role} {rid}: {fin['status']}" + (f" (+{len(esc)} escalations)" if esc else ""), ticket)
-        return {"runId": rid, "status": fin["status"], "escalations": esc, "outputPath": os.path.join(run, "output.md")}
+        return {"runId": rid, "status": fin["status"], "escalations": esc, "outputPath": os.path.join(run, "output.md"),
+                "waiting": waiting}
 
     # ----- intake: factory/workflows/intake.js from `// --- start` ---------------------------
 
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index b76619c..2f7d097 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -63,6 +63,10 @@ async function park(ticket, reason, outputs, phase) {
   log(`${ticket} parked: ${reason}`)
 }
 
+// Added to an EMPTY-OUTPUT park when either run's last message says it was still waiting on a
+// command: a plain re-dispatch would likely end the same way.
+const WAITING_REASON = ': ended its turn waiting on a background command'
+
 // An EMPTY-OUTPUT run is re-dispatched once, same role, same inputs; a second in a row parks the ticket
 // with both runs. The agent call reports no reason a run stopped, so neither is a budget kill.
 async function runRole(role, ticket, phase) {
@@ -71,7 +75,8 @@ async function runRole(role, ticket, phase) {
   log(`${role} ${first.runId} (${ticket}): EMPTY-OUTPUT; re-dispatching ${role} once`)
   const second = await runOnce(role, ticket, phase)
   if (!second || second.status !== 'EMPTY-OUTPUT') return second
-  await park(ticket, `EMPTY-OUTPUT from ${role}`, [first.runId, second.runId], phase)
+  const waiting = first.waiting || second.waiting ? WAITING_REASON : ''
+  await park(ticket, `EMPTY-OUTPUT from ${role}${waiting}`, [first.runId, second.runId], phase)
   return null
 }
 
@@ -127,11 +132,13 @@ async function runOnce(role, ticket, phase) {
   // An EMPTY-OUTPUT run keeps the agent's last message, so a human can see why it stopped. A failure
   // here never parks and never changes the route.
   const said = typeof out === 'string' ? out.trim() : ''
+  let waiting = false
   if (fin.status === 'EMPTY-OUTPUT' && said) {
-    await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+    const kept = await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+    waiting = kept.waiting === true
   }
   log(`${role} ${runId} (${ticket}): ${fin.status}`)
-  return { runId, status: fin.status, outputPath }
+  return { runId, status: fin.status, outputPath, waiting }
 }
 
 async function transition(ticket, to, roundOp, phase) {
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index cb10d46..87635f6 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -72,6 +72,10 @@ async function park(reason, outputs, phase) {
   log(`${TICKET} parked: ${reason}`)
 }
 
+// Added to an EMPTY-OUTPUT park when either run's last message says it was still waiting on a
+// command: a plain re-dispatch would likely end the same way.
+const WAITING_REASON = ': ended its turn waiting on a background command'
+
 // An EMPTY-OUTPUT run is re-dispatched once, same role, same inputs; a second in a row parks the ticket
 // with both runs. The agent call reports no reason a run stopped, so neither is a budget kill.
 async function runRole(role, phase) {
@@ -80,7 +84,8 @@ async function runRole(role, phase) {
   log(`${role} ${first.runId}: EMPTY-OUTPUT; re-dispatching ${role} once`)
   const second = await runOnce(role, phase)
   if (!second || second.status !== 'EMPTY-OUTPUT') return second
-  await park(`EMPTY-OUTPUT from ${role}`, [first.runId, second.runId], phase)
+  const waiting = first.waiting || second.waiting ? WAITING_REASON : ''
+  await park(`EMPTY-OUTPUT from ${role}${waiting}`, [first.runId, second.runId], phase)
   return null
 }
 
@@ -123,11 +128,13 @@ async function runOnce(role, phase) {
   // An EMPTY-OUTPUT run keeps the agent's last message, so a human can see why it stopped. A failure
   // here never parks and never changes the route.
   const said = typeof out === 'string' ? out.trim() : ''
+  let waiting = false
   if (fin.status === 'EMPTY-OUTPUT' && said) {
-    await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+    const kept = await clerk(`${BIN} run last-message ${runId} '--text=${said.slice(-4000).replace(/'/g, "'\\''")}'`, phase, `run last-message ${role}`)
+    waiting = kept.waiting === true
   }
   log(`${role} ${runId}: ${fin.status}${fin.escalations && fin.escalations.length ? ` (+${fin.escalations.length} escalations)` : ''}`)
-  return { runId, status: fin.status, escalations: fin.escalations || [] }
+  return { runId, status: fin.status, escalations: fin.escalations || [], waiting }
 }
 
 async function transition(to, roundOp, phase) {
diff --git a/pyproject.toml b/pyproject.toml
index 67fd6de..eed0fa1 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -5,7 +5,14 @@ requires-python = ">=3.11"
 dependencies = ["pyyaml>=6"]
 
 [dependency-groups]
-dev = ["pytest>=8"]
+dev = [
+    "pytest>=8",
+    "pytest-xdist>=3.8.0",
+]
 
 [tool.uv]
 package = false
+
+[tool.pytest.ini_options]
+# The suite runs across every CPU core so that one run stays well under the 10-minute limit of a single agent tool call.
+addopts = "-n auto"
diff --git a/tests/factory/_fixtures.py b/tests/factory/_fixtures.py
index bc169fc..fd86ddf 100644
--- a/tests/factory/_fixtures.py
+++ b/tests/factory/_fixtures.py
@@ -220,15 +220,19 @@ def started(cp: subprocess.CompletedProcess) -> None:
 FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
 
 STANDIN = '''#!{python}
-import json, os, pathlib, sys, time
+import fcntl, json, os, pathlib, sys, time
 cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
 with log.open("a") as f:
     f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
                         "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
 role = cwd.name.split("-", 2)[2]
 plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
-nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
-nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
+nf = log.with_name(log.name + ".n-" + role)
+with open(log.with_name(log.name + ".lock"), "w") as lk:  # copies of one role may start at once
+    fcntl.flock(lk, fcntl.LOCK_EX)
+    n = int(nf.read_text()) + 1 if nf.exists() else 1
+    nf.write_text(str(n))
+p = plays[min(n, len(plays)) - 1]
 time.sleep(p.get("sleep", 0))
 text, err = p.get("say", ""), "fail" in p
 if "write" in p:
@@ -286,7 +290,7 @@ class Store(CliStore):
 # ----- the build store of `factory drive` (test_drive_build.py) -----------------------------------
 
 BUILD_STANDIN = '''#!{python}
-import json, os, pathlib, re, sys, time
+import fcntl, json, os, pathlib, re, sys, time
 t0 = time.time()
 cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
 with log.open("a") as f:
@@ -294,8 +298,12 @@ with log.open("a") as f:
                         "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
 role = cwd.name.split("-", 2)[2]
 plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
-nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
-nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
+nf = log.with_name(log.name + ".n-" + role)
+with open(log.with_name(log.name + ".lock"), "w") as lk:  # copies of one role may start at once
+    fcntl.flock(lk, fcntl.LOCK_EX)
+    n = int(nf.read_text()) + 1 if nf.exists() else 1
+    nf.write_text(str(n))
+p = plays[min(n, len(plays)) - 1]
 time.sleep(p.get("sleep", 0))
 text, err = p.get("say", ""), "fail" in p
 if "write" in p:
diff --git a/tests/factory/test_drive.py b/tests/factory/test_drive.py
index fe3506d..4de48ad 100644
--- a/tests/factory/test_drive.py
+++ b/tests/factory/test_drive.py
@@ -54,7 +54,7 @@ def test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message(tmp_pat
     assert cp.returncode == 0, cp.stderr
     assert res["state"] == "parked"
     parked = s.ticket()["parked"]
-    assert parked["reason"] == "EMPTY-OUTPUT from triage"
+    assert parked["reason"] == "EMPTY-OUTPUT from triage: ended its turn waiting on a background command"
     assert [m["status"] for m in s.runs()] == ["EMPTY-OUTPUT", "EMPTY-OUTPUT"]
     for m in s.runs():
         kept = (s.root / "runs" / m["run_id"] / "last-message.md").read_text()
diff --git a/tests/factory/test_empty_output.py b/tests/factory/test_empty_output.py
index d1e049b..b208ff7 100644
--- a/tests/factory/test_empty_output.py
+++ b/tests/factory/test_empty_output.py
@@ -60,10 +60,18 @@ def test_last_message_is_kept_for_an_empty_output_run(tmp_path):
     s.ok("run", "finish", s.rid)
     text = "The suite is still running; I'll write the review when it ends.\nsecond line"
     res = s.ok("run", "last-message", s.rid, f"--text={text}")
-    assert res == {"ok": True, "run_id": s.rid, "last_message": f"runs/{s.rid}/last-message.md"}
+    assert res == {"ok": True, "run_id": s.rid, "last_message": f"runs/{s.rid}/last-message.md",
+                   "waiting": True}
     assert (s.run_dir / "last-message.md").read_text() == text + "\n"
 
 
+def test_last_message_that_is_not_about_waiting_prints_waiting_false(tmp_path):
+    s = Store(tmp_path)
+    s.ok("run", "finish", s.rid)
+    res = s.ok("run", "last-message", s.rid, "--text=I could not finish: the input file was missing.")
+    assert res["waiting"] is False
+
+
 def test_last_message_is_refused_for_a_run_that_wrote_its_output(tmp_path):
     s = Store(tmp_path)
     (s.run_dir / "output.md").write_text("Type: bug\nTitle: x\n\nSTATUS: ACCEPT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
diff --git a/uv.lock b/uv.lock
index 6e50f2e..9efadc1 100644
--- a/uv.lock
+++ b/uv.lock
@@ -11,6 +11,15 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/d1/d6/3965ed04c63042e047cb6a3e6ed1a63a35087b6a609aa3a15ed8ac56c221/colorama-0.4.6-py2.py3-none-any.whl", hash = "sha256:4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6", size = 25335, upload-time = "2022-10-25T02:36:20.889Z" },
 ]
 
+[[package]]
+name = "execnet"
+version = "2.1.2"
+source = { registry = "https://pypi.org/simple" }
+sdist = { url = "https://files.pythonhosted.org/packages/bf/89/780e11f9588d9e7128a3f87788354c7946a9cbb1401ad38a48c4db9a4f07/execnet-2.1.2.tar.gz", hash = "sha256:63d83bfdd9a23e35b9c6a3261412324f964c2ec8dcd8d3c6916ee9373e0befcd", size = 166622, upload-time = "2025-11-12T09:56:37.75Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/ab/84/02fc1827e8cdded4aa65baef11296a9bbe595c474f0d6d758af082d849fd/execnet-2.1.2-py3-none-any.whl", hash = "sha256:67fba928dd5a544b783f6056f449e5e3931a5c378b128bc18501f7ea79e296ec", size = 40708, upload-time = "2025-11-12T09:56:36.333Z" },
+]
+
 [[package]]
 name = "iniconfig"
 version = "2.3.0"
@@ -63,6 +72,19 @@ wheels = [
     { url = "https://files.pythonhosted.org/packages/24/25/1de2678b631f5a49215c6c96fff41ba892b0a34df68d6d80292b1b48aa7f/pytest-9.1.1-py3-none-any.whl", hash = "sha256:37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c", size = 386536, upload-time = "2026-06-19T10:58:31.347Z" },
 ]
 
+[[package]]
+name = "pytest-xdist"
+version = "3.8.0"
+source = { registry = "https://pypi.org/simple" }
+dependencies = [
+    { name = "execnet" },
+    { name = "pytest" },
+]
+sdist = { url = "https://files.pythonhosted.org/packages/78/b4/439b179d1ff526791eb921115fca8e44e596a13efeda518b9d845a619450/pytest_xdist-3.8.0.tar.gz", hash = "sha256:7e578125ec9bc6050861aa93f2d59f1d8d085595d6551c2c90b6f4fad8d3a9f1", size = 88069, upload-time = "2025-07-01T13:30:59.346Z" }
+wheels = [
+    { url = "https://files.pythonhosted.org/packages/ca/31/d4e37e9e550c2b92a9cbc2e4d0b7420a27224968580b5a447f420847c975/pytest_xdist-3.8.0-py3-none-any.whl", hash = "sha256:202ca578cfeb7370784a8c33d6d05bc6e13b4f25b5053c30a152269fd10f0b88", size = 46396, upload-time = "2025-07-01T13:30:56.632Z" },
+]
+
 [[package]]
 name = "pyyaml"
 version = "6.0.3"
@@ -129,10 +151,14 @@ dependencies = [
 [package.dev-dependencies]
 dev = [
     { name = "pytest" },
+    { name = "pytest-xdist" },
 ]
 
 [package.metadata]
 requires-dist = [{ name = "pyyaml", specifier = ">=6" }]
 
 [package.metadata.requires-dev]
-dev = [{ name = "pytest", specifier = ">=8" }]
+dev = [
+    { name = "pytest", specifier = ">=8" },
+    { name = "pytest-xdist", specifier = ">=3.8.0" },
+]
