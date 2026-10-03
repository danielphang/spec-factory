## Proposed change
A. `factory/cli.py`, `results_record`: replace the optional first-match check (lines 431-433) with a strict check that applies when `--killed` is not given:
   1. Collect every line of the output that starts with `Commit:`. If there are none, refuse: `results record: the output has no Commit: line`.
   2. For each such line, parse the value with today's grammar (optional backtick, 7-40 hex, optional backtick, word boundary). If it does not parse, refuse and name the offending value (for example `results record: Commit: HEAD is not a commit id`). If it parses but the lowercased value is not a prefix of `--head`, refuse with today's message (`the output says Commit: <value>, not the head <head[:12]>`).
   3. All refusals raise `Refused` before any `store.record_result` or `store.log_event` call, so nothing is written. This is the same placement as today's check.
   When `--killed` is given, keep today's check unchanged (first hex `Commit:` line, refuse only on mismatch; no line means no check).
B. `tests/factory/test_shepherd.py`, in the merge-gate story: change the direct `results record ... --role verifier --output <red.md>` call (line 268) so its `--output` is the dispatched run's `output.md` (`f.store / "runs" / ver.run_id / "output.md"`). In that file the dispatcher has already replaced `Commit: HEAD` with the real head (line 648). The story's assertions stay as they are.
C. New test file `tests/factory/test_results_commit.py`. It drives `bin/factory` as a subprocess against a temporary `FACTORY_STATE`, as `tests/factory/test_shepherd.py` does. It covers each scenario in the spec below: refusals leave no row and no `result.*` event, and the accepted forms record.

Size: about 20 changed lines in `factory/cli.py`, 1 in `test_shepherd.py`, and a new test file of about 100 lines.

I checked this design in a scratch copy of `factory/`, `bin/` and `tests/factory/` (not in this checkout). Without part B the factory suite failed only in the merge-gate story (`results record: Commit: HEAD is not a commit id`, exit 2). With part B it was `55 passed`. All nine WHEN commands below gave the PR results stated in their THEN lines.

## Tests to change
- `tests/factory/test_shepherd.py` line 268 (in the merge-gate story). It writes `red.md` with `Commit: HEAD` (line 264) and records it directly with `results record --output red.md` through `f.ok`, which asserts exit 0. Under the fix that output has a non-hex `Commit:` value, so the call exits 2 and the story fails. The change points the call at the run's `output.md`, which has the same content with the real head substituted. The behaviour under test (a red verifier and a red ci row block the merge) is unchanged. The other `Commit: HEAD` fixtures (lines 327, 408-409, 489 and the stubs under `tests/factory/fixtures/stubs/`) go through `dispatch`, which substitutes the real head. They passed unchanged in the scratch run.

