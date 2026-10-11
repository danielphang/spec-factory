Type: feature

Title: `factory stats`: a read-only report, built from the store, of how often each role changes an outcome, what each role costs, and where tickets stop

Summary:
The operator cannot see which checks pay for themselves. Each check is a role run, such as the code reviewer or the verifier, and the counts that would show its worth already sit in the store. The store is the factory's record of tickets, runs and events. Counting them today takes a hand-written script, and the requester's script found that the code reviewer changed an outcome 4 times in 94 runs. The requester wants a read-only `factory stats [--since DATE] [--store PATH ...]` command. It reads the store log, each run's `meta.yaml` and `output.md`, and each run's cost record, and reports five things:
- A: runs and verdicts per role and per model. This includes the verdicts that change an outcome, BLOCKING findings and budget kills. It also counts the gate commands each implementer saw fail and fixed before it handed off.
- B: parks grouped by reason, after a fixed list of regexes strips run ids and ticket ids. A park is a ticket stopped for a human. B also counts gate approvals against request-changes, conflicts and archive refusals.
- C: each SPEC-DEFECT and each BLOCKED implementer counted against the run that wrote the spec and the run that critiqued it.
- D: context tokens and wall time per role, beside A. Each message id is counted once.
- E: the stats become the evidence the design doc's model-per-role table cites, and later the retro's input.
The command writes nothing and refuses nothing.

Evidence:
- The request's table (2026-10-07, both stores, every run on record): code reviewer 94 runs and 4 changed outcomes; verifier 108 runs and 9 (5 SPEC-DEFECT, 4 FAILED); spec critic 84 runs and 19 REVISE; implementer 111 runs and 18 BLOCKED; 82 parks, 30 of them NEEDS-HUMAN from triage. The requester says the script that produced these figures "should become the command". That script is not attached to the request, and I did not find it.
- The data is there. I counted the event types in this repo's store log, `.factory/store/log/2026-10.jsonl`. It has 431 `run.started`, 424 `run.finished`, 53 `ticket.parked`, 66 `human.resolved`, 8 `merge.refused` and 6 `run.killed` events. Park events carry a free-text `reason`, for example `"reason": "NEEDS-HUMAN from triage"` (line 17).
- Each run's `meta.yaml` records `role`, `model`, `status`, `wall_s` and `round`. Example: `.factory/store/runs/run-0429-reviewer/meta.yaml`.
- Since #65 (T-0040, the driver), each run also keeps `reply.json`. `run finish --reply` keeps `session_id`, `total_cost_usd`, `num_turns` and `usage` from it (`factory/cli.py:504-514`, `factory/drive.py:7`).
- The #61 double count, absorbed into this ticket. `factory/cost.py` `tally()` (lines 47-71) adds the usage of every transcript record that carries usage, with no check on message id. Streamed blocks that repeat one call's usage are therefore counted again. I read the code. I did not measure the 2.05× factor the owner cites.
- No `stats` subcommand exists today. I checked the `add_parser` list in `factory/cli.py:1758-1927`. No issue or ticket duplicates this one. `dev/issues.md` lists it as #70, and this ticket, T-0043, is that issue. #61 is merged into it, and #94 is listed as "after #70".
- Owner's notes (Green, 2026-10-07): cost from run records when present and from transcripts otherwise, with the output saying which source it used. A baseline caveat: #41 removed the suite run from the reviewer.
- Operator decisions of 2026-10-11: the retro (#42) is built after this ticket and consumes it. #94, whether a critic REVISE predicts trouble later on, should be an easy query on its output. The golden-set baseline (docs/golden.md, #80 part E) records calls, turns, tokens, suite runs, verdict, whether the verdict changed an outcome, and operator decisions asked for, per entry and role.
- Discussion: https://github.com/danielphang/spec-factory/discussions/69.

Capabilities: live-store-guard, build-dispatch, harness-docs

Assumptions (my inferences, not stated by the requester):
- live-store-guard: the command has to answer while a role run is in flight. The guard lets a command through only if it is in the `READ_ONLY` set (`factory/cli.py:1939`), so `stats` must join that set. Otherwise the guard refuses it on a live store, which breaks "refuses nothing".
- build-dispatch: part D reads the cost that "A role process's reply is recorded with its run" stores. I take the owner's proposal as the default: run records first, transcripts as the fallback, and the output names its source per row.
- Part E, retro half. No retro role exists in this repo: `factory/prompts/` has no retro prompt, and nothing under `factory/` refers to a retro. The 2026-10-11 decision builds the retro after this ticket. So I assume this ticket does not wire stats into a retro `input.md`. The request's acceptance line "the retro's input.md contains the stats section" moves to #42. Inside this ticket, E means the design doc changes. §8 Retro's INPUT already asks for "per-role run and outcome counts for the period, broken down by model". The doc names `factory stats` as their source, and the model-per-role paragraph (`docs/design.md:70`) cites the current A and D figures.
- The pre-hand-off gate failures added to part A have no structured field in the implementer's output. `factory/prompts/implementer.md` lines 57-66 give acceptance results but no record of gate failures. The spec writer must pick a source and say how reliable it is. The choices are the run's transcript (reachable through `session_id` since #65) or the free text. Runs that have neither are reported as not recorded, not as zero.
- "The two live stores" are this repo's `.factory/store` and `~/dev/nanobot-upstream/.factory/store`. Reading the second one through `--store PATH` is allowed, because the briefing permits reads there. Both stores have grown since 2026-10-07, so reproducing the Evidence figures needs a cut-off date. Either the command takes an `--until` that the request does not list, or the writer explains the difference. I take the request's "within the differences the writer explains" to allow either.
- Suggested priority (a suggestion, the call is the operator's): p1, matching `dev/issues.md` and the 2026-10-11 intake order, which puts this ticket first after #86.

Reason: the intent is clear and its decisions are already made: read-only, no model, regexes for park reasons, the cost source as the owner proposed, and the retro built afterwards as a consumer. The open points are design details the spec writer can settle and state. They are the source for implementer gate failures and how to bound the reproduction of the Evidence figures, and neither needs a product call.

STATUS: ACCEPT
CONFIDENCE: medium. The intent and the data sources are verified, but the retro-input acceptance line cannot run until #42 exists, and I moved it there by inference.
ESCALATIONS: none
