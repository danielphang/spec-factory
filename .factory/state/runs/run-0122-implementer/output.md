Sub-ticket: T-0014.1 (ST-1 / Add rules 9–12 and code counterpart lines to the writing standard). Branch `factory/T-0014.1`, commit `c64183a` on base `ba4618a`. There is no remote, so the PR is this branch plus this description.

## What changed

All of the change is in `docs/writing.md`. That file is the writing standard: the page every role (each agent in the factory's pipeline) follows when it writes something a person reads. The change only adds lines (45 of them). No existing line is edited, moved or removed. The text is copied from the approved spec v3's design.md and is not rewrapped.

- **A. Intro sentence.** The two lines starting "Where a rule matches a code-design principle, a `Code counterpart:` line names it" are now directly after "example taken from the factory's own writing, and its rewrite." They continue that paragraph.
- **B. Counterpart lines on existing rules.** Rules 1, 2, 3, 5, 6 and 7 each gain one `Code counterpart:` line. Each line sits directly before the rule's `Before (` line, with the exact text from design.md's table. Rules 4 and 8 get none.
- **C. Rules 9–12.** These are: one name per concept, one mode per section, a heading states what is under it, and parallel facts go in a table. They sit between rule 8's After paragraph and the closing "`README.md` is a worked example…" line, with a blank line after each rule. Each has a Check, a Code counterpart, a Before and an After line.

Wording check. I joined the inserted lines and compared them with the design.md text for parts A, B and C, taken from the pinned spec in my input. The joined texts are identical (`diff` printed nothing). Compared line by line, the only difference is the blank line after rule 12. design.md asks for that line ("a blank line after each rule").

## Acceptance results

All commands ran in the worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0014.1`, the change branch. The ticket's commands begin with `cd ~/dev/spec-factory`, which is the `main` checkout. The change is not on `main` until it merges, so on this branch the worktree is the equivalent place to run them. "Before" is the base `ba4618a`; "after" is `c64183a`.

| # | Criterion | Before | After |
|---|---|---|---|
| 1 | twelve numbered rules with the four new headings (NEW) | `rules=1,2,3,4,5,6,7,8 new=0` | `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4` |
| 2 | each new rule has one check, one before, one after (NEW) | `9:000 10:000 11:000 12:000 ` | `9:111 10:111 11:111 12:111 ` |
| 3 | example phrases are in the standard and match the README (NEW) | `writing=nnnnnn readme=nyyyny` | `writing=yyyyyy readme=nyyyny` |
| 4 | counterpart lines on the agreed rules, in place (NEW) | `intro=0 rules=000000000000 misplaced=0` | `intro=0 rules=111011101111 misplaced=0` |
| 5 | under budget, nothing removed, clean whitespace (REGRESSION) | `lines=86 wide=0 removed=0 ws=clean` | `lines=131 wide=0 removed=0 ws=clean` |
| 6 | only the standard changes (NEW) | `changed=[]` (no commit yet) | `changed=[docs/writing.md]` |
| 7 | the standard's existing tests still pass (REGRESSION) | `5 passed in 0.70s` | `5 passed in 0.51s` |

What the "after" column shows:
- Criteria 1–4: the four rules exist, each with one check and one example pair. The standard now quotes all six example phrases. The README still matches: it has the four after-phrases and neither before-phrase. Counterpart lines are on every agreed rule except 4 and 8, and none is out of place.
- Criterion 5: the file is 131 lines, the same as the spec's scratch build and under the 140-line budget. No line is wider than 100 characters, no line was removed since `e703c1b`, and there are no whitespace errors.
- Criteria 6 and 7: the branch changes only `docs/writing.md`, and the standard's existing tests still pass.
- Every before output matches the "today" output that verification.md records, so the spec matched the checkout before the change.

Gate commands, each run from the worktree exactly as written:
- `git diff --check main...HEAD`: no output, exit 0. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 103.88s (0:01:43)`. The whole harness test suite passes.

## Tests added/changed

None. The approved spec sets "Tests to change: none". Criterion 6 also requires that `docs/writing.md` is the only changed file, so a new test file would fail it. The acceptance commands above are the checks for this change.

## Known gaps and uncertainties

- I did not write a test and watch it fail first (step 3 of my process). A new test file would break criterion 6, as noted above. Instead, the four NEW acceptance commands served as the failing checks: they failed before the change and pass after it.
- `main` moved one commit after the branch was cut: `431e349`, "issues: #27 indexed". That commit changes neither `docs/writing.md` nor `README.md`. Criterion 6 uses the merge base, so its result is unaffected.
- The change reaches the roles only after the operator moves the runtime to the merge commit. The runtime is the second checkout at `~/dev/spec-factory-harness`, pinned to one commit, which the factory runs tickets from. The spec makes the operator's rewrite and comprehension test the acceptance before that move (Operator step 0). I did not touch the runtime checkout.

## Out-of-scope observations

- The README's "Maintaining this page" summary of the standard will not mention the four new rules until a later change, as the spec's out-of-scope list notes.

## Conflict resolution note

The merge gate refused the branch because its head `c64183a` did not contain `main` (`431e349`, "issues: #27 indexed", one line added to `dev/issues.md`). I merged `main` into the branch with no rebase: merge commit `89e8b7d`. Git reported no conflict, since `main`'s commit touches only `dev/issues.md` and the branch touches only `docs/writing.md`. `git diff c64183a 89e8b7d --stat` lists only `dev/issues.md | 1 +`, so `docs/writing.md` is byte-for-byte as reviewed and verified. After the merge, all seven acceptance commands, run in the worktree, gave the same outputs as the "after" column above (criterion 6 still prints `changed=[docs/writing.md]`; criterion 7 printed `5 passed in 0.40s`). `git diff --check main...HEAD` printed nothing (exit 0), and `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `126 passed in 100.52s (0:01:40)` (exit 0).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run after the commit, and the inserted text matches the spec's text exactly.
ESCALATIONS: none
