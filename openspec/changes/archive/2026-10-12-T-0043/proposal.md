## Problem

The operator cannot see which of the factory's checks pay for themselves, or what each one costs. The records that would show it are already kept, but nothing reads them as a whole, and the one cost report the factory has counts most tokens about twice.

Some terms. The factory turns a written request into merged code through a chain of AI agents. Each request is a ticket. Each step on a ticket is a role run: one agent doing one job, such as triage (accepting the request), writing the spec (the design the code must meet), critiquing the spec, implementing it, reviewing the code or verifying it by running its checks. Every run ends with a verdict on a `STATUS:` line. Some verdicts change what happens next: the critic's REVISE sends a spec back, the code reviewer's REQUEST-CHANGES sends code back, the verifier's SPEC-DEFECT or FAILED stops a merge, and the implementer's BLOCKED says the spec cannot be built as written. A finding marked BLOCKING is one the critic or reviewer says must be fixed. A park sets a ticket aside for a human, with a one-line reason. The store is the factory's record for one target repository, kept as plain files: each run's record (its role, model, verdict and wall time), each run's output, and an append-only event log. Since 2026-10-10 a run started by `factory drive` (the command that runs a ticket's roles one after another) also records its token use and dollar cost. Earlier runs have that only in their transcript, the log file Claude Code keeps for each agent session outside the store.

Counting these records takes a hand-written script today. One such count over both stores, made on 2026-10-07, found that the code reviewer, which runs on the most expensive model, changed an outcome 4 times in 94 runs, and that 30 of 82 parks were triage asking a human. The operator decides from figures like these which model each role runs and whether a check is worth its cost. The design's model-per-role table says a change to it needs that evidence. The existing token report, `factory/cost.py`, counts most model calls about twice (1.9 times over both stores), because a transcript repeats one call's usage once for each block the reply streamed.

This change adds `factory stats`, a command that reads one or more stores, writes nothing, and prints four tables:
- runs and verdicts by role and model, with the verdicts that changed an outcome, BLOCKING findings, runs killed for running out of budget, and the check commands an implementer saw fail and then fixed before handing off;
- parks by reason, with the human decisions at the spec gate (where the operator approves a spec) and the merge refusals;
- each spec defect caught downstream, against the run that wrote that spec and the run that critiqued it;
- each role's wall time and tokens, taken from the run's cost record or else its transcript, counting each model call once.

It also fixes the double count in `factory/cost.py`. It serves the operator. It will also serve the retro, a planned role that proposes changes to the agents' rules from failure rates, which is built after this change and reads the same figures.

## Evidence

All commands were run from `~/dev/spec-factory` at `main` `5215c5f`, through the briefing's wrapper: a shell prefix that runs each command with a fresh, empty home directory, so a check cannot write the operator's real files. The figures for the two live stores come from throwaway prototypes of the rules under Decisions. They ran on this repository's store, `.factory/store`, and on the Nanobot target's store, `~/dev/nanobot-upstream/.factory/store`.
- Round 1's prototype (about 170 lines) covered all four sections and the transcripts. The harness removed it with that run's scratch directory.
- This round's prototype, `scratch/p.py` in this run's directory, covers section A without the gate column and section B, including the park-correction rule below. On 2026-10-11 it printed the same live-store rows as round 1 (the A rows and the two park rows below), and every fixture row of sections A (gate column aside) and B that the scenarios state.

- The request's figures reproduce exactly when runs that were killed are left out and the count stops between 2026-10-07 05:48:28 and 14:50:20 UTC. With `--until 2026-10-07T12:00` the prototype prints these rows. The columns are role, model, runs, killed, changed outcome, verdicts, BLOCKING findings, and fixed gate failures:
  - `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`. This matches the request's 94 runs, 4 changed outcomes (3 REQUEST-CHANGES, 1 ESCALATE) and 5 budget kills.
  - `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`. This matches 84 runs and 19 REVISE.
  - `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 0 read, 111 not recorded |`. This matches 111 runs and 18 BLOCKED.
  - `| verifier | opus | 108 | 0 | 8 | FAILED 4, SPEC-DEFECT 4, VERIFIED 100 | - | - |` and `| verifier | fable | 5 | 0 | 1 | SPEC-DEFECT 1, VERIFIED 4 | - | - |`. The request's "Verifier (Opus) 108 runs, 9 changed (5 SPEC-DEFECT, 4 FAILED)" took its run count from the Opus row and its outcomes from both rows. The command keeps the two models apart.
  - Parks: `| NEEDS-HUMAN from triage | 30 |` and `| all parks | 82 |`, matching the request.
- One of the request's figures does not reproduce. Its "1 BLOCKING finding in total" for the reviewer is 3 under the counting rule in Decisions. The 3 lines are in the 3 REQUEST-CHANGES runs, and the reviewer's prompt requires at least one BLOCKING finding for that verdict (`factory/prompts/reviewer.md:62`), so 1 cannot be right. Three more `[BLOCKING]` lines are round-2 restatements marked RESOLVED, and the rule leaves them out. The script behind the request's figures is not attached to the request. I could not find it, so I cannot say which rule it used. The same "1 BLOCKING finding" appears in `docs/principles.md:59-60`.
- Data sources, checked by reading the stores:
  - Each run's `meta.yaml` records `role`, `model`, `status`, `started`, `finished`, `wall_s` and `spec_version`, as in `.factory/store/runs/run-0429-reviewer/meta.yaml`.
  - The log records parks (`ticket.parked`, with a free-text `reason`), spec approvals (`approval.recorded`, `kind: spec`), human resolutions (`human.resolved`, with a `kind`), merge refusals (`merge.refused`, with a `reason`) and which run wrote each spec version (`spec.added`, with `source`).
  - Ten `spec.added` events in this store name a source that is not a run. Nine name a gate edit, such as `"source": "gate edit /Users/dphang/dev/spec-factory/intake/answers/T-0012-gate-edit.md"`, and one an amendment (`"source": "amend /private/tmp/..."`, T-0040 version 4).
  - A human can correct a park's reason after the fact. This store has one `park.corrected` event, on T-0040.3 at 2026-10-10 17:18 UTC (log line 2158). It carries `previous`, the reason the park was recorded with (`harness-bug: run start implementer: BLOCKED from harness: spec drift: ...`), `reason`, the corrected text (`BLOCKED from harness: spec drift: ...`), and `why`. No code writes the event: `grep -rIn park.corrected factory bin tests` finds nothing, so the operator wrote it by hand. The Nanobot store has none.
  - Cost records (`claude:` in `meta.yaml`) exist for 14 runs, all in the Nanobot store and none in this one. An example is `run-0413-spec_writer`: `total_cost_usd: 5.685489`, `usage: {input_tokens: 122, cache_creation_input_tokens: 178311, cache_read_input_tokens: 13781545, output_tokens: 74126}`.
- The double count. `factory/cost.py` `tally()` (lines 47-71) adds the usage of every transcript record that carries one, with no check on the message id.
  - Over the transcripts the prototype matched to runs, adding every record gives 2,016,972,806 context tokens for the Nanobot store against 1,069,416,588 when each message id is counted once (1.89 times). For this store it gives 1,604,833,468 against 828,079,342 (1.94 times). The double-count report (issue #61) estimated about 2.05 times. I measured 1.89 and 1.94.
  - Counting each id once, from its last record, matches the cost record exactly. The transcript of `run-0413-spec_writer` (Nanobot store, session `4730aa67-…`) has 109 records with usage for 61 message ids. Once per id, that is 13,959,978 context tokens and 74,126 output tokens, which equals its cost record (122 + 178,311 + 13,781,545, and 74,126).
- Finding transcripts. Claude Code keeps them under `~/.claude/projects`: 7,806 `.jsonl` files on this machine.
  - The rule under Decisions matched a transcript to 630 of the 631 runs in both stores up to the cut. The one left without a transcript is an implementer run. Scanning the directory took about 12 seconds.
  - The rule must allow for old paths. This store's earliest runs named its pre-2026-10-04 path, `/Users/dphang/dev/spec-factory/intake/state/runs/...`, which no record in the store gives. Both stores also record a move from `.factory/state` in a `store.migrated` event.
  - The rule must keep the stores apart. Run ids repeat across stores: both have a `run-0355-implementer`, with overlapping times. Taking the path the prompt names first avoids the mix-up.
- With transcripts, the prototype's cost table for the same cut gives these totals:
  - spec writer: 591,000,935 context tokens over 92 runs;
  - implementer: 372,507,821 over 114;
  - verifier on Opus: 232,945,610 over 108;
  - code reviewer: 94,860,442 over 99.

  The code reviewer therefore costs about 95M context tokens for its 4 changed outcomes.
- Implementer check failures fixed before hand-off. The implementer's output records only its final check results (`factory/prompts/implementer.md:57-66`). The transcript records every call.
  - Each implementer's `input.md` lists its check commands, the gate commands, on one line, such as `.factory/store/runs/run-0427-implementer/input.md:64`.
  - Matching those commands against the transcript's Bash calls finds 0 failures fixed before hand-off in the 111 implementer runs up to the cut. Over all records it finds 2, both in the Nanobot store after the cut. One is `run-0384-implementer`, whose `tests/cli/test_commands.py` gate failed with `Exit code 1` and then passed.
- Previewing the critic question (does a REVISE predict trouble downstream?): up to the cut, 52 tickets had a spec approved. 16 of them had a critic REVISE, and 4 of them later had a SPEC-DEFECT or a BLOCKED implementer. 36 had none, and 7 of them later had a catch.
- Behaviour on `main` today:
  - `bin/factory stats --store x` prints `factory: error: argument cmd: invalid choice: 'stats' (choose from ticket, run, spec, plan, subticket, results, merge, init, store, paths, archive, approve-spec, request-changes, resolve, decision, drive, config, status, log)` and exits 2.
  - The fence lets a command through during a run only if it is in `READ_ONLY` (`factory/cli.py:1939-1940`).
  - The harness lock covers every command except `init` and `paths` (`factory/cli.py:1972`, `factory/instance.py` `guard()`). So a read run from any checkout other than the accepted runtime is refused on an instance's own store.
- Every NEW scenario under verification.md was run on `main`, and its output there is given with it.
- Capabilities I read in full: `openspec/specs/live-store-guard/spec.md` (its first requirement is restated below), `openspec/specs/harness-docs/spec.md` and `openspec/specs/build-dispatch/spec.md` ("A role process's reply is recorded with its run", the source of the cost records).

## Root cause

- No command reads the store as a whole. `factory/cli.py` `build_parser()` (lines 1753-1934) has no `stats` subparser.
- `factory/cost.py` `tally()` (lines 47-71) adds `usage` from every transcript record that has it. Claude Code writes one record for each streamed block of a reply, and each carries the whole call's usage, so a call is counted once per block.
- `factory/cli.py` `main()` (lines 1969-1985) puts every command except `init` and `paths` through the instance lookup, the fence and the harness lock.

## Out of scope

- Feeding these figures into the retro's input. The retro role does not exist yet. The operator decided on 2026-10-11 that the retro is built after this change and reads from it, so the request's "the retro's input.md contains the stats section" moves to that work (issue #42).
- The retro's prompt block in `docs/design.md` §8 and its copy `docs/prompts/08-retro.md`. The block already asks for per-role run and outcome counts by model, and no prompt file changes.
- Post-merge reverts. No store records them, and a revert event is a separate ticket if wanted.
- Acting on the figures: the reviewer trial (issue #64), detecting a stuck run, and a trained critic.
- A JSON output. Cut: no consumer needs one yet. The REVISE question (issue #94) is answered by a table this change prints, and the retro can call the module directly.
- Breaking BLOCKING findings down by rubric item, as the request's "14 of 16 were rubric 6" does. Cut: the command is not asked for it.
- Any change to what runs, records or the log store. Cost from transcripts that Claude Code has already deleted is reported as missing, not estimated.
- Every other command's place in the fence and the harness lock.

## Open questions

none

## Decisions

- The command is `factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...`.
  - With no `--store`, it reads the store of the instance found from the caller's directory. As other commands do, it honours `FACTORY_STATE`, the environment variable that points a command at another store (tests use it to point at a throwaway one). With neither, it is refused with exit 2. A `--store` path with neither `runs/` nor `log/` is refused with exit 2.
- `--until` is added beyond the request, so that a past figure can be reproduced on a store that keeps growing.
  - WHEN is an ISO date or date-time, taken as UTC when it has no zone. `--since` is inclusive and `--until` exclusive.
  - Runs are windowed by `started` and events by `ts`. Looking up who wrote and who critiqued a spec ignores the window.
- The output is Markdown with fixed section headings and column orders, given in design.md part B. Rejected: JSON (Out of scope).
- `stats` is handled like `paths`: no instance needed, no live-store fence (the guard against role runs writing the store), no harness lock check, and `--accept-harness` ignored.
  - Why: it writes nothing, and it must read a live store while runs are in flight and from a checkout the instance has not accepted, such as a verifier's.
  - The fence's read-only list in the documents gains `stats`. This follows the standing 2026-10-04 rule that a new command is fenced until it is added to that list.
  - Rejected: adding it only to `READ_ONLY`, as triage assumed. The lock would still refuse it everywhere but the accepted runtime.
- The rows are keyed by role and model, summed over every store given, and ordered triage, spec_writer, critic, planner, implementer, reviewer, verifier, then any other role by name, and models by name within a role.
- A row's "runs" counts runs with a verdict other than `KILLED`. `KILLED` runs have their own column, and runs still in flight (status `running` or none) are left out. This is how the request counted (94 reviewer runs plus 5 killed).
- A changed outcome is a verdict of `REQUEST-CHANGES`, `ESCALATE`, `FAILED`, `SPEC-DEFECT`, `REVISE` or `BLOCKED`, from any role. This is the request's list.
- BLOCKING findings are counted for the reviewer and the critic only. A finding is a line of `output.md` that starts with `[BLOCKING]`, after optional leading spaces and an optional `-`, `*` or `1.` marker, and that does not contain `RESOLVED`.
  - Rejected: counting every mention of the word, which counts "No BLOCKING findings".
  - Rejected: counting round-2 restatements of a fixed finding.
- Park reasons are normalised by a fixed list in the module, extended when a new reason appears. The steps are:
  1. take the first line;
  2. replace run ids with `<run>`, ticket ids with `<ticket>`, and 7-to-40-character hex strings that contain a letter with `<sha>`;
  3. keep the first two `: `-separated fields;
  4. trim, and drop a trailing colon.
- A park counts under its corrected reason. A `park.corrected` event replaces the reason of the latest earlier `ticket.parked` event of the same ticket whose reason equals the correction's `previous`. A correction that matches no park changes nothing.
  - Only corrections dated before `--until` apply, so a past figure stays repeatable after a later correction. The park itself is windowed by its own `ts`.
  - Why: the operator corrects a reason because the recorded one was wrong, as on T-0040.3, where a refusal was mis-filed as a harness bug. Counting the original would report the error the human fixed.
  - Rejected: ignoring corrections. Rejected: applying every correction whatever its date, which lets a later correction move a figure quoted for a past cut.
- Section B's decision rows are:
  - `spec approved`: `approval.recorded` events with `kind: spec`;
  - `spec changes requested`: `human.resolved` events with `kind: request-changes`;
  - one `resolved: <kind>` row per other `human.resolved` kind;
  - one `merge refused: <reason>` row per `merge.refused` reason (`head does not contain main` is the conflict case);
  - `archive refused`: parks whose normalised reason is `archive` or starts with `archive:`.
- Section C is built as follows:
  - Each catch is a verifier run with `SPEC-DEFECT` or an implementer run with `BLOCKED`.
  - Its spec is the parent ticket's (the ticket id without a trailing `.N`) at the run's `spec_version`.
  - "Written by" is that version's `spec.added` source when the source is a run id. It is `human` when the source is anything else (a gate edit or an amendment), and `unknown` when the version has no `spec.added` event.
  - "Critiqued by" is the latest critic run of the parent at that `spec_version`, or `none`.
  - The REVISE count is all critic REVISE runs of the parent.
  - A second table splits approved tickets by whether they had a REVISE and counts those with a later catch. This answers the REVISE question with no further tool.
- Cost per run comes from the run's cost record (`claude.usage`, `claude.total_cost_usd`) when present, else from its transcript, else nothing. Each row names how many runs used each source. This is the owner's proposal.
  - Context tokens are input + cache-read + cache-creation tokens, the definition `factory/cost.py` already uses.
  - Dollars come only from cost records, because transcripts carry none.
  - Killed runs count, because they spent tokens.
- Transcripts are searched only under the `--transcripts` directories, for every `*.jsonl` file at any depth.
  - Rejected: searching `~/.claude/projects` by default. That ties the command to one machine's layout and costs about 12 seconds on every call.
- A transcript is matched to a run R of a store S as follows:
  - Its first user message that names a run directory, `<P>/runs/<R>/`, gives the candidate. A user message is skipped when it starts with `[Workflow harness — user request]`, which relays the operator's words.
  - The transcript's first timestamp must lie between R's `started` and `finished`.
  - A P that is the path of another store given on the command line rules the transcript out.
  - A candidate whose P is S's path, or S's path before a `store.migrated` event, wins. Otherwise a single remaining candidate is taken. Otherwise there is none.
  - Rejected: requiring S's path. That loses every run from before an unrecorded move (this store's first 103).
- Usage counts each message id once, taking its last record. A record with no id counts alone. The `calls` column of `factory/cost.py` then counts message ids. This fix applies to `factory/cost.py` itself and absorbs issue #61, the report of the double count.
- Implementer gate failures fixed before hand-off are read from the transcript.
  - The gate commands are the backticked commands on the "Gate commands" line of the run's `input.md`. Each is matched by its own text: what follows the wrapper's last `; `, with the closing `)` removed.
  - A gate counts once per run when a Bash call containing it returned an error (`is_error: true`) and a later call returned none.
  - A run with no transcript or no gate line is "not recorded", not zero.
  - Rejected: the implementer's output, which states only the final results.
  - The text match can miss a command the implementer ran in another form. That is a known limit, stated in README.
- `docs/design.md`'s model-per-role paragraph cites `factory stats` and the reviewer, critic, verifier and implementer figures from sections A and D, for `--until 2026-10-07T12:00` with `--transcripts`. This is part E of the request. Its retro half moves to the retro's own issue, #42 (Out of scope).
- `docs/principles.md` §4 gets the command's figure, 3 BLOCKING findings, in place of 1 (Evidence), and its "Implemented by" line names `factory stats`.

## Risk

Blast radius:
- `factory/cost.py`'s output roughly halves for the same transcripts. Figures quoted from it before this change, such as changelog entries 58 and 67, stay as history and are not restated.
- `factory stats` runs under any harness revision and on a live store. A defect in it can print a wrong figure or fail, but it cannot write. The command opens files only for reading, and scenario "Stats reads a live store with a run in flight and an unaccepted harness, and writes nothing" checks the store.
- A wrong park normalisation misleads the operator. The fixture's reasons cover each rule, and its two corrections cover the correction rule (one applied, one dated after `--until`).
- Every other command's fence and lock behaviour is unchanged. The three restated live-store-guard scenarios check that.

Protected paths: `factory/cli.py`, `factory/cost.py`, `factory/stats.py`

## Operator steps

none
