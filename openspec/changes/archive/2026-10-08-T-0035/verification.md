## Acceptance

Base outputs below are from `~/dev/spec-factory` at `49ea4c7` (`main`), each command run under a throwaway HOME in this round. On the prototype (`scratch/proto` in this run's directory, built by `scratch/edit.py` from `49ea4c7`, with the round 2 wording) each scenario printed its THEN line exactly.

- Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules → NEW. Today the second line is `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged`: the scratch-experiment phrase is missing, and the three removed phrases are found in both files. The writer line already matches; that half is a regression guard.
- A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban → NEW. Today the second line is `critic batch=1 suite=1 scratch=0 cap=1 build=1`.
- The writer prompt is as #73 left it, and only the critic's PROCESS changes → REGRESSION. Today it prints `sections_changed=0 writer=0 others=0`. It must still do so after the change.
- Principle 2 names the critic's no-suite rule and no longer its build ban → NEW. Today it prints `CONTIGUOUS`, then `entries73=1 implemented=0 builds=1 status=1`.
- The changelog records the revert as its last entry → NEW. Today it prints `CONTIGUOUS`, then `1`: entry 58 contains only `no test suite`.
- The Spiking section allows a small scratch check and records the replay → NEW. Today it prints `bound=1 nobuild=1 scratch=0 whole=0 replay=0`.
- The critic revert adds no whitespace errors → REGRESSION. Today it prints `exit=0`, because the diff is empty.

## Responses

- [BLOCKING] Decisions, first bullet: FIXED. The bullet now opens "This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73". Evidence bullet 1 also says what T-0034 is, at its first mention.
- [SHOULD-FIX] Unglossed terms: FIXED. Problem glosses intakes ("tickets the factory had already taken from request to approved spec"). Evidence glosses current truth ("the archived requirements that describe it as built"). Decisions gloss the request's item B ("its list of what the critic keeps") and item C ("its `docs/principles.md` change"), the triage role ("which sorts a request before the spec writer sees it") and a spike ("a ticket built only to test whether an approach works").
- [NIT] Part C attributes the replay to #74: FIXED. Part C now reads "The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found ...", and keeps "#74 removed the cap ...". The Spiking scenario still matches it (`replay=1`), checked on the rebuilt prototype.
- [NIT] Spiking line ranges: FIXED. Evidence and Root cause both say "heading at line 169, paragraph at lines 171-178".
- Not blocking (the kept "finding or question" sentence): no change. Decisions bullet 2 keeps it declared with its reason, as the critic noted.
- Also changed: part D now says to insert entry 59 directly after entry 58, because `docs/changelog.md` ends with a `Declined:` line after the numbered entries (line 64); "append" was ambiguous. Evidence's size and test counts are re-derived from this round's prototype.

## Critic rounds

round 1 · spec v1 · run-0330-critic · REVISE

Round 1 review of T-0035 spec v1 (issue #74: drop the critic's per-claim cap and no-build rule).

What I checked myself, from `~/dev/spec-factory` at `49ea4c7` (`main`), each command under a throwaway HOME:
- Cited paths and lines: `git grep -n 'Ground any one claim'` prints `docs/design.md:469`, `docs/prompts/03-spec-critic.md:43`, `factory/prompts/critic.md:43`, as the spec says. `docs/design.md:467-474` is the PROCESS block quoted in Evidence, word for word. `docs/principles.md:44-45` holds "runs no test suite and builds nothing (#73, `factory/prompts/critic.md`)"; "## Spiking" is the file's last section and the file is 178 lines. `docs/changelog.md`'s last entry is 58 (#73). `diff factory/prompts/critic.md docs/prompts/03-spec-critic.md` shows one line, `round 2` against `round {2}`. `git show f25dffe --stat` matches the Evidence (added lines in the design doc, the two prompt copies, principles, changelog). `.factory/answers/T-0034-acceptance-2026-10-08.md` holds both quoted sentences.
- Absence claims: `git grep` for the six removed phrases over `README.md`, `dev/` and `tests/factory/` finds nothing; `grep -rn 'Ground any\|build nothing' tests/factory` finds nothing. The only test naming the critic prompt is `tests/factory/test_writing_standard.py:73`, which compares the design block with its `docs/prompts/` copy; the change keeps them equal, so "Tests to change: none" holds.
- Acceptance commands, all six non-trivial scenarios run as written on the base: scenario 1 prints `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged` then `critic copy=SAME doc=7/8 run=7/8 gone=6 fill=unchanged`; scenario 2 prints `critic batch=1 suite=1 scratch=0 cap=1 build=1`; scenario 3 prints `sections_changed=0 writer=0 others=0`; scenario 4 prints `CONTIGUOUS` then `entries73=1 implemented=0 builds=1 status=1`; scenario 5 prints `CONTIGUOUS` then `1`; scenario 6 prints `bound=1 nobuild=1 scratch=0 whole=0 replay=0`. Every base output matches verification.md, so each NEW item fails today for the stated reason. Each phrase list is specific enough that dropping the Turn economy paragraph, the kept "finding or question" sentence or the design-block re-copy would fail scenario 1, and a run-copy-only edit would fail `copy=SAME`.
- Request and decision log: the request's items A-D and its "Then" line are as the spec describes them. The spec overturns the 2026-10-08 T-0034 "builds nothing" and per-claim-cap lines of the decision log and says so, with the operator's acceptance record as authority; the no-suite line stands. No conflict with another open ticket that I can see.

Findings

[BLOCKING] 6 Decisions, first bullet
Problem: The first sentence turns on two names the human-facing sections never gloss, "T-0034" and "standing decision", and the sentence is the one that tells the gate operator they are overturning an earlier decision of their own.
Evidence: `grep -n 'T-0034' ` over the spec finds it only in Evidence bullet 1 (inside a file path) and in this bullet; neither says that T-0034 is the ticket that applied #73, and nothing says a standing decision is one later tickets must keep. The rubric makes an unglossed system-specific term in a first paragraph of Decisions blocking even when the reader could work it out, and here the reader must, to know what is being overturned. The fix is a phrase, not a rewrite.
Suggested fix: Open the bullet "This change overturns part of a standing decision, one later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: ..." and keep the rest as is.

[SHOULD-FIX] 6 Problem, second paragraph; Evidence, bullet 6; Decisions, bullets 2 and 3
Problem: Three more factory terms appear unglossed: "intakes" (Problem, "replayed three past intakes"), "Current truth for `harness-docs`" (Evidence) and "item B" / "item C" / "the triage" (Decisions), which the operator can follow only with the request and the triage run open beside the spec.
Evidence: Read as the gate operator: an intake is a ticket's run from request to approved spec, current truth is the archived spec that describes the repository as built, item B/C are the request's lettered proposals, and the triage is the first role, which sorts a request before the spec writer sees it. None of those is said anywhere in the spec.
Suggested fix: Gloss each once at first use ("three past intakes, tickets run from request to approved spec"; "the archived requirements for this repository, called current truth"; "the request's item C, its principles.md change"; "the triage, the role that sorts a request before the writer").

[NIT] 1 design.md part C, Spiking replacement text, and changelog entry 59
Problem: Part C says "#74's replay of three past intakes", but the replay was the operator's acceptance of #73 (T-0034), run before #74 existed; entry 59 gets it right ("the operator's replay").
Evidence: `.factory/answers/T-0034-acceptance-2026-10-08.md` is titled "#73 (T-0034) operator acceptance" and names the follow-up ticket as the revert, not the replay.
Suggested fix: In part C write "The replay that accepted #73, three past intakes (#49, #51, #57) with the same inputs, found ...", and keep "#74 removed the cap ...".

[NIT] 1 Evidence bullet 4 against Root cause
Problem: Evidence gives the Spiking section as lines 169-178 and Root cause as 171-178.
Evidence: The "## Spiking" heading is at line 169 and its paragraph starts at 171, so both are right about different things; a reader comparing the two will stop on it.
Suggested fix: Use one range, or say "heading at 169, paragraph 171-178".

Not blocking, noted so the operator sees the one judgment call: the spec keeps the #73 sentence "A claim you could settle only by running a test suite or building the change is a finding for the writer, or a question", which the request's item A does not ask to keep, and adds the scratch-experiment allowance beside it. Decisions bullet 2 states this choice and its reason, and the two sentences do not contradict each other (an experiment in the critic's scratch directory is not a build of the change), so it is declared, not hidden. If the operator wants the fuller revert, deleting that sentence changes only scenario 1's phrase list.

Prior findings: none (round 1).

round 2 · spec v2 · run-0332-critic · APPROVE

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

## Verifier results

9a87c3e3983a8dd04c7e21f9dd6fdfe99dfe5a41 · T-0035.1 · VERIFIED · run-0334-verifier
