One sub-ticket. The whole change is additions to one file, `docs/writing.md`, about 45 lines,
and no test or protected path is touched. Rejected: splitting it into parts A+B (counterpart
lines on existing rules) and part C (four new rules). Part A's intro sentence promises counterpart
lines on new rules too, and the counterpart scenario only reaches its THEN once both parts land.
A split would leave a half-true standard on `main` between merges and buy no easier review.

Baseline checked on `~/dev/spec-factory` at `d8e1ada` (the spec was verified at `967ee77`):
`git log 967ee77..HEAD -- docs/writing.md README.md` prints nothing, so neither file has drifted.
`docs/writing.md` is 86 lines with rules 1–8 at lines 21, 29, 38, 46, 54, 62, 70, 78. Each rule
has exactly one `Before (` line (lines 23, 32, 40, 48, 56, 65, 72, 80), which is where part B
anchors. Line 19 ends "example taken from the factory's own writing, and its rewrite." and the
last line is "`README.md` is a worked example of these rules applied to a whole page.", which are
part A's and part C's anchors. The phrase scenario prints `writing=nnnnnn readme=nyyyny`, and
`tests/factory/test_writing_standard.py` prints `5 passed in 0.41s`.

---

ST-1 / Add rules 9–12 and code counterpart lines to the writing standard

Parent: the approved spec v3 for this change (proposal.md, design.md,
specs/writing-standard/spec.md, verification.md). Read it for context. Do NOT implement parts
outside this sub-ticket.

Depends on: none
Parallel-safe: yes (it is the only sub-ticket)

Scope: design.md parts A, B and C, all in `docs/writing.md`, additions only.
- A. The intro sentence directly after line 19, as a continuation of that paragraph.
- B. One `Code counterpart:` line directly before the `Before (` line of rules 1, 2, 3, 5, 6 and
  7, with the exact text from design.md's table. Rules 4 and 8 get none.
- C. Rules 9–12, with the exact wording from design.md, between rule 8's After paragraph and
  the closing `README.md` line, with a blank line after each rule. Rewrapping is allowed at no more
  than 100 characters; wording is fixed by the gate.

Acceptance (every WHEN runs from `~/dev/spec-factory`; commands are verbatim from the parent):
1. twelve numbered rules with the four new headings → NEW.
   WHEN `echo "rules=$(grep -o '^## [0-9]*\.' docs/writing.md | tr -dc '0-9\n' | paste -sd, -) new=$(grep -c -i -E '^## 9\. One name per concept|^## 10\. One mode per section|^## 11\. A heading states what is under it|^## 12\. Parallel facts go in a table' docs/writing.md)"`
   THEN `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4`
2. each new rule has one check, one before, one after → NEW.
   WHEN `awk '/^## [0-9]+\./{n=$2+0} n>=9 && /^Check: /{c[n]++} n>=9 && /^Before \(/{b[n]++} n>=9 && /^After: /{a[n]++} END{for(i=9;i<=12;i++) printf "%d:%d%d%d ", i, c[i], b[i], a[i]; print ""}' docs/writing.md`
   THEN `9:111 10:111 11:111 12:111` (trailing space allowed)
3. example phrases are in the standard and match the README → NEW.
   WHEN `w=; r=; for h in "installed harness" "the pinned checkout of the harness that runs tickets" "Accepting a harness revision" "Upgrading the runtime" "The human's stops" "Where a human decides"; do w="$w$(tr '\n' ' ' < docs/writing.md | grep -qF "$h" && echo y || echo n)"; r="$r$(tr '\n' ' ' < README.md | grep -qF "$h" && echo y || echo n)"; done; echo "writing=$w readme=$r"`
   THEN `writing=yyyyyy readme=nyyyny`
4. counterpart lines on the agreed rules, in place → NEW.
   WHEN `awk '/^## [0-9]+\./{n=$2+0; ck=0; bf=0} /^Check: /{ck=1} /^Before \(/{bf=1} /^Code counterpart: /{k[n]++; if (!ck || bf) bad++} END{s=""; for(i=1;i<=12;i++) s=s (k[i]+0); print "intro=" (k[0]+0) " rules=" s " misplaced=" (bad+0)}' docs/writing.md`
   THEN `intro=0 rules=111011101111 misplaced=0`
5. under budget, nothing removed, clean whitespace → REGRESSION.
   WHEN `echo "lines=$(grep -c '' docs/writing.md) wide=$(awk 'length($0)>100' docs/writing.md | grep -c '') removed=$(git diff -U0 e703c1b -- docs/writing.md | grep -v '^--- ' | grep -c '^-') ws=$(git diff --check e703c1b -- docs/writing.md >/dev/null && echo clean || echo errors)"`
   THEN `wide=0 removed=0 ws=clean`, and `lines=` below 140 (the parent's scratch build gave 131)
6. only the standard changes → NEW. Run on the change branch, before merge.
   WHEN `echo "changed=[$(git diff --name-only "$(git merge-base main HEAD)" HEAD -- . ':(exclude).factory' | paste -sd, -)]"`
   THEN exactly `changed=[docs/writing.md]`
7. the standard's existing tests still pass → REGRESSION.
   WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_writing_standard.py 2>&1 | tail -1`
   THEN the last line reports `5 passed` and no failures

Intermediate check (NEW, for the reviewer, not a parent scenario): the inserted text matches
design.md word for word. Criteria 1–4 count lines and phrases but do not compare wording, and
the gate fixed the wording. The reviewer joins each inserted block's wrapped lines and compares
it with the design.md text for parts A, B and C; any wording difference fails the ticket.

Tests to change: none
Protected paths: none
Out of scope:
- Every file other than `docs/writing.md`, including `README.md` and its "Maintaining this page"
  summary, `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, the role prompts and the
  critic and reviewer rubrics.
- Any edit, move or removal of an existing line in `docs/writing.md`, including rewording rules
  1–8.
- Rewriting any existing document to the new rules, and rules for research items 1, 5 or 7.
- Operator steps 0 (the rewrite and comprehension acceptance test) and 1 (moving the runtime
  checkout at `~/dev/spec-factory-harness` to the merge commit). They are the operator's, after
  merge; the implementer does not touch the runtime checkout.

Coverage map:
- twelve numbered rules with the four new headings → ST-1
- each new rule has one check, one before, one after → ST-1
- example phrases are in the standard and match the README → ST-1
- counterpart lines on the agreed rules, in place → ST-1
- under budget, nothing removed, clean whitespace → ST-1
- only the standard changes → ST-1 (pre-merge, on the change branch)
- the standard's existing tests still pass → ST-1
- Operator steps 0 and 1 → operator, after merge; not a sub-ticket

STATUS: PLANNED
CONFIDENCE: high, one additive edit to one file whose anchors and baseline outputs I re-checked at d8e1ada with no drift since the spec's 967ee77.
ESCALATIONS: none
