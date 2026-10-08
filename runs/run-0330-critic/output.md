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

STATUS: REVISE
CONFIDENCE: high. Every cited path, line, commit and base output was checked and matched; the one blocking item is a gloss the rubric requires in the sentence that states the authority to overturn an earlier decision, and it needs no change to the design or the acceptance.
ESCALATIONS: none
