## Acceptance

- Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule → NEW. On `main` at `2e73dbb` it prints `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged`, then `critic copy=SAME doc=0/6 run=0/6 fill=unchanged`: no copy holds any of the rules.
- Spec writer and critic run prompts carry the new rules → NEW. On `main` at `2e73dbb` it prints `spec_writer batch=0 writes=0`, then `critic batch=0 suite=0 cap=0`, the same under `zsh` and `sh`.
- Rubric, round limit, format and every other prompt are unchanged → REGRESSION. On `main` it prints `sections_changed=0 removed=0 others=0`, and on the prototype as well.
- The changelog and the principles page record the change → NEW. On `main` at `2e73dbb` it prints `CONTIGUOUS`, then `0` (the last entry, 57 for #41, holds none of the five phrases), then `implemented=0 status=0`.
- The turn-economy change adds no whitespace errors → REGRESSION. It printed `exit=0` on the prototype.

## Responses

- [BLOCKING] 6, unglossed terms in Evidence ¶1, Operator steps ¶1 and Problem ¶3 → FIXED. Problem ¶1 now names the intake workflow and glosses triage, the spec writer and the critic as its three agents. A new Problem ¶4 glosses the harness and the runtime, and says the replay runs before the runtime moves. Evidence ¶1 glosses the workflow transcripts. Operator steps 1 glosses the store and a throwaway store. Under rule 5, the quoted cost lines are now followed by a reading of every field (runs, median and p90 turns, total context tokens, share of the total, tokens per run). The Problem and Operator steps now say "turns" throughout, the name the Problem gives a model call, where v1 also said "agent calls".
- [SHOULD-FIX] 1, D.1 numbered the last entry 58 → FIXED. D.1 now says the last entry on `main` is 57 and the new entry is 58 (`grep -n '^[0-9]*\. ' docs/changelog.md | tail -1` prints line 61, `57. After issue #41 …`).
- [NIT] 2, the entry on one line → FIXED. D.1 now says to write the entry on one line, as every existing entry is. The prototype's entry is one line, and the changelog scenario printed `5` on it.

No scenario, part or decision changed in this round. I rebuilt the prototype in this run's scratch directory and re-ran all five scenarios on it and on `main`. Each printed what verification.md states. The suite printed `364 passed`.

## Out-of-scope observations

- `agents/factory-spec-critic.md` and `agents/factory-spec-writer.md` repeat old copies of their prompts, including the critic's `Spot-check at least 2 …` line (`agents/factory-spec-critic.md:28`). Inline runs never see them. T-0030 part A.3 replaces those bodies with a pointer to the run's `system-prompt.txt`, which removes the drift.
- The briefing every role receives (`.factory/context.md`, line 14) tells the reader how to run the harness suite, and the composed "Running code" section says to wrap "every test or check command the briefing above gives". A critic could read both as an invitation to run the suite. The new PROCESS lines override that for the critic. If the replay shows critics still running the suite, the briefing is the next place to look. It is infra (`.factory/**`), outside this ticket.

## Critic rounds

round 1 · spec v1 · run-0322-critic · REVISE

## Critic review, T-0034 spec v1, round 1

Spot-checks (on `main` at `2e73dbb`, clean tree):
- `docs/design.md:371` ends the "On revision" bullet with `wrong just to get approved.`, then a blank line and `FORMAT` (373). `docs/design.md:461`, `docs/prompts/03-spec-critic.md:42`, `factory/prompts/critic.md:42` each hold `Spot-check at least 2 cited paths and 1 acceptance command yourself.` as the only PROCESS line, before a blank and `ANTI-GOODHARTING (REVIEWER SIDE)`. `agents/factory-spec-critic.md:28` holds the same line.
- `diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md` shows only `400`/`{400}` and the run copy's extra "Acceptance items describe behaviour" bullet at lines 60–63; the critic pair differs only by `2`/`{2}`. Matches "keeps the differences it has today".
- `docs/principles.md`: principle 2 spans lines 31–46, "Implemented by" is 41–44 and ends `` `factory/prompts/reviewer.md`, `factory/compose.py`). ``, the status line is 45–46 and reads "done by #41. The code reviewer is the only reader role that was given gate commands; the critic and triage never were." Spiking is 167–176 and ends "The critic reads and spot-checks; it does not build." All as cited.
- `.factory/context.md:14` gives the suite command; `factory/prompts/preamble.md:54-60` is SCRATCH FILES and says only where files go.
- Acceptance scenario 1 run on `main`: printed `spec_writer copy=SAME doc=0/4 run=0/4 fill=unchanged` then `critic copy=SAME doc=0/6 run=0/6 fill=unchanged`, as verification.md states. Scenario 4 run on `main`: printed `CONTIGUOUS`, `0`, `implemented=0 status=0`, as stated. I did not run scenario 2 (it starts runs) or the suite.
- Tests pinning the old text: none. `tests/factory/test_coding_standard.py:86`, `test_decision_log.py:255`, `test_writing_standard.py:77` compare each design block to its `docs/prompts/` copy only; `test_instance.py:88-90` compares `agents/factory-*.md` to the files `init` writes, not to the prompts. "Tests to change: none" holds.
- Open tickets: T-0027 (ready-for-planner) edits the critic's rubric item 5 lines; T-0033 (ready-for-planner) edits the writer's FORMAT `## Risk` line. Neither touches the lines this spec inserts.

### Findings

[BLOCKING] 6 Evidence ¶1, Operator steps ¶1, Problem ¶3
Problem: The first paragraph of Evidence and of Operator steps each use a factory-specific name that no earlier human-facing paragraph has glossed, so the gate reader has to infer what they are.
Evidence: Evidence ¶1: "re-derived by triage from this session's workflow transcripts" ("triage" is a role, the agent that sorts a request before the writer; nothing says so; "workflow transcripts" likewise). Operator steps ¶1: "run the intake workflow twice on a throwaway store" ("intake workflow" and "store" never glossed; the Problem described the writer-critic loop but never named it intake). Problem ¶3: "before the running harness is upgraded" and "replays a few approved intakes" ("harness", "intakes" unglossed; Problem ¶1 passes, it says what is wrong and for whom). The rubric makes an unglossed system term in a first paragraph of these sections BLOCKING even when a careful reader could work it out. Also rule 5: the quoted triage line `spec_writer runs 58 median_calls 29.0 …` is not followed by what its fields mean (`ctxM`, `share`, `perrunM`).
Suggested fix: Gloss each at first use in one clause ("triage, the role that sizes a request before the writer", "the intake workflow, the triage-writer-critic chain that produces a spec", "a throwaway store, a scratch copy of the ticket state", "the harness, the code that runs the roles") and add a half-sentence reading after the quoted cost line.

[SHOULD-FIX] 1 design.md D.1
Problem: D.1 says the last changelog entry on `main` is 58, but it is 57, so an implementer following D.1 numbers the new entry 59 and the contiguity check fails.
Evidence: `grep -n '^[0-9]*\. ' docs/changelog.md | tail -1` → line 61, `57. After issue #41 …`; `Declined:` is line 63. The prototype text in D.1 is numbered 58 and verification.md says "the last entry, 57 for #41", so the spec contradicts itself in one place only.
Suggested fix: Change "(58 on `main` today)" to "(57 on `main` today; the new entry is 58)".

[NIT] 2 design.md D.1 / scenario "The changelog and the principles page record the change"
Problem: The scenario greps only the first line of the last numbered entry, but D.1 never says the entry must be one line, as every existing entry is.
Evidence: `grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF …` reads one line; lines 59–61 of `docs/changelog.md` are each one unwrapped entry.
Suggested fix: Add "on one line, as the existing entries are" to D.1.

No other findings. Grounded, testable, scoped to one PR, protected paths declared, consistent with T-0027 and T-0033, no silent product choice: the per-claim cap, the no-suite rule and the replay as an Operator step are all stated as Decisions with rejected alternatives.

round 2 · spec v2 · run-0324-critic · APPROVE

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

## Verifier results

f25dffed5f970142f9da01b0ed24f8e8deaac40a · T-0034.1 · VERIFIED · run-0327-verifier
