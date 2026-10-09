Round 1 review of T-0039 v1 (reading rules for the implementer, verifier, code reviewer, planner and triage).

What I checked myself (repo at `b002c95`, commands run through the fresh-HOME wrapper):
- Cited paths and lines: `factory/prompts/critic.md` 50-55 and `docs/design.md` 485-490 hold the critic paragraph as quoted; `factory/prompts/spec_writer.md` 59-65 holds the writer form with the "suite run" example and the one-write sentence; `factory/prompts/reviewer.md` 7-8 is the "Do not run the test suite or the gate commands" rule; `factory/compose.py` 186-188 writes the "Scratch directory" section; `docs/changelog.md` line 63 is entry 59 (#74) and carries the 37% figure; `tests/factory/test_capability_index.py` 249-259 limits its 72-column check to lines containing "capabilit"; `docs/principles.md` 173 credits reading rules to #73 only. `grep -rli 'turn economy'` over the three prompt locations matches only the writer and critic copies.
- Placement anchors: the declared-path bullet is the last RULES bullet in `factory/prompts/implementer.md` (line 44, PR DESCRIPTION at 51) and `verifier.md` (line 34, OUTPUT at 41); `reviewer.md` line 10 ends WHAT YOU RUN; `planner.md` line 19 ends RULES; `triage.md` line 28 is the CLARIFY line, and `diff docs/prompts/01-triage.md factory/prompts/triage.md` shows only the instance-added block at 30-33.
- Tests that read the five prompts (`test_coding_standard.py` 82, `test_writing_standard.py` 74, `test_decision_log.py` 248, `test_capability_index.py` 249-259) compare a design block to its `docs/prompts/` copy or check specific triage lines; none pins a bullet count, a line number or the full text. "Tests to change: none" holds.
- Acceptance run as written on base: scenario "The five role prompts carry the critic's reading paragraph in every copy" printed the five lines with `copy=SAME doc=0 run=0 writes=0 fill=unchanged`; the changelog scenario printed `63 CONTIGUOUS` then `terms=2 footer=1`. Both match the Acceptance section's stated base output. Saved under the run's scratch directory.
- Request vs spec: the request's "changelog 58" is a mis-cite; the spec's correction to entry 59 is right. The critic-form choice, the preamble rejection and the Operator-step placement of the replay are each stated with a reason. Protected paths line names all ten prompt copies in the gate's fixed form. No open ticket (T-0027, T-0031) touches these prompts.

Findings

[BLOCKING] 6 Problem, first paragraph
Problem: The first paragraph glosses what a role is and says nothing about what is wrong or for whom; the reader learns the defect only in paragraph 3.
Evidence: Paragraph 1 is "The factory runs each step of a ticket as a separate model agent, a 'role': ... Each role is steered by its own written prompt." The writing standard's rule 1 check is "a reader who stops after the first paragraph can say what the problem is and who has it"; that reader cannot. The rubric makes this BLOCKING by name.
Suggested fix: Open with one sentence such as "Five of the factory's seven role prompts (implementer, verifier, code reviewer, planner, triage) lack the reading rules that cut the spec writer's tokens by about 37%, and the two that run test suites pay the most for it", then keep the role gloss as the rest of that paragraph.

[SHOULD-FIX] 1, 6 Problem paragraph 2; Evidence bullet 3; Risk
Problem: The spec quotes only the favourable half of changelog entry 59; the same entry records that #73's critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less, which is the risk the Risk section describes and the operator's reason to run the replay.
Evidence: `docs/changelog.md` line 63: "...cut its tokens by about 37% at the same quality, but that its critic rules saved nothing ... and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk". The spec's Evidence bullet 3 quotes the entry up to "at the same quality". T-0035 later attributed the under-checking to the critic's cap and build ban, not to the three reading sentences, which it kept.
Suggested fix: Add one sentence to Evidence (and a clause to Risk) stating entry 59's critic result and that T-0035 kept the reading sentences while removing the cap and build ban, so the operator sees the one measured case where these rules did not pay.

Not findings, noted for the implementer: scenario "Triage and planner runs receive the reading paragraph" reuses the `FACTORY_STATE` throwaway-store pattern of current-truth scenario "Planner, spec writer and critic runs get the new rules in their system prompts", so I did not re-run it; scenario "Implementer, reviewer and verifier runs receive the reading paragraph" needs the role-escalations GIVEN fixture run first, as the spec says.

I could not check: that the harness suite passes on the prototype (the verifier runs it); the spec's report of 4 location-dependent failures in `tests/factory/test_instance.py` on both base and prototype is plausible but unverified by me.

STATUS: REVISE
CONFIDENCE: high, every cited path, line and base output I checked matched the spec, and the one blocking item is a one-sentence reorder.
ESCALATIONS: none
