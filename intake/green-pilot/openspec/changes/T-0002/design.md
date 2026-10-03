## Proposed change
A. `factory/cli.py`, `results_record`: read the `--output` file only when `--killed` is not given. Today that is line 425: `text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""`. After #16 merges, apply the same rule to #16's version of the read. With `--killed`, the function records the KILLED row (and no `ci` row, as today) without opening or checking the output. With #16 merged, its killed-only `Commit:` check then has nothing to look at. Remove that branch so the `Commit:` checks apply only to unkilled runs. Do not change anything else in the unkilled path.
B. New test file `tests/factory/test_killed_checker.py`. It covers both checker roles (one test, parametrized over `verifier` and `reviewer`). It brings a sub-ticket to checks with the existing `built_to_implementer` helper (`from .test_shepherd import built_to_implementer`; this relative import works under the current pytest setup, checked in a scratch run), dispatches the implementer and the other checker normally, then runs the killed checker exactly as `build.js:91-94` and `:139` do:
   1. `run start`, then `run compose`.
   2. `run finish <id> --status-override KILLED`, then `run cleanup <id>`.
   3. `results record <st> --head <ticket head> --role <role> --output <store>/runs/<id>/output.md --run <id> --killed`, asserting first that the file does not exist.
   4. Act on the join with the shepherd's `act_on_join`.
   Then it asserts the sub-ticket is parked with reason `budget kill: <role>`. Every CLI call goes through the shepherd's `ok()`, so a non-zero exit fails the test with its stderr.

Size: about 3 changed lines in `factory/cli.py` (a few more if #16's killed branch is removed), and a new test file of about 35 lines.

I checked this design in scratch copies of `factory/`, `bin/` and `tests/factory/`, not in this checkout:
- (i) This checkout with part A: every WHEN below gave its PR result. `tests/factory` plus a sketch of part B gave `57 passed`.
- (ii) A simulation of #16's change (its part A, and part B's fixture edit) without this fix: the base results below, and the part B sketch failed in both cases with `FileNotFoundError: … runs/run-0007-verifier/output.md` (and `…run-0007-reviewer…`). The rest passed: `2 failed, 55 passed`.
- (iii) The same simulation with part A: the PR results below, and `57 passed`.

## Tests to change
none

