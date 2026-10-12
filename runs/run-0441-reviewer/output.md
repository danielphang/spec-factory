Commit: 41417c1789d40b26370b10f2bdcae6a84f903a9d (branch `factory/T-0043.2`, base `a0f77c9ffdb638dfcb77ec1dde702a861e6796d4`)

## What I checked

Read the whole diff (`factory/cli.py` +45/-3, `factory/stats.py` new 235 lines, `tests/factory/test_stats.py` new 426 lines; `git diff --stat` on the worktree) against sub-ticket T-0043.2 and spec v2 parts B, C and D and every rule under Decisions. Read ST-1's functions as they stand on this head (`factory/cost.py:33` `_records`, `:64` `transcript_usage`, `:100` `_when`, `:154` `match_transcripts`, `:189` `gate_failures`), `factory/instance.py:41-104` and `factory/cli.py:2006-2030` (`main()`), and the fixtures the new test imports (`tests/factory/test_live_store_guard.py:24-46`, `tests/factory/test_instance.py:19-48`). Did not run the suite or the gate commands.

1. Test integrity. No existing test file is in the diff (`git diff --stat` lists only the three files above). `tests/factory/test_stats.py` imports fixtures from `test_instance.py` and `test_live_store_guard.py` and changes neither. The sub-ticket's "Tests to change: none" holds.

2. Correctness, against each Decision:
   - Store resolution (`factory/cli.py:1629-1651`): `--store` paths resolve from `instance.caller_cwd()`; with none, `FACTORY_STATE` (`instance.env_path`, which also resolves a relative value from the caller's directory) then the instance's `state_root`; no store and a path with neither `runs/` nor `log/` raise `Refused`; `main()`'s `except Refused` (`cli.py:2024-2027`) prints the error and the `{"ok": false}` JSON and returns 2. `parse_when` (`stats.py:42-47`) wraps `cost._when`, which takes a date or date-time and adds UTC when there is no zone, and turns `ValueError` into `Refused`.
   - Window (`stats.py:113-114`): `since` inclusive, `until` exclusive, runs by `_started`, events by `_ts`; a run with no `started` has `_started=None` and is left out.
   - Runs, kills, in flight (`stats.py:38`, `:118-119`, `:133-134`): `status` `None` or `running` left out; `KILLED` counted in its own column and excluded from `runs`; section D counts both (`:213`).
   - Changed outcomes (`stats.py:28`): the six verdicts, any role.
   - BLOCKING (`stats.py:30`, `:85-90`): `^\s*(?:[-*]|1\.)?\s*\[BLOCKING\]`, `RESOLVED` excluded, reviewer and critic rows only.
   - Park normalisation (`stats.py:50-55`): first line, the three id rules in order, first two `: ` fields, strip, trailing colon dropped. `"archive: "` normalises to `archive` and the `archive refused` row counts `archive` and `archive:` prefixes (`:163`).
   - Corrections (`stats.py:93-103`): applied in `ts` order, only when dated before `until`, to the latest earlier park of the same ticket whose current reason equals `previous`; no match changes nothing.
   - Section B rows and order (`stats.py:155-168`), section C's catch definition, parent-ticket rule, `human`/`unknown` writer, latest critic of that version, REVISE count over the parent, and the yes/no split over tickets with an approval in the window (`:171-205`), section D's record-then-transcript-then-none source with the `cost.py` context definition (`:208-234`): each matches the spec's text and the headings, column orders and row orders of part B.
   - `READ_ONLY` gains `("stats", None)` (`cli.py:1976-1977`); `main()` runs `stats` with `init` and `paths` before `instance.require()`, the fence and `instance.guard()` (`cli.py:2011-2013`), so `--accept-harness` is ignored. The `fence()` and `main()` comments are updated.
   - Edge cases the spec implies: a run id source is matched with `fullmatch` so a gate-edit path that mentions a run id still reads `human` (`stats.py:187`); `_table` quotes nothing, so a reason containing `|` would break a row (the PR's Known gaps say so; no such reason exists today).

3. Scope. Every hunk is part B, part C or part D's `test_stats.py`. `factory/cost.py` is untouched (`git diff --stat`). No document changes.

4. Silent behaviour changes. None for other commands: the only `main()` change is the added `"stats"` in the pre-instance tuple, and `READ_ONLY` gains a key that `main()` never reaches for `stats` (the comment at `cli.py:1973-1974` says so). The `stats` subparser gets `help=` text where the other subparsers have none; harmless.

5. Security and data safety. `stats.py` opens files for reading only (`glob`, `read_yaml`, `open(..., encoding=)` with the default mode); no subprocess, no write, no path from an untrusted source other than the operator's own arguments.

6. Protected paths. `factory/cli.py` and `factory/stats.py` are touched; both are declared by the sub-ticket and by the spec's Risk section. Listed under ESCALATIONS for the record.

7. Coding standard. Rule 1: `ROLES`, `Refused`, `read_yaml` and all five ST-1 functions are reused; no Markdown-table helper exists in the repo (`cost.py:236` prints a literal), so `_table` is the first rung that holds; the context-token sum repeated from `transcript_usage` is noted in Known gaps and `cost.py` is out of scope here, so it is not a `reuse:` finding. Rule 3: the PR says "factory: markers added: none", and I see no undeclared shortcut. Rule 5: the identifiers (`parks`, `catches`, `CHANGED`, `BLOCKING`, `PARK_RULES`) are the spec's names. Rule 6: the tests patch nothing and write only under `tmp_path`. Lean already.

8. PR description. See the SHOULD-FIX below.

## Findings

- [SHOULD-FIX] PR description: What changed: the first paragraph uses "harness lock", "live-store fence", "instance lookup" and "a run in flight" without saying what each is; the writing standard (rule 2) asks for a gloss at first use → the operator at the gate, new to this project, cannot tell from the description what checks the command skips or why skipping them is safe. One sentence each would do: the fence refuses writes to a store while an agent run is in progress there; the lock makes an instance run only the harness commit it has accepted; `stats` skips both because it only reads.
- [NIT] factory/stats.py:69: `_load` raises on a `meta.yaml` whose `started` does not parse or that YAML reads as a non-mapping, so one bad record exits the whole command with 1 → on a live store with a run being started, a half-written record could fail a report that the spec says must run while runs are in flight. The PR's Known gaps declare the `ValueError` case and both live stores parse today, so this is not blocking.

net: Lean already.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every Decision was checked against the lines that implement it, the ST-1 functions it calls were read on this head, and no existing test or out-of-scope file is in the diff; the two findings are a description gloss and an edge case the implementer already declared.
ESCALATIONS: Protected paths `factory/cli.py` and `factory/stats.py` are touched; both are declared by sub-ticket T-0043.2 and by spec v2's Risk section, so this is for the record and the merge gate needs no further approval.
