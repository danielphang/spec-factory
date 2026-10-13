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
