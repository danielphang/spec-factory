Round 2 review of T-0035 spec v2 (issue #74: drop the critic's per-claim cap and no-build rule). Per the convergence rule I reviewed (a) whether round 1's findings were resolved and (b) the text that changed between v1 and v2, from the unified diff in my input.

What I checked myself, from `~/dev/spec-factory` at `49ea4c7` (`main`, clean tree), each command under a throwaway HOME:
- Changed text against the repo: `git grep -n 'Ground any one claim'` still prints `docs/design.md:469`, `docs/prompts/03-spec-critic.md:43`, `factory/prompts/critic.md:43`. `docs/principles.md` is 178 lines; `## Spiking` is at line 169 and its paragraph runs 171-178, as Evidence and Root cause now both say. `docs/changelog.md` is 64 lines: entry 58 at line 62, a blank line, then `Declined:` at line 64, so part D's "insert directly after entry 58" is the right instruction. `.factory/answers/T-0034-acceptance-2026-10-08.md` holds both quoted sentences (2 hits). `git grep` for the six removed phrases over `README.md`, `dev/` and `tests/factory/` finds 0 hits.
- Acceptance commands re-run as written on the base: scenario 1 prints `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` then `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged`; the changelog scenario prints `CONTIGUOUS` then `1`; the Spiking scenario prints `bound=1 nobuild=1 scratch=0 whole=0 replay=0`. All three match verification.md, so the NEW items still fail today for the stated reasons.
- Part A's wording against scenario 1: I applied part A's eight replacement lines to a scratch copy of `docs/prompts/03-spec-critic.md` (in this run's scratch directory, no clone) and ran scenario 1's phrase counts on it: `doc=8/8 gone=0`. The diff against the current copy touches only lines 43-47, so the "Nothing else" scenario's sections before `PROCESS` and from `ANTI-GOODHARTING` on stay identical. The spec's text, followed as written, satisfies its own checks.
- Decision log: lines 86-93 are the eight 2026-10-08 T-0034 decisions. The spec overturns line 86 (the cap) and the "builds nothing" half of line 87, keeps the no-suite half and line 88 (the "finding or question" sentence), and says so with the operator's acceptance record as authority.

Findings

[NIT] 1 Decisions, first bullet
Problem: "(T-0034's other 2026-10-08 decision)" implies T-0034 has two decisions dated 2026-10-08; the log has eight, and the cap is the first of them.
Evidence: Decision log lines 86-93 all carry `2026-10-08 T-0034`; the cap is line 86, the no-suite/no-build rule line 87.
Suggested fix: Write "(another of T-0034's 2026-10-08 decisions)" or "(T-0034's cap decision of the same date)".

Prior findings:
- [BLOCKING] 6 Decisions, first bullet (T-0034 and "standing decision" unglossed): RESOLVED. The bullet now opens "This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73", and Evidence bullet 1 glosses T-0034 at its first mention.
- [SHOULD-FIX] 6 Unglossed terms (intakes, current truth, item B/C, the triage): RESOLVED. Each is glossed at first use in the v2 text I diffed: "tickets the factory had already taken from request to approved spec", "the archived requirements that describe it as built", "its list of what the critic keeps", "its `docs/principles.md` change", "The triage role, which sorts a request before the spec writer sees it", and "a spike, a ticket built only to test whether an approach works".
- [NIT] 1 Part C attributed the replay to #74: RESOLVED. Part C now reads "The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found ..."; the Spiking scenario's `replay` phrase still matches.
- [NIT] 1 Spiking line ranges disagreed: RESOLVED. Both now say "heading at line 169, paragraph at lines 171-178", which the file confirms.
- Not blocking, the kept "finding or question" sentence: unchanged by design, declared in Decisions bullet 2 with its reason. I still read the two sentences as compatible (a scratch experiment is not a build of the change), and this round's scratch check confirms the kept sentence is what makes scenario 1's eighth phrase hit.

The writer's one unprompted change, part D's "insert directly after entry 58" in place of "append", is correct for the file as it stands.

STATUS: APPROVE
CONFIDENCE: high. Every round 1 finding is fixed in the text I diffed; the changed text matches the repository line for line; the base outputs of three scenarios match verification.md; and part A's wording, applied to a scratch copy, yields exactly the counts scenario 1 expects.
ESCALATIONS: none
