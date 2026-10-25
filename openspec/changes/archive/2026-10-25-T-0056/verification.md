## Acceptance
- The scorecard gives each instance's measures for the window and the window before, and writes nothing → NEW; today `stats` rejects `--scorecard` (argparse usage error), so it prints `exit=2 store=unchanged` and no heading or table line.
- The scorecard takes a run's tokens from its transcript when the run has no cost record → NEW; today it prints nothing (`--scorecard` is rejected).
- The scorecard refuses a missing --since and a malformed target_is_factory → NEW; today it prints `no-since=2 0 bad-setting=2 0 good=2`: every call is refused as an unknown argument, and neither message names `--since` or `target_is_factory`.
- Without --scorecard, stats prints sections A to D and no scorecard → REGRESSION; passes today.
- An escape is recorded against a merged change, its link kept only as a hash, and counted by the scorecard → NEW; today it prints `no-merge=2 sub-ticket=2 unknown=2 empty=2 link-note=2 refused-wrote=0 recorded=2 printed=0/0 link-in-store=0`, then `events=0 fields= hash=differ`, and no `Escapes` row: there is no `escape` command, so every call is an argparse usage error.
- An intervention recorded outside the CLI is counted by the scorecard → NEW; today it prints `unknown=2 recorded=2` and no row.
- run finish records the transcript's tokens for a run with no reply, and keeps a reply's record → NEW; today `run finish` rejects `--transcripts`, so it prints `finish=2 2`, then `none`, then a Python traceback (the second run never starts, because the first stays in flight), and no section D line.
- A run the intake script starts carries its transcript's tokens → NEW; today it prints `state=parked`, then `triage none`.
- A drive run whose claude process failed records its transcript's tokens → NEW; today it prints `state=parked`, then `triage KILLED none`.
- README and the instance template describe the scorecard, the two records and the token record → NEW; today it prints `scorecard=no setting=no escape=no hash=no intervene=no record=no old=yes depends=no pieces=no template=no`, then `built=long`.
- README is at most 1,225 lines → REGRESSION; passes today (1,184 lines), and the change keeps it within 1,225.
- README describes init's report of a differing agent copy → REGRESSION; passes today, unchanged by this change.
- The changelog records issue 108 in one entry without a numbering gap → REGRESSION; passes today, unchanged by this change.
- README stays within its line budget and both documents pass the whitespace check → REGRESSION; passes today at 1,225 (`readme=within`, `check=0`), and at the old 1,185 too.
- The README, the design doc and the changelog describe the launch copy and the route back to checks → REGRESSION; passes today at 1,225.
- README opens with the north-star paragraph and stays within its budget → REGRESSION; passes today at 1,225.
- The drift checks live in factory/drift.py → REGRESSION; passes today.
- The shared helpers and the live-store fence live in factory/common.py → REGRESSION; passes today.
- Instance and store setup live in factory/setup.py → REGRESSION; passes today.
- The gates live in factory/gates.py → REGRESSION; passes today.
- The human decisions live in factory/human.py → NEW; today it prints `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`, without `escape_add` and `intervention_add`.
- factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines → REGRESSION; passes today (880 lines).

## Responses

Round 3, on the critic's review of v2 (run-0569):
- [BLOCKING] 3, 5, seam marker: FIXED. design.md's bold paragraph is now the heading `### Size and seams (NEEDS-SPLIT, two sub-tickets)`, which `_planner_needed`'s heading check (`factory/cli.py:511-514`) matches: `SEAM_HEADING_RE` (`:496`) is `^#{2,3}\s` and the line contains "seams". This spec also now ends `STATUS: NEEDS-SPLIT`, the status the role prompt gives a spec over one reviewable PR. Both `factory/drive.py:291` and `factory/workflows/intake.js:187` send NEEDS-SPLIT to the critic as they do READY-FOR-CRITIC, and `_planner_needed` (`factory/cli.py:509`) sends a parent whose last spec writer ended NEEDS-SPLIT to the planner. Either one alone routes the build to the planner. Decisions' last bullet and Risk now name the heading. No seam's content changed.
- [BLOCKING] 6, unglossed terms: FIXED. Evidence's first paragraph now glosses the wrapper and briefing, a round and the critic, and a capability; a new Evidence bullet, placed before the baseline bullet that defines a change by its events, glosses the event log, an event, a parent ticket and a sub-ticket; the amendment bullet glosses a spec amendment, a gate edit and the spec gate; Out of scope glosses the live-store fence; Decisions' first bullet glosses the runner session and "standing", and names the event as a line of the event log.

Round 2 followed Answer 2 and the move of `main`: the intervention command as written (question 1, option (a)); an escape keeping only `issue_sha256` and a note refused when it contains `://` (question 2, option (b)); and the raised README budget modifying all four requirements that state 1,185, shipped in the first seam.

## Critic rounds

round 1 · spec v2 · run-0569-critic · REVISE

# Critic review of T-0056 spec v2 (first critic review of this ticket's spec)

What I checked on `main` at `3e4705a` from `~/dev/spec-factory`, every command through the briefing's wrapper with a throwaway HOME:
- Cited code lines exist and say what the spec says: `factory/cli.py:340-341` and `:366-376` (cost only from `--reply`), `factory/drive.py:228`, `:235`, `:577` (three `run finish` calls), `:168` (`--by workflow`), `factory/workflows/build.js:122`, `:134`, `intake.js:126`, `:131` (`run finish` with no reply), `factory/human.py:156-159`, `factory/common.py:38`, `factory/cost.py` `match_transcripts` at `:159`. `cli.py` is 880 lines, README 1,184, `human.py`'s top-level names today lack `escape_add` and `intervention_add`. `tests/factory/test_drive.py:82`, `:167`, `:177` pin what the spec says; no test greps `run finish`'s command text, `1185`, `escape.recorded` or `issue_sha256`.
- Timestamps: `store.now()` drops microseconds and the scenarios' stand-ins write second-resolution timestamps after `run start`, and `match_transcripts` rejects only `first < started`, so the run-finish scenarios are not racy. The fixtures' user messages carry `TASK_PREFIX`, not `RELAY_PREFIX`, so `_opening` reads them.
- Hand count of the first factory-stats scenario's 25 THEN lines from its fixture, both windows and both stores, and of the transcript scenario's two lines: every figure matches (for example T-0002 wall 12,600 s and lead 54 h, T-0003 900+2,340 s and 6 h; tokens 6,580 and 1,200 give the 3,890 median).
- Ran as written: the fixture GIVEN, the first scorecard WHEN (`exit=2 store=unchanged`, nothing else), the refusal WHEN (`no-since=2 0 bad-setting=2 0 good=2`), the escape WHEN (two lines ending `recorded=2 printed=0/0 link-in-store=0` and `events=0 fields= hash=differ`), the intervention WHEN (`unknown=2 recorded=2`) and the documents WHEN (all `no`, `old=yes`, `built=long`). Each equals the Verification's "today" line.
- README anchors for E1 to E5 are at lines 103, 114, 933, 977-983, 996 and 1053 as cited; the documents scenario's section headings exist at lines 101, 123, 899, 941 and 954. No current-truth harness-docs scenario greps a phrase E1 or E3 removes. `factory launch-script` and README "Upgrading the runtime" exist for the operator steps. Approved changes not yet archived: none, so rubric 5 raises nothing.
- Not checked: the built change's README length, the suite's three-minute bound, and the intake-script and drive scenarios against the built code. The verifier runs those.

## Findings

[BLOCKING] 3, 5 Proposed change "Size and seams" and Decisions "The change is built as two seams"
Problem: The harness would build this change as one sub-ticket of about 520 lines, not the two seams the spec decides, because the seam marker is a bold paragraph and the harness looks for a heading.
Evidence: `factory/cli.py:496` and `:512-514` (`_planner_needed`) send a parent to the planner only when its spec writer ended NEEDS-SPLIT, a planner already ran, or the approved spec has a `##` or `###` heading containing "seam" outside a fence. The stored spec `.factory/store/specs/T-0056/v2.md:231` reads `**Size and seams (two sub-tickets).**`, with no `#`; `grep -i '^##.*seam'` on it finds nothing; the writer's run-0568 ended `STATUS: READY-FOR-CRITIC`. Every past split spec used a heading: `.factory/store/specs/T-0025.md:220` `### Size and seams`, `T-0023/v2.md:111` `### Size and seams (NEEDS-SPLIT)`. The whole-spec build would also defeat Risk's ordering ("the seam that first grows README carries the raised budget") and S2's dependency on S1.
Suggested fix: Make the marker a `### Size and seams (two sub-tickets)` heading in design.md, as T-0023 and T-0025 did.

[BLOCKING] 6 Evidence, first paragraph; Decisions, first bullet
Problem: The operator at the gate meets system terms of art that no human-facing section has glossed: in Evidence's first paragraph "the briefing's wrapper", "the earlier rounds" and "Capabilities opened" (the current-truth spec files, one per feature area), and in Decisions' first bullet "a runner session", an "event" (a line of the store's log) and "standing".
Evidence: Problem glosses factory, run, store, north star, instance and `factory stats`, and no earlier text glosses capability, round, runner session, event or standing; the Evidence paragraph names four `openspec/specs/…/spec.md` paths with no word on what they are, and the log is first described under Evidence's eighth bullet. Rubric 6 names this case as blocking.
Suggested fix: Add a clause at each first use, for example "Capabilities (the current-truth spec files, one per feature area, that this change edits) opened: …", "a runner session (a Claude Code session that runs the factory for the operator)", "one `intervention.recorded` line in the store's event log", and "standing (binds later tickets)".

No SHOULD-FIX or NIT findings. The rest of the spec is grounded, its NEW scenarios fail today for the stated reasons, "Tests to change: none" holds by my own search, and the protected path is declared.

## Prior findings
None: run-0557 and run-0559 reviewed T-0055, not this ticket.

round 2 · spec v3 · run-0571-critic · APPROVE

# Critic review of T-0056 spec v3 (round 2 of this ticket's critic review)

Per the convergence rule I reviewed only whether my round-1 findings were resolved and the text the v2-to-v3 diff changed. `main` is still `3e4705a`, as the spec says, so the code citations I checked in round 1 stand.

What I checked from `~/dev/spec-factory`, through the briefing's wrapper with a throwaway HOME:
- The seam routing. `factory/cli.py:496` defines `SEAM_HEADING_RE` as `^#{2,3}\s`; `_planner_needed` (`:499-516`) returns a planner reason when the last spec writer run's status is `NEEDS-SPLIT` (`:509-510`) or when a `##`/`###` line outside a fence contains "seam" (`:511-514`), as the spec's Responses describe. `factory/drive.py:291` and `factory/workflows/intake.js:187` both accept `NEEDS-SPLIT` beside `READY-FOR-CRITIC` from the spec writer. The writer's run-0570 output ends `STATUS: NEEDS-SPLIT`.
- The stored spec. `.factory/store/specs/T-0056/v3.md:232` is `### Size and seams (NEEDS-SPLIT, two sub-tickets)`, with 14 fence markers before it, so it sits outside a fence. I ran the harness's own check over v3 (`specstore.lines_outside_fences` with `_planner_needed`'s heading test) and it reports that one seam heading. v2 had none.
- The diff. Beyond the heading and the Responses section, v3 changes only glosses in Evidence (first paragraph, a new "store's event log" bullet, the amendment bullet), Out of scope (the live-store fence), Decisions (first and last bullets) and Risk (the heading's name). No scenario, figure, requirement or seam content changed, as the writer says.
- The human-facing sections, read as the gate operator. Problem's first paragraph says what is wrong (the five north-star numbers cannot be read from the store) and for whom (the operator at the fortnightly review). Evidence's first paragraph now glosses the wrapper, briefing, round, critic and capability; Decisions' first bullet glosses the runner session, the event log and "standing".
- Approved changes not yet archived: none, so rubric 5 raises nothing.
- Not run this round: any acceptance command. Round 1 ran six of the WHENs as written and each matched its "today" line; none of them changed.

## Findings

[SHOULD-FIX] 6 Operator steps, step 1; Decisions, first bullet
Problem: Two terms specific to this system remain unglossed in a first paragraph: "(protected)" after `.factory/instance.yaml` in step 1, and "Answer 2, question 1, option (a)" in Decisions' first bullet.
Evidence: No human-facing section says what a protected path is (a path the harness refuses to let a role change, which only the operator edits) or that an Answer is the operator's written reply to a round's open questions, stored with the ticket. Both are unchanged from v2 and I missed them in round 1. I do not block on them: the operator reading this gate is the person who wrote Answer 2 and configured the protected paths, and the parenthetical "(protected)" can be dropped without changing the step, so the failure does not matter for this spec's reader.
Suggested fix: Write "(a protected path: one the harness refuses to let a role change, so you edit it yourself)" in step 1, and "(Answer 2, your written reply to the last round's open questions, question 1, option (a); …)" in the first Decisions bullet, or drop "(protected)".

## Prior findings
- [BLOCKING] 3, 5 seam marker: RESOLVED. The marker is a `###` heading outside a fence that the harness's seam check finds, and the writer's run ended NEEDS-SPLIT; either alone sends the approved spec to the planner.
- [BLOCKING] 6 unglossed terms in Evidence and Decisions: RESOLVED. Every term I named is glossed at its first use, in the section where it first appears, and the glosses are accurate against the code and store I read in round 1.

## Verifier results

6991572ee604bbf88e7b71af43e9233279029fdb · T-0056.1 · VERIFIED · run-0582-verifier
fa0d3b5e26a0c591316cfa2d56b46156f742d293 · T-0056.2 · VERIFIED · run-0585-verifier
