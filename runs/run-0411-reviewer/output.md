Commit: 4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8

Round 1. Diff `2ad4d8c...4bfedc7`: `factory/drive.py` (+269/-23) and the new `tests/factory/test_drive_build.py` (+244), confirmed with `git diff --stat` in the worktree. No other file changed.

## What I checked

1. Test integrity. No existing test file is touched; the sub-ticket's "Tests to change: none" holds. The nine new tests live in a new file, as the sub-ticket directs. The file imports `BIN`, `REPO` and `Store` from `tests/factory/test_drive.py` (lines 24, 25, 53; `tests/factory/__init__.py` exists, so the relative import resolves), and every `Store` attribute it uses (`tmp`, `root`, `log`, `env`, `ok`, `drive`, `ticket`, `runs`, `calls`) exists there (lines 57-91).

2. Correctness, the port. I read `Driver.build` and `Driver.build_one` (`factory/drive.py:321-525`) side by side with `factory/workflows/build.js` from `// --- start` (line 217) to its end and with `buildOne` (lines 142-215). Every branch is present with the same store command, arguments, transition (`--by workflow`, `pr:init`, `join.round_op`), park reason and park outputs: `plan whole-spec` and the planner's `spec tasks` / `plan add` / `subticket add`; the `ready-implementers` loop with the one-time `subticket add`, the closed-sub-ticket park, `resumable` and `remaining`; `parent-check` twice and `reuse`; the parent-close verifier, `archive`, `closed`; in `build_one`, the implementer, `ticket head` with `merge_refused` and its join, `checks-in-flight`, the role filter from `results show` (`ci` meaning the verifier), `results record` with `--head`, `--output`, `--run` and `--killed`, the join's five decisions, `merge`, the verbatim `BLOCKED ` park, the second join after a refusal, and the trailing `park`/`wait` park. The two departures the PR description names (`j.get("reason") or ""` where the script would throw on `undefined`) are correct and unreachable with today's `ticket join`. `park()` (`drive.py:150`) applies the script's `"` to `'` replacement, so the stored reason matches.

3. Concurrency. `_all` (`drive.py:582`) is `asyncio.gather` over tasks; `check()` returns `None` rather than raising on a parked run, so a failed checker never short-circuits the gather and the other checker records its result first (`test_a_failed_checker_ends_the_pass_only_after_the_other_has_recorded` pins it). The sub-tickets of one `ready-implementers` answer run under `asyncio.Semaphore(self.parallel)` (`drive.py:352-357`) and the loop waits for all before asking again, as the script's `parallel()` does. `--parallel` is `type=_at_least_one, default=2` at `factory/cli.py:1904` (part A's). Under a stop, cancelling the route cancels the gather's children; `_all` waits for them and re-raises, so `stop()` runs after no task is still routing. The run and proc entries a cancelled `run_once` leaves in `self.running` / `self.procs` are what `stop()` finishes KILLED; the stop test pins both checkers KILLED and the sub-ticket left at `checks-in-flight`, unparked.

4. Scope. Every change is part B items 1-4 or the plumbing they need: `run_once` returning `outputPath`, `transition(..., ticket)`, `step()` reading the sub-ticket's title, the `titles` map, `self.parallel`, the `re` import, the removal of A's interim refusal and the now-unused `Refused` import, the module docstring. Nothing touches A's intake routing, `call()`, the argv, `run finish --reply` or the stop sequence beyond that. `build.js` is untouched. Part C's documents are untouched.

5. Silent behaviour changes. `step()` now folds a multi-line step text onto one line (`drive.py:143`). This also changes an intake park line whose reason ends in stderr's newline: it no longer emits a trailing blank line. That is a fix toward the spec's "Every line ... MUST have the form `<ticket id> "<title>": <step>`", the stored reason is unchanged, and the PR description discloses it. Not a finding.

6. Security and data safety. No new paths, no new subprocess beyond `claude` (A's), no shell. The implementer's `Edit(/<worktree>/**)` and `--add-dir` are A's `role_argv`, unchanged; the new test pins that the checkers get neither.

7. Protected paths. `factory/drive.py` under `factory/**`, declared by the sub-ticket and the parent's Risk section. Listed under ESCALATIONS for the record.

8. Coding standard. `_all` sits on rung 2 (stdlib `gather`) plus the one behaviour `gather` lacks, cancel-and-wait on a sibling's exception, which the PR description justifies against `TaskGroup`. No duplicate of an existing helper, no dead code, callers of the changed functions named (rule 2). `factory:` markers: none added, A's one removed, stated (rule 3). Lean already.

9. PR description. What changed is in words, glosses the build half, the checkers and the join decisions, and names the two departures from the script. Known gaps is honest about the unexercised branches, the untested `_all` exception path, and the stop test not being re-run against base. Readable at the gate.

## Findings

None.

Prior findings: none (round 1).

## Out-of-scope observations

- `Known gaps` lists several ported branches that no suite test or fixture reaches (planner refusals, `merge_refused`, a `BLOCKED ` merge refusal, `reuse`, `archive` success). They match the script line for line, so I did not require tests the spec did not ask for; a later ticket could add fixtures for them.

STATUS: APPROVE
CONFIDENCE: high. The port matches `build.js` branch for branch on a side-by-side read, the concurrency and stop semantics follow from the code and are pinned by the new tests, and no existing test or out-of-scope file changed.
ESCALATIONS: protected path `factory/drive.py` (`factory/**`) touched, declared by the sub-ticket and the parent's Risk section; for the record only.
