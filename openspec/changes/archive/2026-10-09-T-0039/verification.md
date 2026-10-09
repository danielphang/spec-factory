## Acceptance

- The five role prompts carry the critic's reading paragraph in every copy → NEW; today each of the five lines prints `doc=0 run=0` (`copy=SAME writes=0 fill=unchanged` already hold), because no copy of these prompts carries the paragraph.
- Only the paragraph is added, and no other prompt changes → REGRESSION; prints `extra=0 deleted=0 others=0` on base and must still after the change. A mutated prototype printed `extra=2 deleted=1 others=1`.
- Implementer, reviewer and verifier runs receive the reading paragraph → NEW; today prints `preamble=1 economy=0 writes=0` for each role. The run starts, but its prompt lacks the paragraph.
- Triage and planner runs receive the reading paragraph → NEW; today prints `triage preamble=1 economy=0 writes=0`, then `planner preamble=1 economy=0 writes=0`.
- The changelog records the reading rules for the five roles as its last entry → NEW; today prints `63 CONTIGUOUS`, then `terms=2 footer=1`, because the last entry is #57's.
- The reading-rules change adds no whitespace errors → REGRESSION; prints `exit=0` on base.

## Responses

- [BLOCKING] 6, Problem first paragraph → FIXED. The Problem now opens with what is wrong and for whom: five of the seven role prompts (triage, planner, implementer, code reviewer, verifier) lack the reading rules that cut the spec writer's tokens by about 37% at the same quality; the operator pays for those tokens on every ticket, and the implementer and verifier pay most because they run suites and long commands. The role gloss follows in the same paragraph. The request's 18% and 13% shares are still left out of the Problem, because I found no source for them in this repo (Evidence bullet 3).
- [SHOULD-FIX] 1, 6, Problem paragraph 2, Evidence bullet 3, Risk → FIXED. Evidence bullet 3 now quotes the other half of changelog entry 59 (`docs/changelog.md` line 63): #73's critic rules "saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less". It also says #73 gave the critic a per-claim cap and a build ban besides the reading paragraph, and that #74 removed the cap and ban and kept "the three reading rules". Problem paragraph 2 says the replay found no critic saving and that the cap was removed while the rules stayed. Risk now names this as the precedent and says the reading sentences and the cap were never tested apart, which is one reason for the operator's replay. Re-checked on `b002c95` (unchanged since round 1): the changelog scenario still prints `63 CONTIGUOUS`, then `terms=2 footer=1`, and `git diff --check main...HEAD` prints `exit=0`.

## Critic rounds

round 1 · spec v1 · run-0368-critic · REVISE

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

round 2 · spec v2 · run-0370-critic · APPROVE

Round 2 review of T-0039 v2 (reading rules for the implementer, verifier, code reviewer, planner and triage). Per convergence, I reviewed only my round-1 findings and the text the v1→v2 diff changed: Problem paragraphs 1-3, Evidence bullet 3, Risk, and the new Responses section.

What I checked myself (repo still at `b002c95`, clean apart from an untracked `.factory/answers/` file; commands run through the fresh-HOME wrapper):
- `docs/changelog.md` line 63 (entry 59) against the new quotations: "saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less" is verbatim; the entry names the missed Nanobot `UV_PYTHON_INSTALL_DIR` risk and the brace-list declaration bug (the spec's "one Nanobot risk and one declaration bug"); it describes the dropped cap as "at most two paths and one command for any one claim" and the dropped rule as "no clone, worktree or prototype", and says the change "keeps ... the three reading rules". Every new factual claim in Problem paragraph 2, Evidence bullet 3 and Risk matches the entry. "The two were never tested apart" is the spec's inference, and the entry supports it: it records no second replay after the cap was dropped.
- Acceptance command re-run as written: the changelog scenario prints `63 CONTIGUOUS`, then `terms=2 footer=1`, as the Acceptance section states for base.
- Writing standard rule 1 (`docs/writing.md` lines 23-24) against the new Problem paragraph 1: a reader who stops there can say what is wrong (five role prompts lack the reading rules) and who has it (the operator paying for tokens, most on implementer and verifier runs).

Prior findings

[BLOCKING] 6 Problem, first paragraph → RESOLVED. The paragraph now opens with the defect and the party who pays, and keeps the role gloss in the same paragraph.

[SHOULD-FIX] 1, 6 Problem paragraph 2; Evidence bullet 3; Risk → RESOLVED. The unfavourable half of entry 59 is quoted with its figures, the cap and ban are named as the confound, and Risk states the precedent and that the operator's replay is the check on it. The quotations are verbatim against line 63.

New findings on changed text

[NIT] 6 Problem, first paragraph
Problem: "role prompts" and "spec writer" appear in the first sentence, and the gloss of what a role is arrives in the fifth sentence of the same paragraph.
Evidence: Paragraph 1 as given in v2. The gloss is inside the first paragraph, so the rubric's BLOCKING condition does not hold; a reader has it before the paragraph ends.
Suggested fix: Move the "The factory runs each step of a ticket as a separate model agent, a 'role' ..." sentence to second position, before "The five are ...".

I could not check: that the harness suite passes on the prototype (the verifier runs it); unchanged from round 1.

## Verifier results

a86d154a75c6545d91f87cc79a007d2fe16e5df3 · T-0039.1 · VERIFIED · run-0375-verifier
