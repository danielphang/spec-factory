Commit: fcc87564a0b3d9a07741c959676d28aa7d06d46a (`main`, the merge of `factory/T-0014.1`). Base: 431e3492d977c01f5ac3252f94b6f40f08b6c043 (`main` just before that merge).

This is a parent-close run (verifying the merged result on `main`). I ran every WHEN command from the parent spec as written in `~/dev/spec-factory`. That checkout is on `main` at `fcc8756`, and its `docs/writing.md` and `README.md` have no local changes. I ran them again in the run worktree, with the same results. For the base, I ran them in a scratch clone with `main` reset to `431e349`, which leaves the repo untouched.

Per criterion:

| Type | Scenario | Base (431e349) | Head (fcc8756) | Result |
|---|---|---|---|---|
| NEW | twelve numbered rules with the four new headings | `rules=1,2,3,4,5,6,7,8 new=0` | `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4` | PASS |
| NEW | each new rule has one check, one before, one after | `9:000 10:000 11:000 12:000` | `9:111 10:111 11:111 12:111 ` | PASS |
| NEW | example phrases are in the standard and match the README | `writing=nnnnnn readme=nyyyny` | `writing=yyyyyy readme=nyyyny` | PASS |
| NEW | counterpart lines on the agreed rules, in place | `intro=0 rules=000000000000 misplaced=0` | `intro=0 rules=111011101111 misplaced=0` | PASS |
| REGRESSION | under budget, nothing removed, clean whitespace | `lines=86 wide=0 removed=0 ws=clean` | `lines=131 wide=0 removed=0 ws=clean` | PASS |
| NEW | only the standard changes | `changed=[]` | see note | PASS |
| REGRESSION | the standard's existing tests still pass | `5 passed in 0.67s` | `5 passed in 0.35s` (worktree: `5 passed in 1.77s`) | PASS |

Note on "only the standard changes". Its GIVEN line says it runs on the change branch before the merge. On `main` after the merge, the merge base is HEAD itself, so it prints `changed=[]` and checks nothing, as `verification.md` says. So I ran the command as written in the state its GIVEN line describes. `HEAD` was the branch tip `89e8b7d` (`factory/T-0014.1`) and `main` was `431e349`, and it printed `changed=[docs/writing.md]`. Two more checks agree. `git diff --name-only 431e349 fcc8756` prints only `docs/writing.md`. The branch's one content commit, `c64183a`, shows `docs/writing.md | 45 +++` and no other file.

Beyond the scenarios, I compared the text word for word with design.md. The risk section says the gate depends on this. I took parts A, B and C from the pinned design and diffed each against the merged file:
- Part A (intro sentence, file lines 20–21): identical.
- Part B (six counterpart lines, in rule order 1, 2, 3, 5, 6, 7): identical.
- Part C (rules 9–12, file lines 94–129): identical, with no rewrapping.

All 86 lines of the base file are still present, in the same order (checked by a Python in-order match: 86 of 86). The widest line is 99 characters. The file uses LF line endings only (0 CR characters).

Gate suite: PASS.
- `git diff --check main...HEAD` in the worktree printed nothing and exited 0. HEAD is `main` here, so the range is empty. The base-relative whitespace check `git diff --check e703c1b -- docs/writing.md` in the regression scenario printed `clean`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `126 passed in 101.99s` and exited 0.

Probes:
- Do the example phrases match where they are meant to, not by accident? Every phrase occurs in `docs/writing.md` only inside rules 9–12. "installed harness" is at line 100 and "the pinned checkout…" at 101 (both rule 9). The two how-to headings are at 111 (rule 10), "The human's" / "Where a human decides" at 118/120 (rule 11), and "Role, Does and Model" at 129 (rule 12). → OK.
- Are the after-states really in `README.md`, including rule 12's, which no scenario covers? Yes. The `runtime` row of the terms table (line 74) says "the pinned checkout of the harness that runs tickets". `## Where it runs` (150) is followed by `### Accepting a harness revision` (202) and `### Upgrading the runtime` (219). `## Where a human decides` is at 273. The `| Role | Does | Model |` table header is at 31. → OK.
- Does the merge need a re-acceptance, as Operator step 1 says it does not? `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` prints `e703c1bfb…` on `fcc8756`. The same command prints the same commit in the runtime (`~/dev/spec-factory-harness`, HEAD `43a01dd`), and `.factory/harness.lock` holds `e703c1bfb…` too. So the merge does not move the harness revision, and no `--accept-harness` run is needed. → OK.
- Does the counterpart-placement check catch a bad file? I made a scratch copy, moved rule 10's counterpart line below its Before line, and added a stray counterpart line in the intro. It printed `intro=0 rules=111011101111 misplaced=2`, so both faults were caught. The `intro=` field never counts, though. Lines before the first heading are stored under an empty key, but the field reads key `0`, so it always prints 0. The `misplaced=` count covers the gap: a line before any `Check:` counts as misplaced. → OK for this change. The check has a field that does nothing (see ESCALATIONS).

What this verification does not cover: the parent spec's Operator step 0. That step is the operator's acceptance test: a rewrite of a sample by a fresh agent, a control rewrite, a comprehension check, and the operator's approval. It is to be done before the runtime moves, and it is not in the merge checks. VERIFIED covers only the merged text and its acceptance scenarios. The new rules reach the roles only after Operator step 1 moves the runtime.

STATUS: VERIFIED
CONFIDENCE: high. Every scenario ran on head and base with the expected outputs, the text matches design.md word for word, and the full suite passed (126).
ESCALATIONS:
- The `intro=` field in the scenario "counterpart lines on the agreed rules, in place" always prints 0. It would not report a `Code counterpart:` line placed before rule 1. The awk command stores lines that come before any `## N.` heading under an empty key, but it prints the count for key `0`. On a scratch copy with a stray line in the intro, it still printed `intro=0`. The same scenario's `misplaced=` count does catch that line, so this change passes for real and is not affected. If the scenario is used again, its awk should start with `BEGIN{n=0}` so the field counts what it claims to.
