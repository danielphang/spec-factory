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

STATUS: REVISE
CONFIDENCE: high, both findings rest on code and store files I read and on commands I ran; the first-scenario figures I re-derived by hand
ESCALATIONS: none
