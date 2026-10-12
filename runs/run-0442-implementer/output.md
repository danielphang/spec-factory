Sub-ticket: T-0043.3 (ST-3 of T-0043, spec v2: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`), branch `factory/T-0043.3`, head `608a62c`, base `ebc5773`

## What changed

ST-3 adds no code. It records the new `factory stats` command in the five documents that describe the harness. `factory stats` is the read-only command, added by the two earlier sub-tickets, that counts each role's verdicts, parks and token cost from a store, the factory's file-based record of runs and events. The commit is `608a62c` and changes only `README.md`, `docs/design.md`, `docs/principles.md`, `dev/build-harness.spec.md` and `docs/changelog.md`. `git diff --stat main...HEAD -- factory tests bin agents pyproject.toml uv.lock` prints nothing.

Part E, file by file:
- `README.md`:
  - In "Where a human decides", the list of commands that are not writes now ends "`log tail`, `paths` and `stats`".
  - "Accepting a harness revision" gains one sentence: "`paths` and `stats` skip both checks on any store, because they write nothing." This matches `factory/cli.py` `main()`, which runs `init`, `paths` and `stats` before `instance.require()`, the fence and `instance.guard()`.
  - New how-to subsection, `### Counting what each role catches and costs`, after "What you read at each stop". It gives the command line, a table of the options and a table of the four sections. It explains cost records against transcripts and suggests `--transcripts ~/.claude/projects`, which took 12.3 s when I ran it. It also says why `--until` makes a figure repeatable, and states the gate-column limit: a gate command run in another form is missed, so the column can undercount.
  - "What depends on Claude Code" gains a row. `factory stats` reads the store with no Claude Code, and reads Claude Code's transcripts only when given `--transcripts`.
  - **Built** gains a `factory stats` bullet. It says the command has run over both targets' stores, which I did.
  - "Related work and history" gains one sentence: `factory stats` answers #70, absorbs #61, and the retro feed is #42.
- `docs/design.md`:
  - The fence paragraph's read-only list now ends "`log tail`, `paths` and `stats`".
  - The role-context paragraph's `harness.lock` clause now adds "`paths` and `stats`, which only read, run under any revision".
  - The model-per-role paragraph gains two sentences that cite `factory stats` and the command I ran (`--until 2026-10-07T12:00 --transcripts ~/.claude/projects`, over both stores, on 2026-10-11). They give the reviewer, critic, verifier (both models) and implementer figures from sections A and D, and how these differ from the request's hand count.
  - No prompt block changed, §8 included.
- `docs/principles.md` §4:
  - "1 BLOCKING finding in total" becomes "3 BLOCKING findings in total".
  - "Implemented by:" now names `factory stats` and no longer says "double-counts".
  - "Planned:" keeps only the evidence ladder (#79).
- `dev/build-harness.spec.md`: a `**`factory stats`**` paragraph follows the `**`factory drive`**` paragraph. It gives `factory/stats.py`, the options, the refusals, the window rules, the four sections, that the command reads and never writes, and that `main()` runs it, like `paths`, before the instance lookup, the fence and the lock. It also says `stats` is listed in `READ_ONLY`.
- `docs/changelog.md`: entry 70 follows the "After issue #N (date), where ...:" form of entries 66 to 69. It names issues #70 and #61, the once-per-message-id count, the measured 1.89 and 1.94 factors, `factory stats` with its four tables and its exemption, the corrected BLOCKING figure, and the alternatives rejected under the spec's Decisions. It says that figures quoted from `factory/cost.py` before this change (entries 58 and 67) are history and are not restated.

The design doc's figures come from `bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 --transcripts /Users/dphang/.claude/projects`. I ran it under the wrapper on this branch and it exited 0. I gave the transcripts directory as an absolute path because the wrapper's HOME is a temporary directory. The rows it printed:
- A: `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 111 read, 0 not recorded |`, `| verifier | opus | 108 | 0 | 8 | ... |` and `| verifier | fable | 5 | 0 | 1 | ... |`.
- D: reviewer 99 runs and 94,860,442 context tokens; critic 84 and 66,027,675; implementer 114 and 372,507,821; verifier on Opus 108 and 232,945,610; verifier on Fable 5 and 5,189,563.

These equal the spec's Evidence figures: the A rows, and the totals of 94,860,442, 372,507,821 and 232,945,610 context tokens, with the run counts of 99, 114 and 108. Evidence also said the gate column found 0 fixed failures in 111 implementer runs, and the command prints `0 in 111 read`.

I re-checked two claims the changelog repeats from the spec's Evidence:
- That a once-per-id count equals a cost record. `transcript_usage()` on `run-0413-spec_writer`'s transcript (`4730aa67-….jsonl`) returns `(61, 13959978, 74126)`. That run's `meta.yaml` cost record gives 122 + 178,311 + 13,781,545 = 13,959,978 context tokens.
- The double-count factors, with `scratch/factor.py`. For the Nanobot store it printed 2,016,972,806 tokens counting every record against 1,069,416,588 counting once (1.886), the same as Evidence. For this store it printed 1.95 over 443 matched runs, against the 1.94 that Evidence measured on fewer runs. So the changelog says the factors were "measured ... when the change was specified".

## Acceptance results

All commands ran from the worktree through the briefing's wrapper, after `uv sync --frozen`.

- NEW "The documents record factory stats". I ran the spec's command verbatim from `scratch/docs-check.sh`.
  - Before (base `ebc5773`): `readonly=no howto=no built=no depends=no lock=no design-fence=no design-lock=no design-model=no principles=no principles-old=yes buildspec=no prompts=0`, `CONTIGUOUS`, `0`, `clean`. This matches the "today" output in verification.md: nothing was documented yet.
  - After (`608a62c`): `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`. This is exactly the expected output: every document records `stats`, the old figure is gone, no prompt copy changed, the changelog has no numbering gap, its last entry has all four markers, and the diff has no whitespace errors.
- REGRESSION "Stats reproduces the hand count on the two live stores", run on `608a62c` with `TMPDIR` set to the scratch directory. It printed `exit=0`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 0 read, 111 not recorded |`, `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| verifier | fable | 5 | 0 | 1 | SPEC-DEFECT 1, VERIFIED 4 | - | - |`, `| verifier | opus | 108 | 0 | 8 | FAILED 4, SPEC-DEFECT 4, VERIFIED 100 | - | - |`, `| NEEDS-HUMAN from triage | 30 |` and `| all parks | 82 |`. These are the eight expected lines, exactly. The command whose figures the design doc quotes still prints them.
- REGRESSION and gate: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, as written.
  - First run on `608a62c`: exit 1, `1 failed, 576 passed in 348.15s`. The failure was `tests/factory/test_drive_build.py::test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit`, with `assert (4 == 4 and 3 == 4)`: a timing assertion on how many stub role processes ran at once.
  - The branch changes no code, so the code under test is the base's. Run alone three times on `608a62c`, that test passed each time (`1 passed, 8 deselected`, in 6.8 to 8.7 s).
  - Second full run on `608a62c`: exit 0, `577 passed in 346.30s`. I take the first failure to be load-dependent flakiness, not a regression; see Known gaps.
- Gate `git diff --check main...HEAD`, as written: exit 0, no output, so no whitespace errors.

## Tests added/changed

None. The sub-ticket lists no interim tests and no tests to change, and it changes documents only.

## Known gaps and uncertainties

- The status date in README's header already read 2026-10-11, which is today. "Bump the status date" therefore left it unchanged.
- The design doc's command line writes `--transcripts ~/.claude/projects`, as part E specifies. I ran it with the absolute path `/Users/dphang/.claude/projects`, the same directory, because the wrapper's HOME is a temporary directory. Its D figures depend on transcripts Claude Code still keeps. If Claude Code deletes old transcripts, a rerun may print fewer tokens, and those runs move to the `none` source column.
- The design paragraph says the implementer had "no gate failure found fixed before hand-off". That rests on the text match README states as a limit, so the true count may be higher.
- The full suite failed once on a timing assertion in `test_drive_build.py` and then passed. I did not investigate that test, because this branch touches no code.
- README's "Related work and history" paragraph had overlong lines before this change. I added one sentence to it without reflowing the paragraph, so it stays ragged.

## Out-of-scope observations

- `test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit` (`tests/factory/test_drive_build.py:194`) asserts an exact peak concurrency of stub processes. Under the load of the full suite it saw 3 where 4 were expected. A sound fix is out of this ticket's scope.
- Over every matched run, this store's double-count factor is now 1.95, against the spec's 1.94, because the store has grown. The changelog keeps the measured figure and says when it was measured.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The NEW check prints exactly its expected output, the live-store regression prints its eight lines, and both gates pass on `608a62c` (the suite on its second run).
ESCALATIONS: none
