## Proposed change

This is too large for one reviewable change (about 650 lines with tests and documents), so it is marked NEEDS-SPLIT. There are three seams:
- ST-1 is part A and its tests.
- ST-2 is parts B and C and their tests, and depends on ST-1.
- ST-3 is part E, and depends on ST-2.

Part D lists the tests of each. The acceptance scenarios split the same way:
- ST-1 owns "The transcript cost report counts each message once".
- ST-3 owns "The documents record factory stats".
- ST-2 owns every other scenario, the three restated live-store-guard scenarios included.

A. Transcript reading (`factory/cost.py`).
   - Count each message id once. Change `tally()` to keep, for each transcript, the last usage seen for each `message.id`, counting a record without an id on its own. Make `calls` the number of ids kept. Put this in a function `transcript_usage(path) -> (calls, ctx, out)`, which `tally()` and part B both use. Update the module docstring, which today says nothing of the double count.
   - Add `match_transcripts(dirs, stores) -> {(store, run_id): path}`, implementing the matching rule under Decisions. It reads at most the opening records of each file it needs to place: up to the first user message naming a run directory.
   - Add `gate_failures(transcript, input_md) -> int | None`, implementing the gate rule under Decisions. It returns None when the input has no "Gate commands" line.
   - `python -m factory.cost DIR...` keeps its interface and table, so `| role | model | agents | calls | ctx tokens | out tokens |` is unchanged.

B. The command (`factory/stats.py`, new). `report(stores, since, until, transcripts) -> str` builds the text below. A store is read from `runs/*/meta.yaml`, `runs/*/output.md`, `runs/*/input.md` and `log/*.jsonl`. Parse `started`, `finished` and `ts` whether YAML gives a string or a datetime. Keep the names `CHANGED`, `BLOCKING` and `PARK_RULES` (the normalisation list) as module constants. The output, in this order:
   - `# factory stats`, then `Stores: <absolute resolved path>[, <path>]...`, then a line naming the window and the number of runs left out as in flight.
   - `## A. Runs and verdicts by role and model`, then a table with the header `| role | model | runs | killed | changed outcome | verdicts | BLOCKING findings | gate fails fixed before hand-off |` and a `|---|` separator row.
     - Verdicts are `<STATUS> <n>` pairs, joined by `, ` and sorted by status.
     - BLOCKING is a number for reviewer and critic rows, else `-`.
     - The gate column is `<fails> in <read> read, <n> not recorded` for implementer rows, else `-`.
     - A row with no runs and no kills is not printed.
   - `## B. Where tickets stop`. Park reasons are taken after the correction rule under Decisions (`park.corrected`), then normalised. First `| park reason | parks |`, with rows by count descending and then reason in code-point order, and a last row `| all parks | <n> |`. Then a blank line and `| gate or merge decision | count |`, with rows in this order:
     - `spec approved` and `spec changes requested`, always printed;
     - `resolved: <kind>`, by kind;
     - `merge refused: <reason>`, by reason;
     - `archive refused`, always printed.
   - `## C. Where spec defects were caught and where they came from`. First `| caught by | status | ticket | spec version | written by | critiqued by | critic REVISE on the ticket |`, one row per catch, ordered by the catching run's `started`. Then a blank line and `| critic REVISE on the ticket | approved specs | caught downstream |`, with rows `yes` and then `no`. Both count tickets, per store, with a spec approval in the window.
   - `## D. What each role costs`, with `| role | model | runs | wall s | context tokens | output tokens | USD from records | cost from |`.
     - Runs include killed runs.
     - Numbers are plain integers, and USD has two decimals.
     - `cost from` reads `record <n>, transcript <n>, none <n>`.
     - Rows follow section A's order.

C. CLI (`factory/cli.py`).
   - Add the `stats` subparser with `--store` (repeatable), `--since`, `--until` and `--transcripts` (repeatable), and a `stats_cmd(a)` that resolves the stores (Decisions), calls `stats.report` and prints it.
   - Refusals (no store found, a path that is not a store, an unparsable WHEN) raise `Refused`, so they exit 2.
   - In `main()`, line 1972, handle `stats` as `init` and `paths` are, before `instance.require()`, the fence and `instance.guard()`.
   - Add `("stats", None)` to `READ_ONLY` (line 1939), so the code's list matches the documents. Update `fence()`'s and `main()`'s comments.

D. Tests, in new files only, in each sub-ticket that adds the code they test.
   - `tests/factory/test_cost_once.py` (ST-1) covers:
     - `tally()` on a transcript with repeated message ids;
     - the matching rule (path preference, the relay message skipped, another store's path ruled out, the time window, a unique fallback);
     - `gate_failures()` for a fixed failure, a failure never fixed, and an input with no gate line.
   - `tests/factory/test_stats.py` (ST-2) covers:
     - each section's rows on a fixture like the acceptance fixture;
     - the window;
     - each normalisation rule, and the correction rule (a matching correction, one dated after `--until`, one whose `previous` matches no park);
     - the refusals;
     - a run on an own store with a run in flight, from the store's `runs/`, and under a harness lock that names another revision. Use `tests/factory/test_live_store_guard.py`'s way of building one.

E. Documents (ST-3).
   - `README.md`:
     - In "Where a human decides", the sentence listing the commands that are not writes ends "`log tail`, `paths` and `stats`".
     - In "Accepting a harness revision", one sentence says that `paths` and `stats` skip both checks because they write nothing.
     - A new how-to subsection, `### Counting what each role catches and costs`, after "What you read at each stop", says:
       - what `factory stats` prints;
       - its options;
       - that `--transcripts ~/.claude/projects` adds cost for runs without a cost record;
       - that `--until` makes a past figure repeatable;
       - the gate-failure limit (a command run in another form is missed).
     - In "What depends on Claude Code", a row says `factory stats` reads the store with no Claude Code, and Claude Code transcripts only for `--transcripts`.
     - A **Built** bullet names `factory stats`.
     - Bump the status date.
   - `docs/design.md`:
     - The fence paragraph's read-only list ends "`log tail`, `paths` and `stats`".
     - The role-context paragraph's lock clause says that `paths` and `stats`, which only read, run under any revision.
     - The model-per-role paragraph gains one or two sentences citing `factory stats` and the figures it prints for the reviewer, critic, verifier and implementer rows of sections A and D. Use `--until 2026-10-07T12:00 --transcripts ~/.claude/projects` over both stores, give the date and the command, and compare with the figures under Evidence.
     - The §8 prompt block is unchanged.
   - `docs/principles.md` §4: line 60's "1 BLOCKING finding in total" becomes "3 BLOCKING findings in total". The "Implemented by:" line (68) names `factory stats` and drops "double-counts", and the "Planned:" line keeps only the evidence ladder (#79).
   - `dev/build-harness.spec.md`: after the `**`factory drive`**` paragraph (line 295), add a `**`factory stats`**` paragraph. It gives `factory/stats.py`, the options, the four sections, that the command reads and never writes, and that it skips the instance lookup, the fence and the lock as `paths` does.
   - `docs/changelog.md`: entry 70, in the "After issue #N (date), where ...:" form of entries 66-69. It names issues #70 and #61, the once-per-message-id count, the measured 1.89 and 1.94 factors, `factory stats` and its exemption, and the rejected alternatives under Decisions.
   - No file under `docs/prompts/` or `factory/prompts/` changes.

## Tests to change

none. No suite test calls `factory.cost`, asserts the read-only list, or runs a command that is not one of `init` and `paths` outside the lock. I checked with `grep -rn 'cost\|tally\|READ_ONLY' tests/factory/*.py`. `tests/factory/test_harness_lock.py:48` names `("init", "paths")` only to choose how its helper runs the CLI, and no test there calls `stats`. The one current-truth requirement that the new behaviour contradicts, live-store-guard's list of commands exempt from the in-flight refusal, is restated below as a MODIFIED requirement.
