## Review of T-0033 spec v2 (round 2)

What I checked myself, on `main` at `5426ff2` (`git rev-parse --short HEAD`), with a throwaway `HOME` and `TMPDIR` set to this run's scratch directory:

- Where `main` is. The spec says `main` is `220ebdc`; it is now `5426ff2`. `git log --oneline 220ebdc..HEAD` is one commit, and `git diff --stat 220ebdc HEAD` touches only `.factory/answers/T-0030.1-ruling-2026-10-07.md` and one row of `dev/issues.md`. `git diff --quiet d226a4d 220ebdc -- factory/cli.py factory/workflows/build.js factory/prompts docs dev README.md` exits 0, as the Evidence says. Nothing this spec reads or edits has moved since the round-1 evidence.
- New symbols A.1 relies on. `specstore.lines_outside_fences` is `factory/specstore.py` line 77: it yields `(line, in_fence)` and a fence at any indentation toggles. `compose.without_evidence` is `factory/compose.py` line 94 and reads the spec through that generator, cutting a section at a line that starts `## ` or `=== ` only outside a fence. `factory/cli.py` already imports `specstore` (line 21) and uses the generator at line 502, so the implementer has a pattern to copy. The rulings reach the reviewer and verifier inputs at `factory/compose.py` lines 278 and 300, as cited.
- Acceptance commands, run as written. The fixture (41 lines) and merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`. The reviewer-escalation ruling scenario printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`. The spec-writer prompt scenario, with the new `braces` count, printed `reads=0 form=0 braces=0` three times, then `copy=SAME fill=unchanged`. The design-doc scenario, with the new `piece9` count, printed `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0`. All four match verification.md's "today" lines, so the writer's unrun v2 items fail today for the stated reasons.
- The code the parts edit is where the spec says: `merge_cmd` at `factory/cli.py` 645 with `MergeLock` at 662; `resolve`'s `--ruling` branch at 865-876 still sends a non-planner ESCALATE to `ready-for-critic`; `factory/workflows/build.js` 194-200 still asks the join again after a refusal and files it as `harness-bug: merge:`. The `--decision` guard at line 826 lists the modes C.1 must extend.
- Tests to change. The test file added since v1, `tests/factory/test_role_inputs.py`, matches `Risk|merge|ruling` on one line, a `## Risk` heading inside its fixture spec text; it exercises no merge or ruling route. `grep -rn 'review protected PRs\|piece-8 approvals' tests/factory/` finds nothing, so the new E.1 edits break no test. "Tests to change: none" still holds.
- Writing standard, read as the operator new to this system. The Problem's first paragraph says what is wrong (undeclared protected-path changes merge) and for whom (the operator who approved a spec that never said so), and now glosses instance, harness, operator, spec gate, sub-ticket, reviewer, verifier, merge gate and integration branch. The first paragraph of Evidence, Decisions and Operator steps each uses only terms the Problem or its own first sentence has glossed. The design.md text that goes into `docs/design.md` keeps that document's "checks" and "checkers", which is right.

### Findings

[NIT] 6 proposal.md, Decisions bullet 9
Problem: "a VERIFIED verifier result with a PASS gate result" uses "gate" for the recorded `ci` row, while every other sentence in these sections uses "the gate" for the merge gate, so one name covers two concepts (rule 9).
Evidence: Decisions bullet 5 ("The gate runs this check") and bullet 6 ("A refusal exits 2") mean the merge gate; bullet 9 means the `ci` row the Evidence calls "`ci` PASS" (bullet 3). No other section has the clash.
Suggested fix: Write "a PASS `ci` result (the gate suite)" or "a PASS test-suite result" in bullet 9; no other change.

### Prior findings (round 1)

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps: RESOLVED. The Problem names and glosses the terms; "GIVEN block" is gone from Evidence; Decisions bullet 1 glosses the pinned spec and `decisions.md`; Operator step 1 glosses the runtime, `harness.lock` and the Nanobot instance; step 2 glosses a gate edit.
- [SHOULD-FIX] 6, two names per concept: RESOLVED. "Integration branch" is introduced in the Problem and used throughout; "reviewing agents" and "checkers" are gone from proposal.md. The one residue is the NIT above.
- [SHOULD-FIX] 4, brace lists: RESOLVED. Decisions bullet 2 states the one-entry rule and that a brace list declares nothing; D.2 adds the FORMAT line; the spec-writer scenario's `braces` count fails today (verified above); the new test file covers a refused brace-list entry.
- [NIT] 2, three untested branches: RESOLVED. The design.md opening lists five cases the new test file covers, including the two I named and the no-approved-spec wording.
- [NIT] 5, piece 9: RESOLVED. E.1 changes line 49 and the design-doc scenario's `piece9` count fails today (verified above).

The change not asked for by a finding (reading the Risk section with `specstore.lines_outside_fences`) is sound: it reuses the section rule `main` adopted in `220ebdc`, and without it a quoted example declaration in a Risk section would authorize paths. The spec also says plainly that v2's scenarios were not re-run; I re-ran four of them and they match.

Out-of-scope observations: none new. The round-1 note on the 2026-10-07 T-0032 decision line stands; the spec records the correct cause in Evidence and leaves the log alone, which is right for this ticket.

STATUS: APPROVE
CONFIDENCE: high; every round-1 finding is addressed in the text, the new symbols A.1 cites exist and behave as described, four acceptance commands including both v2 additions reproduce verification.md's "today" output on the current `main`, and no existing test pins the overturned route.
ESCALATIONS: none
