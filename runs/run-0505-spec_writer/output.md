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

## Evidence

All measurements are on this machine (10 cores), with Python 3.12.13, in scratch clones of `main` at `88c65e1`. Each figure comes from pytest's own summary line, `583 passed in N s`. Other sessions were loading the machine at the time; the load average is given where it was recorded.

| Suite run | Load | Time |
|---|---|---|
| Today, one test at a time | 9.7 | 385.56 s (the request measured 443.67 s on a quiet machine) |
| pytest-xdist `-n auto`, nothing else changed | 7.6 / 2.1 | 97.12 s / 146.81 s (the second on a Python 3.14 environment) |
| `-n auto` set in `pyproject.toml`, as this spec proposes | various | 95.21 s, 95.15 s, 89.78 s (gate command form), 93.99 s, 66.80 s (load 42.8) |
| Two `-n auto` runs at once | 4.4 / 6.9 | 167.57 s and 169.66 s; 162.35 s and 162.48 s with the Part D prototype |
| CLI called in-process, one test at a time (prototype) | 5.2 / 10.9 | 113.45 s (first prototype, 1 failure, see below), 116.86 s (second prototype, 583 passed) |
| CLI in-process plus `-n auto` (prototype) | 3.3 / 8.6 | 30.82 s (first prototype, 1 failure), 26.84 s (second prototype, 583 passed) |

What the table shows: running in parallel alone brings one run from about 6.5 minutes to about 1.5 minutes. Two runs at once still finish in under 3 minutes. The in-process route alone is no faster than the parallel run. The two together are fastest, but see Decisions for why that route is not taken.

Where a test's time goes. A counting wrapper around the CLI entry points in a scratch clone recorded 5,581 CLI process starts in one suite run: 5,392 through `bin/factory` and 189 through the test-only launcher `tests/factory/clean_harness_cli.py`. A `bin/factory` call that stops after parsing its arguments costs 0.086 s. Starting Python alone costs 0.015 s, and starting it and importing `factory.cli` costs 0.071 s. So most of a call's cost is starting a process and importing the CLI. The CLI helpers in `tests/factory/_cli.py:23-39` (`cli`, `run`, `run_env`) and the fixture classes in `tests/factory/_fixtures.py:264-266` and `:483-488` each call `subprocess.run` on the CLI.

Why the in-process route needs more than a helper change. The test directory `tests/factory/` is itself a Python package named `factory`, and it shadows the harness package of the same name inside the pytest process. A first in-process prototype failed with 423 errors of `ImportError: cannot import name 'cli' from 'factory' (.../tests/factory/__init__.py)`. Harness functions also import `factory` modules lazily at call time (`factory/cli.py:395`, `:600`; `factory/compose.py:96`, `:105`; `factory/specstore.py:271`; `factory/instance.py:160`; `factory/store.py:21`). So the prototype that worked swaps the harness modules in and out of `sys.modules` around every call. A second prototype instead added `tests/__init__.py`, which renames the test package. That one wrote `tests/__pycache__/__init__.cpython-312.pyc` into the checkout: two paths changed. Current truth is the factory store's record of what the harness does today, kept as requirements grouped by capability. That prototype breaks the harness-suite capability's requirement there, "A suite run writes nothing into the checkout". The first prototype also failed `test_shepherd.py::test_two_merges_at_once_are_serialised_and_leave_the_checkout_clean`, which runs two CLI calls on two threads. The second, which falls back to a subprocess for a call off the main thread, passed it.

The parallel run is safe for the current suite. All 583 tests passed in each of the 14 full `-n auto` runs made for this spec, including every one in the table. `--collect-only` lists the same 583 test ids with `addopts = "-n auto"` as without it: `cmp` of the two sorted lists printed nothing. The current-truth harness-suite scenarios "A suite run in a fresh clone passes and adds nothing to the checkout" and "The harness suite passes with an uncommitted harness edit" printed `583 passed in 95.21s`, then `paths changed: 0`, and `583 passed in 95.15s`, on the `addopts` prototype. With pytest-xdist added by `uv add --dev pytest-xdist`, `uv.lock` gains two packages, `execnet` 2.1.2 and `pytest-xdist` 3.8.0, and nothing else in it changes.

The flaky test and its cause. Today `tests/factory/test_drive_build.py:123` (`test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`) runs two sub-tickets' checkers through the driver. The driver is `factory drive`, the command that runs each role as an agent process. Its stand-in agents follow plays, the scripted replies the test sets for each role. Its plays give every reviewer and verifier `"sleep": 2`, a two-second pause before the reply. In 40 copies of that test run at once, one failed with `'T-0001.2 "Two": verifier run-0004-verifier: KILLED'` among its step lines. The driver records a run as KILLED when the agent process exits non-zero or prints no JSON reply (`factory/drive.py:220-228`). The stand-ins count calls per role with an unlocked read, then a truncating write, of a shared file (`tests/factory/_fixtures.py:230-231` for the intake stand-in, `:297-298` for the build stand-in). Starting two copies of that read-increment-write at once, 200 times, raised `ValueError: invalid literal for int() with base 10: ''` in 39 rounds. The check script in this spec starts four copies of each real stand-in at once, 200 times. On `main` it printed `STANDIN: 200 rounds, 23 with a copy that did not reply` and `BUILD_STANDIN: 200 rounds, 21 ...`. With a file lock around the counter it printed `0` for both. A second run on `main`, made for this revision with the counter's final value added, printed `STANDIN: 200 rounds, 13 with a copy that did not reply, counter 769` and `BUILD_STANDIN: 200 rounds, 21 with a copy that did not reply, counter 763`. Four copies times 200 rounds should count 800, so 31 and 37 calls were lost to the race. The same script on a locked prototype printed `0` and `counter 800` for both. The request's own account, that "its 2-second sleeps decide whether a checker gets killed", matches the symptom. The kill comes from the counter race, not from the sleeps.

The other load effect was not seen. The test also needs all four checkers running at the same moment. This could fail if one checker finished its 2-second sleep before the driver started the fourth. On `main` the test ran 246 times under stress: 16, 40 and 30 copies at once, then four rounds of 40 at once beside ten busy loops. Two runs failed. One is the KILLED failure quoted above. The other was in the busy-loop rounds, where output was not kept, so its cause is not known. With the lock, three rounds of 40 beside the busy loops gave 0 failures in 120.

The EMPTY-OUTPUT park reason. The pipeline can be run two ways: by the driver, or by two Workflow scripts, `intake.js` and `build.js`, that run the same steps from inside a Claude Code session. Each must leave the same records. So the reason is written in three places: `factory/drive.py:182`, `factory/workflows/intake.js:83` and `factory/workflows/build.js:74`. Each place writes `EMPTY-OUTPUT from <role>`. The last message is kept by `factory run last-message` (`factory/cli.py:298-305`), which prints `{"ok", "run_id", "last_message"}`. The driver calls it at `factory/drive.py:241-242`, the scripts at `intake.js:126-127` and `build.js:130-131`. A prototype of Part D printed these park reasons through a current-truth fixture that takes one ticket through both the driver and a Workflow script and compares the records each leaves. The waiting message is the one T-0047.2's verifier ended on:

| Case | Reason on `main` | Reason with Part D |
|---|---|---|
| Intake, triage says "Waiting for the suite runs to finish before writing the output." | `EMPTY-OUTPUT from triage` | `EMPTY-OUTPUT from triage: ended its turn waiting on a background command` |
| Build, reviewer says the same | `EMPTY-OUTPUT from reviewer` | `EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command` |
| Intake, triage says "I could not finish: the input file was missing." | `EMPTY-OUTPUT from triage` | `EMPTY-OUTPUT from triage` |

In each case the script and the driver produced the same records (`same`). On the Part D prototype, that fixture's four current-truth intake cases and four build cases printed exactly their current-truth lines. So did the four scenarios of the requirement this spec modifies, except the first, whose reason gains the suffix. The full suite passed (583) with the two test changes listed under Tests to change, and `git diff --check main...HEAD` printed nothing.

Other facts checked on this checkout:
- The gate commands are `gate_commands` in `.factory/instance.yaml:22-24`, and the suite command there is `uv run --frozen pytest -q -p no:cacheprovider tests/factory`. Gate commands are the checks every sub-ticket must pass before merge. There is no `.factory/config`.
- `pyproject.toml` has no `[tool.pytest.ini_options]`, and there is no `pytest.ini`, `setup.cfg` or `tox.ini`.
- `factory/prompts/preamble.md:45-48` already tells every role to run commands in the foreground. This change does not touch it.
- `factory/cli.py` is 884 lines. The current-truth harness-code requirement keeps it under 900 (`/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-code/spec.md`), and the Part D prototype made it 890. The same capability fixes the top-level names of `factory/common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`. This change adds none there.
- The acceptance scenarios reuse fixtures from current truth: `t0023-parent.sh` and `t0023-wf.mjs` (`/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`), and `t0032-*`, `t0022-*` and `t0040-*` (build-dispatch).
- `factory/stats.py:50-55` groups parks by the first two `: `-separated fields of the reason. A waiting park will therefore count as its own row, `EMPTY-OUTPUT from <role>: ended its turn waiting on a background command`.

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
- A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT (MODIFIED): its four scenarios.
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

## Responses

- [BLOCKING] Part letters unglossed in Decisions and Evidence → FIXED. The Problem's last paragraph now introduces the change as five lettered parts, A to E, with one line each, before Evidence or Decisions uses a letter. Part B also glosses gate commands there.
- [SHOULD-FIX] sub-ticket, current truth and play used unglossed → FIXED. Problem paragraph 2 says what a sub-ticket is before naming T-0047.2, and Problem bullet 3 says what a checker is. Evidence glosses current truth at its first use (the store's record of what the harness does today, grouped by capability) and plays at theirs (the scripted replies a test sets for each stand-in role). While there, I also glossed the Workflow scripts and replaced "driver-against-script fixture" with what that fixture does.
- [NIT] Stand-in check blind to a swallow-and-restart fix → FIXED. The script now also prints the stand-in's final verifier count, and the THEN expects `counter 800` for each stand-in. On `main` it printed `counter 769` / `763`, and again `777` / `765`. A locked prototype printed `800` for both. The WHEN gains `-B`, so importing the helper module writes no bytecode under `tests/`. Evidence and verification.md carry the new output.
- [NIT] Tests to change omitted `test_drive_build.py:60` → FIXED. Tests to change now names it, and says why it stays green: its reviewer says `""`, and `drive.py:241` sends only a non-blank message to `run last-message`.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, `main` is still at `88c65e1`, and the one changed acceptance command was run as written on `main`, where it fails for the stated reason, and on a locked prototype, where it passes. The other items are unchanged from round 1 and the critic reproduced them.
ESCALATIONS: none
