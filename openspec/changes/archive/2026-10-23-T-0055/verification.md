## Acceptance

Run every command from the repository root of the checkout under test, through the HOME wrapper. "Today" means `main` at `788a201`, run on 2026-10-20. The baseline-review scenario reads commit `02e403f` on the store branch, which every checkout of this repository shares.

- The north star holds the measurement section and keeps its measures and target sentence → NEW. Today it prints `heading=0 second=0 terms=0 rows=0 measures=4 serves=1`: there is no measurement section, while the four measures and the target sentence are already there.
- The north star's working rules include the rule for factory work → NEW. Today it prints `rule=0 terms=0 four=0 three=1`: the section still introduces three working rules, and none of them is the rule for factory work.
- README opens with the north-star paragraph and stays within its budget → NEW. Today it prints `block=0 top=0 metric=0 links=0 readme=within`: README has no north-star paragraph.
- The filing section states the rule for factory work → NEW. Today it prints `terms=0`.
- Where things live has a row for each new file → NEW. Today it prints `status=0 reviews=0 contributing=0`.
- CONTRIBUTING.md gives the three steps and the rule, and links the north star → NEW. Today it prints `missing=CONTRIBUTING.md`.
- STATUS.md has its sections and links, and quotes only the baseline review's figures → NEW. Today it prints `missing=STATUS.md`.
- The review template's sections are the six the request lists, in order → NEW. Today it prints `missing=docs/reviews/TEMPLATE.md`.
- The baseline review matches the operator's text after its first line → NEW. Today it prints `missing=docs/reviews/2026-10-19.md`.
- No relative link in the three new pages is broken → NEW. Today it prints `STATUS.md missing`, `CONTRIBUTING.md missing`, `docs/reviews/TEMPLATE.md missing`.
- The changelog records issue 116 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `entries=0 terms=0 last=1`: there is no entry for issue #116.

On the prototype (Proposed change A to G applied to a clone of this repository at `788a201`, in this run's scratch directory; the clone carries the store branch's commits), every scenario printed exactly its THEN line. The STATUS.md scenario's prose check matches figures one number at a time, so it is weak: a mistyped 6 for 5 passes it, because 6 occurs elsewhere in the review. Its table check is strict, and it caught both mistyped cells I tried (Evidence). The current-truth harness-docs scenarios still apply after this change, among them README's 1,185-line budget (the prototype has 1,182 lines), the whitespace check over `README.md`, `docs/` and `dev/`, and the north star's target sentence. All 76 that need no harness run printed the same on the prototype as on `788a201` (Evidence).

## Responses

Critic round 1 (review of v2):
- [BLOCKING] Decisions, first bullet, "the store", "T-0056" and "question 1" unintroduced: FIXED. Problem's first paragraph now says what an instance and the store are. The bullet names "round-1 question 1" and what it asked, introduces T-0056 as the ticket that adds the scorecard to `factory stats` (#117), and says what `factory stats` is. The question-2 bullet names its question too.
- [BLOCKING] README left at exactly 1,185 lines while T-0058 also adds to README: FIXED, by landing under the budget rather than raising it. README now gains 8 lines and ends at 1,182 on the prototype. B1 is three lines plus its blank, B2 joins the filing section's first paragraph (two more lines, no new blank), and B3 is the same two rows. T-0058 adds about one line by my reading of its Proposed change E (Evidence), so both stay within 1,185 in either merge order. I did not raise the budget: T-0058's spec checks the figure 1,185 itself as a regression, so raising it here would not prevent its park if it merged second. Decisions names T-0058. The filing rule no longer repeats the `docs/north-star.md` pointer, which the north-star paragraph on README's first screen carries. Its requirement and scenario change to match; the scenario is renamed "The filing section states the rule for factory work".
- [NIT] Line count ignored blank lines: FIXED. Proposed change B says "Eight lines added, one of them blank" and gives B2 as a replacement, so the count adds up: 4 + 2 + 2 = 8, and 1,174 + 8 = 1,182, which is what the prototype has.
- [NIT] Operator step 2 read as if the About text were empty: FIXED. The step quotes the current text, says it already meets the request, and offers the overwrite only as an option. Evidence records the `gh repo view` output.
- [NIT] Changelog decision gave no reason and seemed to contradict T-0049: FIXED. The decision now gives the reason and cites entry 73 (commit `21f90c4`, which changed `docs/north-star.md` and README but not `docs/design.md`) as the precedent. It also says how T-0049's case differs: T-0049 changed neither `docs/design.md` nor the north star.

Round 2 of the writer (v2) applied the operator's Answer 1 to the two round-1 questions; that record is unchanged and lives in the decision log.

Out-of-scope observations:
- README's "Related work and history" says "The store holds 54 tickets and 68 sub-tickets". In round 1, `ls .factory/store/tickets` counted 60 ticket files and 68 sub-ticket files. That figure belongs to whichever change next re-derives it.
- The briefing's rule against copying Nanobot commit SHAs into a spec conflicts with the operator's request for the baseline verbatim. I followed the operator and recorded it under Decisions and Risk.

## Critic rounds

round 1 · spec v2 · run-0557-critic · REVISE

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

round 2 · spec v3 · run-0559-critic · APPROVE

# Critic review of T-0055 spec v3 (round 2 of critic review)

Round 2: I reviewed whether the round-1 findings are resolved and the text that changed between v2 and v3. Checks ran on `main` at `788a201`, which is still the tip of `~/dev/spec-factory`, with a clean tree.

What I checked:
- README is 1,174 lines. The "Filing a request from an issue tracker" section's first paragraph is two lines and its second line is exactly `kept by hand in both directions.`, so B2's replacement is well defined. The next `### ` heading is "Running many tickets: runner and operator sessions", which the filing scenario cuts on. README has no Markdown links (`grep -c '](' README.md` prints 0), as Evidence now says. The six new README lines in B1 and B2 are 98 to 102 characters, within README's wrap.
- The north star's "serves" sentence is at line 21, followed by a blank line and `## What it will not trade away` at line 23, so A1's insertion makes "How we know it is working" the second `## ` section as the requirement asks. Line 59 still reads "And three working rules that follow from them:".
- T-0058: `.factory/store/tickets/T-0058.yaml` is `awaiting-spec-gate`. Its spec at lines 107 to 112 edits README at lines 611, 619, 952 and 529 and requires README within 1,185; line 252 lists that budget as a REGRESSION. README line 611 today is 92 characters and the replacement sentence is about 160, so that edit wraps once. Lines 619 and 952 are 97 and 83 characters today; if their replacements also wrap, the pair still lands at 1,185 or under, because this change now leaves three lines of slack. The round-1 overlap is resolved in either merge order.
- Commit `21f90c4` changed `README.md`, `docs/changelog.md`, `docs/north-star.md` and `docs/standards.md`, not `docs/design.md`; `1058db5` changed `README.md` alone. Both as Evidence states. Changelog entries 73 to 75 are contiguous and the file ends with `Declined:`.
- `gh repo view danielphang/spec-factory --json description` prints the About text the spec quotes, word for word.
- The baseline at `02e403f:requests/T-0055.md` names exactly four Nanobot-fork SHAs (lines 60, 61 and 63 of the baseline block), so the Decision's "four" is right. My round-1 note said nine; that count included spec-factory SHAs and was wrong.
- Acceptance commands run today through the HOME wrapper: the filing scenario printed `terms=0`, and the README north-star scenario printed `block=0 top=0 metric=0 links=0 readme=within`. Both match the spec's "today" lines. The filing scenario's five phrases each appear contiguously in B2 once its lines are joined by a space, so the scenario passes on the proposed text and fails on a text that omits any one phrase.
- Not checked: the prototype's 1,182-line README and the 76 current-truth replays. Both need the built change; the verifier runs them.

## Findings

No blocking findings. No SHOULD-FIX or NIT findings on the changed text.

Noted for the gate, not findings: the baseline review will publish four short commit SHAs from the Nanobot fork; the spec records this under Decisions and Risk, the operator asked for the baseline verbatim, and the spec text itself copies none of them. The STATUS.md scenario's prose check is weak, as Verification says; its table check is strict, and round 1 confirmed each quoted cell's source.

## Prior findings (round 1)

- [BLOCKING] 6 Decisions, first bullet, "the store", "T-0056" and "question 1" unintroduced: RESOLVED. Problem's first paragraph now glosses instance and store. The bullet names round-1 question 1 and what it asked, introduces T-0056 as the ticket that adds the scorecard to `factory stats` (#117), and says what `factory stats` is. The question-2 bullet names its question.
- [BLOCKING] 5 README left at exactly 1,185 lines while T-0058 also edits README: RESOLVED. The change now adds 8 lines (B1 three plus a blank, B2 two by joining the first paragraph, B3 two rows), so README ends at 1,182 with three lines of slack. T-0058 adds one to three lines by my reading of its spec, so both tickets fit in either merge order. Decisions names T-0058 and gives the reason for not raising the budget.
- [NIT] 1 Line count ignored blank lines: RESOLVED. "Eight lines added, one of them blank"; 1,174 + 8 = 1,182.
- [NIT] 1 Operator step 2 read as if the About text were empty: RESOLVED. The step quotes the current text, says it meets the request, and offers the overwrite as an option.
- [NIT] 5 Changelog decision gave no reason: RESOLVED. The decision cites entry 73 (commit `21f90c4`) as the precedent and says how T-0049 differs. I confirmed both commits' file lists.

## Verifier results

44e52a30cf8a9fa6adbe89015eb5ffe6b7c055bb · T-0055.1 · VERIFIED · run-0567-verifier
