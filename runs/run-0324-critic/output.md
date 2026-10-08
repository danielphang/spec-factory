## Critic review, T-0034 spec v2, round 2

Round 2: I reviewed whether the three round-1 findings were resolved and the text the v1→v2 diff changed. Spot-checks on `main` at `2e73dbb` (clean tree, `git log --oneline -1 main`):
- `docs/design.md:461`, `docs/prompts/03-spec-critic.md:42`, `factory/prompts/critic.md:42` each still hold `Spot-check at least 2 cited paths and 1 acceptance command yourself.` as the only PROCESS line, followed by a blank line and `ANTI-GOODHARTING (REVIEWER SIDE)`. `docs/design.md:371` still ends the "On revision" bullet with `wrong just to get approved.`; in `factory/prompts/spec_writer.md` that line is followed by a blank and the "Acceptance items describe behaviour" bullet, as part A says.
- `docs/principles.md`: principle 2 "Implemented by" ends `` `factory/prompts/reviewer.md`, `factory/compose.py`). `` at lines 41–44; the status line at 45–46 reads "done by #41. The code reviewer is the only reader role …"; Spiking (167–176) ends "The critic reads and spot-checks; it does not build." `.factory/context.md:14-15` gives the suite command. All as the spec cites.
- `grep -n '^[0-9]*\. ' docs/changelog.md | tail -1` → line 61, `57. After issue #41 …`. D.1's "last entry is 57, new entry is 58" is now correct.
- Acceptance scenario 1 run on `main` under a fresh HOME: printed `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged`, then `critic copy=SAME doc=0/6 run=0/6 fill=unchanged`. Scenario 4 on `main`: `CONTIGUOUS`, `0`, `implemented=0 status=0`. Both match verification.md. I did not run scenario 2 (it starts runs), the suite, or any build.
- Open tickets: T-0027 and T-0033 are still `ready-for-planner` (`.factory/store/tickets/T-0027.yaml`, `T-0033.yaml`); T-0030 is `planned` with T-0030.3 merged. The merge-order note still holds.
- The request (`.factory/store/requests/T-0034.md:7`) gives 34% and p90 73 where triage's re-derivation gives `share 33` and `p90 71`. The spec quotes triage's line and says "about a third" in prose, so the two sources agree at the altitude the Problem uses. Not a finding.

### Prior findings

- [BLOCKING] 6, unglossed terms in Evidence ¶1, Operator steps ¶1, Problem ¶3 → RESOLVED. Problem ¶1 now names the intake workflow and glosses triage, the spec writer and the critic; the new Problem ¶4 glosses the harness and the runtime before the replay is mentioned; Evidence ¶1 glosses the workflow transcripts; Operator steps 1 glosses the store and a throwaway store. The two quoted cost lines are followed by a reading of every field, and the reading is correct (p90 71 as "the slowest tenth took 71 or more"). Reading Problem, Evidence, Open questions, Decisions and Operator steps as the gate operator, I found no first-paragraph term of art that an earlier paragraph has not glossed.
- [SHOULD-FIX] 1, D.1 numbered the last entry 58 → RESOLVED. Checked against the changelog, above.
- [NIT] 2, entry on one line → RESOLVED. D.1 now says so, and the scenario's one-line grep matches the rule.

### Findings

None. The changed text introduces no new path, symbol, scenario or decision; the writer's note that no scenario, part or decision changed matches the diff. The one new sentence under Evidence ("The three copies are the design doc's block, its documented copy and the copy the harness actually sends") is accurate: the suite's design-block tests compare the block to `docs/prompts/`, and `factory/prompts/critic.md` is what `run start` composes.

Rubric 2 note, for the record: the writer reports a prototype with `364 passed`. I did not reproduce that and my approval does not rest on it. It rests on the scenarios being text checks that fail on `main` for the stated reason and that a wrong or partial edit (one copy edited, a rule paraphrased, an existing line changed) would fail through `copy=`, `doc=`/`run=`, `fill=` or `removed=`.

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is fixed as stated, the cited lines and two acceptance scenarios were re-checked on `main` and matched, and the v2 diff touches prose only
ESCALATIONS: none
