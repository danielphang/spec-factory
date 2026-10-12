# Plan for T-0043: `factory stats` and the once-per-message cost count

The approved spec (v2) already names its three seams (design.md, "Proposed change": ST-1 is part A, ST-2 is parts B and C, ST-3 is part E, with part D's tests split between them). This plan follows those seams and does not split further: each one is a single reviewable change, and a fourth would only add a re-verify cycle. The three run in a chain, because each needs the previous one's code or output.

Checked on this checkout (`main` at `5215c5f`, the revision verification.md was captured on): `factory/cost.py` exists and has `tally()` at line 47 and no `transcript_usage`, `match_transcripts` or `gate_failures`; `factory/cli.py` has `build_parser()` at line 1753, `READ_ONLY` at line 1939, `main()` at line 1969 and no `"stats"`; `factory/stats.py`, `tests/factory/test_cost_once.py` and `tests/factory/test_stats.py` do not exist; `tests/factory/test_live_store_guard.py` exists; no file under `tests/factory/` mentions `factory.cost`, `tally` or `READ_ONLY`; and the log shows no earlier plan or sub-ticket for T-0043.

---

## ST-1 / Count each transcript message once, and add the transcript readers that `factory stats` needs
Depends on: none
Parallel-safe: no (ST-2 builds on the functions this adds, and ST-3 on ST-2)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A (all of it: `transcript_usage()`, the once-per-message-id fix in `tally()` and in `calls`, the docstring, `match_transcripts()`, `gate_failures()`, and the unchanged `python -m factory.cost` interface and table), and part D's `tests/factory/test_cost_once.py`.

Acceptance:
- NEW. "The transcript cost report counts each message once". First run the fixture GIVEN block from "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" once, as written in the spec. WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')` THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`. On `main` it prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`.
- NEW (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_cost_once.py` THEN it passes. The file covers what part D lists for it: `tally()` on repeated message ids; the matching rule (S's own path preferred, the `[Workflow harness — user request]` message skipped, another given store's path ruled out, the started/finished window, a single remaining candidate taken); and `gate_failures()` for a failure fixed later, a failure never fixed, and an input with no "Gate commands" line (returns None).
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes.

Interim tests: none
Tests to change: none
Protected paths: `factory/cost.py`
Out of scope: `factory/stats.py`, the `stats` subcommand and every `factory/cli.py` change (ST-2); every document, including the changelog entry that names #61 (ST-3). Do not change the `python -m factory.cost` header or columns.

---

## ST-2 / Add `factory stats` and exempt it from the instance lookup, the live-store fence and the harness lock
Depends on: ST-1
Parallel-safe: no (depends on ST-1's functions; ST-3 depends on this command)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B (`factory/stats.py`, a new file: `report()`, the module constants `CHANGED`, `BLOCKING` and `PARK_RULES`, and sections A to D in the spec's exact headings, column orders and row orders), part C (the `stats` subparser, `stats_cmd`, refusals that raise `Refused` and exit 2, handling `stats` before `instance.require()`, the fence and `instance.guard()` in `main()`, `("stats", None)` added to `READ_ONLY`, and the `fence()` and `main()` comments), and part D's `tests/factory/test_stats.py`. Every rule under the spec's Decisions applies here: store resolution and `FACTORY_STATE`, the window, the row order, the definition of runs and kills, changed outcomes, BLOCKING lines, park normalisation and corrections, section B's rows, section C's attribution, the cost source, and the transcript matching (through ST-1's `match_transcripts`, `transcript_usage` and `gate_failures`).

Acceptance (run each scenario's fixture GIVEN block once first, as the spec writes it; each WHEN runs in a subshell through the briefing's wrapper):
- NEW. "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures". WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' $F/out | grep '^| [a-z]' | grep -v '^| role |')` THEN it prints exactly the eight lines the spec gives, starting `exit=0` and ending `| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |`.
- NEW. "A window bounds the count and the command writes nothing". WHEN the spec's command (`bin/factory stats --store $F/s1 --since 2026-10-03 --transcripts $F/tx` with the before-and-after `cksum` of `$F`) THEN it prints exactly `exit=0 store=unchanged since=1`.
- NEW. "Parks are grouped by normalised reason, with gate and merge decisions". WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## B\./,/^## C\./p' $F/out | grep '^| ' | grep -vE '^\| (park reason|gate or merge decision) \|')` THEN it prints exactly the seventeen lines the spec gives, from `exit=0` through `| archive refused | 2 |`.
- NEW. "Each downstream spec catch names the runs that wrote and critiqued its spec". WHEN the spec's section C command THEN it prints exactly `exit=0`, `| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |`, `| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |`, `| yes | 1 | 1 |`, `| no | 1 | 0 |`.
- NEW. "Cost comes from the run record, else the transcript of that store's run, counted once per call". WHEN the spec's section D command (with `--transcripts $F/tx --until 2026-10-08`) THEN it prints exactly the eight lines the spec gives, from `exit=0` through `| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`.
- NEW. "Stats reproduces the hand count on the two live stores". WHEN `(bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 > ${TMPDIR:-/tmp}/t0043-live.txt 2>&1; echo "exit=$?"; ...)` as the spec writes it THEN it prints exactly the eight lines the spec gives, from `exit=0` through `| all parks | 82 |`. This reads both live stores and writes only under the temporary directory. A mismatch is checked against the stores first, as the scenario says.
- NEW. "Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing". GIVEN live-store-guard's `t0024-inflight.sh` block, run once. WHEN the spec's command (the lock overwritten to `0000…`, `stats` run from the target and from `$W`, then `ticket show`) THEN it prints exactly `here=0 inside=0 store=unchanged own=1 locked=2`.
- REGRESSION. "Unmarked writes from inside the target are refused while a run is in flight, init included". WHEN the spec's command THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`.
- REGRESSION. "The refusal names the throwaway store and not the marker". WHEN the spec's command THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`.
- REGRESSION. "A harness acceptance is refused while a run is in flight". WHEN the spec's command THEN it prints exactly `accept=2 store=unchanged`.
- REGRESSION (made true by ST-1). "The transcript cost report counts each message once": WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')` THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`.
- NEW (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_stats.py` THEN it passes. The file covers what part D lists for it: each section's rows on a fixture like the acceptance fixture; the window; each normalisation rule; the correction rule (a matching correction, one dated after `--until`, one whose `previous` matches no park); the refusals (no store found, a path with neither `runs/` nor `log/`, an unparsable WHEN); and a run on an instance's own store with a run in flight, from inside the store's `runs/`, under a lock that names another revision, built the way `tests/factory/test_live_store_guard.py` builds one.
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes, `tests/factory/test_cost_once.py` from ST-1 included.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/stats.py`
Out of scope: any change to `factory/cost.py` beyond calling ST-1's functions. If one of them has to change, report it as a gap rather than editing it here. Also out of scope: every document (README, `docs/design.md`, `docs/principles.md`, `dev/build-harness.spec.md`, `docs/changelog.md`), which ST-3 changes; a JSON output; the fence and lock behaviour of every other command; and the loose wording of live-store-guard's second requirement (the spec's Out-of-scope observations). README will not mention `stats` until ST-3 merges. The spec's split puts that page change in ST-3.

---

## ST-3 / Record `factory stats` in README, the design, the principles, the build spec and the changelog
Depends on: ST-2
Parallel-safe: no (its design-doc figures are printed by ST-2's command)

Parent: T-0043, spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0043/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E, all of it.
- `README.md`: the read-only list in "Where a human decides", the sentence in "Accepting a harness revision", the new `### Counting what each role catches and costs` subsection, the "What depends on Claude Code" row, the **Built** bullet and the status date. Read its "Maintaining this page" section first.
- `docs/design.md`: the fence paragraph's read-only list, the role-context paragraph's lock clause, and the model-per-role paragraph's citation of `factory stats`, with the figures it prints over both stores with `--until 2026-10-07T12:00 --transcripts <transcripts dir>`. The §8 prompt block is unchanged.
- `docs/principles.md` §4: 3 BLOCKING findings in place of 1; the "Implemented by:" and "Planned:" lines.
- `dev/build-harness.spec.md`: the `**`factory stats`**` paragraph after the `**`factory drive`**` paragraph.
- `docs/changelog.md`: entry 70, in the form of entries 66 to 69.

Acceptance:
- NEW. "The documents record factory stats". WHEN the spec's command (the `y()`/`j()` greps over README.md, docs/design.md, docs/principles.md and dev/build-harness.spec.md, the changelog numbering `awk`, the last entry's `#70`/`#61`/`factory stats`/`message id` count, and `git diff --check main...HEAD`) THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no buildspec=yes prompts=0`, then `CONTIGUOUS`, then `4`, then `clean`.
- REGRESSION (made true by ST-2). "Stats reproduces the hand count on the two live stores": the spec's command and its eight THEN lines, unchanged. It confirms that the command whose figures the design doc quotes still prints them.
- REGRESSION (intermediate check). WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory` THEN the whole suite passes.

Interim tests: none
Tests to change: none
Protected paths: none
Out of scope: any code or test change; any file under `docs/prompts/` or `factory/prompts/`, including the §8 retro block and its copy; feeding the figures into the retro's input (issue #42); restating figures quoted from `factory/cost.py` before this change, such as changelog entries 58 and 67.

---

## Coverage map: parent scenario → sub-ticket ID

| Parent scenario | Sub-ticket |
|---|---|
| Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures | ST-2 |
| A window bounds the count and the command writes nothing | ST-2 |
| Parks are grouped by normalised reason, with gate and merge decisions | ST-2 |
| Each downstream spec catch names the runs that wrote and critiqued its spec | ST-2 |
| Cost comes from the run record, else the transcript of that store's run, counted once per call | ST-2 |
| The transcript cost report counts each message once | ST-1 (rechecked as REGRESSION in ST-2) |
| Stats reproduces the hand count on the two live stores | ST-2 (rechecked as REGRESSION in ST-3) |
| Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing | ST-2 |
| Unmarked writes from inside the target are refused while a run is in flight, init included | ST-2 (REGRESSION) |
| The refusal names the throwaway store and not the marker | ST-2 (REGRESSION) |
| A harness acceptance is refused while a run is in flight | ST-2 (REGRESSION) |
| The documents record factory stats | ST-3 |

Every parent scenario maps to a sub-ticket. Parts A, B, C, D and E are each covered: A by ST-1; B and C by ST-2; D split as the spec splits it (`test_cost_once.py` in ST-1, `test_stats.py` in ST-2); E by ST-3.

## Out-of-scope observations

- ST-3's design-doc figures for section D depend on which transcripts exist on the machine that runs the command, because cost from a run with no cost record comes only from its transcript. Under the briefing's wrapper, `HOME` is a throwaway directory, so `~/.claude/projects` inside the wrapped command does not reach the operator's transcripts. The ST-3 implementer has to give the transcript directory as an absolute path (`/Users/dphang/.claude/projects`), which the command only reads. The acceptance check for the docs tests only that the paragraph names `factory stats`, not its figures, so the reviewer of ST-3 is the check on those numbers.
- The live-store scenario reads `/Users/dphang/dev/nanobot-upstream/.factory/store`, which lies under a protected path (`reference_harness`). It only reads, as the spec states. No sub-ticket writes there.

STATUS: PLANNED
CONFIDENCE: high, the spec names its seams, scenario ownership and test files, and each fact this plan relies on was checked on `main` at `5215c5f`.
ESCALATIONS: none
