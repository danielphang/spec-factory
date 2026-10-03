## Problem
The spec factory is a pipeline of AI agents that turns a request into merged code. Before a change merges, two checker agents look at it: a reviewer, which reads the diff, and a verifier, which runs the acceptance commands and the test suite. A script called the build loop runs each checker. It then records the checker's verdict with a small command, `factory results record`, which files the verdict in a results table keyed by commit. Next it asks the store what to do with the ticket. When something needs a person, the build loop "parks" the ticket, which stops work on it and writes down a reason for the operator.

A checker run can be killed: the agent hits a budget or session limit and returns nothing. The intended outcome is a park with reason `budget kill: <role>`, which tells the operator to send the same work out again. That is what happens today, but only on paper. When the build loop records a killed checker, the recording command crashes. The build loop always passes the path of the run's output file, and a killed run never writes that file. The command opens the file before it checks whether the run was killed. Because recording failed, the build loop parks the ticket with reason `harness-bug: results record <role>`. That reason tells the operator the factory itself is broken, and it hides the real cause (an ordinary budget kill).

Who is affected: the operator. Every killed reviewer or verifier run is reported as a factory defect, so the operator investigates the factory instead of re-dispatching the work. No work is lost: the ticket still stops for a human.

## Evidence
- Request: GitHub danielphang/spec-factory#18. It was found by the spec writer of #16 (green-pilot T-0001) as an out-of-scope observation.
- Code on this checkout (`/Users/dphang/dev/nanobot-upstream`, branch `feat/lionbot-v3`, HEAD `f8f40e0c5`):
  - `factory/workflows/build.js:139` records every checker with `results record … --output ${r.outputPath} --run …`, and appends ` --killed` when the run's status is KILLED. When that call fails, `build.js:140` parks with `harness-bug: results record ${role}: <stderr>`.
  - A run counts as killed when the agent returns null or empty text (`build.js:91`). It is then closed with `run finish <id> --status-override KILLED` (`build.js:93`). `run finish` writes `output.md` only when `--output-file` is given (`factory/cli.py:255`), so a killed run has no `output.md` unless the agent wrote one before it died.
  - `factory/cli.py:425` (`results_record`) reads `Path(a.output).read_text(...)` whenever `--output` is given, before the `if a.killed:` branch at line 426.
  - Once both checker rows exist, `ticket join` already returns `park` with `budget kill: <roles>` when a row is KILLED (`factory/cli.py:532-533`). A killed verifier writes no `ci` row, and the join allows for that (`cli.py:436`, `cli.py:524-525`). The right reason exists. Only the recording step fails before it.
  - The test suite misses this because its stand-in for the build loop records killed checkers without `--output` (`tests/factory/test_shepherd.py:642-645`), which is not how `build.js:139` calls the command.
- Reproduced black-box with `bin/factory` against a throwaway store, run from the repo root under both bash and zsh. The exact commands are the WHEN lines in the spec below.
  - A reviewer APPROVE is recorded, then a killed verifier is recorded the way `build.js` does it (`--output` names the run's missing `output.md`, plus `--killed`). Result: `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci`. Recording exits 1 with `FileNotFoundError`. In the build loop that exit becomes `harness-bug: results record verifier: …`.
  - The same with the roles swapped: `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer`.
  - A killed verifier whose partial output names another commit (`Commit: deadbeef00`): `exit=2 rows=[] status=` (refused). In the build loop that is also a `harness-bug:` park.
  - A killed verifier with no `--output`: `exit=0 rows=[verifier.yaml ] status=KILLED`. This is the path the test fixture uses, and it works.
- The factory suite today: `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` → `55 passed in 70.71s`.

## Root cause
`results_record` in `factory/cli.py`. It reads the `--output` file unconditionally when the flag is present (line 425). Only after that does it look at `--killed` (line 426). The build loop always passes `--output`, and a killed run has no file at that path, so the read raises `FileNotFoundError`. `main()` turns that into exit 1 (`cli.py` `main`, the `except Exception` branch). A second, smaller failure has the same cause. If a killed run did leave a partial output, the `Commit:` check (lines 431-433) still runs on it. A stale `Commit:` line then refuses the record (exit 2), which also parks as `harness-bug:`.

## Out of scope
- `factory/workflows/build.js` (a protected path): unchanged. Its call shape (`--output` always, `--killed` when killed) is what this change makes work.
- Without `--killed`, `results record` behaves exactly as it does at the time this is built, including #16's `Commit:` checks and the error when the `--output` file is missing.
- The join's routing, its reasons, the merge gate, and the rule that a killed verifier writes no `ci` row.
- The existing test fixture's killed path in `tests/factory/test_shepherd.py` (it records without `--output`). It stays as it is. The new test uses the build loop's call shape instead.
- The `--head` validation and the stale-result rule.

## Open questions
none

## Decisions
- With `--killed`, `results record` does not open the `--output` file at all. A missing file is not the only case covered: a killed run's output is never read. This is the requester's proposed fix ("does not read `--output` when `--killed` is given (a killed row needs no output)"), and the operator approved it in advance. Only tolerating a missing file would leave the second failure in Root cause in place: a killed run whose partial output has a stale `Commit:` line would still park as `harness-bug:`, the misleading reason this ticket removes.
- As a result, a killed run's output is no longer checked for its `Commit:` line. This changes one case that #16's spec keeps "exactly as today": a killed output that names another commit is now recorded KILLED instead of refused. That check protected nothing. A KILLED row can never satisfy the merge gate, which requires `ci PASS`, `APPROVE` and `VERIFIED` (`factory/cli.py:467-470`), and the join parks on it. #16's two killed scenarios (no `--output`, and a cut-off output with no `Commit:` line) still record KILLED and still pass.
- The fix goes in `factory/cli.py`, not `build.js`, so the build loop stays unchanged and the command works for both callers (with or without `--output`).
- The requirements are ADDED under capability `checker-results` (the capability #16's change uses). Current truth (`openspec/specs/`) is empty on this checkout. If #16's change is archived first, its requirement `killed-run-recording-is-unchanged` stays true, and these requirements sit beside it under new names.
- Sequencing: build after #16 (green-pilot T-0001 / T-0001.1) merges, on top of its `results_record`, as the operator's note requires. Every acceptance result below was checked against both the current code and a simulation of #16's change.

## Risk
- Blast radius: the `--killed` path of one function, `results_record` in `factory/cli.py`. Its callers are the build loop's checker step (`build.js:139`) and tests. Recording an unkilled run is unchanged. After the change, every killed checker records a KILLED row and exits 0, and the join parks it as `budget kill: <role>`. A killed run's partial output is no longer looked at by this command (see Decisions). It is still kept in the run folder for the operator.
- Merge-order risk: #16 rewrites the same few lines. Building after #16 merges, as required, avoids a conflict. The implementer should drop #16's killed-only `Commit:` branch if it becomes unreachable, rather than leave dead code.
- Protected paths touched: none. `factory/cli.py` and `tests/factory/` are outside `factory/workflows/**` and `factory/config.yaml`.
- Guardrail paths touched: none. No existing test is edited. One new test file is added.

