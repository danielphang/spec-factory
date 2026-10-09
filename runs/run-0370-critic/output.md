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

STATUS: APPROVE
CONFIDENCE: high, both round-1 findings are fixed with text that matches the cited changelog entry word for word, and nothing else in the spec changed.
ESCALATIONS: none
