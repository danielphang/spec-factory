Sub-ticket: T-0055.1 (parent T-0055, spec v3). Branch `factory/T-0055.1`, head `44e52a30cf8a9fa6adbe89015eb5ffe6b7c055bb`, base `1321c17`.

## What changed

This change adds documents only. It touches no harness code, prompt, test or protected path. Each lettered part is the spec's prototype text, applied without rewording. The parts adapted to the current base are listed under Known gaps.

- **A. `docs/north-star.md`.** A new second section, "How we know it is working", sits after the "whom the factory serves" sentence. It gives:
  - the primary metric (correct target changes per hour of operator attention), its constraint and cost as the second measure;
  - operator decisions and interventions as the stand-in for hours of attention;
  - spec-factory's merges reported on a line of their own;
  - the scorecard's five numbers as a table, and the three outside comparisons;
  - the review cadence.

  In "How it decides where effort goes", "three working rules" becomes "four". The list now opens with the new rule, "Factory work serves a target or a number". Nothing else in the file changed.
- **B. `README.md`.** README gains 8 lines, from 1,176 to 1,184 of its 1,185-line budget:
  - B1: a three-line "**North star.**" paragraph between the opening paragraph and the status table, plus a blank line.
  - B2: the rule for factory work, added to the first paragraph of "Filing a request from an issue tracker", which grows by two lines.
  - B3: two rows in "Where things live", for `STATUS.md` with `docs/reviews/`, and for `CONTRIBUTING.md`.
  - The status header's date moves from 2026-10-22 to 2026-10-23, as "Maintaining this page" asks.
- **C. New `CONTRIBUTING.md`.** It gives the rule for factory work, then the three steps (Issue, Factory ticket, Spec gate) and links to further reading.
- **D. New `STATUS.md`** (56 lines). Its sections are: the north star in one line, Scorecard, Current focus, Top of the queue, Open experiments and Links. Every figure in the Scorecard section is copied from the baseline review.
- **E. New `docs/reviews/TEMPLATE.md`.** It holds the six numbered sections the request lists, in order, and a reminder that the repository is public.
- **F. New `docs/reviews/2026-10-19.md`**, the baseline review. I generated it with the spec's own command from `02e403f:requests/T-0055.md`, not by retyping it. It has 100 lines, and only the first line differs from the operator's text.
- **G. `docs/changelog.md`.** One entry for issue #116, numbered **77**, placed before the closing `Declined:` line.

## Acceptance results

I ran every command from the worktree root through the HOME wrapper, under bash. I ran them again under `/bin/sh` and the output was identical (`diff` printed nothing). Before = base `1321c17`; after = `44e52a3`.

| Scenario | Before | After |
|---|---|---|
| North star holds the measurement section… | `heading=0 second=0 terms=0 rows=0 measures=4 serves=1` | `heading=1 second=1 terms=13 rows=5 measures=4 serves=1` |
| North star's working rules include the rule… | `rule=0 terms=0 four=0 three=1` | `rule=1 terms=4 four=1 three=0` |
| README opens with the north-star paragraph… | `block=0 top=0 metric=0 links=0 readme=within` | `block=1 top=1 metric=1 links=3 readme=within` |
| Filing section states the rule… | `terms=0` | `terms=5` |
| Where things live has a row for each new file | `status=0 reviews=0 contributing=0` | `status=1 reviews=1 contributing=1` |
| CONTRIBUTING.md gives the three steps… | `missing=CONTRIBUTING.md` | `steps=Issue.\|Factory ticket.\|Spec gate.\| rule=4 northstar=1 ws=clean` |
| STATUS.md has its sections and links… | `missing=STATUS.md` | `lines=within sections=## Scorecard\|## Current focus\|## Top of the queue\|## Open experiments\|## Links\| northstar=1 links=5 scorecard=3 rows=6 cells_unsourced=0 prose_unsourced=0 ws=clean` |
| Review template's sections are the six… | `missing=docs/reviews/TEMPLATE.md` | the six `## 1.` … `## 6.` headings in order, then `decided=yes experiment=yes stats=yes baseline=yes status=yes` |
| Baseline review matches the operator's text… | `missing=docs/reviews/2026-10-19.md` | `head=# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19` / `body=verbatim ws=clean` |
| No relative link in the three new pages is broken | `STATUS.md missing` / `CONTRIBUTING.md missing` / `docs/reviews/TEMPLATE.md missing` | `STATUS.md relative=some broken=0` / `CONTRIBUTING.md relative=some broken=0` / `docs/reviews/TEMPLATE.md relative=some broken=0` |
| Changelog records issue 116… | `CONTIGUOUS` / `entries=0 terms=0 last=1` | `CONTIGUOUS` / `entries=1 terms=7 last=1` |

Every "before" line matches the spec's "Today" line, and every "after" line matches its THEN line exactly.

**Regression check.** Current truth is the store's `openspec/specs/harness-docs/spec.md`. I took its 66 scenarios that run no `factory`, `uv run` or `pytest` command and ran them on a detached worktree of the base and on the head. `diff` of the two outputs printed nothing (exit 0). Among them:
- README's 1,185-line budget prints `readme=within`;
- the whitespace check over `README.md docs dev .factory/context.md` prints `exit=0`.

Some scenarios print the same "No such file" error on base and on head, because they rely on a temporary file that an earlier step creates. This change does not affect them. I removed the temporary worktree afterwards.

**Gates**, run exactly as written at `44e52a3`:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `627 passed in 153.27s`.

## Tests added/changed

None. The parent's "Tests to change" is none, and this change is documents only. The acceptance scenarios above are the checks.

## Known gaps and uncertainties

- **The changelog entry is numbered 77, not 76 as the spec's part G says.** T-0058.1 merged into `main` after this spec was written (`1321c17`) and took entry 76. The acceptance check requires the entries to stay numbered without a gap, so 77 is the only correct number. The entry's text is the prototype's, unchanged.
- **README ends at 1,184 lines, not 1,182 as the spec predicted.** The spec measured 1,174 on `788a201`. T-0058.1 has since added 2 lines, so the base is 1,176. This change adds exactly 8 lines, as the spec specifies. One line of the 1,185 budget is left. The spec reserved room for T-0058 so that both orders of merge would fit, and T-0058 has now merged.
- **README's status date is now 2026-10-23.** The spec says to bump it if the merge lands after 2026-10-19. It was 2026-10-22 on the base, and today is 2026-10-23. If the merge lands on a later day, that date is stale by the difference.
- **The STATUS.md prose check is weak, as the spec itself says.** The check matches one number at a time against the whole review. I also compared each STATUS.md table cell by eye against the review's tables, and the strict table check passed (`cells_unsourced=0`).
- **The baseline review contains commit SHAs from the Nanobot fork, in a public repository.** The operator kept them deliberately (spec Decisions). No acceptance check reads them.
- **The operator steps are still to do:** create the `experiment` label, and optionally reword the About text. STATUS.md and the template already link the label's issue query, which shows nothing until the label exists.

## Out-of-scope observations

- Several current-truth harness-docs scenarios read `$TMPDIR/t0029-prompt.sh`, a file an earlier step is supposed to write. Run one at a time, they print "No such file" on the base as well. This is a property of how those scenarios are written, not something this change caused.

## Responses to findings

Round 1; none.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its exact THEN line under bash and under /bin/sh. Both gates passed, and the 66 current-truth doc scenarios print the same on the base and the head.
ESCALATIONS: none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
