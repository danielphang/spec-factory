## Round 2 review (checkout `0b1abad`, HOME wrapper, scratch under this run's directory)

Reviewed: whether the three round-1 findings were resolved, and the text that changed in v2 (Problem paragraphs 1-2 and 4, Evidence "The figure" and the new "One repeat did carry something extra" bullet, Root cause's runtime gloss, the new Decisions bullet on the changelog count, Risk's instance gloss, Operator steps step 1, Design B's count, verification.md's closing paragraph).

## Spot-checks

- The re-derived figure is right. I read `.factory/state/log/2026-10.jsonl` as committed at `0b1abad` with my own Python filter: 126 `escalation.queued` events, 205 items. The implementer and verifier events whose items are declared-path lists are exactly the ten the spec names (0063, 0096, 0099, 0109, 0177; 0064, 0097, 0100, 0110, 0179). Counting only the declared-path lines in those events, and leaving out the unrelated items the spec's Out of scope names (0109's "No undeclared protected path" and "No prompt-injection", 0177's fixture note, 0064's and 0097's out-of-scope remarks), gives 18 implementer and 12 verifier items, 30 in all. 30/205 is 14.6%, which "one in seven" states fairly.
- The extra flag is real: runs 0096 and 0099 each end their declared-path item with "Also flagged: the harness turned an approved and verified head into a fix round", as Evidence now says.
- The 35 queued events with no `run` field are all harness park notices (`factory/store.py:156`: archive, NEEDS-HUMAN, SPEC-DEFECT, budget kill), never a role's ESCALATIONS list, so Operator step 2's grep on `"run": "run-NNNN-(implementer|verifier)"` misses nothing it should catch.
- `--accept-harness <sha>` is the flag README documents (`README.md:215, 231, 345`); step 1's `<commit>` is the same thing.
- Acceptance re-run on this checkout: the changelog scenario printed `CONTIGUOUS`, then `0`; the design-blocks scenario printed `implementer copy=SAME rule=0 fill=unchanged`, then `verifier copy=SAME rule=0 fill=unchanged`. Both match verification.md's "today" lines. The changelog's last entry is 52, so Design B's "53, or 54 if issue #46's entry lands first" is correct.
- The retro's 38 is at `retro_with_efficiency.md:145` as cited. Its 26 is at line 118 ("Incidents: 26 declared-path lists queued by the implementer (16) and the verifier (10) out of 139"), not line 116.
- The prototype clone verification.md points at (`.factory/state/runs/run-0260-spec_writer/scratch/c`) no longer exists; the harness cleared that run's scratch. I could not re-check `265 passed` or "37 added lines across six files". Nothing in Acceptance depends on either figure, and the implementer rebuilds the change from Design A and B, so this is not a finding.

## Prior findings (round 1)

- [BLOCKING] 6, Operator steps step 1: RESOLVED. Step 1 now says what the runtime is (the checkout at `~/dev/spec-factory-harness` that runs execute from, which a merge does not move), what an instance is (one repository's own setup of the factory, naming this repo's and instance A), and what `--accept-harness <commit>` does. The runtime is also glossed at its first use in Root cause and an instance at its first use in Risk. A technical reader new to the system can perform step 1 without inferring anything.
- [SHOULD-FIX] 1, the figure: RESOLVED. One count, re-derived from the log and reproduced here independently, is used in Problem, Evidence, Decisions and Design B; the retro's two contradicting figures are recorded as rejected.
- [NIT] 6, Problem, "harness": RESOLVED. The term list opens with the gloss.

## Findings

[NIT] 1 Evidence, "The figure", last sub-bullet; Responses, second item
Problem: The retro's 26 is cited at line 116, but it is at line 118 (line 116 is a prose line of P5's "After" text).
Evidence: `sed -n '116p;118p' .factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md`; my round-1 finding gave "lines 110-116" for P5, which likely led the writer here, so the error is partly mine.
Suggested fix: Change "line 116" to "line 118" in Evidence (the Responses section is history and can stay).

No other findings. The changed text introduces no new term of art without a gloss, no new decision, and no new path; Design A and B, the acceptance scenarios and Tests to change are unchanged from v1, where they were checked and fail today for the stated reason. Scope still fits one PR. Every protected and guardrail path the change touches is declared under Risk.

STATUS: APPROVE
CONFIDENCE: high, the one count that changed between rounds was reproduced independently from the committed log, and both re-run acceptance scenarios matched verification.md; the only finding is a line-number slip.
ESCALATIONS: none
