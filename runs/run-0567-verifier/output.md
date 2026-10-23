Commit: 44e52a30cf8a9fa6adbe89015eb5ffe6b7c055bb (branch `factory/T-0055.1`, base `1321c1710aa703876eac6c66df7e38d1dd92d10a`, which is `main`)

How I ran them: I extracted the 11 WHEN commands mechanically from the sub-ticket input, stripping the leading "- WHEN `" and the trailing backtick. I then diffed them against the WHEN lines of `.factory/store/specs/T-0055/v3.md`, and they were identical. Each command ran from the worktree root through the HOME wrapper, under bash. On the PR I ran them again under zsh and `/bin/sh`, and the output was identical (`diff` printed nothing). Base = a detached worktree at `1321c17` in my scratch directory, removed afterwards. Outputs are in `scratch/out-pr.txt` and `scratch/out-base.txt`.

Per criterion:
- NEW | The north star holds the measurement section and keeps its measures and target sentence | base `heading=0 second=0 terms=0 rows=0 measures=4 serves=1` | PR `heading=1 second=1 terms=13 rows=5 measures=4 serves=1` | PASS
- NEW | The north star's working rules include the rule for factory work | base `rule=0 terms=0 four=0 three=1` | PR `rule=1 terms=4 four=1 three=0` | PASS
- NEW | README opens with the north-star paragraph and stays within its budget | base `block=0 top=0 metric=0 links=0 readme=within` | PR `block=1 top=1 metric=1 links=3 readme=within` | PASS
- NEW | The filing section states the rule for factory work | base `terms=0` | PR `terms=5` | PASS
- NEW | Where things live has a row for each new file | base `status=0 reviews=0 contributing=0` | PR `status=1 reviews=1 contributing=1` | PASS
- NEW | CONTRIBUTING.md gives the three steps and the rule, and links the north star | base `missing=CONTRIBUTING.md` | PR `steps=Issue.|Factory ticket.|Spec gate.| rule=4 northstar=1 ws=clean` | PASS
- NEW | STATUS.md has its sections and links, and quotes only the baseline review's figures | base `missing=STATUS.md` | PR `lines=within sections=## Scorecard|## Current focus|## Top of the queue|## Open experiments|## Links| northstar=1 links=5 scorecard=3 rows=6 cells_unsourced=0 prose_unsourced=0 ws=clean` | PASS
- NEW | The review template's sections are the six the request lists, in order | base `missing=docs/reviews/TEMPLATE.md` | PR prints the six headings `## 1. Scorecard against the last review` … `## 6. Decisions and the new queue order` in order, then `decided=yes experiment=yes stats=yes baseline=yes status=yes` | PASS
- NEW | The baseline review matches the operator's text after its first line | base `missing=docs/reviews/2026-10-19.md` | PR `head=# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19` / `body=verbatim ws=clean` | PASS
- NEW | No relative link in the three new pages is broken | base `STATUS.md missing` / `CONTRIBUTING.md missing` / `docs/reviews/TEMPLATE.md missing` | PR `STATUS.md relative=some broken=0` / `CONTRIBUTING.md relative=some broken=0` / `docs/reviews/TEMPLATE.md relative=some broken=0` | PASS
- NEW | The changelog records issue 116 in one entry without a numbering gap | base `CONTIGUOUS` / `entries=0 terms=0 last=1` | PR `CONTIGUOUS` / `entries=1 terms=7 last=1` | PASS

Every base output equals the spec's "Today" line, so each NEW criterion fails on base for the reason the spec states, and passes on the PR.

Gate suite: PASS
- `git diff --check main...HEAD` (wrapped, exactly as written): no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` (wrapped, exactly as written): `627 passed in 145.16s (0:02:25)`, exit 0.

Probes:
- The new files against the spec's prototype text. I extracted each fenced block from v3.md and diffed it against the file. `CONTRIBUTING.md`, `STATUS.md` and `docs/reviews/TEMPLATE.md` are identical to parts C, D and E. The north star's new section is identical to A1, and it sits at line 23, directly after the "serves" sentence at line 21, as the second `## ` section. The README and north-star diffs hold only parts A2, B1, B2 and B3, plus the status date moving from 2026-10-22 to 2026-10-23. Nothing else in those files changed. → OK
- The baseline review, regenerated. I re-ran part F's own generation command and `cmp` found the output byte-identical to `docs/reviews/2026-10-19.md` (100 lines). → OK
- The STATUS.md figures, checked by hand, because the spec itself calls the scenario's prose check weak. I compared every one against the review. All 12 table cells match the review's "Whole period" column: 27/42, 1 + 1 / 5 + 3, 5.0/3.1, 66 min / 67 min, 21.9 h / 10.6 h, and 15 / 436 / 18 / 500. The prose figures also match: "5 more … to the record alone" matches the record-only escapes, 5. "Only 1 of its changes merged after that" matches 10-12→10-19 changes merged, 1. → OK
- The changelog entry is numbered 77, not the 76 that part G gives. Entry 76 on `main` is T-0058.1's ("After four small harness defects…"), which merged after the spec was written. Renumbered to 76, the entry's text is identical to the spec's. The criterion requires contiguous numbering, so 77 is the correct number. → OK (a stale number in the spec, not a defect in the change)
- README's budget. README is now 1,184 lines, not the 1,182 the spec predicted, because T-0058.1 added 2 lines first. The change adds exactly 8. The north-star paragraph appears on the first screen, at lines 7-9. I ran four current-truth harness-docs scenarios on both base and PR: the 1,185-line budget, the whitespace checks over the documents, and the combined README/changelog check. They print the same on both. → OK, with one line of budget left (see the escalation below)
- Anchor links. None of the three new pages has an anchor link (`grep` found none), so the link check's exclusion of `#` hides nothing. → OK

Not verified: the GitHub URLs in STATUS.md and CONTRIBUTING.md, including the `experiment` label query, which shows nothing until the operator creates the label. I also did not check the claim that the queue top (#117, #105, #118) matches issue #96 today. Both need network access, and the GitHub connector failed to connect in this session.

STATUS: VERIFIED
CONFIDENCE: high. All 11 commands match their THEN lines exactly, under three shells, and each fails on base as the spec states. Both gates pass, and the new files are byte-identical to the spec's prototype text.
ESCALATIONS:
- README is now 1,184 of its 1,185-line budget. The spec's room-for-T-0058 reasoning assumed 1,182, so the next ticket that adds 2 or more lines to README will have to raise the budget or trim. This is outside this sub-ticket's criteria, and nothing fails today.
