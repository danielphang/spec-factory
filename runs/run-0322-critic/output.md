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

STATUS: REVISE
CONFIDENCE: high, every cited line and both document scenarios were checked on `main` and matched; the one BLOCKING item is a writing-standard gloss, not a design defect
ESCALATIONS: none
