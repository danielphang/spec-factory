## Spec critic review, round 1 (spec v1)

What I checked myself, from `~/dev/spec-factory` at `967ee77`:

- Cited paths and symbols: `docs/writing.md` has 86 lines, eight `## N.` headings at lines 21, 29,
  38, 46, 54, 62, 70, 78 and a widest line of 99; `HARNESS_PATHS` in `factory/instance.py` line 33
  is `("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")`; `README.md` has the Role /
  Does / Model table at lines 31–40, the `runtime` terms row, "## Where it runs" at 150,
  "### Accepting a harness revision" at 202, "### Upgrading the runtime" at 219, "## Where a human
  decides" at 273, and "Maintaining this page" at 373 with the "Reader first" bullet at 387.
  `e703c1b` is the only commit touching `docs/writing.md`. Issue 23's first comment lists the ten
  items as the spec describes; its second comment is the "prose is for the why" note the Decisions
  section attributes to it.
- All seven acceptance commands, run as written on today's checkout: `rules=1,2,3,4,5,6,7,8 new=0`,
  `9:000 10:000 11:000 12:000`, `writing=nnnnnn readme=nyyyny`, `intro=0 rules=000000000000
  misplaced=0`, `lines=86 wide=0 removed=0 ws=clean`, `changed=[]`, `5 passed in 1.79s`. The four
  NEW items fail today for the reason the spec gives.
- The same commands against a scratch copy I built from design.md parts A–C (not in the repo):
  `rules=1,...,12 new=4`, `9:111 10:111 11:111 12:111`, `writing=yyyyyy readme=nyyyny`, `intro=0
  rules=111011101111 misplaced=0`, `lines=131 wide=0`. The design text produces the THEN outputs,
  and a stub (headings without Check/Before/After, or counterpart lines in the wrong place) would
  not.

Findings:

[BLOCKING] 6 Operator steps, step 1
Problem: The only paragraph a new operator must act on says "move the runtime", "the harness
revision" and "`--accept-harness`" without saying what any of them is, and no earlier human-facing
section glosses "runtime" (Evidence bullet 9 glosses the harness lock as a commit pin, but never
says what the runtime is or that it lives in a second checkout).
Evidence: Read Problem, Evidence, Open questions and Decisions for a first use of "runtime" with a
gloss; there is none. The term is specific to this project (it is a row in the README's terms
table).
Suggested fix: Open step 1 with the gloss, e.g. "The factory runs from a second checkout of this
repo, the runtime at `~/dev/spec-factory-harness`, pinned to one commit. After merge, move it
between tickets: ...", and say "no `--accept-harness` is needed" as "the harness lock, the pin that
guards the code paths, does not cover `docs/`, so no re-acceptance step".

[SHOULD-FIX] 1 Risk, sentence 2
Problem: "the gate reads the four rules and the twelve-row mapping word for word (design.md,
part B)" cites the wrong place and count: Part B is a six-row table of counterpart lines for rules
1–7, and the four rules are Part C.
Evidence: design.md as submitted; Part B table has rows for rules 1, 2, 3, 5, 6, 7; Part C holds
rules 9–12 with their own counterpart lines.
Suggested fix: "the gate reads the six counterpart lines (part B) and the four new rules with
theirs (part C) word for word".

[NIT] 2 Scenario "only the standard changes"
Problem: The THEN accepts `changed=[]`, so on any checkout where `merge-base main HEAD` equals
HEAD (including `main` after the merge) the item passes without checking anything.
Evidence: Ran it on `main`: `changed=[]`. It carries weight only on the unmerged branch.
Suggested fix: None needed if the verifier runs it on the change branch, which is where it is
meant to run; otherwise drop the `changed=[]` clause.

Prior findings: none (round 1).

Out-of-scope observations:
- Scenario "under budget" measures removals against `e703c1b` by hand-filtering `^-` lines, which is
  fine today because that commit is the file's only history. If a later ticket edits the file, the
  anchor stays correct but the "nothing removed" meaning drifts to "nothing removed since the
  first version". Not this ticket's problem.

STATUS: REVISE
CONFIDENCE: high; every cited path, line and command was checked on the checkout and the design
text reproduces the THEN outputs on a scratch copy, so the one blocking issue is purely the
Operator steps gloss.
ESCALATIONS: none
