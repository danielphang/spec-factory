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

