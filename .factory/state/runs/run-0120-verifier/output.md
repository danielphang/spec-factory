Commit: c64183ac7d10f6286136a0b419764d05202736fc (branch `factory/T-0014.1`, worktree
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0120-verifier/wt`, `git status --short` empty
before and after every run)

The writing standard (`docs/writing.md`, the page every role follows for text a person reads) now
has rules 9–12 and the ten agreed `Code counterpart:` lines, with nothing removed. Every acceptance
command gives its expected output on the PR and its recorded "today" output on the base. Both gate
commands pass, and the inserted text matches design.md word for word.

Where each side ran. Base: `~/dev/spec-factory`, which is `main` at `431e349` (the base I was given),
and has changes only under `.factory/`. PR: the worktree at `c64183a`. The commands say "from
`~/dev/spec-factory`", but that checkout is `main` and does not hold the change before merge, so I
ran them from the change branch's worktree. Criterion 6's GIVEN line asks for exactly that. Each
command was run verbatim from a script, with no edits.

Per criterion:

| # | Kind | Command (short name) | Base `431e349` | PR `c64183a` | Result |
|---|---|---|---|---|---|
| 1 | NEW | twelve numbered rules with the four new headings | `rules=1,2,3,4,5,6,7,8 new=0` | `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4` | PASS |
| 2 | NEW | each new rule has one check, one before, one after | `9:000 10:000 11:000 12:000 ` | `9:111 10:111 11:111 12:111 ` | PASS |
| 3 | NEW | example phrases are in the standard and match the README | `writing=nnnnnn readme=nyyyny` | `writing=yyyyyy readme=nyyyny` | PASS |
| 4 | NEW | counterpart lines on the agreed rules, in place | `intro=0 rules=000000000000 misplaced=0` | `intro=0 rules=111011101111 misplaced=0` | PASS |
| 5 | REGRESSION | under budget, nothing removed, clean whitespace | `lines=86 wide=0 removed=0 ws=clean` | `lines=131 wide=0 removed=0 ws=clean` | PASS |
| 6 | NEW | only the standard changes | `changed=[]` | `changed=[docs/writing.md]` | PASS |
| 7 | REGRESSION | the standard's existing tests still pass | `5 passed in 0.36s` | `5 passed in 1.70s` | PASS |

What the outputs mean:
- The NEW criteria (1–4 and 6) fail on the base for the reason verification.md gives: rules 9–12 and
  the counterpart lines do not exist yet, and nothing has changed on `main`. Each base output
  matches verification.md's "today" output exactly, so none of them is a spec defect.
- Criterion 5 holds on both sides. The PR file has 131 lines, the same as the spec's scratch build
  and under the 140-line budget. No line is removed relative to `e703c1b`, and there are no
  whitespace errors.
- Criterion 6: `git merge-base main HEAD` is `ba4618a`, so the diff counts only the branch's own
  commit. The two-dot diff `431e349..c64183a` also lists `dev/issues.md`. That comes from `main`
  moving one commit (`431e349`, "issues: #27 indexed") after the branch was cut, not from the
  branch. The PR description names its base as `ba4618a` while my input names `431e349`. That is
  the same fact seen from two sides, and it does not change any result.

Intermediate check (wording; the plan gives it to the reviewer, and I ran it independently):
- Part A: the two lines at `docs/writing.md` lines 20–21 are identical to design.md's block (`diff`
  printed nothing). They continue the paragraph that ends at line 19.
- Part B: the six inserted lines, each with its rule number, are identical to design.md's table
  (`diff` printed nothing). Rules 4 and 8 have none. Each line directly precedes its rule's
  `Before (` line (lines 25/26, 35/36, 44/45, 61/62, 71/72, 79/80).
- Part C: rules 9–12 at lines 91–125 are identical to design.md's block both line by line and with
  lines joined (`diff` printed nothing for either). Each rule is followed by a blank line, and the
  closing `README.md` line is still the file's last line.
- Nothing existing was edited: `diff <(git show 431e349:docs/writing.md) docs/writing.md | grep -c
  '^<'` prints `0`. Every base line is still present, in order.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 115.53s`. A rerun
  that captured the exit code gave `126 passed in 101.79s`, exit 0. The whole harness suite passes.

Probes:
- Line width at the boundary. The widest line in the PR file is 99 characters, under the 100 limit,
  and the same as the file's widest line before the change. → OK
- The README anchors the new examples cite, checked by heading structure rather than by phrase.
  `## Where it runs` (README line 150) has `### Accepting a harness revision` (202) and `### Upgrading
  the runtime` (219) as its how-to subsections, which is rule 10's After. `## Where a human decides`
  is at line 273 (rule 11). The `runtime` row at line 74 holds "the pinned checkout of the harness
  that runs tickets" (rule 9). The `| Role | Does | Model |` table at line 31 has 8 data rows, which
  matches rule 12's "the eight roles". The examples describe the README as it is, not only the
  phrases criterion 3 searches for. → OK
- Is criterion 4's placement check sensitive? I took a mutated copy of the PR file, in a pipe with no
  file written, that moves rule 2's counterpart line to after its `Before (` line. The same awk
  printed `misplaced=1`. A green criterion 4 therefore means the lines really are in place; it does
  not pass vacuously. → OK
- Wrapped phrases. "Upgrading the runtime" and "The human's stops" are split across lines in the
  standard (lines 115–116 and 122–123). Criterion 3 finds them only because it joins lines, which
  is the design the spec states. Nothing is special-cased to the test inputs. → OK

STATUS: VERIFIED
CONFIDENCE: high. All seven criteria and both gates were run verbatim on the head and the base,
and the text was diffed against design.md with no difference found.
ESCALATIONS: none
