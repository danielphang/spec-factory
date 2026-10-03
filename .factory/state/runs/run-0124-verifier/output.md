Commit: 89e8b7d3ec7536f788d449d009f28df44fed3c1a (merge of `main` 431e349 into the branch tip c64183a). Base: 431e3492d977c01f5ac3252f94b6f40f08b6c043.

Where the commands ran: in the verifier worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0124-verifier/wt`, which had a clean `git status`. The ticket says to run them from `~/dev/spec-factory`, but that checkout is on `main` and does not have the change yet, so the worktree is the equivalent location. I ran the PR head at 89e8b7d. For the base, I checked out 431e349 (detached) in the same worktree, ran the same script, and checked out 89e8b7d again. Every command was copied verbatim from the sub-ticket into one script.

Per criterion:

| # | Kind | Command (short name) | Base 431e349 | PR 89e8b7d | Result |
|---|---|---|---|---|---|
| 1 | NEW | twelve numbered rules with the four new headings | `rules=1,2,3,4,5,6,7,8 new=0` | `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4` | PASS |
| 2 | NEW | each new rule has one check, one before, one after | `9:000 10:000 11:000 12:000 ` | `9:111 10:111 11:111 12:111 ` | PASS |
| 3 | NEW | example phrases are in the standard and match the README | `writing=nnnnnn readme=nyyyny` | `writing=yyyyyy readme=nyyyny` | PASS |
| 4 | NEW | counterpart lines on the agreed rules, in place | `intro=0 rules=000000000000 misplaced=0` | `intro=0 rules=111011101111 misplaced=0` | PASS |
| 5 | REGRESSION | under budget, nothing removed, clean whitespace | `lines=86 wide=0 removed=0 ws=clean` | `lines=131 wide=0 removed=0 ws=clean` | PASS |
| 6 | NEW | only the standard changes | `changed=[]` | `changed=[docs/writing.md]` | PASS |
| 7 | REGRESSION | the standard's existing tests still pass | `5 passed in 1.44s` | `5 passed in 1.70s` | PASS |

What the table shows: on the base, each NEW criterion fails for the reason verification.md gives (rules 9–12 and the counterpart lines do not exist yet, and nothing has changed). On the PR, each prints exactly its THEN. Both REGRESSION criteria hold on both commits. At 131 lines the file is 9 under the 140-line budget, and it matches the spec's scratch build.

Gate suite: PASS.
- `git diff --check main...HEAD`: no output, exit 0. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 114.19s (0:01:54)`. I ran it a second time with output redirected to a file so I could capture the exit code: `exit=0`, `126 passed in 104.09s (0:01:44)`. The whole harness suite passes.

Probes:
- Word-for-word comparison (the reviewer's intermediate check, repeated here). I took the design.md text for part A, the six part-B table lines with their backticks removed, and the part-C block from the pinned spec in my input. I joined it into one line and squeezed the whitespace. I did the same with every `+` line of `git diff -U0 431e349 HEAD -- docs/writing.md`. → `cmp` reported the two identical (2908 bytes each). → OK. The inserted text is the approved wording, with nothing added or dropped.
- Existing lines kept and placement. `git diff -U0 431e349 HEAD -- docs/writing.md | grep -c '^-[^-]'` printed `0`: no existing line was removed or edited. The widest line is 99 characters. `grep -n -B1 -A1` shows the intro sentence at lines 20–21, directly after line 19 with no blank line between them, so it renders as part of that paragraph. Each `Code counterpart:` line comes straight after the last line of its rule's Check text: for rules 2 and 6 that is a continuation line (line 34 and line 70). Each comes directly before the `Before (` line, or, for rules 9, 11 and 12, before its own wrapped second line. The file still ends with the `README.md` closing line and a final newline. → OK.
- Do the criteria catch nearby wrong inputs? I mutated scratch copies of the file and ran the criteria on them:
  - Rule 3's counterpart line moved below its Before line → criterion 4 printed `misplaced=1`.
  - A counterpart line added to rule 8, plus a stray one before rule 1 → `rules=111011111111 misplaced=1`.
  - A duplicate After line in rule 10 → criterion 2 printed `10:112`.
  → OK. Criteria 2 and 4 react to a wrong count and a wrong placement, so they do not pass only on the exact tested text.
- The `intro=` counter in criterion 4 is a boundary case. For a `Code counterpart:` line placed before the first rule heading, I ran `printf 'Code counterpart: stray\n## 1. x\nCheck: y\n' | awk '<criterion 4>'`. It printed `intro=0 … misplaced=1`, and a key dump showed the count landed under the key `""`, not `0`. At that point `n` has no value yet, so `k[0]` is never incremented: `intro=` always prints 0. → CONCERN, but minor and not about this PR. `misplaced=` still catches such a line, so the requirement that no counterpart line stands outside a rule is still enforced. This PR has no such line.

Out-of-scope observations:
- Criterion 4's `intro=` field cannot report anything other than 0 (see the last probe). If a later spec reuses this command, it should rely on `misplaced=`, or initialise `n=0` in a `BEGIN` block.
- The PR description says the implementer ran in `.factory/state/worktrees/T-0014.1` at `c64183a`. I re-ran everything independently at the merge head `89e8b7d`. `git diff --stat 431e349 89e8b7d` lists only `docs/writing.md | 45 +` (45 lines added), which agrees with its conflict note.

STATUS: VERIFIED
CONFIDENCE: high. I ran all seven criteria on both base and head and both gates on the head, and the inserted text compared byte-identical to design.md once lines were joined.
ESCALATIONS: none
