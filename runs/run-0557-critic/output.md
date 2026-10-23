# Critic review of T-0055 spec v2 (round 1 of critic review; round 1 of the writer stopped at NEEDS-HUMAN)

What I checked on `main` at `788a201`, from `~/dev/spec-factory`:
- Cited paths: `docs/north-star.md:14-19` (four measures, no target), `:21` (the serves sentence), `:60-61` ("Measure before and after" under "And three working rules"), `README.md:1-12` and `:1091` (the `docs/north-star.md` row), `docs/decided-against.md`, changelog entry 75 then `Declined:`. All as the spec says. No `CONTRIBUTING.md`, `STATUS.md` or `docs/reviews/`. README is 1,174 lines.
- Store commit `02e403f:requests/T-0055.md` exists in this repository's object store (the `factory-store` branch is local) and its baseline block has the headings the STATUS.md scenario cuts on (`## The Nanobot port`, `## Spec-factory (factory work)`, `## Escapes`). Every one of the twelve cells `STATUS.md` quotes appears in that instance's table in the form the scenario greps (`| 27 |`, `| 66 min (`, `| 15 / 436 |`, and so on).
- Acceptance commands run through the HOME wrapper today: the north-star section scenario (printed `heading=0 second=0 measures=4 serves=1`), the working-rules scenario (`four=0 three=1`), the changelog scenario (`CONTIGUOUS`, `entries=0 last=1`), the filing scenario (`terms=0`), the Where-things-live scenario (`status=0 reviews=0 contributing=0`) and the relative-links scenario (three `missing` lines). All match the spec's "today" lines.
- Part F's generation command, run into my scratch directory: 100 lines, first line the new title, `body=verbatim` by the scenario's own hash comparison, no trailing whitespace.
- `grep -rlE 'north-star|STATUS\.md|CONTRIBUTING|1185|docs/reviews' tests factory agents` prints nothing, exit 1. Current truth pins only the serves sentence and the issue-110 entry, both kept. "Tests to change: none" holds.
- Read-only GitHub checks: no label named `experiment` exists; the repository already has an About description (see the NIT below).
- Not checked: the 76 current-truth scenario replays on the prototype, and README's final line count after the implementer's edits. Both need the built change.

## Findings

[BLOCKING] 6 Decisions, first bullet
Problem: The first paragraph of Decisions says "until the store records operator time", and no human-facing section before it glosses "the store", a term specific to this system; it also names "T-0056" and "question 1" before either is introduced.
Evidence: Problem and Evidence never use the word "store" except as "the store branch at commit `02e403f`" (Evidence, bullet 4), itself unglossed. `docs/writing.md` rule 2 and the rubric's reading-as-operator test make an unglossed system term in a section's first paragraph blocking. The Proposed change does gloss it ("Store, the factory's record of every ticket and run") but that section is not one the gate operator is held to read.
Suggested fix: On first use, in Problem or in that bullet, say what the store is (the factory's record of every ticket and run, kept on its own branch) and write "T-0056, the scorecard ticket (#117)" and "round-1 question 1" so the references are introduced.

[BLOCKING] 5 Decisions, "README stays within 1,185 lines" and Proposed change B
Problem: This spec leaves README at exactly its 1,185-line budget while T-0058, at the same spec gate, also edits README and expects to stay within 1,185, so whichever of the two merges second fails the current-truth scenario "README is at most 1,185 lines" at its gate.
Evidence: `.factory/store/tickets/T-0058.yaml` is `awaiting-spec-gate`. `.factory/store/specs/T-0058.md:107-112` replaces README line 611's last sentence (90 characters on that line today) with one about 160 characters long, which wraps to a second line, and ends "README stays within its 1,185-line budget", a REGRESSION it lists at its line 252. 1,174 + 11 (this spec's B1 to B3 with their two blank lines) = 1,185, so one more line is over. T-0058 is not in "Approved changes not yet archived", so the rubric's strict clause does not fire, but the outcome is a predictable spurious park for one of two tickets the operator is approving in the same sitting. T-0049's standing decision (decision log, 2026-10-19) set the budget as "the prototype's lines plus 12 lines of slack" and this spec consumes all of it.
Suggested fix: Either raise the budget in this spec to 1,185 plus a few lines of slack, modifying the current-truth requirement and the two scenarios that name 1,185 (the spec's own README scenario and T-0049's), or cut two or three lines from README elsewhere so the change lands under budget; in either case name T-0058 under Decisions so the operator sees the pair.

[NIT] 1 Proposed change B, first line, and Decisions, "README stays within 1,185 lines"
Problem: "Nine lines added" and "four lines ... three ... and two table rows" count only text lines; with B1's and B2's trailing blank lines the change adds 11, which is what takes 1,174 to 1,185.
Evidence: README lines 1 to 7 and 836 to 838 today; 1,174 + 9 = 1,183, not "exactly at its budget".
Suggested fix: Say eleven lines, two of them blank.

[NIT] 1 Operator steps, step 2
Problem: The step reads as if the About description were empty, but one is already set and says nearly the same thing.
Evidence: `gh repo view danielphang/spec-factory --json description` prints "A spec-driven AI software pipeline: a written request becomes merged, verified code with as little operator attention as the work allows."
Suggested fix: Quote the current text and make the step "replace it if you prefer the new wording", so the operator knows they are overwriting.

[NIT] 5 Decisions, "One changelog entry records the change", and Proposed change G
Problem: The decision gives no reason, and T-0049's standing decision declined an entry because `docs/changelog.md` records changes to `docs/design.md`, which this change does not touch.
Evidence: Decision log line "2026-10-19 T-0049 No changelog entry. `docs/changelog.md` records changes to `docs/design.md`, which this change leaves alone." Precedent the other way: entry 73 (issue #110) was added by commit `21f90c4`, which changed no `docs/design.md`; README's row calls the file "The design document's changelog".
Suggested fix: Keep the entry and say in the Decision why, citing entry 73 as the precedent for a documents-only change to the north star, so the two decisions do not read as a contradiction.

Not findings, noted for the gate: the baseline review will publish nine short commit SHAs from the Nanobot fork; the spec records this under Decisions and Risk, the operator asked for the baseline verbatim, and the spec text itself copies none of them. The STATUS.md prose check is weak, as Verification says; its table check is the strict one, and I confirmed each quoted cell's source.

STATUS: REVISE
CONFIDENCE: high, every cited path and five acceptance commands checked on 788a201, and the T-0058 overlap read from its spec at the gate
ESCALATIONS: none
