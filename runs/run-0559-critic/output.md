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

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding re-checked against the repository and two acceptance commands run today; only the built prototype's counts are unverified, and the verifier runs them
ESCALATIONS: none
